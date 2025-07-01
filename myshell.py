#!/usr/bin/env python3
"""
Python Unix Shell
-----------------
A feature-rich Unix-like shell implemented in Python for learning and custom automation.
See README.md for features and limitations.
"""

from parser import CommandParser
from executor import CommandExecutor
from shell_builtins import Builtins
from jobcontrol import JobControl
from history import HistoryManager
from completion import CompletionEngine
from config import ShellConfig
from utils import shell_print
import os
import shlex
import subprocess
import readline
import glob
import signal
import re
from plugins import load_plugins
import time

# Plugin system
try:
    from plugins import PluginBase
except ImportError:
    PluginBase = None

# ========== Tab Completion Setup ==========
def completer(text, state):
    # Complete command names if first word, else files
    buffer = readline.get_line_buffer()
    line = shlex.split(buffer) if buffer else []
    if len(line) == 0 or (len(line) == 1 and not buffer.endswith(' ')):
        # Complete command names
        cmds = [cmd for cmd in os.listdir('/bin') if cmd.startswith(text)]
        cmds += [cmd for cmd in os.listdir('/usr/bin') if cmd.startswith(text)]
        cmds = list(set(cmds))
        try:
            return cmds[state]
        except IndexError:
            return None
    else:
        # Complete file names
        matches = glob.glob(text+'*')
        try:
            return matches[state]
        except IndexError:
            return None

readline.set_completer(completer)
readline.parse_and_bind('tab: complete')
# ========== End Tab Completion Setup ==========

# ========== Main Shell Function ==========
def main():
    # Initialize modules
    parser = CommandParser()
    executor = CommandExecutor()
    builtins = Builtins()
    jobcontrol = JobControl()
    history = HistoryManager()
    completion = CompletionEngine()
    config = ShellConfig()
    plugins = load_plugins(locals())
    custom_commands = locals().get('custom_commands', {})
    pre_exec_hooks = locals().get('pre_exec_hooks', [])
    post_exec_hooks = locals().get('post_exec_hooks', [])
    on_error_hooks = locals().get('on_error_hooks', [])

    # Load config
    config.load(os.path.expanduser('~/.myshellrc'))

    # Set up tab completion
    readline.set_completer(completion.complete)
    readline.parse_and_bind('tab: complete')

    # Load plugins (TODO: dynamic discovery)
    # Example: plugins.append(MyPlugin())
    for plugin in plugins:
        plugin.activate(locals())

    # Main shell loop
    while True:
        try:
            prompt = config.render_prompt()
            line = input(prompt)
            if not line.strip():
                continue
            # Detect background job (&)
            run_in_bg = False
            if line.strip().endswith('&'):
                run_in_bg = True
                line = line.strip()[:-1].strip()
            # History
            history.add(line)
            # History expansion
            line = history.expand(line)
            # Parse command
            parsed = parser.parse(line)
            # Plugin custom commands
            if isinstance(parsed, dict) and 'pipeline' in parsed and isinstance(parsed['pipeline'], list) and parsed['pipeline']:
                cmd = parsed['pipeline'][0]['args']
                if cmd and cmd[0] in custom_commands:
                    custom_commands[cmd[0]](*cmd[1:])
                    continue
            # Built-in dispatch (pass jobcontrol for jobs, fg, bg, disown)
            if isinstance(parsed, dict) and builtins.dispatch(parsed, custom_commands=custom_commands):
                if 'pipeline' in parsed and isinstance(parsed['pipeline'], list) and parsed['pipeline']:
                    cmd = parsed['pipeline'][0]['args']
                    if cmd:
                        if cmd[0] == 'jobs':
                            jobcontrol.list_jobs()
                        elif cmd[0] == 'fg' and len(cmd) > 1:
                            jobcontrol.fg(int(cmd[1]))
                        elif cmd[0] == 'bg' and len(cmd) > 1:
                            jobcontrol.bg(int(cmd[1]))
                        elif cmd[0] == 'disown' and len(cmd) > 1:
                            jobcontrol.disown(int(cmd[1]))
                continue
            # Parallel jobs
            if isinstance(parsed, dict) and 'parallel_jobs' in parsed and isinstance(parsed['parallel_jobs'], list):
                procs = []
                for job in parsed['parallel_jobs']:
                    status, process = executor.execute(job, run_in_bg=True)
                    if process:
                        procs.append(process)
                continue
            # Wait command
            if isinstance(parsed, dict) and 'wait' in parsed and parsed['wait'] is True:
                while True:
                    try:
                        pid, _ = os.wait()
                    except ChildProcessError:
                        break
                continue
            # Pre-exec hooks
            for hook in pre_exec_hooks:
                try:
                    hook(line)
                except Exception as e:
                    shell_print(f"[plugin pre-exec error] {e}")
            # Command timing
            timing_threshold_str = config.get('TIMING_THRESHOLD')
            if timing_threshold_str is None:
                timing_threshold_str = '1.0'
            try:
                timing_threshold = float(timing_threshold_str)
            except (TypeError, ValueError):
                timing_threshold = 1.0
            start_time = time.time()
            try:
                status, process = executor.execute(parsed, run_in_bg=run_in_bg)
                elapsed = time.time() - start_time
                # Post-exec hooks
                for hook in post_exec_hooks:
                    try:
                        hook(line, status)
                    except Exception as e:
                        shell_print(f"[plugin post-exec error] {e}")
                if elapsed > timing_threshold:
                    shell_print(f"[timing] Command took {elapsed:.2f} seconds.")
            except Exception as e:
                # On-error hooks
                for hook in on_error_hooks:
                    try:
                        hook(line, e)
                    except Exception as e2:
                        shell_print(f"[plugin on-error error] {e2}")
                shell_print(f"Shell error: {e}")
                continue
            # Add to job control if background job
            if run_in_bg and process:
                jobcontrol.add_job(process, line)
        except EOFError:
            shell_print("")
            break
        except KeyboardInterrupt:
            shell_print("")
            continue

# ========== Script Execution Mode ==========
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
        with open(script_path) as f:
            lines = [line.rstrip() for line in f if line.strip() and not line.strip().startswith('#')]
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('if '):
                cond_cmd = line[3:].strip()
                if lines[i+1].strip() == 'then':
                    block = []
                    j = i+2
                    while j < len(lines) and lines[j].strip() != 'fi':
                        block.append(lines[j])
                        j += 1
                    print(f"myshell$ {cond_cmd}")
                    cond_status = os.system(cond_cmd)
                    if cond_status == 0:
                        for bline in block:
                            print(f"myshell$ {bline}")
                            os.system(bline)
                    i = j
            elif line.startswith('for '):
                for_parts = line[4:].split(' in ')
                var = for_parts[0].strip()
                values = for_parts[1].strip().rstrip(';').split()
                if lines[i+1].strip() == 'do':
                    block = []
                    j = i+2
                    while j < len(lines) and lines[j].strip() != 'done':
                        block.append(lines[j])
                        j += 1
                    for val in values:
                        os.environ[var] = val
                        for bline in block:
                            print(f"myshell$ {bline}")
                            os.system(bline)
                    i = j
            elif line.startswith('while '):
                cond_cmd = line[6:].strip().rstrip(';')
                if lines[i+1].strip() == 'do':
                    block = []
                    j = i+2
                    while j < len(lines) and lines[j].strip() != 'done':
                        block.append(lines[j])
                        j += 1
                    while os.system(cond_cmd) == 0:
                        for bline in block:
                            print(f"myshell$ {bline}")
                            os.system(bline)
                    i = j
            else:
                print(f"myshell$ {line}")
                os.system(line)
            i += 1
    else:
        main() 
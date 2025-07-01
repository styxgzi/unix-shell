"""
parser.py - Command and script parser for the advanced Python shell.
"""
import shlex

class CommandParser:
    """Parses shell commands and scripts into executable structures."""
    def parse(self, line):
        """Parse a single command line or script line. Returns a parsed structure."""
        # Parallel background jobs: split on '&' (not at end)
        if '&' in line and not line.strip().endswith('&'):
            jobs = [l.strip() for l in line.split('&') if l.strip()]
            return {'parallel_jobs': [self.parse(job) for job in jobs]}
        # Wait command
        if line.strip() == 'wait':
            return {'wait': True}
        # TODO: Recognize nested blocks and function definitions
        if line.strip().startswith('function ') or ('()' in line and '{' in line):
            return {'function_def': line.strip()}
        if line.strip().startswith(('if ', 'for ', 'while ', 'case ')):
            return {'block': line.strip()}
        if '<<' in line:
            return {'heredoc': line.strip()}
        # Fallback: pipeline parsing
        pipe_parts = [p.strip() for p in line.split('|')]
        commands = []
        for part in pipe_parts:
            tokens = shlex.split(part)
            cmd = {'args': [], 'stdin': None, 'stdout': None, 'stderr': None, 'append': False}
            i = 0
            while i < len(tokens):
                if tokens[i] == '>':
                    cmd['stdout'] = tokens[i+1]
                    cmd['append'] = False
                    i += 2
                elif tokens[i] == '>>':
                    cmd['stdout'] = tokens[i+1]
                    cmd['append'] = True
                    i += 2
                elif tokens[i] == '<':
                    cmd['stdin'] = tokens[i+1]
                    i += 2
                elif tokens[i] == '2>':
                    cmd['stderr'] = tokens[i+1]
                    i += 2
                else:
                    cmd['args'].append(tokens[i])
                    i += 1
            commands.append(cmd)
        return {'pipeline': commands} 
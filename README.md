# Python Unix Shell (Major Project)

A modular, extensible Unix-like shell implemented in Python, designed as a major project for advanced learning, automation, and extensibility.

## Project Structure

```
unix-shell/
├── myshell.py         # Entry point
├── parser.py          # Command and script parser
├── executor.py        # Command execution engine
├── builtins.py        # Built-in commands (cd, alias, etc.)
├── jobcontrol.py      # Job and process management
├── plugins/           # Plugin system
│   └── __init__.py
├── completion.py      # Tab and custom completion
├── history.py         # Command history and expansion
├── config.py          # Configuration and environment
├── utils.py           # Utility functions
├── tests/             # Test suite
│   └── test_shell.py
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── requirements.txt
```

## Roadmap: Advanced Features
- Full-featured scripting (nested blocks, case, functions, here-docs)
- Advanced job control and process management
- History expansion and custom key bindings
- Dynamic and customizable prompt
- Plugin/extension system
- File descriptor and process substitution
- Integration with git, virtualenv, containers, etc.
- Better error messages, suggestions, and auto-correction
- Security, sandboxing, and restricted mode
- Command caching and parallel execution

## Features
- Command history & line editing
- Tab completion for commands and files
- Customizable prompt (`MYSHELL_PROMPT`)
- Aliases and unalias
- Job control: background jobs (`&`), `jobs`, `fg`, `bg`
- Globbing (`*.py`)
- Environment variable expansion and management (`export`, `unset`)
- Command substitution (`$(...)`, `` `...` ``)
- Logical operators (`&&`, `||`)
- Advanced redirection (`>`, `<`, `>>`, `2>`, `2>&1`)
- Exit status (`$?`)
- Configuration file (`.myshellrc`)
- Script execution (run a script file line by line)
- Minimal scripting: `if ... then ... fi`, `for ... in ...; do ... done`, `while ...; do ... done`

## Usage Examples

Interactive shell:
```sh
python3 myshell.py
```

Run a script:
```sh
python3 myshell.py script.sh
```

## Plugins
- Add a `.py` file to the `plugins/` directory with a `Plugin` class.
- Plugins can register custom commands, completions, or hooks.
- See `plugins/sample_plugin.py` for an example.

## Running Tests
```sh
pytest tests
```

## Customization
- Set aliases and environment variables in `~/.myshellrc`.
- Customize the prompt with `export MYSHELL_PROMPT="myshell$ "`.

## Limitations
- Scripting support is minimal (no nested or complex shell constructs).
- Not a full POSIX shell (no functions, case/esac, here-docs, etc.).
- Some advanced job control and error handling are simplified.
- Not as robust as bash/zsh for edge cases or complex scripts.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code style, adding features, and submitting pull requests.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE).

## For Learning and Advanced Customization
This shell is ideal for advanced learning, custom automation, and as a base for further development. For full POSIX compliance, use bash, zsh, or fish. 
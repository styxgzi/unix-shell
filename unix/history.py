"""
history.py - Command history and expansion for the advanced Python shell.
"""

class HistoryManager:
    """Manages command history and history expansion (!, !!, etc.)."""
    def __init__(self):
        self.history = []
    def add(self, line):
        """Add a command to history."""
        self.history.append(line)
    def get(self, index):
        """Get a command from history by index."""
        if 0 <= index < len(self.history):
            return self.history[index]
        return None
    def expand(self, line):
        """Expand history references in a command line."""
        if line.strip() == '!!':
            return self.history[-1] if self.history else ''
        elif line.startswith('!') and line[1:].isdigit():
            idx = int(line[1:]) - 1
            return self.get(idx) or line
        elif line.startswith('!') and len(line) > 1:
            prefix = line[1:]
            for cmd in reversed(self.history):
                if cmd.startswith(prefix):
                    return cmd
            return line
        return line 
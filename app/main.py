import sys
import os
import subprocess
import readline
import ctypes
import ctypes.util


# --- Tab Autocompletion Setup ---

# Suppress readline's automatic trailing space after completions
# We handle trailing characters ourselves (space for files, / for dirs)
_rl_suppress = None
try:
    _rl_lib = ctypes.CDLL(ctypes.util.find_library("readline"))
    _rl_suppress = ctypes.c_int.in_dll(_rl_lib, "rl_completion_suppress_append")
except (OSError, ValueError, TypeError):
    pass

# List of builtin commands for tab autocompletion
BUILTINS = ["echo", "exit", "type", "pwd", "cd", "history"]


def display_hook(substitution, matches, longest_match_length):
    """Show completion matches: files without trailing space, dirs with /."""
    print()
    display_items = []
    for match in matches:
        if match.endswith(" "):
            display_items.append(match[:-1])   # Strip trailing space for display
        else:
            display_items.append(match)         # Keep dirname/ as-is
    print("  ".join(sorted(display_items)))
    sys.stdout.write("$ " + readline.get_line_buffer())
    sys.stdout.flush()


def completer(text, state):
    if state == 0:
        completer.matches = []
        seen = set()
        begidx = readline.get_begidx()

        if begidx == 0:
            # COMPLETING A COMMAND NAME (first word on the line)

            # 1. Check builtins
            for cmd in BUILTINS:
                if cmd.startswith(text) and cmd not in seen:
                    completer.matches.append(cmd + " ")
                    seen.add(cmd)

            # 2. Check PATH for executables
            path_dirs = os.environ.get("PATH", "").split(os.pathsep)
            for directory in path_dirs:
                if not os.path.isdir(directory):
                    continue
                try:
                    for filename in os.listdir(directory):
                        if filename.startswith(text) and filename not in seen:
                            full_path = os.path.join(directory, filename)
                            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                                completer.matches.append(filename + " ")
                                seen.add(filename)
                except OSError:
                    continue
        else:
            # COMPLETING A FILENAME/DIRECTORY (argument position)

            # Split text into directory path and prefix
            if "/" in text:
                dir_path = text[:text.rfind("/") + 1]   # e.g., "path/to/"
                prefix = text[text.rfind("/") + 1:]      # e.g., "f"
                search_dir = dir_path
            else:
                dir_path = ""
                prefix = text
                search_dir = "."

            if os.path.isdir(search_dir):
                try:
                    for entry in os.listdir(search_dir):
                        if entry.startswith(prefix):
                            entry_path = os.path.join(search_dir, entry)
                            if os.path.isdir(entry_path):
                                # Directory → trailing /
                                completer.matches.append(dir_path + entry + "/")
                            else:
                                # File → trailing space
                                completer.matches.append(dir_path + entry + " ")
                except OSError:
                    pass

        completer.matches.sort()

    # Suppress readline's default trailing space (we add our own)
    if _rl_suppress is not None:
        _rl_suppress.value = 1

    if state < len(completer.matches):
        return completer.matches[state]
    return None


def parse_command(command):
    args = []           # List to hold each argument
    current = ""        # The argument we're currently building
    in_single_quotes = False
    in_double_quotes = False
    i = 0               # Index to walk through the string

    while i < len(command):
        char = command[i]

        if in_single_quotes:
            # INSIDE SINGLE QUOTES: everything is literal, even backslashes
            if char == "'":
                in_single_quotes = False    # Closing single quote
            else:
                current += char             # Every character is literal

        elif in_double_quotes:
            # INSIDE DOUBLE QUOTES: backslash only escapes " and \
            if char == '"':
                in_double_quotes = False    # Closing double quote
            elif char == '\\' and i + 1 < len(command) and command[i + 1] in '"\\$`\n':
                # Backslash followed by a special char → escape it
                current += command[i + 1]   # Add the next char literally
                i += 1                      # Skip the next char
            else:
                current += char             # Normal char (including \ before non-special chars)

        else:
            # OUTSIDE ALL QUOTES
            if char == '\\' and i + 1 < len(command):
                # Backslash outside quotes → escape the next character
                current += command[i + 1]   # Add the next char literally
                i += 1                      # Skip the next char
            elif char == "'":
                in_single_quotes = True     # Opening single quote
            elif char == '"':
                in_double_quotes = True     # Opening double quote
            elif char == ' ':
                # Space outside quotes → delimiter
                if current != "":
                    args.append(current)
                    current = ""
            else:
                current += char             # Normal character

        i += 1  # Move to the next character

    # Don't forget the last argument
    if current != "":
        args.append(current)

    return args


def main():
    # Set up readline for tab autocompletion
    readline.set_completer(completer)
    readline.set_completer_delims(' \t\n')                       # Only split words on whitespace
    readline.parse_and_bind("tab: complete")
    readline.set_completion_display_matches_hook(display_hook)   # Custom display for matches
    history_entries = []

    while True:
        try:
            command = input("$ ")
        except EOFError:
            break

        parts = parse_command(command)
        if not parts:
            continue

        # Keep the original command text in history and register it with readline
        history_entries.append(command)
        readline.add_history(command)
        cmd = parts[0]

        if cmd == "exit":
            break
        elif cmd == "echo":
            print(" ".join(parts[1:]))
        elif cmd == "pwd":
            print(os.getcwd())
        elif cmd == "cd":
            directory = parts[1]
            if directory == "~":
                directory = os.environ["HOME"]
            if os.path.isdir(directory):
                os.chdir(directory)
            else:
                print(f"cd: {directory}: No such file or directory")
        elif cmd == "history":
            count = int(parts[1]) if len(parts) > 1 else len(history_entries)
            first_index = max(0, len(history_entries) - count)

            for index, entry in enumerate(history_entries[first_index:], start=first_index + 1):
                print(f"{index:5d}  {entry}")
        elif cmd == "type":
            argument = parts[1]

            if argument in BUILTINS:
                print(f"{argument} is a shell builtin")
            else:
                path_dirs = os.environ["PATH"].split(os.pathsep)

                found = False

                for directory in path_dirs:
                    full_path = os.path.join(directory, argument)

                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        print(f"{argument} is {full_path}")
                        found = True
                        break

                if not found:
                    print(f"{argument}: not found")
        else:
            path_dirs = os.environ["PATH"].split(os.pathsep)

            found = False

            for directory in path_dirs:
                full_path = os.path.join(directory, cmd)

                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    subprocess.run([cmd] + parts[1:], executable=full_path)
                    found = True
                    break

            if not found:
                print(f"{cmd}: not found")


if __name__ == "__main__":
    main()
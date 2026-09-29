import sys
import os
import subprocess
import readline


# List of builtin commands for tab autocompletion
BUILTINS = ["echo", "exit", "type", "pwd", "cd"]


def filename_matches(text):
    """Return the one matching file or directory for a filename prefix."""
    # Keep the path the user typed (for example, "notes/") separate from
    # the part that should be matched (for example, "rea").
    directory, slash, prefix = text.rpartition("/")
    directory_part = directory + slash

    # No slash means that we should look in the current directory.
    search_directory = directory_part if directory_part else "."

    try:
        matches = [
            entry
            for entry in os.listdir(search_directory)
            if entry.startswith(prefix)
        ]
    except OSError:
        return []

    # This stage only completes when there is exactly one possible entry.
    if len(matches) != 1:
        return []

    match = directory_part + matches[0]
    full_path = os.path.join(search_directory, matches[0])

    # Directories keep accepting more path text, while files finish an argument.
    if os.path.isdir(full_path):
        return [match + "/"]
    return [match]


def completer(text, state):
    # On the FIRST call (state=0), build the full list of matches
    if state == 0:
        completer.matches = []
        seen = set()

        # Anything after the first space is a filename argument.
        if " " in readline.get_line_buffer():
            completer.matches = filename_matches(text)
        else:
            # Complete command names for the first word, as before.
            for cmd in BUILTINS:
                if cmd.startswith(text) and cmd not in seen:
                    completer.matches.append(cmd)
                    seen.add(cmd)

            path_dirs = os.environ.get("PATH", "").split(os.pathsep)
            for directory in path_dirs:
                if not os.path.isdir(directory):
                    continue
                try:
                    for filename in os.listdir(directory):
                        full_path = os.path.join(directory, filename)
                        if (
                            filename.startswith(text)
                            and filename not in seen
                            and os.path.isfile(full_path)
                            and os.access(full_path, os.X_OK)
                        ):
                            completer.matches.append(filename)
                            seen.add(filename)
                except OSError:
                    continue

            completer.matches.sort()

    # Return matches one at a time — readline calls with state=0, 1, 2...
    if state < len(completer.matches):
        match = completer.matches[state]
        if match.endswith("/"):
            return match
        return match + " "
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
    readline.set_completer(completer)           # Tell readline to use our completer function
    readline.set_completer_delims(" \t\n")    # Treat a complete path as one word
    readline.parse_and_bind("tab: complete")    # Bind the TAB key to trigger completion

    while True:
        try:
            command = input("$ ")
        except EOFError:
            break

        parts = parse_command(command)
        if not parts:
            continue
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
        elif cmd == "type":
            argument = parts[1]

            if argument in ["type", "echo", "exit", "pwd", "cd"]:
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

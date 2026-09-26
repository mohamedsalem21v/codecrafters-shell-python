import sys
import os
import subprocess
import readline


# List of builtin commands for tab autocompletion
BUILTINS = ["echo", "exit", "type", "pwd", "cd"]


def completer(text, state):
    # Find all builtin commands that start with the typed text
    matches = [cmd for cmd in BUILTINS if cmd.startswith(text)]

    # Return the match at position 'state', with a trailing space
    if state < len(matches):
        return matches[state] + " "
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
    readline.parse_and_bind("tab: complete")    # Bind the TAB key to trigger completion

    while True:
        sys.stdout.write("$ ")

        try:
            command = input()
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

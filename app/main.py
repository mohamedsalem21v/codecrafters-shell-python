import sys
import os
import subprocess


def parse_command(command):
    args = []           # List to hold each argument
    current = ""        # The argument we're currently building
    in_single_quotes = False  # Are we inside single quotes?

    for char in command:
        if char == "'" and not in_single_quotes:
            # Opening single quote — enter quoted mode
            in_single_quotes = True
        elif char == "'" and in_single_quotes:
            # Closing single quote — exit quoted mode
            in_single_quotes = False
        elif char == " " and not in_single_quotes:
            # Space outside quotes — this is a delimiter
            if current != "":
                args.append(current)
                current = ""
        else:
            # Normal character — add it to the current argument
            current += char

    # Don't forget the last argument
    if current != "":
        args.append(current)

    return args


def main():
    while True:
        sys.stdout.write("$ ")

        command = input()

        parts = parse_command(command)
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

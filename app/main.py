import sys
import os


def main():
    while True:
        sys.stdout.write("$ ")

        command = input()

        parts = command.split(" ")
        cmd = parts[0]

        if cmd == "exit":
            break
        elif cmd == "echo":
            print(command[5:])
        elif cmd == "type":
            argument = parts[1]

            if argument in ["type", "echo", "exit"]:
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
            print(f"{cmd}: not found")


if __name__ == "__main__":
    main()

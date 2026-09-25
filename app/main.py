import sys


def main():
    while True:
        sys.stdout.write("$ ")
        
        command = input()
        if command == "exit":
            break
        elif command.startswith("echo"):
            print(command[5:])
        elif command[5:] in ["type", "echo", "exit"]:
            print(f"{command[5:]} is a shell builtin")
        else:
            print(f"{command.strip('type ')}: not found")


if __name__ == "__main__":
    main()

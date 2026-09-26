[![progress-banner](https://backend.codecrafters.io/progress/shell/d3a55dd1-75cb-472a-b22a-60483f4f794c)](https://app.codecrafters.io/users/mohamedsalem21v?r=2qF)

# Build Your Own Shell (Python)

A POSIX-compliant shell built from scratch in Python as part of the [CodeCrafters "Build Your Own Shell" Challenge](https://app.codecrafters.io/courses/shell/overview).

## 🚀 Features Implemented

### 1. REPL & Command Handling
- **Interactive Prompt**: Outputs `$ ` prompt and awaits user commands.
- **Handling Invalid Commands**: Gracefully prints `<command>: not found` for unrecognized inputs.

### 2. Builtin Commands
- **`exit`**: Exits the shell cleanly (`exit 0`).
- **`echo`**: Prints back the provided text to stdout with full quoting and escaping support.
- **`type`**: Identifies whether a command is a shell builtin or an external program:
  - Reports builtins (`<command> is a shell builtin`).
  - Searches through `$PATH` for executables and reports their absolute paths (`<command> is <full_path>`).
- **`pwd`**: Prints the current absolute working directory.
- **`cd`**: Changes the current working directory:
  - Supports **absolute paths** (e.g. `cd /usr/local/bin`).
  - Supports **relative paths** (e.g. `cd ./local/bin`, `cd ../../`).
  - Supports **home directory shortcut `~`** (resolves using `$HOME`).
  - Prints error message if directory does not exist (`cd: <directory>: No such file or directory`).

### 3. Command Line Parsing, Quoting & Escaping
- **Single Quotes (`'...'`)**:
  - Treats all enclosed characters literally.
  - Preserves consecutive whitespaces.
  - Concatenates adjacent quoted and unquoted strings.
  - Backslashes inside single quotes are treated literally with no special escape semantics.
- **Double Quotes (`"..."`)**:
  - Preserves consecutive whitespace characters within quotes.
  - Backslash escaping inside double quotes:
    - `\"` escapes double quote (literal `"`).
    - `\\` escapes backslash (literal `\`).
    - Treats other backslashes literally (e.g. `\n` remains `\n`).
  - Preserves literal single quotes nested inside.
- **Backslash Escaping Outside Quotes**:
  - Escapes any immediately following character, stripping special meaning (e.g., `\ ` produces a literal space without argument splitting, `\'` and `\"` produce literal quotes).

### 4. Running External Programs
- Discovers executables via directories defined in the `$PATH` environment variable.
- Checks execute permissions (`os.X_OK`) before invocation.
- Spawns and executes programs with arguments using `subprocess.run()`.

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.x
- [uv](https://github.com/astral-sh/uv) (package manager)

### Running Locally
To launch the shell locally:

```sh
./your_program.sh
```

Or run directly with Python:

```sh
python -m app.main
```

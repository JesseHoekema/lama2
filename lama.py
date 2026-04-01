import sys
import os
from lexer import lex
from parser import Parser
from interpreter import Interpreter
from builtins_lama import get_globals

def run_code(code_str, interpreter):
    try:
        tokens = lex(code_str)
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter.interpret(ast.statements)
    except Exception as e:
        print(f"Error: {e}")

def run_file(filename):
    try:
        with open(filename, 'r') as f:
            code = f.read()

        interpreter = Interpreter(get_globals())
        run_code(code, interpreter)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

def run_repl():
    print("🦙 LAMA REPL v1.0")
    print("Type 'exit' or 'quit' to exit.")

    interpreter = Interpreter(get_globals())

    while True:
        try:
            line = input("lama> ")
            if line.strip() in ("exit", "quit"):
                break
            run_code(line, interpreter)
        except (KeyboardInterrupt, EOFError):
            print()
            break

def print_usage():
    print("🦙 LAMA Language CLI")
    print()
    print("Usage:")
    print("  lama run <file.lama>          Run a Lama script")
    print("  lama repl                     Start the Lama REPL")
    print()
    print("  lama install                  Install all deps from lama.json")
    print("  lama install <name>           Install a package and add to lama.json")
    print("  lama uninstall <name>         Remove a package from modules/")
    print("  lama list                     List installed packages")
    print("  lama packages                 List all available packages")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    # ── Package management ───────────────────────────────────────────────
    if command == "install":
        from package_manager import install_package, install_all
        if len(sys.argv) >= 3:
            print(f"🦙 Installing '{sys.argv[2]}'…")
            install_package(sys.argv[2])
        else:
            print("🦙 Installing dependencies from lama.json…")
            install_all()
        return

    if command == "uninstall":
        from package_manager import uninstall_package
        if len(sys.argv) < 3:
            print("Usage: lama uninstall <name>")
            sys.exit(1)
        uninstall_package(sys.argv[2])
        return

    if command == "list":
        from package_manager import list_packages
        list_packages()
        return

    if command == "packages":
        from package_manager import list_available
        list_available()
        return

    # ── Script / REPL ────────────────────────────────────────────────────
    if command == "run" and len(sys.argv) >= 3:
        run_file(sys.argv[2])
    elif command == "repl":
        run_repl()
    elif command.endswith(".lama") and len(sys.argv) == 2:
        run_file(command)
    else:
        print_usage()

if __name__ == "__main__":
    main()
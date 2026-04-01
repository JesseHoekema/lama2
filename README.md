# LAMA Language

LAMA is a powerful, beginner-friendly programming language built from scratch in Python. It combines the elegant, readable syntax of Python with the modern project structure and package management of Node.js.

---

## Top Features
- **Pythonic Syntax**: Clean, indentation-based scoping. No curly braces or semicolons required!
- **Node-style Package Manager**: Manage dependencies via `lama.json` and a `modules/` folder (like `node_modules`).
- **Standard Library**: Built-in modules for `math`, `time`, `string`, and `file` I/O.
- **Robust Exception Handling**: Native `try/catch` blocks for error management.
- **OOP Support**: Simple class-based object-oriented programming.

---

## Installation
To install the LAMA CLI globally:

1. **Clone the repo** and enter the directory.
2. **Install via pip**:
   ```bash
   pip3 install -e .
   ```
3. **Verify**:
   ```bash
   lama --help
   ```

---

## Quick Start
Initializing a new LAMA project is as easy as `npm init`:

```bash
mkdir my-app && cd my-app
lama init
lama run index.lama
```

### Example `index.lama`:
```lama
import time

fn greet(name):
    say "Hello, {name}! Welcome to LAMA."

say "=== MY PROJECT ==="
greet("Developer")
say "Unix Time: " + str(time.now())
```

---

## Package Management
Install packages directly from GitHub or the internal registry:

```bash
# Install from registry
lama install colors

# Install from any GitHub repo
lama install user/repo
```

Your dependencies are tracked in **`lama.json`**:
```json
{
  "name": "my-project",
  "version": "1.0.0",
  "main": "index.lama",
  "dependencies": {
    "colors": "1.0.0",
    "greet": {
      "source": "https://github.com/user/greet"
    }
  }
}
```

---

## Documentation
For a full list of commands, operators, and built-ins, see the [Documentation](docs.md).

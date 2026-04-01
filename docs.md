# 🦙 LAMA Language Documentation

LAMA is a dynamically-typed, beginner-friendly programming language designed to be readable and extendable. It heavily features a Python-like syntax using indentation for scoping block structures.

This document describes all available features, commands, syntax, and built-ins.

---

## 1. Basics & Variables
Variables in LAMA are dynamically typed. You do not need to use a keyword like `var` or `let`.
```lama
name = "Jesse"
age = 15
isCool = true
```

## 2. Output
You can print to the standard output using the `say` command or the built-in `print` function.
```lama
say "Hello World"
say name
say "Age: " + str(age)
```

## 3. Comments
LAMA currently only supports single-line comments using the `#` symbol.
```lama
# This is a comment
```

## 4. Operators
### Arithmetic
- `+` (Addition - also concatenates strings and lists)
- `-` (Subtraction)
- `*` (Multiplication)
- `/` (Division)
- `%` (Modulo)

### Logical and Comparison
- `==`, `!=`, `>`, `<`, `>=`, `<=`
- `and`, `or`, `not`

## 5. Control Flow
### Conditions
Conditionals use `if`, `elif`, and `else` followed by a colon and an indented block.
```lama
if x > 10:
    say "Greater than 10"
elif x == 10:
    say "Exactly 10"
else:
    say "Less than 10"
```

### Loops
LAMA supports `while` and `for` loops.
```lama
# While loop
c = 3
while c > 0:
    say c
    c = c - 1

# For Range loop
for i in range(0, 5):
    say i

# For In List loop
nums = [1, 2, 3]
for n in nums:
    say n
```

## 6. Functions
Functions are defined using the `fn` keyword.
```lama
fn add(a, b):
    return a + b

say add(5, 5)
```

## 7. Data Structures
### Lists
A dynamically sized contiguous array of objects.
```lama
myList = [1, 2, 3]
myList.append(4)
myList.remove(2)
say myList[0]
```

### Dictionaries
A key-value map. Keys must be strings.
```lama
user = {
    "name": "Jesse",
    "age": 15
}
say user["name"]
```

## 8. Strings interpolation
You can embed variables inside strings directly by wrapping the variable name in `{}`.
```lama
say "Hello {name}"
```

## 9. Classes
LAMA supports simple Class-based object-oriented programming. The constructor must be named `init` and accept `self` as the first argument.
```lama
class User:
    fn init(self, name):
        self.name = name

    fn greet(self):
        say "Hello " + self.name

u = User("Jesse")
u.greet()
```

## 10. Exception Handling
Code that might raise an error can be wrapped in a `try/catch` block.
```lama
try:
    x = 10 / 0
catch e:
    say "Error occurred: " + e
```

## 11. Modules & Imports
You can import modules using `import` or specific keys using `from ... import`.
```lama
import math
from time import sleep

say "Random: " + str(math.random())
sleep(1000) # Sleep for 1000 ms
```

## 12. Package Manager (LAMA CLI)
LAMA comes with a built-in package manager to install modules from GitHub or the internal registry.

### CLI Commands:
- `lama install <name>`: Install a package (e.g., `lama install colors` or `lama install user/repo`).
- `lama install`: Install all dependencies listed in `lama.json`.
- `lama uninstall <name>`: Remove an installed package.
- `lama list`: Show all currently installed packages.
- `lama packages`: Show available built-in packages.

### Creating & Publishing a Module
To make your code available for others to install:

1.  **Create a GitHub Repository**: Make a public repository (e.g., `myname/mytoolkit`).
2.  **Add a `lama.json` (Recommended)**: Create a `lama.json` file at the root of your repository to define the module name and entry point:
    ```json
    {
      "name": "toolkit",
      "main": "index.lama"
    }
    ```
    - `name`: The name users will use to `import` it.
    - `main`: The file that contains the module code.
3.  **Fallback (No lama.json)**: If you don't add a manifest, LAMA will look for `toolkit.lama`, `main.lama`, or `index.lama` at the root.
4.  **Push to GitHub**: Ensure your code is on the `main` or `master` branch.
5.  **Install**: Others can now install your module using:
    ```bash
    lama install myname/mytoolkit
    ```

### Using Your Module
Once installed, a module is imported by its name (from `lama.json` or the repo name):
```lama
import toolkit
toolkit.do_something()
```

#### Handling Hyphens and Aliases
If a module name contains hyphens (like `my-cool-repo`) and doesn't have a `lama.json` override, you can use a string import and an alias:
```lama
import "my-cool-repo" as repo
repo.start()
```

---

## Built-In Functions
LAMA provides several global functions out of the box:
- `open(filepath, mode)`: Opens and returns a `LamaFile` object. Modes include `r`, `w`, `a`.
- `print(args)`: An alternative to `say` that can accept multiple arguments.
- `str(val)`: Converts `val` to a string.
- `int(val)`: Converts `val` to an integer.
- `float(val)`: Converts `val` to a float.
- `len(val)`: Returns the length of a string, list, or dict.

## Standard Libraries
### `math`
- `math.add(a, b)`: Adds a and b.
- `math.sub(a, b)`: Subtracts b from a.
- `math.random()`: Returns a random float between `0.0` and `1.0`.
- `math.pi`: The mathematical constant Pi.

### `time`
- `time.now()`: Returns the current UNIX epoch time.
- `time.sleep(ms)`: Sleeps the current thread for `ms` milliseconds.

### `string`
- `string.upper(s)`: Returns the string uppercase.
- `string.lower(s)`: Returns the string lowercase.
- `string.split(s, sep)`: Splits the string by `sep` returning a list.

### `File` Object Data
Objects returned by `open()` have the following methods:
- `read()`: Returns the file's content as a string.
- `write(data)`: Writes the `data` to the file.
- `close()`: Saves and closes the file stream.

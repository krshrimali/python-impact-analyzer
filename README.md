# Python Impact Analyzer

A tool that analyzes Python code to identify functions that would be impacted by changes to a specific function or code location.

## Features

- Analyzes Python code to build a dependency graph between functions and methods
- Identifies which functions would be impacted by changes to a specific function
- Supports analyzing individual files or entire directories
- Handles object-oriented code with classes and methods
- Can identify impacts based on function name or line number

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/python-impact.git
cd python-impact

# Build the project
cargo build --release

# The binary will be available at target/release/python-impact
```

## Usage

```bash
# Analyze a single Python file
python-impact --path path/to/your/file.py

# Analyze a directory (non-recursive)
python-impact --path path/to/your/directory

# Analyze a directory recursively
python-impact --path path/to/your/directory --recursive

# Analyze impacts of a specific function
python-impact --path path/to/your/file.py --function function_name

# For class methods, use the format ClassName.method_name
python-impact --path path/to/your/file.py --function ClassName.method_name

# Analyze impacts of code at a specific line
python-impact --path path/to/your/file.py --line 42
```

## Examples

### Analyzing a Simple Function

If you have a Python file with functions that call each other:

```python
def add(a, b):
    return a + b

def calculate(a, b):
    result = add(a, b)
    return result * 2

def main():
    print(calculate(5, 3))
```

You can analyze the impact of changing the `add` function:

```bash
python-impact --path example.py --function add
```

Output:
```
Target Function:
  add (example.py:1)

Impacted Functions:
  calculate (example.py:4)
  main (example.py:8)
```

### Analyzing Object-Oriented Code

The tool also works with classes and methods:

```python
class Calculator:
    def add(self, a, b):
        return a + b
    
    def calculate(self, a, b):
        return self.add(a, b) * 2

def main():
    calc = Calculator()
    print(calc.calculate(5, 3))
```

You can analyze the impact of changing the `Calculator.add` method:

```bash
python-impact --path example.py --function Calculator.add
```

Output:
```
Target Function:
  Calculator.add (example.py:2)

Impacted Functions:
  Calculator.calculate (example.py:5)
  main (example.py:8)
```

## How It Works

The tool uses the following process to analyze Python code:

1. Parse the Python code using the tree-sitter parser
2. Identify all function and method definitions
3. Build a dependency graph by analyzing function calls
4. When analyzing impacts, traverse the dependency graph in reverse to find functions that depend on the target function

## Limitations

- The tool analyzes static code and may not capture all dynamic dependencies
- It doesn't track dependencies through variables or function pointers
- It may not handle all Python language features, especially more advanced metaprogramming techniques

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
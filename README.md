# Python Impact Analyzer

A tool that analyzes Python code to identify functions that would be impacted by changes to a specific function or code location.

## Features

- Analyzes Python code to build a dependency graph between functions and methods
- Identifies which functions would be impacted by changes to a specific function
- Supports analyzing individual files or entire directories
- Handles object-oriented code with classes and methods
- Can identify impacts based on function name or line number
- Generates visual dependency graphs to help understand function relationships

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

# Generate a visualization of function impacts
python-impact --path path/to/your/file.py --function function_name --visualize

# Specify an output file for the visualization
python-impact --path path/to/your/file.py --function function_name --visualize --output my_graph.dot

# Generate a visualization of the entire dependency graph
python-impact --path path/to/your/file.py --visualize
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

## Visualizing Dependencies

The tool can generate visual representations of function dependencies to help you understand the relationships between functions in your codebase.

### Generating Visualizations

To generate a visualization of the impact of a specific function:

```bash
python-impact --path path/to/your/file.py --function function_name --visualize
```

This will create a DOT file (e.g., `function_name_impact.dot`) that represents the dependency graph. The graph shows the target function and all functions that would be impacted by changes to it.

You can specify a custom output file:

```bash
python-impact --path path/to/your/file.py --function function_name --visualize --output my_graph.dot
```

### Viewing Visualizations

The generated DOT files can be viewed using various tools:

1. **Graphviz**: Convert the DOT file to an image format
   ```bash
   dot -Tpng function_name_impact.dot -o function_name_impact.png
   ```

2. **Online DOT viewers**: Upload the DOT file to online viewers like [WebGraphviz](http://www.webgraphviz.com/)

3. **IDE plugins**: Many IDEs have plugins for viewing DOT files

### Interpreting the Graph

In the visualization:
- Each node represents a function or method
- Edges (arrows) show dependencies between functions
- By default, arrows point from a function to the functions it impacts
- The target function is typically at the top of the graph

### Example Visualization

For the example code:

```python
def add(a, b):
    return a + b

def calculate(a, b):
    result = add(a, b)
    return result * 2

def main():
    print(calculate(5, 3))
```

A visualization of the impact of the `add` function would show arrows from `add` to `calculate` and from `calculate` to `main`, indicating that changes to `add` would impact both `calculate` and `main`.

## How It Works

The tool uses the following process to analyze Python code:

1. Parse the Python code using the tree-sitter parser
2. Identify all function and method definitions
3. Build a dependency graph by analyzing function calls
4. When analyzing impacts, traverse the dependency graph in reverse to find functions that depend on the target function
5. For visualizations, generate a DOT format representation of the relevant portion of the dependency graph

## Continuous Integration

This project uses GitHub Actions for continuous integration. All tests are automatically run on every pull request to ensure code quality and prevent regressions.

The CI workflow:
- Builds the project
- Runs all tests
- Reports any test failures

You can see the workflow configuration in the `.github/workflows/rust-tests.yml` file.

## Limitations

- The tool analyzes static code and may not capture all dynamic dependencies
- It doesn't track dependencies through variables or function pointers
- It may not handle all Python language features, especially more advanced metaprogramming techniques

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Python Impact Analyzer: Algorithm Documentation

## Overview

The Python Impact Analyzer is a tool designed to help developers understand the potential impact of code changes in Python projects. When modifying a function or a specific piece of code, it's crucial to know which other parts of the codebase might be affected. This tool analyzes Python code to identify dependencies between functions and methods, and determines which functions would be impacted by changes to a specific function or code location.

## Key Features

- **Function Dependency Analysis**: Identifies direct dependencies between functions through function calls
- **If Condition Impact Analysis**: Detects potential impacts through shared variables in if conditions
- **Object-Oriented Code Support**: Handles classes, methods, and inheritance relationships
- **Visualization**: Generates visual representations of dependency graphs

## High-Level Architecture

The Python Impact Analyzer is built with a modular architecture consisting of the following components:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Code Analyzer  │────▶│  Dependency     │────▶│  Impact         │
│  (Parser)       │     │  Graph Builder  │     │  Analyzer       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Visualization  │
                                               │  Generator      │
                                               └─────────────────┘
```

1. **Code Analyzer**: Parses Python code using tree-sitter to extract function definitions, function calls, and if conditions.
2. **Dependency Graph Builder**: Constructs a directed graph representing dependencies between functions.
3. **Impact Analyzer**: Traverses the dependency graph to identify functions that would be impacted by changes.
4. **Visualization Generator**: Creates visual representations of the dependency graph in DOT format.

## Detailed Algorithm

### 1. Code Parsing and Analysis

The first step is to parse the Python code and extract relevant information:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Read Python    │────▶│  Parse with     │────▶│  Extract        │
│  Source Files   │     │  tree-sitter    │     │  Definitions    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Extract        │
                                               │  Function Calls │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Extract If     │
                                               │  Conditions     │
                                               └─────────────────┘
```

#### 1.1 Reading Source Files

The tool reads Python source files from the specified path. If a directory is provided, it can recursively scan all Python files in the directory.

#### 1.2 Parsing with tree-sitter

The tool uses the tree-sitter parser to parse Python code into an abstract syntax tree (AST). This provides a structured representation of the code that can be traversed to extract information.

#### 1.3 Extracting Function Definitions

The tool traverses the AST to identify function and method definitions. For each function or method, it extracts:
- Function name
- File path
- Start line
- End line

For methods within classes, it constructs the full name in the format `ClassName.method_name`.

#### 1.4 Extracting Function Calls

The tool traverses the AST again to identify function calls within each function. It tracks:
- The calling function
- The called function
- Special handling for method calls (e.g., `self.method()`)

#### 1.5 Extracting If Conditions

The tool identifies if statements and extracts:
- The condition text
- Variables used in the condition
- The function containing the condition
- The line number of the condition

### 2. Building the Dependency Graph

Once the code is parsed and analyzed, the tool builds a directed graph representing dependencies between functions:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Create Graph   │────▶│  Add Function   │────▶│  Add Dependency │
│  Structure      │     │  Nodes          │     │  Edges          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

#### 2.1 Creating the Graph Structure

The tool uses the petgraph library to create a directed graph (DiGraph) structure.

#### 2.2 Adding Function Nodes

Each function or method is added as a node in the graph. The node is identified by a unique key in the format `file_path:function_name`.

#### 2.3 Adding Dependency Edges

For each function call identified, an edge is added from the calling function to the called function. This represents a dependency relationship: the calling function depends on the called function.

### 3. Analyzing Function Impacts

To determine which functions would be impacted by changes to a specific function, the tool analyzes the dependency graph:

```
┌─────────────────┐     ┌─────────────────┐
│  Reverse        │────▶│  Traverse Graph │
│  Dependency     │     │  from Target    │
│  Graph          │     │  Function       │
└─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │  Collect        │
                        │  Impacted       │
                        │  Functions      │
                        └─────────────────┘
```

#### 3.1 Reversing the Dependency Graph

To find functions impacted by changes to a target function, the tool reverses the dependency graph. In the reversed graph, edges point from a function to the functions that depend on it (i.e., functions that would be impacted by changes to it).

#### 3.2 Traversing the Graph

Starting from the target function, the tool performs a depth-first search (DFS) of the reversed graph. Each function reached during this traversal would be impacted by changes to the target function.

#### 3.3 Collecting Impacted Functions

The functions reached during the graph traversal are collected into a set of impacted functions.

### 4. Analyzing If Condition Impacts

In addition to direct function call dependencies, the tool analyzes potential impacts through shared variables in if conditions:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Extract        │────▶│  Identify       │────▶│  Find Functions │
│  Variables from │     │  Shared         │     │  with Shared    │
│  If Conditions  │     │  Variables      │     │  Variables      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

#### 4.1 Extracting Variables from If Conditions

For each if condition, the tool extracts the variables used in the condition. It filters out Python keywords like `True`, `False`, `None`, etc.

#### 4.2 Identifying Shared Variables

The tool identifies variables that are used in if conditions across different functions.

#### 4.3 Finding Functions with Shared Variables

When analyzing the impact of changes to a function, the tool identifies other functions that use the same variables in their if conditions. These functions might be impacted by changes to the target function, even if there's no direct function call dependency.

### 5. Generating Visualizations

To help developers understand the dependencies and potential impacts, the tool can generate visualizations:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Generate       │────▶│  Create DOT     │────▶│  Save to        │
│  Subgraph for   │     │  Representation │     │  File           │
│  Target Function│     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

#### 5.1 Generating a Subgraph

For a specific target function, the tool generates a subgraph containing only the target function and the functions it impacts.

#### 5.2 Creating a DOT Representation

The tool converts the graph or subgraph to DOT format, which is a text-based graph description language.

#### 5.3 Saving to File

The DOT representation is saved to a file, which can be visualized using tools like Graphviz.

## Algorithm in Action: An Example

Let's walk through a simple example to illustrate how the algorithm works:

```python
def add(a, b):
    return a + b

def calculate(a, b):
    result = add(a, b)
    return result * 2

def main():
    print(calculate(5, 3))
```

### Step 1: Parse the Code

The tool parses the code and identifies three functions: `add`, `calculate`, and `main`.

### Step 2: Build the Dependency Graph

The tool builds a dependency graph with the following edges:
- `calculate` depends on `add` (because `calculate` calls `add`)
- `main` depends on `calculate` (because `main` calls `calculate`)

```
add <── calculate <── main
```

### Step 3: Analyze Impacts

If we want to know which functions would be impacted by changes to `add`, the tool reverses the graph and traverses it starting from `add`:

```
add ──> calculate ──> main
```

The traversal reaches `calculate` and `main`, so these functions would be impacted by changes to `add`.

## If Condition Impact Example

Let's look at an example with if conditions:

```python
def check_condition(value):
    if value > 10:
        return "Greater than 10"
    else:
        return "Less than or equal to 10"

def process_value(value):
    if value % 2 == 0:
        return "Even"
    else:
        return "Odd"
```

### Step 1: Extract Variables from If Conditions

The tool extracts the variable `value` from the if conditions in both functions.

### Step 2: Identify Shared Variables

The tool identifies that the variable `value` is used in if conditions in both `check_condition` and `process_value`.

### Step 3: Analyze Impacts

If we want to know which functions would be impacted by changes to `check_condition`, the tool identifies that `process_value` uses the same variable `value` in its if condition. Therefore, changes to `check_condition` might impact `process_value`, even though there's no direct function call dependency.

## Conclusion

The Python Impact Analyzer uses a combination of static code analysis, graph theory, and variable tracking to identify potential impacts of code changes. By analyzing both direct function call dependencies and shared variables in if conditions, it provides a comprehensive view of the potential ripple effects of code changes.

This helps developers make more informed decisions when modifying code, reducing the risk of unintended consequences and making the codebase more maintainable.
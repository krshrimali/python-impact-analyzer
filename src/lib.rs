use std::fs;
use std::path::{Path, PathBuf};
use std::collections::{HashMap, HashSet};
use anyhow::{Result, Context, anyhow};
use colored::*;
use petgraph::graph::{DiGraph, NodeIndex};
use petgraph::visit::Dfs;
use tree_sitter::{Parser as TsParser, Node, TreeCursor};

// Export the visualization module
pub mod visualization;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct FunctionInfo {
    pub name: String,
    pub file_path: PathBuf,
    pub start_line: usize,
    pub end_line: usize,
}

pub struct CodeAnalyzer {
    parser: TsParser,
    pub functions: HashMap<String, FunctionInfo>,
    pub dependency_graph: DiGraph<String, ()>,
    pub node_indices: HashMap<String, NodeIndex>,
}

impl std::fmt::Debug for CodeAnalyzer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("CodeAnalyzer")
            .field("functions", &self.functions)
            .field("dependency_graph", &self.dependency_graph)
            .field("node_indices", &self.node_indices)
            .finish_non_exhaustive()
    }
}

impl CodeAnalyzer {
    pub fn new() -> Result<Self> {
        let mut parser = TsParser::new();
        parser.set_language(tree_sitter_python::language())
            .context("Failed to set Python language for parser")?;

        Ok(CodeAnalyzer {
            parser,
            functions: HashMap::new(),
            dependency_graph: DiGraph::new(),
            node_indices: HashMap::new(),
        })
    }

    pub fn analyze_path(&mut self, path: &Path, recursive: bool) -> Result<()> {
        if path.is_dir() {
            if recursive {
                for entry in fs::read_dir(path)? {
                    let entry = entry?;
                    let path = entry.path();
                    if path.is_dir() {
                        self.analyze_path(&path, recursive)?;
                    } else if let Some(ext) = path.extension() {
                        if ext == "py" {
                            self.analyze_file(&path)?;
                        }
                    }
                }
            }
        } else if let Some(ext) = path.extension() {
            if ext == "py" {
                self.analyze_file(path)?;
            }
        }

        Ok(())
    }

    pub fn analyze_file(&mut self, file_path: &Path) -> Result<()> {
        println!("Analyzing file: {}", file_path.display());

        let source_code = fs::read_to_string(file_path)
            .with_context(|| format!("Failed to read file: {}", file_path.display()))?;

        let tree = self.parser.parse(&source_code, None)
            .context("Failed to parse Python code")?;

        let root_node = tree.root_node();

        // First pass: collect all function definitions
        self.collect_functions(root_node, file_path, &source_code)?;

        // Second pass: analyze function calls and build dependency graph
        self.analyze_function_calls(root_node, file_path, &source_code)?;

        Ok(())
    }

    fn collect_functions(&mut self, node: Node, file_path: &Path, source_code: &str) -> Result<()> {
        let mut cursor = node.walk();
        self.traverse_tree_for_functions(&mut cursor, file_path, source_code)?;
        Ok(())
    }

    fn traverse_tree_for_functions(&mut self, cursor: &mut TreeCursor, file_path: &Path, source_code: &str) -> Result<()> {
        let node = cursor.node();

        if node.kind() == "function_definition" {
            // Find the function name
            let mut name_node = None;
            for i in 0..node.child_count() {
                if let Some(child) = node.child(i) {
                    if child.kind() == "identifier" {
                        name_node = Some(child);
                        break;
                    }
                }
            }

            if let Some(name_node) = name_node {
                let name = self.get_node_text(name_node, source_code);
                let start_line = node.start_position().row + 1; // 1-indexed line numbers
                let end_line = node.end_position().row + 1;

                let function_key = format!("{}:{}", file_path.display(), name);

                let function_info = FunctionInfo {
                    name: name.to_string(),
                    file_path: file_path.to_path_buf(),
                    start_line,
                    end_line,
                };

                self.functions.insert(function_key.clone(), function_info);

                // Add node to dependency graph if it doesn't exist
                if !self.node_indices.contains_key(&function_key) {
                    let idx = self.dependency_graph.add_node(function_key.clone());
                    self.node_indices.insert(function_key, idx);
                }
            }
        } else if node.kind() == "class_definition" {
            // Find the class name
            let mut name_node = None;
            for i in 0..node.child_count() {
                if let Some(child) = node.child(i) {
                    if child.kind() == "identifier" {
                        name_node = Some(child);
                        break;
                    }
                }
            }

            if let Some(name_node) = name_node {
                let class_name = self.get_node_text(name_node, source_code);

                // Process methods within the class
                for i in 0..node.child_count() {
                    if let Some(child) = node.child(i) {
                        if child.kind() == "block" {
                            let mut method_cursor = child.walk();
                            self.traverse_tree_for_class_methods(&mut method_cursor, file_path, source_code, &class_name)?;
                        }
                    }
                }
            }
        }

        // Continue traversing
        if cursor.goto_first_child() {
            loop {
                self.traverse_tree_for_functions(cursor, file_path, source_code)?;
                if !cursor.goto_next_sibling() {
                    break;
                }
            }
            cursor.goto_parent();
        }

        Ok(())
    }

    fn traverse_tree_for_class_methods(&mut self, cursor: &mut TreeCursor, file_path: &Path, source_code: &str, class_name: &str) -> Result<()> {
        let node = cursor.node();

        if node.kind() == "function_definition" {
            // Find the method name
            let mut name_node = None;
            for i in 0..node.child_count() {
                if let Some(child) = node.child(i) {
                    if child.kind() == "identifier" {
                        name_node = Some(child);
                        break;
                    }
                }
            }

            if let Some(name_node) = name_node {
                let method_name = self.get_node_text(name_node, source_code);
                let full_name = format!("{}.{}", class_name, method_name);
                let start_line = node.start_position().row + 1;
                let end_line = node.end_position().row + 1;

                let function_key = format!("{}:{}", file_path.display(), full_name);

                let function_info = FunctionInfo {
                    name: full_name,
                    file_path: file_path.to_path_buf(),
                    start_line,
                    end_line,
                };

                self.functions.insert(function_key.clone(), function_info);

                // Add node to dependency graph if it doesn't exist
                if !self.node_indices.contains_key(&function_key) {
                    let idx = self.dependency_graph.add_node(function_key.clone());
                    self.node_indices.insert(function_key, idx);
                }
            }
        }

        // Continue traversing
        if cursor.goto_first_child() {
            loop {
                self.traverse_tree_for_class_methods(cursor, file_path, source_code, class_name)?;
                if !cursor.goto_next_sibling() {
                    break;
                }
            }
            cursor.goto_parent();
        }

        Ok(())
    }

    fn analyze_function_calls(&mut self, node: Node, file_path: &Path, source_code: &str) -> Result<()> {
        let mut cursor = node.walk();
        self.traverse_tree_for_calls(&mut cursor, file_path, source_code, None)?;
        Ok(())
    }

    fn traverse_tree_for_calls(&mut self, cursor: &mut TreeCursor, file_path: &Path, source_code: &str, current_function: Option<String>) -> Result<()> {
        let node = cursor.node();

        let new_current_function = if node.kind() == "function_definition" {
            // Find the function name
            let mut name_node = None;
            for i in 0..node.child_count() {
                if let Some(child) = node.child(i) {
                    if child.kind() == "identifier" {
                        name_node = Some(child);
                        break;
                    }
                }
            }

            if let Some(name_node) = name_node {
                let name = self.get_node_text(name_node, source_code);
                Some(format!("{}:{}", file_path.display(), name))
            } else {
                current_function.clone()
            }
        } else if node.kind() == "class_definition" {
            // Find the class name
            let mut name_node = None;
            for i in 0..node.child_count() {
                if let Some(child) = node.child(i) {
                    if child.kind() == "identifier" {
                        name_node = Some(child);
                        break;
                    }
                }
            }

            let class_name = if let Some(name_node) = name_node {
                self.get_node_text(name_node, source_code)
            } else {
                "UnknownClass".to_string()
            };

            // Process methods within the class
            for i in 0..node.child_count() {
                if let Some(child) = node.child(i) {
                    if child.kind() == "block" {
                        let mut method_cursor = child.walk();
                        self.traverse_tree_for_class_method_calls(&mut method_cursor, file_path, source_code, &class_name)?;
                    }
                }
            }

            current_function.clone()
        } else if node.kind() == "call" {
            // Process function call
            if let Some(current_function) = &current_function {
                let called_function = self.extract_function_call(node, source_code);

                // Extract the current class name if this is a method call
                let current_class_name = if let Some(info) = self.functions.get(current_function) {
                    if info.name.contains('.') {
                        // Extract the class name from ClassName.method_name
                        let parts: Vec<&str> = info.name.split('.').collect();
                        if parts.len() >= 2 {
                            Some(parts[0].to_string())
                        } else {
                            None
                        }
                    } else {
                        None
                    }
                } else {
                    None
                };

                // If this is a self.method call and we're in a class method, construct the full class.method name
                let full_called_function = if called_function.starts_with("self.") {
                    if let Some(class_name) = current_class_name.clone() {
                        let method_name = &called_function[5..];
                        let full_name = format!("{}.{}", class_name, method_name);
                        println!("DEBUG: Found self.method call: {} -> {} in {}", called_function, full_name, current_function);
                        full_name
                    } else {
                        println!("DEBUG: Found self.method call but no class context: {}", called_function);
                        called_function
                    }
                } else {
                    called_function
                };

                if let Some(called_function_key) = self.find_function_key(&full_called_function, file_path, Some(current_function)) {
                    // Add edge to dependency graph
                    if let (Some(&caller_idx), Some(&callee_idx)) = (
                        self.node_indices.get(current_function),
                        self.node_indices.get(&called_function_key),
                    ) {
                        println!("DEBUG: Adding dependency: {} -> {}", current_function, called_function_key);
                        self.dependency_graph.add_edge(caller_idx, callee_idx, ());
                    } else {
                        println!("DEBUG: Failed to get node indices for {} -> {}", current_function, called_function_key);
                    }
                } else {
                    println!("DEBUG: Could not find function key for {}", full_called_function);
                }
            }

            current_function.clone()
        } else {
            current_function.clone()
        };

        // Continue traversing
        if cursor.goto_first_child() {
            loop {
                self.traverse_tree_for_calls(cursor, file_path, source_code, new_current_function.clone())?;
                if !cursor.goto_next_sibling() {
                    break;
                }
            }
            cursor.goto_parent();
        }

        Ok(())
    }

    fn traverse_tree_for_class_method_calls(&mut self, cursor: &mut TreeCursor, file_path: &Path, source_code: &str, class_name: &str) -> Result<()> {
        let node = cursor.node();

        if node.kind() == "function_definition" {
            // Find the method name
            let mut name_node = None;
            for i in 0..node.child_count() {
                if let Some(child) = node.child(i) {
                    if child.kind() == "identifier" {
                        name_node = Some(child);
                        break;
                    }
                }
            }

            if let Some(name_node) = name_node {
                let method_name = self.get_node_text(name_node, source_code);
                let full_name = format!("{}.{}", class_name, method_name);
                let current_function = format!("{}:{}", file_path.display(), full_name);

                // Process the method body for function calls
                for i in 0..node.child_count() {
                    if let Some(child) = node.child(i) {
                        if child.kind() == "block" {
                            let mut block_cursor = child.walk();
                            self.traverse_tree_for_class_method_calls_block(&mut block_cursor, file_path, source_code, class_name, &current_function)?;
                        }
                    }
                }
            }
        } else if node.kind() == "call" {
            // This is a function call within a class but outside any method
            // We don't have a current function context here
        }

        // Continue traversing
        if cursor.goto_first_child() {
            loop {
                self.traverse_tree_for_class_method_calls(cursor, file_path, source_code, class_name)?;
                if !cursor.goto_next_sibling() {
                    break;
                }
            }
            cursor.goto_parent();
        }

        Ok(())
    }

    fn traverse_tree_for_class_method_calls_block(&mut self, cursor: &mut TreeCursor, file_path: &Path, source_code: &str, class_name: &str, current_function: &str) -> Result<()> {
        let node = cursor.node();

        if node.kind() == "call" {
            // Process function call within a class method
            let mut function_name = None;
            let mut is_self_method = false;

            // Extract the function name
            for i in 0..node.child_count() {
                if let Some(child) = node.child(i) {
                    if child.kind() == "identifier" {
                        function_name = Some(self.get_node_text(child, source_code));
                        break;
                    } else if child.kind() == "attribute" {
                        let attribute_text = self.get_node_text(child, source_code);
                        if attribute_text.starts_with("self.") {
                            // This is a self.method call
                            is_self_method = true;
                            function_name = Some(attribute_text[5..].to_string());
                            break;
                        } else {
                            function_name = Some(attribute_text);
                            break;
                        }
                    }
                }
            }

            if let Some(func_name) = function_name {
                let called_function_key = if is_self_method {
                    // For self.method calls, construct the full class.method name
                    let full_name = format!("{}.{}", class_name, func_name);
                    let key = format!("{}:{}", file_path.display(), full_name);
                    if self.functions.contains_key(&key) {
                        Some(key)
                    } else {
                        // If the method is not found in the current class, check parent classes
                        // For simplicity, we'll just check all classes for a method with the same name
                        // In a real implementation, we would need to track class inheritance
                        let mut parent_method_key = None;
                        for (k, v) in &self.functions {
                            if v.name.ends_with(&format!(".{}", func_name)) {
                                parent_method_key = Some(k.clone());
                                break;
                            }
                        }
                        parent_method_key
                    }
                } else {
                    // For other function calls, use the regular find_function_key method
                    self.find_function_key(&func_name, file_path, Some(current_function))
                };

                if let Some(called_key) = called_function_key {
                    // Add edge to dependency graph
                    if let (Some(&caller_idx), Some(&callee_idx)) = (
                        self.node_indices.get(current_function),
                        self.node_indices.get(&called_key),
                    ) {
                        self.dependency_graph.add_edge(caller_idx, callee_idx, ());
                    }
                }
            }
        }

        // Continue traversing
        if cursor.goto_first_child() {
            loop {
                self.traverse_tree_for_class_method_calls_block(cursor, file_path, source_code, class_name, current_function)?;
                if !cursor.goto_next_sibling() {
                    break;
                }
            }
            cursor.goto_parent();
        }

        Ok(())
    }

    fn extract_function_call(&self, call_node: Node, source_code: &str) -> String {
        // Extract the function name from a call node
        for i in 0..call_node.child_count() {
            if let Some(child) = call_node.child(i) {
                if child.kind() == "identifier" {
                    return self.get_node_text(child, source_code);
                } else if child.kind() == "attribute" {
                    // Handle method calls like obj.method()
                    let attribute_text = self.get_node_text(child, source_code);

                    // Special handling for self.method calls
                    if attribute_text.starts_with("self.") {
                        // Extract just the method name after "self."
                        return attribute_text[5..].to_string();
                    }

                    return attribute_text;
                }
            }
        }

        "unknown_function".to_string()
    }

    fn find_function_key(&self, function_name: &str, current_file: &Path, current_function: Option<&str>) -> Option<String> {
        // First try exact match in current file
        let key = format!("{}:{}", current_file.display(), function_name);
        if self.functions.contains_key(&key) {
            return Some(key);
        }

        // If this is a method call within a class context, try to find the class method
        if let Some(current_func) = current_function {
            if let Some(info) = self.functions.get(current_func) {
                if info.name.contains('.') {
                    // Extract the class name from ClassName.method_name
                    let parts: Vec<&str> = info.name.split('.').collect();
                    if parts.len() >= 2 {
                        let class_name = parts[0];
                        // Try to find the method with the class name prefix
                        let class_method_key = format!("{}:{}.{}", current_file.display(), class_name, function_name);
                        if self.functions.contains_key(&class_method_key) {
                            return Some(class_method_key);
                        }
                    }
                }
            }
        }

        // Then try to find in any file
        for (k, v) in &self.functions {
            if v.name == function_name {
                return Some(k.clone());
            }
        }

        None
    }

    fn get_node_text(&self, node: Node, source_code: &str) -> String {
        let start_byte = node.start_byte();
        let end_byte = node.end_byte();

        source_code[start_byte..end_byte].to_string()
    }

    pub fn find_function_at_line(&self, file_path: &Path, line: usize) -> Option<String> {
        for (key, info) in &self.functions {
            if info.file_path == file_path && line >= info.start_line && line <= info.end_line {
                return Some(key.clone());
            }
        }

        None
    }

    pub fn find_impacted_functions(&self, function_key: &str) -> HashSet<String> {
        let mut impacted = HashSet::new();

        if let Some(&start_idx) = self.node_indices.get(function_key) {
            // Reverse the graph to find functions that depend on the target function
            let reversed_graph = petgraph::visit::Reversed(&self.dependency_graph);

            let mut dfs = Dfs::new(reversed_graph, start_idx);
            while let Some(nx) = dfs.next(reversed_graph) {
                let function = self.dependency_graph[nx].clone();
                if function != function_key {
                    impacted.insert(function);
                }
            }
        }

        impacted
    }

    pub fn print_impacted_functions(&self, function_key: &str) -> Result<()> {
        if !self.node_indices.contains_key(function_key) {
            return Err(anyhow!("Function not found: {}", function_key));
        }

        let impacted = self.find_impacted_functions(function_key);

        if let Some(info) = self.functions.get(function_key) {
            println!("\n{}", "Target Function:".green().bold());
            println!("  {} ({}:{})", info.name, info.file_path.display(), info.start_line);
        }

        println!("\n{}", "Impacted Functions:".yellow().bold());
        if impacted.is_empty() {
            println!("  No functions would be impacted by changes to this function.");
        } else {
            for function in impacted {
                if let Some(info) = self.functions.get(&function) {
                    println!("  {} ({}:{})", info.name, info.file_path.display(), info.start_line);
                }
            }
        }

        Ok(())
    }
}

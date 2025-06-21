use std::fs::File;
use std::io::Write;
use std::path::{Path, PathBuf};
use anyhow::{Result, Context};
use petgraph::dot::{Dot, Config};
use petgraph::graph::DiGraph;
use petgraph::visit::Reversed;

use crate::CodeAnalyzer;

/// Generates a DOT format representation of the dependency graph
pub fn generate_dot(
    analyzer: &CodeAnalyzer,
    _function_key: Option<&str>,
    reverse: bool,
) -> String {
    if reverse {
        // For impact visualization (what functions are impacted by this one)
        // we use the reversed graph
        let reversed_graph = Reversed(&analyzer.dependency_graph);
        let dot = Dot::with_config(&reversed_graph, &[Config::EdgeNoLabel]);
        format!("{:?}", dot)
    } else {
        // For dependency visualization (what functions this one depends on)
        let dot = Dot::with_config(&analyzer.dependency_graph, &[Config::EdgeNoLabel]);
        format!("{:?}", dot)
    }
}

/// Saves the dependency graph in DOT format to a file
pub fn save_dot_file(
    analyzer: &CodeAnalyzer,
    output_path: &Path,
    function_key: Option<&str>,
    reverse: bool,
) -> Result<PathBuf> {
    let dot_content = generate_dot(analyzer, function_key, reverse);

    let mut file = File::create(output_path)
        .with_context(|| format!("Failed to create output file: {}", output_path.display()))?;

    file.write_all(dot_content.as_bytes())
        .with_context(|| format!("Failed to write to output file: {}", output_path.display()))?;

    Ok(output_path.to_path_buf())
}

/// Generates a subgraph containing only the nodes related to a specific function
pub fn generate_impact_subgraph(
    analyzer: &CodeAnalyzer,
    function_key: &str,
) -> Result<DiGraph<String, ()>> {
    let mut subgraph = DiGraph::new();
    let mut node_map = std::collections::HashMap::new();

    // Add the target function node
    let target_idx = subgraph.add_node(function_key.to_string());
    node_map.insert(function_key, target_idx);

    // Get impacted functions
    let impacted = analyzer.find_impacted_functions(function_key);

    // Add impacted function nodes
    for func in &impacted {
        let idx = subgraph.add_node(func.clone());
        node_map.insert(func.as_str(), idx);
    }

    // Add edges
    if let Some(&start_idx) = analyzer.node_indices.get(function_key) {
        // For each impacted function, add an edge from the target to it
        for func in &impacted {
            if let Some(&func_idx) = analyzer.node_indices.get(func) {
                // Check if there's a direct edge in the original graph
                if analyzer.dependency_graph.edges_connecting(func_idx, start_idx).count() > 0 {
                    // Add the edge in our subgraph (but reversed, since we're showing impact)
                    if let (Some(&from_idx), Some(&to_idx)) = (
                        node_map.get(function_key),
                        node_map.get(func.as_str()),
                    ) {
                        subgraph.add_edge(from_idx, to_idx, ());
                    }
                }
            }
        }
    }

    Ok(subgraph)
}

/// Saves an impact visualization for a specific function
pub fn save_impact_visualization(
    analyzer: &CodeAnalyzer,
    function_key: &str,
    output_path: &Path,
) -> Result<PathBuf> {
    // Generate the subgraph
    let subgraph = generate_impact_subgraph(analyzer, function_key)?;

    // Convert to DOT format
    let dot = Dot::with_config(&subgraph, &[Config::EdgeNoLabel]);

    // Save to file
    let mut file = File::create(output_path)
        .with_context(|| format!("Failed to create output file: {}", output_path.display()))?;

    write!(file, "{:?}", dot)
        .with_context(|| format!("Failed to write to output file: {}", output_path.display()))?;

    Ok(output_path.to_path_buf())
}

/// Generates a human-readable label for a function key
pub fn get_function_label(analyzer: &CodeAnalyzer, function_key: &str) -> String {
    if let Some(info) = analyzer.functions.get(function_key) {
        format!("{} ({}:{})", info.name, info.file_path.display(), info.start_line)
    } else {
        function_key.to_string()
    }
}

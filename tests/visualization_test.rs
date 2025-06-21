use std::path::Path;
use anyhow::Result;
use std::fs;
use python_impact::CodeAnalyzer;
use python_impact::visualization;

#[test]
fn test_generate_dot() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/simple.py");
    
    analyzer.analyze_file(path)?;
    
    // Test generating DOT for the entire graph
    let dot = visualization::generate_dot(&analyzer, None, false);
    assert!(!dot.is_empty(), "Generated DOT should not be empty");
    assert!(dot.contains("digraph"), "Generated DOT should contain 'digraph'");
    
    // Test generating DOT for a specific function
    let add_key = format!("{}:{}", path.display(), "add");
    let dot = visualization::generate_dot(&analyzer, Some(&add_key), true);
    assert!(!dot.is_empty(), "Generated DOT should not be empty");
    assert!(dot.contains("digraph"), "Generated DOT should contain 'digraph'");
    
    Ok(())
}

#[test]
fn test_save_dot_file() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/simple.py");
    
    analyzer.analyze_file(path)?;
    
    // Test saving DOT file
    let output_path = Path::new("target/test_graph.dot");
    let result = visualization::save_dot_file(&analyzer, output_path, None, false)?;
    
    assert!(result.exists(), "Output file should exist");
    
    // Clean up
    fs::remove_file(output_path)?;
    
    Ok(())
}

#[test]
fn test_generate_impact_subgraph() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/simple.py");
    
    analyzer.analyze_file(path)?;
    
    // Test generating impact subgraph
    let add_key = format!("{}:{}", path.display(), "add");
    let subgraph = visualization::generate_impact_subgraph(&analyzer, &add_key)?;
    
    // The subgraph should have at least 2 nodes (add and calculate)
    assert!(subgraph.node_count() >= 2, "Subgraph should have at least 2 nodes");
    
    Ok(())
}

#[test]
fn test_save_impact_visualization() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/simple.py");
    
    analyzer.analyze_file(path)?;
    
    // Test saving impact visualization
    let add_key = format!("{}:{}", path.display(), "add");
    let output_path = Path::new("target/test_impact.dot");
    let result = visualization::save_impact_visualization(&analyzer, &add_key, output_path)?;
    
    assert!(result.exists(), "Output file should exist");
    
    // Clean up
    fs::remove_file(output_path)?;
    
    Ok(())
}

#[test]
fn test_complex_visualization() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/complex.py");
    
    analyzer.analyze_file(path)?;
    
    // Test generating impact visualization for a method
    let method_key = format!("{}:{}", path.display(), "Calculator.add");
    let output_path = Path::new("target/test_complex_impact.dot");
    let result = visualization::save_impact_visualization(&analyzer, &method_key, output_path)?;
    
    assert!(result.exists(), "Output file should exist");
    
    // Clean up
    fs::remove_file(output_path)?;
    
    Ok(())
}
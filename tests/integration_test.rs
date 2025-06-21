use std::path::Path;
use anyhow::Result;
use python_impact::CodeAnalyzer;

#[test]
fn test_simple_dependencies() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/simple.py");
    
    analyzer.analyze_file(path)?;
    
    // Test that changing 'add' impacts 'calculate'
    let add_key = format!("{}:{}", path.display(), "add");
    let impacted = analyzer.find_impacted_functions(&add_key);
    
    assert!(impacted.iter().any(|f| f.contains("calculate")), 
            "Changing 'add' should impact 'calculate'");
    
    // Test that changing 'calculate' impacts 'main'
    let calculate_key = format!("{}:{}", path.display(), "calculate");
    let impacted = analyzer.find_impacted_functions(&calculate_key);
    
    assert!(impacted.iter().any(|f| f.contains("main")), 
            "Changing 'calculate' should impact 'main'");
    
    // Test that changing 'multiply' impacts 'calculate'
    let multiply_key = format!("{}:{}", path.display(), "multiply");
    let impacted = analyzer.find_impacted_functions(&multiply_key);
    
    assert!(impacted.iter().any(|f| f.contains("calculate")), 
            "Changing 'multiply' should impact 'calculate'");
    
    Ok(())
}

#[test]
fn test_complex_dependencies() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/complex.py");
    
    analyzer.analyze_file(path)?;
    
    // Test that changing Calculator.add impacts Calculator.calculate
    let add_key = format!("{}:{}", path.display(), "Calculator.add");
    let impacted = analyzer.find_impacted_functions(&add_key);
    
    assert!(impacted.iter().any(|f| f.contains("Calculator.calculate")), 
            "Changing 'Calculator.add' should impact 'Calculator.calculate'");
    
    // Test that changing Calculator.calculate impacts AdvancedCalculator.advanced_calculate
    let calc_key = format!("{}:{}", path.display(), "Calculator.calculate");
    let impacted = analyzer.find_impacted_functions(&calc_key);
    
    assert!(impacted.iter().any(|f| f.contains("AdvancedCalculator.advanced_calculate")), 
            "Changing 'Calculator.calculate' should impact 'AdvancedCalculator.advanced_calculate'");
    
    // Test that changing process_data impacts main
    let process_key = format!("{}:{}", path.display(), "process_data");
    let impacted = analyzer.find_impacted_functions(&process_key);
    
    assert!(impacted.iter().any(|f| f.contains("main")), 
            "Changing 'process_data' should impact 'main'");
    
    Ok(())
}

#[test]
fn test_conditional_dependencies() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/conditional.py");
    
    analyzer.analyze_file(path)?;
    
    // Test that changing is_valid_input impacts process_value
    let valid_key = format!("{}:{}", path.display(), "is_valid_input");
    let impacted = analyzer.find_impacted_functions(&valid_key);
    
    assert!(impacted.iter().any(|f| f.contains("process_value")), 
            "Changing 'is_valid_input' should impact 'process_value'");
    
    // Test that changing process_negative impacts process_value
    let neg_key = format!("{}:{}", path.display(), "process_negative");
    let impacted = analyzer.find_impacted_functions(&neg_key);
    
    assert!(impacted.iter().any(|f| f.contains("process_value")), 
            "Changing 'process_negative' should impact 'process_value'");
    
    // Test that changing process_value impacts calculate_results
    let process_key = format!("{}:{}", path.display(), "process_value");
    let impacted = analyzer.find_impacted_functions(&process_key);
    
    assert!(impacted.iter().any(|f| f.contains("calculate_results")), 
            "Changing 'process_value' should impact 'calculate_results'");
    
    Ok(())
}
use std::path::Path;
use anyhow::Result;
use python_impact::CodeAnalyzer;

#[test]
fn test_if_condition_impact() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/if_condition_test.py");
    
    analyzer.analyze_file(path)?;
    
    // Test that changing if conditions in check_condition impacts calculate_result
    let check_key = format!("{}:{}", path.display(), "check_condition");
    let if_impacted = analyzer.find_functions_impacted_by_if_conditions(&check_key);
    
    assert!(if_impacted.iter().any(|f| f.contains("calculate_result")), 
            "Changing if conditions in 'check_condition' should impact 'calculate_result'");
    
    // Test that changing if conditions in check_condition impacts process_value due to shared variable
    assert!(if_impacted.iter().any(|f| f.contains("process_value")), 
            "Changing if conditions in 'check_condition' should impact 'process_value' due to shared variable");
    
    // Test that changing if conditions in process_value impacts check_condition due to shared variable
    let process_key = format!("{}:{}", path.display(), "process_value");
    let if_impacted = analyzer.find_functions_impacted_by_if_conditions(&process_key);
    
    assert!(if_impacted.iter().any(|f| f.contains("check_condition")), 
            "Changing if conditions in 'process_value' should impact 'check_condition' due to shared variable");
    
    // Test that changing if conditions in calculate_result impacts check_condition due to shared variable
    let calc_key = format!("{}:{}", path.display(), "calculate_result");
    let if_impacted = analyzer.find_functions_impacted_by_if_conditions(&calc_key);
    
    assert!(if_impacted.iter().any(|f| f.contains("check_condition")), 
            "Changing if conditions in 'calculate_result' should impact 'check_condition' due to shared variable");
    
    Ok(())
}

#[test]
fn test_specific_if_condition_impact() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/if_condition_test.py");
    
    analyzer.analyze_file(path)?;
    
    // Find the line number of the first if condition in check_condition
    let check_key = format!("{}:{}", path.display(), "check_condition");
    let conditions = analyzer.if_conditions.get(&check_key).unwrap();
    let first_condition = &conditions[0];
    
    // Test that changing this specific if condition impacts calculate_result and process_value
    let if_impacted = analyzer.find_functions_impacted_by_if_condition(&check_key, first_condition.line);
    
    assert!(if_impacted.iter().any(|f| f.contains("calculate_result")), 
            "Changing the specific if condition should impact 'calculate_result'");
    
    assert!(if_impacted.iter().any(|f| f.contains("process_value")), 
            "Changing the specific if condition should impact 'process_value' due to shared variable");
    
    Ok(())
}
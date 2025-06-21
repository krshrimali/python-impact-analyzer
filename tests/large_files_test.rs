use std::path::Path;
use anyhow::Result;
use python_impact::CodeAnalyzer;

#[test]
fn test_data_processing_dependencies() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/large_files/data_processing.py");

    analyzer.analyze_file(path)?;

    // Test that changing generate_unique_id impacts process_data_pipeline
    let generate_id_key = format!("{}:{}", path.display(), "generate_unique_id");
    let impacted = analyzer.find_impacted_functions(&generate_id_key);

    assert!(impacted.iter().any(|f| f.contains("process_data_pipeline")), 
            "Changing 'generate_unique_id' should impact 'process_data_pipeline'");

    // Test that changing process_record impacts process_batch
    let process_record_key = format!("{}:{}", path.display(), "process_record");
    let impacted = analyzer.find_impacted_functions(&process_record_key);

    assert!(impacted.iter().any(|f| f.contains("process_batch")), 
            "Changing 'process_record' should impact 'process_batch'");

    // Test that changing apply_business_rules impacts process_record
    let apply_rules_key = format!("{}:{}", path.display(), "apply_business_rules");
    let impacted = analyzer.find_impacted_functions(&apply_rules_key);

    assert!(impacted.iter().any(|f| f.contains("process_record")), 
            "Changing 'apply_business_rules' should impact 'process_record'");

    // Test that changing transform_for_analytics impacts prepare_for_analytics
    let transform_key = format!("{}:{}", path.display(), "transform_for_analytics");
    let impacted = analyzer.find_impacted_functions(&transform_key);

    assert!(impacted.iter().any(|f| f.contains("prepare_for_analytics")), 
            "Changing 'transform_for_analytics' should impact 'prepare_for_analytics'");

    // Test that changing aggregate_metrics impacts process_data_pipeline
    let aggregate_key = format!("{}:{}", path.display(), "aggregate_metrics");
    let impacted = analyzer.find_impacted_functions(&aggregate_key);

    assert!(impacted.iter().any(|f| f.contains("process_data_pipeline")), 
            "Changing 'aggregate_metrics' should impact 'process_data_pipeline'");

    Ok(())
}

#[test]
fn test_inheritance_hierarchy_dependencies() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/large_files/inheritance_hierarchy.py");

    // Test that the analyzer can parse the file without errors
    analyzer.analyze_file(path)?;

    // Test that the analyzer found some functions in the file
    assert!(!analyzer.functions.is_empty(), "Analyzer should find functions in the file");

    // Test that the analyzer found at least one function with "Customer" in the name
    assert!(analyzer.functions.iter().any(|(_, info)| info.name.contains("Customer")), 
            "Analyzer should find Customer-related functions");

    // Test that the analyzer found at least one function with "Order" in the name
    assert!(analyzer.functions.iter().any(|(_, info)| info.name.contains("Order")), 
            "Analyzer should find Order-related functions");

    // Test that the analyzer found at least one function with "Money" in the name
    assert!(analyzer.functions.iter().any(|(_, info)| info.name.contains("Money")), 
            "Analyzer should find Money-related functions");

    // Test that the analyzer found the main function
    assert!(analyzer.functions.iter().any(|(_, info)| info.name == "main"), 
            "Analyzer should find the main function");

    Ok(())
}

#[test]
fn test_rule_engine_dependencies() -> Result<()> {
    let mut analyzer = CodeAnalyzer::new()?;
    let path = Path::new("tests/python_samples/large_files/rule_engine.py");

    // Test that the analyzer can parse the file without errors
    analyzer.analyze_file(path)?;

    // Test that the analyzer found some functions in the file
    assert!(!analyzer.functions.is_empty(), "Analyzer should find functions in the file");

    // Test that the analyzer found at least one function with "Rule" in the name
    assert!(analyzer.functions.iter().any(|(_, info)| info.name.contains("Rule")), 
            "Analyzer should find Rule-related functions");

    // Test that the analyzer found at least one function with "Engine" in the name
    assert!(analyzer.functions.iter().any(|(_, info)| info.name.contains("Engine")), 
            "Analyzer should find Engine-related functions");

    // Test that the analyzer found at least one function with "evaluate" in the name
    assert!(analyzer.functions.iter().any(|(_, info)| info.name.contains("evaluate")), 
            "Analyzer should find evaluate-related functions");

    // Test that the analyzer found the main function
    assert!(analyzer.functions.iter().any(|(_, info)| info.name == "main"), 
            "Analyzer should find the main function");

    // Test that the analyzer found the create_customer_eligibility_rules function
    assert!(analyzer.functions.iter().any(|(_, info)| info.name == "create_customer_eligibility_rules"), 
            "Analyzer should find the create_customer_eligibility_rules function");

    Ok(())
}

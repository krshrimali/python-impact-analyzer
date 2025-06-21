use std::path::PathBuf;
use anyhow::{Result, anyhow};
use clap::Parser;
use colored::Colorize;
use python_impact::CodeAnalyzer;
use python_impact::visualization;

#[derive(Parser, Debug)]
#[command(
    author, 
    version, 
    about = "Analyzes Python code to identify functions that would be impacted by changes to a specific function or code location",
    long_about = None
)]
struct Args {
    /// Path to the Python file or directory to analyze
    #[arg(short, long)]
    path: PathBuf,

    /// Function name to analyze for impact
    #[arg(short, long)]
    function: Option<String>,

    /// Line number to analyze for impact
    #[arg(short, long)]
    line: Option<usize>,

    /// Recursively analyze directories
    #[arg(short, long, default_value_t = false)]
    recursive: bool,

    /// Generate a visualization of the dependency graph
    #[arg(short, long, default_value_t = false)]
    visualize: bool,

    /// Output file path for the visualization (defaults to "impact_graph.dot")
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// Show dependencies in reverse (what functions are impacted by this one)
    /// Default is to show what functions this one depends on
    #[arg(long, default_value_t = true)]
    reverse: bool,
}

fn main() -> Result<()> {
    let args = Args::parse();

    let mut analyzer = CodeAnalyzer::new()?;

    analyzer.analyze_path(&args.path, args.recursive)?;

    // Determine the function key if a function or line is specified
    let function_key = if let Some(function_name) = &args.function {
        // Find the function by name
        let mut found_key = None;
        for (key, info) in &analyzer.functions {
            if info.name == *function_name {
                found_key = Some(key.clone());
                break;
            }
        }

        if found_key.is_none() && !args.visualize {
            return Err(anyhow!("Function not found: {}", function_name));
        }
        found_key
    } else if let Some(line) = args.line {
        // Find the function containing this line
        let found_key = analyzer.find_function_at_line(&args.path, line);
        if found_key.is_none() && !args.visualize {
            return Err(anyhow!("No function found at line {}", line));
        }
        found_key
    } else {
        None
    };

    // Handle visualization if requested
    if args.visualize {
        let output_path = args.output.unwrap_or_else(|| {
            if let Some(ref key) = function_key {
                if let Some(info) = analyzer.functions.get(key) {
                    PathBuf::from(format!("{}_impact.dot", info.name.replace(".", "_")))
                } else {
                    PathBuf::from("dependency_graph.dot")
                }
            } else {
                PathBuf::from("dependency_graph.dot")
            }
        });

        println!("\n{}", "Generating visualization...".green().bold());

        if let Some(ref key) = function_key {
            // Generate visualization for a specific function
            let file_path = visualization::save_impact_visualization(&analyzer, key, &output_path)?;
            println!("Visualization saved to: {}", file_path.display());
        } else {
            // Generate visualization for the entire dependency graph
            let file_path = visualization::save_dot_file(&analyzer, &output_path, None, args.reverse)?;
            println!("Visualization saved to: {}", file_path.display());
        }

        println!("\nTo view the visualization, use a DOT file viewer or convert to an image with Graphviz:");
        println!("  dot -Tpng {} -o {}.png", output_path.display(), output_path.display().to_string().replace(".dot", ""));
    }

    // Print impact information if a function is specified
    if let Some(ref key) = function_key {
        analyzer.print_impacted_functions(key)?;
    } else if !args.visualize {
        // Print all functions and their dependencies
        println!("\n{}", "All Functions:".blue());
        for (key, info) in &analyzer.functions {
            println!("  {} ({}:{})", info.name, info.file_path.display(), info.start_line);

            let impacted = analyzer.find_impacted_functions(key);
            if !impacted.is_empty() {
                println!("    {}", "Impacts:".yellow());
                for function in impacted {
                    if let Some(impact_info) = analyzer.functions.get(&function) {
                        println!("      {} ({}:{})", impact_info.name, impact_info.file_path.display(), impact_info.start_line);
                    }
                }
            }
        }
    }

    Ok(())
}

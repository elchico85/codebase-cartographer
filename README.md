# codebase-cartographer
An open-source tool for automatically generating architectural audit reports for any Python codebase.

# CodebaseAuditor

A comprehensive Python tool for analyzing, mapping, and understanding codebases through automated static analysis and dependency visualization.

## Overview

As an industrial engineer working on complex optimization systems, I developed this tool to bridge the gap between technical implementation and strategic understanding of software architectures. CodebaseAuditor generates detailed Markdown reports that help stakeholders - from technical teams to management - understand the structure, flow, and dependencies of Python projects.

## Why I Built This

During my work on the **MagonaDSS** (Decision Support System) project, I needed a way to:
- Quickly onboard new team members to complex optimization codebases
- Document the architecture for academic research and thesis work
- Communicate technical complexity to non-technical stakeholders
- Identify architectural patterns in industrial automation projects

Traditional documentation often becomes outdated. This tool generates living documentation that stays synchronized with the actual codebase.

## Key Features

### 🏗️ Architecture Analysis
- **Component Classification**: Automatically categorizes modules (UI, strategies, pipelines, data models, utilities)
- **Entry Point Detection**: Identifies main execution flows and scripts
- **Strategy Pattern Recognition**: Specifically detects optimization strategy classes

### 📊 Dependency Mapping
- **Visual Dependency Graphs**: Generates network diagrams showing module relationships
- **Internal Dependency Analysis**: Focuses on project-internal connections
- **Circular Dependency Detection**: Implicit through graph analysis

### 📈 Complexity Assessment
- **Function Complexity Metrics**: Estimates cognitive complexity using AST analysis
- **Pipeline Identification**: Highlights critical business logic functions
- **Data Flow Analysis**: Maps data processing and manipulation functions

### 📋 Comprehensive Reporting
- **Markdown Output**: Professional documentation ready for GitLab/GitHub
- **Statistics Dashboard**: Project metrics and health indicators
- **Tabular Data**: Structured information about classes, functions, and dependencies

## Installation

### Basic Installation
```bash
# Clone or download the script
wget https://raw.githubusercontent.com/your-repo/codebase-auditor/main/codebase_auditor.py

# Basic usage (uses fallback formatting)
python codebase_auditor.py /path/to/your/project
```

### Enhanced Installation (Recommended)
```bash
# Install optional dependencies for full functionality
pip install networkx matplotlib tabulate

# Now you get visual graphs and better table formatting
python codebase_auditor.py /path/to/your/project
```

## Usage

### Basic Usage
```bash
# Analyze current directory
python codebase_auditor.py

# Analyze specific project
python codebase_auditor.py /path/to/project

# Custom output filename
python codebase_auditor.py /path/to/project --output my_analysis.md
```

### Command Line Options
```bash
python codebase_auditor.py --help

usage: codebase_auditor.py [-h] [--output OUTPUT] [directory]

Analyzes a Python codebase and generates a Markdown report.

positional arguments:
  directory             The project root directory (default: current directory)

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       Output Markdown file name (default: codebase_audit_report.md)
```

## Output Structure

The generated report includes:

1. **Project Statistics** - High-level metrics and health indicators
2. **Architecture Overview** - Component breakdown and module classification  
3. **Logical & Execution Flow** - Entry points, strategies, and pipeline functions
4. **Data Flow Analysis** - Data files and processing functions
5. **Internal Dependency Map** - Visual and textual dependency analysis

## Example Output

```markdown
# Codebase Audit Report

## Project Statistics
| Metric | Value |
|--------|-------|
| Python Files Analyzed | 24 |
| Total Functions | 89 |
| Optimization Strategies | 5 |
| Avg. Function Complexity | 3.2 |

## Architecture Overview
### 🧠 Optimization Strategies (5 modules)
- src.strategies.genetic_algorithm
- src.strategies.simulated_annealing
- src.strategies.tabu_search

### ⚙️ Business Logic / Pipelines (3 modules)  
- src.pipeline.optimization_runner
- src.pipeline.data_preprocessor
```

## Industrial Applications

This tool has proven particularly valuable for:

- **Operations Research Projects**: Understanding complex optimization algorithm implementations
- **Academic Research**: Documenting methodology for thesis work and publications
- **Team Onboarding**: Rapid understanding of industrial automation systems
- **Code Review**: Identifying architectural patterns and potential improvements
- **Stakeholder Communication**: Translating technical complexity into business language

## Technical Implementation

### Architecture Pattern Detection
The tool uses AST (Abstract Syntax Tree) analysis to identify common patterns in industrial software:

```python
# Automatically detects strategy pattern classes
if 'strategy' in node.name.lower() or 'strategies' in module_name:
    self.classes[class_name]['is_strategy'] = True
```

### Complexity Metrics
Function complexity is estimated by counting control flow statements:
```python
complexity = sum(1 for n in ast.walk(node) 
                if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With))) + 1
```

### Dependency Resolution
Handles both absolute and relative imports with proper module resolution:
```python
if level > 0:  # Relative import
    parts = module_name.split('.')
    base = parts[: -level]
    resolved_dep = '.'.join(base + ([dep_name] if dep_name else []))
```

## Dependencies

### Required
- Python 3.6+
- Standard library only (ast, pathlib, collections, argparse)

### Optional (Enhanced Features)
- `networkx` - For dependency graph generation
- `matplotlib` - For visual graph rendering  
- `tabulate` - For enhanced table formatting

## Contributing

This tool emerged from real industrial needs. If you're working on similar optimization or industrial automation projects, contributions are welcome:

1. **Architecture Pattern Detection**: Add recognition for new patterns
2. **Complexity Metrics**: Implement additional code quality measures
3. **Visualization**: Enhance graph layouts and styling
4. **Export Formats**: Add support for other documentation formats

## License

MIT License - Feel free to adapt for your industrial or research projects.

## Author

Developed by Valerio Parra - Industrial Engineer specializing in Operations Research and Digital Transformation of manufacturing systems.

*"Bridging the physical and digital worlds through systematic analysis and optimization."*

---

**Note**: This tool is designed for Python codebases. For other languages or mixed-language projects, consider adapting the AST analysis logic or using language-specific parsers.

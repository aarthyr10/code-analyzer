# Advanced Codebase Analyzer with LLM Integration

A powerful tool for analyzing codebases using Large Language Models (LLMs) to extract comprehensive insights, code quality metrics, and architectural knowledge. Features intelligent parsing for multiple programming languages and professional analysis reporting.

## Key Features

- **Native Language Parsing**: Deep AST analysis for Python, JavaScript/TypeScript, SQL, and more
- **LLM-Powered Analysis**: Ollama integration for intelligent code comprehension
- **Large File Handling**: Smart chunking and truncation for files of any size
- **Database Schema Discovery**: Complete SQL analysis with tables, views, procedures, functions
- **Code Quality Metrics**: Complexity scoring, maintainability assessment, technical debt analysis
- **Zero Configuration**: Edit variables and run - no config files needed
- **Professional Reporting**: Structured JSON output with actionable recommendations

## Requirements

- Python 3.8+
- Ollama with local models
- Optional: `esprima` (JavaScript analysis), `sqlglot` (SQL analysis)

## Quick Setup

### 1. Install Dependencies
```bash
pip install requests esprima sqlglot
```

### 2. Setup Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama3.2:1b
ollama pull llama3.2:3b

# Start Ollama service
ollama serve
```

### 3. Configure and Run
Edit the variables at the top of `codebase_analyzer.py`:
```python
PROJECT_PATH = "./your-project"
PROJECT_NAME = "Your Project Name"
OUTPUT_FILE = "analysis_result.json"
```

Run the analysis:
```bash
python codebase_analyzer.py
```

## Configuration Variables

All settings are configured by editing variables at the top of the script:

```python
# Core Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
PRIMARY_MODEL = "llama3.2:1b"        # Fast model for initial analysis
FALLBACK_MODEL = "llama3.2:3b"       # More capable backup model

# File Processing
MAX_FILES = 500                      # Maximum files to analyze
MAX_FILE_SIZE = 2000000              # Files larger than 2MB are chunked
CHUNK_SIZE = 8000                    # Token limit per LLM request
INCLUDE_TESTS = True                 # Include test files in analysis
DETAILED_ANALYSIS = True             # Enable comprehensive analysis

# Output Settings
OUTPUT_FILE = "codebase_analysis.json"
PRETTY_PRINT = True                  # Format JSON output

# Project Settings
PROJECT_PATH = "./project"           # Path to your codebase
PROJECT_NAME = "Codebase Analysis"   # Display name for the project
```

## Performance Tuning

### For Large Projects
```python
MAX_FILES = 1000
MAX_FILE_SIZE = 5000000
PRIMARY_MODEL = "llama3.2:3b"        # Use more capable model
```

### For Quick Analysis
```python
MAX_FILES = 200
INCLUDE_TESTS = False
PRIMARY_MODEL = "llama3.2:1b"        # Use faster model
```

### For SQL-Heavy Projects
```python
MAX_FILE_SIZE = 10000000             # Handle large SQL dumps
CHUNK_SIZE = 12000                   # Larger chunks for SQL
```

## Language Support

### Python Analysis
- **AST Parsing**: Complete syntax tree analysis
- **Class Extraction**: Methods, attributes, inheritance
- **Function Analysis**: Parameters, return types, complexity
- **Import Tracking**: Dependency mapping
- **Complexity Metrics**: Cyclomatic complexity calculation

### JavaScript/TypeScript Analysis
- **Esprima Integration**: Professional JS parsing when available
- **Regex Fallback**: Pattern-based analysis
- **Modern Syntax**: ES6+, React, Node.js patterns
- **Module Analysis**: Import/export tracking
- **Framework Detection**: React, Vue, Angular patterns

### SQL Analysis
- **SQLGlot Integration**: Advanced SQL parsing (silent error handling)
- **Schema Discovery**: Tables, views, procedures, functions, triggers
- **Multi-Database**: MySQL, Postgres SQL, SQL Server, SQLite
- **Large File Processing**: Intelligent sampling of massive SQL files
- **Relationship Analysis**: Foreign keys, constraints

### Other Languages
- Java, C/C++, C#, PHP, Ruby, Go, Rust, HTML, CSS, Vue.js, Scala, Kotlin, Swift

## Sample Output

The analyzer generates comprehensive JSON reports:

```json
{
  "project_name": "E-commerce Platform",
  "analysis_date": "2025-01-20T14:30:00",
  "overview": "Full-stack web application with React frontend and Node.js backend",
  "tech_stack": ["JavaScript", "TypeScript", "SQL", "CSS"],
  "architecture_pattern": "MVC",
  "total_files": 127,
  "total_lines": 15420,
  
  "complexity_summary": {
    "average_complexity": 4.2,
    "high_complexity_files": 8,
    "total_methods_analyzed": 234,
    "maintainability_score": 78
  },
  
  "files": [
    {
      "path": "src/components/ProductCatalog.jsx",
      "language": "React JSX",
      "lines_of_code": 156,
      "complexity_score": 6,
      "purpose": "Product display and filtering component",
      "key_classes": [],
      "key_methods": [],
      "imports": ["react", "axios", "lodash"]
    }
  ],
  
  "key_methods": [
    {
      "name": "processPayment",
      "signature": "async function processPayment(paymentData)",
      "complexity_score": 8,
      "file_path": "src/services/paymentService.js",
      "line_number": 45,
      "cyclomatic_complexity": 12
    }
  ],
  
  "database_info": {
    "tables": ["users", "products", "orders", "payments"],
    "views": ["user_orders", "product_analytics"],
    "procedures": ["calculate_shipping", "process_refund"],
    "functions": ["get_tax_rate", "format_currency"]
  },
  
  "code_quality_metrics": {
    "average_file_size": 121.4,
    "average_complexity": 4.2,
    "large_files_count": 3,
    "complex_files_count": 8,
    "maintainability_score": 78
  },
  
  "recommendations": [
    "Consider splitting 3 large files for better maintainability",
    "Refactor 8 high-complexity files to improve readability",
    "Simplify 15 complex methods with high cyclomatic complexity",
    "Add comprehensive unit tests for payment processing",
    "Implement consistent error handling patterns"
  ]
}
```

## Advanced Features

### Large File Processing
Automatically handles files exceeding LLM token limits:
- **Header Sampling**: First 100 lines for context
- **Middle Sampling**: Representative middle section
- **Footer Sampling**: Last 100 lines for completeness
- **Intelligent Truncation**: Preserves code structure while reducing size

### Token Management
- **Smart Chunking**: Breaks large content into analyzable pieces
- **Content Prioritization**: Focuses on most important sections
- **Model Fallback**: Automatically switches to back up model on failure
- **Silent Processing**: Suppresses unnecessary warnings and errors

### Database Analysis
For SQL-containing projects:
- **Schema Discovery**: All database objects identified
- **Relationship Mapping**: Foreign key and constraint analysis
- **Performance Insights**: Index and optimization opportunities
- **Data Flow Analysis**: Query patterns and data access

## Usage Examples

### Basic Analysis
```python
# Edit PROJECT_PATH in codebase_analyzer.py first
from codebase_analyzer import CodebaseAnalyzer

analyzer = CodebaseAnalyzer()
analysis = analyzer.analyze_project()
output_file = analyzer.save_analysis(analysis)
```

### Runtime Configuration
```python
import codebase_analyzer
from codebase_analyzer import CodebaseAnalyzer


# Override defaults
codebase_analyzer.MAX_FILES = 1000
codebase_analyzer.PRIMARY_MODEL = "llama3.2:3b"
codebase_analyzer.INCLUDE_TESTS = False

analyzer = CodebaseAnalyzer()
analysis = analyzer.analyze_project("./my-project", "Custom Analysis")
```

### Batch Processing
```python
from codebase_analyzer import CodebaseAnalyzer

projects = [
    {"path": "./frontend", "name": "Frontend App"},
    {"path": "./backend", "name": "API Server"},
    {"path": "./database", "name": "Database Schema"}
]

for project in projects:
    import codebase_analyzer
    codebase_analyzer.PROJECT_PATH = project["path"]
    codebase_analyzer.PROJECT_NAME = project["name"]
    codebase_analyzer.OUTPUT_FILE = f"{project['name']}_analysis.json"
    
    analyzer = CodebaseAnalyzer()
    analysis = analyzer.analyze_project()
    analyzer.save_analysis(analysis)
```

### SQL-Only Analysis
```python
from codebase_analyzer import CodebaseAnalyzer

analyzer = CodebaseAnalyzer()
code_files, sample_files = analyzer.scan_codebase("./database-project")
database_info = analyzer.analyze_database_schema(code_files)

print(f"Tables: {len(database_info.tables)}")
print(f"Views: {len(database_info.views)}")
print(f"Procedures: {len(database_info.procedures)}")
```

## Quality Metrics Guide

### Maintainability Score (0-100)
- **90-100**: Excellent - Clean, well-structured code
- **70-89**: Good - Minor improvements needed
- **50-69**: Fair - Moderate refactoring recommended
- **30-49**: Poor - Significant issues present
- **0-29**: Critical - Major restructuring required

### Complexity Scoring (1-10)
- **1-3**: Simple - Easy to understand and modify
- **4-6**: Moderate - Standard complexity level
- **7-8**: Complex - Requires careful review
- **9-10**: Very Complex - Immediate attention needed

### File Categories
- **Small**: < 100 lines - Ideal size
- **Medium**: 100-300 lines - Good size
- **Large**: 300-500 lines - Consider splitting
- **Very Large**: > 500 lines - Refactoring candidate

## CI/CD Integration

### GitHub Actions
```yaml
name: Code Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install Ollama
        run: |
          curl -fsSL https://ollama.ai/install.sh | sh
          ollama pull llama3.2:1b
      - name: Install dependencies
        run: pip install requests esprima sqlglot
      - name: Run analysis
        run: python codebase_analyzer.py
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: analysis-results
          path: codebase_analysis.json
```

### Quality Gate Script
```bash
#!/bin/bash
# quality_gate.sh

python codebase_analyzer.py

SCORE=$(python -c "
import json
with open('codebase_analysis.json') as f:
    data = json.load(f)
    print(data['code_quality_metrics']['maintainability_score'])
")

echo "Maintainability Score: $SCORE"

if [ "$SCORE" -lt 70 ]; then
    echo "Quality gate failed: Score below 70"
    exit 1
fi

echo "Quality gate passed"
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running code analysis..."
python codebase_analyzer.py

if [ $? -eq 0 ]; then
    echo "Analysis complete - check codebase_analysis.json"
else
    echo "Analysis failed"
    exit 1
fi
```

## Troubleshooting

### Common Issues

**Ollama Connection Failed**
```bash
# Check service status
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Verify models are available
ollama list
```

**Large File Warnings**
- Large files are automatically processed with intelligent truncation
- Increase `MAX_FILE_SIZE` if needed: `MAX_FILE_SIZE = 5000000`
- Files larger than limit are sampled, not skipped

**Memory Issues**
```python
# Reduce memory usage
MAX_FILES = 200
CHUNK_SIZE = 4000
INCLUDE_TESTS = False
```

**SQL Analysis Issues**
```bash
# Install SQLGlot for better SQL parsing
pip install sqlglot

# SQLGlot warnings are automatically suppressed
# Fallback regex parsing handles unsupported syntax
```

**Model Performance**
```python
# Use faster model for quick analysis
PRIMARY_MODEL = "llama3.2:3b"

# Use more capable model for detailed analysis
FALLBACK_MODEL = "llama3.2:1b"
```

### Performance Optimization

**For Very Large Codebases**
```python
MAX_FILES = 2000
MAX_FILE_SIZE = 10000000
PRIMARY_MODEL = "llama3.2:3b"
CHUNK_SIZE = 10000
```

**For Resource-Constrained Environments**
```python
MAX_FILES = 100
MAX_FILE_SIZE = 500000
PRIMARY_MODEL = "llama3.2:1b"
CHUNK_SIZE = 4000
INCLUDE_TESTS = False
```

## Contributing

Contributions welcome! Areas for improvement:

- **Language Analyzers**: Add support for additional programming languages
- **Metrics Enhancement**: Develop new code quality and complexity metrics
- **Integration Tools**: Build IDE plugins and platform integrations
- **Performance**: Optimize analysis speed and memory usage
- **Visualization**: Create dashboards and visual reporting tools

### Development Setup
```bash
git clone <repository-url>
cd codebase-analyzer
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Format code
black codebase_analyzer.py

# Lint code
flake8 codebase_analyzer.py
```

## License

MIT License - Free for commercial and personal use.

## Support

Need help? 
1. Check the troubleshooting section above
2. Review configuration variables
3. Verify Ollama installation and models
4. Create an issue with error details and configuration

---

**Professional codebase analysis powered by Large Language Models - Extract insights, improve quality, and understand your code better.**
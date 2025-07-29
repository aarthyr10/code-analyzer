# Comprehensive Multi-Language Codebase Analyzer

A sophisticated static code analysis tool that provides SonarQube-style analysis for multiple programming languages with
AI-powered architectural insights and comprehensive reporting.

## Overview

This analyzer performs deep static analysis of codebases across multiple programming languages, identifying code quality
issues, unused code, complexity metrics, coding standard violations, and architectural patterns. It combines traditional
static analysis with AI-powered insights to provide comprehensive codebase assessment.

## Features

### Multi-Language Support

- **Fully Supported**: Java, Python, JavaScript, HTML, CSS, SCSS
- **File Detection**: Supports 20+ programming languages and file types
- **Image File Handling**: Automatically detects and categorizes image files without analysis
- **Extensible Architecture**: Framework for adding new language analyzers

### Analysis Capabilities

- **Static Code Analysis**: AST-based parsing for detailed code structure analysis
- **Complexity Metrics**: Cyclomatic complexity calculation for methods and classes
- **Usage Analysis**: Identification of unused classes, methods, and variables
- **Coding Standards**: Language-specific style and best practice validation
- **Dependency Analysis**: Internal dependency mapping and circular dependency detection
- **Architecture Analysis**: AI-powered architectural pattern recognition and suggestions

### Reporting

- **Comprehensive JSON Output**: Detailed machine-readable analysis results
- **Markdown Reports**: Human-readable analysis summaries
- **Quality Scoring**: Overall codebase quality assessment (0-10 scale)
- **Actionable Recommendations**: Specific improvement suggestions with priority levels

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama server (for AI-powered analysis)

### Setup

1. Clone the repository and navigate to the project directory

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install and start Ollama server:
```bash
# Install Ollama (visit https://ollama.ai for installation instructions)
ollama pull codellama:13b-instruct
ollama pull nomic-embed-text
ollama pull llama2:13b-chat
```

5. Start Ollama server:

```bash
ollama serve
```

## Configuration

Edit the configuration variables in the main script:

```python
CODEBASE_PATH = "./your-project-path"
OUTPUT_FILE = "analysis_results.json"
OUTPUT_REPORT = "analysis_report.md"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL_CODE = "codellama:13b-instruct"
OLLAMA_MODEL_EMBED = "nomic-embed-text"
OLLAMA_MODEL_ARCHITECTURE = "llama2:13b-chat"
MAX_WORKERS = 8
```

## Usage

### Basic Analysis

```bash
python code_analyzer.py
```

### Command Line Options

Modify the configuration section in `code_analyzer.py` to customize:

- **CODEBASE_PATH**: Target directory for analysis
- **OUTPUT_FILE**: JSON output file name
- **OUTPUT_REPORT**: Markdown report file name
- **MAX_WORKERS**: Number of parallel analysis threads

## Output Files

### JSON Report (`comprehensive_codebase_analysis.json`)

- Complete analysis data in machine-readable format
- Detailed metrics for all analyzed files, classes, and methods
- Issue classifications by severity and category
- Usage statistics and dependency mappings

### Markdown Report (`COMPREHENSIVE_ANALYSIS_REPORT.md`)

- Executive summary of analysis results
- Quality metrics and scores
- Detailed breakdowns by language and file type
- Prioritized improvement recommendations
- Coding standards compliance report

## Analysis Metrics

### Quality Scoring

- **Overall Quality Score**: 0-10 scale based on complexity, issues, and best practices
- **Maintainability Index**: Code maintainability assessment
- **Technical Debt Ratio**: Proportion of high-priority issues

### Issue Classification

- **Critical**: Security vulnerabilities, parse errors
- **High**: Complex methods, god classes, circular dependencies
- **Medium**: Long methods, naming violations, style issues
- **Low**: Minor formatting and style improvements

### Usage Analysis

- **Unused Classes**: Classes with no external references
- **Unused Methods**: Methods never called (excluding entry points)
- **Unused Variables**: Variables declared but never used
- **Code Waste Metrics**: Percentage of potentially removable code

## Supported Languages

### Fully Analyzed Languages

- **Java**: AST parsing, complexity analysis, coding standards
- **Python**: AST parsing, PEP 8 compliance, best practices
- **JavaScript**: Pattern-based analysis, modern JS standards
- **HTML**: Structure validation, accessibility checks
- **CSS/SCSS**: Style validation, best practices

### Detected File Types

- Programming: C/C++, C#, Go, Rust, Swift, Kotlin, Scala, Ruby, PHP
- Web: TypeScript, LESS
- Data: JSON, YAML, XML, SQL
- Scripts: Shell, PowerShell
- Images: PNG, JPEG, GIF, SVG, and 10+ other formats

## Architecture

### Core Components

- **LanguageDetector**: File type identification and language classification
- **FileExtractor**: Codebase traversal and file analysis coordination
- **BaseCodeAnalyzer**: Abstract base for language-specific analyzers
- **UsageAnalyzer**: Cross-reference analysis for unused code detection
- **LLMAnalysisEngine**: AI-powered architectural insights
- **LanguageValidator**: Analysis scope validation and reporting

### Analyzer Classes

- **JavaCodeAnalyzer**: Javalang-based AST analysis
- **PythonCodeAnalyzer**: Python AST module integration
- **JavaScriptCodeAnalyzer**: Regex-based pattern analysis
- **HTMLCodeAnalyzer**: Structure and accessibility validation
- **CSS/SCSSCodeAnalyzer**: Style rule and best practice validation

## Extending the Analyzer

### Adding New Languages

1. Add language extension mapping:
```python
LANGUAGE_EXTENSIONS = {
    '.go': 'go',  # Add new extension
}
```

2. Add to supported languages:
```python
SUPPORTED_LANGUAGES = {'java', 'python', 'go'}  # Add language
```

3. Implement analyzer class:
```python
from code_analyzer import BaseCodeAnalyzer
class GoCodeAnalyzer(BaseCodeAnalyzer):
    def get_language(self) -> str:
        return 'go'

    def analyze_file(self, file_path: str, content: str):
        # Implement Go-specific analysis
        pass
```

4. Register analyzer:
```python
self.analyzers = {
    'go': GoCodeAnalyzer(),  # Add to analyzer registry
}
```

## Performance Considerations

- **Parallel Processing**: Configurable worker threads for file analysis
- **Memory Management**: Streaming analysis for large codebases
- **Incremental Analysis**: Focus on supported languages only
- **Caching**: Vector store persistence for AI analysis components

## Limitations

- **Binary Files**: No analysis of compiled or binary files
- **Generated Code**: May produce false positives for auto-generated code
- **Language Coverage**: Full analysis limited to explicitly supported languages
- **AI Dependencies**: Architectural analysis requires Ollama server availability

## Troubleshooting

### Common Issues

**Ollama Connection Errors**

- Ensure Ollama server is running on correct port
- Verify model availability with `ollama list`

**Memory Issues with Large Codebases**

- Reduce MAX_WORKERS configuration
- Exclude build/dist directories from analysis

**Parser Errors**

- Check for encoding issues in source files
- Verify file permissions for analysis directory

## Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Add tests for new analyzers
5. Submit pull request with documentation

### Code Standards

- Follow PEP 8 for Python code
- Add type hints for all public methods
- Include docstrings for complex algorithms
- Maintain test coverage above 80%

## Changelog

### Version 1.0.0

- Multi-language support architecture
- AI-powered architectural analysis
- Comprehensive usage analysis
- Enhanced reporting capabilities
- Image file detection and categorization
- Coding standards validation framework
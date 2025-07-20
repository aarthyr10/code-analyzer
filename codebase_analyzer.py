#!/usr/bin/env python3

import ast
import json
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import concurrent.futures
from threading import Lock

import requests

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

OLLAMA_BASE_URL = "http://localhost:11434"
PRIMARY_MODEL = "llama3.2:3b"
FALLBACK_MODEL = "llama3.2:1b"
MAX_FILES = 500
CHUNK_SIZE = 8000
MAX_TOKENS_PER_REQUEST = 3000
INCLUDE_TESTS = False
DETAILED_ANALYSIS = False
OUTPUT_FILE = "sakila_analysis.json"
PRETTY_PRINT = True
PROJECT_PATH = "./sakila-main"
PROJECT_NAME = "Sakila Database Project"
MAX_WORKERS = 4
MAX_FILE_SIZE = 1000000


class TokenManager:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.logger = logging.getLogger(__name__)

        if HAS_TIKTOKEN:
            try:
                self.encoding = tiktoken.encoding_for_model(model_name)
                self.has_tokenizer = True
            except:
                try:
                    self.encoding = tiktoken.get_encoding("cl100k_base")
                    self.has_tokenizer = True
                except:
                    self.has_tokenizer = False
        else:
            self.has_tokenizer = False

    def count_tokens(self, text: str) -> int:
        if self.has_tokenizer:
            try:
                return len(self.encoding.encode(text))
            except:
                return len(text) // 4
        else:
            return len(text) // 4


@dataclass
class MethodInfo:
    name: str
    signature: str
    description: str
    complexity_score: int
    file_path: str
    line_number: int
    parameters: List[str]
    return_type: str
    cyclomatic_complexity: int
    technical_details: str = ""
    business_purpose: str = ""


@dataclass
class ClassInfo:
    name: str
    methods: List[str]
    attributes: List[str]
    inheritance: List[str]
    file_path: str
    line_number: int
    description: str = ""
    design_pattern: str = ""
    responsibility: str = ""


@dataclass
class FileInfo:
    path: str
    language: str
    lines_of_code: int
    complexity_score: int
    purpose: str
    key_classes: List[ClassInfo]
    key_methods: List[MethodInfo]
    imports: List[str]
    functions_count: int
    classes_count: int
    token_count: int = 0
    architectural_role: str = ""
    technical_summary: str = ""


@dataclass
class DatabaseInfo:
    tables: List[str]
    views: List[str]
    procedures: List[str]
    functions: List[str]
    triggers: List[str]
    relationships: List[str] = None
    schema_purpose: str = ""
    table_hierarchy: Dict[str, Any] = None
    foreign_key_relationships: Dict[str, List[str]] = None


@dataclass
class ProjectAnalysis:
    project_name: str
    analysis_date: str
    overview: str
    business_domain: str
    technical_architecture: str
    tech_stack: List[str]
    architecture_pattern: str
    total_files: int
    total_lines: int
    total_tokens: int
    complexity_summary: Dict[str, Any]
    files: List[FileInfo]
    key_methods: List[MethodInfo]
    key_classes: List[ClassInfo]
    dependencies: List[str]
    database_info: Optional[DatabaseInfo]
    recommendations: List[str]
    code_quality_metrics: Dict[str, Any]
    token_usage_stats: Dict[str, Any]
    project_summary: str = ""
    use_cases: List[str] = None
    technical_highlights: List[str] = None


class LLMClient:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.primary_model = PRIMARY_MODEL
        self.fallback_model = FALLBACK_MODEL
        self.current_model = self.primary_model
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self.token_manager = TokenManager()

    def check_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate_direct(self, prompt: str) -> str:
        if len(prompt) > MAX_TOKENS_PER_REQUEST * 4:
            prompt = prompt[:MAX_TOKENS_PER_REQUEST * 4]

        data = {
            "model": self.current_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 256
            }
        }

        try:
            response = self.session.post(f"{self.base_url}/api/generate",
                                         json=data, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return ""
        except:
            return ""

    def analyze_project_overview(self, project_structure: Dict, file_samples: List[Tuple[str, str]]) -> Dict[str, Any]:
        sample_files_text = "\n\n".join([
            f"=== {path} ===\n{content[:500]}"
            for path, content in file_samples[:3]
        ])

        prompt = f"""Analyze this project. Return JSON only:
PROJECT STRUCTURE: {json.dumps(project_structure)}
SAMPLE FILES: {sample_files_text}

Return JSON:
{{
    "business_domain": "domain",
    "project_purpose": "purpose", 
    "technical_architecture": "architecture",
    "architecture_pattern": "pattern",
    "primary_use_cases": ["use1", "use2"],
    "target_users": "users"
}}"""

        response = self.generate_direct(prompt)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {
            "business_domain": "Software Development",
            "project_purpose": "Software application",
            "technical_architecture": "Multi-layered application",
            "architecture_pattern": "Layered Architecture",
            "primary_use_cases": ["Data processing"],
            "target_users": "Business users"
        }


class PythonAnalyzer:
    def __init__(self):
        self.token_manager = TokenManager()

    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(content)
            return {
                'classes': self._extract_classes(tree, file_path),
                'functions': self._extract_functions(tree, file_path),
                'imports': self._extract_imports(tree),
                'complexity': self._calculate_complexity(tree),
                'token_count': self.token_manager.count_tokens(content)
            }
        except:
            return {
                'classes': [],
                'functions': [],
                'imports': [],
                'complexity': 1,
                'token_count': self.token_manager.count_tokens(content)
            }

    def _extract_classes(self, tree: ast.AST, file_path: str) -> List[ClassInfo]:
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                attributes = []
                for n in node.body:
                    if isinstance(n, ast.Assign):
                        for target in n.targets:
                            if isinstance(target, ast.Name):
                                attributes.append(target.id)

                inheritance = [base.id for base in node.bases if isinstance(base, ast.Name)]

                classes.append(ClassInfo(
                    name=node.name,
                    methods=methods,
                    attributes=attributes,
                    inheritance=inheritance,
                    file_path=file_path,
                    line_number=getattr(node, 'lineno', 0)
                ))
        return classes

    def _extract_functions(self, tree: ast.AST, file_path: str) -> List[MethodInfo]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                parameters = [arg.arg for arg in node.args.args]
                complexity = self._calculate_function_complexity(node)

                functions.append(MethodInfo(
                    name=node.name,
                    signature=f"def {node.name}({', '.join(parameters)})",
                    description="Python function",
                    complexity_score=min(complexity, 10),
                    file_path=file_path,
                    line_number=getattr(node, 'lineno', 0),
                    parameters=parameters,
                    return_type="Any",
                    cyclomatic_complexity=complexity
                ))
        return functions

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _calculate_complexity(self, tree: ast.AST) -> int:
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler, ast.With)):
                complexity += 1
        return min(complexity, 10)

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        complexity = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler, ast.With)):
                complexity += 1
        return complexity


class JavaScriptAnalyzer:
    def __init__(self):
        self.token_manager = TokenManager()

    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        return self._analyze_with_regex(content, file_path)

    def _analyze_with_regex(self, content: str, file_path: str) -> Dict[str, Any]:
        functions = []
        classes = []
        imports = []

        lines = content.splitlines()[:200]

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith('import ') or 'require(' in stripped:
                imports.extend(self._extract_import_from_line(stripped))

            if 'function ' in stripped or '=>' in stripped:
                func_info = self._extract_function_from_line(stripped, file_path, i + 1)
                if func_info:
                    functions.append(func_info)

            if stripped.startswith('class '):
                class_info = self._extract_class_from_line(stripped, file_path, i + 1)
                if class_info:
                    classes.append(class_info)

        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'complexity': len(functions) + len(classes),
            'token_count': self.token_manager.count_tokens(content)
        }

    def _extract_import_from_line(self, line: str) -> List[str]:
        imports = []
        import_match = re.search(r'import.*from\s+[\'"]([^\'"]+)[\'"]', line)
        if import_match:
            imports.append(import_match.group(1))
        require_match = re.search(r'require\([\'"]([^\'"]+)[\'"]\)', line)
        if require_match:
            imports.append(require_match.group(1))
        return imports

    def _extract_function_from_line(self, line: str, file_path: str, line_num: int) -> Optional[MethodInfo]:
        function_patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)',
            r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
            r'(\w+)\s*:\s*function\s*\(([^)]*)\)',
            r'(\w+)\s*\(([^)]*)\)\s*{'
        ]

        for pattern in function_patterns:
            match = re.search(pattern, line)
            if match:
                name = match.group(1)
                params_str = match.group(2) if len(match.groups()) > 1 else ""
                params = [p.strip() for p in params_str.split(',') if p.strip()]

                return MethodInfo(
                    name=name,
                    signature=f"{name}({params_str})",
                    description="JavaScript function",
                    complexity_score=min(len(line) // 20, 10),
                    file_path=file_path,
                    line_number=line_num,
                    parameters=params,
                    return_type="any",
                    cyclomatic_complexity=3
                )
        return None

    def _extract_class_from_line(self, line: str, file_path: str, line_num: int) -> Optional[ClassInfo]:
        class_match = re.search(r'class\s+(\w+)(?:\s+extends\s+(\w+))?', line)
        if class_match:
            name = class_match.group(1)
            inheritance = [class_match.group(2)] if class_match.group(2) else []

            return ClassInfo(
                name=name,
                methods=[],
                attributes=[],
                inheritance=inheritance,
                file_path=file_path,
                line_number=line_num
            )
        return None


class SQLAnalyzer:
    def __init__(self):
        self.token_manager = TokenManager()

    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        return self._analyze_with_regex(content, file_path)

    def _analyze_with_regex(self, content: str, file_path: str = "") -> Dict[str, Any]:
        tables = set()
        views = set()
        procedures = set()
        functions = set()
        triggers = set()
        relationships = []

        if len(content) > 100000:
            content = content[:100000]

        content_upper = content.upper()

        table_patterns = [
            r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`|")?(\w+)(?:`|")?',
            r'FROM\s+(?:`|")?(\w+)(?:`|")?(?:\s|$|,|\))',
            r'JOIN\s+(?:`|")?(\w+)(?:`|")?'
        ]

        for pattern in table_patterns:
            matches = re.findall(pattern, content_upper)
            filtered_matches = [m for m in matches if m not in {
                'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER',
                'TABLE', 'VIEW', 'INDEX', 'DATABASE', 'SCHEMA', 'TRIGGER', 'PROCEDURE',
                'NULL', 'NOT', 'DEFAULT', 'PRIMARY', 'KEY', 'FOREIGN', 'UNIQUE'
            }]
            tables.update(filtered_matches)

        view_patterns = [r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(?:`|")?(\w+)(?:`|")?']
        for pattern in view_patterns:
            matches = re.findall(pattern, content_upper)
            views.update(matches)

        return {
            'tables': sorted(list(tables)),
            'views': sorted(list(views)),
            'procedures': sorted(list(procedures)),
            'functions': sorted(list(functions)),
            'triggers': sorted(list(triggers)),
            'relationships': relationships,
            'token_count': self.token_manager.count_tokens(content)
        }


class CodebaseAnalyzer:
    def __init__(self):
        self.llm = LLMClient()
        self.token_manager = TokenManager()

        logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)

        self.python_analyzer = PythonAnalyzer()
        self.js_analyzer = JavaScriptAnalyzer()
        self.sql_analyzer = SQLAnalyzer()

        self.supported_languages = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React JSX',
            '.tsx': 'React TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS'
        }

        self.ignore_patterns = {
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', 'env', '.venv', 'dist', 'build', '.next',
            'coverage', '.coverage', 'logs', '.log', 'target',
            'bin', 'obj', 'vendor', 'pkg', '.idea', '.vscode'
        }

        self.file_lock = Lock()

    def should_ignore_path(self, path: Path) -> bool:
        path_parts = path.parts
        return any(pattern in path_parts for pattern in self.ignore_patterns)

    def get_file_language(self, file_path: Path) -> Optional[str]:
        return self.supported_languages.get(file_path.suffix.lower())

    def scan_codebase(self, project_path: str) -> Tuple[Dict[str, str], List[Tuple[str, str]]]:
        project_path = Path(project_path)
        code_files = {}
        sample_files = []

        file_paths = []
        for file_path in project_path.rglob('*'):
            if len(file_paths) >= MAX_FILES:
                break

            if (file_path.is_file() and
                    not self.should_ignore_path(file_path) and
                    self.get_file_language(file_path) and
                    file_path.stat().st_size < MAX_FILE_SIZE):

                if not INCLUDE_TESTS and any(test_indicator in str(file_path).lower()
                                             for test_indicator in ['test', 'spec']):
                    continue

                file_paths.append(file_path)

        def process_file(file_path):
            try:
                content = self._read_file_fast(file_path)
                if content and content.strip():
                    relative_path = file_path.relative_to(project_path)
                    return str(relative_path), content
            except:
                pass
            return None, None

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(process_file, file_paths))

        for relative_path, content in results:
            if relative_path and content:
                code_files[relative_path] = content
                if len(sample_files) < 10:
                    sample_files.append((relative_path, content))

        return code_files, sample_files

    def _read_file_fast(self, file_path: Path) -> str:
        try:
            file_size = file_path.stat().st_size

            if file_size < 50000:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(50000)
        except:
            return ""

    def analyze_file_structure_fast(self, file_path: str, content: str) -> FileInfo:
        language = self.get_file_language(Path(file_path))

        lines_of_code = len([line for line in content.splitlines()
                             if line.strip() and not line.strip().startswith('#')])
        token_count = self.token_manager.count_tokens(content)

        classes = []
        methods = []
        imports = []
        complexity = 1

        if len(content) > 10000:
            content = content[:10000]

        if language == 'Python':
            analysis = self.python_analyzer.analyze_file(file_path, content)
            classes = analysis.get('classes', [])
            methods = analysis.get('functions', [])
            imports = analysis.get('imports', [])
            complexity = analysis.get('complexity', 1)
        elif language in ['JavaScript', 'TypeScript', 'React JSX', 'React TypeScript']:
            analysis = self.js_analyzer.analyze_file(file_path, content)
            classes = analysis.get('classes', [])
            methods = analysis.get('functions', [])
            imports = analysis.get('imports', [])
            complexity = analysis.get('complexity', 1)
        elif language == 'SQL':
            analysis = self.sql_analyzer.analyze_file(file_path, content)
            complexity = len(analysis.get('tables', []))

        purpose = self.analyze_file_purpose_fast(file_path, language)

        return FileInfo(
            path=file_path,
            language=language,
            lines_of_code=lines_of_code,
            complexity_score=min(complexity, 10),
            purpose=purpose,
            key_classes=classes,
            key_methods=methods,
            imports=imports,
            functions_count=len(methods),
            classes_count=len(classes),
            token_count=token_count,
            architectural_role=self.determine_architectural_role_fast(file_path),
            technical_summary=f"{language} file with {lines_of_code} lines"
        )

    def determine_architectural_role_fast(self, file_path: str) -> str:
        file_path_lower = file_path.lower()

        if any(x in file_path_lower for x in ['controller', 'handler', 'route']):
            return "Request Processing"
        elif any(x in file_path_lower for x in ['service', 'business', 'logic']):
            return "Business Logic"
        elif any(x in file_path_lower for x in ['model', 'entity', 'data']):
            return "Data Access"
        elif any(x in file_path_lower for x in ['view', 'template', 'component', 'ui']):
            return "Presentation"
        elif any(x in file_path_lower for x in ['config', 'setting']):
            return "Configuration"
        elif any(x in file_path_lower for x in ['util', 'helper']):
            return "Utility"
        elif any(x in file_path_lower for x in ['test', 'spec']):
            return "Testing"
        elif 'sql' in file_path_lower:
            return "Data Persistence"
        else:
            return "Core Component"

    def analyze_file_purpose_fast(self, file_path: str, language: str) -> str:
        file_name = Path(file_path).name.lower()

        if 'main' in file_name or 'app' in file_name or 'index' in file_name:
            return "Application entry point"
        elif 'config' in file_name:
            return "Configuration"
        elif 'test' in file_name:
            return "Test file"
        elif 'util' in file_name:
            return "Utility functions"
        elif 'model' in file_path.lower():
            return "Data model"
        elif 'view' in file_path.lower():
            return "View component"
        elif 'controller' in file_path.lower():
            return "Controller logic"
        elif language == 'SQL':
            return "Database script"
        else:
            return f"{language} source file"

    def analyze_database_schema(self, code_files: Dict[str, str]) -> Optional[DatabaseInfo]:
        sql_files = {path: content for path, content in code_files.items()
                     if self.get_file_language(Path(path)) == 'SQL'}

        if not sql_files:
            return None

        all_tables = set()
        all_views = set()

        for file_path, content in sql_files.items():
            analysis = self.sql_analyzer.analyze_file(file_path, content)
            all_tables.update(analysis.get('tables', []))
            all_views.update(analysis.get('views', []))

        return DatabaseInfo(
            tables=sorted(list(all_tables)),
            views=sorted(list(all_views)),
            procedures=[],
            functions=[],
            triggers=[],
            relationships=[],
            schema_purpose="Database schema for application data"
        )

    def analyze_project(self, project_path: str = PROJECT_PATH,
                        project_name: str = PROJECT_NAME) -> ProjectAnalysis:

        if not self.llm.check_connection():
            self.logger.error("Cannot connect to Ollama")
            raise ConnectionError("Ollama not available")

        code_files, sample_files = self.scan_codebase(project_path)
        if not code_files:
            raise ValueError("No code files found")

        file_analyses = []
        total_tokens = 0

        def analyze_file_wrapper(item):
            file_path, content = item
            file_info = self.analyze_file_structure_fast(file_path, content)
            return file_info

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            file_analyses = list(executor.map(analyze_file_wrapper, code_files.items()))

        total_tokens = sum(f.token_count for f in file_analyses)

        project_structure = {
            'total_files': len(code_files),
            'languages': list(set(f.language for f in file_analyses)),
            'total_lines': sum(f.lines_of_code for f in file_analyses),
            'total_tokens': total_tokens
        }

        overview_data = self.llm.analyze_project_overview(project_structure, sample_files)
        database_info = self.analyze_database_schema(code_files)
        quality_metrics = self.calculate_quality_metrics_fast(file_analyses)

        all_methods = []
        all_classes = []
        for file_info in file_analyses:
            all_methods.extend(file_info.key_methods)
            all_classes.extend(file_info.key_classes)

        all_methods.sort(key=lambda x: x.complexity_score, reverse=True)
        all_classes.sort(key=lambda x: len(x.methods), reverse=True)

        dependencies = self.extract_dependencies_fast(file_analyses)
        recommendations = self.generate_recommendations_fast(quality_metrics, database_info)

        token_stats = {
            'total_tokens': total_tokens,
            'average_tokens_per_file': total_tokens // len(file_analyses) if file_analyses else 0
        }

        complexity_summary = {
            'average_complexity': quality_metrics.get('average_complexity', 0),
            'high_complexity_files': quality_metrics.get('complex_files_count', 0),
            'total_methods_analyzed': len(all_methods),
            'maintainability_score': quality_metrics.get('maintainability_score', 50)
        }

        analysis = ProjectAnalysis(
            project_name=project_name,
            analysis_date=datetime.now().isoformat(),
            overview=overview_data.get('project_purpose', 'Software project'),
            business_domain=overview_data.get('business_domain', 'Software Development'),
            technical_architecture=overview_data.get('technical_architecture', 'Multi-layered application'),
            tech_stack=project_structure['languages'],
            architecture_pattern=overview_data.get('architecture_pattern', 'Layered Architecture'),
            total_files=len(code_files),
            total_lines=sum(len(content.splitlines()) for content in code_files.values()),
            total_tokens=total_tokens,
            complexity_summary=complexity_summary,
            files=file_analyses,
            key_methods=all_methods[:20],
            key_classes=all_classes[:10],
            dependencies=dependencies,
            database_info=database_info,
            recommendations=recommendations,
            code_quality_metrics=quality_metrics,
            token_usage_stats=token_stats,
            project_summary=f"This is a {overview_data.get('business_domain', 'software')} project with {len(code_files)} files.",
            use_cases=overview_data.get('primary_use_cases', []),
            technical_highlights=[]
        )

        return analysis

    def calculate_quality_metrics_fast(self, file_analyses: List[FileInfo]) -> Dict[str, Any]:
        if not file_analyses:
            return {}

        total_files = len(file_analyses)
        total_lines = sum(f.lines_of_code for f in file_analyses)
        avg_complexity = sum(f.complexity_score for f in file_analyses) / total_files

        large_files = [f for f in file_analyses if f.lines_of_code > 300]
        complex_files = [f for f in file_analyses if f.complexity_score > 5]

        return {
            'average_file_size': round(total_lines / total_files, 1),
            'average_complexity': round(avg_complexity, 2),
            'large_files_count': len(large_files),
            'complex_files_count': len(complex_files),
            'total_methods': sum(f.functions_count for f in file_analyses),
            'maintainability_score': max(100 - (len(large_files) * 10) - (len(complex_files) * 15), 0)
        }

    def extract_dependencies_fast(self, file_analyses: List[FileInfo]) -> List[str]:
        all_imports = set()

        for file_info in file_analyses:
            for imp in file_info.imports:
                if '.' in imp:
                    all_imports.add(imp.split('.')[0])
                else:
                    all_imports.add(imp)

        common_builtins = {'os', 'sys', 'json', 'time', 'datetime', 're'}
        external_deps = [dep for dep in all_imports if dep not in common_builtins and len(dep) > 2]

        return sorted(external_deps)[:20]

    def generate_recommendations_fast(self, quality_metrics: Dict[str, Any],
                                      database_info: Optional[DatabaseInfo]) -> List[str]:
        recommendations = []

        if quality_metrics.get('large_files_count', 0) > 0:
            recommendations.append(f"Consider splitting {quality_metrics['large_files_count']} large files")

        if quality_metrics.get('complex_files_count', 0) > 0:
            recommendations.append(f"Refactor {quality_metrics['complex_files_count']} complex files")

        if quality_metrics.get('maintainability_score', 50) < 70:
            recommendations.append("Improve code maintainability")

        recommendations.extend([
            "Add automated testing",
            "Improve documentation",
            "Set up CI/CD pipeline"
        ])

        return recommendations[:8]

    def save_analysis(self, analysis: ProjectAnalysis, output_file: str = OUTPUT_FILE) -> str:
        indent = 2 if PRETTY_PRINT else None
        analysis_dict = asdict(analysis)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=indent, ensure_ascii=False, default=str)

        return output_file


if __name__ == "__main__":
    if not Path(PROJECT_PATH).exists():
        exit(1)

    try:
        analyzer = CodebaseAnalyzer()
        analysis = analyzer.analyze_project()
        output_file = analyzer.save_analysis(analysis)

        print(f"Analysis complete: {output_file}")
        print(f"Files: {analysis.total_files}")
        print(f"Lines: {analysis.total_lines:,}")
        print(f"Tokens: {analysis.total_tokens:,}")
        print(f"Languages: {', '.join(analysis.tech_stack)}")

    except Exception as e:
        print(f"Error: {e}")
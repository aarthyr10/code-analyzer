#!/usr/bin/env python3

import ast
import json
import logging
import os
import re
import time
from abc import ABC, abstractmethod
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

import javalang
import networkx as nx
from javalang.tree import *
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('codebase_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    path: str
    name: str
    language: str
    lines_of_code: int
    classes_count: int
    methods_count: int
    size_bytes: int
    extension: str


@dataclass
class FolderInfo:
    path: str
    name: str
    total_files: int
    files_by_language: Dict[str, int]
    total_lines_of_code: int
    total_classes: int
    total_methods: int
    files: List[FileInfo]


@dataclass
class VariableInfo:
    name: str
    type: str
    scope: str
    line_declared: int
    is_used: bool
    usage_count: int
    file_path: str
    method_name: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class CodingStandardViolation:
    rule: str
    severity: str
    message: str
    file_path: str
    line_number: int
    column: Optional[int] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


@dataclass
class StyleValidation:
    is_valid: bool
    violations: List[CodingStandardViolation]
    style_score: float
    file_path: str
    language: str


@dataclass
class LanguageMethod:
    name: str
    class_name: str
    package: str
    parameters: List[Dict[str, str]]
    return_type: str
    modifiers: List[str]
    line_start: int
    line_end: int
    complexity: int
    lines_of_code: int
    annotations: List[str]
    calls_methods: List[str]
    local_variables: int
    is_used: bool = False
    usage_count: int = 0


@dataclass
class LanguageClass:
    name: str
    package: str
    file_path: str
    modifiers: List[str]
    extends: Optional[str]
    implements: List[str]
    methods: List[LanguageMethod]
    fields: List[Dict[str, Any]]
    inner_classes: List[str]
    imports: List[str]
    lines_of_code: int
    complexity_score: float
    annotations: List[str]
    language: str
    is_used: bool = False
    usage_count: int = 0


@dataclass
class CodeIssue:
    severity: str
    category: str
    rule: str
    message: str
    file_path: str
    line_number: int
    method_name: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class AnalysisMetrics:
    start_time: float
    end_time: float
    files_processed: int
    methods_analyzed: int
    classes_analyzed: int
    issues_found: int
    token_usage: Dict[str, int]
    api_calls: int
    languages_detected: Dict[str, int]
    variables_analyzed: int = 0
    style_violations: int = 0


class LanguageDetector:
    LANGUAGE_EXTENSIONS = {
        '.java': 'java',
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'scss',
        '.less': 'less',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.go': 'go',
        '.php': 'php',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.rs': 'rust',
        '.swift': 'swift',
        '.dart': 'dart',
        '.xml': 'xml',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.sql': 'sql',
        '.sh': 'shell',
        '.bash': 'shell',
        '.ps1': 'powershell',
        # Image file extensions
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.bmp': 'image',
        '.tiff': 'image',
        '.tif': 'image',
        '.webp': 'image',
        '.svg': 'image',
        '.ico': 'image',
        '.psd': 'image',
        '.raw': 'image',
        '.heic': 'image',
        '.heif': 'image'
    }

    SUPPORTED_LANGUAGES = {'java', 'python', 'javascript', 'html', 'css', 'scss'}

    NO_ANALYSIS_LANGUAGES = {'image'}

    @classmethod
    def detect_language(cls, file_path: Path) -> str:
        extension = file_path.suffix.lower()
        return cls.LANGUAGE_EXTENSIONS.get(extension, 'unknown')

    @classmethod
    def get_supported_languages(cls) -> Set[str]:
        return cls.SUPPORTED_LANGUAGES

    @classmethod
    def is_supported(cls, language: str) -> bool:
        return language in cls.SUPPORTED_LANGUAGES

    @classmethod
    def needs_analysis(cls, language: str) -> bool:
        """Check if a language needs code analysis"""
        return language not in cls.NO_ANALYSIS_LANGUAGES and language != 'unknown'

    @classmethod
    def get_all_detectable_languages(cls) -> Set[str]:
        return set(cls.LANGUAGE_EXTENSIONS.values())

    @classmethod
    def is_web_language(cls, language: str) -> bool:
        return language in {'javascript', 'html', 'css', 'scss'}

    @classmethod
    def is_programming_language(cls, language: str) -> bool:
        return language in {'java', 'python', 'javascript'}

    @classmethod
    def is_image_file(cls, language: str) -> bool:
        return language == 'image'


class FileExtractor:
    def __init__(self, codebase_path: Path):
        self.codebase_path = codebase_path
        self.skip_dirs = {'.git', '.svn', '.hg', 'node_modules', '__pycache__', 'target', 'build', 'dist', '.idea',
                          '.vscode', 'bin', 'obj'}
        self.skip_files = {'.DS_Store', 'Thumbs.db', '.gitignore', '.gitkeep'}
        self.unknown_extensions = set()  # Track unknown file extensions

    def _should_skip_dir(self, dir_path: Path) -> bool:
        return any(skip_dir in str(dir_path) for skip_dir in self.skip_dirs)

    def _should_skip_file(self, file_path: Path) -> bool:
        return (file_path.name in self.skip_files or
                file_path.name.startswith('.') and len(file_path.name) > 1)

    def _count_classes_methods(self, content: str, language: str) -> Tuple[int, int]:
        classes_count = 0
        methods_count = 0

        try:
            if language == 'java':
                tree = javalang.parse.parse(content)
                for class_decl in tree.types:
                    if isinstance(class_decl, ClassDeclaration):
                        classes_count += 1
                        methods_count += len(class_decl.methods) if class_decl.methods else 0

            elif language == 'python':
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes_count += 1
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                methods_count += 1

            elif language == 'javascript':
                classes_count = content.count('class ')
                methods_count = content.count('function ') + content.count('=>')

            elif language == 'html':
                classes_count = 0
                methods_count = content.count('<script>')

            elif language == 'css':
                classes_count = content.count('.') + content.count('#')
                methods_count = 0

            elif language == 'scss':
                classes_count = content.count('.') + content.count('#') + content.count('@mixin')
                methods_count = content.count('@function')
            else:
                classes_count = content.count('class ')
                methods_count = content.count('def ') + content.count('function ')

        except Exception:
            classes_count = content.count('class ')
            methods_count = content.count('def ') + content.count('function ') + content.count(
                'public ') + content.count('private ')

        return classes_count, methods_count

    def extract_files(self) -> Tuple[List[FolderInfo], Dict[str, int], List[str], List[str]]:
        logger.info(f"Starting file extraction from: {self.codebase_path}")

        folders = []
        language_summary = defaultdict(int)
        unsupported_languages = set()

        for root_path in self.codebase_path.rglob('*'):
            if root_path.is_dir() and not self._should_skip_dir(root_path):
                folder_info = self._analyze_folder(root_path, language_summary, unsupported_languages)
                if folder_info.total_files > 0:
                    folders.append(folder_info)

        logger.info(f"Extracted {len(folders)} folders with {sum(language_summary.values())} total files")
        return folders, dict(language_summary), list(unsupported_languages), list(self.unknown_extensions)

    def _analyze_folder(self, folder_path: Path, language_summary: Dict[str, int],
                        unsupported_languages: Set[str]) -> FolderInfo:
        files = []
        files_by_language = defaultdict(int)
        total_lines = 0
        total_classes = 0
        total_methods = 0

        for file_path in folder_path.iterdir():
            if file_path.is_file() and not self._should_skip_file(file_path):
                file_info = self._analyze_file(file_path)
                if file_info:
                    files.append(file_info)
                    files_by_language[file_info.language] += 1
                    language_summary[file_info.language] += 1
                    total_lines += file_info.lines_of_code
                    total_classes += file_info.classes_count
                    total_methods += file_info.methods_count

                    # Track unknown extensions
                    if file_info.language == 'unknown':
                        self.unknown_extensions.add(file_path.suffix.lower())

                    # Track unsupported languages (excluding images and unknown)
                    if (not LanguageDetector.is_supported(file_info.language) and
                            not LanguageDetector.is_image_file(file_info.language) and
                            file_info.language != 'unknown'):
                        unsupported_languages.add(file_info.language)

        return FolderInfo(
            path=str(folder_path),
            name=folder_path.name,
            total_files=len(files),
            files_by_language=dict(files_by_language),
            total_lines_of_code=total_lines,
            total_classes=total_classes,
            total_methods=total_methods,
            files=files
        )

    def _analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        try:
            language = LanguageDetector.detect_language(file_path)

            # For image files, set minimal metrics
            if LanguageDetector.is_image_file(language):
                return FileInfo(
                    path=str(file_path),
                    name=file_path.name,
                    language=language,
                    lines_of_code=0,  # Images have no lines of code
                    classes_count=0,
                    methods_count=0,
                    size_bytes=file_path.stat().st_size,
                    extension=file_path.suffix
                )

            # For non-image files, read content and analyze
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines_of_code = len([line for line in content.split('\n') if line.strip()])
            classes_count, methods_count = self._count_classes_methods(content, language)

            return FileInfo(
                path=str(file_path),
                name=file_path.name,
                language=language,
                lines_of_code=lines_of_code,
                classes_count=classes_count,
                methods_count=methods_count,
                size_bytes=file_path.stat().st_size,
                extension=file_path.suffix
            )
        except Exception as e:
            logger.warning(f"Failed to analyze file {file_path}: {e}")
            return None


class BaseCodeAnalyzer(ABC):
    def __init__(self):
        self.issues = []
        self.complexity_threshold = 10
        self.method_length_threshold = 50
        self.class_length_threshold = 300

    @abstractmethod
    def analyze_file(self, file_path: str, content: str) -> Tuple[List[LanguageClass], List[CodeIssue]]:
        pass

    @abstractmethod
    def get_language(self) -> str:
        pass

    @abstractmethod
    def extract_variables(self, content: str, file_path: str) -> List[VariableInfo]:
        pass

    @abstractmethod
    def validate_coding_standards(self, content: str, file_path: str) -> StyleValidation:
        pass

    def _calculate_complexity_generic(self, code_str: str) -> int:
        complexity = 1
        complexity += code_str.count('if ')
        complexity += code_str.count('else ')
        complexity += code_str.count('elif ')
        complexity += code_str.count('while ')
        complexity += code_str.count('for ')
        complexity += code_str.count('case ')
        complexity += code_str.count('catch ')
        complexity += code_str.count('except ')
        complexity += code_str.count('&& ')
        complexity += code_str.count('|| ')
        complexity += code_str.count(' and ')
        complexity += code_str.count(' or ')
        complexity += code_str.count('? ')
        return complexity


class JavaCodeAnalyzer(BaseCodeAnalyzer):
    def get_language(self) -> str:
        return 'java'

    def analyze_file(self, file_path: str, content: str) -> Tuple[List[LanguageClass], List[CodeIssue]]:
        issues = []
        classes = []

        try:
            tree = javalang.parse.parse(content)
            package_name = tree.package.name if tree.package else "default"
            imports = [imp.path for imp in tree.imports] if tree.imports else []

            for class_decl in tree.types:
                if isinstance(class_decl, ClassDeclaration):
                    java_class, class_issues = self._analyze_class(
                        class_decl, package_name, file_path, imports, content
                    )
                    classes.append(java_class)
                    issues.extend(class_issues)

        except Exception as e:
            logger.warning(f"Failed to parse Java file {file_path}: {e}")
            issues.append(CodeIssue(
                severity="HIGH",
                category="RELIABILITY",
                rule="PARSE_ERROR",
                message=f"Failed to parse Java file: {e}",
                file_path=file_path,
                line_number=1
            ))

        return classes, issues

    def _analyze_class(self, class_decl, package_name: str, file_path: str,
                       imports: List[str], content: str) -> Tuple[LanguageClass, List[CodeIssue]]:
        issues = []
        methods = []
        fields = []

        class_name = class_decl.name
        modifiers = class_decl.modifiers if class_decl.modifiers else []
        extends = class_decl.extends.name if class_decl.extends else None
        implements = [impl.name for impl in class_decl.implements] if class_decl.implements else []
        annotations = [ann.name for ann in class_decl.annotations] if class_decl.annotations else []

        for method in class_decl.methods:
            java_method, method_issues = self._analyze_method(
                method, class_name, package_name, content
            )
            methods.append(java_method)
            issues.extend(method_issues)

        for field in class_decl.fields:
            field_info = self._analyze_field(field, class_name, file_path)
            fields.append(field_info)

        total_loc = len([line for line in content.split('\n') if line.strip()])
        complexity_score = sum(method.complexity for method in methods) / len(methods) if methods else 0

        if total_loc > self.class_length_threshold:
            issues.append(CodeIssue(
                severity="MEDIUM",
                category="MAINTAINABILITY",
                rule="CLASS_TOO_LONG",
                message=f"Class has {total_loc} lines, consider splitting",
                file_path=file_path,
                line_number=1,
                suggestion="Split into smaller, focused classes"
            ))

        if len(methods) > 20:
            issues.append(CodeIssue(
                severity="HIGH",
                category="MAINTAINABILITY",
                rule="GOD_CLASS",
                message=f"Class has {len(methods)} methods, violates Single Responsibility Principle",
                file_path=file_path,
                line_number=1,
                suggestion="Decompose into multiple classes with single responsibilities"
            ))

        java_class = LanguageClass(
            name=class_name,
            package=package_name,
            file_path=file_path,
            modifiers=modifiers,
            extends=extends,
            implements=implements,
            methods=methods,
            fields=fields,
            inner_classes=[],
            imports=imports,
            lines_of_code=total_loc,
            complexity_score=complexity_score,
            annotations=annotations,
            language='java'
        )

        return java_class, issues

    def _analyze_method(self, method_decl, class_name: str, package_name: str,
                        content: str) -> Tuple[LanguageMethod, List[CodeIssue]]:
        issues = []

        method_name = method_decl.name
        modifiers = method_decl.modifiers if method_decl.modifiers else []
        return_type = method_decl.return_type.name if method_decl.return_type else "void"
        annotations = [ann.name for ann in method_decl.annotations] if method_decl.annotations else []

        parameters = []
        if method_decl.parameters:
            for param in method_decl.parameters:
                parameters.append({
                    "name": param.name,
                    "type": param.type.name if hasattr(param.type, 'name') else str(param.type)
                })

        complexity = self._calculate_complexity(method_decl)
        method_content = str(method_decl.body) if method_decl.body else ""
        loc = len([line for line in method_content.split('\n') if line.strip()])

        calls_methods = self._extract_method_calls(method_content)

        if complexity > self.complexity_threshold:
            issues.append(CodeIssue(
                severity="HIGH",
                category="MAINTAINABILITY",
                rule="COMPLEX_METHOD",
                message=f"Method complexity is {complexity}, exceeds threshold of {self.complexity_threshold}",
                file_path="",
                line_number=1,
                method_name=method_name,
                suggestion="Break down into smaller methods"
            ))

        if loc > self.method_length_threshold:
            issues.append(CodeIssue(
                severity="MEDIUM",
                category="MAINTAINABILITY",
                rule="LONG_METHOD",
                message=f"Method has {loc} lines, consider refactoring",
                file_path="",
                line_number=1,
                method_name=method_name,
                suggestion="Extract functionality into separate methods"
            ))

        java_method = LanguageMethod(
            name=method_name,
            class_name=class_name,
            package=package_name,
            parameters=parameters,
            return_type=return_type,
            modifiers=modifiers,
            line_start=1,
            line_end=1,
            complexity=complexity,
            lines_of_code=loc,
            annotations=annotations,
            calls_methods=calls_methods,
            local_variables=0
        )

        return java_method, issues

    def _analyze_field(self, field_decl, class_name: str, file_path: str) -> Dict[str, Any]:
        field_info = {
            "name": field_decl.declarators[0].name if field_decl.declarators else "unknown",
            "type": field_decl.type.name if hasattr(field_decl.type, 'name') else str(field_decl.type),
            "modifiers": field_decl.modifiers if field_decl.modifiers else [],
            "class_name": class_name,
            "is_static": "static" in (field_decl.modifiers or []),
            "is_final": "final" in (field_decl.modifiers or []),
            "visibility": self._get_visibility(field_decl.modifiers or [])
        }
        return field_info

    def _calculate_complexity(self, method_decl) -> int:
        if method_decl.body:
            method_str = str(method_decl.body)
            return self._calculate_complexity_generic(method_str)
        return 1

    def _extract_method_calls(self, method_content: str) -> List[str]:
        pattern = r'(\w+)\s*\('
        matches = re.findall(pattern, method_content)
        return list(set(matches))

    def _get_visibility(self, modifiers: List[str]) -> str:
        if "private" in modifiers:
            return "private"
        elif "protected" in modifiers:
            return "protected"
        elif "public" in modifiers:
            return "public"
        else:
            return "package-private"

    def extract_variables(self, content: str, file_path: str) -> List[VariableInfo]:
        variables = []
        try:
            tree = javalang.parse.parse(content)
            for class_decl in tree.types:
                if isinstance(class_decl, ClassDeclaration):
                    for field in class_decl.fields:
                        for declarator in field.declarators:
                            variables.append(VariableInfo(
                                name=declarator.name,
                                type=field.type.name if hasattr(field.type, 'name') else str(field.type),
                                scope='class',
                                line_declared=1,
                                is_used=False,
                                usage_count=0,
                                file_path=file_path,
                                class_name=class_decl.name
                            ))

                    for method in class_decl.methods:
                        if method.body:
                            method_vars = self._extract_method_variables(method, class_decl.name, file_path)
                            variables.extend(method_vars)
        except Exception as e:
            logger.warning(f"Failed to extract variables from {file_path}: {e}")

        return variables

    def _extract_method_variables(self, method_decl, class_name: str, file_path: str) -> List[VariableInfo]:
        variables = []
        method_content = str(method_decl.body) if method_decl.body else ""

        var_patterns = [
            r'(\w+)\s+(\w+)\s*=',
            r'(\w+)\s+(\w+)\s*;',
        ]

        for pattern in var_patterns:
            matches = re.findall(pattern, method_content)
            for match in matches:
                if len(match) == 2:
                    var_type, var_name = match
                    variables.append(VariableInfo(
                        name=var_name,
                        type=var_type,
                        scope='method',
                        line_declared=1,
                        is_used=var_name in method_content,
                        usage_count=method_content.count(var_name) - 1,
                        file_path=file_path,
                        method_name=method_decl.name,
                        class_name=class_name
                    ))

        return variables

    def validate_coding_standards(self, content: str, file_path: str) -> StyleValidation:
        violations = []

        violations.extend(self._check_naming_conventions(content, file_path))
        violations.extend(self._check_code_formatting(content, file_path))
        violations.extend(self._check_java_best_practices(content, file_path))

        style_score = max(0, 10 - len(violations) * 0.5)

        return StyleValidation(
            is_valid=len(violations) == 0,
            violations=violations,
            style_score=style_score,
            file_path=file_path,
            language='java'
        )

    def _check_naming_conventions(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if 'class ' in line:
                class_match = re.search(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', line)
                if class_match:
                    class_name = class_match.group(1)
                    if not class_name[0].isupper():
                        violations.append(CodingStandardViolation(
                            rule='JAVA_CLASS_NAMING',
                            severity='MEDIUM',
                            message=f'Class name "{class_name}" should start with uppercase letter',
                            file_path=file_path,
                            line_number=i,
                            suggestion=f'Rename to "{class_name.capitalize()}"'
                        ))

            method_match = re.search(r'(public|private|protected).*?\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
            if method_match:
                method_name = method_match.group(2)
                if method_name[0].isupper():
                    violations.append(CodingStandardViolation(
                        rule='JAVA_METHOD_NAMING',
                        severity='MEDIUM',
                        message=f'Method name "{method_name}" should start with lowercase letter',
                        file_path=file_path,
                        line_number=i,
                        suggestion=f'Rename to "{method_name[0].lower() + method_name[1:]}"'
                    ))

        return violations

    def _check_code_formatting(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                violations.append(CodingStandardViolation(
                    rule='LINE_LENGTH',
                    severity='LOW',
                    message=f'Line exceeds 120 characters ({len(line)} characters)',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Break line into multiple lines'
                ))

            if line.rstrip() != line:
                violations.append(CodingStandardViolation(
                    rule='TRAILING_WHITESPACE',
                    severity='LOW',
                    message='Line has trailing whitespace',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Remove trailing whitespace'
                ))

        return violations

    def _check_java_best_practices(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if 'System.out.println' in line:
                violations.append(CodingStandardViolation(
                    rule='NO_SYSTEM_OUT',
                    severity='MEDIUM',
                    message='Avoid using System.out.println in production code',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Use proper logging framework instead'
                ))

            if re.search(r'catch\s*\([^)]+\)\s*\{\s*\}', line):
                violations.append(CodingStandardViolation(
                    rule='EMPTY_CATCH_BLOCK',
                    severity='HIGH',
                    message='Empty catch block found',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Add proper exception handling or logging'
                ))

        return violations


class PythonCodeAnalyzer(BaseCodeAnalyzer):
    def get_language(self) -> str:
        return 'python'

    def analyze_file(self, file_path: str, content: str) -> Tuple[List[LanguageClass], List[CodeIssue]]:
        issues = []
        classes = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    python_class, class_issues = self._analyze_class(node, file_path, content)
                    classes.append(python_class)
                    issues.extend(class_issues)

        except Exception as e:
            logger.warning(f"Failed to parse Python file {file_path}: {e}")
            issues.append(CodeIssue(
                severity="HIGH",
                category="RELIABILITY",
                rule="PARSE_ERROR",
                message=f"Failed to parse Python file: {e}",
                file_path=file_path,
                line_number=1
            ))

        return classes, issues

    def _analyze_class(self, class_node: ast.ClassDef, file_path: str, content: str) -> Tuple[
        LanguageClass, List[CodeIssue]]:
        issues = []
        methods = []
        fields = []

        class_name = class_node.name
        base_classes = [base.id if isinstance(base, ast.Name) else str(base) for base in class_node.bases]
        decorators = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in class_node.decorator_list]

        imports = self._extract_imports(content)

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method, method_issues = self._analyze_method(node, class_name, content)
                methods.append(method)
                issues.extend(method_issues)
            elif isinstance(node, ast.Assign):
                field_info = self._analyze_field(node, class_name)
                if field_info:
                    fields.append(field_info)

        content_lines = content.split('\n')
        class_start = class_node.lineno - 1
        class_end = class_node.end_lineno if hasattr(class_node, 'end_lineno') else len(content_lines)
        class_content = '\n'.join(content_lines[class_start:class_end])
        total_loc = len([line for line in class_content.split('\n') if line.strip()])

        complexity_score = sum(method.complexity for method in methods) / len(methods) if methods else 0

        if total_loc > self.class_length_threshold:
            issues.append(CodeIssue(
                severity="MEDIUM",
                category="MAINTAINABILITY",
                rule="CLASS_TOO_LONG",
                message=f"Class has {total_loc} lines, consider splitting",
                file_path=file_path,
                line_number=class_node.lineno,
                suggestion="Split into smaller, focused classes"
            ))

        if len(methods) > 15:
            issues.append(CodeIssue(
                severity="HIGH",
                category="MAINTAINABILITY",
                rule="GOD_CLASS",
                message=f"Class has {len(methods)} methods, violates Single Responsibility Principle",
                file_path=file_path,
                line_number=class_node.lineno,
                suggestion="Decompose into multiple classes with single responsibilities"
            ))

        python_class = LanguageClass(
            name=class_name,
            package="",
            file_path=file_path,
            modifiers=[],
            extends=base_classes[0] if base_classes else None,
            implements=[],
            methods=methods,
            fields=fields,
            inner_classes=[],
            imports=imports,
            lines_of_code=total_loc,
            complexity_score=complexity_score,
            annotations=decorators,
            language='python'
        )

        return python_class, issues

    def _analyze_method(self, method_node: ast.FunctionDef, class_name: str, content: str) -> Tuple[
        LanguageMethod, List[CodeIssue]]:
        issues = []

        method_name = method_node.name
        args = [arg.arg for arg in method_node.args.args]
        returns = ast.unparse(method_node.returns) if method_node.returns else "None"
        decorators = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in method_node.decorator_list]

        parameters = [{"name": arg, "type": "Any"} for arg in args]

        content_lines = content.split('\n')
        method_start = method_node.lineno - 1
        method_end = method_node.end_lineno if hasattr(method_node, 'end_lineno') else method_start + 10
        method_content = '\n'.join(content_lines[method_start:method_end])

        complexity = self._calculate_complexity_generic(method_content)
        loc = len([line for line in method_content.split('\n') if line.strip()])

        calls_methods = self._extract_method_calls_python(method_node)

        if complexity > self.complexity_threshold:
            issues.append(CodeIssue(
                severity="HIGH",
                category="MAINTAINABILITY",
                rule="COMPLEX_METHOD",
                message=f"Method complexity is {complexity}, exceeds threshold of {self.complexity_threshold}",
                file_path="",
                line_number=method_node.lineno,
                method_name=method_name,
                suggestion="Break down into smaller methods"
            ))

        if loc > self.method_length_threshold:
            issues.append(CodeIssue(
                severity="MEDIUM",
                category="MAINTAINABILITY",
                rule="LONG_METHOD",
                message=f"Method has {loc} lines, consider refactoring",
                file_path="",
                line_number=method_node.lineno,
                method_name=method_name,
                suggestion="Extract functionality into separate methods"
            ))

        python_method = LanguageMethod(
            name=method_name,
            class_name=class_name,
            package="",
            parameters=parameters,
            return_type=returns,
            modifiers=[],
            line_start=method_node.lineno,
            line_end=method_end,
            complexity=complexity,
            lines_of_code=loc,
            annotations=decorators,
            calls_methods=calls_methods,
            local_variables=0
        )

        return python_method, issues

    def _analyze_field(self, assign_node: ast.Assign, class_name: str) -> Optional[Dict[str, Any]]:
        if assign_node.targets:
            target = assign_node.targets[0]
            if isinstance(target, ast.Name):
                return {
                    "name": target.id,
                    "type": "Any",
                    "modifiers": [],
                    "class_name": class_name,
                    "is_static": False,
                    "is_final": False,
                    "visibility": "public"
                }
        return None

    def _extract_imports(self, content: str) -> List[str]:
        imports = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        return imports

    def _extract_method_calls_python(self, method_node: ast.FunctionDef) -> List[str]:
        calls = []
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        return list(set(calls))

    def extract_variables(self, content: str, file_path: str) -> List[VariableInfo]:
        variables = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append(VariableInfo(
                                name=target.id,
                                type='Any',
                                scope='global',
                                line_declared=node.lineno,
                                is_used=False,
                                usage_count=0,
                                file_path=file_path
                            ))
                elif isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        variables.append(VariableInfo(
                            name=arg.arg,
                            type='Any',
                            scope='parameter',
                            line_declared=node.lineno,
                            is_used=True,
                            usage_count=1,
                            file_path=file_path,
                            method_name=node.name
                        ))
        except Exception as e:
            logger.warning(f"Failed to extract variables from {file_path}: {e}")

        return variables

    def validate_coding_standards(self, content: str, file_path: str) -> StyleValidation:
        violations = []

        violations.extend(self._check_python_naming_conventions(content, file_path))
        violations.extend(self._check_python_formatting(content, file_path))
        violations.extend(self._check_python_best_practices(content, file_path))

        style_score = max(0, 10 - len(violations) * 0.5)

        return StyleValidation(
            is_valid=len(violations) == 0,
            violations=violations,
            style_score=style_score,
            file_path=file_path,
            language='python'
        )

    def _check_python_naming_conventions(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if line.strip().startswith('class '):
                class_match = re.search(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', line)
                if class_match:
                    class_name = class_match.group(1)
                    if not class_name[0].isupper() or '_' in class_name:
                        violations.append(CodingStandardViolation(
                            rule='PYTHON_CLASS_NAMING',
                            severity='MEDIUM',
                            message=f'Class name "{class_name}" should use PascalCase',
                            file_path=file_path,
                            line_number=i,
                            suggestion='Use PascalCase for class names'
                        ))

            if line.strip().startswith('def '):
                func_match = re.search(r'def\s+([A-Za-z_][A-Za-z0-9_]*)', line)
                if func_match:
                    func_name = func_match.group(1)
                    if any(c.isupper() for c in func_name) and not func_name.startswith('__'):
                        violations.append(CodingStandardViolation(
                            rule='PYTHON_FUNCTION_NAMING',
                            severity='MEDIUM',
                            message=f'Function name "{func_name}" should use snake_case',
                            file_path=file_path,
                            line_number=i,
                            suggestion='Use snake_case for function names'
                        ))

        return violations

    def _check_python_formatting(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                violations.append(CodingStandardViolation(
                    rule='PEP8_LINE_LENGTH',
                    severity='LOW',
                    message=f'Line exceeds 79 characters ({len(line)} characters)',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Break line according to PEP 8'
                ))

            if line.endswith(' ') or line.endswith('\t'):
                violations.append(CodingStandardViolation(
                    rule='TRAILING_WHITESPACE',
                    severity='LOW',
                    message='Line has trailing whitespace',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Remove trailing whitespace'
                ))

        return violations

    def _check_python_best_practices(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if 'print(' in line and 'debug' not in line.lower():
                violations.append(CodingStandardViolation(
                    rule='NO_PRINT_STATEMENTS',
                    severity='MEDIUM',
                    message='Avoid using print() in production code',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Use logging module instead'
                ))

            if 'except:' in line:
                violations.append(CodingStandardViolation(
                    rule='BARE_EXCEPT',
                    severity='HIGH',
                    message='Bare except clause found',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Catch specific exceptions instead'
                ))

        return violations


class JavaScriptCodeAnalyzer(BaseCodeAnalyzer):
    def get_language(self) -> str:
        return 'javascript'

    def analyze_file(self, file_path: str, content: str) -> Tuple[List[LanguageClass], List[CodeIssue]]:
        issues = []
        classes = []

        try:
            class_matches = re.finditer(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', content)
            for match in class_matches:
                class_name = match.group(1)
                js_class = LanguageClass(
                    name=class_name,
                    package="",
                    file_path=file_path,
                    modifiers=[],
                    extends=None,
                    implements=[],
                    methods=[],
                    fields=[],
                    inner_classes=[],
                    imports=self._extract_imports_js(content),
                    lines_of_code=len(content.split('\n')),
                    complexity_score=1.0,
                    annotations=[],
                    language='javascript'
                )
                classes.append(js_class)

        except Exception as e:
            logger.warning(f"Failed to parse JavaScript file {file_path}: {e}")

        return classes, issues

    def _extract_imports_js(self, content: str) -> List[str]:
        imports = []
        import_patterns = [
            r'import\s+.*?from\s+["\']([^"\']+)["\']',
            r'require\(["\']([^"\']+)["\']\)',
        ]
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        return imports

    def extract_variables(self, content: str, file_path: str) -> List[VariableInfo]:
        variables = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            var_patterns = [
                r'(let|const|var)\s+([A-Za-z_][A-Za-z0-9_]*)',
                r'function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(',
            ]

            for pattern in var_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if isinstance(match, tuple) and len(match) == 2:
                        var_type, var_name = match
                    else:
                        var_type, var_name = 'function', match

                    variables.append(VariableInfo(
                        name=var_name,
                        type=var_type,
                        scope='global',
                        line_declared=i,
                        is_used=content.count(var_name) > 1,
                        usage_count=content.count(var_name) - 1,
                        file_path=file_path
                    ))

        return variables

    def validate_coding_standards(self, content: str, file_path: str) -> StyleValidation:
        violations = []

        violations.extend(self._check_js_naming_conventions(content, file_path))
        violations.extend(self._check_js_formatting(content, file_path))
        violations.extend(self._check_js_best_practices(content, file_path))

        style_score = max(0, 10 - len(violations) * 0.5)

        return StyleValidation(
            is_valid=len(violations) == 0,
            violations=violations,
            style_score=style_score,
            file_path=file_path,
            language='javascript'
        )

    def _check_js_naming_conventions(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            var_match = re.search(r'(let|const|var)\s+([A-Z][A-Za-z0-9_]*)', line)
            if var_match:
                var_name = var_match.group(2)
                violations.append(CodingStandardViolation(
                    rule='JS_VARIABLE_NAMING',
                    severity='MEDIUM',
                    message=f'Variable "{var_name}" should use camelCase',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Use camelCase for variable names'
                ))

        return violations

    def _check_js_formatting(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                violations.append(CodingStandardViolation(
                    rule='JS_LINE_LENGTH',
                    severity='LOW',
                    message=f'Line exceeds 100 characters ({len(line)} characters)',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Break line into multiple lines'
                ))

        return violations

    def _check_js_best_practices(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if 'console.log' in line:
                violations.append(CodingStandardViolation(
                    rule='NO_CONSOLE_LOG',
                    severity='MEDIUM',
                    message='Avoid console.log in production code',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Use proper logging library'
                ))

            if 'var ' in line:
                violations.append(CodingStandardViolation(
                    rule='NO_VAR_DECLARATION',
                    severity='MEDIUM',
                    message='Use let or const instead of var',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Replace var with let or const'
                ))

        return violations


class HTMLCodeAnalyzer(BaseCodeAnalyzer):
    def get_language(self) -> str:
        return 'html'

    def analyze_file(self, file_path: str, content: str) -> Tuple[List[LanguageClass], List[CodeIssue]]:
        return [], []

    def extract_variables(self, content: str, file_path: str) -> List[VariableInfo]:
        variables = []

        id_pattern = r'id=["\']([^"\']+)["\']'
        class_pattern = r'class=["\']([^"\']+)["\']'

        for pattern, var_type in [(id_pattern, 'html-id'), (class_pattern, 'html-class')]:
            matches = re.finditer(pattern, content)
            for match in matches:
                var_name = match.group(1)
                variables.append(VariableInfo(
                    name=var_name,
                    type=var_type,
                    scope='global',
                    line_declared=content[:match.start()].count('\n') + 1,
                    is_used=True,
                    usage_count=1,
                    file_path=file_path
                ))

        return variables

    def validate_coding_standards(self, content: str, file_path: str) -> StyleValidation:
        violations = []

        violations.extend(self._check_html_structure(content, file_path))
        violations.extend(self._check_html_accessibility(content, file_path))

        style_score = max(0, 10 - len(violations) * 0.5)

        return StyleValidation(
            is_valid=len(violations) == 0,
            violations=violations,
            style_score=style_score,
            file_path=file_path,
            language='html'
        )

    def _check_html_structure(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if '<img' in line and 'alt=' not in line:
                violations.append(CodingStandardViolation(
                    rule='IMG_ALT_REQUIRED',
                    severity='HIGH',
                    message='img tag missing alt attribute',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Add alt attribute for accessibility'
                ))

        return violations

    def _check_html_accessibility(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if '<input' in line and 'type=' in line and 'label' not in content.lower():
                violations.append(CodingStandardViolation(
                    rule='INPUT_LABEL_REQUIRED',
                    severity='MEDIUM',
                    message='Input should have associated label',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Associate input with label element'
                ))

        return violations


class CSSCodeAnalyzer(BaseCodeAnalyzer):
    def get_language(self) -> str:
        return 'css'

    def analyze_file(self, file_path: str, content: str) -> Tuple[List[LanguageClass], List[CodeIssue]]:
        return [], []

    def extract_variables(self, content: str, file_path: str) -> List[VariableInfo]:
        variables = []

        css_var_pattern = r'--([A-Za-z-_][A-Za-z0-9-_]*)\s*:\s*([^;]+);'
        matches = re.finditer(css_var_pattern, content)

        for match in matches:
            var_name = match.group(1)
            variables.append(VariableInfo(
                name=f'--{var_name}',
                type='css-variable',
                scope='global',
                line_declared=content[:match.start()].count('\n') + 1,
                is_used=content.count(f'var(--{var_name})') > 0,
                usage_count=content.count(f'var(--{var_name})'),
                file_path=file_path
            ))

        return variables

    def validate_coding_standards(self, content: str, file_path: str) -> StyleValidation:
        violations = []

        violations.extend(self._check_css_formatting(content, file_path))
        violations.extend(self._check_css_best_practices(content, file_path))

        style_score = max(0, 10 - len(violations) * 0.5)

        return StyleValidation(
            is_valid=len(violations) == 0,
            violations=violations,
            style_score=style_score,
            file_path=file_path,
            language='css'
        )

    def _check_css_formatting(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if '{' in line and not line.strip().endswith('{'):
                violations.append(CodingStandardViolation(
                    rule='CSS_BRACE_PLACEMENT',
                    severity='LOW',
                    message='Opening brace should be at end of line',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Move opening brace to end of selector line'
                ))

        return violations

    def _check_css_best_practices(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if '!important' in line:
                violations.append(CodingStandardViolation(
                    rule='AVOID_IMPORTANT',
                    severity='MEDIUM',
                    message='Avoid using !important',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Use more specific selectors instead'
                ))

        return violations


class SCSSCodeAnalyzer(BaseCodeAnalyzer):
    def get_language(self) -> str:
        return 'scss'

    def analyze_file(self, file_path: str, content: str) -> Tuple[List[LanguageClass], List[CodeIssue]]:
        return [], []

    def extract_variables(self, content: str, file_path: str) -> List[VariableInfo]:
        variables = []

        scss_var_pattern = r'\$([A-Za-z-_][A-Za-z0-9-_]*)\s*:\s*([^;]+);'
        matches = re.finditer(scss_var_pattern, content)

        for match in matches:
            var_name = match.group(1)
            variables.append(VariableInfo(
                name=f'${var_name}',
                type='scss-variable',
                scope='global',
                line_declared=content[:match.start()].count('\n') + 1,
                is_used=content.count(f'${var_name}') > 1,
                usage_count=content.count(f'${var_name}') - 1,
                file_path=file_path
            ))

        return variables

    def validate_coding_standards(self, content: str, file_path: str) -> StyleValidation:
        violations = []

        violations.extend(self._check_scss_formatting(content, file_path))
        violations.extend(self._check_scss_best_practices(content, file_path))

        style_score = max(0, 10 - len(violations) * 0.5)

        return StyleValidation(
            is_valid=len(violations) == 0,
            violations=violations,
            style_score=style_score,
            file_path=file_path,
            language='scss'
        )

    def _check_scss_formatting(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if line.strip().startswith('$') and ':' in line and not line.strip().endswith(';'):
                violations.append(CodingStandardViolation(
                    rule='SCSS_SEMICOLON',
                    severity='LOW',
                    message='SCSS variable declaration should end with semicolon',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Add semicolon at end of variable declaration'
                ))

        return violations

    def _check_scss_best_practices(self, content: str, file_path: str) -> List[CodingStandardViolation]:
        violations = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if '@import' in line and not (line.strip().endswith("';") or line.strip().endswith('"')):
                violations.append(CodingStandardViolation(
                    rule='SCSS_IMPORT_QUOTES',
                    severity='LOW',
                    message='SCSS import should use quotes',
                    file_path=file_path,
                    line_number=i,
                    suggestion='Use quotes around import path'
                ))

        return violations


class LanguageValidator:
    @staticmethod
    def validate_language_support(language_summary: Dict[str, int], unsupported_languages: List[str],
                                  unknown_extensions: List[str]) -> Dict[str, Any]:
        validation_result = {
            'is_valid': True,
            'primary_language': None,
            'supported_files': 0,
            'unsupported_files': 0,
            'image_files': 0,
            'unknown_files': 0,
            'errors': [],
            'warnings': [],
            'language_distribution': language_summary,
            'unsupported_languages': unsupported_languages,
            'unknown_extensions': unknown_extensions
        }

        supported_files = sum(count for lang, count in language_summary.items()
                              if LanguageDetector.is_supported(lang))
        unsupported_files = sum(count for lang, count in language_summary.items()
                                if not LanguageDetector.is_supported(lang) and
                                not LanguageDetector.is_image_file(lang) and lang != 'unknown')
        image_files = language_summary.get('image', 0)
        unknown_files = language_summary.get('unknown', 0)

        validation_result['supported_files'] = supported_files
        validation_result['unsupported_files'] = unsupported_files
        validation_result['image_files'] = image_files
        validation_result['unknown_files'] = unknown_files

        if supported_files == 0:
            validation_result['is_valid'] = False
            validation_result['errors'].append(
                f"No supported language files found. Supported languages: {', '.join(LanguageDetector.get_supported_languages())}"
            )
            if unsupported_languages:
                validation_result['errors'].append(
                    f"Found unsupported languages: {', '.join(unsupported_languages)}. These will be added soon."
                )
        else:
            supported_languages = {lang: count for lang, count in language_summary.items()
                                   if LanguageDetector.is_supported(lang)}
            validation_result['primary_language'] = max(supported_languages.items(), key=lambda x: x[1])[0]

            if unsupported_files > 0:
                validation_result['warnings'].append(
                    f"Found {unsupported_files} files in unsupported languages: {', '.join(unsupported_languages)}. Analysis will focus on supported languages only."
                )

            if image_files > 0:
                validation_result['warnings'].append(
                    f"Found {image_files} image files. These will be tracked but not analyzed."
                )

            if unknown_files > 0:
                validation_result['warnings'].append(
                    f"Found {unknown_files} files with unknown extensions: {', '.join(unknown_extensions)}."
                )

        return validation_result


class UsageAnalyzer:
    def __init__(self, classes: List[LanguageClass]):
        self.classes = classes
        self.class_usage = defaultdict(int)
        self.method_usage = defaultdict(int)
        self.analyze_usage()

    def analyze_usage(self):
        class_names = {cls.name for cls in self.classes}
        all_methods = {}

        for cls in self.classes:
            for method in cls.methods:
                method_key = f"{cls.name}.{method.name}"
                all_methods[method_key] = method

        for cls in self.classes:
            for import_stmt in cls.imports:
                for class_name in class_names:
                    if class_name in import_stmt:
                        self.class_usage[class_name] += 1

            for method in cls.methods:
                for called_method in method.calls_methods:
                    for method_key in all_methods:
                        if called_method in method_key:
                            self.method_usage[method_key] += 1

            if cls.extends:
                if cls.extends in class_names:
                    self.class_usage[cls.extends] += 1

            for interface in cls.implements:
                if interface in class_names:
                    self.class_usage[interface] += 1

        for cls in self.classes:
            cls.usage_count = self.class_usage.get(cls.name, 0)
            cls.is_used = cls.usage_count > 0

            for method in cls.methods:
                method_key = f"{cls.name}.{method.name}"
                method.usage_count = self.method_usage.get(method_key, 0)
                method.is_used = method.usage_count > 0 or method.name in ['main', '__init__', '__new__']

    def get_unused_classes(self) -> List[LanguageClass]:
        return [cls for cls in self.classes if not cls.is_used and not cls.name.endswith('Test')]

    def get_unused_methods(self) -> List[Tuple[LanguageClass, LanguageMethod]]:
        unused = []
        for cls in self.classes:
            for method in cls.methods:
                if not method.is_used and not self._is_special_method(method):
                    unused.append((cls, method))
        return unused

    def _is_special_method(self, method: LanguageMethod) -> bool:
        special_methods = {
            'main', 'toString', 'equals', 'hashCode', 'clone', 'finalize',
            '__init__', '__new__', '__str__', '__repr__', '__eq__', '__hash__'
        }
        return (method.name in special_methods or
                method.name.startswith('test') or
                'public' in method.modifiers and method.name.startswith('get') or
                'public' in method.modifiers and method.name.startswith('set'))


class LLMAnalysisEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ollama_llm = None
        self.embeddings = None
        self.vector_store = None
        self.chains = {}
        self._initialize_llm_components()

    def _initialize_llm_components(self):
        try:
            self.ollama_llm = OllamaLLM(
                model=self.config['OLLAMA_MODEL_CODE'],
                base_url=self.config['OLLAMA_BASE_URL'],
                temperature=0.1
            )

            self.embeddings = OllamaEmbeddings(
                model=self.config['OLLAMA_MODEL_EMBED'],
                base_url=self.config['OLLAMA_BASE_URL']
            )

            self.vector_store = Chroma(
                collection_name="codebase",
                embedding_function=self.embeddings,
                persist_directory=str(self.config['VECTOR_STORE_PATH'])
            )
            self._create_analysis_chains()

            logger.info("LLM components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LLM components: {e}")
            raise

    def _create_analysis_chains(self):
        architecture_template = PromptTemplate(
            input_variables=["class_info", "dependencies", "language"],
            template="""
            You are a senior software architect. Analyze the following {language} classes and their dependencies:

            Classes: {class_info}
            Dependencies: {dependencies}

            Provide analysis in JSON format:
            {{
                "architectural_pattern": "pattern name",
                "design_patterns": ["pattern1", "pattern2"],
                "layer_separation": "Good/Fair/Poor",
                "coupling_analysis": "description",
                "cohesion_analysis": "description", 
                "suggestions": ["suggestion1", "suggestion2"],
                "language_specific_recommendations": ["rec1", "rec2"]
            }}
            """
        )

        self.chains['architecture'] = LLMChain(
            llm=self.ollama_llm,
            prompt=architecture_template
        )

    def analyze_architecture(self, classes: List[LanguageClass]) -> Dict[str, Any]:
        try:
            languages = list(set(cls.language for cls in classes))
            primary_language = languages[0] if languages else "unknown"

            class_info = []
            for cls in classes[:10]:
                class_info.append({
                    "name": cls.name,
                    "package": cls.package,
                    "methods": len(cls.methods),
                    "extends": cls.extends,
                    "implements": cls.implements,
                    "complexity": cls.complexity_score,
                    "language": cls.language,
                    "is_used": cls.is_used,
                    "usage_count": cls.usage_count
                })

            dependencies = self._extract_dependencies(classes)
            result = self.chains['architecture'].run(
                class_info=json.dumps(class_info, indent=2),
                dependencies=json.dumps(dependencies, indent=2),
                language=primary_language
            )

            return json.loads(result)

        except Exception as e:
            logger.error(f"Architecture analysis failed: {e}")
            return {"error": str(e)}

    def _extract_dependencies(self, classes: List[LanguageClass]) -> Dict[str, Any]:
        dependencies = {
            "internal_dependencies": {},
            "external_dependencies": set(),
            "package_coupling": defaultdict(set)
        }

        for cls in classes:
            for imp in cls.imports:
                if not imp.startswith('java.lang') and not imp.startswith('import sys'):
                    dependencies["external_dependencies"].add(imp)

            dependencies["package_coupling"][cls.package].add(cls.name)

        dependencies["external_dependencies"] = list(dependencies["external_dependencies"])
        dependencies["package_coupling"] = dict(dependencies["package_coupling"])

        return dependencies


class SonarQubeStyleAnalyzer:
    def __init__(self, codebase_path: str, config: Dict[str, Any]):
        self.codebase_path = Path(codebase_path)
        self.config = config
        self.analyzers = {
            'java': JavaCodeAnalyzer(),
            'python': PythonCodeAnalyzer(),
            'javascript': JavaScriptCodeAnalyzer(),
            'html': HTMLCodeAnalyzer(),
            'css': CSSCodeAnalyzer(),
            'scss': SCSSCodeAnalyzer()
        }
        self.llm_engine = LLMAnalysisEngine(config)
        self.metrics = AnalysisMetrics(
            start_time=0, end_time=0, files_processed=0,
            methods_analyzed=0, classes_analyzed=0, issues_found=0,
            token_usage={}, api_calls=0, languages_detected={}
        )

    def extract_files(self) -> Tuple[List[FolderInfo], Dict[str, int], List[str], List[str]]:
        file_extractor = FileExtractor(self.codebase_path)
        folders, language_summary, unsupported_languages, unknown_extensions = file_extractor.extract_files()
        return folders, language_summary, unsupported_languages, unknown_extensions

    def _collect_supported_files(self, folders: List[FolderInfo], primary_language: str) -> List[Tuple[Path, str]]:
        supported_files = []
        for folder in folders:
            for file in folder.files:
                if LanguageDetector.is_supported(file.language):
                    supported_files.append((Path(file.path), file.language))
        return supported_files

    def analyze(self) -> Dict[str, Any]:
        logger.info(f"Starting SonarQube-style analysis of codebase: {self.codebase_path}")
        self.metrics.start_time = time.time()

        try:
            file_extractor = FileExtractor(self.codebase_path)
            folders, language_summary, unsupported_languages, unknown_extensions = file_extractor.extract_files()

            print("*" * 100)
            print("STEP 1: FILE EXTRACTION COMPLETED")
            print("*" * 100)
            self._print_extraction_summary(folders, language_summary)

            validation_result = LanguageValidator.validate_language_support(
                language_summary, unsupported_languages, unknown_extensions
            )

            print("\n" + "*" * 100)
            print("STEP 2: LANGUAGE VALIDATION")
            print("*" * 100)
            self._print_validation_result(validation_result)

            if not validation_result['is_valid']:
                raise ValueError("No supported languages found for analysis")

            print("\n" + "*" * 100)
            print("STEP 3: RUNNING SONARQUBE-STYLE ANALYSIS")
            print("*" * 100)

            # Modified to exclude image files from analysis
            source_files = []
            for folder in folders:
                for file in folder.files:
                    if LanguageDetector.is_supported(file.language):
                        source_files.append((Path(file.path), file.language))

            classes, static_issues = self._parallel_static_analysis(source_files)

            print(f"Analyzing variables and coding standards...")
            all_variables, style_validations = self._analyze_variables_and_standards(source_files)

            usage_analyzer = UsageAnalyzer(classes)
            unused_classes = usage_analyzer.get_unused_classes()
            unused_methods = usage_analyzer.get_unused_methods()
            unused_variables = self._find_unused_variables(all_variables)

            llm_analysis = self._llm_analysis(classes)
            dependency_analysis = self._analyze_dependencies(classes)

            final_report = self._generate_comprehensive_report(
                folders, language_summary, validation_result,
                classes, static_issues, llm_analysis, dependency_analysis,
                unused_classes, unused_methods, all_variables, unused_variables, style_validations
            )

            self.metrics.end_time = time.time()
            self.metrics.files_processed = sum(folder.total_files for folder in folders)
            self.metrics.classes_analyzed = len(classes)
            self.metrics.issues_found = len(static_issues)
            self.metrics.languages_detected = language_summary
            self.metrics.variables_analyzed = len(all_variables)
            self.metrics.style_violations = sum(len(sv.violations) for sv in style_validations)

            final_report['analysis_metrics'] = asdict(self.metrics)

            print("\n" + "*" * 100)
            print("ANALYSIS COMPLETED SUCCESSFULLY")
            print("*" * 100)

            return final_report

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

    def _print_extraction_summary(self, folders: List[FolderInfo], language_summary: Dict[str, int]):
        print(f"Total Folders Analyzed: {len(folders)}")
        print(f"Total Files Found: {sum(language_summary.values())}")
        print(f"Languages Detected: {len(language_summary)}")

        print("\nFOLDER BREAKDOWN:")
        for folder in folders[:10]:
            print(f"   {folder.name}: {folder.total_files} files, {folder.total_lines_of_code} LOC, "
                  f"{folder.total_classes} classes, {folder.total_methods} methods")

        print("\nLANGUAGE DISTRIBUTION:")
        for lang, count in sorted(language_summary.items(), key=lambda x: x[1], reverse=True):
            print(f"   {lang.capitalize()}: {count} files")

        print("\nTOP FILES BY LANGUAGE:")
        all_files = [file for folder in folders for file in folder.files]
        for lang in language_summary.keys():
            lang_files = [f for f in all_files if f.language == lang][:3]
            if lang_files:
                print(f"   {lang.capitalize()}:")
                for file in lang_files:
                    print(
                        f"     - {file.name}: {file.lines_of_code} LOC, {file.classes_count} classes, {file.methods_count} methods")

    def _print_validation_result(self, validation_result: Dict[str, Any]):
        if validation_result['is_valid']:
            print(f"VALIDATION PASSED")
            print(f"Primary Language: {validation_result['primary_language'].upper()}")
            print(f"Supported Files: {validation_result['supported_files']}")
            if validation_result['unsupported_files'] > 0:
                print(f"Unsupported Files: {validation_result['unsupported_files']}")
        else:
            print(f"VALIDATION FAILED")
            for error in validation_result['errors']:
                print(f"   ERROR: {error}")

        if validation_result['warnings']:
            print(f"\nWARNINGS:")
            for warning in validation_result['warnings']:
                print(f"   WARNING: {warning}")

        if validation_result['unsupported_languages']:
            print(f"\nLANGUAGES TO BE ADDED SOON:")
            for lang in validation_result['unsupported_languages']:
                print(f"   - {lang.capitalize()}")

    def _collect_supported_files(self, folders: List[FolderInfo], primary_language: str) -> List[Tuple[Path, str]]:
        supported_files = []
        for folder in folders:
            for file in folder.files:
                if LanguageDetector.is_supported(file.language):
                    supported_files.append((Path(file.path), file.language))
        return supported_files

    def _analyze_variables_and_standards(self, source_files: List[Tuple[Path, str]]) -> Tuple[
        List[VariableInfo], List[StyleValidation]]:
        all_variables = []
        style_validations = []

        def analyze_file_standards(file_info: Tuple[Path, str]) -> Tuple[List[VariableInfo], StyleValidation]:
            file_path, language = file_info
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                analyzer = self.analyzers.get(language)
                if analyzer:
                    variables = analyzer.extract_variables(content, str(file_path))
                    style_validation = analyzer.validate_coding_standards(content, str(file_path))
                    return variables, style_validation

                return [], StyleValidation(True, [], 10.0, str(file_path), language)

            except Exception as e:
                logger.warning(f"Failed to analyze standards for {file_path}: {e}")
                return [], StyleValidation(False, [], 0.0, str(file_path), language)

        with ThreadPoolExecutor(max_workers=self.config['MAX_WORKERS']) as executor:
            future_to_file = {executor.submit(analyze_file_standards, file_info): file_info
                              for file_info in source_files}

            for future in as_completed(future_to_file):
                try:
                    variables, style_validation = future.result()
                    all_variables.extend(variables)
                    style_validations.append(style_validation)
                except Exception as e:
                    logger.error(f"Error in standards analysis: {e}")

        return all_variables, style_validations

    def _find_unused_variables(self, variables: List[VariableInfo]) -> List[VariableInfo]:
        return [var for var in variables if not var.is_used and var.scope != 'parameter']

    def _parallel_static_analysis(self, source_files: List[Tuple[Path, str]]) -> Tuple[
        List[LanguageClass], List[CodeIssue]]:
        all_classes = []
        all_issues = []

        def analyze_file(file_info: Tuple[Path, str]) -> Tuple[List[LanguageClass], List[CodeIssue]]:
            file_path, language = file_info
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                analyzer = self.analyzers.get(language)
                if not analyzer:
                    return [], []

                classes, issues = analyzer.analyze_file(str(file_path), content)

                for issue in issues:
                    issue.file_path = str(file_path)

                return classes, issues

            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
                return [], [CodeIssue(
                    severity="HIGH",
                    category="RELIABILITY",
                    rule="FILE_READ_ERROR",
                    message=f"Failed to read file: {e}",
                    file_path=str(file_path),
                    line_number=1
                )]

        with ThreadPoolExecutor(max_workers=self.config['MAX_WORKERS']) as executor:
            future_to_file = {executor.submit(analyze_file, file_info): file_info
                              for file_info in source_files}

            for future in as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    classes, issues = future.result()
                    all_classes.extend(classes)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error processing {file_info[0]}: {e}")

        return all_classes, all_issues

    def _llm_analysis(self, classes: List[LanguageClass]) -> Dict[str, Any]:
        llm_results = {
            'architecture_analysis': {},
            'improvement_suggestions': []
        }

        try:
            if classes:
                llm_results['architecture_analysis'] = self.llm_engine.analyze_architecture(classes)

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            llm_results['error'] = str(e)

        return llm_results

    def _analyze_dependencies(self, classes: List[LanguageClass]) -> Dict[str, Any]:
        try:
            G = nx.DiGraph()

            for cls in classes:
                G.add_node(cls.name,
                           package=cls.package,
                           methods_count=len(cls.methods),
                           complexity=cls.complexity_score,
                           language=cls.language,
                           is_used=cls.is_used)

            for cls in classes:
                for imp in cls.imports:
                    imported_class = imp.split('.')[-1] if '.' in imp else imp.replace('import ', '').strip()
                    if any(c.name == imported_class for c in classes):
                        G.add_edge(cls.name, imported_class)

            analysis = {
                'total_classes': G.number_of_nodes(),
                'total_dependencies': G.number_of_edges(),
                'strongly_connected_components': len(list(nx.strongly_connected_components(G))),
                'is_dag': nx.is_directed_acyclic_graph(G),
                'density': nx.density(G),
                'average_clustering': nx.average_clustering(G.to_undirected()),
            }

            try:
                cycles = list(nx.simple_cycles(G))
                analysis['circular_dependencies'] = len(cycles)
                analysis['cycle_details'] = cycles[:5]
            except:
                analysis['circular_dependencies'] = 0
                analysis['cycle_details'] = []

            return analysis

        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")
            return {'error': str(e)}

    def _generate_comprehensive_report(self, folders: List[FolderInfo], language_summary: Dict[str, int],
                                       validation_result: Dict[str, Any], classes: List[LanguageClass],
                                       issues: List[CodeIssue], llm_analysis: Dict[str, Any],
                                       dependency_analysis: Dict[str, Any], unused_classes: List[LanguageClass],
                                       unused_methods: List[Tuple[LanguageClass, LanguageMethod]],
                                       all_variables: List[VariableInfo], unused_variables: List[VariableInfo],
                                       style_validations: List[StyleValidation]) -> Dict[str, Any]:

        total_methods = sum(len(cls.methods) for cls in classes)
        total_loc = sum(cls.lines_of_code for cls in classes)
        avg_complexity = sum(cls.complexity_score for cls in classes) / len(classes) if classes else 0

        issues_by_severity = Counter(issue.severity for issue in issues)
        issues_by_category = Counter(issue.category for issue in issues)
        languages_summary = Counter(cls.language for cls in classes)

        critical_issues = [issue for issue in issues if issue.severity == "CRITICAL"]
        high_issues = [issue for issue in issues if issue.severity == "HIGH"]

        suggestions = self._generate_suggestions(classes, issues, llm_analysis, unused_classes, unused_methods)

        coding_standards_summary = self._generate_coding_standards_summary(style_validations)

        report = {
            'metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'codebase_path': str(self.codebase_path),
                'analyzer_version': '3.0.0',
                'analysis_type': 'SonarQube-Style Multi-Language Analysis'
            },
            'extraction_summary': {
                'total_folders': len(folders),
                'folder_details': [asdict(folder) for folder in folders],
                'language_distribution': language_summary,
                'total_files_discovered': sum(language_summary.values()),
                'total_lines_discovered': sum(folder.total_lines_of_code for folder in folders),
                'total_classes_discovered': sum(folder.total_classes for folder in folders),
                'total_methods_discovered': sum(folder.total_methods for folder in folders)
            },
            'language_validation': validation_result,
            'project_overview': {
                'name': self.codebase_path.name,
                'primary_language': validation_result.get('primary_language', 'mixed'),
                'supported_languages': dict(languages_summary),
                'estimated_complexity': 'High' if avg_complexity > 7 else 'Medium' if avg_complexity > 4 else 'Low',
                'maintainability_index': max(0, 100 - avg_complexity * 10),
                'technical_debt_ratio': len([i for i in issues if i.severity in ['CRITICAL',
                                                                                 'HIGH']]) / total_methods if total_methods > 0 else 0
            },
            'sonarqube_style_analysis': {
                'total_files_analyzed': validation_result['supported_files'],
                'total_classes_analyzed': len(classes),
                'total_methods_analyzed': total_methods,
                'total_lines_analyzed': total_loc,
                'overall_quality_score': self._calculate_quality_score(classes, issues),
                'average_complexity': round(avg_complexity, 2),
                'total_issues': len(issues),
                'issues_by_severity': dict(issues_by_severity),
                'issues_by_category': dict(issues_by_category),
                'critical_issues': [asdict(issue) for issue in critical_issues[:10]],
                'high_priority_issues': [asdict(issue) for issue in high_issues[:10]]
            },
            'usage_analysis': {
                'unused_classes': {
                    'count': len(unused_classes),
                    'details': [{'name': cls.name, 'file_path': cls.file_path, 'language': cls.language,
                                 'lines_of_code': cls.lines_of_code} for cls in unused_classes]
                },
                'unused_methods': {
                    'count': len(unused_methods),
                    'details': [{'class_name': cls.name, 'method_name': method.name, 'file_path': cls.file_path,
                                 'language': cls.language, 'complexity': method.complexity} for cls, method in
                                unused_methods]
                },
                'unused_variables': {
                    'count': len(unused_variables),
                    'details': [asdict(var) for var in unused_variables]
                },
                'code_waste_metrics': {
                    'unused_loc': sum(cls.lines_of_code for cls in unused_classes) + sum(
                        method.lines_of_code for _, method in unused_methods),
                    'potential_cleanup_percentage': round(
                        (len(unused_classes) + len(unused_methods) + len(unused_variables)) / (
                                len(classes) + total_methods + len(all_variables)) * 100, 2) if (
                                                                                                        len(classes) + total_methods + len(
                                                                                                    all_variables)) > 0 else 0
                }
            },
            'variable_analysis': {
                'total_variables': len(all_variables),
                'variables_by_type': dict(Counter(var.type for var in all_variables)),
                'variables_by_scope': dict(Counter(var.scope for var in all_variables)),
                'unused_variables_by_language': dict(Counter(var.file_path.split('.')[-1] for var in unused_variables))
            },
            'coding_standards_report': coding_standards_summary,
            'complexity_analysis': {
                'by_language': {lang: {'avg_complexity': round(
                    sum(cls.complexity_score for cls in classes if cls.language == lang) / len(
                        [cls for cls in classes if cls.language == lang]), 2) if [cls for cls in classes if
                                                                                  cls.language == lang] else 0,
                                       'class_count': len([cls for cls in classes if cls.language == lang])}
                                for lang in set(cls.language for cls in classes)},
                'most_complex_classes': [
                    {'name': cls.name, 'language': cls.language, 'complexity': cls.complexity_score} for cls in
                    sorted(classes, key=lambda x: x.complexity_score, reverse=True)[:10]],
                'most_complex_methods': [
                    {'class': method.class_name, 'method': method.name, 'complexity': method.complexity} for method in
                    sorted([method for cls in classes for method in cls.methods], key=lambda x: x.complexity,
                           reverse=True)[:20]]
            },
            'architecture_analysis': llm_analysis.get('architecture_analysis', {}),
            'dependency_analysis': dependency_analysis,
            'improvement_suggestions': suggestions,
            'detailed_classes': [asdict(cls) for cls in classes[:20]]
        }

        return report

    def _generate_coding_standards_summary(self, style_validations: List[StyleValidation]) -> Dict[str, Any]:
        all_violations = []
        for sv in style_validations:
            all_violations.extend(sv.violations)

        violations_by_severity = Counter(v.severity for v in all_violations)
        violations_by_rule = Counter(v.rule for v in all_violations)
        violations_by_language = Counter(sv.language for sv in style_validations if sv.violations)

        avg_style_score = sum(sv.style_score for sv in style_validations) / len(
            style_validations) if style_validations else 0

        return {
            'total_violations': len(all_violations),
            'violations_by_severity': dict(violations_by_severity),
            'violations_by_rule': dict(violations_by_rule),
            'violations_by_language': dict(violations_by_language),
            'average_style_score': round(avg_style_score, 2),
            'files_analyzed': len(style_validations),
            'clean_files': len([sv for sv in style_validations if sv.is_valid]),
            'detailed_violations': [asdict(v) for v in all_violations[:50]]
        }

    def _generate_suggestions(self, classes: List[LanguageClass], issues: List[CodeIssue],
                              llm_analysis: Dict[str, Any], unused_classes: List[LanguageClass],
                              unused_methods: List[Tuple[LanguageClass, LanguageMethod]]) -> List[Dict[str, Any]]:
        suggestions = []

        if unused_classes:
            suggestions.append({
                'category': 'Code Cleanup',
                'priority': 'MEDIUM',
                'description': f'Found {len(unused_classes)} unused classes that can be removed',
                'action': 'Remove unused classes to reduce codebase size and complexity',
                'affected_items': [f"{cls.name} ({cls.language})" for cls in unused_classes[:10]],
                'potential_loc_reduction': sum(cls.lines_of_code for cls in unused_classes)
            })

        if unused_methods:
            suggestions.append({
                'category': 'Code Cleanup',
                'priority': 'LOW',
                'description': f'Found {len(unused_methods)} unused methods that can be removed',
                'action': 'Remove unused methods to improve code maintainability',
                'affected_items': [f"{cls.name}.{method.name} ({cls.language})" for cls, method in unused_methods[:10]],
                'potential_loc_reduction': sum(method.lines_of_code for _, method in unused_methods)
            })

        complex_methods = []
        for cls in classes:
            for method in cls.methods:
                if method.complexity > 8:
                    complex_methods.append((method, cls))

        if complex_methods:
            suggestions.append({
                'category': 'Code Complexity',
                'priority': 'HIGH',
                'description': f'Found {len(complex_methods)} methods with high complexity',
                'action': 'Refactor complex methods by extracting smaller functions',
                'affected_methods': [f"{cls.name}.{method.name} (complexity: {method.complexity}, {cls.language})" for
                                     method, cls in complex_methods[:10]]
            })

        unsupported_issues = [issue for issue in issues if issue.category == 'UNSUPPORTED']
        if unsupported_issues:
            languages_to_implement = set()
            for issue in unsupported_issues:
                if 'Language' in issue.message:
                    lang_match = re.search(r'Language (\w+)', issue.message)
                    if lang_match:
                        languages_to_implement.add(lang_match.group(1))

            if languages_to_implement:
                suggestions.append({
                    'category': 'Feature Extension',
                    'priority': 'LOW',
                    'description': f'TODO: Implement analyzers for {len(languages_to_implement)} additional languages',
                    'action': 'Create analyzer classes following the BaseCodeAnalyzer pattern',
                    'languages_to_implement': list(languages_to_implement),
                    'implementation_note': 'Follow the pattern used by JavaCodeAnalyzer and PythonCodeAnalyzer'
                })

        return suggestions

    def _calculate_quality_score(self, classes: List[LanguageClass], issues: List[CodeIssue]) -> float:
        if not classes:
            return 5.0

        score = 8.0
        avg_complexity = sum(cls.complexity_score for cls in classes) / len(classes)
        score -= min(3.0, avg_complexity / 3)

        critical_issues = len([i for i in issues if i.severity == 'CRITICAL'])
        high_issues = len([i for i in issues if i.severity == 'HIGH'])
        medium_issues = len([i for i in issues if i.severity == 'MEDIUM'])

        total_methods = sum(len(cls.methods) for cls in classes)
        if total_methods > 0:
            issue_ratio = (critical_issues * 3 + high_issues * 2 + medium_issues) / total_methods
            score -= min(4.0, issue_ratio * 2)

        return max(0.0, min(10.0, score))


def generate_comprehensive_report(results: Dict[str, Any], output_file: str):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Comprehensive Multi-Language Codebase Analysis Report\n\n")
        f.write(f"**Generated:** {results['metadata']['analysis_timestamp']}\n")
        f.write(f"**Analyzer Version:** {results['metadata']['analyzer_version']}\n")
        f.write(f"**Analysis Type:** {results['metadata']['analysis_type']}\n\n")

        f.write("## STEP 1: FILE EXTRACTION SUMMARY\n\n")
        extraction = results['extraction_summary']
        f.write(f"- **Total Folders:** {extraction['total_folders']}\n")
        f.write(f"- **Total Files Discovered:** {extraction['total_files_discovered']}\n")
        f.write(f"- **Total Lines of Code:** {extraction['total_lines_discovered']:,}\n")
        f.write(f"- **Total Classes:** {extraction['total_classes_discovered']}\n")
        f.write(f"- **Total Methods:** {extraction['total_methods_discovered']}\n\n")

        f.write("### Language Distribution\n\n")
        f.write("| Language | Files | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        total_files = extraction['total_files_discovered']
        for lang, count in extraction['language_distribution'].items():
            percentage = (count / total_files * 100) if total_files > 0 else 0
            f.write(f"| {lang.capitalize()} | {count} | {percentage:.1f}% |\n")

        f.write(f"\n## STEP 2: LANGUAGE VALIDATION\n\n")
        validation = results['language_validation']
        f.write(f"- **Validation Status:** {'PASSED' if validation['is_valid'] else 'FAILED'}\n")
        if validation['is_valid']:
            f.write(f"- **Primary Language:** {validation['primary_language'].upper()}\n")
            f.write(f"- **Supported Files:** {validation['supported_files']}\n")
            if validation['unsupported_files'] > 0:
                f.write(f"- **Unsupported Files:** {validation['unsupported_files']}\n")

        if validation['unsupported_languages']:
            f.write(f"\n### Languages To Be Added Soon\n")
            for lang in validation['unsupported_languages']:
                f.write(f"- {lang.capitalize()}\n")

        f.write(f"\n## STEP 3: SONARQUBE-STYLE ANALYSIS RESULTS\n\n")
        sonar = results['sonarqube_style_analysis']
        f.write(f"- **Files Analyzed:** {sonar['total_files_analyzed']}\n")
        f.write(f"- **Classes Analyzed:** {sonar['total_classes_analyzed']}\n")
        f.write(f"- **Methods Analyzed:** {sonar['total_methods_analyzed']}\n")
        f.write(f"- **Lines Analyzed:** {sonar['total_lines_analyzed']:,}\n")
        f.write(f"- **Overall Quality Score:** {sonar['overall_quality_score']:.1f}/10\n")
        f.write(f"- **Average Complexity:** {sonar['average_complexity']}\n\n")

        f.write("### Issues Summary\n\n")
        f.write("| Severity | Count |\n")
        f.write("|----------|-------|\n")
        for severity, count in sonar['issues_by_severity'].items():
            f.write(f"| {severity} | {count} |\n")

        f.write("\n## Usage Analysis\n\n")
        usage = results['usage_analysis']
        f.write(f"- **Unused Classes:** {usage['unused_classes']['count']}\n")
        f.write(f"- **Unused Methods:** {usage['unused_methods']['count']}\n")
        f.write(f"- **Unused Variables:** {usage['unused_variables']['count']}\n")
        f.write(f"- **Potential Cleanup:** {usage['code_waste_metrics']['potential_cleanup_percentage']}%\n")
        f.write(f"- **Unused Lines of Code:** {usage['code_waste_metrics']['unused_loc']:,}\n\n")

        if usage['unused_classes']['details']:
            f.write("### All Unused Classes\n\n")
            f.write("| Class Name | File Path | Language | Lines of Code |\n")
            f.write("|------------|-----------|----------|---------------|\n")
            for cls_info in usage['unused_classes']['details']:
                f.write(
                    f"| {cls_info['name']} | {cls_info['file_path']} | {cls_info['language']} | {cls_info['lines_of_code']} |\n")

        if usage['unused_methods']['details']:
            f.write("\n### All Unused Methods\n\n")
            f.write("| Class Name | Method Name | File Path | Language | Complexity |\n")
            f.write("|------------|-------------|-----------|----------|------------|\n")
            for method_info in usage['unused_methods']['details']:
                f.write(
                    f"| {method_info['class_name']} | {method_info['method_name']} | {method_info['file_path']} | {method_info['language']} | {method_info['complexity']} |\n")

        if usage['unused_variables']['details']:
            f.write("\n### All Unused Variables\n\n")
            f.write("| Variable Name | Type | Scope | File Path | Line Declared |\n")
            f.write("|---------------|------|-------|-----------|---------------|\n")
            for var_info in usage['unused_variables']['details']:
                f.write(
                    f"| {var_info['name']} | {var_info['type']} | {var_info['scope']} | {var_info['file_path']} | {var_info['line_declared']} |\n")

        f.write("\n## Coding Standards Report\n\n")
        standards = results['coding_standards_report']
        f.write(f"- **Total Violations:** {standards['total_violations']}\n")
        f.write(f"- **Average Style Score:** {standards['average_style_score']:.1f}/10\n")
        f.write(f"- **Files Analyzed:** {standards['files_analyzed']}\n")
        f.write(f"- **Clean Files:** {standards['clean_files']}\n\n")

        if standards['violations_by_severity']:
            f.write("### Violations by Severity\n\n")
            f.write("| Severity | Count |\n")
            f.write("|----------|-------|\n")
            for severity, count in standards['violations_by_severity'].items():
                f.write(f"| {severity} | {count} |\n")

        if standards['violations_by_rule']:
            f.write("\n### Most Common Violations\n\n")
            f.write("| Rule | Count |\n")
            f.write("|------|-------|\n")
            sorted_violations = sorted(standards['violations_by_rule'].items(), key=lambda x: x[1], reverse=True)
            for rule, count in sorted_violations[:10]:
                f.write(f"| {rule} | {count} |\n")

        if standards['detailed_violations']:
            f.write("\n### Detailed Violations\n\n")
            f.write("| File | Line | Rule | Severity | Message | Suggestion |\n")
            f.write("|------|------|------|----------|---------|------------|\n")
            for violation in standards['detailed_violations'][:20]:
                suggestion = violation.get('suggestion', 'N/A')
                f.write(
                    f"| {violation['file_path']} | {violation['line_number']} | {violation['rule']} | {violation['severity']} | {violation['message']} | {suggestion} |\n")

        f.write("\n## Variable Analysis\n\n")
        variables = results['variable_analysis']
        f.write(f"- **Total Variables:** {variables['total_variables']}\n")
        f.write(f"- **Unused Variables:** {usage['unused_variables']['count']}\n\n")

        if variables['variables_by_type']:
            f.write("### Variables by Type\n\n")
            f.write("| Type | Count |\n")
            f.write("|------|-------|\n")
            for var_type, count in variables['variables_by_type'].items():
                f.write(f"| {var_type} | {count} |\n")

        if variables['variables_by_scope']:
            f.write("\n### Variables by Scope\n\n")
            f.write("| Scope | Count |\n")
            f.write("|-------|-------|\n")
            for scope, count in variables['variables_by_scope'].items():
                f.write(f"| {scope} | {count} |\n")

        f.write("\n## Complexity Analysis\n\n")
        complexity = results['complexity_analysis']

        if complexity['by_language']:
            f.write("### Complexity by Language\n\n")
            f.write("| Language | Average Complexity | Class Count |\n")
            f.write("|----------|-------------------|-------------|\n")
            for lang, metrics in complexity['by_language'].items():
                f.write(f"| {lang.capitalize()} | {metrics['avg_complexity']} | {metrics['class_count']} |\n")

        if complexity['most_complex_classes']:
            f.write("\n### Most Complex Classes\n\n")
            f.write("| Class Name | Language | Complexity Score |\n")
            f.write("|------------|----------|------------------|\n")
            for cls_info in complexity['most_complex_classes']:
                f.write(f"| {cls_info['name']} | {cls_info['language']} | {cls_info['complexity']:.2f} |\n")

        if complexity['most_complex_methods']:
            f.write("\n### Most Complex Methods\n\n")
            f.write("| Class | Method | Complexity |\n")
            f.write("|-------|--------|-----------|\n")
            for method_info in complexity['most_complex_methods']:
                f.write(f"| {method_info['class']} | {method_info['method']} | {method_info['complexity']} |\n")

        f.write("\n## Improvement Suggestions\n\n")
        for suggestion in results['improvement_suggestions']:
            f.write(f"### {suggestion['category']} ({suggestion['priority']})\n")
            f.write(f"{suggestion['description']}\n\n")
            f.write(f"**Action:** {suggestion['action']}\n\n")

            if 'affected_items' in suggestion:
                f.write("**Affected Items:**\n")
                for item in suggestion['affected_items'][:10]:
                    f.write(f"- {item}\n")
                f.write("\n")

            if 'potential_loc_reduction' in suggestion:
                f.write(f"**Potential LOC Reduction:** {suggestion['potential_loc_reduction']:,} lines\n\n")

        f.write("## Analysis Metrics\n\n")
        metrics = results['analysis_metrics']
        f.write(f"- **Analysis Duration:** {metrics['end_time'] - metrics['start_time']:.2f} seconds\n")
        f.write(f"- **Files Processed:** {metrics['files_processed']}\n")
        f.write(f"- **Classes Analyzed:** {metrics['classes_analyzed']}\n")
        f.write(f"- **Methods Analyzed:** {metrics['methods_analyzed']}\n")
        f.write(f"- **Variables Analyzed:** {metrics['variables_analyzed']}\n")
        f.write(f"- **Issues Found:** {metrics['issues_found']}\n")
        f.write(f"- **Style Violations:** {metrics['style_violations']}\n")


def generate_requirements_txt():
    requirements = [
        "javalang>=0.13.0",
        "langchain>=0.3.0",
        "langchain-core>=0.3.0",
        "langchain-text-splitters>=0.3.0",
        "langchain-ollama>=0.2.0",
        "langchain-chroma>=0.1.0",
        "chromadb>=0.5.0",
        "networkx>=3.0",
        "numpy>=1.24.0",
        "requests>=2.32.0",
        "typing-extensions>=4.0.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0",
        "tenacity>=8.0.0"
    ]

    with open("requirements.txt", "w") as f:
        for req in requirements:
            f.write(f"{req}\n")

    print("requirements.txt generated successfully!")


if __name__ == "__main__":
    CODEBASE_PATH = "./sakila-master"
    OUTPUT_FILE = "comprehensive_codebase_analysis.json"
    OUTPUT_REPORT = "COMPREHENSIVE_ANALYSIS_REPORT.md"
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL_CODE = "codellama:13b-instruct"
    OLLAMA_MODEL_EMBED = "nomic-embed-text"
    OLLAMA_MODEL_ARCHITECTURE = "llama2:13b-chat"
    VECTOR_STORE_PATH = "./vector_store"
    MAX_WORKERS = min(8, os.cpu_count())
    CHUNK_SIZE = 2000
    CHUNK_OVERLAP = 200
    COMPLEXITY_THRESHOLD = 10
    METHOD_LENGTH_THRESHOLD = 50
    CLASS_LENGTH_THRESHOLD = 300

    config = {
        'CODEBASE_PATH': CODEBASE_PATH,
        'OUTPUT_FILE': OUTPUT_FILE,
        'OUTPUT_REPORT': OUTPUT_REPORT,
        'OLLAMA_BASE_URL': OLLAMA_BASE_URL,
        'OLLAMA_MODEL_CODE': OLLAMA_MODEL_CODE,
        'OLLAMA_MODEL_EMBED': OLLAMA_MODEL_EMBED,
        'OLLAMA_MODEL_ARCHITECTURE': OLLAMA_MODEL_ARCHITECTURE,
        'MAX_WORKERS': MAX_WORKERS,
        'VECTOR_STORE_PATH': VECTOR_STORE_PATH,
        'CHUNK_SIZE': CHUNK_SIZE,
        'CHUNK_OVERLAP': CHUNK_OVERLAP,
        'COMPLEXITY_THRESHOLD': COMPLEXITY_THRESHOLD,
        'METHOD_LENGTH_THRESHOLD': METHOD_LENGTH_THRESHOLD,
        'CLASS_LENGTH_THRESHOLD': CLASS_LENGTH_THRESHOLD
    }

    logger.info("Starting Comprehensive Multi-Language Codebase Analysis")
    logger.info(f"Configuration: {json.dumps(config, indent=2, default=str)}")

    try:
        # Step 1: Validate codebase path exists
        if not Path(CODEBASE_PATH).exists():
            raise FileNotFoundError(f"Codebase path does not exist: {CODEBASE_PATH}")

        # Step 2: Initialize the SonarQube-style analyzer
        analyzer = SonarQubeStyleAnalyzer(CODEBASE_PATH, config)

        # Step 3: Run the comprehensive analysis (includes all three main steps)
        results = analyzer.analyze()

        # Step 4: Save results to JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Analysis completed successfully!")
        logger.info(f"Results saved to: {OUTPUT_FILE}")

        # Step 5: Print comprehensive summary
        print("\n" + "*" * 100)
        print("COMPREHENSIVE ANALYSIS SUMMARY")
        print("*" * 100)

        extraction = results['extraction_summary']
        validation = results['language_validation']
        sonar = results['sonarqube_style_analysis']
        usage = results['usage_analysis']

        print(f"Total Folders: {extraction['total_folders']}")
        print(f"Files Discovered: {extraction['total_files_discovered']}")
        print(f"Primary Language: {validation.get('primary_language', 'Mixed').upper()}")
        print(f"Files Analyzed: {sonar['total_files_analyzed']}")
        print(f"Classes Analyzed: {sonar['total_classes_analyzed']}")
        print(f"Methods Analyzed: {sonar['total_methods_analyzed']}")
        print(f"Lines Analyzed: {sonar['total_lines_analyzed']:,}")
        print(f"Quality Score: {sonar['overall_quality_score']:.1f}/10")
        print(f"Total Issues: {sonar['total_issues']}")
        print(f"Unused Classes: {usage['unused_classes']['count']}")
        print(f"Unused Methods: {usage['unused_methods']['count']}")
        print(f"Cleanup Potential: {usage['code_waste_metrics']['potential_cleanup_percentage']}%")

        metrics = results['analysis_metrics']
        print(f"Analysis Duration: {metrics['end_time'] - metrics['start_time']:.2f} seconds")

        print("\nLANGUAGE BREAKDOWN:")
        for lang, count in extraction['language_distribution'].items():
            percentage = (count / extraction['total_files_discovered'] * 100) if extraction[
                                                                                     'total_files_discovered'] > 0 else 0
            status = "Analyzed" if lang in ['java', 'python'] else "Coming Soon"
            print(f"   {lang.capitalize()}: {count} files ({percentage:.1f}%) - {status}")

        if validation['unsupported_languages']:
            print(f"\nUPCOMING LANGUAGE SUPPORT:")
            for lang in validation['unsupported_languages']:
                print(f"   - {lang.capitalize()} analyzer will be added soon")

        print("*" * 100)

        # Step 6: Generate comprehensive markdown report
        generate_comprehensive_report(results, OUTPUT_REPORT)
        logger.info(f"Comprehensive report saved to: {OUTPUT_REPORT}")

        # Step 7: Generate requirements.txt file
        generate_requirements_txt()

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise

    # TODO: Language Extension Framework
    #
    # To add support for new languages, follow these steps:
    #
    # 1. Add language extension mapping in LanguageDetector.LANGUAGE_EXTENSIONS
    # 2. Add language to LanguageDetector.SUPPORTED_LANGUAGES set
    # 3. Create new analyzer class inheriting from BaseCodeAnalyzer:
    #
    #    class CppCodeAnalyzer(BaseCodeAnalyzer):
    #        def get_language(self) -> str:
    #            return 'cpp'
    #
    #        def analyze_file(self, file_path: str, content: str) -> Tuple[List[LanguageClass], List[CodeIssue]]:
    #            # TODO: Implement C++ AST parsing using tree-sitter or similar
    #            # TODO: Extract classes, methods, complexity metrics
    #            # TODO: Identify C++ specific code smells
    #            pass
    #
    # 4. Register analyzer in SonarQubeStyleAnalyzer.__init__:
    #    self.analyzers = {
    #        'java': JavaCodeAnalyzer(),
    #        'python': PythonCodeAnalyzer(),
    #        'cpp': CppCodeAnalyzer(),  # Add new analyzer
    #    }
    #
    # 5. Update LLM prompts to handle language-specific analysis
    #
    # Suggested libraries for different languages:
    # - JavaScript/TypeScript: Use 'esprima' or 'acorn' for AST parsing
    # - C/C++: Use 'tree-sitter' with C/C++ grammar
    # - C#: Use 'pythonnet' to interface with Roslyn
    # - Go: Use 'tree-sitter' with Go grammar
    # - Rust: Use 'tree-sitter' with Rust grammar
    # - Ruby: Use 'ripper' through subprocess calls
    # - PHP: Use 'php-ast' through subprocess calls
    # - Kotlin: Use 'tree-sitter' with Kotlin grammar
    # - Scala: Use 'tree-sitter' with Scala grammar
    #
    # Each new analyzer should implement:
    # - File parsing and AST generation
    # - Class and method extraction
    # - Complexity calculation
    # - Code smell detection
    # - Import/dependency analysis
    # - Language-specific best practices validation

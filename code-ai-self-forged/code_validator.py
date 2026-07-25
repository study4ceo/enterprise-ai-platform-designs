"""Code validation and safety checks."""

import ast
import re
from typing import Tuple, List
from logger import get_logger

logger = get_logger(__name__)


class CodeValidator:
    """Validates Python code for safety before execution."""

    # Dangerous patterns to block
    DANGEROUS_IMPORTS = {
        "os.system",
        "subprocess.call",
        "subprocess.run",
        "subprocess.Popen",
        "eval",
        "exec",
        "__import__",
        "compile",
    }

    DANGEROUS_BUILTINS = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",  # Restrict file access in MVP
    }

    def __init__(self, allow_file_access: bool = False):
        """Initialize validator.
        
        Args:
            allow_file_access: Whether to allow file operations
        """
        self.allow_file_access = allow_file_access

    def validate(self, code: str) -> Tuple[bool, List[str]]:
        """Validate code for safety.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check syntax
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
            return False, issues

        # Check for dangerous patterns
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if self._is_dangerous_import(alias.name):
                        issues.append(f"Dangerous import: {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                if node.module and self._is_dangerous_import(node.module):
                    issues.append(f"Dangerous import: {node.module}")
                for alias in node.names:
                    full_name = f"{node.module}.{alias.name}" if node.module else alias.name
                    if self._is_dangerous_import(full_name):
                        issues.append(f"Dangerous import: {full_name}")

            # Check function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_BUILTINS:
                        if node.func.id == "open" and not self.allow_file_access:
                            issues.append(f"File access not allowed: {node.func.id}")
                        elif node.func.id != "open":
                            issues.append(f"Dangerous builtin: {node.func.id}")

        if issues:
            logger.warning("Code validation failed", issues=issues)
            return False, issues

        logger.info("Code validation passed")
        return True, []

    def _is_dangerous_import(self, import_name: str) -> bool:
        """Check if import is dangerous."""
        for dangerous in self.DANGEROUS_IMPORTS:
            if dangerous in import_name or import_name in dangerous:
                return True
        return False

    def extract_code_from_markdown(self, text: str) -> str:
        """Extract code from markdown code blocks.
        
        Args:
            text: Text that may contain markdown code blocks
            
        Returns:
            Extracted code or original text
        """
        # Match ```python ... ``` or ``` ... ```
        pattern = r"```(?:python)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # Return the first code block
            return matches[0].strip()
        
        return text.strip()

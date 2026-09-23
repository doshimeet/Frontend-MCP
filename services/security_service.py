"""
Security & Path Sandboxing Service
Prevents directory traversal attacks and restricts filesystem write operations.
"""

import os
from pathlib import Path
from config import REPO_ROOT


class SecurityException(Exception):
    """Raised when a path traversal or prohibited filesystem operation is attempted."""
    pass


class SecurityService:
    """Validates and sandboxes filesystem paths against allowed workspace boundaries."""

    def __init__(self, allowed_root: Path = REPO_ROOT):
        self.allowed_root = allowed_root.resolve()

    def sanitize_and_validate_path(self, target_path_str: str) -> Path:
        """
        Resolves a user-provided or AI-provided path and verifies that:
        1. It does not escape outside the user's workspace or home directory.
        2. It does not target dangerous system directories (/System, /Windows, /etc, /usr).
        3. Returns a clean, absolute Path object.
        """
        if not target_path_str or target_path_str.strip() == "":
            raise SecurityException("Target path cannot be empty.")

        # Expand ~ and environment variables
        resolved = Path(target_path_str).expanduser()
        if not resolved.is_absolute():
            resolved = (self.allowed_root / resolved).resolve()
        else:
            resolved = resolved.resolve()

        # Check both resolved and raw path representations to catch symlinks like /etc -> /private/etc
        raw_expanded_str = str(Path(target_path_str).expanduser())
        path_variants = [str(resolved), raw_expanded_str]

        # Prohibited System Roots (Cross-Platform & macOS symlinks)
        prohibited_roots = [
            "/etc", "/private/etc", "/bin", "/sbin", "/usr", "/System", "/Library",
            "/private/var", "/var",
            "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
        ]
        for prob in prohibited_roots:
            for p_var in path_variants:
                if p_var == prob or p_var.startswith(prob + os.sep) or p_var.startswith(prob + "/"):
                    raise SecurityException(
                        f"Security Violation: Target path '{p_var}' targets a protected system directory."
                    )

        return resolved

import os
from typing import Union, Optional
from shlex import quote
from datetime import datetime

class AbsPathTool:

    def __init__(self):
        pass
    
    def _filepath_err_handling(self, file_path: str) -> str:
        """
        Validates an absolute file path string with comprehensive checks.
        Assumes input is already an absolute path - no path resolution performed.
        
        Args:
            file_path: Absolute path string to validate
            
        Returns:
            Sanitized absolute path if valid
            
        Raises:
            ValueError: If path is empty/whitespace or not a file
            PermissionError: If read access is denied
            RuntimeError: For unexpected filesystem errors
        """
        # --------------------------------------
        # Initial Validation
        # --------------------------------------
        self.logger.debug(f"Validating absolute file path: '{file_path}'")
        
        # Ensure that file_path is a string
        if not isinstance(file_path, str):
            error_msg = f"Path must be string, got {type(file_path).__name__}"
            self.logger.error(error_msg)
            raise TypeError(error_msg)
        
        # should not happen because of if condition before calling this function (here as a fail safe)
        clean_path = file_path.strip()
        if not clean_path:
            error_msg = "Empty file path provided"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # --------------------------------------
        # Core Validation (Single-Step)
        # --------------------------------------
        try:
            # Combined existence and file type check
            if not os.path.isfile(clean_path):
                error_msg = f"Path is not a regular file: '{clean_path}'"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Readability check
            if not os.access(clean_path, os.R_OK):
                error_msg = f"Read permission denied: '{clean_path}'"
                self.logger.error(error_msg)
                raise PermissionError(error_msg)
                
            # ----------------------------------
            # Success Path
            # ----------------------------------
            # Only sanitization needed (path is already absolute)
            sanitized = quote(clean_path)
            
            # Log file metadata
            stat = os.stat(clean_path)
            self.logger.info(f"Validated file: {sanitized}")
            self.logger.info(f"Size: {stat.st_size:,} bytes | Modified: {datetime.fromtimestamp(stat.st_mtime).isoformat()}")
            
            return sanitized
            
        except (ValueError, PermissionError):
            raise  # Re-raise expected exceptions
            
        except OSError as e:
            error_msg = f"Filesystem error: {e.strerror} (errno {e.errno})"
            self.logger.critical(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected validation error: {str(e)}"
            self.logger.critical(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def _sanitize_path(self, path: str) -> str:
        """Normalize path separators and resolve relative markers."""
        path = os.path.normpath(path)
        if os.sep != '/':  # Convert to forward slashes if not on Unix
            path = path.replace(os.sep, '/')
        return path
    
    def _validate_path_type(self, path: str, expected_type: str) -> bool:
        """Check if path matches expected filesystem type."""
        if expected_type == 'file':
            return os.path.isfile(path)
        elif expected_type == 'dir':
            return os.path.isdir(path)
        elif expected_type == 'link':
            return os.path.islink(path)
        return False
    
    def resolve_symlinks(self, path: str, strict: bool = False) -> Optional[str]:
        """Resolve all symlinks in a path."""
        try:
            return os.path.realpath(path)
        except OSError as e:
            if strict:
                raise
            self.logger.warning(f"Symlink resolution failed for {path}: {e}")
            return None
    
    def abs_path(
            self, 
            path: Union[str, os.PathLike, None] = '', 
            var_name: str = "path",
            strict: bool = False,
            check_exists: bool = False
        ) -> Optional[str]:
        """Convert a path to absolute path with configurable validation.
        
        Args:
            path: Path to convert (None, str, or Path-like)
            var_name: Name of the variable/path being checked (for error messages)
            strict: If True, raises exceptions on failure; if False, returns empty string
            check_exists: If True, verifies the path exists on filesystem
            
        Returns:
            Absolute path (str) if valid, empty string ("") if invalid and strict=False
            
        Raises (when strict=True):
            TypeError: If input is not string/Path-like
            ValueError: For empty/None input or non-existent paths
            OSError: For filesystem-related errors during path resolution
        
        Example:
            >> handler = PathHandler()
            >> # Basic conversion
            >> handler.abs_path("relative/path")  # returns absolute path
            '/current/working/dir/relative/path'
            
            >> # Strict mode (raises exceptions)
            >> handler.abs_path(None, strict=True)  # raises ValueError
            >> handler.abs_path(123, strict=True)  # raises TypeError
            
            >> # Check existence
            >> handler.abs_path("missing_file.txt", check_exists=True)  # returns "" if file doesn't exist
        
            >> # Non-strict mode (returns empty string on errors)
            >> handler.abs_path("")  # returns ""
        """
        # =============================================
        # Initial Logging - Track function entry
        # =============================================
        self.logger.debug(
            f"Starting path conversion for '{var_name}': "
            f"path={path}, " 
            f"strict={strict} (must be string/Path-like, must not be empty or None, check for filesystem-related errors), " 
            f"check_exists={check_exists} (check if path exists)"
        )

        # =============================================
        # Phase 1: Basic Input Validation
        # (Applies regardless of check_exists)
        # =============================================
        
        # Case: None input
        if path is None:
            error_msg = f"Path '{var_name}' cannot be None"
            if strict:
                self.logger.error(f"{error_msg} (strict mode)")
                raise ValueError(error_msg)
            self.logger.warning(f"{error_msg}. Returning empty string")
            return ""

        # Case: Invalid type (not string or PathLike)
        if not isinstance(path, (str, os.PathLike)):
            error_msg = (
                f"Path '{var_name}' must be string or PathLike, "
                f"got {type(path).__name__}"
            )
            if strict:
                self.logger.error(f"{error_msg} (strict mode)")
                raise TypeError(error_msg)
            self.logger.warning(f"{error_msg}. Returning empty string")
            return ""

        # Case: Empty/whitespace string
        if not str(path).strip():
            error_msg = f"Path '{var_name}' is empty/whitespace"
            if strict:
                self.logger.error(f"{error_msg} (strict mode)")
                raise ValueError(error_msg)
            self.logger.debug(f"{error_msg}. Returning empty string")
            return ""

        # =============================================
        # Phase 2: Path Conversion
        # =============================================
        try:
            # Convert to absolute path (does NOT check existence yet)
            abs_path = os.path.abspath(str(path))
            self.logger.debug(
                f"Converted '{var_name}' to absolute path: '{abs_path}'"
            )

            # =========================================
            # Phase 3: Existence Verification (Optional)
            # =========================================
            if check_exists:
                if not os.path.exists(abs_path):
                    error_msg = f"Path '{var_name}' does not exist: '{abs_path}'"
                    if strict:
                        self.logger.error(f"{error_msg} (strict mode)")
                        raise ValueError(error_msg)
                    self.logger.warning(f"{error_msg}. Returning empty string")
                    return ""

            # =========================================
            # Success Case
            # =========================================
            self.logger.info(f"Successfully converted '{var_name}' path into: '{abs_path}' ")
            return abs_path

        # =============================================
        # Error Handling for Filesystem Operations
        # =============================================
        except OSError as e:
            error_msg = (
                f"Filesystem error while processing '{var_name}': "
                f"{str(e)} (errno={e.errno})"
            )
            if strict:
                self.logger.critical(error_msg, exc_info=True)
                raise
            self.logger.error(f"{error_msg}. Returning empty string")
            return ""
            
        except Exception as e:
            error_msg = (
                f"Unexpected error processing '{var_name}': "
                f"{type(e).__name__}: {str(e)}"
            )
            if strict:
                self.logger.critical(error_msg, exc_info=True)
                raise
            self.logger.error(f"{error_msg}. Returning empty string")
            return ""

    def abs_path_list(
            self, 
            path_list: Union[list, tuple], 
            var_name: str = "path_list",
            strict: bool = False, 
            check_exists: bool = False
        ) -> list:
        """Process a sequence of paths into absolute paths with comprehensive validation.
        
        Processes each path in the input sequence through abs_path(), providing:
        - Path normalization
        - Existence checking (when enabled)
        - Detailed error handling
        
        Args:
            path_list: Sequence of paths (list or tuple) to process. Elements can be:
                    - Strings
                    - Path-like objects
                    - None values (will be filtered out)
            var_name: Descriptive name for the path list (used in error messages/logging)
            strict: Validation mode:
                    - True: Raises exceptions on first error
                    - False: Skips invalid paths, returns partial results
            check_exists: When True, verifies each path exists in filesystem
            
        Returns:
            List of successfully processed absolute paths. May be empty if:
            - Input was empty
            - All paths were invalid (in non-strict mode)
            - No paths passed existence checks
            
        Raises (only when strict=True):
            TypeError: If path_list is not a list/tuple
            ValueError: For empty path_list or invalid individual paths
            OSError: For filesystem errors during existence checks
            
        Example:
            >> processor.abs_path_list(
            ..     ["file.txt", None, <invalid_path>/path"],
            ..     var_name="input_files",
            ..     strict=False
            .. )
            ['/absolute/path/to/file.txt']  # Only valid paths returned
        """
        # ----------------------------------------------------------------------
        # Initial Validation and Logging
        # ----------------------------------------------------------------------
        self.logger.debug(
            f"Starting path list processing for '{var_name}': "
            f"strict={strict} (element must be string/Path-like, must not be empty or None, check for filesystem-related errors),"
            f"check_exists={check_exists} (check if file exists), "
            f"input_type={type(path_list).__name__}, "
            f"length={len(path_list) if hasattr(path_list, '__len__') else 'N/A'}"
        )

        # Validate container type
        if not isinstance(path_list, (list, tuple)):
            error_msg = f"'{var_name}' must be list or tuple, got {type(path_list).__name__}"
            if strict:
                self.logger.error(error_msg)
                raise TypeError(error_msg)
            self.logger.warning(f"{error_msg}. Returning empty list")
            return []

        # Handle empty input
        if not path_list:
            error_msg = f"'{var_name}' is empty"
            if strict:
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            self.logger.debug(f"{error_msg}. Returning empty list")
            return []

        # ----------------------------------------------------------------------
        # Path Processing Loop
        # ----------------------------------------------------------------------
        abs_paths = []
        invalid_paths = []

        for idx, path in enumerate(path_list):
            try:
                # Skip None values silently
                if path is None:
                    self.logger.debug(f"Skipping None value at {var_name}[{idx}]")
                    continue
                    
                # Process individual path
                item_name = f"{var_name}[{idx}]"
                result = self.abs_path(
                    path=path,
                    var_name=item_name,
                    strict=strict,
                    check_exists=check_exists
                )
                
                # Only collect successful conversions (abs_path returns None on failure)
                if result:
                    abs_paths.append(result)
                    self.logger.debug(f"Processed {item_name}: {path} -> {result}")

            except Exception as e:
                error_msg = f"Invalid path at {var_name}[{idx}]: {str(e)}"
                if strict:
                    self.logger.error(f"{error_msg} (strict mode)")
                    raise ValueError(error_msg) from e
                invalid_paths.append((idx, path, str(e)))
                self.logger.warning(error_msg)

        # ----------------------------------------------------------------------
        # Result Compilation and Reporting
        # ----------------------------------------------------------------------
        success_count = len(abs_paths)
        total_attempted = len(path_list) - path_list.count(None)  # Exclude None values
        conversion_rate = (success_count / total_attempted) if total_attempted > 0 else 0.0
        
        self.logger.info(
            f"Path list processing completed for '{var_name}': "
            f"{success_count}/{total_attempted} succeeded ({conversion_rate:.1%})"
        )
        
        if invalid_paths and not strict:
            self.logger.warning(
                f"Skipped {len(invalid_paths)} invalid paths in '{var_name}': "
                f"{', '.join(f'#{i} ({reason})' for i, _, reason in invalid_paths)}"
            )
        
        return abs_paths
import subprocess
import os
import errno
import sys
from subprocess import check_output,CalledProcessError,DEVNULL
from pathlib import Path
from typing import List, Optional, Set

def parse_tool_opts(tool_opts:list)-> dict: 
    """This functions parses the tool options file given to be used in commands vlog, qverify, cdc run... and returns a dict file"""
    opts_dict = {}
    if tool_opts:  # Checks if the list is not empty
        for tool_opt in tool_opts: # check for each file specified in opts.tool_opts (if multiple)
            with open(tool_opt, 'r') as f:  # open the file 
                for line in f: # read line by line
                    line = line.strip() # strip any leading/trailing whitespaces and newline character/carriage return
                    if not line or line.startswith('#'):  # Skip empty lines and comments
                        continue
                    elif '=>' not in line:  # Skip lines without '=>'
                        continue
                    key, value = line.split('=>', 1)  # Split on first '=>' 
                    key = key.strip()
                    value = value.strip()

                    if key == 'suppress':
                        err_id, explanation = value.split(' ', 1)
                        formatted_value = f"Error ID: {err_id.strip()} Explanation: {explanation.strip()}"
                        if key in opts_dict:
                            opts_dict[key].append(formatted_value)  # Append to existing list
                        else:
                            opts_dict[key] = [formatted_value]  # Initialize as a list
                    else:
                        if key in opts_dict:
                            opts_dict[key] += value  # Append to existing list
                        else:
                            opts_dict[key] = value  # Initialize as a list
    return opts_dict
                  
def get_git_root(self) -> Path:
    """Safely get Git root directory with error handling.
    
    Returns:
        Path: Absolute path to Git root directory if in a Git repo, else None.
    """
    try:
        self._git_root = Path(
            check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=DEVNULL,
                text=True
            ).strip()
        ).resolve()
        return self._git_root
    except (CalledProcessError, FileNotFoundError):
        return None  # Not in a Git repo or git not installed
    
def get_git_submodules(repo_path=".") -> list:
    """Returns a list of submodule paths in a Git repo."""
    try:
        # Get submodule paths
        result = subprocess.run(
            ["git", "submodule", "status", "--recursive"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        submodules = [
            line.strip().split()[1]  # Extract path (e.g., "dir/submodule")
            for line in result.stdout.splitlines()
        ]
        return submodules
    except subprocess.CalledProcessError:
        return []  # No submodules or not a Git repo
    
    
def find_tool_dir(self, tool_name: str) -> Path:
    """Find the most relevant tool directory in a Git repository.
    
    Args:
        tool_name: Name of the tool directory to find (e.g., 'lint')
        
    Returns:
        Path: The most relevant tool directory path
    """
    # Initialize tool directories list
    if not hasattr(self, '_tool_dirs'):
        self._tool_dirs = []
    else:
        self._tool_dirs.clear()
    
    # Get Git root or fallback
    self._git_root = self.get_git_root()
    if not self._git_root:
        print("Warning: Not in a Git repository")
        return (Path.cwd() / tool_name).resolve()
    
    # Get current working directory
    cwd = Path.cwd().resolve()
    
    # First check if we're already in a matching directory
    if cwd.name == tool_name and cwd.is_dir():
        print(f"Already in {tool_name} directory: {cwd}")
        return cwd
    
    try:
        # Calculate relative path from Git root
        try:
            rel_cwd = cwd.relative_to(self._git_root)
            print(f"Working in: {rel_cwd}")
        except ValueError:
            print("Warning: CWD is outside Git repository")
            rel_cwd = None
        
        # Find all matching tool directories
        for d in self._git_root.rglob(tool_name):
            try:
                if d.is_dir():
                    abs_path = d.resolve()
                    # Skip if it's our current directory (already checked)
                    if abs_path != cwd:
                        self._tool_dirs.append(abs_path)
            except (PermissionError, FileNotFoundError):
                continue
        
        if not self._tool_dirs:
            print(f"No '{tool_name}' directories found in repository")
            return (self._git_root / tool_name).resolve()
        
        # Find best matching directory
        best_match = None
        best_score = -1
        
        for tool_dir in self._tool_dirs:
            try:
                rel_tool = tool_dir.relative_to(self._git_root).parent
                
                # Calculate path match score
                match_count = 0
                for cwd_part, tool_part in zip(
                    rel_cwd.parts if rel_cwd else (),
                    rel_tool.parts
                ):
                    if cwd_part == tool_part:
                        match_count += 1
                    else:
                        break
                
                # Update best match
                if match_count > best_score:
                    best_score = match_count
                    best_match = tool_dir
            except ValueError:
                continue
        
        if best_match:
            print(f"Found {len(self._tool_dirs)} {tool_name} directories, selecting: {best_match}")
            return best_match
        else:
            print("No suitable directory found, using default location")
            return (self._git_root / tool_name).resolve()
            
    except Exception as e:
        print(f"Error finding {tool_name} directory: {str(e)}")
        return (Path.cwd() / tool_name).resolve()
        
def underline_string(input_string):
    # Count the number of characters (including spaces)
    char_count = len(input_string)
    
    # Create the underline with dashes
    underline = '-' * char_count
    
    # Return the original string and the underline
    return f"{input_string}\n# {underline}"

def tree(
        root_dir: str,
        prefix: str = "",
        max_depth: Optional[int] = None,
        current_depth: int = 0,
        is_root: bool = True,
        collapse_dirs: Optional[Set[str]] = None,
        skip_hidden: bool = True,
        skip_underscore: bool = True,
        show_files: bool = False,
        skip_symlinks: bool = True,
        output_file: Optional[str] = None,
        logger = None,
        _output: Optional[List[str]] = None,
        _collapse_single: bool = True
    ) -> List[str]:
    """
    Generate a directory tree structure with smart collapsing of single-item directory chains.
    
    This function recursively walks through directories and prints their structure in a tree-like format,
    with options to customize the output. It supports collapsing of single-directory chains and
    filtering of specific directory types.
    
    Args:
        root_dir: Starting directory for the tree
        prefix: Internal use for proper indentation (default: "")
        max_depth: Maximum recursion depth (default: None = unlimited)
        current_depth: Internal use for tracking recursion depth (default: 0)
        is_root: Internal flag for root directory handling (default: True)
        collapse_dirs: Set of directory names to stop recursion (default: common EDA dirs)
        skip_hidden: Skip hidden files/directories (starting with '.') (default: True)
        skip_underscore: Skip files/directories starting with '_' (default: True)
        show_files: Include files in the output (default: False)
        skip_symlinks: Skip symbolic links (default: True)
        output_file: Path to save output (default: None = print to console)
        logger: Optional logger object for output (default: None)
        _output: Internal use for accumulating output (default: None)
        _collapse_single: Enable smart collapsing of single-item chains (default: True)
    
    Returns:
        List of strings representing the directory tree
    
    Example:
        >> tree("/path/to/dir", max_depth=2, show_files=True)
        project/
        ├── src/
        │   ├── main.py
        │   └── utils/
        └── tests/
            └── test_main.py
    """
    
    # Initialize output list if not provided (first call)
    if _output is None:
        _output = []
    
    def write_output(line: str) -> None:
        """Helper function to handle output writing consistently."""
        _output.append(line)
        if logger:
            logger.process_info(line)

    # Set default directories to collapse if not provided
    if collapse_dirs is None:
        collapse_dirs = {"rtl", "tb", "reg", "sim", "syn", "sta", "lec", "lint", "upf", "doc", "script"}
    else:
        collapse_dirs = set(collapse_dirs)  # Ensure it's a set for fast lookups

    # Stop recursion if max depth reached
    if max_depth is not None and current_depth > max_depth:
        return _output

    # Handle root directory using pathlib.Path.resolve()
    if is_root:
        root_path = Path(root_dir).resolve()
        root_name = root_path.name
        write_output(root_name + "/")
        is_root = False

    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        write_output(f"{prefix}Cannot access {root_dir} (permission denied)")
        
        return _output

    # Filter entries based on various criteria
    filtered_entries = []
    for entry in entries:
        path = os.path.join(root_dir, entry)
        
        # Skip hidden/underscore entries if configured
        if (skip_hidden and entry.startswith('.')) or (skip_underscore and entry.startswith('_')):
            continue
            
        # Skip symlinks if configured
        if skip_symlinks and os.path.islink(path):
            continue
            
        # Skip files if show_files is False
        if os.path.isfile(path) and not show_files:
            continue
            
        filtered_entries.append(entry)

    # Process each filtered entry
    for i, entry in enumerate(filtered_entries):
        path = os.path.join(root_dir, entry)
        is_last = i == len(filtered_entries) - 1

        # Handle files (only if show_files is True)
        if os.path.isfile(path):
            connector = "\u2514\u2500\u2500 " if is_last else "\u251C\u2500\u2500 " # "└── " and "├── "
            write_output(prefix + connector + entry)
            continue

        # Skip if not a directory (shouldn't happen due to filtering)
        if not os.path.isdir(path):
            continue

        # Determine connectors and prefixes for tree structure
        connector = "\u2514\u2500\u2500 " if is_last else "\u251C\u2500\u2500 " # "└── " and "├── "
        next_prefix = prefix + ("    " if is_last else "\u2502   ") # "<4 spaces>" and │<3 spaces>"

        # Handle directory collapsing (smart single-item chain collapsing)
        collapsed_path = []
        current_path = path
        
        if _collapse_single:
            while True:
                try:
                    # Get sub-entries with filtering
                    sub_entries = [e for e in os.listdir(current_path) 
                                 if not ((skip_hidden and e.startswith('.')) or 
                                     (skip_underscore and e.startswith('_')))]
                    
                    # Further filter out files if show_files is False
                    if not show_files:
                        sub_entries = [e for e in sub_entries 
                                     if not os.path.isfile(os.path.join(current_path, e))]
                    
                    # Stop collapsing conditions:
                    # 1. Not exactly one subdirectory
                    # 2. Current directory is in collapse_dirs
                    if (len(sub_entries) != 1 or 
                        not os.path.isdir(os.path.join(current_path, sub_entries[0])) or
                        os.path.basename(current_path) in collapse_dirs):
                        break
                        
                    collapsed_path.append(sub_entries[0])
                    current_path = os.path.join(current_path, sub_entries[0])
                except (PermissionError, OSError):
                    break

        # Handle collapsed path display
        if collapsed_path:
            full_collapsed = entry + "/" + "/".join(collapsed_path)
            final_dir = os.path.basename(current_path)
            
            if final_dir in collapse_dirs:
                write_output(prefix + connector + full_collapsed + "/ --- (Stopped)")
            else:
                write_output(prefix + connector + full_collapsed + "/")
                # Recurse into the final directory of the collapsed path
                tree(
                    current_path,
                    next_prefix,
                    max_depth,
                    current_depth + len(collapsed_path) + 1,
                    is_root=False,
                    collapse_dirs=collapse_dirs,
                    skip_hidden=skip_hidden,
                    skip_underscore=skip_underscore,
                    show_files=show_files,
                    skip_symlinks=skip_symlinks,
                    output_file=None,
                    logger=logger,
                    _output=_output,
                    _collapse_single=_collapse_single
                )
        else:
            # Handle regular directory (no collapsing)
            if entry in collapse_dirs:
                write_output(prefix + connector + entry + "/ --- (Stopped)")
            else:
                write_output(prefix + connector + entry + "/")
                # Recurse into the directory
                tree(
                    path,
                    next_prefix,
                    max_depth,
                    current_depth + 1,
                    is_root=False,
                    collapse_dirs=collapse_dirs,
                    skip_hidden=skip_hidden,
                    skip_underscore=skip_underscore,
                    show_files=show_files,
                    skip_symlinks=skip_symlinks,
                    output_file=None,
                    logger=logger,
                    _output=_output,
                    _collapse_single=_collapse_single
                )

    # Handle output (only at root level)
    if current_depth == 0:
        # Join all lines with newlines
        full_output = '\n'.join(_output)
        # Write to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(full_output)
                if logger:
                    logger.process_info(f"Tree output saved to {output_file}")
                else:
                    print(f"Tree output saved to {output_file}")
            except IOError as e:
                if logger:
                    logger.process_error(f"Failed to write output: {str(e)}")
                else:
                    print(f"Error: Failed to write output file - {str(e)}")
                    
        # Print to console if no logger is specified
        if not logger:
            print(full_output)
    
    return _output

if __name__ == '__main__':
    collapse_dirs = {"rtl", "tb", "reg", "sim", "syn", "sta", "lec", "lint", "upf", "doc", "script", "docs", "lib", "libs", "src", "tests", "include","platform", "target", "full_cva6_repo"}
    tree(is_root = True, root_dir = '.', output_file='test.txt',collapse_dirs=collapse_dirs)
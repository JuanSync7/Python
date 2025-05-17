import re
import os
import argparse
from os import PathLike
from collections import defaultdict
from pathlib import Path
from typing import Union, Optional

def extract_tool_commands(
    content: str,
    tool_command: str = 'lint report item',
    validate: bool = False
) -> list[tuple[str, int, int]]:
    """
    Extract complete tool waiver commands with line number tracking.
    
    Parses TCL-style tool waiver commands that start with '<tool> report item' and end with '}',
    while tracking their exact line numbers in the original file. Returns each command with
    its content and line number range.

    Args:
        content: The input text containing tool waiver commands.
        tool_command: The tool command (default: 'lint report item').
        validate: If True, enables additional input validation and post-processing checks.
                 When False, only performs minimal required validation for performance.
                 (default: False)

    Returns:
        A list of tuples, each containing:
        - command (str): The complete tool waiver command text
        - start_line (int): The starting line number (1-based)
        - end_line (int): The ending line number (1-based)

    Raises:
        TypeError: If validate=True and content is not a string or tool is not a string.
        ValueError: If validate=True and content is empty or tool name is invalid.
        RuntimeError: If parsing fails (includes line number context in error message).

    Example:
        >> extract_tool_commands("1: # Comment\\n2: lint report item\\n3: -arg test\\n4: }")
        [("lint report item\\n   -arg test\\n}", 2, 4)]

        >> extract_tool_commands(content, validate=True)  # With full validation
    """
    # Input validation (only when validate=True)
    if validate:
        if not isinstance(content, str):
            raise TypeError(f"Content must be string, got {type(content).__name__}")
        if not isinstance(tool, str):
            raise TypeError(f"Command must be string, got {type(command).__name__}")
        if not content.strip():
            raise ValueError("Content cannot be empty")
        if not tool or not tool.isidentifier():
            raise ValueError(f"Invalid tool name: '{tool}' (must be non-empty valid identifier)")

    commands = []          # Stores complete commands as (text, start_line, end_line)
    current_command = []   # Accumulates lines for current command being processed
    in_command = False     # State flag indicating we're inside a command
    current_line_start = 0 # Tracks starting line of current command
    line_count = 0         # Counter for total lines processed (for error reporting)

    try:
        # Process each line with 1-based numbering
        for i, line in enumerate(content.splitlines(), 1):
            line_count = i
            stripped = line.strip()
            
            # Command start detection
            if stripped.startswith(tool_command):
                # Save previous command if exists
                if current_command:
                    commands.append(("\n".join(current_command), current_line_start, i-1))
                
                # Start new command
                current_command = [stripped]
                in_command = True
                current_line_start = i
                
            # Command continuation
            elif in_command:
                current_command.append(stripped)
                
                # Command end detection
                if stripped.endswith("}"):
                    cmd_text = "\n".join(current_command)
                    
                    # Validation (runs regardless of validate flag)
                    if "{" in cmd_text and cmd_text.count("{") != cmd_text.count("}"):
                        print(f"Warning: Unbalanced braces in command at line {i}")
                    
                    commands.append((cmd_text, current_line_start, i))
                    current_command = []
                    in_command = False

        # Handle unterminated commands (missing closing })
        if current_command:
            cmd_text = "\n".join(current_command)
            commands.append((cmd_text, current_line_start, line_count))
            if "}" not in cmd_text:
                print(f"Warning: Unterminated command at line {current_line_start}")
                
    except Exception as e:
        # Provide context for parsing errors
        raise RuntimeError(
            f"Parsing failed at line {line_count}: {str(e)}\n"
            f"Current command context: {current_command[-3:] if current_command else 'None'}"
        )

    # Post-processing validation (only when validate=True)
    if validate:
        if not commands:
            print("Warning: No complete commands found in content")
        else:
            # Validate command line ranges
            for cmd_text, start, end in commands:
                if start > end:
                    raise RuntimeError(f"Invalid line range {start}-{end} in command")
                if len(cmd_text.splitlines()) != (end - start + 1):
                    print(f"Warning: Possible line count mismatch in command {start}-{end}")

    return commands

def parser_lint_waiver_warning_lines(warning_content, directive: str):
    """
    Parse lint tool warning messages to extract the first line number mentioned for each duplicate waiver warning.

    Processes warning messages that follow the format:
    ## Applying Lint Waivers...
    # Warning : Path specified is covered... [File 'path.tcl', Line 'X'] and [File 'path.tcl', Line 'Y']
    [directive-321]

    Args:
        warning_content (str): The warning messages output from the lint tool.

    Returns:
        set: A set of integers representing the first line numbers mentioned in each duplicate
             waiver warning (the lines that should be removed).

    Example:
        Input:
            "## Applying Lint Waivers...\n
             # Warning: Path specified [File 'file.tcl', Line '9'] and [File 'file.tcl', Line '11']\n
             [directive-321]"
        Output:
            {9}
    """
    duplicates = set()
    in_lint_waiver_section = False
    
    for line in warning_content.splitlines():
        stripped = line.strip()
        
        # Check for section header
        if stripped.startswith("## Applying Lint Waivers"):
            in_lint_waiver_section = True
            continue
            
        # Only process warnings if we're in the right section
        if not in_lint_waiver_section:
            continue
            
        # Skip empty lines or non-warning lines
        if not stripped.startswith("# Warning"):
            continue
            
        # Extract the first line number match
        if match := re.search(r"Line '(\d+)'", line):
            try:
                line_num = int(match.group(1))
                duplicates.add(line_num)
            except (ValueError, IndexError):
                continue  # Skip malformed line numbers
                
    return duplicates

def clean_waiver_file(
    waiver_path: Union[str, PathLike],
    log_file: Union[str, PathLike],
    output_path: Optional[Union[str, PathLike]] = None
) -> None:
    """
    Remove duplicate lint waiver commands based on warnings in the log file.

    Args:
        waiver_path: Path to input waiver file (str, PathLike, or pathlib.Path)
        log_file: Path to log file containing duplicate warnings
        output_path: Path for cleaned output file (defaults to '<waiver_path>.cleaned')

    Returns:
        None: Output is written to specified file

    Raises:
        FileNotFoundError: If input files not found
        ValueError: For empty/malformed files
        TypeError: For invalid path types
        OSError: For filesystem errors
    """
    # Convert all paths to Path objects for consistent handling
    try:
        waiver_path = Path(waiver_path) if not isinstance(waiver_path, Path) else waiver_path
        log_file = Path(log_file) if not isinstance(log_file, Path) else log_file
        output_path = Path(output_path) if output_path is not None else None
    except TypeError as e:
        raise TypeError(f"Invalid path type: {str(e)}")

    # Set default output path if not provided
    if output_path is None:
        output_path = waiver_path.with_name(f"{waiver_path.name}.cleaned")

    try:
        # Read and validate waiver file
        try:
            content = waiver_path.read_text().splitlines()
            if not content:
                raise ValueError(f"Waiver file '{waiver_path}' is empty")
        except FileNotFoundError:
            raise FileNotFoundError(f"Waiver file not found: {waiver_path}")
        except UnicodeDecodeError:
            raise ValueError(f"Waiver file '{waiver_path}' is not a text file")

        # Read and validate log file
        try:
            logs = log_file.read_text()
            if not logs.strip():
                raise ValueError(f"Log file '{log_file}' is empty")
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {log_file}")
        except UnicodeDecodeError:
            raise ValueError(f"Log file '{log_file}' is not a text file")

        # Process file contents
        try:
            commands = extract_tool_commands('\n'.join(content))
            if not commands:
                raise ValueError("No valid lint commands found")
                
            duplicate_lines = parser_lint_waiver_warning_lines(warning_content=logs,directive='directive-321')
            if not duplicate_lines:
                print("Warning: No duplicate warnings found")
                return
        except Exception as e:
            raise ValueError(f"Error processing files: {str(e)}")

        # Identify lines to remove
        lines_to_remove = set()
        for line_num in duplicate_lines:
            for cmd in commands:
                try:
                    cmd_text, start, end = cmd
                    if start <= line_num <= end:
                        lines_to_remove.update(range(start, end + 1))
                        break
                except (ValueError, TypeError) as e:
                    print(f"Warning: Malformed command tuple - {str(e)}")
                    continue

        # Write output file
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open('w') as f:
                for i, line in enumerate(content, 1):
                    if i not in lines_to_remove:
                        f.write(line + '\n')
        except OSError as e:
            raise OSError(f"Failed to write {output_path}: {str(e)}")

        print(f"Removed {len(lines_to_remove)} lines from {len(duplicate_lines)} commands")
        print(f"Clean file: {output_path}")

    except Exception as e:
        if output_path and output_path.exists():
            try:
                output_path.unlink()
            except:
                pass
        raise
    
def group_specific_checks(input_file, checks_to_group, output_dir):
    """
    Organize lint waiver commands into separate files based on specified check types.

    Processes a TCL file containing lint waiver commands and groups them into separate
    output files based on their check type. Commands matching specified checks are
    written to individual files, while all others are collected in an 'other_commands.tcl' file.

    Args:
        input_file (str): Path to the input file containing lint waiver commands.
                         Expected format: TCL file with 'lint report item' commands.
        checks_to_group (set): A set of check names (strings) to be grouped separately.
                              Example: {"clock_crossing", "expr_operands_width_mismatch"}
        output_dir (str): Directory path where grouped files will be created.
                         Directory will be created if it doesn't exist.

    Returns:
        None: Outputs are written to files in the specified directory.

    Raises:
        FileNotFoundError: If the input_file cannot be found.
        OSError: If there are issues creating the output directory or files.

    Example:
        >>> group_specific_checks(
        ...     "waivers.tcl",
        ...     {"clock_crossing", "expr_operands_width_mismatch"},
        ...     "grouped_waivers"
        ... )
        Created grouped_waivers/clock_crossing_commands.tcl with 12 commands
        Created grouped_waivers/expr_operands_width_mismatch_commands.tcl with 8 commands
        Created grouped_waivers/other_commands.tcl with 23 other commands
    """
    # Read input file content
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Extract all complete lint commands with line numbers
    commands = extract_tool_commands(content)
    
    # Initialize storage for grouped commands
    check_groups = defaultdict(list)  # Dictionary: {check_name: [command1, command2, ...]}
    other_commands = []               # Commands not matching specified checks
    
    # Process each lint command
    for cmd_tuple in commands:
        cmd_text, start_line, end_line = cmd_tuple  # Unpack command data
        
        # Extract check name from command using regex
        match = re.search(r'-check\s+\{([^}]+)\}', cmd_text, re.DOTALL)
        if match:
            check_name = match.group(1).strip()
            
            # Group commands based on specified checks
            if check_name in checks_to_group:
                check_groups[check_name].append(cmd_text)
            else:
                other_commands.append(cmd_text)
        else:
            # Commands without check specification go to 'other'
            other_commands.append(cmd_text)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Write commands for each specified check to separate files
    for check_name, cmd_list in check_groups.items():
        # Create safe filename by replacing special characters
        safe_name = re.sub(r'\W+', '_', check_name)
        output_file = os.path.join(output_dir, f'{safe_name}_commands.tcl')
        
        # Write all commands for this check type
        with open(output_file, 'w') as f:
            f.write('\n\n'.join(cmd_list) + '\n')  # Separate commands with blank lines
        
        print(f"Created {output_file} with {len(cmd_list)} commands")
    
    # Write remaining commands to 'other_commands.tcl'
    if other_commands:
        other_file = os.path.join(output_dir, 'other_commands.tcl')
        with open(other_file, 'w') as f:
            f.write('\n\n'.join(other_commands) + '\n')
        print(f"Created {other_file} with {len(other_commands)} other commands")
          
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Group specific lint checks into separate files')
    parser.add_argument('input_file', help='Input file containing lint commands. Can be report or log file')
    parser.add_argument('--waiver_file', help='Path to the waiver file to clean',)
    parser.add_argument('--checks', nargs='+', required=False,
                       help='List of checks to group (space-separated)')
    parser.add_argument('-o','--output-dir', default='grouped_checks',
                       help='Output directory for grouped files (default: grouped_checks)')
    
    args = parser.parse_args()
    
    if args.checks:
        group_specific_checks(
            args.input_file,
            set(args.checks),
            args.output_dir
        )
    
    # Clean waiver file
    if args.waiver_file:
        clean_waiver_file(args.waiver_file, args.input_file, None)
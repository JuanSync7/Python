import re
import os
import argparse

def extract_unused_line_numbers(report_text):
    """
    Extract line numbers from the 'Unused Status Update Directives' section of a lint report.
    
    Args:
        report_text (str): The full text content of the lint report file.
        
    Returns:
        set: A set of line numbers (integers) where unused directives were found.
        
    Note:
        The function looks for section "Section 2  : Unused Status Update Directives"
        and extracts all back reference line numbers from that section.
    """
    # Find the section using a flexible pattern that accounts for variable whitespace
    section_header = r"Section 2\s\s:\s*Unused Status Update Directives"
    section_match = re.search(
        rf"{section_header}(.*?)(?:\n={100}|$)",  # Match until next section or end of file
        report_text,
        re.DOTALL  # Allow . to match newlines
    )
    
    if not section_match:
        print("Error: Could not find 'Unused Status Update Directives' section")
        return set()
    
    section_content = section_match.group(1)
    
    line_numbers = set()
    
    # Extract all line numbers from back references in the section
    for match in re.finditer(
        r"Back reference: File '.*?', Line '(\d+)'",  # Capture the line number
        section_content
    ):
        line_numbers.add(int(match.group(1)))

    return line_numbers

def process_waiver_file(input_path, output_path, unused_lines):
    """
    Process a waiver file to remove directives at specified line numbers.
    
    Args:
        input_path (str): Path to the input waiver file.
        output_path (str): Path where the filtered waiver file will be written.
        unused_lines (set): Set of line numbers (1-based) to remove from the file.
        
    Note:
        The function identifies waiver blocks (starting with 'lint report item' and ending with '}'),
        and removes those blocks that begin on lines specified in unused_lines.
    """
    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    # Find all waiver items (multi-line blocks starting with 'lint report item')
    waiver_blocks = []
    current_block = None
    
    # Parse the file to identify all waiver blocks
    for i, line in enumerate(lines):
        if line.lstrip().startswith('lint report item'):
            if current_block is not None:
                # Close previous block if not properly terminated (error case)
                waiver_blocks.append((current_block[0], i-1))
            current_block = (i, None)  # Start new block
        elif current_block is not None and '}' in line.rstrip():
            # Found end of current block (closing brace)
            waiver_blocks.append((current_block[0], i))
            current_block = None
    
    # Remove blocks that start on unused_lines
    kept_lines = []
    last_pos = 0  # Tracks our position in the original file
    
    for start, end in sorted(waiver_blocks):
        # Add lines before this block
        if last_pos < start:
            kept_lines.extend(lines[last_pos:start])
        
        # Add the block if it's not in unused_lines
        # Note: +1 because line numbers in the report are 1-based
        if (start + 1) not in unused_lines:
            kept_lines.extend(lines[start:end+1])
        
        last_pos = end + 1
    
    # Add remaining lines after last block
    if last_pos < len(lines):
        kept_lines.extend(lines[last_pos:])
    
    # Write output file
    with open(output_path, 'w') as f:
        f.writelines(kept_lines)
    
    # Print statistics
    removed = len([s for s, _ in waiver_blocks if (s + 1) in unused_lines])
    print(f"Created filtered waiver file: {output_path}")
    print(f"Removed {removed} unused waiver directives")
    print(f"Kept {len(waiver_blocks) - removed} waiver directives")
    
def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments with attributes:
            - report: Path to lint report file
            - input: Path to input waiver file
            - output: Path for output filtered waiver file
            - force: Flag to overwrite existing output file
    """
    parser = argparse.ArgumentParser(
        description="Filter unused waiver directives from a lint report."
    )
    
    parser.add_argument(
        '-r', '--report',
        required=True,
        help="Path to the lint report file (e.g., lint_status_history.rpt)"
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help="Path to the input waiver file to be filtered"
    )
    
    parser.add_argument(
        '-o', '--output',
        required=False,
        default = "rtl_lint/waivers/lint_waivers_filtered.tcl",
        help="Path for the output filtered waiver file"
    )
    
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help="Overwrite output file if it exists (default: generate unique name)"
    )
    
    return parser.parse_args()
    
def main():
    """
    Main function to filter unused waiver directives using command line arguments.
    """
    args = parse_arguments()
    
    # Check if output file exists and handle accordingly
    if os.path.exists(args.output) and not args.force:
        base, ext = os.path.splitext(args.output)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        args.output = f"{base}_{counter}{ext}"
    
    # Read the lint report file
    with open(args.report, 'r') as f:
        unused_directives_report = f.read()

    # Extract line numbers of unused directives
    unused_start_lines = extract_unused_line_numbers(unused_directives_report)
    
    # Process the waiver file to remove unused directives
    process_waiver_file(args.input, args.output, unused_start_lines)
    
if __name__ == "__main__":
    main()
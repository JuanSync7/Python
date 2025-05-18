import re
def remove_sv_comments(content):
    """
    Removes SystemVerilog comments from either:
    - A file path (str) pointing to .sv/.v file
    - A raw string containing SystemVerilog code
    
    Preserves string literals and removes:
    - Block comments (/* ... */)
    - Line comments (// ...)
    """
    if isinstance(content, str) and '\n' not in content and len(content) < 256:
    try:
        with open(content, 'r') as f:
            content = f.read()
    except (IOError, OSError, UnicodeDecodeError):
        pass  # Assume it's code if file open fails
        
    in_string = False
    in_block_comment = False
    in_line_comment = False
    i = 0
    n = 0
    output = []
    
    while i < n:
        if not in_string and not in_block_comment and not in_line_comment:
            # Check for comment starts outside strings
            if content.startswith("/*", i):
                in_block_comment = True
                i += 2
                continue
            elif content.startswith("//", i):
                in_line_comment = True
                i += 2
                continue
            elif content[i] == '"':
                in_string = True
                output.append(content[i])
                i += 1
                continue
        else:
            # Handle string literals (ignore /* or // inside them)
            if in_string:
                if content[i] == '"' and (i == 0 or content[i-1] != '\\'):
                    in_string = False
                output.append(content[i])
                i += 1
                continue
            # Handle block comments
            elif in_block_comment:
                if content.startswith("*/", i):
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue
            # Handle line comments
            elif in_line_comment:
                if content[i] == '\n':
                    in_line_comment = False
                    output.append(content[i])  # Keep the newline
                i += 1
                continue

        # Append non-comment characters
        if not in_block_comment and not in_line_comment:
            output.append(content[i])
        i += 1

    return ''.join(output)

def check_include_relative_path(include_file) -> bool:
    
    if include_file.startswith("/"):
        return False
    else:
        return True

def lint_check_include_line(filelist):
    """
    Check that `include directives appear on lines by themselves,
    with only optional whitespace and/or a comment.
    
    Args:
        filelist: List of files to check
    Returns:
        dict: Mapping of filenames to lists of error line numbers
    """
    errors = {}
    
    include_list = []
    
    include_pattern = re.compile(r'^\s*`include\s+"(\\.|[^"\\])*?"\s*$')
    
    for file in filelist:
        try:
            content = remove_sv_comments(file)
            content = content.splitlines()
            for line_num,line in enumerate(content,1):
                line = line.strip() # remove leading and trailing white spaces
                if  '`include' in line:
                    include_line = include_pattern.fullmatch(line)
                    if not include_line: # check if its the expected include pattern
                        errors.setdefault(file, []).append(line_num)
                    else: # if it is a full match
                        check_include_relative_path(include_line.group(1))
                        
                    
        except UnicodeDecodeError:
            print(f'Warning: Could not read file {file} (likely binary file)')
            continue
        except Exception as e:
            print(f'Error processing {file}: {str(e)}')
            continue
        
    # Print summary of errors
    for file, line_nums in errors.items():
        print(f'\nInclude directive violations in {file}:')
        for line in line_nums:
            print(f'  Line {line}: Only whitespace/comments allowed with `include')
            
    return errors
    
    
def extract_all_include(filelist) -> list:
    include_pattern = re.compile(r'^\s*`include\s+"([^"]+)"\s*$')
    
    include_list = []
    
    for file in filelist:
        try:
            with open(file, 'r') as f:
                for line in f:
                    match = include_pattern.match(line.strip())
                    if match:
                        include_list.append((file, match.group(1)))
        except IOError:
            print(f"Warning: Could not read file {file}")
            continue
                    
    return include_list

def extract_all_define(filelist) -> list:
    """
    Extract all `define macros from Verilog files.
    
    Args:
        filelist: List of file paths to search
    
    Returns:
        List of tuples (filename, define_name, define_value)
    """

    # Pattern to match `define and capture the rest until non-continued line
    define_pattern = re.compile(
        r'^\s*`define\s+([a-zA-Z_]\w*)\s*((?:.*\\\n)*.*)',
        re.MULTILINE
    )    
    
    define_list = []
    
    for file in filelist:
        try:
            with open(file, 'r') as f:
                content = f.read()
                for match in define_pattern.finditer(content):
                    define_name = match.group(1)
                    define_value = match.group(2)
                    # Remove trailing backslashes and join lines
                    define_value = re.sub(r'\\\n', '', define_value).strip()
                    define_list.append((file, define_name, define_value))
        except IOError:
            print(f"Warning: Could not read file {file}")
            continue

        r'(?:(?:/\*.*?\*/)|(?://.*?\n)|(?:^\s*`.*?$))*(^\s*module\s+(\w+)\b(?:[^;]*?\);)?\s*(.*?)^\s*endmodule\b',
        re.MULTILINE | re.DOTALL | re.IGNORECASE

def extract_module_name(line):
    """Extract module name without complex bracket counting"""
    MODULE_KW = "module"
    idx = line.find(MODULE_KW)
    if idx == -1:
        return None
    
    pos = idx + len(MODULE_KW)
    length = len(line)
    
    # Skip whitespace
    while pos < length and line[pos].isspace():
        pos += 1
    
    # Handle parameterized modules
    if pos < length and line[pos] == '#':
        pos += 1
        # Find opening parenthesis
        while pos < length and line[pos] != '(':
            pos += 1
        if pos >= length:
            return None
        pos += 1  # Skip '('
        
        # Find closing parenthesis (no nesting needed)
        paren_level = 1
        while pos < length and paren_level > 0:
            if line[pos] == '(':
                paren_level += 1
            elif line[pos] == ')':
                paren_level -= 1
            pos += 1
    
    # Now find the module name
    while pos < length and line[pos].isspace():
        pos += 1
    
    start = pos
    while pos < length and (line[pos].isalnum() or line[pos] == '_'):
        pos += 1
    
    return line[start:pos] if start != pos else None
    
 
def split_verilog_modules(input_file, output_dir="output"):
    """Split a Verilog file with multiple modules into separate files."""
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    clean_content = remove_sv_comments(content)
    
    # Process both original and clean content
    orig_lines = original_content.split('\n')
    clean_lines = clean_content.split('\n')
    
    modules = []
    current_module = None
    in_module = False
    pre_content = []
    
    for i, (orig_line, clean_line) in enumerate(zip(orig_lines, clean_lines)):
        clean_line_stripped = clean_line.strip()
        if not in_module:
            # Detect module start (ignoring comments)
            if re.match(r'^\s*module\b', clean_line):
                module_name = extract_module_name(clean_line)
                current_module = {
                    'name': module_name,
                    'start_line': i,
                    'content': [orig_line]
                }
                in_module = True
                current_module['content'].append(pre_content)
        else:
            pre_content.append(orig_line) # if not in_module, append to pre_content
            # Check for endmodule at brace level 0
            if (re.search(r'^\s*endmodule\b', clean_line_stripped)):
                modules.append(current_module)
                in_module = False
                
    # Write modules to files
    for module in modules:
        output_file = os.path.join(output_dir, f"{module['name']}.sv")
        with open(output_file, 'w') as f:
            f.write(module['content'])
            print(f"Created: {output_file}")

def check_standalone_generate(segment):
    '''IEEE 1800-2017 Standard Clarification on generate Blocks'''
    block_type = [
        ('GEN_IF',r'\bgenerate\b.*?\bif\b.*?\bendgenerate\b'),
        ('GEN_FOR',r'\bgenerate\b.*?\bfor\b.*?\bendgenerate\b'),
        ('GEN_CASE',r'\bgenerate\b.*?\b(case|casex|casez)\b.*?\bendgenerate\b'),
        ('GEN_ALONE',r'\bgenerate\b.*?\bendgenerate\b')
    ]       
    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in block_type)
    gen_type = re.match(token_regex,segment,re.MULTILINE|re.DOTALL)
    kind = gen_type.lastgroup
    value = gen_type.group()
    if kind == 'GEN_ALONE': # if it is a standalone generate statement
        #TODO some way to handle ERROR
        print("Standalone generate statement not allowed based on IEEE 1800-2017 Standard Clarification on generate Blocks.")
    return kind, value



def postfix_to_infix_verilog(postfix_expr):
    """Convert postfix notation to infix notation for SystemVerilog operators."""
    # Define operator properties: precedence, associativity, and arity
    OPERATORS = {
        # Unary operators
        '!': {'prec': 14, 'assoc': 'right', 'arity': 1},
        '~': {'prec': 14, 'assoc': 'right', 'arity': 1},
        # Binary operators
        '**': {'prec': 15, 'assoc': 'right', 'arity': 2},
        '*': {'prec': 12, 'assoc': 'left', 'arity': 2},
        '/': {'prec': 12, 'assoc': 'left', 'arity': 2},
        '%': {'prec': 12, 'assoc': 'left', 'arity': 2},
        '+': {'prec': 11, 'assoc': 'left', 'arity': 2},
        '-': {'prec': 11, 'assoc': 'left', 'arity': 2},
        '<<': {'prec': 10, 'assoc': 'left', 'arity': 2},
        '>>': {'prec': 10, 'assoc': 'left', 'arity': 2},
        '<<<': {'prec': 10, 'assoc': 'left', 'arity': 2},
        '>>>': {'prec': 10, 'assoc': 'left', 'arity': 2},
        '<': {'prec': 9, 'assoc': 'left', 'arity': 2},
        '<=': {'prec': 9, 'assoc': 'left', 'arity': 2},
        '>': {'prec': 9, 'assoc': 'left', 'arity': 2},
        '>=': {'prec': 9, 'assoc': 'left', 'arity': 2},
        '==': {'prec': 8, 'assoc': 'left', 'arity': 2},
        '!=': {'prec': 8, 'assoc': 'left', 'arity': 2},
        '===': {'prec': 8, 'assoc': 'left', 'arity': 2},
        '!==': {'prec': 8, 'assoc': 'left', 'arity': 2},
        '&': {'prec': 7, 'assoc': 'left', 'arity': 2},
        '^': {'prec': 6, 'assoc': 'left', 'arity': 2},
        '^~': {'prec': 6, 'assoc': 'left', 'arity': 2},
        '~^': {'prec': 6, 'assoc': 'left', 'arity': 2},
        '|': {'prec': 5, 'assoc': 'left', 'arity': 2},
        '&&': {'prec': 4, 'assoc': 'left', 'arity': 2},
        '||': {'prec': 3, 'assoc': 'left', 'arity': 2},
    }

    stack = []
    
    for token in postfix_expr.split():
        if token not in OPERATORS:
            # Push operands (numbers/variables)
            stack.append((token, None))
        else:
            op_info = OPERATORS[token]
            if op_info['arity'] == 1:
                # Handle unary operators
                right = stack.pop()
                right_expr, right_op = right
                
                # Determine if right operand needs parentheses
                if right_op and (
                    OPERATORS[right_op]['prec'] < op_info['prec'] or
                    (OPERATORS[right_op]['prec'] == op_info['prec'] and
                     op_info['assoc'] == 'left')
                ):
                    right_str = f"({right_expr})"
                else:
                    right_str = right_expr
                
                new_expr = f"{token}{right_str}"
                stack.append((new_expr, token))
            else:
                # Handle binary operators
                right = stack.pop()
                left = stack.pop()
                left_expr, left_op = left
                right_expr, right_op = right

                # Process left operand
                if left_op and (
                    OPERATORS[left_op]['prec'] < op_info['prec'] or
                    (OPERATORS[left_op]['prec'] == op_info['prec'] and
                     op_info['assoc'] == 'right')
                ):
                    left_str = f"({left_expr})"
                else:
                    left_str = left_expr

                # Process right operand
                if right_op and (
                    OPERATORS[right_op]['prec'] < op_info['prec'] or
                    (OPERATORS[right_op]['prec'] == op_info['prec'] and
                     op_info['assoc'] == 'left')
                ):
                    right_str = f"({right_expr})"
                else:
                    right_str = right_expr

                new_expr = f"{left_str} {token} {right_str}"
                stack.append((new_expr, token))

    return stack[0][0] if stack else ""

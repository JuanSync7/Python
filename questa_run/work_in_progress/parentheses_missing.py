#!/usr/bin/env python3
import re
from collections import defaultdict

# SystemVerilog operator precedence (highest to lowest)
OPERATOR_PRECEDENCE = [
    ['++', '--', '**'],                   # Highest precedence
    ['!', '~', '&', '~&', '|', '~|', '^', '~^', '^~', '+', '-'],  # Unary operators
    ['*', '/', '%'],
    ['+', '-'],
    ['<<', '>>', '<<<', '>>>'],
    ['<', '<=', '>', '>=', 'inside', 'dist'],
    ['==', '!=', '===', '!==', '==?', '!=?'],
    ['&'],
    ['^', '^~', '~^'],
    ['|'],
    ['&&'],
    ['||'],
    ['?', ':'],                           # Conditional operator
    ['->', '<->'],
    ['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '<<<=', '>>>=']  # Lowest
]

systemverilog_operator_precedence = [
    (1,  "Unary, Postfix",       ["++", "--", "()", "[]", ".", "::"],                     "Left-to-right"),
    (2,  "Unary",                ["+", "-", "!", "~", "&", "~&", "|", "~|", "^", "~^", "^~", "++", "--"], "Right-to-left"),
    (3,  "Multiplicative",       ["*", "/", "%"],                                         "Left-to-right"),
    (4,  "Additive",             ["+", "-"],                                              "Left-to-right"),
    (5,  "Shift",                ["<<", ">>", "<<<", ">>>"],                               "Left-to-right"),
    (6,  "Relational",           ["<", "<=", ">", ">="],                                  "Left-to-right"),
    (7,  "Equality",             ["==", "!=", "===", "!==", "==?", "!=?"],                "Left-to-right"),
    (8,  "Bitwise AND",          ["&", "~&"],                                             "Left-to-right"),
    (9,  "Bitwise XOR",          ["^", "~^", "^~"],                                       "Left-to-right"),
    (10, "Bitwise OR",           ["|", "~|"],                                             "Left-to-right"),
    (11, "Logical AND",          ["&&"],                                                  "Left-to-right"),
    (12, "Logical OR",           ["||"],                                                  "Left-to-right"),
    (13, "Conditional (Ternary)", ["?:"],                                                 "Right-to-left"),
    (14, "Assignment & Concatenation", ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=", "<<<=", ">>>=", "{}", "{{}}"], "Right-to-left"),
]

def shunting_yard(tokens):
    """Convert infix tokens to postfix notation (RPN) using Shunting Yard algorithm."""
    PRECEDENCE = {
        '**': 15, '!': 14, '~': 14,  # Unary ops would need special handling
        '*': 12, '/': 12, '%': 12,
        '+': 11, '-': 11,
        '<<': 10, '>>': 10, '<<<': 10, '>>>': 10,
        '<': 9, '<=': 9, '>': 9, '>=': 9,
        '==': 8, '!=': 8, '===': 8, '!==': 8,
        '&': 7, '^': 6, '^~': 6, '~^': 6,
        '|': 5,
        '&&': 4,
        '||': 3,
        '?': 2,
        ':': 1
    }
    RIGHT_ASSOC = {'**'}
    
    output = []
    op_stack = []
    
    for token in tokens:
        if token in PRECEDENCE:
            # Handle operator precedence and associativity
            while (op_stack and op_stack[-1] != '(' and
                   (PRECEDENCE[op_stack[-1]] > PRECEDENCE[token] or
                    (PRECEDENCE[op_stack[-1]] == PRECEDENCE[token] and 
                     token not in RIGHT_ASSOC))):
                output.append(op_stack.pop())
            op_stack.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            # Pop until matching '('
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Mismatched parentheses")
            op_stack.pop()  # Remove the '('
        else:
            # Numbers or variables go directly to output
            output.append(token)
    
    # Pop remaining operators
    while op_stack:
        op = op_stack.pop()
        if op == '(':
            raise ValueError("Mismatched parentheses")
        output.append(op)
    
    return output
    
    
    return postfix_expr

# Example usage:
postfix_expr = "a b + c d * * e f ** g + /"  # Equivalent to ((a + b) * (c * d)) / (e ** f + g)
infix_expr = postfix_to_infix_verilog(postfix_expr)
print(infix_expr)  # Output: "a + b * c * d / (e ** f + g)"

def high_level_tokenize(expr):
    
    split_sv_module = r'''
        (?P<MODULE_NAME>module\s+[a-zA-Z_$][\w$]*)  # Module declaration (e.g., "module my_module")
        (?P<IMPORT>(?:\s*import\s+[a-zA-Z_$][\w$]*::.*?;)*)  # Imports (optional, multiple)
        (?P<PARAMETERS>\s*\#\s*\(.*?\))?  # Parameters (optional, e.g., "#(parameter WIDTH=32)")
        (?P<PORTS>\s*\(.*?\))?  # Ports (optional, e.g., "(input clk, output data)")
        (?P<REST>.*?)  # Everything until...
        endmodule  # Closing "endmodule"
    '''
    
    token_spec = [
        ('MODULE_NAME', r'(?<=module\s)[a-zA-Z_$][\w$]*'),
        ('IMPORT', r'(?<=import)\s*[a-zA-Z_$][\w$]*::.*?;'),
        ('PARAMETERS', r'\s*(?<=#)\s*\(.*?\)'),
        ('PORTS', r'(\(\s*(input|output|inout)\s+(wire|reg|logic|.*?_s|.*?_t|.*?_if)?\s*(?:\[.*?\])?\s*([\w,\s]+)\s*\));')
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
    tokens = []
    
    for mo in re.finditer(tok_regex, expr, re.MULTILINE):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'COMMENT' or kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise ValueError(f'Unexpected character: {value}')
            
        tokens.append((kind, value))
    return tokens

def tokenize(expr):
    """Tokenize SystemVerilog expression while preserving existing groupings."""
    token_spec = [
        ('COMMENT', r'//.*?$|/\*.*?\*/'),
        ('PAREN', r'[()]'),
        ('Array', r'[\[\]]'),
        ('CONCAT', r'[{}]'),
        ('COMMA', r'''[,]'''),
        ('BIT_CAST', r''''[bhdBHD]'''),
        ('HEX_NUM', r'''(?<='[hH])[0-9A-F]+'''),
        ('BIN_NUM', r'''(?<='[bB])[0-1]+'''),
        ('DEC_NUM', r'''(?<='[dD])[0-9]+'''),
        ('LOGICAL_OPS',r'&&|\|\||!'),
        ('BITWISE_OPS', r'~&|~\||~^|[~&|^]'),
        ('OPERATOR', r'<<<=|>>>=|<<=|>>=|<=|>=|===|!==|==?|!=?|\+\+|--|\*\*|->|<->|[+*/%!<>:=%-]'),
        ('TERNARY',r'[?]'),
        ('NUMBER', r'\d+\'[bhdBHD]?\s*[0-9a-fA-F_xzXZ?]+|\d+\.\d+|\d+'),
        ('L_IDENT', r'[a-zA-Z_$][\w$]*(?=\s*=\s*)'),
        ('R_IDENT', r'[a-zA-Z_$][\w$]*'),
        ('SEMICOLON', r';+'),
        ('SKIP', r'\s+'),
        ('MISMATCH', r'.')
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
    tokens = []
    square_bracket_depth = 0  # Track array bracket nesting
    curly_bracket_depth = 0 # Track concatination and replication bracket nesting
    paren_depth = 0 # Track parentheses depth nesting
    ternary_depth = 0 # Ternary Depth
    colon_seeking_queue = []
    
    for mo in re.finditer(tok_regex, expr, re.MULTILINE):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'COMMENT' or kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise ValueError(f'Unexpected character: {value}')
        
        # Update array context tracking
        if value == '[': 
            square_bracket_depth += 1
            colon_seeking_queue.append('[')
        elif value == ']': 
            square_bracket_depth -= 1
        elif value == '{':
            curly_bracket_depth += 1
        elif value == '}':
            curly_bracket_depth -= 1  
        elif value == '(':
            kind = kind + f"_{paren_depth}"
            paren_depth += 1
        elif value == ')':
            paren_depth -= 1
            kind = kind + f"_{paren_depth}"
        elif value == '?':
            ternary_depth += 1
            colon_seeking_queue.append('?')
            
        # Update based on more specific cases
        if value == ":":
            if colon_seeking_queue[-1] == '[':
                kind = "ARRAY_COLON"
                colon_seeking_queue.pop()
            elif colon_seeking_queue[-1] == '?':
                kind = "TERNARY_COLON"
                colon_seeking_queue.pop()
            else:
                kind = "COLON"     
        #TODO handling the concatination  
        if value == ",":
            kind = "CONCAT_COMMA" if curly_bracket_depth > 0 else 'COMMA'
            
        #TODO something for port
        
        #TODO something for parameters
            
        tokens.append((kind, value))
    return tokens

def extract_between(tokens, start_token, end_token,inclusive = False):
    """
    Extract all tokens between `start_token` and `end_token` (inclusive/exclusive).
    
    Args:
        tokens (list): List of (token_type, token_value) tuples.
        start_token (str/tuple): Token that marks the start (e.g., '=' or ('OPERATOR', '=')).
        end_token (str/tuple): Token that marks the end (e.g., ';' or ('SEMICOLON', ';')).
    
    Returns:
        list: List of matches, where each match is a sublist of tokens between `start_token` and `end_token`.
    """
    matches = []
    inside_match = False
    current_match = []
    if inclusive:
        current_match.append(start_token)
    for token in tokens:
        # Check if the current token matches `start_token`
        if not inside_match:
            if (isinstance(start_token, str)) and (token[1] == start_token):
                inside_match = True
            elif (isinstance(start_token, tuple)) and ((token[0], token[1]) == start_token):
                inside_match = True
            continue
        
        # If inside a match, collect tokens until `end_token` is found
        if inside_match:
            # Check if the current token matches `end_token`
            if (isinstance(end_token, str) and (token[1] == end_token)) or \
                (isinstance(end_token, tuple) and ((token[0], token[1]) == end_token)):
                if inclusive:
                    current_match.append(end_token)
                matches.append(current_match)
                current_match = []
                inside_match = False
            else:
                current_match.append(token)
                
    return matches

#TODO grouping
def grouping(tokens):
    ''

#TODO handle ternary environment

#TODO handle bracket environment

#TODO handle concatination environment

#TODO handle arithmetic expressions environment


def test():
    expression = [()]
    expr1 = extract_between(tokenize('wire [15:0] data = mem[addr + 1] && sys_a | sys_b;'),('OPERATOR', '='),('SEMICOLON', ';'))
    expr2 = extract_between(tokenize("x = a + b; y = (c ? d : e); z = f << 1;"),'=',';')
    expr3 = tokenize('x = cond ? buffer[start:end] : default_value;')
    expr4 = tokenize("concat = {8'h01 , (sys_a)'hAB} ;")
    expr5 = tokenize("nested_ternary = c ? d : array[a[b ? e : f] : g]")
    print ("EPXR1: ", expr1)
    print ("EPXR2: ", expr2)
    print ("EPXR3: ", expr3)
    print ("EPXR4: ", expr4)
    print ("EPXR5: ", expr5)
    
    # Store the tokenized file
    #tokenize_file = tokenize(expr3)
    #TODO look for all Expressions in the tokenize list based by looking at '=' (for start) and ';' (for end)
    expression_list = extract_between(expr3,('OPERATOR', '='),('SEMICOLON', ';'),True)
    #TODO look for ternary
    
    print("EXPR111::",expression_list)
    for expression in expression_list:
        print("EXPR:::::",expression)
        cond = extract_between(expression,('OPERATOR', '='),('TERNARY','?'),False)
        true_expr = extract_between(expression,('TERNARY','?'),('TERNARY_COLON',':'),False)
        false_expr = extract_between(expression,('TERNARY_COLON',':'),('SEMICOLON', ';'),False)
        print("a",true_expr,"b",false_expr)
        print("HI")
    #TODO Look for Brackets
    
    # Example SystemVerilog module
    verilog_code = """
    `define MULTILINE_DEFINE \
        This is a multi-line \
        macro definition with \
        values 1, 2, 3

    `define SINGLE_LINE 42 
    `include "./Cpu.svh"
    `include "Cpummr.svh"
    module test 
    import CpuPkg.sv::*;
    
    # (WIDTH = 32) (
    input clk,
    output logic out
    );
        `include "Cpu2.svh"
        x + y 
        
    endmodule
    """
    # Pre-process: Normalize line continuations (\) for multi-line defines
    normalized_code = re.sub(r'\\\s*\n', ' ', verilog_code)  # Join lines ending with backslash

    define_pattern = r'''
        (`define\s+)                    # Macro directive
        (\w+)                           # Capture macro name (group 1)
        (?:                             # Optional value part:
            \s+                         # Whitespace before value
            (                           # Capture group 2 for value:
                (?:                     # Non-capturing group:
                    (?!\s*(?:`\w+|;|/\*|//|\n|$))  # Negative lookahead for terminators
                    .       # Match any character
                )*                      # Repeat until terminator
            )
        )?                              # Value is optional
        (?=\s*(?:`\w+|;|/\*|//|\n|$))  # Positive lookahead for terminator
    '''
    include_pattern = r'`include\s+"([^"]+)"'

    defines = re.findall(define_pattern,normalized_code,re.VERBOSE | re.DOTALL)
    cleaned_code = re.sub(define_pattern,'',normalized_code,0,re.VERBOSE | re.DOTALL)

    # Compile with re.VERBOSE and re.DOTALL (to handle newlines)
    print("CLEAN_DEFINE:",cleaned_code)
    includes = re.findall(include_pattern, normalized_code,re.VERBOSE | re.DOTALL)
    cleaned_code = re.sub(include_pattern,'',cleaned_code,0,re.VERBOSE | re.DOTALL)
    cleaned_code = re.sub(r'''\r''','',cleaned_code,0,re.VERBOSE | re.DOTALL)
    print("CLEAN:",cleaned_code)
        # Third pass: Parse modules (with multi-line support)
    split_sv_module = r'''
        \s*(?P<MODULE_NAME>(?:module\s+[a-zA-Z_$][\w]*))          # Module declaration
        \s*(?P<IMPORT>(?:import\s+[a-zA-Z_$][\w.]*:{2}.*?;)*) # Imports (optional, multiple)
        \s*(?P<PARAMETERS>\#\s*\(.*?\))?                     # Parameters (optional)
        \s*(?P<PORTS>\(.*?\);)?                              # Ports (optional)
        \s*(?P<REST>.*?)                                       # Module body
        endmodule                                           # Closing "endmodule"
    '''
    
    # Compile with re.VERBOSE | re.DOTALL
    match = re.compile(split_sv_module, re.VERBOSE | re.DOTALL).search(cleaned_code)

    if match:
        print(defines)
        print("Module Name:", match.group("MODULE_NAME"))  # "module my_module"
        print("Imports:", match.group("IMPORT"))          # "import pkg::*;"
        print("Parameters:", match.group("PARAMETERS"))    # "#(parameter WIDTH = 32)"
        print("Ports:", match.group("PORTS"))             # "(input clk, output [WIDTH-1:0] data)"
        print("Body:", match.group("REST"))               # "logic [WIDTH-1:0] counter;"
    
    print("Includes:",includes)
    defines = [' '.join(define_tuple) for define_tuple in defines]
    print("Defines:",defines)
    
    body = match.group("REST")
    ports = match.group("PORTS")
    

    # Example usage:
    '''expression_list1 = extract_between(expression_list[0],('OPERATOR', '='),('SEMICOLON', ';'),False)
    print("expr1L:",expression_list1)
    infix_expr = "a + 42 * (var1 << 2) ** var2"
    tokens = [t[1] for t in expression_list1[0]]
    postfix = shunting_yard(tokens)
    infix = postfix_to_infix_verilog(postfix)

    print(f"Original: {expression_list}")
    print(f"Tokens:   {tokens}")
    print(f"Postfix:  {' '.join(postfix)}")
    print('infix:',infix)'''


test()

def build_expression(tokens):
    """Build expression with proper parentheses using shunting-yard algorithm."""
    output = []
    op_stack = []
    
    for kind, token in tokens:
        if kind in ['NUMBER', 'IDENT']:
            output.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            op_stack.pop()  # Remove '('
        else:  # Operator
            while (op_stack and op_stack[-1] != '(' and
                   (PRECEDENCE[op_stack[-1]] > PRECEDENCE[token] or
                    (PRECEDENCE[op_stack[-1]] == PRECEDENCE[token] and 
                     token not in RIGHT_ASSOC))):
                output.append(op_stack.pop())
            op_stack.append(token)
    
    while op_stack:
        output.append(op_stack.pop())
    
    # Reconstruct expression with minimal parentheses
    expr_stack = []
    for token in output:
        if token in PRECEDENCE:
            right = expr_stack.pop()
            left = expr_stack.pop()
            
            # Check if parentheses are needed
            new_expr = f"{left} {token} {right}"
            if (has_lower_precedence(left, token) or 
                (token in RIGHT_ASSOC and has_lower_precedence(right, token, right_assoc=True))):
                new_expr = f"({new_expr})"
            expr_stack.append(new_expr)
        else:
            expr_stack.append(token)
    
    return expr_stack[0] if expr_stack else ""


def process_file(input_file, output_file):
    """Process entire SystemVerilog file with multi-line expressions"""
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    processed_lines = []
    in_comment = False
    expr_buffer = []
    in_expr = False
    open_parens = 0
    
    for line in lines:
        # Handle block comments
        if '/*' in line:
            in_comment = True
        if '*/' in line:
            in_comment = False
            processed_lines.append(line)
            continue
        if in_comment:
            processed_lines.append(line)
            continue
            
        # Skip single-line comments
        if line.strip().startswith('//'):
            processed_lines.append(line)
            continue
            
        # Check for expression continuations
        stripped = line.strip()
        if not in_expr and '=' in stripped and not stripped.startswith(('assign', '#')):
            # Start of new expression
            lhs, rhs = stripped.split('=', 1)
            expr_buffer = [rhs]
            open_parens = rhs.count('(') - rhs.count(')')
            in_expr = open_parens > 0 or any(op in rhs for op in ['?', ':', '+', '*', '&', '|', '^'])
            if not in_expr:
                try:
                    processed_rhs = parenthesize_expression([rhs])
                    processed_lines.append(f"{lhs}= {processed_rhs};\n")
                except:
                    processed_lines.append(line)
            continue
            
        if in_expr:
            expr_buffer.append(stripped)
            open_parens += stripped.count('(') - stripped.count(')')
            if ';' in stripped and open_parens <= 0:
                # End of expression
                full_expr = ' '.join(expr_buffer)[:-1]  # Remove semicolon
                try:
                    processed_rhs = parenthesize_expression(expr_buffer)
                    processed_lines.append(f"{lhs}= {processed_rhs};\n")
                except:
                    processed_lines.extend(expr_buffer)
                expr_buffer = []
                in_expr = False
            continue
            
        processed_lines.append(line)
    
    with open(output_file, 'w') as f:
        f.writelines(processed_lines)
        
def get_line_efficient(filepath, n):
    with open(filepath) as f:
        for i, line in enumerate(f, 1):  # Start counting at 1
            if i == n:
                return line
    return None 

def read_file(file_path,method): 
    with open(file_path,'r') as f:
        return (
            f.read() if method == r'read' else  # return the entire file as a string
            f.readline() if method == r'readline' else
            f.readlines() if method == r'readlines' else # return a list of all the lines
            None
        )
        
def parentheses_missing_check(report,line):
    report_pattern = r"""
    parentheses_missing.*?Expression\s*'(?P<expression>[^']+)'  # Extract expression inside quotes
    .*?Module\s*'(?P<module>[^']+)'       # Extract module name
    .*?File\s*'(?P<file>[^']+)'           # Extract file path
    .*?Line\s*'(?P<line>\d+)'             # Extract line number
"""

    report = read_file(file,"readlines") # read the full report and store it per line
    
    for i,line in enumerate(f,1): # read the report line by line
        # Use regex to find matches
        match = re.search(report_pattern,line,re.VERBOSE)
        if match:
            expression.append(match.group("expression"))
            module.append(match.group("module"))
            file.append(match.group("file"))
            line.append(match.group("line"))
    
    content = read_file(file,'findline')
    
    line_to_fix = get_line_efficient(file,line)
    
    match = re.search(expression,line_to_fix)
    if match:
        pass
    else:
        print("not the correct line")
        

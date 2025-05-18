def port_grouping(ports):
    token_pattern = [
        ("INPUT", r'input'),
        ("OUTPUT", r'output'),
        ("INOUT", r'inout'),
        ("INTERFACE", r'[\w]+_if'),
        ("STRUCTURE", r'[\w]+_s'),
        ("USER_TYPE", r'[\w]+_t'),
        ("TYPE"), 
    ]
    
import re

def split_sv_file(file_path):
    """
    Splits a SystemVerilog file into logical segments using ';' as a delimiter,
    while respecting procedural blocks (always, initial, task, function).
    
    Args:
        file_path (str): Path to the SystemVerilog file.
    
    Returns:
        list: List of split code segments with preserved block structure.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    # Remove single-line and multi-line comments to avoid false splits
    content = re.sub(r'//.*?\n', '\n', content)  # Single-line
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL|re.MULTILINE)  # Multi-line

    # Split on semicolons, but ignore those inside procedural blocks
    segments = [] # store all the various segments in a list
    current_segment = [] # collate the lines in a segment 
    in_block = False
    pending_block = False 
    has_begin = False
    block_depth = 0 
    generate_block = False
    generate_depth = 0

    for line in content.split('\n'):
        line = line.strip()
        if not line: # if it is an empty line 
            continue

        # Check for procedural block starts (always, initial, task, function)
        procedural_block = re.match(r'\b(always|always_ff|always_comb|always_ff|initial|task|function)\b', line)
        generate_block = re.match(r'\b(generate|endgenerate)\b',line)
        
        # determine when a generate block begins
        if re.match(r'\bgenerate\b',line):
            generate_depth += 1
        # generate block end 
        if re.match(r'\bendgenerate\b',line):
            generate_depth -= 1
            if generate_depth == 0:
                generate_block = False
        
        # Detect 'begin' and 'end' keywords and count the begin and end statements
        if re.match(r'\bbegin\b',line):
            has_begin = True
            block_depth += 1
        if re.match(r'\bend\b',line):
            block_depth -= 1
            if block_depth == 0:
                has_begin = False
            
        # if a procedural or generate sv keyword is found 
        if procedural_block or generate_block:
            if has_begin: # if there is a begin statement 
                in_block = True # we know it will be a block 
            else: # Otherwise, we wait to see the subsequent line
                pending_block = True 
            current_segment.append(line) # append the line to the current_segment
        continue
                
        if pending_block and (has_begin or ';' in line): # if decision is pending, and there is either 'begin' keyword or a ;
            if has_begin: # if there is a begin keyword
                in_block = True # we can be certain we are in a procedural block
            current_segment.append(line) # append the line
            pending_block = False # we dont need this. We now need to look for an 'end' statement
            if not in_block: # Single-line block (no need begin/end)
                if not generate_block: # if this procedural block is not in a generate block
                    segments.append(' '.join(current_segment)) # append it as a segment
                    current_segment = [] # clear the segment
                else: # if it is in a generate
                    current_segment.append(line) # collate it as a segment 
                in_block = False # this procedural block has ended
            continue
                
        if(in_block): # if we are in a procedural block
            if procedural_block == True: # if another procedural block is called, we know this is not valid 
                #TODO better error handling
                print('Error: Procedural statement declared inside another procedural statement.') # call an error
            if block_depth == 0: # if the block depth is 0, we know this procedural block has ended
                in_block = False # we know this is the end of the current procedural block
                if not generate_block: # if it is not in a generate block 
                    segments.append(' '.join(current_segment)) # append it as a segment
                    current_segment = [] # clear current_segment for the subsequent runs
                else: # else if it in a generate block
                    current_segment.append(line) # collate as a "generate" segment 
            else: # else the block has not ended as block depth > 0
                current_segment.append(line) # continue adding lines to the current segment 
            continue
    
        # Case 4: Outside blocks → split on semicolons
        parts = [p.strip() for p in line.split(';') if p.strip()]
        for part in parts:
            segments.append(part)
                
    # Add remaining segments
    if current_segment:
        segments.append(' '.join(current_segment))

    return [s for s in segments if s]  

# Example usage
if __name__ == "__main__":
    sv_file = "example.sv"
    split_code = split_sv_file(sv_file)
    for i, segment in enumerate(split_code, 1):
        print(f"Segment {i}: {segment}")    

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


def body_grouping(body):
    token_pattern = [
        ('COMMENT', r'//.*?$|/\*.*?\*/'),
        ('PAREN', r'[()]'),
        ("2STATE_TYPE",r'bit|byte|shortint|longint|int'),
        ("4STATE_TYPE",r'logic|reg|integer|time'),
        ("NET_TYPE",r'wire|tri|wand|wor|triand|trior|supply0|supply1|'), 
        ('COMP_TYPE',r'struct|union|enum|packed|unpacked\b)'), # Composite Types
        ("TYPEDEF",r'typedef'),
        ("SIG_MOD",r"")
        ("GENERATE",r'generate'),
        ("GENVAR",r'genvar\s+[a-ZA-Z_][/w]+')  # combine the genvar and genvar name
        ("ENDGENERATE",r'endgenerate'),
        ("IF",r'if'),
        ('ELIF',r'else if'),
        ('ELSE'r'else'),
        ("PLI_FUNC",r'$[\w]+(.*?)'),
        ("DELAY",r"#[\w]+"),
        ('ASSIGN', r'assign\s+(\w)+'),
        ("ALWAYS_BLK",r'always_[cfl][afo][a-z]*|always(?!\w)'),
        ('SENS_LIST' r'@\s*\((.*?)\)'),
        ('BEGIN',r'begin\s+'),
        ('END'),r'end\s+',
        ("ENDCASE",r'endcase'),
        ('INSIDE',r'inside'),
        ("SEMICLON",r';'),
        ('STATEMENT'),
        ('SKIP', r'[\s\n]+'),
        ('MISMATCH', r'.')
    ]
    case_depth = 0
    case_cond = False
    case_active = FALSE
    block_depth = 0
    always_block_active = FALSE
    
    if 'begin':
        block_depth += 1
    elif 'end':
        block_depth -= 1
        
    # Start the always block active tag
    if kind == 'ALWAYS' or kind == 'ALWAYS_COMB' or kind == 'ALWAYS_FF' or kind == 'ALWAYS_LATCH':
        always_block_active = TRUE
    # end the always block tag
    elif kind == 'end' and block_depth == 0:
        always_block_active = FALSE
            
    if 'case':
        case_depth += 1
        case_active = True
    elif 'endcase':
        casse_active = FALSE
    elif case_active and kind == "PAREN":
        case_cond = TRUE
    elif case_cond and kind == "PAREN":
        case_cond = FALSE
        
    if case_depth > 1 and kind == "PAREN":
        value = 'PAREN_CASE'
    elif kind == "IDENT":
        value = 'CASE_COND'
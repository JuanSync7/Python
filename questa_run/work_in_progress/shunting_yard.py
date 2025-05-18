import re

class ShuntingYardSystemVerilog:
    def __init__(self):
        # Operator precedence (higher number = higher precedence)
        self.precedence = {
            '(': 21, ')': 21, '[': 21, ']': 21, '{': 21, '}': 21, '::': 21, '.': 21,
            ',': 21,
            '+u': 19, '-u': 19, '!': 19, '~': 19, '&u': 19, '~&': 19, 
            '|u': 19, '~|': 19, '^u': 19, '~^': 19, '^~': 19,
            '**': 18,
            '*': 17, '/': 17, '%': 17,
            '+': 16, '-': 16,
            '<<': 15, '>>': 15, '<<<': 15, '>>>': 15,
            '<': 14, '<=': 14, '>': 14, '>=': 14, 'inside': 14, 'dist': 14,
            '==': 13, '!=': 13, '===': 13, '!==': 13, '==?': 13, '!=?': 13, '=?=' : 13, '!?=' : 13,
            '&': 12,
            '^': 11, '~^': 11, '^~': 11,
            '|': 10,
            '&&': 9,
            '||': 8,
            ':' : 7,
            '?': 7,
            ':=':13, ':/':13
        }
        
        self.right_associative = {'**', '?', ':'}
        self.unary_ops = {'+u', '-u', '!', '~', '&u', '~&', '|u', '~|', '^u', '~^', '^~'}
        self.multi_char_ops = {
            '**', '<<', '>>', '<<<', '>>>', '<=', '>=', '==', '!=', 
            '===', '!==', '==?', '!=?', '~&', '~|', '~^', '^~', '::', '&&', '||', ':=' , ':/', 'inside', 'dist'
        }

        # Numeric literal pattern
        self.num_regex = re.compile(
            r"(?:[0-9]+'[sS]?[bB][01xzXZ_]+)|"      # Binary
            r"(?:[0-9]+'[sS]?[oO][0-7xzXZ_]+)|"     # Octal
            r"(?:[0-9]+'[sS]?[dD][0-9xzXZ_]+)|"     # Decimal
            r"(?:[0-9]+'[sS]?[hH][0-9a-fA-FxzXZ_]+)|" # Hex
            r"(?:[0-9]+)|"                           # Simple decimal
            r"(?:[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)?)|" # Real
            r"(?:'[01xzXZ])"                         # Fill literals
        )

    def is_operand(self, token):
        """Check if token is an operand (identifier, number, etc.)"""
        if not token:
            return False
        if self.num_regex.fullmatch(token):
            return True
        if token == 'inside' or token == 'dist':
            return False
        if token[0].isalpha() or token[0] == '_' or token[0] in {'"', "'"}:
            return True
        if token in {'{', '}', '[', ']'}:
            return False
        return False

    def tokenize(self, expression):
        """Tokenize SystemVerilog expressions"""
        tokens = []
        i = 0
        n = len(expression)
        
        while i < n:
            if expression[i].isspace():
                i += 1
                continue
                
            # Match numeric literals first
            match = self.num_regex.match(expression[i:])
            if match:
                tokens.append(match.group())
                i += match.end()
                continue
                
            # Check for multi-character operators
            found = False
            for op in sorted(self.multi_char_ops, key=len, reverse=True):
                if expression.startswith(op, i):
                    tokens.append(op)
                    i += len(op)
                    found = True
                    break
            if found:
                continue
                
            # Handle single-character tokens
            if expression[i] in {'{', '}', '(', ')', '[', ']', ',', '?', ':', '.'}:
                tokens.append(expression[i])
                i += 1
                continue
                
            # Handle other operators
            if expression[i] in {'+', '-', '*', '/', '%', '!', '~', '&', '|', '^', '<', '>', '='}:
                tokens.append(expression[i])
                i += 1
                continue
                
            # Handle identifiers
            if expression[i].isalpha() or expression[i] == '_':
                j = i
                while j < n and (expression[j].isalnum() or expression[j] in {'_', '$'}):
                    j += 1
                tokens.append(expression[i:j])
                i = j
                continue
                
            # Handle string literals
            if expression[i] in {'"', "'"}:
                quote = expression[i]
                j = i + 1
                while j < n and expression[j] != quote:
                    if expression[j] == '\\':
                        j += 1
                    j += 1
                if j < n:
                    j += 1
                tokens.append(expression[i:j])
                i = j
                continue
                
            tokens.append(expression[i])
            i += 1
            
        return tokens

    def determine_unary(self, tokens, index):
        """Determine if operator is unary"""
        if index >= len(tokens):
            return False
            
        token = tokens[index]
        if token in {'!', '~', '~&', '~|', '~^', '^~'}:
            return True
            
        if token in {'+', '-', '&', '|', '^'}:
            if index == 0:
                return True
            prev = tokens[index-1]
            if prev in {'(', '[', ',', '?', ':', '==', '!=', '===', '!==', '==?', '!=?',
                       '<', '<=', '>', '>=', '&&', '||', '&', '|', '^', '+', '-', '*', 
                       '/', '%', '**', '<<', '>>', '<<<', '>>>'}:
                return True
                
        return False

    def infix_to_postfix(self, expression):
        """Convert infix to postfix notation"""
        tokens = self.tokenize(expression)
        output = []
        operator_stack = []
        in_dist = False
        in_inside = False
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if self.is_operand(token):
                # Check for array indexing
                output.append(token)
                i += 1
            elif token == 'dist':
                operator_stack.append(token)
                if not in_dist and not in_inside:
                    in_dist = True
                else:
                    raise ValueError("inside statement in another inside / distribution statement.")
                i += 1
            elif token == 'inside':
                operator_stack.append(token)
                if not in_inside and not in_dist:
                    in_inside = True
                else:
                    raise ValueError("inside statement in another inside / distribution statement.")
                i += 1
            elif token == '[':
                operator_stack.append(token)
                i += 1
            elif token == ']':
                while operator_stack and operator_stack[-1] != '[':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '[':
                    operator_stack.pop()
                    # Mark this as a array block
                    if in_dist:
                        output.append('[]d')
                    elif in_inside:
                        output.append('[]i')
                    else:
                        output.append('[]')
                else:
                    raise ValueError("Mismatched sqauare braces")
                i += 1
            elif token == '{':
                operator_stack.append(token)
                i += 1
            elif token == '}':
                # Process until we find the matching '{'
                while operator_stack and operator_stack[-1] != '{':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '{':
                    operator_stack.pop()
                    if in_inside:
                        output.append('{}i')
                        in_inside = False
                    elif in_dist:
                        output.append('{}d')
                        in_dist = False
                    else:
                        # Mark this as a concatenation/replication block
                        output.append('{}')
                else:
                    raise ValueError("Mismatched curly braces")
                i += 1
            elif token == ',':
                # Just push to stack, we'll handle during evaluation
                operator_stack.append(token)
                i += 1
            elif token == '(':
                operator_stack.append(token)
                i += 1
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                else:
                    raise ValueError("Mismatched parentheses")
                i += 1
            else:
                is_unary = self.determine_unary(tokens, i)
                op_key = (token + 'u') if (is_unary and token in {'+', '-', '&', '|', '^'}) else token
                
                prec = self.precedence.get(op_key, 0)
                
                while operator_stack and operator_stack[-1] != '(':
                    top_op = operator_stack[-1]
                    if top_op == '{' or '[':
                        break
                    top_prec = self.precedence.get(top_op, 0)
                    
                    if (op_key in self.right_associative and prec < top_prec) or \
                       (op_key not in self.right_associative and prec <= top_prec):
                        output.append(operator_stack.pop())
                    else:
                        break
                        
                operator_stack.append(op_key if op_key in self.unary_ops else token)
                i += 1
        
        while operator_stack:
            op = operator_stack.pop()
            if op in {'(', '{'}:
                raise ValueError("Mismatched brackets")
            output.append(op)
            
        return output

    def evaluate_postfix(self, postfix):
        """Evaluate postfix notation"""
        stack = []
        in_concat = False
        in_replication = False

        for token in postfix:
            if self.is_operand(token):
                stack.append(token)
            elif token == '[]d' or token == '[]i':
                operand = stack.pop()
                stack.append(f'[{operand}]')
            elif token == '[]':
                if len(stack) < 2:
                    raise ValueError("Not enough operands for array indexing")
                index = stack.pop()
                array = stack.pop()
                stack.append(f"{array}[{index}]")
            elif token == '{}i':
                operand = stack.pop()
                stack.append(f"{{ {operand} }}")
            elif token == '{}d':
                operand = stack.pop()
                stack.append(f"{{ {operand} }}")
            elif token == '{}':
                if (in_concat):
                    operand = stack.pop()
                    stack.append(f'{{{operand}}}')
                    in_concat = False
                elif in_replication:
                    operand = stack.pop()
                    stack.append(f"{{{operand}}}")
                    in_replication = False
                else:
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(f"{left}{{{right}}}")
                    in_replication = True
            elif token == ',':
                right = stack.pop()
                left = stack.pop()
                stack.append(f'{left} , {right}')
                in_concat = True
            elif token in self.unary_ops:
                if not stack:
                    raise ValueError(f"Missing operand for unary operator {token}")
                operand = stack.pop()
                op = token[:-1] if token.endswith('u') else token
                stack.append(f"({op}{operand})")
            elif token == "inside" or token == 'dist':
                right = stack.pop()
                left = stack.pop()
                stack.append(f"({left} {token} {right})")
            elif token == ":":
                right = stack.pop()
                left = stack.pop()
                stack.append(f"{left}{token}{right}")
            else:
                if len(stack) < 2:
                    raise ValueError(f"Not enough operands for operator {token}")
                right = stack.pop()
                left = stack.pop()
                stack.append(f"({left}{token}{right})")
        
        if len(stack) != 1:
            print(stack)
            raise ValueError("Invalid expression")
            
        return stack[0]


# Test cases
if __name__ == "__main__":
    sh = ShuntingYardSystemVerilog()
    
    test_cases = [
        "a + b * c  /d ",
        "{8, 1, 3, 4 , 7}",
        "{16{0}}",
        "data[{addr, offset}]",
        "!a & {b, c} | d",
        "8'b0 + {4'd15, 4'd0}",
        "{DW{1'b1}} & mask",
        "({a, b} << 1) + 1",
        "{{a, b}, {c, d}}",
        "e inside { [3:7] }",
        "a ? b: c ? d:e",
        "data[DW-1: AXI? 3+1:0]",
        "multi_dim [3-1][2]",
        "( b * ( a - 1))",
        "addr dist { 2 := 5, [10:12] := 8 }"
    ]
    
    for expr in test_cases:
        print(f"\nInfix expression: {expr}")
        try:
            postfix = sh.infix_to_postfix(expr)
            print(f"Postfix (RPN): {' '.join(postfix)}")
            
            try:
                eval_expr = sh.evaluate_postfix(postfix)
                print(f"Evaluated form: {eval_expr}")
            except ValueError as e:
                print(f"Evaluation error: {e}")
        except ValueError as e:
            print(f"Error in conversion: {e}")
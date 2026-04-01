import re

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line})"

KEYWORDS = {
    "if", "elif", "else", "while", "for", "in", "fn", "return",
    "and", "or", "not", "class", "try", "catch", "true", "false",
    "import", "from", "say", "as"
}

TOKEN_REGEX = [
    ("COMMENT", r'#.*'),
    ("STRING", r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
    ("NUMBER", r'\d+(\.\d+)?'),
    ("IDENTIFIER", r'[a-zA-Z_]\w*'),
    ("OPERATOR", r'==|!=|>=|<=|=>|>|<|\+|-|\*|/|%|='),
    ("PUNCT", r'\(|\)|\[|\]|\{|\}|:|,|\.'),
    ("WHITESPACE", r'[ \t]+'),
    ("NEWLINE", r'\n'),
    ("MISMATCH", r'.')
]

def lex(code):
    tokens = []
    line_num = 1
    
    indent_stack = [0]
    nest_level = 0
    
    lines = code.split('\n')
    
    for line_idx, raw_line in enumerate(lines):
        line_num = line_idx + 1
        
        stripped = raw_line.lstrip(' \t')
        if not stripped or stripped.startswith('#'):
            continue
            
        indent_len = len(raw_line) - len(stripped)
        
        if nest_level == 0:
            if indent_len > indent_stack[-1]:
                indent_stack.append(indent_len)
                tokens.append(Token("INDENT", "INDENT", line_num, 0))
            elif indent_len < indent_stack[-1]:
                while len(indent_stack) > 1 and indent_stack[-1] > indent_len:
                    indent_stack.pop()
                    tokens.append(Token("DEDENT", "DEDENT", line_num, 0))
                if indent_stack[-1] != indent_len:
                    raise SyntaxError(f"Indentation error on line {line_num}")
                
        pos = 0
        while pos < len(stripped):
            match = None
            for token_def in TOKEN_REGEX:
                pattern = token_def[1]
                regex = re.compile(pattern)
                match = regex.match(stripped, pos)
                if match:
                    type_ = token_def[0]
                    value = match.group(0)
                    if type_ == "MISMATCH":
                        raise SyntaxError(f"Unexpected character '{value}' on line {line_num}")
                    if type_ != "WHITESPACE" and type_ != "COMMENT":
                        if type_ == "PUNCT":
                            if value in '([{': nest_level += 1
                            elif value in ')]}': nest_level -= 1
                            
                        if type_ == "IDENTIFIER" and value in KEYWORDS:
                            type_ = "KEYWORD"
                        if type_ == "STRING":
                            value = value[1:-1]
                        if type_ == "NUMBER":
                            value = float(value) if "." in value else int(value)
                            
                        tokens.append(Token(type_, value, line_num, pos + indent_len))
                    break
            
            if not match:
                raise SyntaxError(f"Lexer failed at line {line_num}, col {pos}")
            else:
                pos = match.end()
                
        if nest_level == 0:
            tokens.append(Token("NEWLINE", "\n", line_num, len(raw_line)))
            
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "DEDENT", line_num + 1, 0))
        
    tokens.append(Token("EOF", "EOF", line_num + 1, 0))
    
    # Clean up empty newlines sequences
    cleaned_tokens = []
    for t in tokens:
        if t.type == "NEWLINE" and cleaned_tokens and cleaned_tokens[-1].type == "NEWLINE":
            continue
        cleaned_tokens.append(t)
        
    return cleaned_tokens

if __name__ == "__main__":
    code = '''
if x > 10:
    say "big"
elif x == 10:
    say "exact"
else:
    say "small"
'''
    for t in lex(code):
        print(t)

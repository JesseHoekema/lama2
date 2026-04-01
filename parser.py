class AST: pass

class Program(AST):
    def __init__(self, statements): self.statements = statements

class Number(AST):
    def __init__(self, value): self.value = value

class String(AST):
    def __init__(self, value): self.value = value

class Boolean(AST):
    def __init__(self, value): self.value = value

class Identifier(AST):
    def __init__(self, name): self.name = name

class ListExpr(AST):
    def __init__(self, elements): self.elements = elements

class DictExpr(AST):
    def __init__(self, pairs): self.pairs = pairs

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left; self.op = op; self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op; self.expr = expr

class Assign(AST):
    def __init__(self, target, value):
        self.target = target; self.value = value

class MemberAssign(AST):
    def __init__(self, obj, prop, value):
        self.obj = obj; self.prop = prop; self.value = value

class IndexAssign(AST):
    def __init__(self, obj, index, value):
        self.obj = obj; self.index = index; self.value = value

class Say(AST):
    def __init__(self, expr): self.expr = expr

class If(AST):
    def __init__(self, condition, body, elifs, else_body):
        self.condition = condition; self.body = body; self.elifs = elifs; self.else_body = else_body

class While(AST):
    def __init__(self, condition, body):
        self.condition = condition; self.body = body

class ForRange(AST):
    def __init__(self, var, start, end, body):
        self.var = var; self.start = start; self.end = end; self.body = body

class ForIn(AST):
    def __init__(self, var, iterable, body):
        self.var = var; self.iterable = iterable; self.body = body

class FunctionDef(AST):
    def __init__(self, name, params, body):
        self.name = name; self.params = params; self.body = body

class ClassDef(AST):
    def __init__(self, name, methods):
        self.name = name; self.methods = methods

class MethodCall(AST):
    def __init__(self, obj, method, args):
        self.obj = obj; self.method = method; self.args = args

class MemberAccess(AST):
    def __init__(self, obj, prop):
        self.obj = obj; self.prop = prop

class IndexAccess(AST):
    def __init__(self, obj, index):
        self.obj = obj; self.index = index

class Call(AST):
    def __init__(self, func, args):
        self.func = func; self.args = args

class Return(AST):
    def __init__(self, expr): self.expr = expr

class TryCatch(AST):
    def __init__(self, try_body, catch_var, catch_body):
        self.try_body = try_body; self.catch_var = catch_var; self.catch_body = catch_body

class Import(AST):
    def __init__(self, module, alias=None):
        self.module = module; self.alias = alias

class FromImport(AST):
    def __init__(self, module, name, alias=None):
        self.module = module; self.name = name; self.alias = alias

class ExprStmt(AST):
    def __init__(self, expr): self.expr = expr

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def match(self, type_, value=None):
        curr = self.current()
        if curr and curr.type == type_ and (value is None or curr.value == value):
            self.pos += 1
            return curr
        return None

    def expect(self, type_, value=None):
        curr = self.match(type_, value)
        if not curr:
            raise SyntaxError(f"Expected {type_} {value if value else ''}, got {self.current().type if self.current() else 'EOF'}")
        return curr

    def consume_newlines(self):
        while self.match("NEWLINE"):
            pass

    def parse(self):
        statements = []
        self.consume_newlines()
        while self.current() and self.current().type != "EOF":
            statements.append(self.parse_statement())
            self.consume_newlines()
        return Program(statements)

    def parse_block(self):
        self.expect("INDENT")
        statements = []
        self.consume_newlines()
        while self.current() and self.current().type != "DEDENT":
            statements.append(self.parse_statement())
            self.consume_newlines()
        self.expect("DEDENT")
        return statements

    def parse_statement(self):
        curr = self.current()
        if curr.type == "KEYWORD":
            if curr.value == "say":
                return self.parse_say()
            elif curr.value == "if":
                return self.parse_if()
            elif curr.value == "while":
                return self.parse_while()
            elif curr.value == "for":
                return self.parse_for()
            elif curr.value == "fn":
                return self.parse_function()
            elif curr.value == "class":
                return self.parse_class()
            elif curr.value == "return":
                return self.parse_return()
            elif curr.value == "try":
                return self.parse_try()
            elif curr.value == "import":
                return self.parse_import()
            elif curr.value == "from":
                return self.parse_from_import()

        # Assignment or Expression Statement
        expr = self.parse_expression()
        
        # Check if it's an assignment
        if self.match("OPERATOR", "="):
            val = self.parse_expression()
            self.expect("NEWLINE")
            if isinstance(expr, Identifier):
                return Assign(expr.name, val)
            elif isinstance(expr, MemberAccess):
                return MemberAssign(expr.obj, expr.prop, val)
            elif isinstance(expr, IndexAccess):
                return IndexAssign(expr.obj, expr.index, val)
            else:
                raise SyntaxError("Invalid assignment target")
        
        self.expect("NEWLINE")
        return ExprStmt(expr)

    def parse_say(self):
        self.expect("KEYWORD", "say")
        expr = self.parse_expression()
        self.expect("NEWLINE")
        return Say(expr)

    def parse_if(self):
        self.expect("KEYWORD", "if")
        condition = self.parse_expression()
        self.expect("PUNCT", ":")
        self.expect("NEWLINE")
        body = self.parse_block()
        
        elifs = []
        self.consume_newlines()
        while self.match("KEYWORD", "elif"):
            elif_cond = self.parse_expression()
            self.expect("PUNCT", ":")
            self.expect("NEWLINE")
            elif_body = self.parse_block()
            elifs.append((elif_cond, elif_body))
            self.consume_newlines()
            
        else_body = None
        if self.match("KEYWORD", "else"):
            self.expect("PUNCT", ":")
            self.expect("NEWLINE")
            else_body = self.parse_block()
            
        return If(condition, body, elifs, else_body)

    def parse_while(self):
        self.expect("KEYWORD", "while")
        condition = self.parse_expression()
        self.expect("PUNCT", ":")
        self.expect("NEWLINE")
        body = self.parse_block()
        return While(condition, body)

    def parse_for(self):
        self.expect("KEYWORD", "for")
        var_name = self.expect("IDENTIFIER").value
        self.expect("KEYWORD", "in")
        
        if self.match("IDENTIFIER", "range"):
            self.expect("PUNCT", "(")
            start = self.parse_expression()
            self.expect("PUNCT", ",")
            end = self.parse_expression()
            self.expect("PUNCT", ")")
            self.expect("PUNCT", ":")
            self.expect("NEWLINE")
            body = self.parse_block()
            return ForRange(var_name, start, end, body)
        else:
            iterable = self.parse_expression()
            self.expect("PUNCT", ":")
            self.expect("NEWLINE")
            body = self.parse_block()
            return ForIn(var_name, iterable, body)

    def parse_function(self):
        self.expect("KEYWORD", "fn")
        name = self.expect("IDENTIFIER").value
        self.expect("PUNCT", "(")
        params = []
        if not self.match("PUNCT", ")"):
            params.append(self.expect("IDENTIFIER").value)
            while self.match("PUNCT", ","):
                params.append(self.expect("IDENTIFIER").value)
            self.expect("PUNCT", ")")
        self.expect("PUNCT", ":")
        self.expect("NEWLINE")
        body = self.parse_block()
        return FunctionDef(name, params, body)

    def parse_class(self):
        self.expect("KEYWORD", "class")
        name = self.expect("IDENTIFIER").value
        self.expect("PUNCT", ":")
        self.expect("NEWLINE")
        self.expect("INDENT")
        methods = []
        self.consume_newlines()
        while self.current() and self.current().type != "DEDENT":
            if self.current().type == "KEYWORD" and self.current().value == "fn":
                methods.append(self.parse_function())
            else:
                self.pos += 1 # Consume invalid line
            self.consume_newlines()
        self.expect("DEDENT")
        return ClassDef(name, methods)

    def parse_return(self):
        self.expect("KEYWORD", "return")
        expr = self.parse_expression()
        self.expect("NEWLINE")
        return Return(expr)

    def parse_try(self):
        self.expect("KEYWORD", "try")
        self.expect("PUNCT", ":")
        self.expect("NEWLINE")
        try_body = self.parse_block()
        self.consume_newlines()
        self.expect("KEYWORD", "catch")
        catch_var = self.expect("IDENTIFIER").value
        self.expect("PUNCT", ":")
        self.expect("NEWLINE")
        catch_body = self.parse_block()
        return TryCatch(try_body, catch_var, catch_body)

    def parse_import(self):
        self.expect("KEYWORD", "import")
        
        # Support both identifier and string for module name
        curr = self.current()
        if curr.type == "STRING":
            mod = self.expect("STRING").value
        else:
            mod = self.expect("IDENTIFIER").value
            
        alias = None
        if self.match("KEYWORD", "as"):
            alias = self.expect("IDENTIFIER").value
            
        self.expect("NEWLINE")
        return Import(mod, alias)

    def parse_from_import(self):
        self.expect("KEYWORD", "from")
        
        curr = self.current()
        if curr.type == "STRING":
            mod = self.expect("STRING").value
        else:
            mod = self.expect("IDENTIFIER").value
            
        self.expect("KEYWORD", "import")
        name = self.expect("IDENTIFIER").value
        
        alias = None
        if self.match("KEYWORD", "as"):
            alias = self.expect("IDENTIFIER").value
            
        self.expect("NEWLINE")
        return FromImport(mod, name, alias)

    def parse_expression(self):
        return self.parse_logic_or()

    def parse_logic_or(self):
        left = self.parse_logic_and()
        while self.match("KEYWORD", "or"):
            right = self.parse_logic_and()
            left = BinOp(left, "or", right)
        return left

    def parse_logic_and(self):
        left = self.parse_equality()
        while self.match("KEYWORD", "and"):
            right = self.parse_equality()
            left = BinOp(left, "and", right)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while True:
            op = self.current()
            if op and op.type == "OPERATOR" and op.value in ("==", "!="):
                self.pos += 1
                right = self.parse_comparison()
                left = BinOp(left, op.value, right)
            else:
                break
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while True:
            op = self.current()
            if op and op.type == "OPERATOR" and op.value in (">", "<", ">=", "<="):
                self.pos += 1
                right = self.parse_term()
                left = BinOp(left, op.value, right)
            else:
                break
        return left

    def parse_term(self):
        left = self.parse_factor()
        while True:
            op = self.current()
            if op and op.type == "OPERATOR" and op.value in ("+", "-"):
                self.pos += 1
                right = self.parse_factor()
                left = BinOp(left, op.value, right)
            else:
                break
        return left
        
    def parse_factor(self):
        left = self.parse_unary()
        while True:
            op = self.current()
            if op and op.type == "OPERATOR" and op.value in ("*", "/", "%"):
                self.pos += 1
                right = self.parse_unary()
                left = BinOp(left, op.value, right)
            else:
                break
        return left

    def parse_unary(self):
        op = self.current()
        if op and (op.type == "OPERATOR" and op.value == "-") or (op.type == "KEYWORD" and op.value == "not"):
            self.pos += 1
            return UnaryOp(op.value, self.parse_unary())
        return self.parse_call_member()

    def parse_call_member(self):
        expr = self.parse_primary()
        
        while True:
            if self.match("PUNCT", "."):
                prop = self.expect("IDENTIFIER").value
                
                # Check if it's a method call
                if self.match("PUNCT", "("):
                    args = []
                    if not self.match("PUNCT", ")"):
                        args.append(self.parse_expression())
                        while self.match("PUNCT", ","):
                            args.append(self.parse_expression())
                        self.expect("PUNCT", ")")
                    expr = MethodCall(expr, prop, args)
                else:
                    expr = MemberAccess(expr, prop)
                    
            elif self.match("PUNCT", "["):
                index = self.parse_expression()
                self.expect("PUNCT", "]")
                expr = IndexAccess(expr, index)
                
            elif self.match("PUNCT", "("):
                args = []
                if not self.match("PUNCT", ")"):
                    args.append(self.parse_expression())
                    while self.match("PUNCT", ","):
                        args.append(self.parse_expression())
                    self.expect("PUNCT", ")")
                expr = Call(expr, args)
            else:
                break
                
        return expr

    def parse_primary(self):
        curr = self.current()
        if curr.type == "NUMBER":
            self.pos += 1
            return Number(curr.value)
        elif curr.type == "STRING":
            self.pos += 1
            return String(curr.value)
        elif curr.type == "KEYWORD" and curr.value == "true":
            self.pos += 1
            return Boolean(True)
        elif curr.type == "KEYWORD" and curr.value == "false":
            self.pos += 1
            return Boolean(False)
        elif curr.type == "IDENTIFIER":
            self.pos += 1
            return Identifier(curr.value)
        elif self.match("PUNCT", "("):
            expr = self.parse_expression()
            self.expect("PUNCT", ")")
            return expr
        elif self.match("PUNCT", "["):
            items = []
            if not self.match("PUNCT", "]"):
                items.append(self.parse_expression())
                while self.match("PUNCT", ","):
                    items.append(self.parse_expression())
                self.expect("PUNCT", "]")
            return ListExpr(items)
        elif self.match("PUNCT", "{"):
            pairs = []
            if not self.match("PUNCT", "}"):
                self.consume_newlines()
                while not self.match("PUNCT", "}"):
                    key = self.parse_expression()
                    if not isinstance(key, String):
                        raise SyntaxError("Dictionary keys must be strings")
                    self.expect("PUNCT", ":")
                    val = self.parse_expression()
                    pairs.append((key.value, val))
                    if not self.match("PUNCT", ","):
                        self.consume_newlines()
                        if self.match("PUNCT", "}"):
                            break
                    self.consume_newlines()
            return DictExpr(pairs)

        raise SyntaxError(f"Unexpected token {curr.type} '{curr.value}' in expression")

if __name__ == "__main__":
    from lexer import lex
    code = '''
user = {
    "name": "Jesse",
    "age": 15
}
say user["name"]
'''
    tokens = lex(code)
    parser = Parser(tokens)
    ast = parser.parse()
    print("Parsed successfully!", ast)

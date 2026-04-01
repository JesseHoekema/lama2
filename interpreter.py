from parser import *

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception): pass
class ContinueException(Exception): pass
class LamaError(Exception):
    def __init__(self, message):
        self.message = message

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise LamaError(f"Undefined variable '{name}'")

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        # If not found, define it in the global scope (or current scope if top level)
        self.define(name, value)


class LamaFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, args):
        env = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            if i < len(args):
                env.define(param, args[i])
            else:
                env.define(param, None)
                
        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnException as r:
            return r.value
        return None

    def bind(self, instance):
        return BoundMethod(instance, self)


class LamaClass:
    def __init__(self, name, methods, superclass=None):
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def call(self, interpreter, args):
        instance = LamaInstance(self)
        if "init" in self.methods:
            initializer = self.methods["init"].bind(instance)
            initializer.call(interpreter, args)
        return instance

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None


class LamaInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
            
        method = self.klass.find_method(name)
        if method is not None:
            return method.bind(self)
            
        raise LamaError(f"Undefined property '{name}' on instance of {self.klass.name}")

    def set(self, name, value):
        self.fields[name] = value


class BoundMethod:
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method

    def call(self, interpreter, args):
        env = Environment(self.method.closure)
        env.define("self", self.instance)
        for i, param in enumerate(self.method.declaration.params[1:]): # skip self
            if i < len(args):
                env.define(param, args[i])
            else:
                env.define(param, None)
                
        try:
            interpreter.execute_block(self.method.declaration.body, env)
        except ReturnException as r:
            return r.value
        return None

class Interpreter:
    def __init__(self, globals_env):
        self.globals = globals_env
        self.environment = self.globals

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except Exception as e:
            print(f"Error: {e}")

    def execute(self, stmt):
        method_name = f'visit_{type(stmt).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(stmt)

    def evaluate(self, expr):
        method_name = f'visit_{type(expr).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(expr)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    def execute_block(self, statements, env):
        previous = self.environment
        try:
            self.environment = env
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    # Statement Visitors
    def visit_ExprStmt(self, stmt):
        self.evaluate(stmt.expr)

    def visit_Say(self, stmt):
        value = self.evaluate(stmt.expr)
        if hasattr(value, '__str__'):
            print(str(value)) # String representation
        else:
            print(value)

    def visit_Assign(self, stmt):
        value = self.evaluate(stmt.value)
        self.environment.assign(stmt.target, value)

    def visit_MemberAssign(self, stmt):
        obj = self.evaluate(stmt.obj)
        value = self.evaluate(stmt.value)
        if isinstance(obj, LamaInstance):
            obj.set(stmt.prop, value)
        else:
            raise LamaError(f"Only object instances have properties")

    def visit_IndexAssign(self, stmt):
        obj = self.evaluate(stmt.obj)
        index = self.evaluate(stmt.index)
        value = self.evaluate(stmt.value)
        if isinstance(obj, list) or isinstance(obj, dict):
            obj[index] = value
        else:
            raise LamaError(f"Cannot index into {type(obj)}")

    def visit_If(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute_block(stmt.body, Environment(self.environment))
            return
            
        for elif_cond, elif_body in stmt.elifs:
            if self.is_truthy(self.evaluate(elif_cond)):
                self.execute_block(elif_body, Environment(self.environment))
                return
                
        if stmt.else_body:
            self.execute_block(stmt.else_body, Environment(self.environment))

    def visit_While(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            try:
                self.execute_block(stmt.body, Environment(self.environment))
            except BreakException:
                break
            except ContinueException:
                continue

    def visit_ForRange(self, stmt):
        start = self.evaluate(stmt.start)
        end = self.evaluate(stmt.end)
        for i in range(start, end):
            env = Environment(self.environment)
            env.define(stmt.var, i)
            try:
                self.execute_block(stmt.body, env)
            except BreakException:
                break
            except ContinueException:
                continue

    def visit_ForIn(self, stmt):
        iterable = self.evaluate(stmt.iterable)
        for item in iterable:
            env = Environment(self.environment)
            env.define(stmt.var, item)
            try:
                self.execute_block(stmt.body, env)
            except BreakException:
                break
            except ContinueException:
                continue

    def visit_FunctionDef(self, stmt):
        func = LamaFunction(stmt, self.environment)
        self.environment.define(stmt.name, func)

    def visit_ClassDef(self, stmt):
        self.environment.define(stmt.name, None)
        methods = {}
        for method in stmt.methods:
            func = LamaFunction(method, self.environment)
            methods[method.name] = func
            
        klass = LamaClass(stmt.name, methods)
        self.environment.assign(stmt.name, klass)

    def visit_Return(self, stmt):
        value = None
        if stmt.expr:
            value = self.evaluate(stmt.expr)
        raise ReturnException(value)

    def visit_TryCatch(self, stmt):
        try:
            self.execute_block(stmt.try_body, Environment(self.environment))
        except BaseException as e:
            # We catch also Python exceptions to bubble up as Lama exceptions
            error_msg = str(e)
            if isinstance(e, LamaError):
                error_msg = e.message
            elif isinstance(e, ReturnException):
                raise e # don't catch returns
                
            env = Environment(self.environment)
            env.define(stmt.catch_var, error_msg)
            self.execute_block(stmt.catch_body, env)

    def visit_Import(self, stmt):
        import builtins_lama
        import os
        # Use alias if provided, otherwise the module name
        name_to_define = stmt.alias if stmt.alias else stmt.module
        
        # 1. Check modules/ folder for a .lama file
        mod_path = os.path.join("modules", f"{stmt.module}.lama")
        if os.path.exists(mod_path):
            mod_env = self._load_lama_module(stmt.module, mod_path)
            self.environment.define(name_to_define, mod_env)
            return
        # 2. Fall back to built-in stdlib
        mod_env = builtins_lama.load_module(stmt.module)
        if mod_env:
            self.environment.define(name_to_define, mod_env)
        else:
            raise LamaError(f"Module '{stmt.module}' not found. Run: lama install {stmt.module}")

    def visit_FromImport(self, stmt):
        import builtins_lama
        import os
        # Use alias if provided, otherwise the member name
        name_to_define = stmt.alias if stmt.alias else stmt.name
        
        # 1. Check modules/ folder
        mod_path = os.path.join("modules", f"{stmt.module}.lama")
        if os.path.exists(mod_path):
            mod_env = self._load_lama_module(stmt.module, mod_path)
            if stmt.name in mod_env:
                self.environment.define(name_to_define, mod_env[stmt.name])
                return
            raise LamaError(f"Name '{stmt.name}' not found in module '{stmt.module}'")
        # 2. Fall back to built-in stdlib
        mod_env = builtins_lama.load_module(stmt.module)
        if mod_env and stmt.name in mod_env:
            self.environment.define(name_to_define, mod_env[stmt.name])
        else:
            raise LamaError(f"Name '{stmt.name}' not found in module '{stmt.module}'")

    def _load_lama_module(self, name, path):
        """Executes a .lama module file and returns its exported environment as a dict."""
        from lexer import lex
        from parser import Parser
        from builtins_lama import get_globals
        with open(path, 'r') as f:
            code = f.read()
        tokens = lex(code)
        ast = Parser(tokens).parse()
        mod_interp = Interpreter(get_globals())
        mod_interp.interpret(ast.statements)
        # Return all top-level names defined in the module
        return dict(mod_interp.globals.values)

    # Expression Visitors
    def visit_Number(self, expr): return expr.value
    def visit_String(self, expr):
        val = expr.value
        # Very simple string interpolation for {name}
        if "{" in val and "}" in val:
            import re
            def replace_var(match):
                var_name = match.group(1)
                try:
                    return str(self.environment.get(var_name))
                except LamaError:
                    return "undefined"
            val = re.sub(r'\{([a-zA-Z_]\w*)\}', replace_var, val)
        return val
        
    def visit_Boolean(self, expr): return expr.value
    
    def visit_Identifier(self, expr):
        return self.environment.get(expr.name)
        
    def visit_ListExpr(self, expr):
        return [self.evaluate(e) for e in expr.elements]
        
    def visit_DictExpr(self, expr):
        return {k: self.evaluate(v) for k, v in expr.pairs}

    def visit_BinOp(self, expr):
        left = self.evaluate(expr.left)
        
        # Short circuit logic
        if expr.op == "and": return self.is_truthy(left) and self.is_truthy(self.evaluate(expr.right))
        if expr.op == "or": return self.is_truthy(left) or self.is_truthy(self.evaluate(expr.right))
            
        right = self.evaluate(expr.right)
        
        if expr.op == "+": return left + right
        if expr.op == "-": return left - right
        if expr.op == "*": return left * right
        if expr.op == "/": return left / right
        if expr.op == "%": return left % right
        if expr.op == "==": return left == right
        if expr.op == "!=": return left != right
        if expr.op == ">": return left > right
        if expr.op == "<": return left < right
        if expr.op == ">=": return left >= right
        if expr.op == "<=": return left <= right

    def visit_UnaryOp(self, expr):
        right = self.evaluate(expr.expr)
        if expr.op == "-": return -right
        if expr.op == "not": return not self.is_truthy(right)

    def visit_MemberAccess(self, expr):
        obj = self.evaluate(expr.obj)
        if isinstance(obj, LamaInstance):
            return obj.get(expr.prop)
        elif isinstance(obj, dict) and expr.prop in obj:
            return obj[expr.prop]
        raise LamaError(f"Cannot access property '{expr.prop}'")

    def visit_IndexAccess(self, expr):
        obj = self.evaluate(expr.obj)
        index = self.evaluate(expr.index)
        try:
            return obj[index]
        except (KeyError, IndexError):
            raise LamaError(f"Index out of bounds or key not found: {index}")

    def visit_Call(self, expr):
        callee = self.evaluate(expr.func)
        args = [self.evaluate(arg) for arg in expr.args]
        
        if hasattr(callee, 'call'):
            return callee.call(self, args)
        elif callable(callee):
            # Native python functions
            return callee(*args)
        raise LamaError("Can only call functions and classes")

    def visit_MethodCall(self, expr):
        obj = self.evaluate(expr.obj)
        args = [self.evaluate(arg) for arg in expr.args]
        
        if isinstance(obj, LamaInstance):
            method = obj.get(expr.method)
            return method.call(self, args)
            
        if isinstance(obj, dict) and expr.method in obj:
            method = obj[expr.method]
            if hasattr(method, 'call'):
                return method.call(self, args)
            elif callable(method):
                return method(*args)
        
        # Handle LamaFile and other objects with get()
        if hasattr(obj, 'get') and callable(getattr(obj, 'get')) and not isinstance(obj, dict):
            try:
                method = obj.get(expr.method)
                if hasattr(method, 'call'):
                    return method.call(self, args)
            except:
                pass
                
        # Handle native list/string methods
        if isinstance(obj, list):
            if expr.method == "append": obj.append(args[0]); return None
            if expr.method == "remove": obj.remove(args[0]); return None
            
        if isinstance(obj, str):
            if expr.method == "upper": return obj.upper()
            if expr.method == "lower": return obj.lower()
            if expr.method == "split": return obj.split()
            
        raise LamaError(f"Method '{expr.method}' not found on object")

    def is_truthy(self, value):
        if value is None: return False
        if isinstance(value, bool): return value
        if isinstance(value, (int, float)): return value != 0
        if isinstance(value, (str, list, dict)): return len(value) > 0
        return True

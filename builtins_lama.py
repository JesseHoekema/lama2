import math as pymath
import time as pytime
import random as pyrandom

# Standard Library Implementation for LAMA Language

class LamaNativeFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        
    def call(self, interpreter, args):
        return self.func(*args)
        
    def __str__(self):
        return f"<native fn {self.name}>"


def create_math_module():
    env = {}
    env["add"] = LamaNativeFunction("math.add", lambda a, b: a + b)
    env["sub"] = LamaNativeFunction("math.sub", lambda a, b: a - b)
    env["random"] = LamaNativeFunction("math.random", lambda: pyrandom.random())
    env["pi"] = pymath.pi
    return env

def create_time_module():
    env = {}
    env["now"] = LamaNativeFunction("time.now", lambda: pytime.time())
    env["sleep"] = LamaNativeFunction("time.sleep", lambda ms: pytime.sleep(ms / 1000.0))
    return env

def create_string_module():
    env = {}
    env["upper"] = LamaNativeFunction("string.upper", lambda s: str(s).upper())
    env["lower"] = LamaNativeFunction("string.lower", lambda s: str(s).lower())
    env["split"] = LamaNativeFunction("string.split", lambda s, sep=None: str(s).split(sep))
    return env

class LamaFile:
    def __init__(self, path, mode):
        self.file = open(path, mode)
        
    def get(self, prop):
        if prop == "read": return LamaNativeFunction("read", lambda: self.file.read())
        if prop == "write": return LamaNativeFunction("write", lambda s: self.file.write(str(s)))
        if prop == "close": return LamaNativeFunction("close", lambda: self.file.close())
        raise Exception(f"File object has no property '{prop}'")


def get_globals():
    from interpreter import Environment
    
    env = Environment()
    
    # Built in globals like true, false, open
    env.define("open", LamaNativeFunction("open", lambda path, mode="r": LamaFile(path, mode)))
    env.define("print", LamaNativeFunction("print", lambda *args: print(*args)))
    env.define("str", LamaNativeFunction("str", lambda x: str(x)))
    env.define("int", LamaNativeFunction("int", lambda x: int(x)))
    env.define("float", LamaNativeFunction("float", lambda x: float(x)))
    env.define("len", LamaNativeFunction("len", lambda x: len(x)))
    
    return env

def load_module(name):
    if name == "math": return create_math_module()
    if name == "time": return create_time_module()
    if name == "string": return create_string_module()
    return None

import token as T
from collections import OrderedDict
from stack import Stack
from parsing import Tokenizing
from parsing.parsing import *

   
####
# AST
####

def is_operator(ast, key):
    return key.ttype == T.OP or key.tval == "call"

def call_operator(ast, item, inputs, outputs):
    operator = item.tval
#    print "Calling operator:", item, inputs, outputs 
    # 0 arg operators

    # 1 arg operators
    a = inputs.pop()


    if operator == "?":
        if not a.tval:
            outputs.pop() # Remove the following operator
        return
    elif operator == "call":
        print ""
        call_function(ast, a, inputs, outputs)    
        return
    # 2 arg operators
    b = inputs.pop()
    if operator == "-":
        outputs.push(Tokenizing.Token(T.NUMBER, b.tval - a.tval, 0, 0, 0))
    elif operator == "+":
        outputs.push(Tokenizing.Token(T.NUMBER, b.tval + a.tval, 0, 0, 0))
    elif operator == "*":
        outputs.push(Tokenizing.Token(T.NUMBER, b.tval * a.tval, 0, 0, 0))
    elif operator == "=":
        outputs.push(Tokenizing.Token(T.NUMBER, 0 if b.tval != a.tval else 1, 0, 0, 0))
    elif operator == "<":
        outputs.push(Tokenizing.Token(T.NUMBER, 0 if b.tval < a.tval else 1, 0, 0, 0))
    elif operator == ">":
        outputs.push(Tokenizing.Token(T.NUMBER, 0 if b.tval > a.tval else 1, 0, 0, 0))
    else:
        print "ERROR"
        print "no definition for operator", operator, a, b

def is_function(ast, key):
    return key.tval in ast

def definition_match(keys, stack):
    mapping = {}
    popped = Stack()
    for key in keys[::-1]: #Should this be reversed? 
        if key.tval == "_":
            continue
        if stack.empty():
            while popped:
                stack.push(popped.pop())
            return False, {}
        val = stack.peek()

        if key.ttype == T.NAME:
            v = stack.pop()
            popped.push(v)
            mapping[key.tval] = v
            continue

        if key.ttype == T.STRING:
            if key.tval[1:-1] == val.tval:
                v = stack.pop()
                popped.push(v)
                continue

        if key.tval == val.tval:
            v = stack.pop()
            popped.push(v)
            mapping[key.tval] = v
            continue

        #didn't match any of the above conditions
        #Fail.
        while popped:
            stack.push(popped.pop())
        return False, {}

    return True, mapping

def apply_mapping(code, mapping):
    #print "apply mapping", code, mapping
    #[(1|n), (2|1), (51|-), (1|fib), (1|n), (2|2), (51|-), (1|fib), (51|+)] 
    #{'n': (2|3)}
    new_code = []
    for idx, val in enumerate(code):
        if val.tval in mapping:
            new_code.append(mapping[val.tval])
        else:
            if val.tval != "_":
                new_code.append(val)
    return new_code

def call_function(ast, item, inputs, outputs):
    func_name = item.tval
    if func_name not in ast:
        raise Exception("Function not found: " + func_name)

    func = ast[func_name]
    if func is None: # Native call
        native_call_function(inputs, outputs)
        return 
    for key, code in func.items():
        matched, mapping = definition_match(key, inputs)
        if matched:
            new_code = apply_mapping(code, mapping) 
            outputs.push_many(new_code)
            return 
    raise Exception("Unmatched case: " + func_name + " Has no match for " + str(inputs) )      

def native_call_function(inputs, outputs):
    py_file = inputs.pop().tval[1:-1] # strip off quotes
    func = inputs.pop().tval
    argc = inputs.pop().tval
    
    args = []
    for i in xrange(argc):
        args.append(inputs.pop())

    lib = __import__("native." + py_file)
    if lib is None:
        raise Exception("No lib named '{}'".format(py_file))
    lib = getattr(lib, py_file)
    f = getattr(lib, func, None)
    if f is None:
        raise Exception("No function named {} in library {}".format(func, py_file))

    f(inputs, outputs, args)
import time
def evaluate(ast, args):
    working = Stack()
    working.push(Tokenizing.Token(1, "call", 0, 0, -1))
    working.push(Tokenizing.Token(1, "main", 0, 0, -1))
    tmp = Stack()
    #tokenize args, push them onto tmp
    steps = 0
    while working:
        steps += 1
        print "Step", tmp,"     ",working[::-1]
#        time.sleep(1)
        item = working.pop()
#        if is_function(ast, item):
#            call_function(ast, item, tmp, working)
#        el
#        print item
        if is_operator(ast, item):
            call_operator(ast, item, tmp, working)
        else:
            tmp.push(item)

    return tmp
    #print "-"*20
    #print "steps:", steps
    #print tmp


def file_from_use_statement((path, lib)):
    fpath = "/".join([p.tval for p in path] + [lib.tval])
    return fpath

def build_tree(files):
    ast = {}
    for fname in files:
        if fname != 'native':
            token_stream = Tokenizing.FileSource(fname)
            use_statements, cur_ast = build_ast(token_stream)
        else:
            ast['native']=None
            continue
        tree = build_tree(map(file_from_use_statement, use_statements))
        ast.update(tree)
        #print cur_ast
        ast.update(cur_ast)
    return ast 
###
# Main
###
def run_main():
    import sys
    
    files = []
    args = []
    if "--" in sys.argv:
        pos = sys.argv.index("--")
        files = sys.argv[:pos]
        args = sys.argv[pos+1:]
    else:
        files = sys.argv
    files = files[1:]
    if not files:
        print "Missing program file to run"
        exit(0)
    
    ast = build_tree(files)
   #for f in ast:
    #    print f
    #    for k,v in ast[f].items():
    #        print "  ",k," | ", v
    ret =     evaluate(ast, [])
    print "END"
    print ret
    
if __name__ == "__main__":
    try:
        run_main()
    except Exception as E:
        print "Exception:"
        print E
        raise 

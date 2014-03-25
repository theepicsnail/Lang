from pyparsing import ZeroOrMore, OneOrMore, Optional, Forward, Literal,\
                      Word, nums, alphas, alphanums, Regex, Or, Group, Suppress
class Node(object): # Super class of all AST Nodes
    @classmethod
    def getParser(cls):
        try:
            return cls.parser
        except:
            cls.parser = Forward()
            cls.parser << cls.buildParser()
            cls.parser.setParseAction(cls)
        return cls.parser

    @ classmethod
    def buildParser(cls):
        raise NotImplementedError(cls)

class Assignment(Node):
    @classmethod
    def buildParser(cls):
        return Var.getParser() + Suppress('=') + Expression.getParser()
    def __init__(self,s, l, toks):
        self.var = toks[0]
        self.expr = toks[1]
    def compile(self):
        return self.expr.compile() + self.var.compile() + ["Set"]

class Var(Node):
    @classmethod
    def buildParser(cls):
        return Word(alphas)
    def __init__(self, s, l, toks):
        self.name = toks[0]
    def compile(self):
        return [self.name]

class Num(Node):
    @classmethod
    def buildParser(cls):
        return Word(nums)
    def __init__(self, s,l,toks):
        self.num = int(toks[0])
    def compile(self):
        return [self.num]

class Value(Node):
    @classmethod
    def buildParser(cls):
        return (Var.getParser() | Num.getParser() | (
            Suppress("(") + Expression.getParser() + Suppress(")")
        ))
    def __init__(self, s,l,toks):
        self.val = toks[0]
    def compile(self):
        out = self.val.compile()
        if isinstance(self.val, Var):
            out.append("Get")
        return out

class Term(Node):
    @classmethod
    def buildParser(cls):
        return Value.getParser() + Group(ZeroOrMore(
            Group((Literal('*') | Literal('/')) + Value.getParser())
        ))
    def __init__(self, s,l,toks):
        self.val = toks[0]
        self.exts = toks[1]
    def compile(self):
        out = self.val.compile()
        for (op, val) in self.exts:
            out += val.compile()
            out.append(op)
        return out

class Expression(Node):
    @classmethod
    def buildParser(cls):
        return Term.getParser() + Group(ZeroOrMore(
            Group((Literal('+') | Literal('-')) + Term.getParser())
        ))
    def __init__(self,s,l,toks):
        self.val = toks[0]
        self.exts = toks[1]
    def compile(self):
        out = self.val.compile()
        for (op, val) in self.exts:
            out += val.compile()
            out.append(op)
        return out

class Line(Node):
    @classmethod
    def buildParser(cls):
        return Assignment.getParser() | Expression.getParser()
    def __init__(self, s, l, toks):
        self.line = toks[0]
    def compile(self):
        return self.line.compile()


bnf = Line.getParser()
scope={}
while True:
    line = raw_input()
    if not line:
        break
    try:
        ast = bnf.parseString(line, parseAll = True)[0]

        stk = []
        for instr in ast.compile():
            {"+":lambda: stk.append(stk.pop()+stk.pop())
            ,"-":lambda: stk.append(-stk.pop()+stk.pop())
            ,"*":lambda: stk.append(stk.pop()*stk.pop())
            ,"/":lambda: stk.append(1.0/stk.pop() * stk.pop())
            ,"Get":lambda: stk.append(scope.get(stk.pop(),0))
            ,"Set":lambda: scope.update(dict([(stk.pop(), stk.pop())]))
            }.get(instr,lambda: stk.append(instr))()
        print ""
        print "Done:", stk, scope
    except Exception as e:
        print e
        raise
for line in ["1", "x", "x=1", "x=1+1", "x=x+3", "y=1*(2+3)", "z=8*(x-2*y)" ]:
    print "-"*10
    print "Input:", line
    try:
        for i in bnf.parseString(line, parseAll = True ):
            print "compiled:"
            print i.compile()
    except:
        print "Failed to parse"
        raise


print ""



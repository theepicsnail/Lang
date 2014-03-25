from pyparsing import ZeroOrMore, OneOrMore, Optional, Forward, Literal,\
                      Word, nums, alphas, alphanums, Regex, Or, Group

def dbg(*a, **b):
    print a, b

class ParseAction(object):
    __slots__=["toks"]
    def __init__(self, s, l, toks):
        self.toks = toks;
    def dump(self, depth=1):
        def output(i):
            if isinstance(i, ParseAction):
                print "  " * depth, type(i)
                i.dump(depth+1)
            elif isinstance(i, list):
                for j in i:
                    output(j)
            else:
                print "  " * depth, i

        for i in self.toks:
            output(i)
    def compact(self):
        raise NotImplementedError()

class AssignmentStmt(ParseAction):
    pass
class ReturnStmt(ParseAction):
    pass
class CallStmt(ParseAction):
    pass
class PrintStmt(ParseAction):
    pass
class Expression(ParseAction):
    pass
class AddExpression(ParseAction):
    pass
class OrExpression(ParseAction):
    pass
class ValueExpression(ParseAction):
    pass
class LambdaFuncExpression(ParseAction):
    pass
class Scope(ParseAction):
    pass
class DataType(ParseAction):
    pass
class ArgList(ParseAction):
    pass
class Trailer(ParseAction):
    pass



def BNF():
    lbracket, rbracket, lparen, rparen, semicolon, amp, comma, \
    eq, pluseq, dot, \
    ty_int, ty_scope, ty_void, ty_type, \
    kw_return, kw_print  = map(Literal, (
        "{ } ( ) ; & , = += . int scope void type return print"
        ).split())
    types = ty_int | ty_scope | ty_void | ty_type
    comments = Regex("//.*").suppress()
    number = (Word(nums) + Optional("." + Word(nums))).setParseAction(lambda s,l,t:[float(t[0])])
    name = Word( alphas+"_", alphanums+"_" )

    datatype = Forward()
    dataArgType = lparen + datatype + ZeroOrMore("," + datatype) + rparen
    datatype << types + Optional(dataArgType)

    statements = Forward()
    expression = Forward()

    # Arguments being passed to a function
    argument = name | expression
    arg_list = argument + ZeroOrMore(comma + argument)
    # foo.asdf foo() foo(x,3)
    trailer = (lparen + Optional(arg_list) + rparen) | (dot + name)
    call_stmt = (name & ~datatype )+ Group(ZeroOrMore(trailer))

    argList = datatype + name + ZeroOrMore( comma + datatype + name )
    scopeValue = lbracket + statements + rbracket
    lambdaFunc = datatype + lparen + Optional(argList) + rparen + scopeValue
    # leaf values: x x() x()() 3
    value = lambdaFunc \
          | scopeValue \
          | number \
          | (lparen + expression + rparen) \
          | call_stmt
          # | string

    addExpression = Forward().setParseAction(AddExpression)
    addExpression << value + Optional('+' + addExpression)

    orExpression = Forward().setParseAction(OrExpression)
    orExpression << addExpression + Optional('|' + orExpression)
    # x
    # x + 5
    # 1 + 3 + 4
    expression << Optional(amp) + orExpression
    # x = 1
    # return 3
    # print 123
    assignment_stmt = name + (eq | pluseq) + expression
    return_stmt = kw_return + expression
    print_stmt = kw_print + expression

    statement = (return_stmt | assignment_stmt | call_stmt | print_stmt) + semicolon.suppress()
    statements << OneOrMore(statement | comments)


    #statement.setParseAction(Statement)
    assignment_stmt.setParseAction(AssignmentStmt)
    return_stmt.setParseAction(ReturnStmt)
    call_stmt.setParseAction(CallStmt)
    print_stmt.setParseAction(PrintStmt)
    expression.setParseAction(Expression)
    orExpression.setParseAction(OrExpression)
    addExpression.setParseAction(AddExpression)
    value.setParseAction(ValueExpression)
    lambdaFunc.setParseAction(LambdaFuncExpression)
    scopeValue.setParseAction(Scope)
    datatype.setParseAction(DataType)
    argList.setParseAction(ArgList)
    trailer.setParseAction(Trailer)
    #argument.setParseAction(dbg)
    #types.setParseAction(dbg)
    #comments.setParseAction(dbg)
    #number.setParseAction(dbg)
    #name.setParseAction(dbg)
    #datatype.setParseAction(dbg)
    #dataArgType.setParseAction(dbg)

    return statements;

bnf = BNF()
for i in bnf.parseString(#file("test").read()
    """main = int(int x) {
        print(x).y(z).a.b;
        return x
    };
    """
    , parseAll=True):

    print "---"
    print i.dump()

print ""



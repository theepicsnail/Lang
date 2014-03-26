from pyparsing import ZeroOrMore, OneOrMore, Optional, Forward, Literal, \
                      Word, nums, alphas, alphanums, Regex, Or, Group, \
                      Suppress, oneOf, ParseException
import unittest
DEBUG = False

class Node(object): # Super class of all AST Nodes
    @classmethod
    def getParser(cls):
        try:
            return cls.parser
        except:
            cls.parser = Forward()
            if DEBUG: print(dir(cls))
            cls.parser.setResultsName("")
            cls.parser <<= cls.buildParser()
            cls.parser.setParseAction(cls)
        return cls.parser

    @classmethod
    def buildParser(cls):
        raise NotImplementedError(cls)

ParenL = Suppress("(")
ParenR = Suppress(")")
BraceL = Suppress("{")
BraceR = Suppress("}")
Comma = Suppress(",")
Dot = Suppress(".")
Semicolon = Suppress(";")
Name = Word(alphas)

#temporary patches
Expression = Name
Statements = ZeroOrMore(Expression + Semicolon)

class NodeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if cls is NodeTest:
            raise unittest.SkipTest("Skipping base test class")
        print(cls.__name__)
        super(NodeTest, cls).setUpClass()

    def setUp(self):
        self.parser = self.getParser()
        self.assertIsNotNone(self.parser)

    def test_accept(self):
        for test_input in self.accepts:
            print("Accept:", "[ ]", repr(test_input), end="")
            self.assertIsNotNone(self.parser.parseString(
                test_input, parseAll=True))
            print("\b" * (len(repr(test_input)) + 3) + "X")

    def test_reject(self):
        for test_input in self.rejects:
            print("Reject:", "[ ]", repr(test_input),  end="")
            self.assertRaises(ParseException, self.parser.parseString,
                test_input, parseAll=True)
            print("\b" * (len(repr(test_input)) + 3) + "X")

    def test_minimal_coverage(self):
        self.assertNotEqual([], self.rejects)
        self.assertNotEqual([], self.accepts)
        self.assertIn("", self.accepts + self.rejects, "Empty string undefined")



class Type(Node):
    @classmethod
    def buildParser(cls):
        # Type: Int | Void | Scope | String
        return oneOf("void int scope string") #Void | Int | Scope | String

    def __init__(self, text, offset, tokens):
        if DEBUG: print(tokens)

class TestType(NodeTest, Type):
    accepts=["void", "scope", "int", "string"]
    rejects=["main", "Int", "", "intint"]



class DataArgType(Node):
    @classmethod
    def buildParser(cls):
        # DataArgType: '(' DataType? ( ',' DataType )* ')'
        return ParenL + Optional(DataType.getParser()) + ZeroOrMore(
               Comma + DataType.getParser()) + ParenR

    def __init__(self, text, offset, tokens):
        if DEBUG: print(tokens)

class TestDataArgType(NodeTest, DataArgType):
    accepts=["()", "(int)"]
    rejects=["int", "(int,)", ""]



class DataType(Node):
    @classmethod
    def buildParser(cls):
        # DataType: Type DataArgType*
        return Type.getParser() + ZeroOrMore(DataArgType.getParser())

    def __init__(self, text, offset, tokens):
        if DEBUG: print(tokens)

class TestDataType(NodeTest, DataType):
    accepts = ["int", "int()", "int(string)", "int(string)()",
                "int(int(int,int),int)"]
    rejects = ["", "main"]



class ArgList(Node):
    @classmethod
    def buildParser(cls):
        # ArgList: (DataType Name ','? )*
        return ZeroOrMore(DataType.getParser() + Name + Optional(Comma))

    def __init__(self, text, offset, tokens):
        if DEBUG: print(tokens)

class TestArgList(NodeTest, ArgList):
    accepts=["",
        "int x, int y",
        "int(int) x, void y",
        "int(int) x, void y,",
        "int(int) x void y"]
    rejects=["x", "int"]



class Trailer(Node):
    @classmethod
    def buildParser(cls):
        # Trailer: '(' (Expression ','?)*  ')'
        #        : '.' name
        return (ParenL +\
                ZeroOrMore(Name \
                #Expression.getParser()
                + Optional(Comma)) +\
                ParenR)\
            | (Dot + Name)

    def __init__(self, text, offset, tokens):
        if DEBUG: print(tokens)

class TestTrailer(NodeTest, Trailer):
    accepts=[".Foo", ".int"] +\
            ["()", "(x)", "(x,y)"]
    rejects=["", ".", ".0", "("]



class Scope(Node):
    @classmethod
    def buildParser(cls):
        # Scope: '{' Statements '}'
        return BraceL + Statements + BraceR

    def __init__(self, text, offset, tokens):
        if DEBUG: print(tokens)

class TestScope(NodeTest, Scope):
    accepts = ["{}", "{x; y;}"]
    rejects = ["{", "}", ""]




class Lambda(Node):
    @classmethod
    def buildParser(cls):
        # Lambda: '(' ArgList ')' DataType Scope
        return  ParenL + ArgList.getParser() + ParenR + DataType.getParser() +Scope.getParser()

    def __init__(self, text, offset, tokens):
        if DEBUG: print(tokens)

class TestLambda(NodeTest, Lambda):
    accepts = [
        "()void{}",
        "(int x)void{}",
        "(int x, int y)void{}",
        "(int(int) x, int y)void{}",
        "(int(int) x, int y)void(int){}"]
    rejects = [
        "",
        "(int)void{}",
        "()void(int x){}"]



class Value(Node):
    @classmethod
    def buildParser(cls):
        # Value: Lambda | Scope | Expression
        return Lambda.getParser() | Scope.getParser() | Expression
    def __init__(self, text, offset, tokens):
        if DEBUG: print(tokens)

class TestValue(NodeTest, Value):
    accepts = [ "x" ]  #, "1", "{}", "()int{}" ]
    rejects = [ "", "="]


# Temporary patches:
# Expression   - patched as Name
# Statements   - patched as ( Name ';' )*

# Current bnf
# Type: Int | Void | Scope | String
# DataArgType: '(' (DataType Name Comma?)* ')'
# DataType: Type DataArgType*
# ArgList: (DataType Name Comma?)*
# Trailer: '(' (Expression Comma?)* ')'
#        : '.' name
# Scope: '{' + Statements + '}'
# Lambda: '(' ArgList ')' DataType Scope




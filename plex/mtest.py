from pyparsing import ZeroOrMore, OneOrMore, Optional, Forward, Literal, \
                      Word, nums, alphas, alphanums, Regex, Or, Group, \
                      Suppress, oneOf, ParseException
import unittest

class Node(object): # Super class of all AST Nodes
    @classmethod
    def getParser(cls):
        try:
            return cls.parser
        except:
            cls.parser = Forward()
            print dir(cls)
            cls.parser.setResultsName("")
            cls.parser << cls.buildParser()
            cls.parser.setParseAction(cls)
        return cls.parser

    @ classmethod
    def buildParser(cls):
        raise NotImplementedError(cls)


ParenL = Suppress("(")
ParenR = Suppress(")")
Comma = Suppress(",")
Name = Word(alphas)

class Type(Node):
    @classmethod
    def buildParser(cls):
        # Type: Int | Void | Scope | String
        return oneOf("void int scope string") #Void | Int | Scope | String

    def __init__(self, text, offset, tokens):
        print tokens

class TestType(unittest.TestCase):
    def test(self):
        p = Type.getParser()
        p.parseString("void", parseAll=True)
        p.parseString("scope", parseAll=True)
        p.parseString("int", parseAll=True)
        p.parseString("string", parseAll=True)
        self.assertRaises(ParseException, p.parseString, "main", parseAll=True)
        self.assertRaises(ParseException, p.parseString, "Int", parseAll=True)



class DataArgType(Node):
    @classmethod
    def buildParser(cls):
        # DataArgType: '(' DataType? ( ',' DataType )* ')'
        return ParenL + Optional(DataType.getParser()) + ZeroOrMore(
               Comma + DataType.getParser()) + ParenR

    def __init__(self, text, offset, tokens):
        print tokens

class TestDataArgType(unittest.TestCase):
    def test(self):
        p = DataArgType.getParser()
        p.parseString("()", parseAll=True)
        p.parseString("(int)", parseAll=True)
        self.assertRaises(ParseException, p.parseString, "int", parseAll=True)
        self.assertRaises(ParseException, p.parseString, "(int,)", parseAll=True)



class DataType(Node):
    @classmethod
    def buildParser(cls):
        # DataType: Type DataArgType*
        return Type.getParser() + ZeroOrMore(DataArgType.getParser())

    def __init__(self, text, offset, tokens):
        print tokens

class TestDataType(unittest.TestCase):
    def test(self):
        p = DataType.getParser()
        p.parseString("int", parseAll=True)
        p.parseString("int()", parseAll=True)
        p.parseString("int(string)", parseAll=True)
        p.parseString("int(string)()", parseAll=True)
        p.parseString("int(int(int,int),int)", parseAll=True)
        self.assertRaises(ParseException, p.parseString, "", parseAll=True)
        self.assertRaises(ParseException, p.parseString, "main", parseAll=True)



class ArgList(Node):
    @classmethod
    def buildParser(cls):
        # ArgList: (DataType Name Comma?)*
        return ZeroOrMore(DataType.getParser() + Name + Optional(Comma))

    def __init__(self, text, offset, tokens):
        print tokens

class TestArgList(unittest.TestCase):
    def test(self):
        p = ArgList.getParser()

        # Normal Arg List
        p.parseString("", parseAll=True)
        p.parseString("int x, int y", parseAll=True)
        p.parseString("int(int) x, void y", parseAll=True)
        self.assertRaises(ParseException, p.parseString, "x", parseAll=True)
        self.assertRaises(ParseException, p.parseString, "int", parseAll=True)

        # Weird Edge cases
        p.parseString("int(int) x, void y,", parseAll=True)
        p.parseString("int(int) x void y", parseAll=True)



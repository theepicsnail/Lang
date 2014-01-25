from matchers import *
import token as T
from collections import OrderedDict
##
# Parse tree
###


depth = 1 
def tokenizeDebug(func):
    return func
    def nfunc(tokens):
        global depth
        prefix = "%15r" %tokens.peek().tval 
        print prefix,
        print ("  |"*depth)[:-1]+">",
        print func.func_name

        depth += 1
        try:
            ret = func(tokens)
        except Exception as e:
            depth -=1
            print prefix, 
            print ("  |"*depth)[:-1]+"X", e
            raise
        depth -=1
        print prefix,
        print ("  |"*depth)[:-1]+"<",
        print ret

        return ret
    return nfunc



@tokenizeDebug
def build_ast(tokens):
    #<use statement>* <function>+
    use_statements = zero_or_more(use_statement, tokens)
    ret =  use_statements, dict(one_or_more(function, tokens))
    #print "\n\n build ast:",tokens, tokens.peek()
    required(token_field_matcher(ttype=T.ENDMARKER), tokens)
    return ret
@tokenizeDebug
def use_statement(tokens):
    NAME = token_field_matcher(ttype=T.NAME)
    def NAME_DOT(tokens):
        name = required(NAME, tokens)
        required(token_field_matcher(tval = "."), tokens)
        return name

    required(token_field_matcher(tval="use"), tokens)
    #use NAME_DOT+ NAME
    path = zero_or_more(NAME_DOT, tokens)
    name = required(NAME, tokens)
    zero_or_more(token_field_matcher(ttype = T.NEWLINE), tokens)
    return (path, name)

@tokenizeDebug
def function(tokens):
    #fun <$name> \n <func_definition>+
    #print "Geting function"
    required(token_field_matcher(tval="fun"), tokens)
    identifier = required(token_field_matcher(ttype=T.NAME), tokens).tval
    #print "id", identifier
    required(token_field_matcher(ttype=T.NEWLINE), tokens)
    defs = OrderedDict(one_or_more(function_definition, tokens))
    return (identifier, defs)

@tokenizeDebug
def function_definition(tokens):
    key_list = one_or_more(function_definition_key, tokens)
    #print "keys", key_list
    required(token_field_matcher(tval = "|"), tokens)
    value = zero_or_more(function_definition_value, tokens)
    #print "Value", value, map(lambda x:x.ttype, value)
    zero_or_more(token_field_matcher(ttype = T.NEWLINE), tokens)
    return (tuple(key_list), value)

@tokenizeDebug
def function_definition_key(tokens):
    def key_value(token):
        return token.ttype in [T.NUMBER, T.NAME, T.STRING] or token.tval in ["."]
    key_value.func_name = "Function key value"
    return required(token_lambda_matcher(key_value), tokens)

@tokenizeDebug
def function_definition_value(tokens):
    #one or more non-newline tokens
    def def_value(token):
        return token.ttype != T.NEWLINE 
    def_value.func_name = "Function definition value"
    return required(token_lambda_matcher(def_value), tokens)




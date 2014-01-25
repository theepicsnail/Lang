"""
    Parsing utilities.
    This module contains the helpers for matching various AST node quantites.

    optional (regex: ?)
    required 
    zero_or_more (regex: *)
    one_or_more(regex: +)

    
"""
class ParseException(Exception):
    pass

def _expected_found_exception(expected, found):
    
    dump = "Line %i, Unexpected: %r " % (found.start[0], found.tval)
    raise ParseException("Expected {}, found {}.\n{}".format(expected, found, dump))

# Quantity modifiers

def optional(node, tokens):
    """Regex ?. If the node raises an exception, return None"""
    pos = tokens.tell()
    try:
        v = node(tokens)
        return v
    except ParseException:
        tokens.seek(pos)
        return None

def required(node, tokens):
    """Match a given node. If the node returns None, raise a parse exception"""
    val = node(tokens)
    if val == None:
        _expected_found_exception(node.func_name, None)
    return val

def zero_or_more(node, tokens):
    """Regex *"""
    out = []
    while True:
        ret = optional(node, tokens)

        if ret is None:
            return out

        out.append(ret)

def one_or_more(node, tokens):
    """Regex +"""
    first = required(node, tokens)
    rest = zero_or_more(node, tokens)
    return [first] + rest

def token_field_matcher(**match_criteria):
    """Only match a token that has key/values equal to the passed in arguments"""

    def cb (token):
        for key, val in match_criteria.items():
            if getattr(token, key) != val:
                return False
        return True
    cb.func_name = "field matcher: " + str(match_criteria)
    return token_lambda_matcher(cb)

def token_lambda_matcher(cb):
    """Given a callback (that returns True or False), 
    either return the token or raise an exception"""
    match_def = "lambda matcher " + str(cb)
    def matcher(tokens):
        token = tokens.get()
        if token == None:
            return None
        if not cb(token):
            _expected_found_exception(match_def, token)
        return token
    
    matcher.func_name = "matcher: " + match_def
    return matcher


import collections, tokenize, token
def FileSource(fname):
    return Tokenizer( file(fname, "rb").readline )

def UrlSource(url):
    #implement url sources
    return None


class TokenizerException(Exception):
    pass

Token = collections.namedtuple("Token", ["ttype", "tval", "start", "end", "line"])
Token.__str__ = lambda x: "%r"%(x.tval)
Token.__repr__ = lambda x: "%r"%(x.tval)
class Tokenizer(object):
    def __init__(self, readline):
        self.tokens = []
        self.state = []
        self.pos = 0
        tokenize.tokenize(readline, self.consumer)
    def __str__(self):
        return "[" + "], [".join(map(str, self.tokens))+"]"
    def consumer(self, ttype, tval, start, end, line):
        #print ttype, tval, start, end, line
        if ttype in [token.INDENT, token.DEDENT, tokenize.NL, tokenize.COMMENT]:
            #We don't want/care about indent/dedent tokens
            return
        if ttype == token.NUMBER:
            if "." in tval:
                tval = float(tval)
            else:
                tval = int(tval)
        if ttype == 52: 
            if tval == ' ':
                return 
            ttype = 51
        if ttype == token.OP:
            if tval in "(){}[]":
                ttype = token.STRING
        #print (ttype, tval),
        self.tokens.append(Token(ttype, tval, start, end, line))

    def get(self):
        if self.pos == len(self.tokens):
#            print "Get -> None"
            return None
        
        token = self.tokens[self.pos]
        self.pos += 1
#        print "Get -> ", token
        return token

    def unget(self):
#        print "Unget"
        if self.pos == 0:
            raise TokenizerException("Tried to return tokens with nothing to return")
        self.pos -= 1
        return self

    def tell(self):
        return self.pos

    def seek(self, pos):
        if pos < 0 or pos >= len(self.tokens):
            raise TokenizerException("Tried to seek to invalid location: " + pos)
        self.pos = pos
    def peek(self):
        return self.tokens[self.pos]

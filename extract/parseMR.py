#!/usr/bin/env python

"""
Reads in the geoquery corpus and writes three text files:
1. Strings
2. Syntax trees
3. Variable free semantic representation (functional query language)

These can then be used as parallel corpora
"""

from bs4 import BeautifulSoup
from pyparsing import *
import ply.lex as lex
import ply.yacc as yacc

from FunqlTerms import *


class GeoLexer(object):
    def __init__(self):
        self.build()
        
    tokens = (
        'COMMA', # ,
        'IDENTIFIER', # for keywords
        'LPAREN', # (
        'NUMBER', # 1234
        'RPAREN', # )
        'STRING',
        'BLANK', #_
    )

    t_COMMA  = r','
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_BLANK  = r'_'
    
    def t_IDENTIFIER(self, t):
        r'[A-Za-z][-A-Za-z_0-9]*'
        return t

    def t_STRING(self, t):
        r'''["'][^()'"]*["']'''
        return t

    def t_NUMBER(self, t):
        r'[0-9]+(\.[0-9]+)?'
        t.value = int(t.value)
        return t

    t_ignore = ' \t\v\r'

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1

    def t_error(self, t):
        print "FunQL Lexer: Illegal character " + t.value[0]
        t.lexer.skip(1)
    
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer
    
    def lex(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: break
            print tok


class GeoParser(object):
    def __init__(self):
        self.tokens = GeoLexer.tokens
        lexer = GeoLexer()
        self.lexer = lexer.lexer
        self.parser = yacc.yacc(module=self)
    
    def parse(self, funql):
        return self.parser.parse(funql, self.lexer)
    
    def lex(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: break
            print tok
    
    start = 'funql'    # the start symbol in our grammar

    def p_geoTerm(self, p):
        r'funql : function'
        p[0] = p[1]

    def p_function(self, p):
        r'function : IDENTIFIER LPAREN args RPAREN'
        p[0] = FunqlTerm(p[1], p[3])

    def p_function_empty(self, p):
        r'function : IDENTIFIER'
        p[0] = FunqlConst(p[1])

    def p_args(self, p):
        r'args : argument'
        p[0] = [p[1]]
        
    def p_args2(self, p):
        r'args : argument COMMA args'
        p[0] = [p[1]] + p[3]
    
    def p_argument(self, p):
        r'argument : function'
        p[0] = p[1]
    
    def p_argument_str(self, p):
        r'argument : STRING'
        p[0] = FunqlConst(p[1])
    
    def p_argument_blank(self, p):
        r'argument : BLANK'
        p[0] = FunqlConst('_')
    
    def p_argument_num(self, p):
        r'argument : NUMBER'
        p[0] = FunqlConst(str(p[1]))

    def p_error(self, p):
        print "Parse Error: ", p.value, " at lexeme ", p.lineno, p.lexpos

def transform(term):
    if isinstance(term, list):
        term = [t for t in term if t not in (",",)]
    if (len(term) == 1 and isinstance(term[0], unicode)):
        return term
    if all(isinstance(t,unicode) for t in term[1]):
        return ["{}({})".format(term[0],",".join(t for t in term[1] if str(t) not in (",",) ))]
    res = []
    
    argLength = len(term[1:])
    res.append(term[0]+"("+",".join("X" for _ in range(argLength))+")")
    for subTerm in term[1:]:
        res = res + transform(subTerm)
    
    return res

def parseFunql(term):
    parser = GeoParser()
    return parser.parse(term)
#
# Just for testing the script without anything else
#
def main():

    soup = BeautifulSoup(open("../data/corpus.xml"), "xml")
    
    # extract strings
    string = []
    raw_string = soup("nl")
    for item in raw_string:
        if item["lang"] == "en":
            string.append(item.string.replace("\n",""))
    
    # extract variable-free gequery
    geo_funql = []
    raw_geo_funql = soup("mrl")
    for item in raw_geo_funql:
        if item["lang"] == "geo-funql":
            geo_funql.append(item.string.replace("\n",""))

    parser = GeoParser()
    
    for s in geo_funql:
        print s
        #parser.lex(s)
        parse = parser.parse(s)
        print parse.toMR()
        if str(parse) != s:
            print ">>", parse
            raw_input()
    


if __name__ == "__main__":
    main()


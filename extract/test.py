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


def transform(term):
    res = []
    if term == ",":
        return res
    if not isinstance(term, list) or len(term) == 1:
        return [term]
    if term[0] in ("countryid", "stateid", "cityid"):
        return [term[0] + "(" + "".join("".join(map(str, term[1:]))) + ")"]
    argLength = len(term[1])
    res.append(term[0]+"("+",".join("X" for _ in range(argLength))+")")
    for subTerm in term[1:]:
        res = res + transform(subTerm)
    
    return res


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

    fname = Word(alphanums + "_")
    
    funq = Forward()
    #funq << OneOrMore(fname)
    funq << fname # | (fname + '(' + funq + ')')
    
    for s in geo_funql:
        #s = "answer(loc(virgina))"
        #print s
        parse = OneOrMore(nestedExpr()).parseString("("+s+")").asList()[0]
        #print ">>", parse
        print " ".join(transform(parse))
        #print ">> ", parse(s)


if __name__ == "__main__":
    main()


#!/usr/bin/env python

"""
Reads in the geoquery corpus and writes three text files:
1. Strings
2. Syntax trees
3. Variable free semantic representation (functional query language)

These can then be used as parallel corpora
"""

from bs4 import BeautifulSoup
from parseMR import parseFunql

def list_to_txt(xml_list):
    txt = ""
    for item in xml_list:
        txt = txt + item + "\n"
    # have to remove last newline for Giza++
    return txt[:(len(txt)-1)]


def main():

    soup = BeautifulSoup(open("../data/corpus.xml"), "xml")
    
    # extract strings
    string = []
    raw_string = soup("nl")  
    for item in raw_string:
        if item["lang"] == "en":
            item = item.string
            item = item.replace(" ?","")
            item = item.replace(" .","")
            string.append(item.replace("\n",""))
    
    string_txt = open("../data/string.txt", "w")
    # changes casing to all lower case for word alignment
    string_txt.write(list_to_txt(string).lower())
    string_txt.close()
    
    # extract syntax
    syntax = []
    raw_syntax = soup("syn")
    for item in raw_syntax:
        if item["lang"] == "en":
            syntax.append(item.string.replace("\n",""))
       
    syntax_txt = open("../data/syntax.txt", "w")
    syntax_txt.write(list_to_txt(syntax))
    syntax_txt.close()
    
    # extract variable-free gequery
    geo_funql = []
    raw_geo_funql = soup("mrl")
    for item in raw_geo_funql:
        if item["lang"] == "geo-funql":
            parsed = parseFunql(item.string.replace("\n",""))
            print parsed
            print parsed.toMR()
            geo_funql.append(parsed.toMR())
    
    geo_funql_txt = open("../data/geo-funql.txt", "w")
    geo_funql_txt.write(list_to_txt(geo_funql))
    geo_funql_txt.close()


if __name__ == "__main__":
    main()


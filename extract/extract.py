#!/usr/bin/env python

"""
Reads in the geoquery corpus and writes these:
1. string.txt for bulk parsing in Alto
2. syntax.txt (not used, but perhaps interesting at some point)
3. geo-funql.txt
4. geo-funql.gold gold standard for EVALB evaluation
5. geo-funql.eval parsed version for EVALB evaluation
6. string_funql.txt combined corpus for EM training

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
    
    # 1. extract strings
    string = []
    raw_string = soup("nl")  
    for item in raw_string:
        if item["lang"] == "en":
            item = item.string
            item = item.replace(" ?","")
            item = item.replace(" .","")
            string.append(item.replace("\n",""))  
    
    string_txt = open("../data/string.txt", "w")
    header = "# IRTG unannotated corpus file, v1.0\n#\n# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n\n"
    # changes casing to all lower case for word alignment
    string = list_to_txt(string).lower()
    string_txt.write(header + string)
    string_txt.close()
        
    # 2. extract syntax
    syntax = []
    raw_syntax = soup("syn")
    for item in raw_syntax:
        if item["lang"] == "en":
            syntax.append(item.string.replace("\n",""))
       
    syntax_txt = open("../data/syntax.txt", "w")
    syntax_txt.write(list_to_txt(syntax))
    syntax_txt.close()
    
    # 3. extract variable-free gequery
    geo_funql = []
    geo_funql_gold = []
    raw_geo_funql = soup("mrl")
    for item in raw_geo_funql:
        if item["lang"] == "geo-funql":
            geo_funql_gold.append(item.string.replace("\n",""))
            parsed = parseFunql(item.string.replace("\n",""))
            #print parsed
            #print parsed.toMR()
            geo_funql.append(parsed.toMR())
    
    geo_funql_txt = open("../data/geo-funql.txt", "w")
    geo_funql_txt.write(list_to_txt(geo_funql))
    geo_funql_txt.close()
    
    # 4. gold standard file, version without ''
    geo_funql_gold_txt = open("../data/geo-funql.gold", "w")
    geo_funql_gold_txt.write(list_to_txt(geo_funql_gold).replace("'","_"))
    geo_funql_gold_txt.close()    

    # 5. extract parsed trees, version for evaluation without ''
    try:
        parsed = open("../data/string.parsed").read().split("\n")
        string = []
    
        # get just the lines with actual parsed trees
        for i in range(5,len(parsed)):
            if (i+3)%4==0:
                string.append(parsed[i])
            else:
                pass
        
        parsed_txt = open("../data/geo-funql.eval", "w")
        parsed_txt.write(list_to_txt(string).replace("'","_"))
        parsed_txt.close()    
    except:
        pass

    # 6. combined corpus for EM training
    alto = []
    
    # append header
    header = "# IRTG unannotated corpus file, v1.0\n#\n# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n# interpretation t: de.up.ling.irtg.algebra.TreeAlgebra"
    
    alto.append(header)
    alto.append("")
  
    # extract strings
    #soup = BeautifulSoup(open("../data/corpus.xml"), "xml")
    string = []
    raw_string = soup("nl")  
    for item in raw_string:
        if item["lang"] == "en":
            item = item.string
            item = item.replace(" ?","")
            item = item.replace(" .","")
            item = item.replace("50","\"50\"")
            string.append(item.replace("\n",""))
   
    # variable-free geoquery
    geo_funql = []
    raw_geo_funql = soup("mrl")
    for item in raw_geo_funql:
        if item["lang"] == "geo-funql":
            geo_funql.append(item.string.replace("\n","").replace("0","\"0\""))
    
    for i in range(len(string)):
        alto.append(string[i].lower())
        alto.append(geo_funql[i])
            
    alto_txt = open("../data/string_funql.txt", "w")
    alto_txt.write(list_to_txt(alto))
    alto_txt.close()

if __name__ == "__main__":
    main()


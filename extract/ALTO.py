#!/usr/bin/env python

"""
Convert individual files to a combined ALTO corpus
"""
from bs4 import BeautifulSoup

def list_to_txt(xml_list):
    txt = ""
    for item in xml_list:
        txt = txt + item + "\n"
    # have to remove last newline for Giza++
    return txt[:(len(txt)-2)]

def main():
  
    alto = []
    
    # append header
    header = "# IRTG unannotated corpus file, v1.0\n#\n# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n# interpretation t: de.up.ling.irtg.algebra.StringAlgebra"
    
    alto.append(header)
    alto.append("")
  
    # read strings and geoquery files
    string = open("../data/string.txt").read().split("\n")
   
    # variable-free geoquery
    
    soup = BeautifulSoup(open("../data/corpus.xml"), "xml")
    geo_funql = []
    raw_geo_funql = soup("mrl")
    for item in raw_geo_funql:
        if item["lang"] == "geo-funql":
            geo_funql.append(item.string.replace("\n",""))
    
    #funql_geo = open("../data/geo-funql.txt").read().split("\n")
    
    for i in range(len(string)):
        alto.append(string[i])
        alto.append(geo_funql[i])
       
    alto_txt = open("../data/alto.irtg", "w")
    alto_txt.write(list_to_txt(alto))
    alto_txt.close()

if __name__ == "__main__":
    main()



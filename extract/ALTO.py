#!/usr/bin/env python

"""
Convert individual files to a combined ALTO corpus
"""

def list_to_txt(xml_list):
    txt = ""
    for item in xml_list:
        txt = txt + item + "\n"
    # have to remove last newline for Giza++
    return txt[:(len(txt)-2)]

def main():
  
    alto = []
    
    # append header
    string_header = "# interpretation string: de.up.ling.irtg.algebra.StringAlgebra"
    funql_header = "# interpretation string: de.up.ling.irtg.algebra.StringAlgebra"
    
    alto.append(string_header)
    alto.append(funql_header)
    alto.append("")
  
    # read strings and geoquery files
    string = open("../data/string.txt").read().split("\n")
   
    # variable-free geoquery
    funql_geo = open("../data/geo-funql.test.txt").read().split("\n")
    
    for i in range(len(string)):
        alto.append(string[i])
        alto.append(funql_geo[i])
    
    print alto
       
    alto_txt = open("../data/alto.txt", "w")
    alto_txt.write(list_to_txt(alto))
    alto_txt.close()

if __name__ == "__main__":
    main()



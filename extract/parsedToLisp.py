#!/usr/bin/env python

import sys

def list_to_txt(xml_list):
    txt = ""
    for item in xml_list:
        txt = txt + item + "\n"
    # have to remove last newline for Giza++
    return txt[:(len(txt)-1)]


def main():
  
    """ EVALUATION """    

    parsed_path = sys.argv[1]
    parsed = open(parsed_path, "r").read().split("\n")
    string = []
    
    # get just the lines with actual parsed trees
    string.append("# IRTG unannotated corpus file, v1.0\n#\n# interpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n")
    for i in range(6,len(parsed)):
        if (i%5)==4 or (i%5)==0:
            string.append(parsed[i])
        else:
            pass

    print list_to_txt(string) 

if __name__ == "__main__":
    main()


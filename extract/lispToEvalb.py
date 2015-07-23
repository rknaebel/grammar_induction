#!/usr/bin/env python

import sys
import re

def list_to_txt(xml_list):
    txt = ""
    for item in xml_list:
        txt = txt + item + "\n"
    # have to remove last newline for Giza++
    return txt[:(len(txt)-1)]


def main():
  
    parsed_path = sys.argv[1]
    lisp = open(parsed_path, "r").read().split("\n")
    string = []
       
    # get every other line with the lisp representation
    for i in range(len(lisp)):
        if i%2==1:
            ev = lisp[i]
            ev = re.sub(r"(id\s)([a-z_\']+)\s([a-z_\']+)\s([a-z_\']+)", "\g<1>\g<2>+\g<3>+\g<4>", ev)
            ev = re.sub(r"(id\s)([a-z_\']+)\s([a-z_\']+)", "\g<1>\g<2>+\g<3>", ev)

            string.append(ev.replace("_null_","").replace("\'",""))
        else:
            pass
    
    print list_to_txt(string) 

if __name__ == "__main__":
    main()


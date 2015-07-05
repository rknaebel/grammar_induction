#!/usr/bin/env python

"""
Prints words in test data missing from training data
"""

from bs4 import BeautifulSoup
from parseMR import parseFunql
import re

def list_to_txt(xml_list):
    txt = ""
    for item in xml_list:
        txt = txt + item + "\n"
    # have to remove last newline for Giza++
    return txt[:(len(txt)-1)]


def main():

    missing = []
    
    for i in range(10):
        train = open("../evaluate/" + str(i) + "/trainingstring." + str(i)).read().replace("\n"," ").split(" ")
        test = open("../evaluate/" + str(i) + "/teststring." + str(i)).read().replace("# IRTG unannotated corpus file, v1.0\n#\n# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n\n","").replace("\n"," ").split(" ")
        
        for word in test:
            if word not in train:
                print i, ":", word, "missing in training set"
        


if __name__ == "__main__":
    main()


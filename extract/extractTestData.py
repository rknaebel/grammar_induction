#!/usr/bin/env python

"""
Reads in the geoquery corpus and writes 10 sets of training and test data:
For 880 sentences, 80 taken as test, 800 as 
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

    soup = BeautifulSoup(open("../data/corpus.xml"), "xml")
    corpus = soup("example") 
  
    gold = open("../data/gold").read().split("\n")
    
    string_header = "# IRTG unannotated corpus file, v1.0\n#\n# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n\n"
    em_header = "# IRTG unannotated corpus file, v1.0\n#\n# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n# interpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n\n"
    stub_string = []
    stub_funql = []
    stub_string_funql = []
    
    """
    for example in corpus:
        #entity = re.search(".*\(([a-z]+id\(\'([a-z]+(\s[a-z]+)?|[a-z]+(\s[a-z]+)?\,\s([a-z]+|_))\'\))", example.mrl.string)
        entity = re.search(".*\(([a-z]+id\(\'[a-z\s]+\'([a-z,_\s]+)?\))", example.mrl.string)
        if entity: 
            stub_funql.append(entity.group(1))
    
    stub_funql = list(set(stub_funql))
    
    for item in stub_funql:
        string = re.search(".*\(\'([a-z\s]+)\'", item).group(1)
        stub_string.append(string)
        stub_string_funql.append(string)
        stub_string_funql.append(item)
    stub_string.append("us\nunited states\namerica")
    stub_funql.append("countryid('usa')\ncountryid('usa')\ncountryid('usa')")
    stub_string_funql.append("us\ncountryid('usa')\nunited states\ncountryid('usa')\namerica\ncountryid('usa')")
    """
    
    for i in range(10):
        test_string = []
        training_string = []
        test_funql = []
        training_funql = []
        em_training = []
        for j in (range(len(corpus))):
            if j % 10 == i:
                test_string.append(corpus[j].nl.string.replace(" ?","").replace(" .","").replace("\n","").replace("50","\"50\"").lower())
                #test_funql.append(corpus[j].nl.string.replace(" ?","").replace(" .","").replace("\n","").replace("50","\"50\"").lower())
                #test_funql.append(corpus[j].mrl.string.replace("\n","").replace("0","\"0\""))
                test_funql.append(gold[j])
            else:
                training_string.append(corpus[j].nl.string.replace(" ?","").replace(" .","").replace("\n","").lower())
                training_funql.append(parseFunql(corpus[j].mrl.string.replace("\n","")).toMR())
                em_training.append(corpus[j].nl.string.replace(" ?","").replace(" .","").replace("\n","").replace("50","\"50\"").lower())
                em_training.append(corpus[j].mrl.string.replace("\n","").replace("0","\"0\""))
        
        """ TEST """
        # teststring.# test strings for bulk parsing  
        test_string_txt = open("../evaluate/" + str(i) + "/teststring." + str(i), "w")
        test_string_txt.write(string_header + list_to_txt(test_string))
        test_string_txt.close()
        
        # testfunql.# test gold standard funql representations for evaluation
        test_funql_txt = open("../evaluate/" + str(i) + "/testfunql." + str(i), "w")
        test_funql_txt.write(list_to_txt(test_funql))
        test_funql_txt.close()
        
        """ TRAINING """
        # trainingstring.# training strings for word alignment
        training_string_txt = open("../evaluate/" + str(i) + "/trainingstring." + str(i), "w")
        training_string_txt.write(list_to_txt(training_string) + list_to_txt(stub_string))
        training_string_txt.close()
        
        # trainingfunql.# training funql representations for word alignment
        training_funql_txt = open("../evaluate/" + str(i) + "/trainingfunql." + str(i), "w")
        training_funql_txt.write(list_to_txt(training_funql) + list_to_txt(stub_funql).replace(" ","+"))
        training_funql_txt.close()
        
        # emtraining.# file with original string and gold standard funql for EM training
        em_training_txt = open("../evaluate/" + str(i) + "/emtraining." + str(i), "w")
        em_training_txt.write(em_header + list_to_txt(em_training) + list_to_txt(stub_string_funql))
        em_training_txt.close()    
    
    """ EVALUATION """   
    # evalfunl.# = file with parses to be evaluated    
    for i in range(10):        
        try:
            parsed = open("../evaluate" + str(i) + "string.parsed").read().split("\n")
            string = []
        
            # get just the lines with actual parsed trees
            for i in range(5,len(parsed)):
                if (i+3)%4==0:
                    string.append(parsed[i])
                else:
                    pass
            
            parsed_txt = open("../evalfunql." + str(i), "w")
            parsed_txt.write(list_to_txt(string).replace("'",""))
            parsed_txt.close()    
        except:
            pass


if __name__ == "__main__":
    main()


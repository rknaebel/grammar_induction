#!/usr/bin/python
#
# author:
# 
# date: 
# description:
#
import sys
import re


def wait(s):
    print s
    raw_input()
    
# Procedures
def extractFeatures(irtg):
    features = []
    matches = re.findall(r"[\w!]+\s+->\s+(s\d+)(\((\w[, ]*)+\))?\s+(\[[-.0-9E]+\])?", irtg)
    for idx,(ruleName, _, _, _) in enumerate(matches):
        features.append("feature f{}: de.up.ling.irtg.maxent.RuleNameFeature('{}')".format(idx, ruleName))
    return features
    


# Main
def main():
    #irtg_file = open("../data/weighten_alto.irtg").read().strip("\n").split("\n\n")
    if len(sys.argv) < 2:
        raise Exception("wrong usage! prepareLogLinModel.py grammar")

    irtg_path = sys.argv[1]
    irtg_file = open(irtg_path, "r").read()

    features = extractFeatures(irtg_file)

    headersplit = irtg_file.find("\n\n\n")
    
    print irtg_file[:headersplit], "\n\n"
    print "\n".join(features)
    print irtg_file[headersplit:]

    return 0
    

main()

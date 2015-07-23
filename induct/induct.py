#!/usr/bin/env python

"""
Induct grammar from sentence alignments between tokenized strings and tokenized trees
"""
import sys

import re
import logging


from Rule import Rule
from IntervalTree import IntervalTree
from IntervalTree import Interval

from inductionMethods import topDownInduction, bottomUpInduction, getErrors


HEADER = ""

LabelDict = dict()

def shiftReduceParse(linearTree, string):
    """ 
    parse listed tree items from right to left (shift reduce)
    returns a tree or None, if some nodes are not aligned
    """
    def isAligned(idx):
        alignment = [item for node in linearTree for item in node[2]]
        return idx in alignment
    
    treeBuffer = []
    
    # check whether first and last word are aligned
    # if not then remove the tree
    lastIndex = len(string)
    if not isAligned(1):
        logging.info("Align first word to first semantic node")
        linearTree[0][2] += (1,)
    if not isAligned(lastIndex):
        logging.info("Align first word to first semantic node")
        linearTree[-1][2] += (lastIndex,)

    
    for node in reversed(linearTree):
        #print "buffer:", treeBuffer
        t = IntervalTree()
        t.name = node[0]
        # Add child nodes to the current node 
        # by popping them from the buffer
        if node[1] == 0:
            pass
        else:
            for _ in range(node[1]):
                n = treeBuffer.pop()
                t.childNodes.append(n)
        
        # unaligned words 
        if node[2] == (0,):
            return None
            
            if t.childNodes:
                minInterval = min(child.interval.start for child in t.childNodes)
                maxInterval = max(child.interval.end   for child in t.childNodes)
                t.interval = Interval(minInterval,maxInterval)
            else:
                # what happens with leaf nodes that have no aligned semantic?
                t.interval = Interval()
        else:
            minInterval, maxInterval = min(node[2])-1, max(node[2])
            
            for child in t.childNodes:
                childInterval = child.interval
                minInterval, maxInterval = min(minInterval,childInterval.start), max(maxInterval,childInterval.end)
            
            t.interval = Interval(minInterval, maxInterval)
            t.alignment = node[2]
            
        treeBuffer.append(t)
    return treeBuffer[0]

def extractMeanings(f):
    alignment = re.findall(r"([^ ]+)\s*\(\{((\s*\d\s*)*)\}\)", f.replace("({ })","({ 0 })"))
    funqls = []
    for a in alignment[1:]:
        funql = [a[0], 0, []]
        if funql[0].count('X') > 0:
            funql[1] = funql[0].count('X')
            funql[0] = funql[0][:funql[0].find("(")]
        funql[2] = tuple(int(idx) for idx in a[1].split())
        funqls.append(funql)
    return funqls

def separateInput(raw_alignments):
    string = []
    funql = []
    
    # get just the lines with actual alignments, not the summary line
    for i in range(len(raw_alignments)):
        if (i+2)%3==0:
            string.append(raw_alignments[i].replace("'s","s").split())
        elif (i+1)%3==0:
            funql.append(raw_alignments[i])
        else:
            pass
    
    return string, funql

def extendLabels(funqls):
    global LabelDict
    for (name,args,_) in funqls:
        if name not in LabelDict: # int(args) > 0 and 
            LabelDict[name] = name.capitalize()[:3]

def ruleInduction(raw_alignments, induceMethod=topDownInduction, split=False):
    string, funql = separateInput(raw_alignments)
    
    ruleSet = set()
    derivationList = []
    logging.debug("=."*55)
    for idx,(s,f) in enumerate(zip(string,funql)):
        logging.debug("Alignment no. {}".format(idx+1))
        logging.debug("String: {}".format(s))
        logging.debug("Alignment: {}".format(f))
        rules = set()
        funqls  = extractMeanings(f)
        logging.debug("Semantic: {}".format(funqls))
        extendLabels(funqls)
        tree    = shiftReduceParse(funqls, s)
        if not tree:
            logging.info("Empty tree")
            continue
        rules   = induceMethod(tree, s, split, LabelDict)
        if rules:
            derivationList.append((" ".join(s),tree.funql(),tree.derivation()))
        ruleSet = ruleSet | rules
        
        strSet = set(s for r in rules for s in r.s.split(" "))
        
        logging.debug(strSet) 
        logging.debug("=."*55)
        
    return ruleSet, derivationList

def storeRules(filename, ruleSet):
    # write grammar to file
    grammar_irtg = open(filename, "w")
    grammar_irtg.write(HEADER)
    grammar_irtg.write("interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n")
    grammar_irtg.write("interpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n")
    grammar_irtg.write("\n\n")
    for r in ruleSet:
        grammar_irtg.write(str(r)+"\n")
    grammar_irtg.close()

def printRules(ruleSet):
    print HEADER
    print "interpretation s: de.up.ling.irtg.algebra.StringAlgebra"
    print "interpretation t: de.up.ling.irtg.algebra.TreeAlgebra"
    print "\n\n"
    for r in ruleSet:
        print r

def main():
    logging.basicConfig(filename='induction.log', filemode='a', level=logging.INFO, format='%(asctime)s (%(levelname)s): %(message)s')
    
    if len(sys.argv) < 3:
        raise Exception("Unexpected number of arguments")

    alignmentFile = ""
    ruleSplit = ""
    nonterminalSplit = ""
    splitSize = 0

    alignmentFile       = sys.argv[1]
    ruleSplit           = sys.argv[2] if sys.argv[2] in ("left", "right", "both") else "both"
    nonterminalSplit    = sys.argv[3] if sys.argv[3] in ("nosplit", "semsplit") else "nosplit"
    grammarOutput       = sys.argv[4]
    llmtrainingOutput   = sys.argv[5]
    
    ruleSet = set()
    trainingCorpus = []
    logging.info("Init through user input")
    logging.info("config: {} {} {} {} {}".format(alignmentFile, ruleSplit, nonterminalSplit, grammarOutput, llmtrainingOutput))
    
    # read alignments and save to string and funql lists
    raw_alignments = open(alignmentFile, "r").read().split("\n")
    split = (nonterminalSplit == "semsplit")
    if ruleSplit in ("left", "both"):
        logging.info("top-down induction")
        rules, train = ruleInduction(raw_alignments, topDownInduction, split)
        ruleSet = ruleSet | rules
        trainingCorpus.extend(train)
    if ruleSplit in ("right", "both"):
        logging.info("bottom-up induction")
        rules, train = ruleInduction(raw_alignments, bottomUpInduction, split)
        ruleSet = ruleSet | rules
        trainingCorpus.extend(train)

    logging.info("store inducted rules in '{}'".format(grammarOutput))
    storeRules(grammarOutput, ruleSet)

    logging.info("store the llm training corpus to '{}'".format(llmtrainingOutput))
    # write grammar to file
    trainLLM = open(llmtrainingOutput, "w")
    trainLLM.write("# IRTG annotated corpus file, v1.0\n")
    trainLLM.write("# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n")
    trainLLM.write("# interpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n\n\n")
    trainLLM.write(HEADER)
    for r in trainingCorpus:
        trainLLM.write("\n".join(r)+"\n")
    trainLLM.close()

    logging.info("Statistical output")
    DELETES, INVALIDS, EXCEPTIONS = getErrors()
    logging.info("number of exceptions:" + str(EXCEPTIONS))
    logging.info("number of invalids:" + str(INVALIDS))
    logging.info("number of deletions:" + str(DELETES))
    
if __name__ == "__main__":
    main()

#!/usr/bin/env python

"""
Induct grammar from sentence alignments between tokenized strings and tokenized trees
"""
import traceback
import sys

import re

from Rule import Rule
from IntervalTree import IntervalTree
from IntervalTree import Interval

DELETES = 0
INVALIDS = 0
EXCEPTIONS = 0

LabelDict = dict()

def shiftReduceParse(linearTree):
    """ 
    parse listed tree items from right to left (shift reduce)
    returns a tree or None, if some nodes are not aligned
    """
    treeBuffer = []
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

def getStringRule(interval, string):
    s = dict(enumerate(string))
    flatInterval = interval.flatten()
    
    stringRule  = s[flatInterval[0]] if flatInterval[0] >= 0 else "?1"
    varIdx      =   1                if flatInterval[0] >= 0 else   2
    for i in flatInterval[1:]:
        if i >= 0:
            stringRule = "*({},{})".format(stringRule, s[i])
        else:
            stringRule = "*({},?{})".format(stringRule, varIdx)
            varIdx += 1
    return stringRule.replace("\'s",'\"\'s\"').replace("50","\"50\"")

def getMeaningRule(name, argnum):
    if argnum > 0:
        return name.replace("+"," ").replace("0","\"0\"") + "({})".format(",".join("?"+str(i+1) for i in range(argnum)))
    else:
        return name.replace("+"," ").replace("0","\"0\"")

def mergeTreeNodes(n1, n2):
    treeNode = IntervalTree()

def splitTree1(node):
    interval = node.interval
    for child in node.childNodes:
        interval = interval.without(child.interval)
    return interval

def splitTree2(cNode, pNode):
    pass

def induceRule1(tree, s, split=False):
    """
    Rule Generation
    """
    global INVALIDS, DELETES
    
    rules = set()
    treeBuffer = [(tree,'S!')]
    while treeBuffer:
        try:
            r = Rule()
            node, label = treeBuffer.pop()
            
            arguments = ['X'] * len(node.childNodes) if not split else [LabelDict[child.name] for child in node.childNodes]
            
            for idx,child in enumerate(node.childNodes):
                treeBuffer.append((child,arguments[idx]))
            #
            # create rule label
            #
            r.label = getLabel(label, node.idx, arguments)
            #
            # create string representation
            #
            interval = splitTree1(node)
            r.s = getStringRule(interval, s)
            #
            # create meaning representation
            #
            r.t = getMeaningRule(node.name,len(node.childNodes))
            
            if len(node.childNodes) != interval.flatten().count(-1):
                #print "Invalid number of arguments"
                INVALIDS += 1
                continue
            if r.s in ("?1", "*(?1,?2)"):
                #print "deleting homomorphism..."
                #print r
                #raw_input()
                DELETES += 1
                continue
            
            rules.add(r)

        except Exception as e:
            print traceback.format_exc()
            raw_input()
            pass

    return rules

def getLabel(start, idx, args):
    assert type(idx) == str
    
    return (start + " -> " + idx +
            ("({})".format(",".join(args)) if args else ""))

def induceRule2(tree, s, split=False):
    """
    Rule Generation
    """
    global INVALIDS, DELETES, EXCEPTIONS
    
    rules = set()
    treeBuffer = [(tree,tree.interval,'S!')]

    try:
        while treeBuffer:
            r = Rule()
            node, nodeInterval, label = treeBuffer.pop()
            arguments = ['X'] * len(node.childNodes) if not split else [LabelDict[child.name] for child in node.childNodes]
            if len(node.alignment) == 1:
                alignedWord = node.alignment[0]
                tmpInterval = Interval(nodeInterval.first(), alignedWord)
            else:
                minWord, maxWord = min(node.alignment), max(node.alignment)
                tmpInterval = Interval(minWord-1, maxWord)
            
            childsInterval = nodeInterval.without(tmpInterval)
            interval = tmpInterval
            
            if node.childNodes:
                splitIdx = node.childNodes[0].interval.last()
                tmpInterval = Interval(childsInterval.first(),splitIdx+1)
                
                treeBuffer.append((node.childNodes[0],tmpInterval,arguments[0]))
                for idx,child in enumerate(node.childNodes[1:]):
                    oldSplit = splitIdx
                    splitIdx = child.interval.last()
                    tmpInterval = Interval(oldSplit+1,splitIdx+1)
                    treeBuffer.append((child,tmpInterval,arguments[idx+1]))
            
            for _ in range(len(node.childNodes)): interval.addPlaceholder()
            
            #
            # create rule label
            #
            r.label = getLabel(label, node.idx, arguments)
            #
            # create string representation
            #
            r.s = getStringRule(interval, s)
            #
            # create meaning representation
            #
            r.t = getMeaningRule(node.name,len(node.childNodes))
            
            if len(node.childNodes) != interval.flatten().count(-1):
                #print "Invalid number of arguments"
                INVALIDS += 1
                continue
            if r.s in ("?1", "*(?1,?2)"):
                #print "deleting homomorphism..."
                DELETES += 1
                continue
            
            rules.add(r)

    except Exception as e:
        #print traceback.format_exc()[:30], "..."
        #raw_input()
        EXCEPTIONS += 1
        pass

    return rules

def separateInput(raw_alignments):
    string = []
    funql = []
    
    # get just the lines with actual alignments, not the summary line
    for i in range(len(raw_alignments)):
        if (i+2)%3==0:
            string.append(raw_alignments[i].split())
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

def ruleInduction(raw_alignments, induceMethod=induceRule1, split=False):
    string, funql = separateInput(raw_alignments)
    
    ruleSet = set()
    derivationList = []
    
    for (s,f) in zip(string,funql):
        rules = set()
        funqls  = extractMeanings(f)
        extendLabels(funqls)
        tree    = shiftReduceParse(funqls)
        if not tree: continue
        rules   = induceMethod(tree, s, split)
        if rules:
            derivationList.append((" ".join(s),tree.funql(),tree.derivation()))
        ruleSet = ruleSet | rules
        
    return ruleSet, derivationList

def storeRules(filename, ruleSet):
    header = "/*\nInduced grammar from aligned sentences\ns = tokenized string from geoquery corpus\nt = tree elements from geoquery function query language (variable-free)\n*/\n\ninterpretation s: de.up.ling.irtg.algebra.StringAlgebra\ninterpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n\n\n"
    # write grammar to file
    grammar_irtg = open(filename, "w")
    grammar_irtg.write(header)
    for r in ruleSet:
        grammar_irtg.write(str(r)+"\n")
    grammar_irtg.close()

def printRules(ruleSet):
    header = "/*\nInduced grammar from aligned sentences\ns = tokenized string from geoquery corpus\nt = tree elements from geoquery function query language (variable-free)\n*/\n\ninterpretation s: de.up.ling.irtg.algebra.StringAlgebra\ninterpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n\n\n"
    print header
    for r in ruleSet:
        print r

def main():
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
    
    # read alignments and save to string and funql lists
    raw_alignments = open(alignmentFile, "r").read().split("\n")
    split = (nonterminalSplit == "semsplit")
    if ruleSplit in ("left",  "both"):
        rules, train = ruleInduction(raw_alignments, induceRule1, split)
        ruleSet = ruleSet | rules
        trainingCorpus.extend(train)
    if ruleSplit in ("right", "both"):
        rules, train = ruleInduction(raw_alignments, induceRule2, split)
        ruleSet = ruleSet | rules
        trainingCorpus.extend(train)

    storeRules(grammarOutput, ruleSet)

    header = "/*\nInduced grammar from aligned sentences\ns = tokenized string from geoquery corpus\nt = tree elements from geoquery function query language (variable-free)\n*/\n\ninterpretation s: de.up.ling.irtg.algebra.StringAlgebra\ninterpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n\n\n"
    # write grammar to file
    trainLLM = open(llmtrainingOutput, "w")
    trainLLM.write(header)
    for r in trainingCorpus:
        trainLLM.write("\n".join(r)+"\n")
    trainLLM.close()
    
    
    sys.stderr.write("number of exceptions:" + str(EXCEPTIONS) + "\n")
    sys.stderr.write("number of invalids:" + str(INVALIDS) + "\n")
    sys.stderr.write("number of deletions:" + str(DELETES) + "\n")

#def main():
    ## read alignments and save to string and funql lists
    #raw_alignments = open("../data/string2geo.A3.final5BEST").read().split("\n")
    
    #ruleSet1 = ruleInduction(raw_alignments, induceRule1)
    #storeRules("../data/grammar1.irtg", ruleSet1)
    
    #ruleSet2 = ruleInduction(raw_alignments, induceRule2)
    #storeRules("../data/grammar2.irtg", ruleSet2)

    #storeRules("../data/grammar3.irtg", ruleSet1 | ruleSet2)
    
    #print "number of exceptions:", EXCEPTIONS
    #print "number of invalids:", INVALIDS
    #print "number of deletions:", DELETES
    
if __name__ == "__main__":
    main()

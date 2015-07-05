#!/usr/bin/env python

"""
Induct grammar from sentence alignments between tokenized strings and tokenized trees
"""
import traceback

import re

from Rule import Rule
from IntervalTree import IntervalTree
from IntervalTree import Interval

DELETES = 0
INVALIDS = 0

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

def induceRule(tree, s):
    """
    Rule Generation
    """
    global INVALIDS, DELETES
    
    rules = set()
    treeBuffer = [tree]
    while treeBuffer:
        try:
            r = Rule()
            node = treeBuffer.pop()
            treeBuffer.extend(node.childNodes)
            #
            # create rule label
            #
            if node.name == "answer":
                r.createLabel("S!", len(node.childNodes))
            else:
                r.createLabel("X", len(node.childNodes))
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
                DELETES += 1
                continue
            
            rules.add(r)

        except Exception as e:
            print traceback.format_exc()
            raw_input()
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


def main():
    # read alignments and save to string and funql lists
    raw_alignments = open("../data/string2geo.A3.final5BEST").read().split("\n")
    
    string, funql = separateInput(raw_alignments)
    
    ruleSet = set()

    for (s,f) in zip(string,funql):
        funqls  = extractMeanings(f)
        tree    = shiftReduceParse(funqls)
        if not tree: continue
        #print ">>", tree
        #print ">>", f
        #print ">>", funqls
        #raw_input()
        rules   = induceRule(tree, s)
        ruleSet = ruleSet | rules
    
    #for rule in ruleSet:
    #    print rule, "\n"
    print len(ruleSet), "rules extracted"
    print DELETES, "deleting homorphisms"
    print INVALIDS, "invalid argument exceptions"
    
    # append header
    header = "/*\nInduced grammar from aligned sentences\ns = tokenized string from geoquery corpus\nt = tree elements from geoquery function query language (variable-free)\n*/\n\ninterpretation s: de.up.ling.irtg.algebra.StringAlgebra\ninterpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n\n\n"
    # write grammar to file
    grammar_irtg = open("../data/grammar.irtg", "w")
    grammar_irtg.write(header)
    for r in ruleSet:
        grammar_irtg.write(str(r)+"\n")
    grammar_irtg.close()

if __name__ == "__main__":
    main()

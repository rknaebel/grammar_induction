#!/usr/bin/python
#
# author:
# 
# date: 
# description:
#

import logging
import traceback

from Rule import Rule
from IntervalTree import Interval

DELETES = 0
INVALIDS = 0
EXCEPTIONS = 0

def getErrors():
    return (DELETES, INVALIDS, EXCEPTIONS)

def getLabel(start, idx, args):
    assert type(idx) == str
    
    return (start + " -> " + idx +
            ("({})".format(",".join(args)) if args else ""))

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


def topDownInduction(tree, s, split=False, LabelDict=None):
    """
    Rule Generation
    """
    global INVALIDS, DELETES, EXCEPTIONS

    logging.info("string: {}".format(s))
    logging.info("tree: {}".format(tree))
    
    rules = set()
    treeBuffer = [(tree,'S!')]
    try:
        while treeBuffer:
        
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
            logging.debug("node.interval:".format(node.interval))
            interval = node.interval
            for child in node.childNodes:
                interval = interval.without(child.interval)
            logging.debug("Interval:".format(interval))
            r.s = getStringRule(interval, s)
            #print r.s
            #
            # create meaning representation
            #
            r.t = getMeaningRule(node.name,len(node.childNodes))
            
            if len(node.childNodes) != interval.flatten().count(-1):
                logging.debug("Invalid number of arguments: child({}) interval({})".format(
                    len(node.childNodes),
                    interval.flatten().count(-1))
                )
                INVALIDS += 1
                return set()
            if r.s in ("?1", "*(?1,?2)"):
                logging.debug("Deleting homorphism: {}".format(r.s))
                DELETES += 1
                return set()
            
            rules.add(r)

    except Exception as e:
        logging.error(e)
        EXCEPTIONS += 1
        return set()

    return rules


def bottomUpInduction(tree, s, split=False, LabelDict=None):
    """
    Rule Generation
    """
    global INVALIDS, DELETES, EXCEPTIONS

    logging.info("string: {}".format(s))
    logging.info("tree: {}".format(tree))
    
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
                logging.debug("Invalid number of arguments: child({}) interval({})".format(
                    len(node.childNodes),
                    interval.flatten().count(-1))
                )
                INVALIDS += 1
                return set()
            if r.s in ("?1", "*(?1,?2)"):
                logging.debug("Deleting homorphism: {}".format(r.s))
                DELETES += 1
                return set()
            
            rules.add(r)

    except Exception as e:
        logging.error(e)
        EXCEPTIONS += 1
        return set()

    return rules

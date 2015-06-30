#!/usr/bin/env python

"""
Induct grammar from sentence alignments between tokenized strings and tokenized trees
"""

import re

# class for a rule object with a label, string, and tree representation
class Rule(object):
    count = 0
    def __init__(self):
        self.label = None
        self.s = None
        self.t = None
        self.i = Rule.count
        Rule.count += 1

    def createLabel(self, start, argnum):
        self.label = start + " -> s" + str(self.i) + ("({})".format(",".join(["X"]*argnum)) if argnum > 0 else "")

    def createMeaning(self, name, argnum):
        if argnum > 0:
            self.t = name.replace("+"," ").replace("0","\"0\"") + "({})".format(",".join("?"+str(i+1) for i in range(argnum)))
        else:
            self.t = name.replace("+"," ").replace("0","\"0\"")
    
    # the __hash__ and __eq__ is used to idenfity duplicate rules later
    def __hash__(self):
        return hash((self.s,self.t))
    
    def __str__(self):
        return "{}\n[s] {}\n[t] {}\n".format(self.label, self.s, self.t)

    def __repr__(self):
        return "({}-[s]:{}-[t]:{})".format(self.label, self.s, self.t)
    
    def __eq__(self, other):
        return self.s == other.s and self.t == other.t


class IntervalTree:
    def __init__(self):
        self.name = ""
        self.interval = (0,0)
        self.childNodes = []
        self.alignment = []

    def sortChildNodes(self):
        self.childNodes.sort(key=lambda t: t.interval[0])

    def induceIrtgRules(self, sentence):
        pass

    def setAlignment(self,xs):
        xs = sorted(xs)
        self.alignment = xs
        minInterval = xs[ 0]-1
        maxInterval = xs[-1]
        # TODO:
        # Im using max(..., 0) to have at least index 0
        # this is used for unaligned words so far, but will be changed
        # later to have intervalls within surrounding semantic representations
        if self.childNodes:
            minChilds = min(self.childNodes, key=lambda t: t.interval[0]).interval[0]
            maxChilds = max(self.childNodes, key=lambda t: t.interval[1]).interval[1]
            self.interval = (max(min(minInterval, minChilds), 0), max(maxInterval, maxChilds))
        else:
            self.interval = (max(0, minInterval), maxInterval)
        

    def __str__(self):
        interval = "[{},{}]".format(self.interval[0],self.interval[1])
        if self.childNodes:
            return "{}{}({})".format(self.name,interval, ",".join(str(t) for t in self.childNodes))
        else:
            return "{}{}".format(self.name,interval)

    __repr__ = __str__


def main():
    # read alignments and save to string and funql lists
    raw_alignments = open("../data/string2geo.A3.final5BEST").read().split("\n")
    
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

    ruleSet = set()

    for (s,f) in zip(string,funql):
        s = dict(enumerate(s))
        #print ">", s
        #print ">", f
        alignment = re.findall(r"([^ ]+)\s*\(\{((\s*\d\s*)*)\}\)", f.replace("({ })","({ 0 })"))
        funqls = []
        for a in alignment[1:]:
            funql = [a[0], 0, []]
            if funql[0].count('X') > 0:
                funql[1] = funql[0].count('X')
                funql[0] = funql[0][:funql[0].find("(")]
            funql[2] = tuple(int(idx) for idx in a[1].split())
            funqls.append(funql)

        # parse listed tree items from right to left (shift reduce)
        treeBuffer = []
        for node in reversed(funqls):
            t = IntervalTree()
            t.name = node[0]
            if node[1] == 0:
                pass
            else:
                for _ in range(node[1]):
                    n = treeBuffer.pop()
                    t.childNodes.append(n)
                t.sortChildNodes()
            t.setAlignment(node[2])
            treeBuffer.append(t)
        tree = treeBuffer[0]
        try:
            #
            # Rule generation
            #
            rules = set()
            treeBuffer = [tree]
            while treeBuffer:
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
                interval = range(*node.interval)
                for child in node.childNodes:
                    #print node
                    #print interval
                    #print node.childNodes
                    start, end = child.interval
                    startPos, endPos = interval.index(start), interval.index(end-1)
                    interval = interval[:startPos] + [-1] + interval[endPos+1:]
                stringRule  = s[interval[0]] if interval[0] >= 0 else "?1" 
                varIdx      =   1  if s[0] >= 0 else   2 
                for i in interval[1:]:
                    if i >= 0:
                        stringRule = "*({},{})".format(stringRule, s[i])
                    else:
                        stringRule = "*({},?{})".format(stringRule, varIdx)
                        varIdx += 1
                #print " ".join(s[i] for i in interval if i >= 0)
                r.s = stringRule.replace("\'s",'\"\'s\"').replace("50","\"50\"")
                #r.s = re.sub(r"([0|50])",r'"\1"',r.s)
                #
                # create meaning representation
                #
                r.createMeaning(node.name,len(node.childNodes))
                
                rules.add(r)
            
            ruleSet = ruleSet | rules
        
        except Exception:
            pass
    
    #for rule in ruleSet:
    #    print rule, "\n"
    print len(ruleSet), "rules extracted"
    


    # append header
    header = "/*\nInduced grammar from aligned sentences\ns = tokenized string from geoquery corpus\nt = tree elements from geoquery function query language (variable-free)\n*/\n\ninterpretation s: de.up.ling.irtg.algebra.StringAlgebra\ninterpretation t: de.up.ling.irtg.algebra.TreeAlgebra\n\n\n"
    
    # write grammar to file
    #grammar_irtg = open("../data/grammar.irtg", "w")
    #grammar_irtg.write(header)
    #for r in ruleSet:
    #    grammar_irtg.write(str(r)+"\n")
    #grammar_irtg.close()

if __name__ == "__main__":
    main()

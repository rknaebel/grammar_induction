#!/usr/bin/env python

"""
Induct grammar from sentence alignments between tokenized strings and tokenized trees
"""

import re

## class for a rule object with a label, string, and tree representation
#class Rule(object):
    #def __init__(self):
        #self.label = None
        #self.s = None
        #self.t = None
    
    ## the __hash__ and __eq__ is used to idenfity duplicate rules later
    #def __hash__(self):
        #return hash(('[s]', self.s,
                     #'[t]', self.t))
    
    #def __eq__(self, other):
        #return self.s == other.s and self.t == other.t
    
## functional token object with the functional token and the index of the string tokens aligned to it
#class FunqlTok(object):
    #def __init__(self):
        #self.funql = None
        #self.s_index = None

## general function to transform a list to text
#def list_to_txt(unlist):
    #txt = ""
    #for item in unlist:
        #txt = txt + item + "\n"
    #return txt 

# function to extract the alignments with list of string and funql sentences
def extract_alignments(string, funql):
    funql_tokens = []
    
    for item in funql:
        alignment = re.findall(r"([\w_()'_+,]+)\s*\(\{((\s*\d+\s*)*)\}\)", item.replace("({ })","({ 0 })"))
        funql_tok_sent = []
        for phrase in alignment:
            funql_tok = FunqlTok()
            funql_tok.funql = phrase[0]
            funql_tok.s_index = map(int,phrase[1].strip().split(" "))
            funql_tok_sent.append(funql_tok)
        funql_tokens.append(funql_tok_sent)
            
    print "A list of the string token indexes for the first funql representation", funql_tokens[0][0].funql, ":\n", funql_tokens[0][0].s_index, "\n"
    
    string_tokens = []
    
    for sentence in string:
        sentence = sentence[:len(sentence)-1]
        string_tokens.append(sentence.split(" "))
    
    # compare string tokens to funql tokens to get alignments
    alignments = []
    
    for i in range(len(string_tokens)):
        for j in range(len(funql_tokens[i])):
            alignment = []
            alignment.append(funql_tokens[i][j].funql)
            for k in range(len(string_tokens[i])):
                for l in range(len(funql_tokens[i][j].s_index)):
                    if k + 1 == funql_tokens[i][j].s_index[l]:
                        alignment.append(string_tokens[i][k])
            
            alignments.append(alignment)
    print "A list of the first 5 alignments, where the 0 index is always the funql representation and indexes 1: are the string tokens:\n", alignments[0:6]
    return alignments

def generate_rules(aligned_tokens):
    rules = []
    
    for i in range(len(aligned_tokens)):
        tok = aligned_tokens[i] # token is a list like ['NULL', 'me', 'the]
        if tok[0] == "NULL": # for string tokens not aligned to funql representations
            for j in range(len(tok[1:])):
                rule = Rule()
                rule.label = "X -> s" + str(i) + str(j+1) + "(X)"
                rule.s = "*(" + tok[j+1] + ", ?1)"
                rule.t = "?1"
                rules.append(rule)
        elif tok[0] == "answer(X)": # specifically for answer(X)
            rule = Rule()                
            rule.label = "S! -> s" + str(i) + "(X)"
            if len(tok) == 1:
                rule.s = "?1"
            elif len(tok) == 2:
                rule.s = "*(" + tok[1] + ", ?1)"
            else:
                rule.s = "?1"
            rule.t = tok[0].replace("(X)","(?1)").replace("(X,X)","(?1,?2)").replace("(X,X,X)","(?1,?2,?3)")    
            rules.append(rule)
        elif "X)" not in tok[0]: # if the funql representation is a leaf node
            rule = Rule()
            rule.label = "X -> s" + str(i) + "(X)"
            if len(tok) == 2:
                rule.s = tok[1]
            else:
                rule.s = "?1"
            rule.t = tok[0].replace("(X)","(?1)").replace("(X,X)","(?1,?2)").replace("(X,X,X)","(?1,?2,?3)") 
            rules.append(rule)
        else:          
            rule = Rule()
            rule.label = "X -> s" + str(i) + "(X)"
            if len(tok) == 1:
                rule.s = "?1"
            elif len(tok) == 2:
                rule.s = "*(" + tok[1] + ", ?1)"
            else: # TODO what about funql representations mapped to multiple string tokens, also when they're not next to each other?
                rule.s = "?1"
            rule.t = tok[0].replace("(X)","(?1)").replace("(X,X)","(?1,?2)").replace("(X,X,X)","(?1,?2,?3)") 
            rules.append(rule)
            
    # just for testing
    print "The rules for the first sentence are:\n"
    for i in range(0,7):        
        print rules[i].label
        print rules[i].s
        print rules[i].t
        print ""
    
    # remove duplicate rules
    rules = list(set(rules))
    printable = []
    for i in range(len(rules)):
        printable.append(rules[i].label)
        printable.append("[s] " + rules[i].s)
        printable.append("[t] " + rules[i].t)
        printable.append("")
    
    return printable


class IntervalTree:
    def __init__(self):
        self.name = ""
        self.interval = (0,0)
        self.childNodes = []
        self.alignment = []

    def induceIRTG(self, sentence):
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

class TreeAlignment:
    pass








def main():
    grammar = []
      
    # append header
    header = "/*\nInduced grammar from aligned sentences\ns = tokenized string from geoquery corpus\nt = tree elements from geoquery function query language (variable-free)\n*/\n\ninterpretation s: de.up.ling.irtg.algebra.StringAlgebra\ninterpretation t: de.up.ling.irtg.algebra.TreeAlgebra"
    grammar.append(header)
    grammar.append("")
  
    # read alignments and save to string and funql lists
    raw_alignments = open("../data/string2geo.A3.finalNBEST").read().split("\n")
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

    for (s,f) in zip(string,funql):
        print ">", s
        print ">", f
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
            t.setAlignment(node[2])
            treeBuffer.append(t)
        
        print treeBuffer[0]

        
                
        print alignment
        raw_input()
        #break

    












    # just for testing
    #print "The first string in the file is:\n", string[0], "\n"
    #print "The first funql representation in the file is:\n", funql[0], "\n"
    
    ## get aligned tokens from sentences
    #aligned_tokens = extract_alignments(string, funql)
    
    ## get list of rules from function and add to grammar
    #for item in generate_rules(aligned_tokens):
        #grammar.append(item)

    ## write grammar to file
    #grammar_irtg = open("../data/grammar.irtg", "w")
    #grammar_irtg.write(list_to_txt(grammar))
    #grammar_irtg.close()

if __name__ == "__main__":
    main()



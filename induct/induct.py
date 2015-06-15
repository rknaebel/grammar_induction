#!/usr/bin/env python

"""
Induct grammar from sentence alignments between tokenized strings and tokenized trees
"""

import re
import collections

from pprint import pprint

# class for a rule object with a label, string, and tree representation
class Rule(object):
    count = 0
    def __init__(self):
        self.label = None
        self.s = None
        self.t = None
        self.i = Rule.count
        Rule.count += 1
    
    # the __hash__ and __eq__ is used to idenfity duplicate rules later
    def __hash__(self):
        return hash((self.s,self.t))
    
    def __str__(self):
        return "{}\n[s] {}\n[t] {}".format(self.label, self.s, self.t)
    
    def __eq__(self, other):
        return self.s == other.s and self.t == other.t
    
# functional token object with the functional token and the index of the string tokens aligned to it
class FunqlTok(object):
    def __init__(self):
        self.funql = None
        self.s_index = None
    
    def __str__(self):
        return "{}-{}".format(self.funql,self.s_index)
    __repr__ = __str__

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
    
    string_tokens = [sentence[:-1].split(" ") for sentence in string]
    
    # compare string tokens to funql tokens to get alignments
    alignments = collections.defaultdict(set)
    
    for i,funql_token in enumerate(funql_tokens):
        for token in funql_token:
            for idx in token.s_index:
                word = string_tokens[i][idx-1]
                alignments[token.funql].add(word)

    print "A list of the first 5 alignments, where the 0 index is always the funql representation and indexes 1: are the string tokens:\n", alignments
    return alignments

def generate_rules(alignment):
    rules = set()
    
    for i,(tok, words) in enumerate(alignment.iteritems()):
        #print i, tok, words
        #raw_input()
        for word in words:
            if tok == "NULL": # for string tokens not aligned to funql representations
                rule = Rule()
                rule.label = "X -> s" + str(rule.i) + "(X)"
                rule.s = "*(" + word + ", ?1)"
                rule.t = "?1"
                rules.add(rule)
            elif tok == "answer(X)": # specifically for answer(X)
                rule = Rule()                
                rule.label = "S! -> s" +  str(rule.i) + "(X)"
                if len(tok) == 1:
                    rule.s = "?1"
                elif len(tok) == 2:
                    rule.s = "*(" + tok[1] + ", ?1)"
                else:
                    rule.s = "?1"
                rule.t = tok[0].replace("(X)","(?1)").replace("(X,X)","(?1,?2)").replace("(X,X,X)","(?1,?2,?3)")    
                rules.add(rule)
            elif "X)" not in tok: # if the funql representation is a leaf node
                rule = Rule()
                rule.label = "X -> s" +  str(rule.i) + "(X)"
                if len(tok) == 2:
                    rule.s = tok[1]
                else:
                    rule.s = "?1"
                rule.t = tok[0].replace("(X)","(?1)").replace("(X,X)","(?1,?2)").replace("(X,X,X)","(?1,?2,?3)") 
                rules.add(rule)
            else:          
                rule = Rule()
                rule.label = "X -> s" +  str(rule.i) + "(X)"
                if len(tok) == 1:
                    rule.s = "?1"
                elif len(tok) == 2:
                    rule.s = "*(" + tok[1] + ", ?1)"
                else: # TODO what about funql representations mapped to multiple string tokens, also when they're not next to each other?
                    rule.s = "?1"
                rule.t = tok[0].replace("(X)","(?1)").replace("(X,X)","(?1,?2)").replace("(X,X,X)","(?1,?2,?3)") 
                rules.add(rule)
            
    # just for testing
    print "The rules for the first sentence are:\n"
    for i,item in enumerate(rules):        
        print item, "\n"
        #if i > 10: break
    
    return rules

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
        if i%3 == 1:
            string.append(raw_alignments[i])
        elif i%3 == 2:
            funql.append(raw_alignments[i])
        else:
            pass
    
    # just for testing
    print "The first string in the file is:\n", string[0], "\n"
    print "The first funql representation in the file is:\n", funql[0], "\n"
    
    # get aligned tokens from sentences
    alignment = extract_alignments(string, funql)
    
    # get list of rules from function and add to grammar
    grammar = generate_rules(alignment)
    
    # write grammar to file
    grammar_irtg = open("../data/grammar.irtg", "w")
    grammar_irtg.write("\n".join(map(str,grammar)))
    grammar_irtg.close()

if __name__ == "__main__":
    main()



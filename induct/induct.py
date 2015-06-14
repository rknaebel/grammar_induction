#!/usr/bin/env python

"""
Induct grammar from sentence alignments between tokenized strings and tokenized trees
"""

import re

class Rule(object):
    def __init__(self):
        self.label = None
        self.s = None
        self.t = None
    
    def __hash__(self):
        return hash(('[s]', self.s,
                     '[t]', self.t))
    
    def __eq__(self, other):
        return self.s == other.s and self.t == other.t
    

class FunqlTok(object):
    def __init__(self):
        self.funql = None
        self.s_index = None


def list_to_txt(unlist):
    txt = ""
    for item in unlist:
        txt = txt + item + "\n"
    # have to remove last newline for Giza++
    return txt #[:(len(txt)-2)]

def extract_alignments(string, funql):
    funql_list = []
    
    for item in funql:
        funql_list.append(item.replace("({ })","({ 0 })").replace(" ({ ",", ").split(" }) "))

    funql_tokens = []

    for sentence in funql_list:
        sentence = sentence[:len(sentence)-1]
        #print sentence
        funql_tok_sent = []
        for phrase in sentence:
            funql_tok = FunqlTok()
            phrase = phrase.split(", ")
            funql_tok.funql = phrase[0]
            funql_tok.s_index = phrase[1]
            funql_tok.s_index = [int(i) for i in funql_tok.s_index.split(" ")]
            funql_tok_sent.append(funql_tok)
        
        funql_tokens.append(funql_tok_sent)
            
    print funql_tokens[0][0].s_index
    
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
                    #print funql_tokens[i][j].s_index[l]
                    if k + 1 == funql_tokens[i][j].s_index[l]:
                        #string_phrase = []
                        #string_phrase.append(string_tokens[i][k])
                        #alignment.append("".join(string_phrase))
                        alignment.append(string_tokens[i][k])
            
            #alignment = [alignment[0], " ".join(alignment[1:len(alignment)])]
            alignments.append(alignment)
    print alignments[0:5]
    return alignments

def generate_rules(aligned_tokens):
    rules = []
    
    for i in range(len(aligned_tokens)):
        
        if aligned_tokens[i][0] == "NULL":
            for j in range(len(aligned_tokens[i][1:])):
                rule = Rule()
                rule.label = "X -> s" + str(i) + str(j+1) + "(X)"
                rule.s = "*(" + aligned_tokens[i][j+1] + ", ?1)"
                rule.t = "?1"
                rules.append(rule) 
        
    for i in range(0,3):        
        print rules[i].label
        print rules[i].s
        print rules[i].t
    
    # remove duplicates
    rules = list(set(rules))
    printable = []
    for i in range(len(rules)):
        printable.append(rules[i].label)
        printable.append("[s] " + rules[i].s)
        printable.append("[t] " + rules[i].t)
        printable.append("")
    
    return printable

def main():
    grammar = []
      
    # append header
    header = "# IRTG unannotated corpus file, v1.0\n#\n# interpretation s: de.up.ling.irtg.algebra.StringAlgebra\n# interpretation t: de.up.ling.irtg.algebra.TreeAlgebra"
    grammar.append(header)
    grammar.append("")
  
    # read alignments
    raw_alignments = open("../data/string2geo.A3.finalNBEST").read().split("\n")
    string = []
    funql = []
   
    for i in range(len(raw_alignments)):
        if (i+2)%3==0:
            string.append(raw_alignments[i])
        elif (i+1)%3==0:
            funql.append(raw_alignments[i])
        else:
            pass
    
    print string[0]
    print funql[0]
    
    aligned_tokens = extract_alignments(string, funql)  
    for item in generate_rules(aligned_tokens):
        grammar.append(item)  

    grammar_irtg = open("../data/grammar.irtg", "w")
    grammar_irtg.write(list_to_txt(grammar))
    grammar_irtg.close()

if __name__ == "__main__":
    main()



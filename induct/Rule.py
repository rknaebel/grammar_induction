#!/usr/bin/python
#
# author:
# 
# date: 
# description:
#

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
        return hash((self.label,self.s,self.t))
    
    def __str__(self):
        return "{}\n[s] {}\n[t] {}\n".format(self.label, self.s, self.t)

    def __repr__(self):
        return "({}-[s]:{}-[t]:{})".format(self.label, self.s, self.t)
    
    def __eq__(self, other):
        return self.s == other.s and self.t == other.t


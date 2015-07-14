#!/usr/bin/python
#
# author:
# 
# date: 
# description:
#
import sys
import re
import itertools
import random

def makeRule(lhs, idx, args, prob, stringRule, semanticRule):
    return "{} -> {}{} [{}]\n  {}\n  {}\n".format(
        lhs,
        str(idx),
        ("(" + ", ".join(args) + ")") if args else "",
        abs(prob + (random.randint(0,1)*2-1)*(random.random()/10.0)),
        stringRule.strip(),
        semanticRule.strip()
    )

def wait(s):
    print s
    raw_input()

def induceRules(rule, inductionSize):
    newRules = []
    (ruleHead,stringRule,semanticRule) = rule.split("\n")
    match = re.match(r"([\w!]+)\s+->\s+s(\d+)(\((\w[, ]*)+\))?\s+(\[[-.0-9E]+\])?", ruleHead)
    if match:
        lhs, idx, args, _, prob = match.groups()
        prob = float(prob[1:-1])
        argNum = len(re.findall(r"[A-Z][a-zA-Z0-9]*",args)) if args else 0
        newArgs = ["X{}".format(i+1) for i in range(inductionSize)]
        if lhs == "S!":
            if argNum > 0:
                for comb in itertools.combinations(newArgs, argNum):
                    new_idx = "s" + str(idx) + "_" + "_".join(a.lower() for a in comb)
                    r = makeRule(lhs, new_idx, comb, prob, stringRule, semanticRule)
                    newRules.append(r)
            else:
                wait(rule)
                newRules.append(rule)
        else:
            if argNum > 0:
                for comb in itertools.combinations(newArgs, argNum):
                    for arg in newArgs:
                        new_idx = "s" + str(idx) + "_" + arg.lower() + "_" + "_".join(a.lower() for a in comb)
                        r = makeRule(arg, new_idx, comb, prob, stringRule, semanticRule)
                        newRules.append(r)
            else:
                # if the rule has no args, then we only have to introduce new lhs
                for arg in newArgs:
                    new_idx = "s" + str(idx) + "_" + arg.lower()
                    r = makeRule(arg, new_idx, (), prob, stringRule, semanticRule)
                    newRules.append(r)
    else:
        raise Exception("Unexpected error! [Cannot read irtg rule error]")

    return newRules
    
# Procedures

# Main
def main():
    #irtg_file = open("../data/weighten_alto.irtg").read().strip("\n").split("\n\n")
    if len(sys.argv) < 2:
        raise Exception("wrong usage! readIrtg.py grammar [splitsize]")
    if len(sys.argv) == 2:
        splitsize = 2
    else:
        splitsize = int(sys.argv[2])
    irtg_path = sys.argv[1]
    irtg_file = open(irtg_path, "r").read().strip("\n").split("\n\n")

    rules = []
    for rule in irtg_file[1:]:
        rules.extend(induceRules(rule,splitsize))
    print irtg_file[0], "\n\n"
    print "\n".join(rules)

    return 0
    

main()

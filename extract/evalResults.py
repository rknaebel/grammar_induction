#!/usr/bin/env python

import sys
import os.path
import evalb

def main():
    """ EVALUATION """    
    # recall - percentage of test sentences that were correctly translated
    # precision - percentage of translations that were correct
    gold_filename = sys.argv[1]
    parse_filename = sys.argv[2]

    ## precision
    #match = re.search("Complete\smatch(\s+)=(\s+)([0-9\.]+)", results)
    #precision = match.group(3)

    ## recall
    #valid = re.search("Number\sof\sValid\ssentence(\s+)=(\s+)([0-9\.]+)", results)
    #total = re.search("Number\sof\ssentence(\s+)=(\s+)([0-9\.]+)", results)  
    #recall = ((float(valid.group(3)) * (float(precision))/100) / float(total.group(3))) * 100
    #fscore = (recall + float(precision)) / 2


    if not (os.path.isfile(gold_filename) or os.path.isfile(parse_filename)):
        "{}-fail,0.0000,0.0000,0.0000".format(parse_filename)
        return 1

    gold_count, parse_count, match_count = evalb.calcExactScore(parse_filename, gold_filename)
    
    precision = float(match_count) / gold_count
    recall = (((float(parse_count) * precision)/100) / gold_count) * 100
    #fscore = (2.0 / ((gold_count + parse_count) / float(match_count)))
    fscore = (2.0 * precision * recall) / (precision + recall)
    coverage = recall / precision
    
    # generated informations to stdout
    print "{},{:.4f},{:.4f},{:.4f},{:.4f}".format(parse_filename,recall,precision,fscore,coverage)

    return 0

if __name__ == "__main__":
    main()


#!/usr/bin/env python

from __future__ import division
import sys
import re

import csv

def main():
  
    """ EVALUATION """    
    # recall - percentage of test sentences that were correctly translated
    # precision - percentage of translations that were correct
    results_path = sys.argv[1]
    directory = sys.argv[2]
    results = open(results_path, "r").read()
    spr = ""

    spr += results_path + "\t" 
    
    # precision
    match = re.search("Complete\smatch(\s+)=(\s+)([0-9\.]+)", results)
    precision = match.group(3)

    # recall
    valid = re.search("Number\sof\sValid\ssentence(\s+)=(\s+)([0-9\.]+)", results)
    total = re.search("Number\sof\ssentence(\s+)=(\s+)([0-9\.]+)", results)  
    recall = ((float(valid.group(3)) * (float(precision))/100) / float(total.group(3))) * 100
    fscore = (recall + float(precision)) / 2
    
    # appending generated informations to the results csv
    full_results = csv.writer(open(directory, "a"))
    full_results.writerow((results_path, round(recall,2), precision, round(fscore,2)))

if __name__ == "__main__":
    main()


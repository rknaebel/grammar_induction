#!/usr/bin/python
#
# author:
# 
# date: 
# description:
#

class IntervalTree:
    def __init__(self):
        self.name = ""
        self.interval = None
        self.childNodes = []
        self.alignment = []

    def sortChildNodes(self):
        ##self.childNodes.sort(key=lambda t: t.interval.)
        pass

    def induceIrtgRules(self, sentence):
        pass

    def __str__(self):
        interval = "[{},{}]".format(self.interval.start,self.interval.end)
        if self.childNodes:
            return "{}{}({})".format(self.name,interval, ",".join(str(t) for t in self.childNodes))
        else:
            return "{}{}".format(self.name,interval)

    __repr__ = __str__

class Interval:
    def __init__(self, start=None, end=None):
        if (start == None) or (end == None):
            self.start = 0
            self.end = 0
            self.interval = [[]]
        else:
            self.start = start
            self.end   = end
            self.interval = [range(start, end)]
    
    def __iter__(self):
        for interval in self.interval:
            for element in interval:
                yield element
    
    def first(self):
        return self.interval[0][0]
    
    def last(self):
        return self.interval[-1][-1]
    
    def without(self, other):
        erg = Interval(self.start,self.end)
        erg.interval = self.interval[:]
        
        if len(other.interval) == 0 or (len(other.interval) == 1 and len(other.interval[0]) == 0):
            return erg
        
        start, end = other.first(), other.last()
        pos = -1
        for idx,intv in enumerate(erg.interval):
            if (start in intv) and (end in intv):
                pos = idx
                break
        else:
            return erg
        
        startpos, endpos = erg.interval[pos].index(start), erg.interval[pos].index(end)
        # what if startpos == 0 or endpos == len(erg.interval) ???
        before = erg.interval[:pos]   + ([erg.interval[pos][:startpos]] if erg.interval[pos][:startpos] else [])
        after  = erg.interval[pos+1:] + ([erg.interval[pos][endpos+1:]] if erg.interval[pos][endpos+1:] else [])
        
        erg.interval = before + [[]] + after

        return erg
    
    def flatten(self):
        res = []
        for xs in self.interval:
            if not xs:
                res.append(-1)
            else:
                res.extend(xs)
        return res
    
    def __str__(self):
        #return "[{}]".format(",".join(map(str,self.interval)))
        return str(self.interval)
    __repr__ = __str__

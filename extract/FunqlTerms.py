#
# Represents Functions - Objects with at least one argument
#
class FunqlTerm():
    def __init__(self, fname, fargs):
        self.name = fname
        self.args = fargs
    
    def toFunql(self):
        return str(self)
    
    def toMR(self):
        term = "{}({})".format(self.name, ",".join(['X']*len(self.args)))
        return ", ".join([term]+[arg.toMR() for arg in self.args])
    
    def __str__(self):
        return "{}({})".format(self.name, ", ".join(map(str,self.args)))

#
# Represents Constants in MR
#
class FunqlConst():
    def __init__(self, val):
        self.val = val
    
    def toFunql(self):
        return str(self)
    
    def toMR(self):
        return self.val.replace(' ', '+')
    
    def __str__(self):
        return "{}".format(self.val)

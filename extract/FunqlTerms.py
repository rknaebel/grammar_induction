#
# Represents Functions - Objects with at least one argument
#
class FunqlTerm():
    def __init__(self, fname, fargs):
        self.name = fname
        self.args = fargs
        self.isConst = False
    
    def toFunql(self):
        return str(self)
    
    def toMR(self):
        if all(t.isConst for t in self.args):
            args = ",".join(arg.toMR() for arg in self.args)
            return "{}({})".format(self.name, args)
        else:
            term = "{}({})".format(self.name, ",".join(['X']*len(self.args)))
            return " ".join([term]+[arg.toMR() for arg in self.args])
    
    def __str__(self):
        return "{}({})".format(self.name, ", ".join(map(str,self.args)))

#
# Represents Constants in MR
#
class FunqlConst():
    def __init__(self, val):
        self.val = val
        self.isConst = True
    
    def toFunql(self):
        return str(self)
    
    def toMR(self):
        return self.val.replace(' ', '+')
    
    def __str__(self):
        return "{}".format(self.val)

import core as FO

def union(sets):
    if len(sets) > 1:
        return sets[0].union(union(sets[1:]))
    else:
        return sets[0]
        
class signature:
    def __init__(self, symbols):
        self.symbols = symbols
        
    def verify(self, x):
        if x.__class__ in (FO.Exists, FO.Forall):
            return self.verify(x.formula)
        elif x.__class__ in (FO.And, FO.Or, FO.Implies, FO.Equivalent):
            return self.verify(x.formula1) and self.verify(x.formula2)
        elif x.__class__ is FO.Function:
            return x.symbol in self.symbols and ('function', len(x.terms)) == self.symbols[x.symbol] and all([self.verify(t) for t in x.terms])
        elif x.__class__ is FO.Relation:
            return x.symbol in self.symbols and ('relation', len(x.terms)) == self.symbols[x.symbol] and all([self.verify(t) for t in x.terms])
        elif x.__class__ is FO.Equals:
            return self.verify(x.term1) and self.verify(x.term2)
        elif x.__class__ is FO.Negation:
            return self.verify(x.formula)
        elif x.__class__ is FO.Constant:
            return x.constant in self.symbols and self.symbols[x.constant] == 'constant'
        else:
            return True


def unimply(formula):
    if formula.__class__ in (FO.And, FO.Or):
        return formula.__class__(unimply(formula.formula1), unimply(formula.formula1))
    elif formula.__class__ in (FO.Exists, FO.Forall):
        return formula.__class__(formula.variable, unimply(formula.formula))
    elif formula.__class__ is FO.Equivalent:
        f1, f2 = unimply(formula.formula1), unimply(formula.formula2)
        return FO.Or(FO.And(f1, f2), FO.And(FO.Negation(f1), FO.Negation(f2)))
    elif formula.__class__ is FO.Implies:
        return FO.Or(FO.Negation(unimply(formula.formula1)), unimply(formula.formula2))
    else:
        return formula
        
def unequiv(formula):
    if formula.__class__ in (FO.And, FO.Or, FO.Implies):
        return formula.__class__(unequiv(formula.formula1), unequiv(formula.formula1))
    elif formula.__class__ in (FO.Exists, FO.Forall):
        return formula.__class__(formula.variable, unequiv(formula.formula))
    elif formula.__class__ is FO.Equivalent:
        f1, f2 = unequiv(formula.formula1), unequiv(formula.formula2)
        return FO.And(FO.Implies(f1, f2), FO.Implies(f2, f1))
    else:
        return formula

def unall(x):
    if x.__class__ is FO.Forall:
        return FO.Negation(FO.Exists(x.variable, FO.Negation(x.formula)))
    elif x.__class__ is FO.Exists:
        return FO.Exists(x.variable, unall(x.formula))
    elif x.__class__ in (FO.And, FO.Or, FO.Implies, FO.Equivalent):
        return x.__class__(unall(x.formula1), unall(x.formula2))
    elif x.__class__ is FO.Negation:
        return FO.Negation(unall(x.formula))
    else:
        return x

def substitute(variable_name, term, x):
    if x.__class__ in (FO.Exists, FO.Forall):
        if x.variable.name != variable_name:
            return x.__class__(x.variable, substitute(variable_name, term, x.formula))
        else:
            return x
    elif x.__class__ in (FO.And, FO.Or, FO.Implies, FO.Equivalent):
        return x.__class__(substitute(variable_name, term, x.formula1), substitute(variable_name, term, x.formula2))
    elif x.__class__ in (FO.Relation, FO.Function):
        return x.__class__(x.symbol, list(map(lambda y:substitute(variable_name, term, y), x.terms)))
    elif x.__class__ is FO.Equals:
        return x.__class__(substitute(variable_name, term, x.term1), substitute(variable_name, term, x.term2))
    elif x.__class__ is FO.Variable and x.name == variable_name:
        return term
    elif x.__class__ is FO.Negation:
        return x.__class__(substitute(variable_name, term, x.formula))
    else:
        return x

def free(x):
    if x.__class__ in (FO.Exists, FO.Forall):
        return free(x.formula).difference({x.variable.name})
    elif x.__class__ is FO.Negation:
        return free(x.formula)
    elif x.__class__ in (FO.And, FO.Or, FO.Implies, FO.Equivalent):
        return free(x.formula1).union(free(x.formula2))
    elif x.__class__ in (FO.Function, FO.Relation):
        return union([free(term) for term in x.terms])
    elif x.__class__ is FO.Equals:
        return free(x.term1).union(free(x.term2))
    elif x.__class__ is FO.Variable:
        return {x.name}
    else:
        return set()
        
def var(x):
    if x.__class__ in (FO.Exists, FO.Forall):
        return var(x.formula).union({x.variable.name})
    elif x.__class__ is FO.Negation:
        return var(x.formula)
    elif x.__class__ in (FO.And, FO.Or, FO.Implies, FO.Equivalent):
        return var(x.formula1).union(var(x.formula2))
    elif x.__class__ in (FO.Function, FO.Relation):
        return union([var(term) for term in x.terms])
    elif x.__class__ is FO.Equals:
        return var(x.term1).union(free(x.term2))
    elif x.__class__ is FO.Variable:
        return {x.name}
    else:
        return set()
        
def nnf(x):
    if x.__class__ in (FO.Implies, FO.Equivalent):
        return nnf(unimply(x))
    elif x.__class__ is FO.Negation:
        y = x.formula
        if y.__class__ is FO.And:
            return FO.Or(nnf(FO.Negation(y.formula1)), nnf(FO.Negation(y.formula2)))
        elif y.__class__ is FO.Or:
            return FO.And(nnf(FO.Negation(y.formula1)), nnf(FO.Negation(y.formula2)))
        elif y.__class__ is FO.Exists:
            return FO.Forall(y.variable, nnf(FO.Negation(y.formula)))
        elif y.__class__ is FO.Forall:
            return FO.Exists(y.variable, nnf(FO.Negation(y.formula)))
        elif y.__class__ is FO.Negation:
            return nnf(y.formula)
        else:
            return x
    elif x.__class__ in (FO.And, FO.Or, FO.Implies, FO.Equivalent):
        return x.__class__(nnf(x.formula1), nnf(x.formula2))
    elif x.__class__ in (FO.Exists, FO.Forall):
        return x.__class__(x.variable, nnf(x.formula))
    else:
        return x

def prenex(x, depth = 0):
    #print ((">    "*depth) + str(x) + "     ")
    if x.__class__ is FO.Equivalent:
        return prenex(unequiv(x), depth+1)
    if x.__class__ in (FO.And, FO.Or, FO.Implies):
        f1, f2 = prenex(x.formula1, depth+1), prenex(x.formula2, depth+1)
        
        # If no quantors, pass.
        if {f1.__class__, f2.__class__}.intersection({FO.Forall, FO.Exists}) == set():
            return x
        # Remove variable conflicts.
        if f1.__class__ in (FO.Forall, FO.Exists):
            f = free(f2)
            if f1.variable.name in f:
                n = FO.Variable(nextvar(f1.variable.name, var(f1)))
                f1 = f1.__class__(n, substitute(f1.variable.name, n, f1.formula))
        elif f2.__class__ in (FO.Forall, FO.Exists):
            f = free(f1)
            if f2.variable.name in f:
                n = FO.Variable(nextvar(f2.variable.name, var(f2)))
                f2 = f2.__class__(n, substitute(f2.variable.name, n, f2.formula))
        
        # Removing quantors from either part of &&,||
        if x.__class__ in (FO.And, FO.Or):
            if f1.__class__ in (FO.Forall, FO.Exists):
                out = f1.__class__(f1.variable, prenex(x.__class__(f1.formula, f2), depth+1))
            else:
                out = f2.__class__(f2.variable, prenex(x.__class__(f1, f2.formula), depth+1))
            #print("<    "*depth + str(out))
            return out
        
        # Removing quantors from antecedent of implication:
        if f1.__class__ in (FO.Forall, FO.Exists):
            rev = {FO.Forall:FO.Exists, FO.Exists:FO.Forall}
            return rev[f1.__class__](f1.variable, prenex(x.__class__(f1.formula, f2)))
        else:
            return f2.__class__(f2.variable, prenex(x.__class__(f1, f2.formula)))
    elif x.__class__ is FO.Negation:
        y = prenex(x.formula)
        if y.__class__ is FO.Exists:
            return FO.Forall(y.variable, prenex(FO.Negation(y.formula)))
        elif y.__class__ is FO.Forall:
            return FO.Exists(y.variable, prenex(FO.Negation(y.formula)))
    elif x.__class__ in (FO.Exists, FO.Forall):
        return x.__class__(x.variable, prenex(x.formula))
    return x
        
def nextvar(name, reserved):
    while name in reserved:
        name += "'"
    return name

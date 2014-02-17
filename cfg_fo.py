# Christoph Burschka, 2012

import core as FO
import symbols as SYM
from parser import symbol, cfg
import lexer_fo as t

def FoParser(signature):
    return cfg.slr1_grammar(prods(**signature), Formula).slr1()

class Formula(symbol.NonTerm):
    def fo(self):
        return self.production[0].fo()

class Term(symbol.NonTerm):
    def fo(self):
        return self.production[0].fo()

class Junction(Formula):
    ops = {SYM.AND: FO.And, SYM.OR: FO.Or, SYM.IMP: FO.Implies, SYM.EQ: FO.Equivalent}

    def fo(self):
        return self.ops[self.production[2].value](self.production[1].fo(), self.production[3].fo())

class Quantified(Formula):
    qs = {SYM.EXISTS: FO.Exists, SYM.FORALL: FO.Forall}
    def fo(self):
        return self.qs[self.production[0].value](self.production[1].fo(), self.production[2].fo())

class Negation(Formula):
    def fo(self):
        return FO.Negation(self.production[1].fo())

class Relation(Formula):
    def fo(self):
        return FO.Relation(self.production[0].value, tuple(x.fo() for x in self.production[2:-1:2]))

class Function(Term):
    def fo(self):
        return FO.Function(self.production[0].value, tuple(x.fo() for x in self.production[2:-1:2]))

class Constant(Term):
    def fo(self):
        return FO.Function(self.production[0].value, tuple(x.fo() for x in self.production[2:-1:2]))

class Equality(Formula):
    def fo(self):
        return FO.Equals(self.production[0].fo(), self.production[2].fo())

class Variable(Term):
    def fo(self):
        return FO.Variable(self.production[0].value)

def prods(relations={}, functions={}, constants=[]):
    prods = {
        Formula: {(Junction,), (Quantified,), (Negation,), (Relation,), (Equality,)},
        Junction: {(t.LeftParen, Formula, t.Junctor, Formula, t.RightParen)},
        Quantified: {(t.Quantor, Variable, Formula)},
        Negation: {(t.Not, Formula)},
        Equality: {(Term, t.Equality, Term)},
        Term: {(Function,), (Constant,), (Variable,)},
        Variable: {(t.Variable,)},
        Relation: {((sym, t.LeftParen, Term) + (t.Comma, Term)*(d-1) + (t.RightParen,)) for (name, (sym, d)) in relations.items()},
        Function: {((sym, t.LeftParen, Term) + (t.Comma, Term)*(d-1) + (t.RightParen,)) for (name, (sym, d)) in functions.items()},
        Constant: {(sym,) for (name, sym) in constants.items()}
    }
    return prods

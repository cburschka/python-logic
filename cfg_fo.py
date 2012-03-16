# Christoph Burschka, 2012

import core as FO
import symbols as SYM
from cfg import cfgrammar

def FoGrammar(signature):
    return cfgrammar(nonterms, terms(signature), prods(signature), 'Formula', tree)

def tree(s, z):
    if s == 'Junctor':
        return SYM.junctors[z[0]]
    if s == 'Quantor':
        return SYM.quantors[z[0]]
    if s == 'Junction':
        lp, f1, op, f2, rp = z
        return op(f1, f2)
    elif s == 'Quantified':
        q, v, f = z
        return q(v, f)
    elif s == 'Negation':
        n, f = z
        return FO.Negation(f)
    elif s == 'Relation':
        return FO.Relation(z[0], z[2:-1:2])
    elif s == 'Equality':
        t1, eq, t2 = z
        return FO.Equals(t1, t2)
    elif s == 'Function':
        return FO.Function(z[0], z[2:-1:2])
    elif s == 'Constant':
        return FO.Constant(z[0])
    elif s == 'Variable':
        return FO.Variable(z[0])
    elif s == 'Term':
        return z[0]
    elif s == 'Formula':
        return z[0]


nonterms = {
    'Formula', 'Junction', 'Quantified', 'Relation', 
    'Negation', 'Function', 'Junctor', 'Quantor', 
    'Term', 'Equality', 'Variable', 'Constant'
}

def terms(signature):
  terms = [SYM.NOT, SYM.AND, SYM.OR, SYM.IMP, SYM.EQ, '=', '(', ',', ')', SYM.EXISTS, SYM.FORALL, -1]
  return set(terms + list(signature.keys()))

def prods(signature):
  prods = {
    ('Formula', ('Junction',)),
    ('Formula', ('Quantified',)),
    ('Formula', ('Negation',)),
    ('Formula', ('Relation',)),
    ('Formula', ('Equality',)),
    ('Junction', ('(', 'Formula', 'Junctor', 'Formula', ')')),
    ('Quantified', ('Quantor', 'Variable', 'Formula')),
    ('Negation', (SYM.NOT, 'Formula')),
    ('Equality', ('Term', '=', 'Term')),
    ('Junctor', (SYM.AND,)),
    ('Junctor', (SYM.OR,)),
    ('Junctor', (SYM.IMP,)),
    ('Junctor', (SYM.EQ,)),
    ('Quantor', (SYM.EXISTS,)),
    ('Quantor', (SYM.FORALL,)),
    ('Term', ('Variable',)),
    ('Term', ('Constant',)),
    ('Term', ('Function',)),
    ('Variable', (-1,))
  }
  for symbol,d in signature.items():
    t, r = d
    if t in ('relation', 'function'):
      ar = [',', 'Term']*(r-1)
      expansion = tuple([symbol, '(', 'Term']+ar+[')'])
      if t == 'relation':
        prods.add(('Relation', expansion))
      else:
        prods.add(('Function', expansion))
    else:
      prods.add(('Constant', symbol))
  return prods




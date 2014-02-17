# Christoph Burschka, 2012

from cfg_fo import FoParser
from lexer_fo import lexer, Relation
from converters import nnf,prenex

class E(Relation):
    pass

signature = {
    'relations': {'E': (E, 2)},
    'functions': {},
    'constants': {},
}

L = lexer(signature)
P = FoParser(signature)
print('This parser will read the following string and convert it to NNF')
formula = '∃x ¬(E(x, x) ∧ ¬x=x)'
print(formula)
print(nnf(P.parse(L.lex(formula)).fo()))

print('This parser will read the following string and convert it to PNF')
formula='¬(∃x E(x, x) ∧ ∀x∀y(¬x=y → E(x,y)))'
print(formula)
print(prenex(P.parse(L.lex(formula)).fo()))

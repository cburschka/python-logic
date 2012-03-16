# Christoph Burschka, 2012

from cfg_fo import FoGrammar
from symbols import lex
from converters import nnf,prenex

signature = {'E': ('relation', 2)}
G = FoGrammar(signature)
print('This parser will read the following string and convert it to NNF')
formula = '∃x ¬(E(x, x) ∧ ¬x=x)'
print(formula)
print(nnf(G.parse(lex(formula))))

print('This parser will read the following string and convert it to PNF')
formula='¬(∃x E(x, x) ∧ ∀x∀y(¬x=y → E(x,y)))'
print(formula)
print(prenex(G.parse(lex(formula))))

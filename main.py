# Christoph Burschka, 2012

from converters import *
from parser import main

sig_graph = {'E':('relation',2)}
sig_ord = {'≤':('relation',2)}

print(main('((.fa. x E(x,x) && .fa. x .fa. y (E(x,y) <-> E(y,x)) ) && .fa. x .fa. y .fa. z ((E(x,y) && E(y,z))->E(x,z)))', sig_graph))

formula=main('(((.fa. x ≤(x,x) && .fa. x .fa. y ((≤(x,y) && ≤(y,x)) -> x=y) ) && .fa. x .fa. y .fa. z ((≤(x,y) && ≤(y,z))->≤(x,z))) && .fa. x .fa. y (≤(x,y) || ≤(y,x)))', sig_ord)
print(formula)
print(prenex(formula))
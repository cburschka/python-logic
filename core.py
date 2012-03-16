# Christoph Burschka, 2012

from copy import copy

class Formula:
  def __init__(self):
    pass

class Term:
  def __init__(self):
    pass


class Exists(Formula):
  def __init__(self, variable, formula):
    self.variable = variable
    self.formula = formula
    
  def evaluate(self, structure, allocation):
    for element in structure.universe:
      if self.formula.evaluate(structure, allocation.extend(self.variable, element)):
        return True
    return False
  
  def __str__(self):
    return '∃' + str(self.variable) + ' ' + str(self.formula)
    
class Constant(Term):
  def __init__(self, constant):
    self.constant = constant
    
  def evaluate(self, structure, allocation):
    return structure.constants[constant]
    
  def __str__(self):
    return str(self.constant)

class Forall(Formula):
  def __init__(self, variable, formula):
    self.variable = variable
    self.formula = formula

  def evaluate(self, structure, allocation):
    for element in structure.universe:
      if not self.formula.evaluate(structure, allocation.extend(self.variable, element)):
        return False
    return True

  def __str__(self):
    return '∀' + str(self.variable) + ' ' + str(self.formula)

class Negation(Formula):
  def __init__(self, formula):
    self.formula = formula

  def evaluate(self, structure, allocation):
    return not self.formula.evaluate(structure, allocation)
  def __str__(self):
    return '¬' + str(self.formula)
class Or(Formula):
  def __init__(self, formula1, formula2):
    self.formula1 = formula1
    self.formula2 = formula2

  def evaluate(self, structure, allocation):
    return self.formula1.evaluate(structure, allocation) or self.formula2.evaluate(structure, allocation)
  def __str__(self):
    return '(' + str(self.formula1) + ' ∨ ' + str(self.formula2) + ')'

class And(Formula):
  def __init__(self, formula1, formula2):
    self.formula1 = formula1
    self.formula2 = formula2

  def evaluate(self, structure, allocation):
    return self.formula1.evaluate(structure, allocation) and self.formula2.evaluate(structure, allocation)
  def __str__(self):
    return '(' + str(self.formula1) + ' ∧ ' + str(self.formula2) + ')'
class Implies(Formula):
  def __init__(self, formula1, formula2):
    self.formula1 = formula1
    self.formula2 = formula2

  def evaluate(self, structure, allocation):
    return not self.formula1.evaluate(structure, allocation) or self.formula2.evaluate(structure, allocation)
  def __str__(self):
    return '(' + str(self.formula1) + ' → ' + str(self.formula2) + ')'

class Equivalent(Formula):
  def __init__(self, formula1, formula2):
    self.formula1 = formula1
    self.formula2 = formula2

  def evaluate(self, structure, allocation):
    return self.formula1.evaluate(structure, allocation) == self.formula2.evaluate(structure, allocation)
    
  def __str__(self):
    return '(' + str(self.formula1) + ' ↔ ' + str(self.formula2) + ')'

class Equals(Formula):
  def __init__(self, term1, term2):
    self.term1 = term1
    self.term2 = term2

  def evaluate(self, structure, allocation):
    return self.term1.evaluate(structure, allocation) is self.term2.evaluate(structure, allocation)
    
  def __str__(self):
    return str(self.term1) + '=' + str(self.term2)

class Relation(Formula):
  def __init__(self, relation, terms):
    self.symbol = relation
    self.terms = terms

  def evaluate(self, structure, allocation):
    return tuple(map(lambda t:t.evaluate(structure, allocation), self.terms)) in structure.relations[self.symbol]
    
  def __str__(self):
    return str(self.symbol) + '(' + ", ".join(map(str, self.terms)) + ')'

class Function(Formula):
  def __init__(self, function, terms):
    self.symbol = function
    self.terms = terms

  def evaluate(self, structure, allocation):
    return structure.functions[self.symbol].evaluate(tuple(map(lambda t:t.evaluate(structure, allocation), self.terms)))
  def __str__(self):
    return str(self.symbol) + '(' + ", ".join(map(str, self.terms)) + ')'
    


class Structure:
  def __init__(self, universe, relations, functions, constants):
    self.universe = universe
    self.relations = relations
    self.functions = functions
    self.constants = constants

class Allocation:
  def __init__(self, a):
    self.a = a
  
  def extend(self, name, value):
    x = copy(self.a)
    x[name] = value
    return Allocation(x)

class Variable(Term):
  def __init__(self, name):
    self.name = name
  def evaluate(self, structure, allocation):
    return allocation.a[self.name]
  def __str__(self):
    return str(self.name)



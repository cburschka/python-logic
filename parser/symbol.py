class Symbol:
    def __str__(self):
        return self.__class__.__name__

class NonTerm(Symbol):
    def __init__(self, production):
        self.production = production
    def graph(self, nodes=None, edges=None):
        if nodes == None:
            nodes, edges = {}, set()
        i = len(nodes)
        nodes[i] = str(self)
        for x in self.production:
            edges.add((i, len(nodes)))
            if issubclass(x.__class__, NonTerm):
                nodes, edges = x.graph(nodes, edges)
            else:
                nodes[len(nodes)] = str(x)
        return nodes, edges

class Term(Symbol):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return self.__class__.__name__ + '(' + self.value + ')'

class Start(NonTerm):
    pass

class End(Term):
    pass


from .symbol import Start, NonTerm, Term, End
from . import pda

class grammar:
    # prods: Ein dictionary, das jedem Nichtterminal ein set aller Produktions-
    #        tupel zuweist.
    # start: Ein Nichtterminalsymbol.
    # Die Menge der Nichtterminale besteht aus den Schlüsseln von prods;
    # alle übrigen Symbole, die in Produktionen vorkommen, sind Terminale.
    # Jedes Nichtterminal muss ein von NonTerm abgeleiteter Typ sein; jedes Terminal
    # muss ein von Term abgeleiteter Typ sein.
    # Argument akzeptieren.
    def __init__(self, prods, start):
        assert type(prods) is dict, 'Produktionen sind kein dictionary.'
        assert all(type(l) is type and type(r) is set for (l,r) in prods.items()), 'Eine Produktion hat nicht die Form type -> set.'
        assert all(all(type(p) is tuple for p in r) for r in prods.values()), 'Eine Produktions-Alternative ist kein Tupel.'

        self.prods = prods
        self.start = start
        self.nonterms = set(self.prods.keys())
        self.symbols = {start}
        for production_set in prods.values():
            for production in production_set:
                self.symbols.update(production)
        self.terms = self.symbols - self.nonterms

        assert self.nonterms <= self.symbols, 'Unerreichbare Nichtterminale auf der linken Seite.'
        assert start in self.nonterms, 'Startsymbol ist nicht produzierbar.'
        assert all(issubclass(s, NonTerm) and s != Start for s in self.nonterms), 'Ungültiges Nichtterminalsymbol.'
        assert all(issubclass(s, Term) and s != End for s in self.terms), 'Ungültiges Terminalsymbol.'


    def __str__(self):
        return 'Start: {0}\nTerminale: {1}\nNichtterminale: {2}\nProduktionen:\n{3}'.format(
            self.start.__name__,
            ', '.join(sorted(x.__name__ for x in self.terms)),
            ', '.join(sorted(x.__name__ for x in self.nonterms)),
            '\n'.join(
                '    {0} →  {1}'.format(l.__name__, ' | '.join(
                    (' '.join(x.__name__ for x in p) or 'ε') for p in r
                ))
                for (l, r) in self.prods.items())
        )

# Ein Simple LR(1) Parser:
# - 1 Symbol als Lookahead
# - die Follow-Sets werden pro Symbol (nicht pro Zustand/Symbol) berechnet.
class slr1_grammar(grammar):
    def slr1(self):
        # Beginne mit einer Startproduktion S' -> S $
        start = self.close_state({(Start, (self.start, End), 0)})

        # Berechne rekursiv die Folgezustände.
        nullable = self.nullable()
        first = self.first(nullable)
        follow = self.follow(nullable, first)
        states, shift, reduce = self.derive_states(start, follow, {start})

        return pda.lr1(self.terms, self.nonterms, start, states, shift, reduce)

    # Ein Zustand ist abgeschlossen, wenn für jedes zu lesende
    # Nichtterminal auch jede Produktion enthalten ist.
    def close_state(self, state):
        # Wiederhole, bis keine neuen Produktionen eingefügt werden.
        old, new = 0, len(state)
        while old < new:
            # Welche Nichtterminale können gelesen werden?
            nonterm_shifts = {right[dot] for (left, right, dot) in state if dot < len(right) and right[dot] in self.nonterms}
            # Füge alle deren Produktionen hinzu.
            for left in nonterm_shifts:
                state.update((left, right, 0) for right in self.prods[left])
            old, new = new, len(state)

        # frozenset() ist immutable, und darf daher selbst Element eines sets sein.
        return frozenset(state)

    # Die Zustandsmenge ist abgeschlossen, wenn sie für jeden Zustand und jedes lesbare Zeichen
    # auch den abgeschlossenen Folgezustand enthält.
    def derive_states(self, state, follow, states, shift=None, reduce=None):
        # Initialisiere die shift/reduce Tabellen:
        if shift == reduce == None:
            shift, reduce = {}, {}

        # Berechne die Reduktionsregeln.
        for left, right, dot in state:
            if dot == len(right):
                add_reduce = {(state, lookahead) : (left, right) for lookahead in follow[left]}
                for state, symbol in set(reduce.keys()).intersection(add_reduce.keys()):
                    raise ValueError('Reduce / Reduce-Konflikt.\nZustand: {0}\nLookahead: {1}\nReduktion 1: {2}\nReduktion 2: {3}'.format(
                        state_string(state), symbol.__name__, rule_string(reduce[(state, symbol)]), rule_string(add_reduce[(state, symbol)])
                    ))
                reduce.update(add_reduce)

        # Berechne die Shiftregeln.
        added = set()
        for symbol in {right[dot] for (left, right, dot) in state if dot < len(right)}:
            # Füge den erreichten Zustand hinzu:
            next = self.close_state({(left, right, dot+1) for (left, right, dot) in state if dot < len(right) and right[dot] == symbol})
            if (state, symbol) in reduce:
                raise ValueError('Shift / Reduce-Konflikt.\nZustand: {0}\nLookahead: {1}\nShift: {2}\nReduktion: {3}'.format(
                    state, symbol, next, reduce[(state, symbol)]
                ))
            shift[(state, symbol)] = next
            if next not in states:
                added.add(next)
        states |= added

        # Rekursion für jeden neuen Zustand.
        for state in added:
            self.derive_states(state, follow, states, shift, reduce)

        return states, shift, reduce

    # Bestimme die auf Null produzierenden Nichtterminale
    def nullable(self):
        # Fixpunkt-Iteration
        nullable = {None}
        old, new = 0, 1
        while old < new:
            for left, right in self.prods.items():
                # Falls alle Symbole einer Alternative auf Null produzieren:
                if any(all(t in nullable for t in alt) for alt in right):
                    nullable.add(left)
            old, new = new, len(nullable)
        return nullable.difference([None])

    # Bestimme die ersten Terminale, auf die jedes Nichtterminal produzieren kann.
    def first(self, nullable):
        first = dict([(n,set()) for n in self.nonterms] + [(t,{t}) for t in self.terms] + [(Start, {self.start})])

        # Fixpunkt-Iteration
        old, new = 0, len(self.terms)
        while old < new:
            for left, right in self.prods.items():
                for alt in right:
                    for t in alt:
                        first[left].update(first[t])
                        if t not in nullable:
                            break
            old, new = new, sum(len(x) for x in first.values())
        return first

    # Bestimme alle Lookahead-Symbole für die Reduktion eines Nichtterminals:
    def follow(self, nullable, first):
        direct = {n:set() for n in self.nonterms}
        parents = {n:set() for n in self.nonterms}

        parents[Start] = set()
        direct[Start], direct[self.start] = set(), {End}

        for symbol in self.nonterms:
            # Finde alle Stellen, wo das Symbol rechts in einer Produktion steht:
            for left, right in self.prods.items():
                for alt in right:
                    for i, t in enumerate(alt):
                        if symbol == t:
                            # Bestimme alle ersten Terminalsymbole der Folgekette:
                            for f in alt[i+1:]:
                                direct[symbol] |= first[f]
                                if f not in nullable:
                                    break
                            else:
                                # Wenn die Kette auf das leere Wort produzieren kann, so folge der linken Seite.
                                parents[symbol].add(left)

        # Berechne transitiven Abschluss von parents:
        old, new = 0, sum(len(p) for p in parents.values())
        while old < new:
            for s, p in parents.items():
                parents[s].update(*(parents[x] for x in p))
            old, new = new, sum(len(p) for p in parents.values())

        # Berechne daraus die Follow-Sets:
        follow = {symbol:direct[symbol].union(*(direct[p] for p in parents[symbol])) for symbol in direct}
        return follow


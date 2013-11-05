# Christoph Burschka, 2012

# A simple LL(1) parser generator.
# An LL(1) parser looks one symbol ahead to determine reductions.

class cfgrammar:
    # The nonterms, terms, prods and start are self-explanatory.
    # "tree" is a function or class that evaluates the parsed string
    # semantically to generate a recursive data structure:
    # Turning the pushdown automaton from a pass/fail to an actual parser.
    
    # The tree function must accept a non-terminal and a list of tokens as arguments.
    # The value it returns will be stored and then passed in place of the 
    # reduced non-terminal in further reductions.
    
    # Note: All terminal symbols must be strings. A -1 integer is interpreted as
    # a wildcard. It will match any terminal symbol.
    def __init__(self, nonterms, terms, prods, start, tree):
        self.terms = terms
        self.nonterms = nonterms
        self.prods = prods
        self.start = start
        self.states = set()
        self.shift = {}
        self.reduce = {}
        self.tree = tree

        # Generate the initial state containing all productions from Start.
        init = set()
        for s, tokens in self.prods:
            if s == start:
                init.add((s, tokens, 0))
        self.init_state = self.close_state(init)
        self.states.add(self.init_state)
        
        # Recursively fill the state table.
        self.derive_states(self.init_state)
        # Replace the production-set states with integer-labeled states.
        self.normalize_states()
    
    # Parse a list of terminal symbols.
    def parse(self, string):
        # Use None as a terminator.
        string.append(None)
        
        # State stack T, Symbol/Object stack N
        T = [self.init_state]
        N = []
        
        # Nibble bits off the string until it is empty.
        while len(string) > 0:
            # Try to shift on a specific terminal symbol.
            if (T[-1], string[0]) in self.shift:
                T.append(self.shift[(T[-1], string[0])])
                N.append(string[0])
                string = string[1:]
                
            # Try to reduce on a specific lookahead terminal symbol.
            elif (T[-1], string[0]) in self.reduce:
                X,r = self.reduce[(T[-1], string[0])]
                o, N = N[-len(r):], N[:-len(r)]
                N.append(self.tree(X, o))
                T = T[:-len(r)]
                if (T[-1], X) in self.shift:
                    T.append(self.shift[(T[-1], X)])
                else:
                    string = []
                    
            # Try to shift on a wildcard.
            elif (T[-1], -1) in self.shift:
                T.append(self.shift[(T[-1], -1)])
                N.append(string[0])
                string = string[1:]
            
            # Try to reduce on a lookahead wildcard.
            elif (T[-1], -1) in self.reduce:
                X,r = self.reduce[(T[-1], -1)]
                o, N = N[-len(r):], N[:-len(r)]
                N.append(self.tree(X, o))
                T = T[:-len(r)]
                if (T[-1], X) in self.shift:
                    T.append(self.shift[(T[-1], X)])
                else:
                    string = []
                    
            # Fail:
            else:
                raise ValueError('Invalid token in state %d: %s' % (T[-1], string[0]))
        return N[0]
                
                
    def __str__(self):
        table = []
        syms = list(self.terms) + list(self.nonterms)
        table.append(['State'] + syms)
        rules = list(self.reduce.values())
        lookup = dict(zip(rules, list(range(len(rules)))))
        m = max(list(map(len, map(str, self.terms))) + list(map(len, self.nonterms)))+2
        for state in self.states:
            row = [state]
            for e in syms:
                if (state, e) in self.shift:
                    row.append('S %d' % self.shift[(state, e)])
                elif (state, e) in self.reduce:
                    row.append('R %d' % lookup[self.reduce[(state,e)]])
                    row.append('')
                else:
                    row.append('')
            table.append(row)
            rows = []
        for x,i in sorted(lookup.items(), key=lambda z:z[1]):
            s,x = x
            rows.append('%d: %s %s %s' % (i, s, SYM.IMP, " ".join(map(str, x))))
        return "\n".join(["|".join([(str(s) + " "*20)[:m] for s in row]) for row in table]) + "\n" + "\n".join(rows)

    
    # Recursively find state classes, shift & reduce actions.
    def derive_states(self, state):
        to_read = set()
        # Determine every possible symbol that may be shifted.
        for s, tokens, i in state:
            if i < len(tokens):
                to_read.add(tokens[i])
        # Generate the states that are reached by each shift.
        for shift in to_read:
            next = set()
            # For each rule of .s, add s. to the next state.
            for s, tokens, i in state:
                if i < len(tokens) and tokens[i] == shift:
                    next.add((s, tokens, i+1))
            # Close by expanding all non-terms in the next step.
            next = self.close_state(next)
            # If an equivalent state hasn't yet been processed, recurse into it.
            if next not in self.states:
                self.states.add(next)
                self.derive_states(next)
            self.shift[(state, shift)] = next
    
        # Determine reduction rules.
        for s, tokens, i in state:
            if len(tokens) == i:
                # Find all possible lookahead symbols and determine the reduction.
                for f in self.follow(s, set()):
                    self.reduce[(state, f)] = (s, tokens)


    # Derived states are defined as sets of production/positions.
    # To generate a proper parsing table, reduce these sets to a simple
    # enumerated list of states.
    def normalize_states(self):
        numbering = dict(zip(sorted(self.states, key=lambda a:a != self.init_state), range(len(self.states))))
        self.states = list(range(len(self.states)))
        self.init_state = numbering[self.init_state]
        shift, red = {}, {}
        for x, next in self.shift.items():
            state, letter = x
            shift[(numbering[state], letter)] = numbering[next]
        for x, rule in self.reduce.items():
            state, letter = x
            red[(numbering[state], letter)] = rule
        self.shift, self.reduce = shift, red


    def follow(self, s, Y=set()):
        f = set()
        #if s == self.start:
        #    return {None}

        for y, tokens in self.prods:
            E = set()
            for i, x in enumerate(tokens):
                if s == x:
                    E = E.union(self.first(tokens[i+1:], set()))
            for e in E:
                if e is None and y not in Y:
                    Y.add(y)
                    f = f.union(self.follow(y, Y))
                else:
                    f.add(e)
        return f if f else {None}

    def first(self, tokens, X):
        collapsing = True
        F = set()
        while len(tokens) > 0 and collapsing:
            collapsing = False
            x, tokens = tokens[0], tokens[1:]
            if x in self.terms or x == -1:
                F.add(x)
                break
            elif x not in X:
                for s, t in self.prods:
                    if s == x:
                        E = self.first(t, X.union([x]))
                        F = F.union(E.difference([None]))
                        collapsing = collapsing or None in E
        if collapsing:
            F.add(None)
        return F

    def close_state(self, state):
        nstate = set()
        # Exhaustively add all productions for expected nonterms.
        while nstate != state:
            nstate = set(list(state))
            begin = set([])
            for s, tokens, i in state:
                if i < len(tokens) and tokens[i] in self.nonterms:
                    begin.add(tokens[i])
            for s, tokens in self.prods:
                if s in begin:
                    state.add((s, tokens, 0))
        return frozenset(state)

def rulestr(rule):
    s, x = rule
    return "%s %s %s" % (s, SYM.IMP, " ".join(map(str, x)))

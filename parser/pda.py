from .symbol import End

class ParseError(ValueError):
    def __init__(self, i, state, symbol):
        self.i, self.state, self.symbol = i, state, symbol
    def __str__(self):
        return 'Parse Error at #{}: Unexpected Symbol "{}" in State {}'.format(self.i, self.symbol, self.state)

class lr1:
    def __init__(self, terms, nonterms, start, states, shift, reduce):
        self.terms = terms
        self.nonterms = nonterms
        self.start = start
        self.states = states
        self.shift = shift
        self.reduce = reduce
        self.normalize_states()

    # Benenne die Zustände mit Zahlen um.
    def normalize_states(self):
        # Erzeuge eine Numerierung, die mit dem Startzustand beginnt.
        numbering = {self.start : 0}

        for state in self.states.difference({self.start}):
            numbering[state] = len(numbering)
        self.start = 0

        self.shift = {(numbering[state], s): numbering[next] for ((state, s), next) in self.shift.items()}
        self.states = list(range(len(self.states)))
        self.reduce = {(numbering[state], s): rule for ((state, s), rule) in self.reduce.items()}



    # Lese eine Symbolkette
    def parse(self, string, verbose=False):
        # Füge das Endsymbol an.
        string = string + [End()]

        # Zustand-Stack, Symbol-Stack
        states = [self.start]
        symbols = []

        i = 0
        while i < len(string):

            # Versuche shift:
            if (states[-1], type(string[i])) in self.shift:
                states.append(self.shift[(states[-1], type(string[i]))])
                symbols.append(string[i])
                i += 1

            # Versuche zu reduzieren:
            elif (states[-1], type(string[i])) in self.reduce:
                left, right = self.reduce[(states[-1], type(string[i]))]
                # Nehme <length> Symbole vom Stack:
                symbol = left(symbols[len(symbols)-len(right):])
                del symbols[len(symbols)-len(right):], states[len(states)-len(right):]

                symbols.append(symbol)
                states.append(self.shift[(states[-1], left)])
            # Fail:
            else:
                raise ParseError(i, states[-1], string[i])
            if verbose:
                print('Stack: [{0}]'.format(', '.join(x.__class__.__name__ for x in symbols)))
                print("State: ", states)
                print('Tokens: [{0}]'.format(', '.join(x.__class__.__name__ for x in string[i:])))
                print('+++')
        return symbols[0]


    def __str__(self):
        namesort = lambda x:x.__name__
        table = []
        symbols = sorted(self.terms, key=namesort) + sorted(self.nonterms, key=namesort)
        table.append(['State', '$'] + [x.__name__ for x in symbols])
        rules = sorted(set(self.reduce.values()), key=lambda x:x[0].__name__)
        lookup = dict(zip(rules, list(range(len(rules)))))
        for state in self.states:
            row = [str(state)]
            if (state, End) in self.reduce:
                row.append('R {0}'.format(lookup[self.reduce[(state, End)]]))
            else:
                row.append('')
            for e in symbols:
                if (state, e) in self.shift:
                    row.append('S {0}'.format(self.shift[(state, e)]))
                elif (state, e) in self.reduce:
                    row.append('R {0}'.format(lookup[self.reduce[(state, e)]]))
                else:
                    row.append('')
            table.append(row)

        rows = []

        return '+++++++++++++\nState Table:\n{0}\n++++++++++\nReductions:\n{1}\n+++++++++++'.format(
            table_string(table),
            '\n'.join('{0}: {1}'.format(i, rule_string(rule)) for (i, rule) in enumerate(rules))
        )

def state_string(state):
    return '{{\n{0}\n}}'.format('\n'.join(
        '  {0} →  {1} • {2}'.format(
            l.__name__, ' '.join(x.__name__ for x in r[:dot]), ' '.join(x.__name__ for x in r[dot:])
        )
        for (l, r, dot) in state
    ))

def rule_string(rule):
    return '{0} →  {1}'.format(rule[0].__name__, ' '.join(r.__name__ for r in rule[1]) or 'ε')

def table_string(table):
    row_length = max(len(row) for row in table)
    assert all(len(row) == row_length for row in table)
    widths = [max(len(row[j])+2 for row in table) for j in range(row_length)]
    row_width = sum(widths) + row_length + 1
    separator = '\n' + ('+'.join('-'*w for w in widths)) + '\n'
    return separator.join(
        '|'.join(
            cell.center(width) for cell,width in zip(row, widths)
        ) for row in table
    )

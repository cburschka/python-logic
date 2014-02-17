import string

# The Lexer recognizes three types of symbols:
#
# meta: single-character symbols, which are always recognized.
#       if a meta-character is encountered, it is immediately interpreted as a
#       new token, and the previously read string is tokenized.
#
#       meta is a dictionary mapping characters to token classes.
#
#       \ cannot be a meta-character. If escaped with \\, it will be interpreted
#       as part of a name or variable.
#
#
# names: multi-character symbols, which are recognized if and only if they are
#        bounded by meta characters or whitespace. names may contain meta-characters,
#        but such names will only be recognized if the meta-character is escaped
#        with \.
#       
#       names is a dictionary mapping strings to token classes.
#
# variable: any string that does not match a name, and is bounded by whitespace
#           or meta-characters.
#
#       variable is a single token class.
#
# if char_filter is passed, then it will be called on every literal character
# (ie. either non-meta and non-whitespace, or escaped with \).
# All names must consist of accepted characters.
#
class lexer:
    def __init__(self, meta, names, variable, char_filter=None):
        print(char_filter)
        assert '\\' not in meta, '\\ is not an allowed meta character.'
        assert not char_filter or all(all(map(char_filter, name)) for name in names), 'A name contains an unacceptable character.'
        self.meta = meta
        self.names = names
        self.variable = variable
        self.filter = char_filter

    def lex(self, s, debug=False):
        tokens = []
        term = ''
        escape = False

        # Terminate the string with a whitespace character.
        s += ' '

        for i, c in enumerate(s):
            # Find an unescaped backslash; skip and switch to escape mode:
            if not escape and c == '\\':
                escape = True

            # Find an unescaped meta-character.
            elif not escape and (c in self.meta or c in string.whitespace):
                # Terminate the current buffer.
                if term:
                    tokens.append(self.names[term](term) if term in self.names else self.variable(term))
                    term = ''
                # Append the meta symbol.
                if c in self.meta:
                    tokens.append(self.meta[c](c))

            # Finding an allowed literal character:
            elif not self.filter or self.filter(c):
                escape = False
                # Add it to the term buffer:
                term += c
            else:
                raise LexError(i, c)

        if debug:
            print([str(t) for t in tokens])
        return tokens

class LexError(ValueError):
    def __init__(self, i, c):
        self.i, self.c = i, c
    def __str__(self):
        return 'Lexical Error at #{}: {} is not allowed.'.format(self.i, self.c)


# Christoph Burschka, 2012

import core as FO
import symbols as SYM

# Create sequence of symbol tokens
def lex(string):

    # Replace ASCII strings with the Unicode symbols they represent.
    for x,y in SYM.replace:
        string = string.replace(x, y)

    # Add space around reserved symbols to isolate them.
    for character in SYM.reserved:
        string = string.replace(character, ' ' + character + ' ')

    # The input string must have spaces wherever two consecutive tokens are non-FO symbols.
    # This occurs only when a quantified expression starts with a signature symbol.
    # eg. "∀varvar=var" can mean "∀varva r=var" or "∀var var=var"
    return string.split()

class parser:
    def __init__(self, signature, parens = True):
        self.signature = signature
        self.parens = parens
        
    # A recursive implementation of an LR-parser.
    # Parse tokens until a full formula is accepted, then return it along with the unparsed remainder.
    # This allows the parser to recurse into a junction without knowing where to split.
    # The FO grammar is non-ambiguous given a tokenized string and a predefined signature.
    def parse_formula(self, tokens):
        # Read the first token: For anything but an equality, it can be a quantor, an open-paren, a negation or a rel symbol.
        if tokens[0] in SYM.quantors:
            # If it's a quantor, then the next token is a variable. Make sure it is not a reserved symbol.
            quantor = SYM.quantors[tokens[0]]
            if tokens[1] in SYM.reserved or tokens[1] in self.signature:
                raise ValueError("Variable expected but '%s' is reserved symbol." % tokens[1])
            var = FO.Variable(tokens[1])
            
            # Now parse the quantified formula.
            form, remainder = self.parse_formula(tokens[2:])
            return quantor(var, form), remainder
    
        elif tokens[0] == SYM.NOT:
            # If it's a negation operator, then another formula follows.
            form, remainder = self.parse_formula(tokens[1:])
            return FO.Negation(form), remainder
            
        elif tokens[0] == '(':
            # An opening parenthesis indicates a binary formula. Parse the left side...
            form1, remainder = self.parse_formula(tokens[1:])
            
            # After parsing the left side, the remainder must start with a junctor.
            if remainder[0] not in SYM.junctors:
                raise ValueError("Junctor expected but '%s' is not one." % remainder[0])
            operator = SYM.junctors[remainder[0]]
            
            # Then parse the right side.
            form2, remainder = self.parse_formula(remainder[1:])
            
            # Ensure the parentheses are closed:
            if remainder[0] != ')':
                raise ValueError("Close-paren expected, but '%s' found." % remainder[0])
            return operator(form1, form2),remainder[1:]
            
        elif tokens[0] in self.signature and self.signature[tokens[0]][0] == 'relation':
            # A relation symbol is followed by a parenthesized list of terms, parsed by parse_terms().
            # This function will ensure the list length matches the arity of the symbol.
            terms, remainder = self.parse_terms(tokens[1:], self.signature[tokens[0]][1])
            return FO.Relation(tokens[0], terms),remainder

        # None of the above symbols matched the first token. It must be the first term of an equality formula.
        term1, remainder = self.parse_term(tokens)
        if remainder[0] != '=':
            raise ValueError("Token '=' expected, but '%s' found." % remainder[0])
        term2, remainder = self.parse_term(remainder[1:])
        return FO.Equals(term1, term2),remainder

    # Parse a parenthesized, comma-separated list of terms of fixed non-zero length.
    def parse_terms(self, tokens, arity):
        # Ensure the list starts with an opening parenthesis.
        if self.parens:
            start, tokens = tokens[0],tokens[1:]
            if start != '(':
                raise ValueError("Open-paren expected, but '%s' found." % tokens[1])

        # Parse the first term, allowing the loop to handle commas.
        term, tokens = self.parse_term(tokens)
        terms = [term]
        
        # Parse the remaining terms.
        for i in range(1, arity):
            # Check for the comma. If the list closes prematurely, explicitly state the arity mismatch.
            if self.parens:
                sep, tokens = tokens[0], tokens[1:]
                if sep != ',':
                    if sep == ')':
                        raise ValueError("Arity violation: %d terms expected, but only %d found." % (arity, i+1))
                    raise ValueError("Comma expected, but '%s' found." % sep)
                term, tokens = self.parse_term(tokens)
            terms.append(term)

        # Check for a closing parenthesis. If a comma indicates the list goes on, state the arity mismatch.
        if self.parens:
            end, tokens = tokens[0], tokens[1:]
            if end != ')':
                if end == ',':
                    raise ValueError("Arity violation: %d terms expected, but more found." % arity)
            raise ValueError("Close-paren expected, but '%s' found." % end)
        return terms, tokens

    # Parse a term.
    def parse_term(self, tokens):
        if tokens[0] in self.signature:
            t,r = self.signature[tokens[0]]
            if t == 'function':
                terms, remainder = self.parse_terms(tokens[1:], r)
                return FO.Function(symbol, terms), remainder
            elif t == 'constant':
                return FO.Constant(symbol), tokens[1:]
            else:
                # A non-function, non-constant symbol is a relation symbol, which is not allowed in a term.
                raise ValueError("Term expected, but relation symbol '%s' found." % symbol)
        elif tokens[0] in SYM.reserved:
            raise ValueError("Variable expected, but reserved symbol '%s' found." % tokens[0])
        else:
            return FO.Variable(tokens[0]), tokens[1:]

def main(string, signature):
    tokens = lex(string)
    formula, remainder = parser(signature).parse_formula(tokens)
    if remainder:
        raise ValueError("Valid formula '%s' read, but junk follows: '%s'." % (formula, remainder))
    return formula

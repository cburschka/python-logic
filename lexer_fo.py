import symbols as SYM
import parser.symbol
import parser.lexer

class Symbol(parser.symbol.Term):
    pass

class Equality(Symbol):
    pass

class Relation(Symbol):
    pass

class Function(Symbol):
    pass

class Constant(Symbol):
    pass

class Operator(parser.symbol.Term):
    pass

class Quantor(Operator):
    pass

class Junctor(Operator):
    pass

class Not(Operator):
    pass

class LeftParen(Operator):
    pass

class RightParen(Operator):
    pass

class Variable(parser.symbol.Term):
    pass

class Comma(Operator):
    pass

lexer = lambda signature: parser.lexer.lexer(
        meta = {
            SYM.EXISTS: Quantor, SYM.FORALL: Quantor,
            SYM.NOT: Not,
            SYM.AND: Junctor, SYM.OR: Junctor, SYM.IMP: Junctor, SYM.EQ: Junctor,
            '(': LeftParen, ')': RightParen, '=': Equality, ',': Comma
        },
        names = dict(
            [(name, sym) for name, (sym, d) in signature['relations'].items()] +
            [(name, sym) for name, (sym, d) in signature['functions'].items()] +
            [(name, sym) for name, sym in signature['constants'].items()]
        ),
        variable = Variable,
        char_filter = lambda c: ('1' <= c <= '9' or 'a' <= c <= 'z' or 'A' <= c <= 'Z')
    )

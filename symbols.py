# Christoph Burschka, 2012

import core as FO

# Constants for non-ASCII characters.
FORALL = '∀' 
EXISTS = '∃'
NOT    = '¬'
IMP    = '→'
EQ     = '↔'
OR     = '∨'
AND    = '∧'

reserved = {FORALL, EXISTS, NOT, IMP, EQ, OR, AND, '(', ')', ',', '='}
quantors = {FORALL:FO.Forall, EXISTS:FO.Exists}
junctors = {AND:FO.And, OR:FO.Or, IMP:FO.Implies, EQ:FO.Equivalent}
replace = [
    ('.fa.', FORALL),
    ('.ex.', EXISTS),
    ('~'   , NOT),
    ('!'   , NOT),
    ('<->' , EQ),
    ('->'  , IMP),
    ('\/'  , OR),
    ('||'  , OR),
    ('/\\' , AND),
    ('&&'  , AND),
    ('\\forall', FORALL),
    ('\exists', EXISTS),
    ('\\neg'   , NOT),
    ('\leftrightarrow' , EQ),
    ("\left", ""),
    ('\\rightarrow'  , IMP),
    ("\\right", ""),
    ('\\vee'  , OR),
    ('\\wedge' , AND),
]

# Create sequence of symbol tokens
def lex(string):

    # Replace ASCII strings with the Unicode symbols they represent.
    for x,y in replace:
        string = string.replace(x, y)

    # Add space around reserved symbols to isolate them.
    for character in reserved:
        string = string.replace(character, ' ' + character + ' ')

    # The input string must have spaces wherever two consecutive tokens are non-FO symbols.
    # This occurs only when a quantified expression starts with a signature symbol.
    # eg. "∀varvar=var" can mean "∀varva r=var" or "∀var var=var"
    return string.split()
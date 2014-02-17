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



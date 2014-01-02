#!/usr/bin/env python2.7

from codetalker.pgm import Grammar, Translator
from codetalker.pgm.special import star, plus, _or, commas
from codetalker.pgm.tokens import STRING, NUMBER, EOF, NEWLINE, WHITE, ReToken, re, CharToken, StringToken, ReToken

'''Man this looks sweet. It really should be
this easy to write a json parser.'''

# special tokens

QUOTE='\''
LPAREN='('
RPAREN=')'

class SYMBOL(CharToken):
    chars = QUOTE + LPAREN + RPAREN
    num = 3

class IDENT(ReToken):
    rx = re.compile('[^ \t\n\r\f\v\d' + QUOTE + LPAREN + RPAREN + ']+')

# rules (value is the start rule)
def value(rule):
    rule | STRING | NUMBER | IDENT | apply_
    rule.pass_single = True

def apply_(rule):
    rule | (LPAREN, IDENT, star(value), RPAREN)
    rule.astAttrs = {'function': IDENT, 'args': [value]}
apply_.astName = 'Apply'

grammar = Grammar(start=value,
                  tokens=[SYMBOL],
                  ignore=[WHITE, NEWLINE],
                  ast_tokens=[STRING, NUMBER, IDENT])

# translator stuff
lisp = Translator(grammar)

ast = grammar.ast_classes

@lisp.translates(STRING)
def t_string(node):
    return {'type': 'string', 'val': node.value[1:-1].decode('string_escape')}

@lisp.translates(NUMBER)
def t_number(node):
    val=0
    if '.' in node.value or 'e' in node.value.lower():
        val=float(node.value)
    else:
        val=int(node.value)
    return {'type': 'number', 'val': val}

@lisp.translates(IDENT)
def t_ident(node):
    return {'type': 'ident', 'val': node.value}

@lisp.translates(ast.Apply)
def t_apply(node):
    return {'type': 'apply',
            'function': lisp.translate(node.function),
            'args': list(lisp.translate(value) for value in node.args)}

loads = lisp.from_string

import os
import sys
from codetalker.pgm.errors import ParseError, TokenError

def parse(text):
    try:
        print loads(text)
    except (TokenError, ParseError), e:
        if text:
            print>>sys.stderr, text.splitlines()[e.lineno-1]
        else:
            print>>sys.stderr
        print>>sys.stderr, ' '*(e.charno-1)+'^'
        print>>sys.stderr, "Invalid Syntax:", e


if len(sys.argv) > 1:
    if not os.path.isfile(sys.argv[1]):
        print 'Error: arg must be a file path'
        sys.exit(1)
    print 'parsing file: %s' % (sys.argv[1],)
    parse(open(sys.argv[1]).read())
else:
    print 'reading from stdin...'
    parse(sys.stdin.read())

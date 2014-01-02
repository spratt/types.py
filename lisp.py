#!/usr/bin/env python2.7

from codetalker.pgm import Grammar, Translator
from codetalker.pgm.special import star, plus, qstar, qplus, _or, commas
from codetalker.pgm.tokens import STRING, NUMBER, EOF, NEWLINE, WHITE, ReToken, re, CharToken, StringToken, ReToken

# special tokens

QUOTE='\''
LPAREN='('
RPAREN=')'

class SYMBOL(CharToken):
    chars = QUOTE + LPAREN + RPAREN
    num = 3

class IDENT(ReToken):
    rx = re.compile('[^ \t\n\r\f\v\d' + QUOTE + LPAREN + RPAREN + ']+')

class BIND(StringToken):
    strings = ['set']

# rules (value is the start rule)
def expr_list_(rule):
    rule | star(expr_)
    rule.astAttrs = {'values': [expr_]}
expr_list_.astName = 'ExpressionList'

def expr_(rule):
    rule | STRING | NUMBER | IDENT | apply_ | bind_

def apply_(rule):
    rule | (LPAREN, IDENT, star(expr_), RPAREN)
    rule.astAttrs = {'function': IDENT, 'args': [expr_]}
apply_.astName = 'Apply'

def bind_(rule):
    rule | (LPAREN, BIND, IDENT, expr_, RPAREN)
    rule.astAttrs = {'name': IDENT, 'value': expr_}
bind_.astName = 'Bind'

grammar = Grammar(start=expr_list_,
                  tokens=[SYMBOL, BIND],
                  ignore=[WHITE, NEWLINE],
                  ast_tokens=[STRING, NUMBER, IDENT])

# translator stuff
lisp = Translator(grammar)

ast = grammar.ast_classes

@lisp.translates(list)
def t_list(node):
    return [lisp.translate(value) for value in node][0]

@lisp.translates(ast.ExpressionList)
def t_expr_list(node):
    return [lisp.translate(value) for value in node.values]

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

@lisp.translates(ast.Bind)
def t_bind(node):
    return {'type': 'bind',
            'name': lisp.translate(node.name),
            'value': lisp.translate(node.value)}

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

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

class DEFUN(StringToken):
    strings = ['defun']

class BOOL(StringToken):
    strings = ['true', 'false']

# rules (value is the start rule)
def expr_list_(rule):
    rule | star(expr_)
    rule.astAttrs = {'values': [expr_]}
expr_list_.astName = 'ExpressionList'

def expr_(rule):
    rule | STRING | NUMBER | BOOL | IDENT | apply_ | bind_ | defun_

def apply_(rule):
    rule | (LPAREN, IDENT, star(expr_), RPAREN)
    rule.astAttrs = {'function': IDENT, 'args': [expr_]}
apply_.astName = 'Apply'

def bind_(rule):
    rule | (LPAREN, BIND, IDENT, expr_, RPAREN)
    rule.astAttrs = {'name': IDENT, 'value': expr_}
bind_.astName = 'Bind'

def defun_(rule):
    rule | (LPAREN, DEFUN, IDENT, LPAREN, star(IDENT), RPAREN, expr_, RPAREN)
    rule.astAttrs = {'name': IDENT, 'params': [IDENT], 'body': expr_}
defun_.astName = 'Defun'

grammar = Grammar(start=expr_list_,
                  tokens=[SYMBOL, BIND, DEFUN],
                  ignore=[WHITE, NEWLINE],
                  ast_tokens=[STRING, NUMBER, BOOL, IDENT])

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
    return {'kind': 'value', 'type': 'String', 'val': node.value[1:-1].decode('string_escape')}

@lisp.translates(NUMBER)
def t_number(node):
    val=0
    if '.' in node.value or 'e' in node.value.lower():
        return {'kind': 'value', 'type': 'Float', 'term': float(node.value)}
    else:
        return {'kind': 'value', 'type': 'Integer', 'term': int(node.value)}

@lisp.translates(BOOL)
def t_bool(node):
    return {'kind': 'value', 'type': 'Boolean', 'term': bool(node.value)}

@lisp.translates(IDENT)
def t_ident(node):
    return {'kind': 'ident', 'name': node.value}

@lisp.translates(ast.Apply)
def t_apply(node):
    return {'kind': 'apply',
            'name': lisp.translate(node.function),
            'args': list(lisp.translate(value) for value in node.args)}

@lisp.translates(ast.Bind)
def t_bind(node):
    return {'kind': 'bind',
            'name': (lisp.translate(node.name))['name'],
            'term': lisp.translate(node.value)}

@lisp.translates(ast.Defun)
def t_defun(node):
    return {'kind': 'func',
            'name': (lisp.translate(node.name))['name'],
            'args': [{'name': (lisp.translate(param))['name']}
                     for param in node.params][1:],
            'term': lisp.translate(node.body)}

loads = lisp.from_string

import json
import os
import sys
from codetalker.pgm.errors import ParseError, TokenError

def parse(text):
    try:
        print json.dumps(loads(text), sort_keys=True,
                         indent=4, separators=(',', ': '))
    except (TokenError, ParseError), e:
        if text:
            print>>sys.stderr, text.splitlines()[e.lineno-1]
        else:
            print>>sys.stderr
        print>>sys.stderr, ' '*(e.charno-1)+'^'
        print>>sys.stderr, "Invalid Syntax:", e

def main():
    if len(sys.argv) > 1:
        if not os.path.isfile(sys.argv[1]):
            print 'Error: arg must be a file path'
            sys.exit(1)
            parse(open(sys.argv[1]).read())
    else:
        parse(sys.stdin.read())

if __name__ == '__main__':
    main()

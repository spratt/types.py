#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
lisp.py
Copyright 2013-2016 Simon David Pratt
See LICENSE for license information

This program parses a subset of lisp syntax and generates an AST in JSON format.

Lisp parsing partially based on Peter Norvig's lispy code:
http://norvig.com/lispy.html
'''

# special tokens

special_chars = [ '(', ')', '"' ]
COMMENT_CHAR = ';'

def parse_begin(tokens):
    L = []
    while tokens[0] != ')':
        L.append(read_from_tokens(tokens))
    tokens.popleft() # pop off ')'
    return L

def parse_set(tokens):
    node = {'kind' : 'bind',
            'name' : parse_ident(tokens),
            'term' : read_from_tokens(tokens)}
    tokens.popleft() # pop off ')'
    return node

def parse_defun(tokens):
    name = parse_ident(tokens)
    args = []
    tokens.popleft() # pop off '('
    while tokens[0] != ')':
        args.append({'name': tokens.popleft()})
    tokens.popleft() # pop off ')'
    node = {'kind' : 'func',
            'name' : name,
            'args' : args,
            'term' : read_from_tokens(tokens)}
    tokens.popleft() # pop off ')'
    return node

special_forms = {
    'begin' : parse_begin,
    'set'   : parse_set,
    'defun' : parse_defun
}

def strip_comments(s):
    lines = []
    for line in s.split('\n'):
        if COMMENT_CHAR in line:
            lines.append(line[:line.index(COMMENT_CHAR)])
        else:
            lines.append(line)
    return '\n'.join(lines)

from collections import deque

def tokenize(s):
    s = strip_comments(s)
    for special_char in special_chars:
        s = s.replace(special_char, ' ' + special_char + ' ')
    return deque(s.split())

def parse_string(tokens):
    ret = []
    tokens.popleft() # pop off '"'
    while tokens[0] != '"':
        ret.append(tokens.popleft())
    tokens.popleft() # pop off '"'
    return {'kind' : 'value',
            'type' : 'String',
            'term' : ''.join(ret)}

def parse_ident(tokens):
    return tokens.popleft()

def parse_boolean(tokens):
    return {'kind'  : 'value',
            'type'  : 'Boolean',
            'value' : tokens.popleft() == 'true'}

import re
def is_number(token):
    return re.match('\d+(\.\d*)?', token)

def parse_number(tokens):
    node = {'kind' : 'value'}
    try:
        token = tokens.popleft()
        if '.' in token:
            node['type'] = 'Float'
            node['value'] = float(token)
        else:
            node['type'] = 'Integer'
            node['value'] = int(token)
    except:
        raise SyntaxError('Invalid atom')
    return node

def parse_symbol(tokens):
    return {'kind' : 'ident',
            'name' : tokens.popleft()}

def parse_atom(tokens):
    if tokens[0] == '"':
        return parse_string(tokens)
    elif tokens[0] == 'false' or tokens[0] == 'true':
        return parse_boolean(tokens)
    elif is_number(tokens[0]):
        return parse_number(tokens)
    else:
        return parse_symbol(tokens)

def read_from_tokens(tokens):
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    if tokens[0] == '(':
        tokens.popleft() # pop off '('
        if tokens[0] in special_forms:
            ident = parse_ident(tokens)
            return special_forms[ident](tokens)
        else:
            node = {'kind' : 'apply',
                    'name' : parse_symbol(tokens),
                    'args' : []}
            while tokens[0] != ')':
                node['args'].append(read_from_tokens(tokens))
            tokens.popleft() # pop off ')'
            return node
    elif tokens[0] == ')':
        raise SyntaxError('unexpected )')
    else:
        return parse_atom(tokens)
    
def parse(text):
    return read_from_tokens(tokenize(text))

def dictToPrettyJSON(d, encoder = None):
    import json
    if encoder == None:
        encoder = json.JSONEncoder
    return json.dumps(d, sort_keys=True, indent=2,
                      separators=(',', ': '), cls=encoder)

def printAST(text):
    print(dictToPrettyJSON(parse(text)))

def main():
    import os
    import sys
    if len(sys.argv) > 1:
        if not os.path.isfile(sys.argv[1]):
            print 'Error: arg must be a file path'
            sys.exit(1)
        printAST(open(sys.argv[1]).read())
    else:
        printAST(sys.stdin.read())

if __name__ == '__main__':
    main()

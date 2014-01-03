#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
types.py
Copyright 2013-2014 Simon David Pratt
See LICENSE for license information

This program adds types to an AST in JSON format using
Damas-Hindley-Milner's Algorithm W for infering types
'''

import sys

# Exceptions ###################################################################

class UndefinedIdentifierException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)

# Types ########################################################################

class Type(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class FunctionType(Type):
    def __init__(self, args):
        super(FunctionType, self).__init__('Function', args)
        
class VarType(object):
    tuid = 0

    @staticmethod
    def inc_tuid():
        VarType.tuid += 1
        return VarType.tuid
    
    def __init__(self):
        self.id = VarType.inc_tuid()
        self.type = None

# Type Inference Class #########################################################
        
class Types(object):
    def __init__(self, ast):
        self.ast = ast
        self._types = []
        for node in self.ast:
            try:
                self._types.append(self._infer(node))
            except UndefinedIdentifierException as e:
                print>>sys.stderr, ('ERROR! Undefined identifier: {}'
                                    .format(str(e)))
    
    def _fresh(self, env, known):
        # TODO
        pass

    def _taggedType(self, node):
        # TODO
        pass

    def _unify(self, first_type, second_type):
        # TODO
        pass

    def _visit_value(self, node, env, known):
        return self._taggedType(node)

    def _visit_ident(self, node, env, known):
        if node['name'] not in env:
            raise UndefinedIdentifierException(node['name'])
        return self._fresh(env['name'], known)

    def _visit_apply(self, node, env, known):
        args=[]
        for arg in node['args']:
            args.append(self._infer(arg, env, known))
        this_type = VarType()
        args.append(this_type)
        self._unify(FunctionType(args), self._infer(node['name'], env, known))
        return this_type

    def _visit_bind(self, node, env, known):
        # TODO
        pass

    def _visit_func(self, node, env, known):
        # TODO
        pass

    def _visit(self, node):
        # an ugly way to dynamically return a method on this object UGLY
        return ({
            'value': self._visit_value,
            'ident': self._visit_ident,
            'apply': self._visit_apply,
            'bind':  self._visit_bind,
            'func':  self._visit_func
        })[(node['kind'])]

    def _infer(self, node, env=None, known=None):
        if env == None: env = {}
        if known == None: known = []
        # get a method from the _visit dispatch and call it UGLY
        return (self._visit(node))(node, env, known)

# Entry Points #################################################################
        
def infer(ast_str):
    import json
    from lisp import dictToPrettyJSON
    ast = json.loads(ast_str)
    types = Types(ast)
    print(dictToPrettyJSON(types.ast))
        
def main():
    import os
    if len(sys.argv) > 1:
        if not os.path.isfile(sys.argv[1]):
            print 'Error: arg must be a file path'
            sys.exit(1)
        infer(open(sys.argv[1]).read())
    else:
        infer(sys.stdin.read())

if __name__ == '__main__':
    main()

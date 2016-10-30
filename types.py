#!/usr/bin/env python3
'''
types.py
Copyright 2013-2014 Simon David Pratt
See LICENSE for license information

This program adds types to an AST in JSON format using
Damas-Hindley-Milner's Algorithm W for infering types
'''

import sys
import json

# Exceptions ###################################################################

class IdentifierException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)

class UnificationException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)

class IncompatibleTypesException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)

# Types ########################################################################

class TypeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Type) or isinstance(obj, VarType):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

class Type(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

class FunctionType(Type):
    def __init__(self, args):
        super(FunctionType, self).__init__('Function', args)

    def __str__(self):
        return 'Function<{}>'.format(self.args)

    def __repr__(self):
        return str(self)
        
class VarType(object):
    tuid = 0

    @staticmethod
    def inc_tuid():
        VarType.tuid += 1
        return VarType.tuid
    
    def __init__(self):
        self.id = VarType.inc_tuid()
        self.type = None

    def __str__(self):
        return 'VarType({},{})'.format(self.id, self.type)

    def __repr__(self):
        return str(self)

# Type Inference Class #########################################################
        
class Types(object):
    tagged = {
        u'Boolean': lambda: Type(u'Boolean', []),
        u'Integer': lambda: Type(u'Integer', []),
        u'Float':   lambda: Type(u'Float',   []),
        u'String':  lambda: Type(u'String',  [])
    }
                
    @staticmethod
    def _taggedType(node):
        if node['type'] in Types.tagged:
            return Types.tagged[node['type']]()
        return node
    
    def __init__(self, ast):
        self.ast = ast
        self._types = []
        env = {}
        for node in self.ast:
            try:
                self._types.append(self._infer(node, env))
            except IdentifierException as e:
                print('ERROR! Undefined identifier: {}'.format(str(e)),
                      file=sys.stderr)

    # Inference methods ########################################################

    @staticmethod
    def _unify(t, s):
        t = Types._prune(t)
        s = Types._prune(s)
        if isinstance(t, VarType):
            if t != s:
                if Types._occursCheck(t, s):
                    raise UnificationException('Recursive Unification')
                t.type = s
        elif isinstance(t, Type) and isinstance(s, VarType):
            Types._unify(s, t)
        elif isinstance(t, Type) and isinstance(s, Type):
            if t.name != s.name or len(t.args) != len(s.args):
                raise IncompatibleTypesException(
                    '{} is incompatible with {}'.format(t.name, s.name))
            for targ, sarg in zip(t.args, s.args):
                Types._unify(targ, sarg)
        else:
            raise UnificationException('Undecided unification')

    @staticmethod
    def _fresh(t, types, vrs = None):
        if vrs == None: vrs = {}
        t = Types._prune(t)
        if isinstance(t, VarType):
            if not Types._occursChecks(t, types):
                if t.id not in vrs:
                    vrs[t.id] = VarType()
                return vrs[t.id]
            return t
        args = []
        for arg in t.args:
            args.append(Types._fresh(arg, types, vrs))
        return Type(t.name, args)

    @staticmethod
    def _prune(t):
        if isinstance(t, VarType) and t.type != None:
            t.type = Types._prune(t.type)
            return t.type
        return t

    @staticmethod
    def _occursCheck(t, s):
        s = Types._prune(s)
        if t == s:
            return True
        elif isinstance(s, Type):
            return Types._occursChecks(t, s.args)
        return False

    @staticmethod
    def _occursChecks(t, types):
        for type_ in types:
            if Types._occursCheck(t, type_):
                return True
        return False

    # Visitor methods ##########################################################

    def _visit_value(self, node, env, known):
        return self._taggedType(node)

    def _visit_ident(self, node, env, known):
        if node['name'] not in env:
            raise IdentifierException(node['name'])
        return Types._fresh(env[node['name']], known)

    def _visit_apply(self, node, env, known):
        args=[]
        for arg in node['args']:
            args.append(self._infer(arg, env, known))
        this_type = VarType()
        args.append(this_type)
        Types._unify(FunctionType(args), self._infer(node['name'], env, known))
        return this_type

    def _visit_bind(self, node, env, known):
        this_type = self._infer(node['term'], env, known)
        if 'type' in node:
            Types._unify(this_type, self._taggedType(node))
        env[node['name']] = this_type
        return this_type

    def _visit_func(self, node, env, known):
        args = []
        types = known[:]
        for arg in node['args']:
            if 'type' not in arg:
                arg_type = VarType()
                types.append(arg_type)
            else:
                arg_type = self._taggedType(arg)
            env[arg['name']] = arg_type
            args.append(arg_type)
        result = self._infer(node['term'], env, types)
        args.append(result)
        if 'type' in node:
            Types._unify(result, self._taggedType(node))
        this_type = FunctionType(args)
        if 'name' in node:
            env[node['name']] = this_type
        return this_type

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
        t = (self._visit(node))(node, env, known)
        node['type'] = t
        return t

# Entry Points #################################################################
        
def infer(ast_str):
    from lisp import dictToPrettyJSON
    ast = json.loads(ast_str)
    types = Types(ast)
    print(dictToPrettyJSON(types.ast, TypeEncoder))
    print(types._types, file=sys.stderr)
        
def main():
    import os
    if len(sys.argv) > 1:
        if not os.path.isfile(sys.argv[1]):
            print('Error: arg must be a file path')
            sys.exit(1)
        infer(open(sys.argv[1]).read())
    else:
        infer(sys.stdin.read())

if __name__ == '__main__':
    main()

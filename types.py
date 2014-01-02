#!/usr/bin/env python2.7
'''
types.py
Copyright 2013-2014 Simon David Pratt
See LICENSE for license information

This program adds type inference to an AST in JSON format
'''

class Types(object):
    def __init__(self, ast):
        self.ast = ast
        self._infer()

    def _infer(self):
        pass

def infer(ast_str):
    import json
    from lisp import dictToPrettyJSON
    ast = json.loads(ast_str)
    types = Types(ast)
    print(dictToPrettyJSON(types.ast))
        
def main():
    import os
    import sys
    if len(sys.argv) > 1:
        if not os.path.isfile(sys.argv[1]):
            print 'Error: arg must be a file path'
            sys.exit(1)
        infer(open(sys.argv[1]).read())
    else:
        infer(sys.stdin.read())

if __name__ == '__main__':
    main()

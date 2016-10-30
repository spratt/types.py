types.py
========
By Simon David Pratt

An implementation of Damas-Hindley-Milner's Algorithm W for infering types.

Files:

- `types.py`: Takes a JSON AST and infers types.
- `lisp.py`: Parses a simple lisp dialect and prints a JSON AST.
- `test.lisp`: An example of the simple lisp dialect.
- `test.ast`: The JSON AST of `test.lisp`.
- `test.tast`: The JSON AST of `test.lisp` with types inferred.

Usage:

`python3 lisp.py test.lisp` output should match `test.ast`.

`python3 types.py test.ast` output should match `test.tast`.

`python3 -m doctest lisp.py` runs doctests.

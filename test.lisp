; This is a comment preceding the first term
(begin
 ; This is a comment comment within the first term
 "this is a string"
 42
 (set x 5)
 (defun foo (a b c)
   5)
 (foo 1 2 x)
 (set num 100)
 (defun id (x)
   x)
 (defun any-to-100 (s)
   num)
 (id true)
 (any-to-100 "abc")
 (any-to-100 200)
 (any-to-100 (id false)))

from globalTypes import * 
from Parser import * 

f = open('sample.c-', 'r')
#f = open('sample2.c-', 'r')
programa = f.read()
progLong = len(programa)
programa = programa + '$'
posicion = 0

globales(programa, posicion, progLong)

AST = parse(True)

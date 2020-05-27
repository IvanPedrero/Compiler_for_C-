from globalTypes import * 
from Parser import * 
from semantica import *
from CGen import *

f = open('sample.c-', 'r')
programa = f.read()
progLong = len(programa)
programa = programa + '$'
posicion = 0

globales(programa, posicion, progLong)

AST = parser(False)
semantica(AST, False)
codeGen(AST, "file.s")
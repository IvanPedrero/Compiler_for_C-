from globalTypes import *


def globales(prog,pos,long):
    global programa
    global p
    global progLong
    programa = prog
    p = pos
    progLong = long

def getToken(imprime = True):

    with open('matriz.txt') as f:
        fil,col=[int(x) for x in next(f).split()]
        simbolos = next(f).split('|')
        M = [[int(x) for x in line.split()] for line in f]

    #f = open('ejemplo.txt', 'r')
    archivo = programa
    longitud = progLong
    global p
    estado = 0
    token = ''

    #print("\nToken                      Tipo\n")

    #Save the simbols to a map.
    mapa ={}
    for i in range(len(simbolos)):
        for c in simbolos[i]:
            mapa[c] = i

    #Define the counter.
    

    #Traverse the array till an EOF is encountered.
    while c != '$':
        #Save the current char.
        c = archivo[p]

        t = ''

        #If an EOL is encountered, go to the final state of COMMENTS.
        if (c == "$"):
            return TokenType.ENDFILE, "$"
        
        if(c == '\n' and estado == 9):
            estado = 9

        estado = M[estado][mapa[c]]
             
        if(estado == 2):
            # NUM      
            t = token
            printToken(t, "NUM", imprime)
            token = ''
            estado = 0
            return TokenType.NUM, t 
        elif(estado == 4):
            # ID
            t = token
            token = ''
            estado = 0

            if t in reserved_keywords:
                printToken(t, "RESERVED", imprime)
                return TokenType.RESERVED, t
            else:
                printToken(t, "ID", imprime)
                return TokenType.ID, t
        elif(estado == 5):
            # + 
            t = token
            printToken(c, "PLUS", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.PLUS, t
        elif(estado == 6):
            # - 
            t = token
            printToken(c, "MINUS", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.MINUS, t
        elif(estado == 7):
            # * 
            token += c
            t = token
            printToken(t, "MULT", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.MULT, t
        elif(estado == 11):
            # /* comment */
            token += c
            t = token
            printToken(t, "COMMENT", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.COMMENT, t
        elif(estado == 12):
            # Division
            t = token
            printToken(t, "DIVISION", imprime)
            token = ''
            estado = 0
            return TokenType.DIVISION, t
        elif(estado == 14):
            # >= 
            token += c
            t = token
            printToken(t, "GREATER EQUAL", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.GREATER_EQUAL, t
        elif(estado == 15):
            # > 
            t = token
            printToken(t, "GREATER", imprime)
            token = ''
            estado = 0
            return TokenType.GREATER, t
        elif(estado == 17):
            # < 
            token += c
            t = token
            printToken(t, "LESS EQUAL", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.LESS_EQUAL, t
        elif(estado == 18):
            # < 
            t = token
            printToken(t, "LESS", imprime)
            token = ''
            estado = 0
            return TokenType.LESS, t
        elif(estado == 20):
            # ==
            token += c
            t = token
            printToken(t, "EQUALS TO", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.EQUALS_TO, t
        elif(estado == 21):
            # =
            t = token
            printToken(t, "EQUAL", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.EQUAL, t
        elif(estado == 23):
            # !=
            token += c
            t = token
            printToken(t, "DIFFERENT", imprime)
            token = ''
            estado = 0
            p = p + 1
            c = archivo[p]
            return TokenType.DIFFERENT, t
        elif(estado == 24):
            # ;
            t = token
            printToken(c, "SEMICOLON", imprime)
            token = ''
            estado = 0
            p += 1
            c = archivo[p]
            return TokenType.SEMICOLON, t
        elif(estado == 25):
            # ,
            t = token
            printToken(c, "COMMA", imprime)
            token = ''
            estado = 0
            p += 1
            c = archivo[p]
            return TokenType.COMMA, t
        elif(estado == 26):
            # (
            t = token
            printToken(c, "OPEN_BRACKETS", imprime)
            token = ''
            estado = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_BRACKETS, t
        elif(estado == 27):
            # )
            t = token
            printToken(c, "CLOSE_BRACKETS", imprime)
            token = ''
            estado = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_BRACKETS, t
        elif(estado == 28):
            # (
            t = token
            printToken(c, "OPEN_SQUARE_BRACKETS", imprime)
            token = ''
            estado = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_SQUARE_BRACKETS, t
        elif(estado == 29):
            # )
            t = token
            printToken(c, "CLOSE_SQUARE_BRACKETS", imprime)
            token = ''
            estado = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_SQUARE_BRACKETS, t
        elif(estado == 30):
            # (
            t = token
            printToken(c, "OPEN_CURLY_BRACKETS", imprime)
            token = ''
            estado = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_CURLY_BRACKETS, t
        elif(estado == 31):
            # )
            t = token
            printToken(c, "CLOSE_CURLY_BRACKETS", imprime)
            token = ''
            estado = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_CURLY_BRACKETS, t
        elif(estado == 33):
            # ERROR
            t = token
            printToken(t, "ERROR", imprime)
            
            detectIntegerError(t)

            token = ''
            estado = 0
            return TokenType.ERROR, t
        elif estado != 0:
            #Get all the char and save them to the tokens.
            token += c
            #Add to the counter.
            p += 1
        else:
            #Add to the counter.
            p += 1
    else:
        return TokenType.ENDFILE, "$"

def printToken(t, tokenType, imprime):
    if imprime:
        print(t," = ",tokenType)

def detectIntegerError(lookup):
    lookup = lookup.replace('$', '').translate({ord(i): None for i in ' '})
    i = 0
    for item in programa.split("\n"):
        i = i + 1
        indicator = ""
        if lookup in item:
            errorIndex = item.index(lookup)
            indicator += (' '*errorIndex) + "^"
            print("\nTraceback (most recent call last):")
            print ("Linea ", i ,": Error en la formación de un entero:")
            print(item.replace('$', ''))
            print(indicator)

        

from globalTypes import *


def globales(prog,pos,long):
    global programa
    global p
    global progLong
    programa = prog
    # Avoid not reading last character adding an space before the EOF.
    programa = programa.replace('$', ' $')
    p = pos
    progLong = long

def getToken(imprime = True):

    with open('matriz.txt') as f:
        fil,col=[int(x) for x in next(f).split()]
        simbolos = next(f).split('|')
        M = [[int(x) for x in line.split()] for line in f]

    archivo = programa
    longitud = progLong
    global p
    state = 0
    token = ''

    #Save the simbols to a map.
    mapa ={}
    for i in range(len(simbolos)):
        for c in simbolos[i]:
            mapa[c] = i

    #Traverse the array till an EOF is encountered.
    while c != '$':
        #Save the current char.
        c = archivo[p]

        t = ''

        #If an EOL is encountered, go to the final state of COMMENTS.
        if (c == "$"):
            return TokenType.ENDFILE, "$"
        
        # Add to the comments the EOL if needed.
        if(c == '\n' and state == 9):
            state = 9

        state = M[state][mapa[c]]
             
        if(state == 2):
            # NUM      
            t = token
            printToken(t, TokenType.NUM, imprime)
            token = ''
            state = 0
            return TokenType.NUM, t 
        elif(state == 4):
            # ID
            t = token
            token = ''
            state = 0

            if t in reserved_keywords:
                printToken(t, getReservedKeyWord(t), imprime)
                return TokenType.RESERVED, t
            else:
                printToken(t, TokenType.ID, imprime)
                return TokenType.ID, t
        elif(state == 5):
            # + 
            t = token
            printToken(c, TokenType.PLUS, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.PLUS, t
        elif(state == 6):
            # - 
            t = token
            printToken(c, TokenType.MINUS, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.MINUS, t
        elif(state == 7):
            # * 
            token += c
            t = token
            printToken(t, TokenType.MULT, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.MULT, t
        elif(state == 11):
            # /* comment */
            token += c
            t = token
            printToken(t, TokenType.COMMENT, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.COMMENT, t
        elif(state == 12):
            # Division
            t = token
            printToken(t, TokenType.DIVISION, imprime)
            token = ''
            state = 0
            return TokenType.DIVISION, t
        elif(state == 14):
            # >= 
            token += c
            t = token
            printToken(t, TokenType.GREATER_EQUAL, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.GREATER_EQUAL, t
        elif(state == 15):
            # > 
            t = token
            printToken(t, TokenType.GREATER, imprime)
            token = ''
            state = 0
            return TokenType.GREATER, t
        elif(state == 17):
            # < 
            token += c
            t = token
            printToken(t, TokenType.LESS_EQUAL, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.LESS_EQUAL, t
        elif(state == 18):
            # < 
            t = token
            printToken(t, TokenType.LESS, imprime)
            token = ''
            state = 0
            return TokenType.LESS, t
        elif(state == 20):
            # ==
            token += c
            t = token
            printToken(t, TokenType.EQUALS_TO, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.EQUALS_TO, t
        elif(state == 21):
            # =
            t = token
            printToken(t, TokenType.EQUAL, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.EQUAL, t
        elif(state == 23):
            # !=
            token += c
            t = token
            printToken(t, TokenType.DIFFERENT, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.DIFFERENT, t
        elif(state == 24):
            # ;
            t = token
            printToken(c, TokenType.SEMICOLON, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.SEMICOLON, t
        elif(state == 25):
            # ,
            t = token
            printToken(c, TokenType.COMMA, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.COMMA, t
        elif(state == 26):
            # (
            t = token
            printToken(c, TokenType.OPEN_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_BRACKETS, t
        elif(state == 27):
            # )
            t = token
            printToken(c, TokenType.CLOSE_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_BRACKETS, t
        elif(state == 28):
            # (
            t = token
            printToken(c, TokenType.OPEN_SQUARE_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_SQUARE_BRACKETS, t
        elif(state == 29):
            # )
            t = token
            printToken(c, TokenType.CLOSE_SQUARE_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_SQUARE_BRACKETS, t
        elif(state == 30):
            # (
            t = token
            printToken(c, TokenType.OPEN_CURLY_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_CURLY_BRACKETS, t
        elif(state == 31):
            # )
            t = token
            printToken(c, TokenType.CLOSE_CURLY_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_CURLY_BRACKETS, t
        elif(state == 33):
            # ERROR
            t = token
            printToken(t, TokenType.ERROR, imprime)
            
            detectIntegerError(t)

            token = ''
            state = 0
            return TokenType.ERROR, t
        elif state != 0:
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
        print(t," = ",tokenType.name)

def detectIntegerError(lookup):
    lookup = lookup.replace('$', '').translate({ord(i): None for i in ' '})
    i = 0
    for line in programa.split("\n"):
        i = i + 1
        indicator = ""
        if lookup in line:
            errorIndex = line.index(lookup)
            indicator += (' '*errorIndex) + "^"
            print("\nTraceback (most recent call last):")
            print ("Linea ", i ,": Error in the formation of an integer:")
            print(line.replace('$', ''))
            print(indicator)

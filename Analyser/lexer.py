from globalTypes import *

def globales_lexer(prog,pos,long):
    global programa
    global currentLine
    global progLong
    global p
    global currentLine

    # Decode the latin characters and decode them in utf-8.
    prog = prog.encode("latin-1").decode("utf-8")

    # Avoid not reading last character adding an space before the EOF.
    prog = prog.replace('$', ' $')

    # Assign the global values.
    programa = prog
    p = pos
    progLong = long

    # Set the line counter to 1.
    currentLine = 1

'''
This function will return a token [TokenType, string]
from the program file given in the 
function globales().
'''
def getToken(imprime = True):

    # Open the matrix to make the calculations of the table.
    with open('matriz.txt') as f:
        fil,col=[int(x) for x in next(f).split()]
        simbolos = next(f).split('|')
        M = [[int(x) for x in line.split()] for line in f]

    # Define the local variables and the scope of the globals that the function will use.
    global p
    global currentLine
    archivo = programa
    longitud = progLong
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

        # Temporal variable to return the values of the token after wiping the token.
        t = ''

        if(c == "\n" and state != 32):
            currentLine = currentLine + 1
        
        # If an EOL is encountered, go to the final state of COMMENTS.
        if (c == "$"):
            return TokenType.ENDFILE, "$", currentLine
        
        # Add to the comments the EOL if needed.
        if(c == '\n' and state == 9):
            state = 9

        # Allow unknown symbols inside the comments.
        if(c not in mapa and state == 9):
            token += c
            state = 9
            p = p + 1
            c = archivo[p]
        # Detect unknown symbols outside the comments.
        elif(c not in mapa and state != 9):
            state = 34
            token += c
            p = p + 1
            c = archivo[p]
            while(c not in mapa):
                token += c
                p = p + 1
                c = archivo[p]

        # Only calculate the state if the character is valid.
        if c in mapa:
            state = M[state][mapa[c]]

        if(state == 2):
            # NUM      
            t = token
            printToken(t, TokenType.NUM, imprime)
            token = ''
            state = 0
            return TokenType.NUM, t, currentLine
        elif(state == 4):
            # ID
            t = token
            token = ''
            state = 0

            if t in reserved_keywords:
                printToken(t, getReservedKeyWord(t), imprime)
                return getReservedKeyWord(t), t, currentLine
            else:
                printToken(t, TokenType.ID, imprime)
                return TokenType.ID, t, currentLine
        elif(state == 5):
            # + 
            t = token
            printToken(c, TokenType.PLUS, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.PLUS, t, currentLine
        elif(state == 6):
            # - 
            t = token
            printToken(c, TokenType.MINUS, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.MINUS, t, currentLine
        elif(state == 7):
            # * 
            token += c
            t = token
            printToken(t, TokenType.MULT, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.MULT, t, currentLine
        elif(state == 11):
            # /* comment */
            token += c
            t = token
            printToken(t, TokenType.COMMENT, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.COMMENT, t, currentLine
        elif(state == 12):
            # Division
            t = token
            printToken(t, TokenType.DIVISION, imprime)
            token = ''
            state = 0
            return TokenType.DIVISION, t, currentLine
        elif(state == 14):
            # >= 
            token += c
            t = token
            printToken(t, TokenType.GREATER_EQUAL, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.GREATER_EQUAL, t, currentLine
        elif(state == 15):
            # > 
            t = token
            printToken(t, TokenType.GREATER, imprime)
            token = ''
            state = 0
            return TokenType.GREATER, t, currentLine
        elif(state == 17):
            # < 
            token += c
            t = token
            printToken(t, TokenType.LESS_EQUAL, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.LESS_EQUAL, t, currentLine
        elif(state == 18):
            # < 
            t = token
            printToken(t, TokenType.LESS, imprime)
            token = ''
            state = 0
            return TokenType.LESS, t, currentLine
        elif(state == 20):
            # ==
            token += c
            t = token
            printToken(t, TokenType.EQUALS_TO, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.EQUALS_TO, t, currentLine
        elif(state == 21):
            # =
            t = token
            printToken(t, TokenType.EQUAL, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.EQUAL, t, currentLine
        elif(state == 23):
            # !=
            token += c
            t = token
            printToken(t, TokenType.DIFFERENT, imprime)
            token = ''
            state = 0
            p = p + 1
            c = archivo[p]
            return TokenType.DIFFERENT, t, currentLine
        elif(state == 24):
            # ;
            t = token
            printToken(c, TokenType.SEMICOLON, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.SEMICOLON, t, currentLine
        elif(state == 25):
            # ,
            t = token
            printToken(c, TokenType.COMMA, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.COMMA, t, currentLine
        elif(state == 26):
            # (
            t = token
            printToken(c, TokenType.OPEN_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_BRACKETS, t, currentLine
        elif(state == 27):
            # )
            t = token
            printToken(c, TokenType.CLOSE_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_BRACKETS, t, currentLine
        elif(state == 28):
            # [
            t = token
            printToken(c, TokenType.OPEN_SQUARE_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_SQUARE_BRACKETS, t, currentLine
        elif(state == 29):
            # ]
            t = token
            printToken(c, TokenType.CLOSE_SQUARE_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_SQUARE_BRACKETS, t, currentLine
        elif(state == 30):
            # {
            t = token
            printToken(c, TokenType.OPEN_CURLY_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.OPEN_CURLY_BRACKETS, t, currentLine
        elif(state == 31):
            # }
            t = token
            printToken(c, TokenType.CLOSE_CURLY_BRACKETS, imprime)
            token = ''
            state = 0
            p += 1
            c = archivo[p]
            return TokenType.CLOSE_CURLY_BRACKETS, t, currentLine
        elif(state == 33): 
            # ERROR
            t = token

            # Print the error.
            printToken(t, TokenType.ERROR, imprime)

            # Detect if it was an unknown symbol.            
            detectIntegerError(t)

            token = ''
            state = 0
            return TokenType.ERROR, t, currentLine
        elif(state == 35): 
            # ERROR
            t = token

            # Detect if it was an unknown symbol.            
            detectUnknownSymbolError(t)

            # Print the unknown error.
            printToken(t, TokenType.ERROR, imprime)

            token = ''
            state = 0

            return TokenType.ERROR, t, currentLine
        elif state != 0:
            #Get all the char and save them to the tokens.
            token += c
            #Add to the counter.
            p += 1
        else:
            #Add to the counter.
            p += 1
    else:
        return TokenType.ENDFILE, "$", currentLine

'''
This function will print the token and it's 
value if the boolean flag is set to true.
'''
def printToken(t, tokenType, imprime):
    if imprime:
        print(t," = ",tokenType)

'''
This function will print the line where a given 
error is found and the position in the line
(Only for errors in the formation of integers 
or variables).
'''
def detectIntegerError(lookup):
    global currentLine

    indicator = ""

    # Get the current line as a string.
    line = programa.split("\n")[currentLine-1]

    # Get the index where the error is in the line.
    errorIndex = line.find(lookup) 

    # Set the indicator of the error.
    indicator += (' '*errorIndex) + "^"

    # Print the error.
    print("\nTraceback (most recent call last):")
    print ("Line ", currentLine ,": Error in the formation of an integer:")
    print(line.replace('$', ''))
    print(indicator,"\n")

    #currentLine = currentLine - 1
  
'''
This function will print the line where a given 
error is found and the position in the line
(Only for errors where an unknown character
[or string] was found).
'''
def detectUnknownSymbolError(lookup):
    global currentLine
    
    lineNumbers = len(programa.split("\n"))

    indicator = ""

    # Avoid length errors.
    if currentLine > lineNumbers:
        return

    # Get the current line as a string.
    line = programa.split("\n")[currentLine-1]

    # Avoid looking for the error if not in line
    if lookup not in line:
        return

    # Get the index where the error is in the line.
    errorIndex = line.find(lookup) 

    # Set the indicator of the error.
    indicator += (' '*errorIndex) + "^"

    # Print the error.
    print("\nTraceback (most recent call last):")
    print ("Line ", currentLine ,": Unknown symbol error:")
    print(line.replace('$', ''))
    print(indicator,"\n")

    currentLine = currentLine - 1

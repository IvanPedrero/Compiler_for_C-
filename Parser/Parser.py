from globalTypes import *
from lexer import *

programa = None
posicion = None
progLong = None
lineno = 0

token = None
tokenString = None

Error = False
SintaxTree = None

imprimeScanner = False


def globales(prog, pos, long):
    global programa
    global posicion
    global progLong
    programa = prog
    posicion = pos
    progLong = long


def syntaxError(message):
    global Error

    if Error != True:
        #print("\n>>> Syntax error at line " + str(lineno) + ": " + message)
        Error = True
        detectError(tokenString, message)

    match(token)


def detectError(lookup, message):
    global lineno

    indicator = ""

    # Get the current line as a string.
    line = programa.split("\n")[lineno-1]

    # Get the index where the error is in the line.
    errorIndex = line.find(lookup) 

    # Set the indicator of the error.
    indicator += (' '*errorIndex) + "^"

    # Print the error.
    print("\nTraceback (most recent call last):")
    print ("Line ", lineno ,": ", message)
    print(line.replace('$', ''))
    print(indicator,"\n")



def match(expected):
    global token, tokenString, lineno, imprimeScanner
    if (token == expected):
        token, tokenString, lineno = getToken(imprimeScanner)
    else:
        '''
        syntaxError("unexpected token at matching -> ")
        printToken(token,tokenString, imprimeScanner)
        print("Expected : ", expected)
        print("      ")
        '''
        syntaxError("Unexpected token at matching")


def matchType():
    global token, tokenString, lineno, imprimeScanner

    tokenType = TokenType.VOID

    if token == TokenType.INT:
        tokenType = TokenType.INT
        token, tokenString, lineno = getToken(imprimeScanner)
    elif token == TokenType.VOID:
        tokenType = TokenType.VOID
        token, tokenString, lineno = getToken(imprimeScanner)
    else:
        syntaxError("Expected a type identifier")
        '''printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken(imprimeScanner)'''

    return tokenType


def is_a_type(tok):
    if tok == TokenType.INT or tok == TokenType.VOID:
        return True
    else:   
        return False


def declaration_list():
    t = None
    p = None

    if token == TokenType.COMMENT:
        match(TokenType.COMMENT)

    t = declaration()
    p = t
    
    while token != TokenType.ENDFILE:

        if token == TokenType.COMMENT:
            match(TokenType.COMMENT)

        q = None

        q = declaration()

        if q != None and p != None:
            p.sibling = q
            p = q

    return t


def declaration():
    global token, tokenString, lineno, imprimeScanner
    #print("STATEMENT: ", token, lineno)

    t = None
    decType = None
    identifier = None

    decType = matchType()

    identifier = tokenString
    match(TokenType.ID)
    
    # Variable declaration.
    if token == TokenType.SEMICOLON:
        t = newDecNode(DecKind.ScalarDecK)

        if  t != None:
            t.variableDataType = decType
            t.name = identifier

        match(TokenType.SEMICOLON)

    # Array declaration.
    elif token == TokenType.OPEN_SQUARE_BRACKETS:
        t = newDecNode(DecKind.ArrayDecK)

        if  t != None:
            t.variableDataType = decType
            t.name = identifier

        match(TokenType.OPEN_SQUARE_BRACKETS)

        if t != None:
            t.val = tokenString
        
        match(TokenType.NUM)
        match(TokenType.CLOSE_SQUARE_BRACKETS)
        match(TokenType.SEMICOLON)

    #Function declaration.
    elif token == TokenType.OPEN_BRACKETS:
        t = newDecNode(DecKind.FuncDecK)

        if  t != None:
            t.functionReturnType = decType
            t.name = identifier
            
        match(TokenType.OPEN_BRACKETS)

        if t != None:
            t.child[0] = param_list()

        match(TokenType.CLOSE_BRACKETS)

        if t != None:
            t.child[1] = compound_statement()
    
    else:
        syntaxError("Unexpected token")
        '''printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken(imprimeScanner)'''

    return t


def var_declaration():
    global token, tokenString, lineno, imprimeScanner

    t = None
    decType = None
    identifier = None

    decType = matchType()

    identifier = tokenString
    match(TokenType.ID)

    # Variable declaration.
    if token == TokenType.SEMICOLON:
        t = newDecNode(DecKind.ScalarDecK)

        if  t != None:
            t.variableDataType = decType
            t.name = identifier

        match(TokenType.SEMICOLON)

    # Array declaration.
    elif token == TokenType.OPEN_SQUARE_BRACKETS:
        t = newDecNode(DecKind.ArrayDecK)

        if  t != None:
            t.variableDataType = decType
            t.name = identifier

        match(TokenType.OPEN_SQUARE_BRACKETS)

        if t != None:
            t.val = tokenString
        
        match(TokenType.NUM)
        match(TokenType.CLOSE_SQUARE_BRACKETS)
        match(TokenType.SEMICOLON)
    
    else:
        syntaxError("Unexpected token")
        '''printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken(imprimeScanner)'''

    return t


def param():
    global token, tokenString, lineno, imprimeScanner

    t = None
    parmType = None
    identifier = None

    parmType = matchType()

    identifier = tokenString
    match(TokenType.ID)

    if token == TokenType.OPEN_SQUARE_BRACKETS:

        match(TokenType.OPEN_SQUARE_BRACKETS)
        match(TokenType.CLOSE_SQUARE_BRACKETS)

        t = newDecNode(DecKind.ArrayDecK)

    else:
        t = newDecNode(DecKind.ScalarDecK)
    
    if t != None:
        t.name = identifier
        t.val = 0
        t.variableDataType = parmType
        t.isParameter = True

    return t


def param_list():
    global token, tokenString, lineno, imprimeScanner

    t = None
    ptr = None
    newNode = None

    if token == TokenType.VOID:
        match(TokenType.VOID)
        return None
    
    t = param()
    ptr = t

    while (token == TokenType.COMMA):
        
        match(TokenType.COMMA)
        newNode = param()

        if(newNode != None):
            ptr.sibling = newNode
            ptr = newNode

    return t


def compound_statement():

    t = None

    match(TokenType.OPEN_CURLY_BRACKETS)

    

    if (token != TokenType.CLOSE_CURLY_BRACKETS):
        
        t = newStmtNode(StmtKind.CompoundK)

        if(t == None):
            return None

        if is_a_type(token):
            t.child[0] = local_declarations()

        if token != TokenType.CLOSE_CURLY_BRACKETS:
            t.child[1] = statement_list()

    
    match(TokenType.CLOSE_CURLY_BRACKETS)

    return t


def local_declarations():
    
    t = None
    ptr = None
    newNode = None

    if is_a_type(token):
        t = var_declaration()
    
    if t != None:
        ptr = t

        while is_a_type(token):

            newNode = var_declaration()

            if newNode != None:

                ptr.sibling = newNode
                ptr = newNode

    return t


def statement_list():
    
    t = None
    ptr = None
    newNode = None

    if token != TokenType.CLOSE_CURLY_BRACKETS:

        t = statement()
        ptr = t

        while token != TokenType.CLOSE_CURLY_BRACKETS:

            newNode = statement()

            if (ptr != None) and (newNode != None):
                ptr.sibling = newNode
                ptr = newNode
             
    return t


def statement():
    global token, tokenString, lineno, imprimeScanner

    t = None

    if token == TokenType.IF:
        t = selection_statement()

    elif token == TokenType.WHILE:
        t = iteration_statement()

    elif token == TokenType.RETURN:
        t = return_statement()

    elif token == TokenType.OPEN_CURLY_BRACKETS:
        t = compound_statement()

    elif token == TokenType.NUM or token == TokenType.ID\
        or token == TokenType.SEMICOLON or token == TokenType.OPEN_CURLY_BRACKETS:
        
        t = expression_statement()
        
    else:
        syntaxError("Unexpected token")
        '''printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken(imprimeScanner)'''
    
    return t


def expression_statement():

     t = None

     if token == TokenType.SEMICOLON:
         match(TokenType.SEMICOLON)

     elif token != TokenType.CLOSE_CURLY_BRACKETS:
         t = expression()
         match(TokenType.SEMICOLON) 

     return t
    

def selection_statement():

    t = None
    expr = None
    ifStmt = None
    elseStmt = None

    match(TokenType.IF)
    match(TokenType.OPEN_BRACKETS)
    expr = expression()
    match(TokenType.CLOSE_BRACKETS)
    ifStmt = statement()

    if token == TokenType.ELSE:
        match(TokenType.ELSE)
        elseStmt = statement()
    
    t = newStmtNode(StmtKind.IfK)

    if t != None:
        t.child[0] = expr
        t.child[1] = ifStmt
        t.child[2] = elseStmt
    
    return t


def iteration_statement():

    t = None
    expr = None
    stmt = None

    match(TokenType.WHILE)
    match(TokenType.OPEN_BRACKETS)
    expr = expression()
    match(TokenType.CLOSE_BRACKETS)
    stmt = statement()

    t = newStmtNode(StmtKind.WhileK)

    if t != None:
        t.child[0] = expr
        t.child[1] = stmt
    
    return t


def return_statement():

    t = None
    expr = None

    match(TokenType.RETURN)

    t = newStmtNode(StmtKind.ReturnK)

    if token != TokenType.SEMICOLON:
        expr = expression()

    if t != None:
        t.child[0] = expr
    
    match(TokenType.SEMICOLON)

    return t


def expression():
    global token, tokenString, lineno, imprimeScanner

    t = None
    lvalue = None
    rvalue = None
    gotLvalue = False

    if token == TokenType.ID:
        lvalue = ident_statement()
        gotLvalue = True
    
    if gotLvalue == True and token == TokenType.EQUAL:

        if lvalue != None and lvalue.nodekind == NodeKind.ExpK and lvalue.exp == ExpKind.IdK:

            match(TokenType.EQUAL)

            rvalue = expression()

            t = newExpNode(ExpKind.AssignK)

            if t != None:
                t.child[0] = lvalue
                t.child[1] = rvalue
        
        else:
            syntaxError("Unexpected token")
        '''printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken(imprimeScanner)'''
    
    else:
        
        t = simple_expression(lvalue)
    
    return t


def simple_expression(passdown):

    t = None
    lExpr = None
    rExpr = None
    operator = None

    lExpr = additive_expression(passdown)

    if token == TokenType.LESS_EQUAL or token == TokenType.GREATER_EQUAL or token == TokenType.GREATER \
        or token == TokenType.LESS or token == TokenType.EQUALS_TO or token == TokenType.DIFFERENT:

        operator = token
        match(token)
        rExpr = additive_expression(None)

        t = newExpNode(ExpKind.OpK)

        if(t != None):
            t.child[0] = lExpr
            t.child[1] = rExpr
            t.op = operator
        
    else:
        t = lExpr

    return t


def additive_expression(passdown):

    t = None
    newNode = None
    
    t = term(passdown)

    while (token == TokenType.PLUS) or (token == TokenType.MINUS):

        newNode = newExpNode(ExpKind.OpK)

        if newNode != None:
            newNode.child[0] = t
            newNode.op = token
            t = newNode
            match(token)
            t.child[1] = term(None)
        
    return t


def term(passdown):

    t = None
    newNode = None

    t = factor(passdown)

    while (token == TokenType.MULT) or (token == TokenType.DIVISION):

        newNode = newExpNode(ExpKind.OpK)

        if newNode != None:
            newNode.child[0] = t
            newNode.op = token
            t = newNode
            match(token)
            t.child[1] = factor(None)
        
    return t


def factor(passdown):

    global token, tokenString, lineno, imprimeScanner

    t = None

    if passdown != None:
        return passdown
    
    if token == TokenType.ID:
        t = ident_statement()
    
    elif token == TokenType.OPEN_BRACKETS:
        match(TokenType.OPEN_BRACKETS)
        t = expression()
        match(TokenType.CLOSE_BRACKETS)
    
    elif token == TokenType.NUM:
        t = newExpNode(ExpKind.ConstK)

        if t != None:
            t.val = tokenString
            t.variableDataType = ExpType.Integer
        
        match(TokenType.NUM)
    
    else:
        syntaxError("Unexpected token")
        '''printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken(imprimeScanner)'''
    
    return t


def ident_statement():

    global token, tokenString, lineno, imprimeScanner

    t = None
    expr = None
    arguments = None
    identifier = None

    if token == TokenType.ID:
        identifier = tokenString
    match(TokenType.ID)

    if token == TokenType.OPEN_BRACKETS:
        
        match(TokenType.OPEN_BRACKETS)
        arguments = args()
        match(TokenType.CLOSE_BRACKETS)

        t = newStmtNode(StmtKind.CallK)
        
        if t != None:
            t.child[0] = arguments
            t.name = identifier
    else:
    
        if token == TokenType.OPEN_SQUARE_BRACKETS:

            match(TokenType.OPEN_SQUARE_BRACKETS)
            expr = expression(); 
            match(TokenType.CLOSE_SQUARE_BRACKETS)

        t = newExpNode(ExpKind.IdK)

        if t != None:
            t.child[0] = expr
            t.name = identifier

    return t


def args():

    t = None

    if token != TokenType.CLOSE_BRACKETS:
        t = args_list()
    
    return t


def args_list():

    t = None
    ptr = None
    newNode = None

    t = expression()

    ptr = t

    while token == TokenType.COMMA:

        match(TokenType.COMMA)
        newNode = expression()

        if ptr != None and t != None:

            ptr.sibling = newNode
            ptr = newNode
        
    return t


# printSpaces indents by printing spaces */
def printSpaces():
    print(" " * indentno, end = "")


def newStmtNode(kind):
    global lineno

    t = TreeNode()

    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        t.nodekind = NodeKind.StmtK
        t.stmt = kind
        t.lineno = lineno
    return t


def newExpNode(kind):
    global lineno

    t = TreeNode()

    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        t.nodekind = NodeKind.ExpK
        t.exp = kind
        t.lineno = lineno
        if(kind == ExpKind.AssignK):
            t.val = TokenType.EQUAL
    return t


def newDecNode(kind):
    global lineno

    t = TreeNode()

    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        t.nodekind = NodeKind.DecK
        t.dec = kind
        t.lineno = lineno

    return t


indentno = 0
def printTree(tree):

    global indentno
    indentno+=2 # INDENT

    while (tree != None):
        printSpaces()

        if tree.nodekind == NodeKind.DecK:
            
            if tree.dec == DecKind.ScalarDecK:
                print(tree.lineno, "Scalar declaration: ", tree.name, " of type: ", tree.variableDataType.name)

            elif tree.dec == DecKind.ArrayDecK:
                print(tree.lineno, "Array declaration: ", tree.name)
            
            elif tree.dec == DecKind.FuncDecK:
                print(tree.lineno, "Function declaration: ", tree.name)
            
            else:
                print(tree.lineno, "<<<unknown declaration type>>>")
        
        elif tree.nodekind == NodeKind.ExpK:

            if tree.exp == ExpKind.OpK:
                print(tree.lineno, "Operator :", tree.op)
            
            elif tree.exp == ExpKind.IdK:
                if tree.name != None:
                    print(tree.lineno, "Identifier :", tree.name)
                else:
                    print(tree.lineno, "Assignment :", tree.val)
            
            elif tree.exp == ExpKind.ConstK:
                print(tree.lineno, "Literal constant :", tree.val)
            
            elif tree.exp == ExpKind.AssignK:
                print(tree.lineno, "Assignment :", tree.val)
            
            else:
                print(tree.lineno, "<<<unknown expression type>>>")
            
        elif tree.nodekind == NodeKind.StmtK:

            if tree.stmt == StmtKind.CompoundK:
                print(tree.lineno, "Compound Statement")
            
            elif tree.stmt == StmtKind.IfK:
                print(tree.lineno, "If Statement")
            
            elif tree.stmt == StmtKind.WhileK:
                print(tree.lineno, "While Statement")
            
            elif tree.stmt == StmtKind.ReturnK:
                print(tree.lineno, "Return Statement")
            
            elif tree.stmt == StmtKind.CallK:
                print(tree.lineno, "Call to Function Statement")
            
            else:
                print(tree.lineno, "<<<unknown statement type>>>")
        
        else:
            print(tree.lineno, "<<<unknown node type>>>")
        
        for i in range(MAXCHILDREN):
            printTree(tree.child[i])
        tree = tree.sibling
    
    indentno-=2 # UNINDENT


def parse(imprime = True):
    global token, tokenString, lineno

    globales_lexer(programa, posicion, progLong)

    token, tokenString, lineno = getToken(imprimeScanner)
    t = declaration_list()

    status = "Finished"

    if (token != TokenType.ENDFILE):
        syntaxError("Code ends before file\n")
    if imprime:
        printTree(t)

        if Error:
            status = status + " with errors"

        print("\n- AST construction status : "+ status +" -")
    return t, Error


def recibeParser(prog, pos, long):
    recibeScanner(prog, pos, long)

from globalTypes import *
from lexer import *

token = None # holds current token
tokenString = None # holds the token string value 
Error = False
#lineno = 1
SintaxTree = None
imprimeScanner = True

def globales(prog,pos,long):
    global programa
    global posicion
    global progLong
    programa=prog
    posicion=pos
    progLong=long

def syntaxError(message):
    global Error
    print(">>> Syntax error at line " + str(lineno) + ": " + message, end='')
    Error = True

def match(expected):
    global token, tokenString, lineno, imprimeScanner
    if (token == expected):
        token, tokenString, lineno = getToken(imprimeScanner)
        #print("TOKEN:", token, lineno)
    else:
        syntaxError("unexpected token -> ")
        printToken(token,tokenString, imprimeScanner)
        print("      ")

def matchType():
    global token, tokenString, lineno, imprimeScanner

    tokenType = TokenType.VOID

    if token == TokenType.INT:
        tokenType = TokenType.INT
        token, tokenString, lineno = getToken()
    elif token == TokenType.VOID:
        tokenType = TokenType.VOID
        token, tokenString, lineno = getToken()
    else:
        syntaxError("expected a type identifier but got a -> ")
        printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken()

    return tokenType

def is_a_type(tok):
    if tok == TokenType.INT or tok == TokenType.VOID:
        return True
    else:   
        return False

def declaration_list():
    t = None
    p = None

    t = declaration()
    p = t
    
    while token != TokenType.ENDFILE:
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
        syntaxError("unexpected token -> ")
        printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken()

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
        t = newDecNode(DecKind.ScalarDecK)

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
        syntaxError("unexpected token -> ")
        printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken()

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

    while t != None and token == TokenType.COMMA:
        match(TokenType.COMMA)
        newNode = param()
        if(newNode != None):
            ptr.sibling = newNode
            ptr = newNode

    return t


def compound_statement():

    t = None

    match(TokenType.OPEN_CURLY_BRACKETS)

    if token != TokenType.CLOSE_CURLY_BRACKETS:

        t = newStmtNode(StmtKind.CompoundK)

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

    elif token ==TokenType.NUM:
        t = expression_statement()

    elif token == TokenType.ID:
        match(TokenType.ID)

    elif token == TokenType.SEMICOLON:
        match(TokenType.SEMICOLON)

    elif token == TokenType.OPEN_BRACKETS:
        match(TokenType.OPEN_BRACKETS)

    elif token == TokenType.OPEN_SQUARE_BRACKETS:
        match(TokenType.OPEN_SQUARE_BRACKETS)

    elif token == TokenType.CLOSE_SQUARE_BRACKETS:
        match(TokenType.CLOSE_SQUARE_BRACKETS)

    elif token == TokenType.EQUAL:
        match(TokenType.EQUAL)

    elif token == TokenType.PLUS or token == TokenType.MINUS or token == TokenType.MULT or token == TokenType.DIVISION:
        match(token)

    else:
        syntaxError("unexpected token -> ")
        printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken()
    
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

        if lvalue != None and lvalue.nodekind == NodeKind.ExpK and lvalue.kind.exp == ExpKind.IdK:

            match(TokenType.EQUAL)

            rvalue = expression()

            t = newExpNode(ExpKind.AssignK)

            if t != None:
                t.child[0] = lvalue
                t.child[1] = rvalue
        
        else:
            syntaxError("unexpected token -> ")
            printToken(token,tokenString, imprimeScanner)
            token, tokenString, lineno = getToken()
    
    else:
        t = simple_expression(lvalue)
    
    return t


def simple_expression(passdown):

    t = None
    lExpr = None
    rExpr = None
    operator = None

    lExpr = additive_expression(passdown)

    if token == TokenType.LESS_EQUAL or token == TokenType.GREATER_EQUAL or token == TokenType.GREATER or token == TokenType.LESS or token == TokenType.EQUALS_TO or token == TokenType.DIFFERENT:
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
        syntaxError("unexpected token -> ")
        printToken(token,tokenString, imprimeScanner)
        token, tokenString, lineno = getToken()
    
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

# Function newStmtNode creates a new statement
# node for syntax tree construction
def newStmtNode(kind):
    global lineno

    t = TreeNode()

    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        #for i in range(MAXCHILDREN):
        #    t.child[i] = None
        #t.sibling = None
        t.nodekind = NodeKind.StmtK
        t.stmt = kind
        t.lineno = lineno
    return t

# Function newExpNode creates a new expression 
# node for syntax tree construction

def newExpNode(kind):
    global lineno

    t = TreeNode()

    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        #for i in range(MAXCHILDREN):
        #    t.child[i] = None
        #t.sibling = None
        t.nodekind = NodeKind.ExpK
        t.exp = kind
        t.lineno = lineno
        t.type = ExpType.Void
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

# Variable indentno is used by printTree to
# store current number of spaces to indent
indentno = 0

# procedure printTree prints a syntax tree to the 
# listing file using indentation to indicate subtrees

def printTree(tree):

    global indentno, imprime
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
                print(tree.lineno, "Identifier :", tree.name)
                if tree.val != 0:
                    print(tree.lineno, "[", tree.val, "]")
            
            elif tree.exp == ExpKind.ConstK:
                print(tree.lineno, "Literal constant :", tree.val)
            
            elif tree.exp == ExpKind.AssignK:
                print(tree.lineno, "Literal constant :", tree.val)
            
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


# the primary function of the parser
# Function parse returns the newly 
# constructed syntax tree

def parse(imprime = True):
    global token, tokenString, lineno

    globales_lexer(programa, posicion, progLong)

    token, tokenString, lineno = getToken(imprimeScanner)
    t = declaration_list()
    if (token != TokenType.ENDFILE):
        syntaxError("Code ends before file\n")
    if imprime:
        printTree(t)
    return t, Error

def recibeParser(prog, pos, long): # Recibe los globales del main
    recibeScanner(prog, pos, long) # Para mandar los globales

#syntaxTree = parse()
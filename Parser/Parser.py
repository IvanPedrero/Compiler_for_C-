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
    """ 
    This function will be called if an error was encountered to
    set a flag (Error) to abort the AST generation.
    """

    global Error

    if token != TokenType.COMMENT:
        if Error != True:
            Error = True
            detectError(tokenString, message)

    match(token)


def detectError(lookup, message):
    """ 
    This function will detect where an error was encountered and will display 
    the line and the indicator symbol where the error is.
    """

    global lineno, tokenString
    
    indicator = ""

    line = programa.split("\n")[lineno-1]

    errorIndex = line.find(lookup) 

    indicator += (' '*errorIndex) + "^"

    print("\nTraceback (most recent call last):")
    print ("Line ", lineno ,": ", message)
    print(line.replace('$', ''))
    print(indicator,"\n")


def match(expected):
    """ 
    This function will compare the current token with an exxpected sent one.
    """

    global token, tokenString, lineno, imprimeScanner
    
    if (token == expected):
        token, tokenString, lineno = getToken(imprimeScanner)
    else:
        syntaxError("Unexpected token at matching")


def matchType():
    """ 
    This function will decide if the token is a valid identifier (int or void).
    """

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

    return tokenType


def is_a_type(tok):
    """ 
    This function will decide if the token is an identifier.
    """

    if tok == TokenType.INT or tok == TokenType.VOID:
        return True
    else:   
        return False


def declaration_list():
    """
    declaration-list -> declaration { declaration }
    """
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
    """
    declaration -> var-declaration | fun-declaration
    """

    global token, tokenString, lineno, imprimeScanner

    t = None
    decType = None
    identifier = None

    decType = matchType()

    identifier = tokenString
    match(TokenType.ID)

    if token == TokenType.SEMICOLON:                # Variable declaration.
        t = newDecNode(DecKind.ScalarDecK)

        if  t != None:
            t.variableDataType = decType
            t.name = identifier

        match(TokenType.SEMICOLON)

    elif token == TokenType.OPEN_SQUARE_BRACKETS:   # Array declaration.
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

    elif token == TokenType.OPEN_BRACKETS:          #Function declaration.
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

    return t


def var_declaration():
    """
    var-declaration -> type-specifier ID [ “[“ NUM “]” ]
    """

    global token, tokenString, lineno, imprimeScanner

    t = None
    decType = None
    identifier = None

    decType = matchType()

    identifier = tokenString
    match(TokenType.ID)

    if token == TokenType.SEMICOLON:                # Variable declaration.
        t = newDecNode(DecKind.ScalarDecK)

        if  t != None:
            t.variableDataType = decType
            t.name = identifier

        match(TokenType.SEMICOLON)

    elif token == TokenType.OPEN_SQUARE_BRACKETS:   # Array declaration.
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

    return t


def param():
    """
    param -> type-specifier ID [ “[“ “]” ]
    """

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
    """
    param-list -> param { , param }
    """

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
    """
    compound-stmt -> “{“ local-declarations statement-list “}”
    """
    
    t = None

    match(TokenType.OPEN_CURLY_BRACKETS)

    if token == TokenType.COMMENT:
        match(token)

    if (token != TokenType.CLOSE_CURLY_BRACKETS):

        if token == TokenType.COMMENT:              # Make sure to ignore the comments.
            match(token)
            return None

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
    """
    local-declarations -> [  var-declarations ]
    """
    
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
    """
    statement-list -> [ statement-list  ]
    """
    
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
    """
    statement -> expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt
    """

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
    
    return t


def expression_statement():
    """
    expression-stmt -> [ expression ] ;
    """

    t = None

    if token == TokenType.SEMICOLON:
        match(TokenType.SEMICOLON)

    elif token != TokenType.CLOSE_CURLY_BRACKETS:
        t = expression()
        match(TokenType.SEMICOLON) 

    return t
    

def selection_statement():
    """
    selection-stmt -> if ( expression ) statement [ else statement ]
    """

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
    """
    iteration-stmt -> while ( expression ) statement
    """

    global lineno
    t = None
    expr = None
    stmt = None

    tempLineno = lineno

    match(TokenType.WHILE)
    match(TokenType.OPEN_BRACKETS)
    expr = expression()
    match(TokenType.CLOSE_BRACKETS)
    stmt = statement()

    t = newStmtNode(StmtKind.WhileK)
    t.lineno = tempLineno

    if t != None:
        t.child[0] = expr
        t.child[1] = stmt
    
    return t


def return_statement():
    """
    return-stmt  -> return [ expression ] ;
    """

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
    """
    expression -> var = expression | simple-expression
    """

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

    else:
        t = simple_expression(lvalue)
    
    return t


def simple_expression(passdown):
    """
    simple-expression -> additive-expression [ relop additive expression ]
    """

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
    """
    additive-expression -> [ additive-expression addop ] term
    """

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
    """
    term -> [ term mulop ] factor
    """

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
    """
    factor -> ( expression ) | var | call | NUM
    """

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
    """
    args -> [ arg-list ]
    """

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


def printSpaces():
    """
    This function will print the corresponding the spaces to the tree level.
    """

    print(" " * indentno, end = "")


def newStmtNode(kind):
    """
    This function will create a new statement node for the tree.
    """

    global lineno

    if Error:
        return None

    t = TreeNode()

    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        t.nodekind = NodeKind.StmtK
        t.stmt = kind
        t.lineno = lineno
    return t


def newExpNode(kind):
    """
    This function will create a new expression node for the tree.
    """

    global lineno

    if Error:
        return None

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
    """
    This function will create a new declaration node for the tree.
    """

    global lineno

    if Error:
        return None

    t = TreeNode()

    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        t.nodekind = NodeKind.DecK
        t.dec = kind
        t.lineno = lineno

    return t


indentno = 0
def printTree(t):

    global indentno
    indentno+=2 # INDENT

    while (t != None):
        printSpaces()

        if t.nodekind == NodeKind.DecK:
            
            if t.dec == DecKind.ScalarDecK:
                print(t.lineno, "Scalar declaration: ", t.name, " of type: ", t.variableDataType.name)

            elif t.dec == DecKind.ArrayDecK:
                print(t.lineno, "Array declaration: ", t.name)
            
            elif t.dec == DecKind.FuncDecK:
                print(t.lineno, "Function declaration: ", t.name)
            
            else:
                print(t.lineno, "<<<Unknown declaration type>>>")
        
        elif t.nodekind == NodeKind.ExpK:

            if t.exp == ExpKind.OpK:
                print(t.lineno, "Operator :", t.op)
            
            elif t.exp == ExpKind.IdK:
                if t.name != None:
                    print(t.lineno, "Identifier :", t.name)
                else:
                    print(t.lineno, "Assignment :", t.val)
            
            elif t.exp == ExpKind.ConstK:
                print(t.lineno, "Literal constant :", t.val)
            
            elif t.exp == ExpKind.AssignK:
                print(t.lineno, "Assignment :", t.val)
            
            else:
                print(t.lineno, "<<<Unknown expression type>>>")
            
        elif t.nodekind == NodeKind.StmtK:

            if t.stmt == StmtKind.CompoundK:
                print(t.lineno, "Compound Statement")
            
            elif t.stmt == StmtKind.IfK:
                print(t.lineno, "If Statement")
            
            elif t.stmt == StmtKind.WhileK:
                print(t.lineno, "While Statement")
            
            elif t.stmt == StmtKind.ReturnK:
                print(t.lineno, "Return Statement")
            
            elif t.stmt == StmtKind.CallK:
                print(t.lineno, "Call to Function Statement")
            
            else:
                print(t.lineno, "<<<Unknown statement type>>>")
        
        else:
            print(t.lineno, "<<<Unknown node type>>>")
        
        for i in range(MAXCHILDREN):
            printTree(t.child[i])
        t = t.sibling
    
    indentno-=2 # UNINDENT


def parse(imprime = True):
    global token, tokenString, lineno

    globales_lexer(programa, posicion, progLong)

    token, tokenString, lineno = getToken(imprimeScanner)
    t = declaration_list()

    status = ""

    if (token != TokenType.ENDFILE):
        syntaxError("Code ends before file\n")

    if imprime and not Error:
        print("\n Abstract Syntax Tree : \n")
        printTree(t)
        status = "Finished"
    else:
        status = "Cancelled"         

    print("\n- AST construction status : "+ status +" -")
        
    return t, Error


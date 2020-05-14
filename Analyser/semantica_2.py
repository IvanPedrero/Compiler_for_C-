from globalTypes import * 
from Parser import * 
from symtab import *

Error = False
location = 0

location = 0


from globalTypes import *
from symtab import *

Error = False
location = 0

# counter for variable memory locations
location = 0

# Procedure traverse is a generic recursive 
# syntax tree traversal routine:
# it applies preProc in preorder and postProc 
# in postorder to tree pointed to by t

def traverse(t, preProc, postProc):
    if (t != None):
        preProc(t)
        for i in range(MAXCHILDREN):
            traverse(t.child[i],preProc,postProc)
        postProc(t)
        traverse(t.sibling,preProc,postProc)

# nullProc is a do-nothing procedure to generate preorder-only or
# postorder-only traversals from traverse
def nullProc(t):
    None

# Procedure insertNode inserts identifiers stored in t into 
# the symbol table 
def insertNode(t):
    global location
    if t.nodekind == NodeKind.StmtK:
        if t.stmt in [StmtKind.IfK,StmtKind.WhileK,StmtKind.ReturnK,StmtKind.CallK,StmtKind.CompoundK]:
            if (st_lookup(t.name) == -1):
                # not yet in table, so treat as new definition
                st_insert(t.name,t.lineno,location)
                location += 1
            else:
                # already in table, so ignore location, 
                # add line number of use only
                st_insert(t.name,t.lineno,0)
    elif t.nodekind == NodeKind.ExpK:
        if t.exp == ExpKind.IdK:
            if (st_lookup(t.name) == -1):
                # not yet in table, so treat as new definition */
                st_insert(t.name,t.lineno,location)
                location += 1
            else:
                # already in table, so ignore location, 
                # add line number of use only */ 
                st_insert(t.name,t.lineno,0)

# Function buildSymtab constructs the symbol 
# table by preorder traversal of the syntax tree
def buildSymtab(syntaxTree, imprime):
    traverse(syntaxTree, insertNode, nullProc)
    if (imprime):
        print()
        print("Symbol table:")
        printSymTab()

def typeError(t, message):
    print("Type error at line", t.lineno, ":",message)
    Error = True

def checkFormalAgainstActualParams(formal, actual):

    if formal == None or actual == None:
        return False

    firstList = None
    secondList = None

    firstList = formal.child[0]
    secondList = formal.child[0]

    while (firstList != None) and (secondList != None):
        if firstList.expressionType != secondList.expressionType:
            return False
        
        if firstList:
            firstList = firstList.sibling
        if secondList:
            secondList = secondList.sibling
    
    if (((firstList == None) and (secondList != None))
	    or ((firstList != None) and (secondList == None))):
        return False
    
    return True
'''
# Procedure checkNode performs type checking at a single tree node
def checkNode(t):
    if t.nodekind == NodeKind.ExpK:
        if t.exp == ExpKind.OpK:
            if ((t.child[0].type != ExpType.Integer) or (t.child[1].type != ExpType.Integer)):
                typeError(t,"Op applied to non-integer")
            if ((t.op == TokenType.EQUAL) or (t.op == TokenType.LESS)or (t.op == TokenType.GREATER)or (t.op == TokenType.LESS_EQUAL)or (t.op == TokenType.GREATER_EQUAL)):
                t.type = ExpType.Boolean
            else:
                t.type = ExpType.Integer
        elif t.exp in [ExpKind.ConstK, ExpKind.IdK]:
            t.type = ExpType.Integer
        elif t.exp == ExpKind.AssignK:
              if (t.child[0].type != ExpType.Integer):
                typeError(t.child[0],"assignment of non-integer value")
    elif t.nodekind == NodeKind.StmtK:
        if t.stmt == StmtKind.IfK:
            if (t.child[0].type == ExpType.Integer):
                typeError(t.child[0],"if test is not Boolean")

        #
        # 
        # elif t.stmt == StmtKind.AssignK:
            if (t.child[0].type != ExpType.Integer):
                typeError(t.child[0],"assignment of non-integer value")
        elif t.stmt == StmtKind.WriteK:
            if (t.child[0].type != ExpType.Integer):
                typeError(t.child[0],"write of non-integer value")
        elif t.stmt == StmtKind.RepeatK:
            if (t.child[1].type == ExpType.Integer):
                typeError(t.child[1],"repeat test is not Boolean")'''


def checkNode(t):
    
    if t.nodekind == NodeKind.DecK:
        
        if t.dec == DecKind.ScalarDecK:
            t.expressionType = t.variableDataType
        
        elif t.dec == DecKind.ArrayDecK:
            t.expressionType = ExpType.Array
        
        elif t.dec == DecKind.FuncDecK:
            t.expressionType = ExpType.Function
    
    elif t.nodekind == NodeKind.StmtK:

        if t.stmt == StmtKind.IfK:
            if (t.child[0].type != ExpType.Integer):
                typeError(t.child[0],"if test is not Boolean")

        if t.stmt == StmtKind.WhileK:
            if (t.child[0].type != ExpType.Integer):
                typeError(t.child[0],"while test is not Boolean")
        
        if t.stmt == StmtKind.CallK:
            #if not checkFormalAgainstActualParams(t.dec, t):
                #typeError(t, "Formal and actual params don't match")
            
            t.exp = t.functionReturnType

        if t.stmt == StmtKind.ReturnK:
            if (t.functionReturnType == ExpType.Integer):
                if ((t.child[0] == None) or (t.child[0].exp != ExpType.Integer)):
                    typeError(t.child[0], "RETURN-expression is either missing or not integer") 
            elif (t.functionReturnType == ExpType.Void):

                    if (t.child[0] != None):
                        typeError(t.child[0], "RETURN-expression must be void")
        
        if t.stmt == StmtKind.CompoundK:
            t.exp = ExpType.Void
        
    elif t.nodekind == NodeKind.ExpK:

        if t.exp == ExpKind.OpK:

            # Arithmetic operator.
            if t.op == TokenType.PLUS or t.op == TokenType.MINUS or t.op == TokenType.MULT or t.op ==  TokenType.DIVISION:
                
                if ((t.child[0].type == ExpType.Integer) or (t.child[1].type == ExpType.Integer)):
                    t.type = ExpType.Integer
                else:
                    typeError(t,"Op applied to non-integer")

            elif  t.op == TokenType.EQUAL or t.op == TokenType.LESS or t.op == TokenType.GREATER or t.op == TokenType.LESS_EQUAL or t.op == TokenType.GREATER_EQUAL:
                
                if ((t.child[0].type == ExpType.Integer) or (t.child[1].type == ExpType.Integer)):
                    t.type = ExpType.Integer
                else:
                    typeError(t,"Relational operators applied to non-integer")
            
            else:
                typeError(t, "Error in type checker, unknown operator")

        elif t.exp in [ExpKind.ConstK, ExpKind.IdK]:
            t.type = ExpType.Integer
        
        elif t.exp == ExpKind.AssignK:
            if ((t.child[0].type == ExpType.Integer) or (t.child[1].type == ExpType.Integer)):
                t.type = ExpType.Integer
            else:
                typeError(t, "Both assigning and assigned expression")





# Procedure typeCheck performs type checking 
# by a postorder syntax tree traversal
def typeCheck(syntaxTree):
    traverse(syntaxTree,nullProc,checkNode)


def semantica(tree, imprime = True):
    print("Building symbol table...")
    buildSymtab(tree, True)
    print("Performing type checking...")
    typeCheck(tree)

def tabla(tree, imprime = True):
    if not imprime:
        return
    else: 
        pass
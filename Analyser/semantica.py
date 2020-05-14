from globalTypes import *
from Parser import *

location = 0

Error = False

originalTree = None

# the stack for hash tables
stack = [0]

scope = 0

# the hash table
hashtable = {
    0:{
        'main':[0, ExpType.Void,0,0],
        'input':[0,ExpType.Integer,0,0],
        'output':[1,ExpType.Void,0,0]
    }
}
    

# Procedure st_insert inserts line numbers and
# memory locations into the symbol table
# loc = memory location is inserted only the
# first time, otherwise ignored
def st_insert(name, tipo, lineno, scope, newScope=-1):
    global location
    try: 
        int(name)
        return
    except ValueError:
        if name in hashtable[scope]:
            if hashtable[scope][name][-1] != lineno:
                hashtable[scope][name].append(lineno)
        else:
            location += 1
            hashtable[scope][name] = [location,tipo,newScope,lineno]


# Function st_lookup returns the memory 
# location of a variable or -1 if not found
def st_lookup(name):
    for x in range(1,len(stack)+1):
        if name in hashtable[stack[(-x)]]:
            return stack[-x]
    return stack[-1]   


def build_table(tree):
    global scope
    scopesCreated = 0
    while tree != None:
        shouldCheck = True
        if(tree.nodekind == NodeKind.DecK):
            if(tree.dec == DecKind.ScalarDecK):
                if tree.variableDataType == TokenType.INT:
                    st_insert(tree.name,ExpType.Integer,tree.lineno,scope)
                elif tree.variableDataType == TokenType.VOID:
                    typeError(tree, "Error no se pueden declarar variables de tipo void")
                shouldCheck = False
            elif(tree.dec == DecKind.ArrayDecK):
                if tree.variableDataType == TokenType.INT:
                    st_insert(tree.name, ExpType.Integer,tree.lineno,scope)
                elif tree.variableDataType == TokenType.VOID:
                    typeError(tree, "Error no se pueden declarar arreglos de tipo void")
                shouldCheck = False

            elif(tree.dec == DecKind.FuncDecK):
                if(stack[-1]!=0):
                    stack.pop()

                aux_tree = tree.child[0]
                numberOfParams = 0
                while(aux_tree != None and aux_tree.stmt != StmtKind.CompoundK):
                    numberOfParams += 1
                    aux_tree = aux_tree.sibling
                
                if tree.child[0] != None:

                    returnType = ExpType.Void

                    if tree.functionReturnType == TokenType.INT:
                        returnType = ExpType.Integer
                    elif tree.functionReturnType == TokenType.VOID:
                        returnType = ExpType.Void

                    st_insert(tree.name, returnType, tree.lineno,stack[0],scope+1)

                    scope+=1
                    scopesCreated += 1
                    # print("Scope number: ", scope, " created")
                    # print("Number of scopes created in this scope: ", scopesCreated)
                    stack.append(scope)
                    hashtable[scope] = {}
                    # print("Es de funcion")
            
        elif(tree.nodekind == NodeKind.ExpK):
            if(tree.exp == ExpKind.IdK):
                if tree.name != None:
                    st_insert(tree.name,None,tree.lineno,st_lookup(tree.name))
                    if hashtable[st_lookup(tree.name)][tree.name][0] == "":
                        typeError(tree, "Use of a variable not defined")
            if(tree.exp == ExpKind.AssignK):
                if tree.child[0] != None:
                    if tree.child[0].name == None:
                        st_insert(tree.child[1].name,None,tree.lineno,st_lookup(tree.child[1].name))
                        st_insert(tree.child[2].name,None,tree.lineno,st_lookup(tree.child[2].name))
                    else:
                        st_insert(tree.child[0].name,None,tree.lineno,st_lookup(tree.child[0].name))
                    
                    shouldCheck = False
        elif(tree.nodekind == NodeKind.StmtK):
            if(tree.stmt == StmtKind.IfK or tree.stmt == StmtKind.WhileK):
                scope+=1
                scopesCreated += 1
                # print("Scope number: ", scope, " created")
                # print("Number of scopes created in this scope: ", scopesCreated)
                stack.append(scope)
                hashtable[scope] = {}
                # print("Es de stmt")
        if shouldCheck:
            for child in tree.child:
                build_table(child)
        
        tree = tree.sibling
    for x in range(scopesCreated):
        # print("Scope number: ", stack[-1], " popped out")
        if(stack[-1]!=0):
            stack.pop()

def printSymTab():
    print("\n Symbol Table : \n")
    print("Variable Name    Location    Scope   Type")
    print("-------------    --------    -----   ---------")
    for scope in hashtable:
        #print("Scope number: ",scope)
        for name in hashtable[scope]:
            if hashtable[scope][name][1] != None:
                loc = hashtable[scope][name][3]
                scp = hashtable[scope][name][1]
                print(name, " "*(17-len(name)),loc, " "*(10-len(str(loc))) , scope, " "*(5-len(str(scope))), scp.name)
            #for i in range(len(hashtable[scope][name])):
                #print("info in symtable: ",hashtable[scope][name][i]) # hashtable[scope][name][5] -> Lineno


def buscarScope(name, lineno):
    found = []
    for scope in hashtable:
        if name in hashtable[scope]:
            #found.append(scope)
            pass
    for i in found:
        for j in range(MAXCHILDREN, len(hashtable[i][name])):
            if lineno == hashtable[i][name][j]:
                return hashtable[i][name][2]
            
    return False

def typeError(t, message):
    global Error
    Error = True
    print("Type error at line", t.lineno, ":",message)
    

def typeCheck(syntaxTree):
    traverse(syntaxTree, nullProc, checkNode)

def traverse(t, preProc, postProc):
    if (t != None):
        preProc(t)
        for i in range(MAXCHILDREN):
            traverse(t.child[i],preProc,postProc)
        postProc(t)
        traverse(t.sibling,preProc,postProc)

def nullProc(t):
    None

def checkNode(t):
    
    errorMessage = ""

    if t.nodekind == NodeKind.DecK:
            
        if t.dec == DecKind.ScalarDecK:
            t.expressionType = ExpType.Integer

        elif t.dec == DecKind.ArrayDecK:
            t.expressionType = ExpType.Array
        
        elif t.dec == DecKind.FuncDecK:
            t.expressionType = ExpType.Function
        
        else:
            typeError(t, "<<<Unknown declaration type>>>")
    
    elif t.nodekind == NodeKind.StmtK:

        if t.stmt == StmtKind.IfK:
            
            if t.child[0].expressionType != ExpType.Integer:
                typeError(t, "IF-expression must be integer!!!")
        
        elif t.stmt == StmtKind.WhileK:
            
            if t.child[0].expressionType != ExpType.Integer:
                typeError(t, "WHILE-expression must be integer!!!")
        
        elif t.stmt == StmtKind.CallK:
            # Line 387
            funcType = getFunctionReturnType(t.name)
            t.expressionType = funcType
        
        elif t.stmt == StmtKind.ReturnK:
            
            if t.functionReturnType == ExpType.Integer:

                if t.child[0] == None or t.child[0].expressionType != ExpType.Integer:
                    typeError(t, "RETURN-expression is either missing or not integer")
            
            elif t.functionReturnType == ExpType.Void:

                if t.child[0] != None:
                    typeError(t, "RETURN-expression must be void")

        elif t.stmt == StmtKind.CompoundK:

            t.expressionType = ExpType.Void
        
        else:
            typeError(t, "<<<Unknown statement type>>>")

    elif t.nodekind == NodeKind.ExpK:
        
        if t.exp == ExpKind.OpK:
            
            if t.op == TokenType.PLUS or t.op == TokenType.MINUS or t.op == TokenType.MULT or t.op == TokenType.DIVISION:

                if (t.child[0].expressionType == ExpType.Integer or t.child[0].expressionType == ExpType.Array) and \
                    (t.child[1].expressionType == ExpType.Integer or t.child[1].expressionType == ExpType.Array):
                    t.expressionType = ExpType.Integer
                else:
                    typeError(t, "Arithmetic operators mus be integer")
            
            elif t.op == TokenType.GREATER or t.op == TokenType.LESS or t.op == TokenType.LESS_EQUAL or t.op == TokenType.GREATER_EQUAL or TokenType.EQUALS_TO or TokenType.DIFFERENT:
                
                if (t.child[0].expressionType == ExpType.Integer or t.child[0].expressionType == ExpType.Array) and \
                    (t.child[1].expressionType == ExpType.Integer or t.child[1].expressionType == ExpType.Array):
                    t.expressionType = ExpType.Integer
                else:
                    typeError(t, "Relational operators must have integer operands")
                
            else:
                typeError(t, "ERROR in type checker, unknown operator")
        
        elif t.exp == ExpKind.IdK:

            if t.name == None:
                return

            if t.expressionType == ExpType.Integer:

                if t.child[0] == None:
                    t.expressionType = ExpType.Integer
                else:
                    typeError(t, "Cant access elements in anything else than an integer as index")
            
            elif t.expressionType == ExpType.Array:

                if t.child[0] == None:
                    t.expressionType = ExpType.Array
                elif t.child[0].expressionType == ExpType.Integer:
                    t.expressionType = ExpType.Array
                else:
                    typeError(t, "Array must be indexed by an scalar")
            
            else:

                typeError(t, "Identifier is an illegal type.")
        
        elif t.exp == ExpKind.ConstK:
            
            t.expressionType = ExpType.Integer
        
        elif t.exp == ExpKind.AssignK:
            
            if t.child[0].expressionType == ExpType.Integer and t.child[1].expressionType == ExpType.Integer:
                    t.expressionType = ExpType.Integer
            else:
                typeError(t, "Assigning and assigned expressions must be integer")
        
        else:
            typeError(t, "Unknown expression type")


def getFunctionReturnType(name):
    global originalTree

    t = originalTree
    while (originalTree != None):
        if originalTree.nodekind == NodeKind.DecK:
            if originalTree.dec == DecKind.FuncDecK:
                if name == originalTree.name:
                    return t.functionReturnType

        originalTree = originalTree.sibling
    originalTree = t
        



def semantica(tree, imprime = True):
    global originalTree
    global Error

    originalTree = tree

    build_table(tree)
    typeCheck(tree)

    if(imprime):
        if Error == True:
            print("Status aborted!")
        else:
            printSymTab()
   # checkNode(tree)
    
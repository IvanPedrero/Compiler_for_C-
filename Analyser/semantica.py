from globalTypes import *
from Parser import *

location = 0

# the stack for hash tables
stack = [0]

# the hash table

SymTableDictionary = {0:{'input':[0,'int',False,0,0,0],'output':[1,'void',False,1,0,0]}}

# Procedure st_insert inserts line numbers and
# memory locations into the symbol table
# loc = memory location is inserted only the
# first time, otherwise ignored
location = 0
def st_insert(name, tipo, arrType, arrSize, lineno, scope, funcScope=-1):
    global location
    try: 
        int(name)
        return
    except ValueError:
        if name in SymTableDictionary[scope]:
            if SymTableDictionary[scope][name][-1] != lineno:
                SymTableDictionary[scope][name].append(lineno)
        else:
            location += 1
            SymTableDictionary[scope][name] = [location,tipo,arrType,arrSize, funcScope,lineno]
        # print("Scope: ",scope)
        # print(SymTableDictionary[scope])


# Function st_lookup returns the memory 
# location of a variable or -1 if not found
def st_lookup(name):
    for x in range(1,len(stack)+1):
        if name in SymTableDictionary[stack[(-x)]]:
            return stack[-x]
    return stack[-1]   

scope = 0

def build_table(tree):
    global scope
    scopesCreated = 0
    while tree != None:
        shouldCheck = True
        if(tree.nodekind == NodeKind.DecK):
            if(tree.dec == DecKind.ScalarDecK):
                if tree.variableDataType == TokenType.INT:
                    st_insert(tree.name,TokenType.INT,False,-1,tree.lineno,scope)
                elif tree.variableDataType == TokenType.VOID:
                    print("Error no se pueden declarar variables de tipo void ",tree.lineno)
                shouldCheck = False
            elif(tree.dec == DecKind.ArrayDecK):
                if tree.variableDataType == TokenType.INT:

                    st_insert(tree.name,tree.variableDataType.name,False,-1,tree.lineno,scope)

                    '''if tree.child[1] != None:
                        st_insert(tree.child[0].str,tree.str,True,tree.child[1].val,tree.lineno,scope)
                    else:
                        st_insert(tree.val,tree.variableDataType.name,True,"void",tree.lineno,scope)'''
                elif tree.str ==  'void':
                    print("Error no se pueden declarar arreglos de tipo void ",tree.lineno)
                shouldCheck = False

            elif(tree.dec == DecKind.FuncDecK):
                if(stack[-1]!=0):
                    # print("Scope number: ", stack[-1], " popped out")
                    stack.pop()

                aux_tree = tree.child[0]
                numberOfParams = 0
                while(aux_tree != None and aux_tree.stmt != StmtKind.CompoundK):
                    numberOfParams += 1
                    aux_tree = aux_tree.sibling
                
                if tree.child[0] != None:

                    st_insert(tree.child[0].name, tree.functionReturnType.name, False,numberOfParams,tree.lineno,stack[0],scope+1)

                    scope+=1
                    scopesCreated += 1
                    # print("Scope number: ", scope, " created")
                    # print("Number of scopes created in this scope: ", scopesCreated)
                    stack.append(scope)
                    SymTableDictionary[scope] = {}
                    # print("Es de funcion")
            
        elif(tree.nodekind == NodeKind.ExpK):
            if(tree.exp == ExpKind.IdK):
                if tree.name != None:
                    st_insert(tree.name,"",False,-1,tree.lineno,st_lookup(tree.name))
                    if SymTableDictionary[st_lookup(tree.name)][tree.name][0] == "":
                        print("Variable not defined in line: ",tree.lineno)
            if(tree.exp == ExpKind.AssignK):
                if tree.child[0] != None:
                    if tree.child[0].name == None:
                        st_insert(tree.child[1].name,"",True,-1,tree.lineno,st_lookup(tree.child[1].name))
                        st_insert(tree.child[2].name,"",True,-1,tree.lineno,st_lookup(tree.child[2].name))
                    else:
                        st_insert(tree.child[0].name,"",True,-1,tree.lineno,st_lookup(tree.child[0].name))
                    
                    shouldCheck = False
        elif(tree.nodekind == NodeKind.StmtK):
            if(tree.stmt == StmtKind.IfK or tree.stmt == StmtKind.WhileK):
                scope+=1
                scopesCreated += 1
                # print("Scope number: ", scope, " created")
                # print("Number of scopes created in this scope: ", scopesCreated)
                stack.append(scope)
                SymTableDictionary[scope] = {}
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
    print("Variable Name    Location    Scope")
    print("-------------    --------    -----")
    for scope in SymTableDictionary:
        #print("Scope number: ",scope)
        for name in SymTableDictionary[scope]:
            print(name, " "*(17-len(name)), SymTableDictionary[scope][name][5], " "*(10-len(str(SymTableDictionary[scope][name][5]))) , scope)
            #for i in range(len(SymTableDictionary[scope][name])):
                #print("info in symtable: ",SymTableDictionary[scope][name][i]) # SymTableDictionary[scope][name][5] -> Lineno


def buscarScope(name, lineno):
    found = []
    for scope in SymTableDictionary:
        if name in SymTableDictionary[scope]:
            #found.append(scope)
            pass
    for i in found:
        for j in range(3,len(SymTableDictionary[i][name])):
            if lineno == SymTableDictionary[i][name][j]:
                return SymTableDictionary[i][name][2]
            
    return False

def typeError(t, message):
    print("Type error at line", t.lineno, ":",message)
    Error = True

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
            print(t.lineno, "<<<Unknown declaration type>>>")
    
    elif t.nodekind == NodeKind.StmtK:

        if t.stmt == StmtKind.IfK:
            
            if t.child[0].expressionType != ExpType.Integer:
                print(t.lineno, "IF-expression must be integer!!!")
        
        elif t.stmt == StmtKind.WhileK:
            
            if t.child[0].expressionType != ExpType.Integer:
                print(t.lineno, "WHILE-expression must be integer!!!")
        
        elif t.stmt == StmtKind.CallK:
            # Line 387
            funcType = getFunctionReturnType(t.name)
            t.expressionType = funcType
        
        elif t.stmt == StmtKind.ReturnK:
            
            if t.functionReturnType == ExpType.Integer:

                if t.child[0] == None or t.child[0].expressionType != ExpType.Integer:
                    print(t.lineno, "RETURN-expression is either missing or not integer")
            
            elif t.functionReturnType == ExpType.Void:

                if t.child[0] != None:
                    print(t.lineno, "RETURN-expression must be void")

        elif t.stmt == StmtKind.CompoundK:

            t.expressionType = ExpType.Void
        
        else:
            print(t.lineno, "<<<Unknown statement type>>>")

    elif t.nodekind == NodeKind.ExpK:
        
        if t.exp == ExpKind.OpK:
            
            if t.op == TokenType.PLUS or t.op == TokenType.MINUS or t.op == TokenType.MULT or t.op == TokenType.DIVISION:

                if (t.child[0].expressionType == ExpType.Integer or t.child[0].expressionType == ExpType.Array) and \
                    (t.child[1].expressionType == ExpType.Integer or t.child[1].expressionType == ExpType.Array):
                    t.expressionType = ExpType.Integer
                else:
                    print("Arithmetic operators mus be integer")
            
            elif t.op == TokenType.GREATER or t.op == TokenType.LESS or t.op == TokenType.LESS_EQUAL or t.op == TokenType.GREATER_EQUAL or TokenType.EQUALS_TO or TokenType.DIFFERENT:
                
                if (t.child[0].expressionType == ExpType.Integer or t.child[0].expressionType == ExpType.Array) and \
                    (t.child[1].expressionType == ExpType.Integer or t.child[1].expressionType == ExpType.Array):
                    t.expressionType = ExpType.Integer
                else:
                    print("Relational operators must have integer operands")
                
            else:
                print("ERROR in type checker, unknown operator")
        
        elif t.exp == ExpKind.IdK:

            if t.name == None:
                return

            if t.expressionType == ExpType.Integer:

                if t.child[0] == None:
                    t.expressionType = ExpType.Integer
                else:
                    print("ERROR, cant access elements in anything else than an integer as index")
            
            elif t.expressionType == ExpType.Array:

                if t.child[0] == None:
                    t.expressionType = ExpType.Array
                elif t.child[0].expressionType == ExpType.Integer:
                    t.expressionType = ExpType.Array
                else:
                    print("ERROR!!!! array must be indexed by an scalar")
            
            else:

                print("ERROR, Identifier is an illegal type.")
        
        elif t.exp == ExpKind.ConstK:
            
            t.expressionType = ExpType.Integer
        
        elif t.exp == ExpKind.AssignK:
            
            if t.child[0].expressionType == ExpType.Integer and t.child[1].expressionType == ExpType.Integer:
                    t.expressionType = ExpType.Integer
            else:
                print("Assigning and assigned expressions must be integer")
        
        else:
            print(t.lineno, "<<<Unknown expression type>>>")


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
        

'''def checkNode(tree):
    if tree != None:
        for child in tree.child:
            checkNode(child)
        checkNode(tree.sibling)
        if tree.nodekind == NodeKind.ExpK:
            if tree.exp == ExpKind.OpK or tree.exp == ExpKind.AssignK:
                if tree.child[0] != None and tree.child[1] != None:

                    if ((tree.child[0].variableDataType not in [ExpType.Integer, ExpType.Array]) or (tree.tree.child[1].variableDataType not in [ExpType.Integer, ExpType.Array])):
                        print("Op applied to non-integer ",tree.lineno, " str: ", tree.name)
                    if (tree.op in [TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.GREATER, TokenType.EQUALS_TO, TokenType.DIFFERENT]):
                        tree.variableDataType = ExpType.Boolean
                    else:
                        tree.variableDataType = ExpType.Integer
            elif tree.exp in [ExpKind.IdK, ExpKind.ConstK]:
                tree.variableDataType = ExpType.Integer

            elif tree.dec == DecKind.ArrayDecK:
                if tree.sibling.variableDataType != ExpType.Integer:
                    print("Esto es void!!! u otra cosa xd", tree.lineno)
                else:
                    tree.type = ExpType.Array
        if tree.nodekind == NodeKind.StmtK:
            if tree.stmt == StmtKind.IfK or tree.stmt == StmtKind.WhileK:
                if(tree.child[0].variableDataType != ExpType.Boolean):
                    print("Boolean expresion expected ",tree.lineno)
            elif tree.stmt == StmtKind.CallK:
                funcScope = SymTableDictionary[0][tree.child[0].name][4]
                paramNum = SymTableDictionary[0][tree.child[0].name][3]
                actualParam = 0
                aux_tree = tree.child[1]
                if(aux_tree != None and paramNum>0):
                    for name in SymTableDictionary[funcScope]:
                        bandera = False
                        if aux_tree.variableDataType == ExpType.Array and aux_tree.child[0] != None:
                            aux_tree.variableDataType = ExpType.Integer
                            bandera = True
                        if SymTableDictionary[funcScope][name][2] == True:
                            if not buscarScope(aux_tree.str,aux_tree.lineno):
                                print("Se esperaba un arreglo como parametro",aux_tree.lineno)
                        elif buscarScope(aux_tree.str,aux_tree.lineno):
                            print("Se esperaba una variable de tipo int como parametro",aux_tree.lineno)
                        elif aux_tree.variableDataType != ExpType.Integer:
                            print("Se esperaba una variable de tipo int como parametro",aux_tree.lineno)
                        actualParam+=1
                        
                        if bandera:
                            aux_tree = aux_tree.sibling.sibling
                        else: 
                            aux_tree = aux_tree.sibling
                        
                        if aux_tree==None or actualParam == paramNum:
                            break
                    if actualParam < paramNum or aux_tree != None:
                        print("Error, el numero de parametros no coincide", tree.lineno)
                elif aux_tree == None and paramNum>0:
                    print("Se esperaba un parametro",tree.lineno)
                elif aux_tree != None and paramNum<=0:
                    print("No se esperaba un parametro",aux_tree.lineno)
                
                if SymTableDictionary[0][tree.child[0].name][1] == "int":
                    tree.variableDataType = ExpType.Integer
                    tree.child[0].variableDataType = ExpType.Integer
                else:
                    tree.type = ExpType.Void
                    tree.child[0].type = ExpType.Void
            elif tree.stmt == StmtKind.ReturnK:
                if tree.child[0] != None:
                    if tree.child[0].variableDataType != ExpType.Integer:
                        print("Return no regresa una variable de tipo entero")
        #checkNode(tree.sibling)
'''

originalTree = None

def semantica(tree, imprime = True):
    global originalTree
    originalTree = tree

    build_table(tree)
    if(imprime):
        printSymTab()
   # checkNode(tree)
    typeCheck(tree)
from globalTypes import *
from Parser import *
from symtab import *

Error = False

originalTree = None

programa = None

def buildSymtab(t):
    global scope

    newScope = 0

    while t != None:

        isNodeParent = True

        if(t.nodekind == NodeKind.DecK):

            if(t.dec == DecKind.FuncDecK):

                if(stackArray[-1] != 0):
                    stackArray.pop()

                currentChild = t.child[0]

                numberOfParams = 0

                while(currentChild != None and currentChild.stmt != StmtKind.CompoundK):

                    numberOfParams += 1

                    currentChild = currentChild.sibling

                if t.child[0] != None:

                    returnType = ExpType.Void

                    if t.functionReturnType == TokenType.INT:
                        returnType = ExpType.Integer
                    elif t.functionReturnType == TokenType.VOID:
                        returnType = ExpType.Void

                    st_insert(t.name, returnType,
                              t.lineno, stackArray[0], scope+1)

                    scope = scope + 1
                    newScope = newScope + 1

                    stackArray.append(scope)
                    BucketList[scope] = {}

            elif(t.dec == DecKind.ScalarDecK):

                if t.variableDataType == TokenType.INT:

                    st_insert(t.name, ExpType.Integer, t.lineno, scope)

                elif t.variableDataType == TokenType.VOID:

                    typeError(
                        t, "Variable can't be of type void")

                isNodeParent = False

            elif(t.dec == DecKind.ArrayDecK):

                if t.variableDataType == TokenType.INT:

                    st_insert(t.name, ExpType.Integer, t.lineno, scope)

                elif t.variableDataType == TokenType.VOID:

                    typeError(
                        t, "Array can't be of type void")

                isNodeParent = False

        elif(t.nodekind == NodeKind.ExpK):

            if(t.exp == ExpKind.IdK):

                if t.name != None:

                    st_insert(t.name, None, t.lineno,
                              st_lookup(t.name))

                    if BucketList[st_lookup(t.name)][t.name][0] == "":

                        typeError(
                            t, "Use of a variable not defined previously")

            if(t.exp == ExpKind.AssignK):

                if t.child[0] != None:

                    if t.child[0].name == None:

                        st_insert(t.child[1].name, None, t.lineno, st_lookup(
                            t.child[1].name))

                        st_insert(t.child[2].name, None, t.lineno, st_lookup(
                            t.child[2].name))

                    else:

                        st_insert(t.child[0].name, None, t.lineno, st_lookup(
                            t.child[0].name))

                    isNodeParent = False

        elif(t.nodekind == NodeKind.StmtK):

            if(t.stmt == StmtKind.IfK or t.stmt == StmtKind.WhileK):

                scope = scope + 1
                newScope = newScope + 1

                stackArray.append(scope)
                BucketList[scope] = {}

        if isNodeParent:

            for child in t.child:
                buildSymtab(child)

        t = t.sibling

    for x in range(newScope):

        if(stackArray[-1] != 0):
            stackArray.pop()


def typeError(t, message):
    global Error
    Error = True
    detectError(t, t.lineno, message)


def detectError(t, lineno, message):

    import Parser

    indicator = ""

    lookup = ""

    line = Parser.programa.split("\n")[lineno-1]

    if t.name != None:
        lookup = t.name
        errorIndex = line.find(lookup) 
        indicator += (' '*errorIndex) + "^"

    else:
        lookup = line
        errorIndex = line.find(lookup) 
        indicator = ""

    print("\n\nTraceback (most recent call last):")
    print ("Line ", lineno ,": ", message)
    print(line.replace('$', ''))
    print(indicator,"\n")


def typeCheck(syntaxTree):
    traverse(syntaxTree, nullProc, checkNode)


def traverse(t, preProc, postProc):
    if (t != None):
        preProc(t)
        for i in range(MAXCHILDREN):
            traverse(t.child[i], preProc, postProc)
        postProc(t)
        traverse(t.sibling, preProc, postProc)


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
            typeError(t, "Unknown declaration type")

    elif t.nodekind == NodeKind.StmtK:

        if t.stmt == StmtKind.IfK:

            if t.child[0].expressionType != ExpType.Integer:
                typeError(t, "If expression not an integer")

        elif t.stmt == StmtKind.WhileK:

            if t.child[0].expressionType != ExpType.Integer:
                typeError(t, "While expression not an integer")

        elif t.stmt == StmtKind.CallK:

            funcType = getFunctionReturnType(t.name)
            t.expressionType = funcType

        elif t.stmt == StmtKind.ReturnK:

            if t.functionReturnType == ExpType.Integer:

                if t.child[0] == None or t.child[0].expressionType != ExpType.Integer:
                    typeError(
                        t, "Return expression not integer or missing")

            elif t.functionReturnType == ExpType.Void:

                if t.child[0] != None:
                    typeError(t, "Return expression must be void")

        elif t.stmt == StmtKind.CompoundK:

            t.expressionType = ExpType.Void

        else:
            typeError(t, "Unknown statement type")

    elif t.nodekind == NodeKind.ExpK:

        if t.exp == ExpKind.OpK:

            if t.op == TokenType.PLUS or t.op == TokenType.MINUS or t.op == TokenType.MULT or t.op == TokenType.DIVISION:

                if (t.child[0].expressionType == ExpType.Integer or t.child[0].expressionType == ExpType.Array) and \
                        (t.child[1].expressionType == ExpType.Integer or t.child[1].expressionType == ExpType.Array):
                    t.expressionType = ExpType.Integer
                else:
                    typeError(t, "Arithmetic operators must be integer")

            elif t.op == TokenType.GREATER or t.op == TokenType.LESS or t.op == TokenType.LESS_EQUAL or t.op == TokenType.GREATER_EQUAL or TokenType.EQUALS_TO or TokenType.DIFFERENT:

                if (t.child[0].expressionType == ExpType.Integer or t.child[0].expressionType == ExpType.Array) and \
                        (t.child[1].expressionType == ExpType.Integer or t.child[1].expressionType == ExpType.Array):
                    t.expressionType = ExpType.Integer
                else:
                    typeError(
                        t, "Relational operators must have integer operands")

            else:
                typeError(t, "Unknown operator")

        elif t.exp == ExpKind.IdK:

            if t.name == None:
                return

            if t.expressionType == ExpType.Integer:

                if t.child[0] == None:
                    t.expressionType = ExpType.Integer
                else:
                    typeError(
                        t, "Can't access elements in anything else than an integer as index")

            elif t.expressionType == ExpType.Array:

                if t.child[0] == None:
                    t.expressionType = ExpType.Array
                elif t.child[0].expressionType == ExpType.Integer:
                    t.expressionType = ExpType.Array
                else:
                    typeError(t, "Array must have an integer as index")

            else:

                typeError(t, "Identifier is an illegal type")

        elif t.exp == ExpKind.ConstK:

            t.expressionType = ExpType.Integer

        elif t.exp == ExpKind.AssignK:

            if t.child[0].expressionType == ExpType.Integer and t.child[1].expressionType == ExpType.Integer:
                t.expressionType = ExpType.Integer
            else:
                typeError(
                    t, "Assigning and assigned expressions must be integers")

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


def semantica(t, imprime=True):
    global programa
    global originalTree
    global Error

    originalTree = t

    status = ""

    buildSymtab(t)

    typeCheck(t)

    if not Error:
        status = "Finished"

        if imprime:
            print("\n Symbol Table : \n")
            printSymTab()
    else:
        status = "Finished with errors"         

    print("\n- Symbol table construction status : "+ status +" -")
            

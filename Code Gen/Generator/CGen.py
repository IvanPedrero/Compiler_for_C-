from globalTypes import *
from semantica import *

Error = False

WORDSIZE = 4

STACKMARKSIZE = 8

output = ""

genComments = False

originalTree = None


def codeGen(syntaxTree, fileName):
    global originalTree

    originalTree = syntaxTree

    output = open(fileName, "w")

    if output == None:
        Error = True
        print("Unable to open the file for writing")
    else:
        '''
        There are three attributes that need to be synthesised before
        code generation can begin.  They're the locals-on-the-stack
        size, and the "assembly-area" size (assembly area is where
        parameters for function calls are set up before execution), as
        well as AP/LP stack-offsets for locals/parameters.
        '''
        calcAsmAttribute(syntaxTree)
        calcSizeAttribute(syntaxTree)
        calcStackOffsets(syntaxTree)

        genProgram(syntaxTree, output, "output")


def calcAsmAttribute(tree):
    i = 0
    asmArea = 0
    asmInThisFunc = 0

    parmPtr = None

    while(tree != None):

        if tree.nodekind == NodeKind.DecK and tree.dec == DecKind.FuncDecK:
            asmArea = 0

        for i in range(MAXCHILDREN):
            calcAsmAttribute(tree.child[i])

        if tree.nodekind == NodeKind.StmtK and tree.stmt == StmtKind.CallK:

            asmInThisFunc = 0

            parmPtr = tree.child[0]

            while parmPtr != None:

                asmInThisFunc = asmInThisFunc + WORDSIZE

                parmPtr = parmPtr.sibling

            if asmInThisFunc > asmArea:
                asmArea = asmInThisFunc

        if tree.nodekind == NodeKind.DecK and tree.dec == DecKind.FuncDecK:

            if genComments:
                print("*** Calculated assemblySize attribute for ",
                    tree.name + " as ", asmArea, "\n")

            tree.assemblyAreaSize = asmArea

        tree = tree.sibling


def calcSizeAttribute(syntaxTree):

    i = 0
    size = 0

    while syntaxTree != None:

        if syntaxTree.nodekind == NodeKind.DecK and syntaxTree.dec == DecKind.FuncDecK:
            size = 0

        for i in range(MAXCHILDREN):
            calcSizeAttribute(syntaxTree.child[i])

        # Local declaration.
        if ((syntaxTree.nodekind == NodeKind.DecK)
            and ((syntaxTree.dec == DecKind.ScalarDecK)
                 or (syntaxTree.dec == DecKind.ArrayDecK))
                and (syntaxTree.isParameter == False or syntaxTree.isParameter == None)):

            if syntaxTree.dec == DecKind.ScalarDecK:
                size = size + WORDSIZE

            elif syntaxTree.dec == DecKind.ArrayDecK:
                size = size + (WORDSIZE * int(syntaxTree.val))

            syntaxTree.localSize = size

        if syntaxTree.nodekind == NodeKind.DecK and syntaxTree.dec == DecKind.FuncDecK:

            if genComments:
                print("*** Calculated local size attribute for ",
                    syntaxTree.name + " as ", size, "\n")

            syntaxTree.localSize = size

        syntaxTree = syntaxTree.sibling


def calcStackOffsets(syntaxTree):
    i = 0

    AP = 0
    LP = 0

    while syntaxTree != None:

        if syntaxTree.nodekind == NodeKind.DecK and syntaxTree.dec == DecKind.FuncDecK:
            AP, LP = 0, 0

        # Visit children nodes.
        for i in range(MAXCHILDREN):
            calcStackOffsets(syntaxTree.child[i])

        # Post-order:
        if ((syntaxTree.nodekind == NodeKind.DecK) and
            ((syntaxTree.dec == DecKind.ArrayDecK)
             or (syntaxTree.dec == DecKind.ScalarDecK))):

            if syntaxTree.isParameter:

                syntaxTree.offset = AP
                AP += varSize(syntaxTree)

                if genComments:
                    print("*** Calculated offset attribute for ",
                        syntaxTree.name + " as ", syntaxTree.offset, "\n")

            else:

                LP -= varSize(syntaxTree)
                syntaxTree.offset = LP
            
                if genComments:
                    print("*** Calculated offset attribute for ",
                        syntaxTree.name + " as ", syntaxTree.offset, "\n")

        syntaxTree = syntaxTree.sibling


def genComment(comment):
    global output

    if genComments:
        output += "# " + comment + "\n"


def genCommentSeparator():
    global output

    if genComments:
        output += "##################################################\n"


def genTopLevelDecl(tree):

    global output

    current = None
    commentBuffer = ""

    current = tree

    while current != None:

        if current.nodekind == NodeKind.DecK:

            if current.dec == DecKind.ScalarDecK:

                genCommentSeparator()
                commentBuffer = "Variable " + current.name + \
                    " is a scalar of type " + current.variableDataType.name
                genComment(commentBuffer)

                output += ".VAR\n"
                output += "    _"+current.name+": .WORD  1\n\n"

            elif current.dec == DecKind.ArrayDecK:

                genCommentSeparator()
                commentBuffer = "Variable " + current.name + " is an array of type " + \
                    current.variableDataType.name + " and size " + current.val
                genComment(commentBuffer)

                output += ".VAR\n"
                output += "    _"+current.name+": .WORD  "+current.val+"\n\n"

            elif current.dec == DecKind.FuncDecK:
                genFunction(current)

        current = current.sibling


def genFunction(tree):
    global output

    commentBuffer = ""

    # Node must be a function or a declaration
    if tree.nodekind == NodeKind.DecK and tree.dec == DecKind.ArrayDecK:
        return

    genCommentSeparator()
    commentBuffer = "Function declaration for  " + tree.name
    genComment(commentBuffer)

    output += "\n"

    # Function header
    output += ".PROC _" + str(tree.name) + "(.NOCHECK,.SIZE=" + str(tree.localSize) + ",.NODISPLAY,.ASSEMBLY=" + str(tree.assemblyAreaSize) + ")\n"

    # Variables declared
    genFunctionLocals(tree)
    output += ".ENTRY\n"

    genStatement(tree.child[1])

    # End of procedure
    # genInstruction("exit")
    # genInstruction("endP")
    output += ".ENDP\n\n"


def genFunctionLocals(tree):
    i = 0

    for i in range(MAXCHILDREN):
        if tree.child[i] != None:
            genFunctionLocals2(tree.child[i])


def genFunctionLocals2(tree):
    '''
    Do a postorder traversal of the syntax tree looking for non-parameter
    declarations, and emit code to declare them.
    '''
    global output

    i = 0
    offset = 0
    commentBuffer = ""

    while tree != None:

        for i in range(MAXCHILDREN):
            genFunctionLocals2(tree.child[i])

        # Postorder operations
        if tree.nodekind == NodeKind.DecK:

            if not tree.isParameter:
                commentBuffer += "Local variable \\" + tree.name + "\\"
                genComment(commentBuffer)
            else:
                commentBuffer += "Parameter \\" + tree.name + "\\"
                genComment(commentBuffer)

        
            if tree.isParameter:
                offset = STACKMARKSIZE
            else:
                offset = 0
            
            offset += tree.offset

            output += "  .LOCAL _" + tree.name + " " + str(offset) + "," + str(varSize(tree)) + " (0,0,0)\n"
            output += "\n"

        tree = tree.sibling



def genStatement(tree):
    
    current = None

    current = tree

    while current != None:

        # Assignment
        if current.nodekind == NodeKind.ExpK and current.exp == ExpKind.AssignK:
            genComment("** assignment statement*")
	    
            genComment("evaluate rvalue as value")
            genExpression(current.child[1], False)
            
            genComment("evaluate lvalue as address")
            genExpression(current.child[0], True)
            
            genInstruction("assignW")
        
        # Statements
        elif current.nodekind == NodeKind.StmtK:

            if current.stmt == StmtKind.IfK:
                genIfStmt(current)
            
            elif current.stmt == StmtKind.WhileK:
                genWhileStmt(current)
            
            elif current.stmt == StmtKind.ReturnK:
                genReturnStmt(current)
            
            elif current.stmt == StmtKind.CallK:
                genCallStmt(current)

            elif current.stmt == StmtKind.CompoundK:
                genStatement(current.child[1])
        
        current = current.sibling


def genExpression(tree, addressNeeded):
    
    scratch = ""

    # if it's an expression, eval as expression...
    if tree.nodekind == NodeKind.ExpK:

        if tree.exp == ExpKind.IdK:

            if tree.declaration != None:

                if tree.declaration.dec == DecKind.ArrayDecK: # Declaration?

                    if(tree.child[0] == None):
                        
                        genComment("leave address of array on stack")

                        if (tree.declaration.isGlobal):
                        
                            genComment("push address of global variable")
                            scratch += "pshAdr  _" + tree.declaration.name
                            genInstruction(scratch)

                        elif tree.declaration.isParameter:
                            scratch += "pshAP   " + str(tree.declaration.offset)
                            genInstruction(scratch)
                            genInstruction("derefW")

                        else:
                            scratch += "pshLP   " + str(tree.declaration.offset)
                            genInstruction(scratch)

                    else:
                        genComment("calculate array offset")
                        genExpression(tree.child[0], False)
                        genInstruction("pshLit  4")
                        genInstruction("mul     noTrap")

                        genComment("get address of array onto stack")
                        if tree.declaration.isGlobal:
                            genComment("push address of global variable")
                            scratch += "pshAdr  _" + tree.declaration.name
                            genInstruction(scratch)

                        elif tree.declaration.isParameter :
                            scratch += "pshAP   " + str(tree.declaration.offset)
                            genInstruction(scratch)
                            genInstruction("derefW")

                        else :
                            scratch += "pshLP   " + str(tree.declaration.offset)
                            genInstruction(scratch)
                        
                        
                        
                        genComment("index into array")
                        genInstruction("add     noTrap")
                        
                        
                        if not addressNeeded:
                            genComment("dereference resulting address")
                            genInstruction("derefW")

                elif tree.declaration.dec == DecKind.ScalarDecK:


                    genComment("calculate effective address of variable")

                    if tree.declaration.isGlobal:
                        genComment("push address of global variable")
                        scratch += "pshAdr  _" + tree.declaration.name

                    elif tree.declaration.isParameter:
                        genComment("push parm address")
                        scratch += "pshAP   " + str(tree.declaration.offset)
                    
                    else:
                        genComment("push address of local")
                        scratch += "pshLP   " + str(tree.declaration.offset)
                    
                    
                    genInstruction(scratch)
                    
                    if not addressNeeded:
                        genInstruction("derefW")
                    
        elif tree.exp == ExpKind.OpK:

            genExpression(tree.child[0], False)
            genExpression(tree.child[1], False)
            
            if tree.op == TokenType.PLUS:
                genInstruction("add     noTrap")
            
            elif tree.op == TokenType.MINUS:
                genInstruction("sub     noTrap")
            
            elif tree.op == TokenType.MULT:
                genInstruction("mul     noTrap")
            
            elif tree.op == TokenType.DIVISION:
                genInstruction("div     noTrap")
            
            elif tree.op == TokenType.LESS:
                genInstruction("intLS")
            
            elif tree.op == TokenType.GREATER:
                genInstruction("intGT")
            
            elif tree.op == TokenType.DIFFERENT:
                genInstruction("relNE")
            
            elif tree.op == TokenType.LESS_EQUAL:
                genInstruction("intLE")
            
            elif tree.op == TokenType.GREATER_EQUAL:
                genInstruction("intGE")
            
            elif tree.op == TokenType.EQUALS_TO:
                genInstruction("relEQ")
            
            else:
                print("Non exixtent operation, exiting...")
                exit()
            
        elif tree.exp == ExpKind.ConstK:

            scratch += "pshLit  " + tree.val
            genInstruction(scratch)
        
        elif tree.exp == ExpKind.AssignK:

            genComment("calculate the rvalue of the assignment")
            genExpression(tree.child[1], False)
            genInstruction("dup1")

            genComment("calculate the lvalue of the assignment")
            genExpression(tree.child[0], True)

            genComment("perform assignment")
            genInstruction("assignW")

    elif tree.nodekind == NodeKind.StmtK:
        
        if tree.stmt == StmtKind.CallK:

            genCallStmt(tree)
            if tree.functionReturnType != ExpType.Void:
                genInstruction("pshRetW")


nextLabel = 0
def genNewLabel():
    global nextLabel

    labelBuffer = ""

    nextLabel += 1

    labelBuffer += "label" + str(nextLabel)
    return labelBuffer


def genInstruction(instruction):
    global output

    output += "        " + instruction + "\n"


def genIfStmt(tree):
    global output

    elseLabel = ""
    endLabel = ""
    scratch = ""
    
    elseLabel = genNewLabel()
    endLabel = genNewLabel()

    genComment("IF statement")
    genComment("if false, jump to else-part")
    genExpression(tree.child[0], False)

    scratch += "brFalse " + elseLabel
    genInstruction(scratch)
    
    genStatement(tree.child[1])
    scratch += " branch " + endLabel
    genInstruction(scratch)
    
    output += elseLabel + ":\n" 

    genStatement(tree.child[2])

    output += endLabel + ":\n"


def genWhileStmt(tree):
    global output
    
    startLabel = ""
    endLabel = ""
    scratch = ""

    startLabel = genNewLabel()
    endLabel = genNewLabel()

    genComment("WHILE statement")
    genComment("if expression evaluates to FALSE, exit loop")

    output += startLabel + ":\n"

    genExpression(tree.child[0], False)

    scratch += "brFalse  " + endLabel
    genInstruction(scratch)
    
    genStatement(tree.child[1])

    scratch += " branch  " + startLabel
    genInstruction(scratch)

    output += endLabel + ":\n"


def genReturnStmt(tree):

    if tree.functionReturnType != ExpType.Void:

        if tree.child[0] != None:
            genExpression(tree.child[0], False)

        else:
            genInstruction("pshLit  0")

        genInstruction("popRetW");	

    genInstruction("exit")


def genCallStmt(tree):
    numPars = 0
    argPtr = None
    scratch = ""

    argPtr = tree.child[0]

    while argPtr != None:

        genExpression(argPtr, False)
        scratch += "mkPar   4," + str(numPars*4)
        genInstruction(scratch)

        numPars += 1
        argPtr = argPtr.sibling
    
    scratch, "call    _" + tree.name + "," + str(numPars)
    genInstruction(scratch)


def genProgram(tree, file, moduleName):

    global output

    output += ".TITLE " + moduleName + "\n"
    output += ".FILE \\" + file.name + "\\ \n\n"
    output += ".EXPORT _main\n\n"
    output += ".IMPORT _input\n"
    output += ".IMPORT _output\n\n"

    genTopLevelDecl(tree)

    # print(output)

    file.write(output)



def varSize(tree):

    size = 0

    if tree.nodekind == NodeKind.DecK:

        # Normal scalar.
        if tree.dec == DecKind.ScalarDecK:
            size = WORDSIZE

        elif tree.dec == DecKind.ArrayDecK:

            # Array parameters passed by reference
            if tree.isParameter:
                size = 4
            else:
                size = WORDSIZE * (int(tree.val))

        else:
            size = 0
    else:
        size = 0
    return int(size)

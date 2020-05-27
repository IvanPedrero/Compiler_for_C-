from globalTypes import *

Error = False

WORDSIZE = 4

STACKMARKSIZE = 8

output = ""


def codeGen(syntaxTree, fileName):

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

        genProgram(syntaxTree, fileName, "output")


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

                print("*** Calculated offset attribute for ",
                      syntaxTree.name + " as ", syntaxTree.offset, "\n")

            else:

                LP -= varSize(syntaxTree)
                syntaxTree.offset = LP

                print("*** Calculated offset attribute for ",
                      syntaxTree.name + " as ", syntaxTree.offset, "\n")

        syntaxTree = syntaxTree.sibling


def genComment(comment):
    global output
    output += "# " + comment + "\n"


def genCommentSeparator():
    global output
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
    print("Entered function for " + tree.name)
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



# Line 575
def genStatement(tree):
    pass












def genProgram(tree, fileName, moduleName):

    global output

    output += ".TITLE " + moduleName + "\n"
    output += ".FILE \\" + fileName + "\\ \n\n"
    output += ".EXPORT _main\n\n"
    output += ".IMPORT _input\n"
    output += ".IMPORT _output\n\n"

    genTopLevelDecl(tree)

    print(output)


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

from globalTypes import *
from semantica import *
from symtab import *

TITLE_TAB = "   "
TEXT_TAB = "        "
COMMENT_TAB = "                 "

generatedCode = ""

# This function will calculate the offsets of each declaration of the syntax tree.
def calculateOffsets(tree):
    i = 0

    # Offsets of the variables.
    AP = 0
    LP = 0

    while tree != None:
        if tree.nodekind == NodeKind.DecK and tree.dec == DecKind.FuncDecK:
            AP, LP = 0, 0

        for i in range(MAXCHILDREN):
            calculateOffsets(tree.child[i])

        # Post-order:
        if ((tree.nodekind == NodeKind.DecK) and
            ((tree.dec == DecKind.ArrayDecK)
             or (tree.dec == DecKind.ScalarDecK))):
            if tree.isParameter:
                tree.offset = AP
                AP += varSize(tree)
            else:
                LP -= varSize(tree)
                tree.offset = LP
        tree = tree.sibling


# This function will return the size of a variable depending on its size.
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


# This function will generate MIPS code recursively given a node of the syntax tree.
def translateCode(tree, imprime=True):
    global generatedCode
    
    isParentTree = True

    if tree == None:
        return

    if tree.nodekind == NodeKind.DecK:

        if tree.dec == DecKind.FuncDecK:

            # Main function.
            if tree.name == "main":

                generatedCode += "\n" + TITLE_TAB + \
                    "main:" + genComment("Driver function")
                generatedCode += TEXT_TAB + "la $t4 stack\n"
                generatedCode += TEXT_TAB + "move $fp $sp\n"

                space = 0
                for scope in range(len(BucketList)):
                    if scope == 0:
                        for name in BucketList[scope]:
                            if BucketList[scope][name][1] == None:
                                space += WORDSIZE

                generatedCode += TEXT_TAB + \
                    "addiu $sp $sp -"+str(space)+"\n"

            # Function declarations:
            else:

                isParentTree = False

                generatedCode += "\n" + TITLE_TAB + tree.name + \
                    ":" + genComment("Function declaration")
                generatedCode += TEXT_TAB + "sw $ra 0($sp)\n"
                generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"
                generatedCode += TEXT_TAB + "move $fp $sp\n"

                childsInTree = 0
                node = tree.child[1]
                while node != None:
                    childsInTree += 1
                    node = node.sibling

                node = tree
                move = 4 * childsInTree + 4
                generatedCode += TEXT_TAB + "addiu $sp $sp " + str(move) + "\n"

                functionSize = 0
                while node != None:
                    if node.functionReturnType == TokenType.INT:
                        functionSize += 2
                        offsetSize, _ = retrieveNodeInformation(
                            node.child[0].name, node.child[0].lineno)
                        generatedCode += TEXT_TAB + "lw $a0 0($sp)\n"
                        generatedCode += TEXT_TAB + \
                            "sw $a0 "+str(offsetSize)+"($fp)\n"
                        generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"
                    else:
                        generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"
                        functionSize += 1

                    node = node.sibling

                spaceNeeded = 0
                for scope in range(len(BucketList)):
                    for node in BucketList[scope]:
                        if tree.child[0] != None and node == tree.child[0].name:
                            spaceNeeded += WORDSIZE

                generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"
                generatedCode += TEXT_TAB + \
                    "addiu $sp $sp -"+str(spaceNeeded)+"\n"

                translateCode(tree.child[1])

                generatedCode += TEXT_TAB + "lw $ra 4($fp)\n"
                size = 4 * functionSize + 8

                generatedCode += TEXT_TAB + "addiu $sp $sp "+str(size)+"\n"
                generatedCode += TEXT_TAB + "lw $fp 0($sp)\n"
                generatedCode += TEXT_TAB + "jr $ra\n"

                isParentTree = False

        else:

            isParentTree = False

    # Expression statement.
    elif tree.nodekind == NodeKind.ExpK:

        hasDeclaration = True

        if tree.exp == ExpKind.AssignK:

            isParentTree = False

            if tree.child[0] != None and tree.child[0].declaration != None and tree.child[0].declaration.dec == DecKind.ArrayDecK:
                node = retrieveNodeObject(tree.child[0].name, tree.lineno)

                if tree.child[0].exp == ExpKind.ConstK:

                    offsetSize = tree.child[0].declaration.offset + \
                        (4 * int(tree.child[0].child[0].val))

                else:
                    hasDeclaration = False

                    generatedCode += TEXT_TAB + "move $t5 $a0\n"
                    translateCode(tree.child[0].child[1])
                    offsetSize = 4
                    generatedCode += TEXT_TAB + "mul $a0 $a0 4\n"
                    generatedCode += TEXT_TAB + "add $t4 $t4 $a0\n"
                    generatedCode += TEXT_TAB + \
                        "sw $t5 "+str(offsetSize)+"($t4)\n"
                    generatedCode += TEXT_TAB + "sub $t4 $t4 $a0\n"

            else:
                if tree.child[0] != None and tree.child[0].declaration != None:

                    try:
                        offsetSize, scope = retrieveNodeInformation(
                            tree.child[0].declaration.name, tree.child[0].declaration.lineno)
                    except:
                        offsetSize = 0
                        scope = 0

                else:

                    try:
                        offsetSize, scope = retrieveNodeInformation(
                            tree.name, tree.lineno)
                    except:
                        offsetSize = 0
                        scope = 0

            translateCode(tree.child[1])

            if hasDeclaration:
                if tree.child[0] != None and tree.child[0].declaration != None and tree.child[0].declaration.isGlobal:
                    generatedCode += TEXT_TAB + "sw $a0 " + \
                        str(tree.child[0].declaration.offset)+"($t4)\n"
                else:
                    generatedCode += TEXT_TAB + \
                        "sw $a0 "+str(offsetSize)+"($fp)\n"

        elif tree.exp == ExpKind.IdK:

            offsetSize, scope = retrieveNodeInformation(tree.name, tree.lineno)

            if tree.child[0] != None and tree.child[0].declaration != None and tree.child[0].declaration.isGlobal:

                generatedCode += TEXT_TAB + "lw $a0 " + \
                    str(tree.child[0].declaration.offset)+"($t4)\n"

            else:
                generatedCode += TEXT_TAB + "lw $a0 "+str(offsetSize)+"($fp)\n"

        elif tree.exp == ExpKind.OpK:

            isParentTree = False

            translateCode(tree.child[0])
            generatedCode += TEXT_TAB + "sw $a0 0($sp)\n"
            generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"

            translateCode(tree.child[1])
            generatedCode += TEXT_TAB + "lw $t5 4($sp)\n"

            if tree.op == TokenType.MULT:
                generatedCode += TEXT_TAB + "mul $a0 $t5 $a0\n"

            elif tree.op == TokenType.DIVISION:
                generatedCode += TEXT_TAB + "div $a0 $t5 $a0\n"

            elif tree.op == TokenType.PLUS:
                generatedCode += TEXT_TAB + "add $a0 $t5 $a0\n"

            elif tree.op == TokenType.LESS:
                generatedCode += TEXT_TAB + "sub $a0 $t5 $a0\n"

            generatedCode += TEXT_TAB + "addiu $sp $sp 4\n"

        elif tree.exp == ExpKind.ConstK:

            generatedCode += TEXT_TAB + "li $a0 "+tree.val+"\n"

        elif tree.dec == DecKind.ArrayDecK:

            isParentTree = False

            node = retrieveNodeObject(tree.child[0].name, tree.lineno)

            if tree.child[1].exp == ExpKind.ConstK:
                index = tree.child[1].val
                offsetSize = node.offset + (4*int(index))
                generatedCode += TEXT_TAB + "lw $a0 "+str(offsetSize)+"($t4)\n"

            else:

                translateCode(tree.child[1])

                generatedCode += TEXT_TAB + "mul $a0 $a0 4\n"
                generatedCode += TEXT_TAB + "add $t4 $t4 $a0\n"
                generatedCode += TEXT_TAB + "move $t5 $a0\n"

                offsetSize, _ = retrieveNodeInformation(
                    tree.child[0].name, tree.lineno)

                generatedCode += TEXT_TAB + "lw $a0 "+str(offsetSize)+"($t4)\n"
                generatedCode += TEXT_TAB + "sub $t4 $t4 $t5\n"

    # Statement expression.
    elif tree.nodekind == NodeKind.StmtK:
        global IF_NUMBER
        global WHILE_NUMBER

        if tree.stmt == StmtKind.IfK or tree.stmt == StmtKind.WhileK:

            isParentTree = False

            if tree.stmt == StmtKind.IfK:

                loopCount = IF_NUMBER

                IF_NUMBER = IF_NUMBER + 1

                conditionalStmt = "if_true_branch_"+str(loopCount)

            else:

                loopCount = WHILE_NUMBER

                WHILE_NUMBER = WHILE_NUMBER + 1

                generatedCode += TEXT_TAB + \
                    "while_start_"+str(loopCount)+":\n"

                conditionalStmt = "while_"+str(loopCount)

            translateCode(tree.child[0].child[0])
            generatedCode += TEXT_TAB + "sw $a0 0($sp)\n"
            generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"

            translateCode(tree.child[0].child[1])
            generatedCode += TEXT_TAB + "lw $t5 4($sp)\n"
            generatedCode += TEXT_TAB + "addiu $sp $sp 4\n"

            if tree.child[0].op == TokenType.EQUALS_TO:
                generatedCode += TEXT_TAB + "beq $a0 $t5 " + \
                    conditionalStmt + genComment("== comparison", False)

            elif tree.child[0].op == TokenType.LESS:
                generatedCode += TEXT_TAB + "slt $t6 $t5 $a0\n"
                generatedCode += TEXT_TAB + "bne $t6 $0 " + \
                    conditionalStmt + genComment("< comparison", False)

            elif tree.child[0].op == TokenType.LESS_EQUAL:
                generatedCode += TEXT_TAB + "slt $t6 $a0 $t5\n"
                generatedCode += TEXT_TAB + "beq $t6 $0 " + \
                    conditionalStmt + genComment("<= comparison", False)

            elif tree.child[0].op == TokenType.GREATER:
                generatedCode += TEXT_TAB + "slt $t6 $a0 $t5\n"
                generatedCode += TEXT_TAB + "bne $t6 $0 " + \
                    conditionalStmt + genComment("> comparison", False)

            elif tree.child[0].op == TokenType.GREATER_EQUAL:
                generatedCode += TEXT_TAB + "slt $t6 $t5 $a0\n"
                generatedCode += TEXT_TAB + "beq $t6 $0 " + \
                    conditionalStmt + genComment(">= comparison", False)

            elif tree.child[0].op == TokenType.DIFFERENT:
                generatedCode += TEXT_TAB + "bne $a0 $t5 " + \
                    conditionalStmt + genComment("!= comparison", False)

            if tree.stmt == StmtKind.IfK:

                generatedCode += TEXT_TAB + \
                    "if_false_branch_"+str(loopCount)+":\n"

                if tree.child[2] != None:
                    translateCode(tree.child[2])

                generatedCode += TEXT_TAB + "b end_if_"+str(loopCount)+"\n"
                generatedCode += TEXT_TAB + \
                    "if_true_branch_"+str(loopCount)+":\n"

                translateCode(tree.child[0])
                generatedCode += TEXT_TAB + "end_if_"+str(loopCount)+":\n"
                translateCode(tree.child[1])

            else:
                generatedCode += TEXT_TAB + \
                    "b while_end_"+str(loopCount)+"\n"
                generatedCode += TEXT_TAB + "while_"+str(loopCount)+":\n"

                translateCode(tree.child[1])

                generatedCode += TEXT_TAB + \
                    "b while_start_"+str(loopCount)+"\n"

                generatedCode += TEXT_TAB + \
                    "while_end_"+str(loopCount)+":\n"

        elif tree.stmt == StmtKind.CallK:

            isParentTree = False

            if tree.name == "input":
                generatedCode += TEXT_TAB + "li $v0 5 \n"
                generatedCode += TEXT_TAB + "syscall \n"
                generatedCode += TEXT_TAB + "move $a0 $v0 \n"

            elif tree.name == "output":
                translateCode(tree.child[0])
                generatedCode += TEXT_TAB + "li $v0 1 \n"
                generatedCode += TEXT_TAB + "syscall \n"

            else:
                generatedCode += TEXT_TAB + "sw $fp 0($sp)\n"
                generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"
                comparitionNodes = []

                for scope in range(len(BucketList)):
                    for n in BucketList[scope]:
                        if tree.child[0] != None and n == tree.child[0].name:
                            comparitionNodes.append(tree.child[0])
                            break

                for scope in range(len(BucketList)):
                    for n in BucketList[scope]:
                        if tree.child[0] != None and n == tree.child[0].name:
                            comparitionNodes.append(tree.child[0])

                treeChild = tree.child[0]
                for node in comparitionNodes:

                    if node != None and node.dec == DecKind.ArrayDecK:

                        temp = None
                        for scope in range(len(Declarations)):
                            for n in Declarations[scope]:
                                if treeChild != None and n == treeChild.name:
                                    temp = treeChild
                                    break

                        generatedCode += TEXT_TAB + "li $a0 0\n"
                        generatedCode += TEXT_TAB + "sw $a0 0($sp)\n"
                        generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"

                    elif treeChild != None:

                        if treeChild.exp == ExpKind.ConstK:
                            generatedCode += TEXT_TAB + "li $a0 "+treeChild.val+"\n"

                        elif treeChild.exp == ExpKind.IdK:
                            offsetSize, scope = retrieveNodeInformation(
                                treeChild.name, treeChild.lineno)

                            if tree.child[0] != None and tree.child[0].declaration != None and tree.child[0].declaration.isGlobal:
                                generatedCode += TEXT_TAB + \
                                    "lw $a0 "+str(offsetSize)+"($t4)\n"
                            else:
                                generatedCode += TEXT_TAB + \
                                    "lw $a0 "+str(offsetSize)+"($fp)\n"

                        generatedCode += TEXT_TAB + "sw $a0 0($sp)\n"
                        generatedCode += TEXT_TAB + "addiu $sp $sp -4\n"

                    if treeChild != None:
                        treeChild = treeChild.sibling

                generatedCode += TEXT_TAB + "jal " + \
                    tree.name + genComment("Call to function")

    # Call recursively the childs if its a parent.
    if isParentTree:
        for child in tree.child:
            translateCode(child)

    # Call the rest of the tree.
    translateCode(tree.sibling)


# This function will return a comment in MIPS format.
def genComment(comment, needSpace=True):
    if needSpace:
        return COMMENT_TAB + "# " + comment + "\n"
    else:
        return "\t\t# " + comment + "\n"


# This function will generate the headers of the MIPS program.
def createHeader():
    global generatedCode

    generatedCode += ".text\n"
    generatedCode += TITLE_TAB + ".globl main\n"


# This function will generate the footers of the MIPS program.
def createFooter():
    global generatedCode

    generatedCode += "\n\n.data\n"
    generatedCode += TITLE_TAB + "stack: .word 0" + \
        genComment(
            "$t4 for stack, $t5 and $t6 for arithmetic/logic operations", False)


# This method will generate the file and will print the generated MIPS code given a file name and an extension.
def createFile(file):
    global generatedCode

    output = None
    try:
        output = open(file, 'w')

        output.write(generatedCode)

    finally:
        if output is not None:
            output.close()


# Function call to start generating the tree.
def codeGen(tree, file):

    calculateOffsets(tree)

    createHeader()

    translateCode(tree)

    createFooter()

    createFile(file)

    print("\n- Code generation status : Finished -")
    print("\n File generated: ", file)

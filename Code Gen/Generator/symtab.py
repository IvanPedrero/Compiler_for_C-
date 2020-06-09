from globalTypes import *

# the hash table
BucketList = {
    0: {
        'main': [0, ExpType.Void, 0, 0],
        'input': [0, ExpType.Integer, 0, 0],
        'output': [1, ExpType.Void, 0, 0]
    }
}

Declarations = {}

# Current location of a node
location = 0

# stack array
stackArray = [0]

# Scope being checked
scope = 0

WORDSIZE = 4

STACKMARKSIZE = 8

IF_NUMBER = 0

WHILE_NUMBER = 0

# Procedure st_insert inserts line numbers and
# memory locations into the symbol table
# loc = memory location is inserted only the
# first time, otherwise ignored


def st_insert(tree, symbolType, lineno, scope, newScope=-1):
    global location

    if tree == None:
        return

    try:
        int(tree.name)
        return
    except ValueError:
        if tree.name in BucketList[scope]:
            if BucketList[scope][tree.name][-1] != lineno:
                BucketList[scope][tree.name].append(lineno)
                # Return if already defined
                try:
                    tree.declarationLine = Declarations[scope][tree.name].lineno
                    tree.declaration = Declarations[scope][tree.name]
                    
                except KeyError:
                    pass

                return False
        else:
            location = location + 1
            BucketList[scope][tree.name] = [
                location, symbolType, newScope, lineno]
            # Return if first time defined´

            # Add the declarations to a dictionary
            if type(tree.val) in [int, str] or tree.val == None:

                try:
                    dic = {tree.name: tree}
                    Declarations[scope].update(dic)
                    return
                except KeyError:
                    Declarations[scope] = {}
                    dic = {tree.name: tree}
                    Declarations[scope].update(dic)

            return True


# Function st_lookup returns the memory
# location of a variable or -1 if not found
def st_lookup(name):
    for node in range(1, len(stackArray)+1):
        if name in BucketList[stackArray[(-node)]]:
            return stackArray[-node]
    return stackArray[-1]


# This function will check if a given variable
# in a given scope already defined.
def checkIfInTable(name, actualScope):
    if name in BucketList[actualScope]:
        return True
    return False


# Procedure printSymTab prints a formatted
# listing of the symbol table contents
# to the listing file
def printSymTab():
    print("Variable Name    Location    Scope   Type")
    print("-------------    --------    -----   ---------")
    for scope in BucketList:
        for name in BucketList[scope]:
            if BucketList[scope][name][1] != None:
                loc = BucketList[scope][name][3]
                scp = BucketList[scope][name][1]
                print(name, " "*(17-len(name)), loc, " "*(10-len(str(loc))),
                      scope, " "*(5-len(str(scope))), scp.name)



# Procedures for code generation:

def retrieveNodeInformation(name, line):

    for scope in range(len(Declarations)):
        if Declarations.get(scope) == None:
            continue
        for n in Declarations[scope]:
            if n == name:  # and line in BucketList[scope][name][5]
                #print(str(Declarations[scope][n].offset) + " " + str(Declarations[scope][n].lineno))
                return Declarations[scope][n].offset, Declarations[scope][n].lineno


def retrieveNodeObject(name, line):
    for scope in range(len(Declarations)):
        for node in Declarations[scope]:
            if node == name:  # and line in  node.lineasDeAparicion:
                #print(Declarations[scope][node].name)
                return Declarations[scope][node]
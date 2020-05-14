from globalTypes import *

# the hash table
BucketList = {
    0: {
        'main': [0, ExpType.Void, 0, 0],
        'input': [0, ExpType.Integer, 0, 0],
        'output': [1, ExpType.Void, 0, 0]
    }
}

# Current location of a node
location = 0

# stack array
stackArray = [0]

# Scope being checked
scope = 0

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
        if name in BucketList[scope]:
            if BucketList[scope][name][-1] != lineno:
                BucketList[scope][name].append(lineno)
        else:
            location = location + 1
            BucketList[scope][name] = [location, tipo, newScope, lineno]


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

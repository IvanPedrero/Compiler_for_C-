from enum import Enum

# Token class.
class TokenType(Enum):
	NUM = 0	
	ID = 1
	PLUS = 2
	MINUS = 3
	MULT = 4
	DIVISION = 5
	GREATER = 6
	GREATER_EQUAL = 7
	LESS = 8
	LESS_EQUAL = 9
	EQUAL = 10
	EQUALS_TO = 11
	DIFFERENT = 12
	SEMICOLON = 13
	COMMA = 14
	OPEN_BRACKETS = 15
	CLOSE_BRACKETS = 16
	OPEN_SQUARE_BRACKETS = 17
	CLOSE_SQUARE_BRACKETS = 18
	OPEN_CURLY_BRACKETS = 19
	CLOSE_CURLY_BRACKETS = 20
	COMMENT = 21
	RESERVED = 22
	ELSE = 23
	IF = 24
	INT = 25
	RETURN = 26
	VOID = 27
	WHILE = 28
	ENDFILE = 29
	ERROR = 30
	
# Reserved word array.
reserved_keywords = ["else","if","int","return","void","while"]

'''
This function will return a reserved word token
given a string. If the string does not match with 
any reserved word, it will return the token ERROR.
'''
def getReservedKeyWord(keyword):
	if keyword not in reserved_keywords:
		return TokenType.ERROR
	else:
		if keyword == "else":
			return TokenType.ELSE
		elif keyword == "if":
			return TokenType.IF
		elif keyword == "int":
			return TokenType.INT
		elif keyword == "return":
			return TokenType.RETURN
		elif keyword == "void":
			return TokenType.VOID
		elif keyword == "while":
			return TokenType.WHILE
		else:
			return TokenType.ERROR



#***********   Syntax tree for parsing ************

class NodeKind(Enum):
    StmtK = 0
    ExpK = 1
    DecK = 2

class StmtKind(Enum):
    IfK = 0
    WhileK = 1
    ReturnK = 2
    CallK = 3
    CompoundK = 5

class ExpKind(Enum):
    OpK = 0
    IdK = 1
    ConstK = 2
    AssignK = 1

class DecKind(Enum):
    ScalarDecK = 0
    ArrayDecK = 1
    FuncDecK = 2

# ExpType is used for type checking
class ExpType(Enum):
    Void = 0
    Integer = 1
    Boolean = 2
    Array = 3
    Function = 4

# Máximo número de hijos por nodo (3 para el if)
MAXCHILDREN = 3

class TreeNode:
    def __init__(self):
        # MAXCHILDREN = 3 está en globalTypes
        self.child = [None] * MAXCHILDREN # tipo treeNode
        self.sibling = None               # tipo treeNode
        self.lineno = 0                   # tipo int
        self.nodekind = None              # tipo NodeKind, en globalTypes
        # en realidad los dos siguientes deberían ser uno solo (kind)
        # siendo la  union { StmtKind stmt; ExpKind exp;, DecKind dec}
        self.stmt = None                  # tipo StmtKind
        self.exp = None                   # tipo ExpKind
        self.dec = None					# tipo DecKind
        # en realidad los tres siguientes deberían ser uno solo (attr)
        # siendo la  union { TokenType op; int val; char * name;}
        self.op = None                    # tipo TokenType
        self.val = None                   # tipo int
        self.name = None                  # tipo String
        # for type checking of exps
        self.type = None                  # de tipo ExpType
		# Function return type
        self.functionReturnType = None
		# Data type
        self.variableDataType = None
		# Expression type
        self.expressionType = None
		# Expression type
        self.isParameter = None
        self.isGlobal = None
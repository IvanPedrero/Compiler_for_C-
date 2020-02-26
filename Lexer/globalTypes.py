from enum import Enum

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
	
reserved_keywords = ["else","if","int","return","void","while"]

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
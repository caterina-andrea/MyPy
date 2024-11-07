#!/usr/bin/python3
#
# Author: Caterina Valdovinos
# Description:
#   Can produce a printed output of the token's qualities
#----------------------------------------------------------------------
AND = 'AND'	
ASSIGN = 'ASSIGN'
BOOLTYPE = 'BOOLTYPE'	
BOOLVAL = 'BOOLVAL'	
COLON = 'COLON'
COMMA = 'COMMA'
DIVIDE = 'DIVIDE'
DO = 'DO'
DOT = 'DOT'
ELIF = 'ELIF'	
ELSE = 'ELSE'	
END = 'END'	
EOS = 'EOS'
EQUAL = 'EQUAL' 
FLOATTYPE = 'FLOATTYPE' 
FLOATVAL = 'FLOATVAL'	
FUN = 'FUN'	
GREATER_THAN = 'GREATER_THAN'
GREATER_THAN_EQUAL = 'GREATER_THAN_EQUAL'
ID = 'ID'
IF = 'IF'	
INTTYPE = 'INTTYPE'
INTVAL = 'INTVAL'	
LESS_THAN = 'LESS_THAN'
LESS_THAN_EQUAL = 'LESS_THAN_EQUAL'
LPAREN = 'LPAREN'
MINUS = 'MINUS'
MODULO = 'MODULO'
MULTIPLY = 'MULTIPLY'
NEW	 = 'NEW'
NIL = 'NIL'	
NOT = 'NOT'	
NOT_EQUAL = 'NOT_EQUAL'
OR = 'OR'
PLUS = 'PLUS'
RETURN = 'RETURN'	
RPAREN = 'RPAREN'
SEMICOLON = 'SEMICOLON'	
SET = 'SET'	
STRINGTYPE = 'STRINGTYPE'	
STRINGVAL = 'STRINGVAL' 
STRUCTTYPE = 'STRUCTTYPE'	
THEN = 'THEN'
VAR = 'VAR'
WHILE = 'WHILE'	
class Token(object):
    def __init__(self, tokentype, lexeme, line, column):
        self.tokentype = tokentype 
        self.lexeme = lexeme 
        self.line = line 
        self.column = column
    
    def __str__(self):
        """ Returns the string to be printed if all goes well """
        s = str(self.tokentype) + " '" + str(self.lexeme)+ "' " + str(self.line) + ':' + str(self.column)
        return s
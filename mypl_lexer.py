#!/usr/bin/python3
#
# Author: Caterina Valdovinos
# Description:
#   Separates the source code and returns separate tokens
#----------------------------------------------------------------------
import mypl_token as token
import mypl_error as error

class Lexer(object):
    def __init__(self, input_stream):
        self.line = 1
        self.column = 0
        self.input_stream = input_stream
    
    def __peek(self):
        """Returns next character keeping it in the stream"""
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol
    
    def __read(self):
        self.__add_to_corr(self.__peek())
        return self.input_stream.read(1)
    
    # returns the next token in the stream
    def next_token(self):
        symbol = self.__peek() # for efficiency purposes
        s = ""
        col = self.column
        line = self.line
        #EOS
        if symbol == "":
            if self.line != 1 and self.column != 0:
                self.line += 1
                self.column = 0
            return token.Token(token.EOS, "", self.line, self.column)
        #NEWLINE
        elif symbol == "\n":
            self.__read()
            return self.next_token()
        #SINGLE LINE COMMENTS  
        elif symbol == "#" :
            while (symbol != '\n' and symbol != ""):
                self.__read()
                symbol = self.__peek()
            return self.next_token()
        #WHITESPACE 
        elif symbol.isspace():  
            self.__read()        
            return self.next_token()   
        #STRINGVAL    
        elif symbol == "'" or symbol == '"':
            return self.__stringval(symbol)   
        #SIGNS
        elif self.__isSign() != 0:  
            goldNum = self.__isSign()
            s += symbol
            #COMPARISON
            if goldNum == 1:
                if symbol == '=':
                    #EQUAL
                    if self.__isSecondEqual():
                        s+= "="
                        errorNum = self.__isSign()
                        if errorNum == 4 or errorNum == 0: #() or not sign
                            return token.Token(token.EQUAL, s, line, col)
                        else:
                            raise error.MyPLError("unexpected symbol '" + self.__peek()+"'", self.line, self.column)
                    #ASSIGN
                    else:
                        #ERROR: more signs post '='
                        errorNum = self.__isSign()
                        if errorNum == 4 or errorNum == 0: #() or not sign
                            return token.Token(token.ASSIGN, s, line, col)
                        else:
                            raise error.MyPLError("unexpected symbol'" + self.__peek()+"'", self.line, self.column)
                elif symbol == '<':
                    #LESS_THAN_EQUAL
                    if self.__isSecondEqual():
                        s+= "="
                        errorNum = self.__isSign()
                        if errorNum == 4 or errorNum == 0: #() or not sign
                            return token.Token(token.LESS_THAN_EQUAL, s, line, col)
                        else:
                            raise error.MyPLError("unexpected symbol '" + self.__peek()+"'", self.line, self.column)
                    #LESS_THAN
                    else:
                        errorNum = self.__isSign()
                        if errorNum == 4 or errorNum == 0: #() or not sign
                            return token.Token(token.LESS_THAN, symbol, line, col)
                        else:
                            raise error.MyPLError("unexpected symbol '" + self.__peek()+"'", self.line, self.column)
                elif symbol == '>':
                    #GREATER_THAN_EQUAL
                    if self.__isSecondEqual():
                        s+= "="
                        errorNum = self.__isSign()
                        if errorNum == 4 or errorNum == 0: #() or not sign
                            return token.Token(token.GREATER_THAN_EQUAL, s, line, col)
                        else:
                            raise error.MyPLError("unexpected symbol '" + self.__peek()+"'", self.line, self.column)
                    #GREATER_THAN
                    else:
                        errorNum = self.__isSign()
                        if errorNum == 4 or errorNum == 0: #() or not sign
                            return token.Token(token.GREATER_THAN, symbol, line, col)
                        else:
                            raise error.MyPLError("unexpected symbol '" +self.__peek()+"'", self.line, self.column)
                #NOT_EQUAL
                else:
                    if self.__isSecondEqual():
                        s+= "="
                        return token.Token(token.NOT_EQUAL, s, line, col)
                    else:
                        raise error.MyPLError("unexpected symbol '" + self.__peek()+"'", self.line, self.column)
            #OPERATOR
            elif goldNum == 2:
                self.__read()
                #MINUS
                if symbol == '-':
                    return token.Token(token.MINUS, symbol, line, col)
                #MODULO
                elif symbol == '%':
                    return token.Token(token.MODULO, symbol, line, col)
                #MULTIPLY
                elif symbol == '*':
                    return token.Token(token.MULTIPLY, symbol, line, col)
                #PLUS
                elif symbol == '+':
                    return token.Token(token.PLUS, symbol, line, col)
                #DIVIDE
                else:
                    return token.Token(token.DIVIDE, symbol, line, col)
            #PUNCTUATION 
            elif goldNum == 3:
                self.__read()
                #COLON
                if symbol == ':':
                    return token.Token(token.COLON, symbol, line, col)
                #SEMICOLON
                elif symbol == ';':
                    return token.Token(token.SEMICOLON, symbol, line, col)
                #COMMA
                elif symbol == ',':
                    return token.Token(token.COMMA, symbol, line, col)
                #DOT
                else:
                    return token.Token(token.DOT, symbol, line, col)
            #PAREN
            else:
                self.__read()
                if symbol == "(":
                    return token.Token(token.LPAREN, symbol, line, col)
                else:
                    return token.Token(token.RPAREN, symbol, line, col)
        #NUMBER            
        elif symbol.isdigit():    
            s += self.__read()
            symbol=self.__peek()
            decFlag = False
            while self.__peek() not in ";,=+-*/%<>()" and not (self.__peek().isspace()):
                s += self.__read()
                symbol = self.__peek()
            if len(s)==3 and s =="0.0":
                return token.Token(token.FLOATVAL, s, line, col)
            for i in range(0,len(s)):
                if int(s[0]) == 0 :
                    if len(s) > 1 and s[1].isdigit():
                        raise error.MyPLError("unexpected symbol '" + s[1] + "'", line, col)
                    elif len(s) == 1:
                        return token.Token(token.INTVAL, s, line, col)
                elif s[i].isalpha():
                    raise error.MyPLError("unexpected symbol '" + s[i] + "'", line, col)
                elif s[i] == ".":
                    decFlag = True
                    if i+1 == len(s):
                        raise error.MyPLError("missing digit in float value ", line, col+i+1)
                    elif s[len(s)-1] == 0 and s != "0.0":
                        raise error.MyPLError("incorrect formatting '" + s + "'", line, col)
            if decFlag == True:
                return token.Token(token.FLOATVAL, s, line, col)
            else:
                return token.Token(token.INTVAL, s, line, col)
            '''decFlag = False
            symbol= self.__peek()
            while symbol != "" and symbol != "/n" and not symbol.isspace() and (symbol == "." or self.__isSign() == 0) and symbol != "#" :
                if self.__peek() == "." and decFlag:
                    raise error.MyPLError("Multiple decimal places", self.line, self.column)
                elif not self.__peek().isdigit() and self.__peek() != ".":
                    raise error.MyPLError('unexpected symbol "' + self.__peek() + '"', self.line, self.column)
                elif self.__peek() == "." and not decFlag:
                    if len(s) == 1 or (s[0] != "0" and len(s) > 1):
                        decFlag = True
                    else:
                        raise error.MyPLError("Invalid float", self.line, self.column)
                s += self.__read()
                symbol = self.__peek()
            for i in range(0,len(s)):
                if s[i] == "." and decFlag:
                    if len(s) == i+1:
                        raise error.MyPLError("incorrect formatting '" + s + "'", line, col)
                    else:
                        return token.Token(token.FLOATVAL, s, line, col)
                else:
                    if len(s) == 1:
                        return token.Token(token.INTVAL, s, line, col)
                    elif s[0] != "0" and len(s) > 1:
                        return token.Token(token.INTVAL, s, line, col)
                    else:
                        raise error.MyPLError("unexpected symbol '" + s[i] + "'", self.line, self.column-i)'''
        #LETTER    
        elif symbol.isalpha():    
            s+=self.__read()
            symbol= self.__peek()
            while symbol == "_" or symbol.isalpha() or symbol.isdigit():
                s += self.__read()
                symbol= self.__peek()
            length = len(s)
            if length == 2:
                if s == 'do':
                    return token.Token(token.DO, s, line, col)
                elif s == 'or':
                    return token.Token(token.OR, s, line, col)
                elif s == 'if':
                    return token.Token(token.IF, s, line, col)
                else:
                    return token.Token(token.ID, s, line, col)
            elif length == 3:
                if s == 'and':
                    return token.Token(token.AND, s, line, col)
                elif s == 'end':
                    return token.Token(token.END, s, line, col)
                elif s == 'fun':
                    return token.Token(token.FUN, s, line, col)
                elif s == 'int':
                    return token.Token(token.INTTYPE, s, line, col)
                elif s == 'new':
                    return token.Token(token.NEW, s, line, col)
                elif s == 'nil':
                    return token.Token(token.NIL, s, line, col)
                elif s == 'not':
                    return token.Token(token.NOT, s, line, col)
                elif s == 'set':
                    return token.Token(token.SET, s, line, col)
                elif s == 'var':
                    return token.Token(token.VAR, s, line, col)
                else:
                    return token.Token(token.ID, s, line, col)
            elif length == 4:
                if s == 'then':
                    return token.Token(token.THEN, s, line, col)
                elif s == 'elif':
                    return token.Token(token.ELIF, s, line, col)
                elif s == 'else':
                    return token.Token(token.ELSE, s, line, col)
                elif s == 'bool':
                    return token.Token(token.BOOLTYPE, s, line, col)
                elif s == 'true':
                    return token.Token(token.BOOLVAL, s, line, col)
                elif s == 'plus':
                    return token.Token(token.PLUS, s, line, col)
                else:
                    return token.Token(token.ID, s, line, col)
            elif length == 5:
                if s == 'false':
                    return token.Token(token.BOOLVAL, s, line, col)
                elif s == 'float':
                    return token.Token(token.FLOATTYPE, s, line, col)
                elif s == 'while':
                    return token.Token(token.WHILE, s, line, col)
                else:
                    return token.Token(token.ID, s, line, col)
            elif length == 6:
                if s == 'return':
                    return token.Token(token.RETURN, s, line, col)
                elif s == 'string':
                    return token.Token(token.STRINGTYPE, s, line, col)
                elif s == 'struct':
                    return token.Token(token.STRUCTTYPE, s, line, col)
                else:
                    return token.Token(token.ID, s, line, col)
            else:
                return token.Token(token.ID, s, line, col)
        else:
            raise error.MyPLError('unexpected symbol "' + symbol + '"', (
                self.line), self.column)
          
#------------------HELPER FUNCTIONS-----------------
    def __isSecondEqual(self):
        '''if next read symbol is equal it adjust line and column then returns true
        else it resets the stream to it's original position and returns false'''
        self.__read()
        if self.__peek() == "=":
            self.__read()
            return True
        else:
            return False
    
    def __isSign(self):
        '''Checks wheather the current symbol is either a = > < ! : , . ( ) - % * + /;
        returns 1 for "< > ! =" 
        returns 2 for "+ - * / %" 
        returns 3 for ": ; , ."
        returns 4 for "( )" 
        returns 0 otherwise'''
        sign = self.__peek()
        if sign == '=' or  sign == '>' or sign == '<' or sign == '!': 
            return 1
        elif sign == '-' or sign == '%' or sign == '*' or sign == '+' or sign == '/':
            return 2
        elif sign == ':' or sign == ';' or sign == ',' or sign == '.': 
            return 3
        elif sign == '(' or sign == ')':
            return 4
        else:
            return 0
            
    def __stringval(self, quote):
        ''' Creates a string to be returned as a token STRINGVAL '''
        s = ""
        col = self.column
        line = self.line
        self.__read()
        symbol = self.__peek()
        while symbol != quote:
            s+= self.__read()
            if symbol == "\n":
                raise error.MyPLError("reached newline reading string ", self.line, self.column)
            elif symbol == "":
                raise error.MyPLError("no accompaining " + quote, self.line, self.column)
            symbol = self.__peek()
        self.__read()
        return token.Token(token.STRINGVAL, s, line, col)
    
    def __add_to_corr(self, symbol):
        '''Adjusts the self.column and self.line accordingly to the symbol'''
        if symbol == "\n":
            self.column = 1
            self.line += 1
        else:
            self.column += 1         
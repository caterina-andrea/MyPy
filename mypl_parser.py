#!/usr/bin/python3
#
# Author: Caterina Valdovinos
# Description:
#   Parses through the source code
#----------------------------------------------------------------------
import mypl_error as error 
import mypl_lexer as lexer 
import mypl_token as token

class Parser(object):

    def __init__(self, lexer): 
        self.lexer = lexer 
        self.current_token = None

    def parse(self): 
        """succeeds if program is syntactically well-formed""" 
        self.__advance() 
        self.__stmts() 
        self.__eat(token.EOS, 'expecting end of file')
        
    def __advance(self): 
        self.current_token = self.lexer.next_token()
        
    def __eat(self, tokentype, error_msg): 
        if self.current_token.tokentype == tokentype: 
            self.__advance()
        else: 
            self.__error(error_msg)
            
    def __error(self, error_msg): 
        s = error_msg + ', found "' + self.current_token.lexeme + '" in parser' 
        l = self.current_token.line 
        c = self.current_token.column 
        raise error.MyPLError(s, l, c)
        
    # Beginning of recursive descent functions
    def __stmts(self): 
        """<stmts> ::= <stmt> <stmts> | e""" 
        if self.current_token.tokentype != token.EOS: 
            self.__stmt() 
            self.__stmts()
            
    def __stmt(self): 
        """<stmt> ::= <sdecl> | <fdecl> | <bstmt>""" 
        if self.current_token.tokentype == token.STRUCTTYPE: 
            self.__sdecl() 
        elif self.current_token.tokentype == token.FUN: 
            self.__fdecl() 
        else: 
            self.__bstmt()
            
    def __bstmts(self):
        '''<bstmts> ::= <bstmt> <bstmts> | e '''
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, 
        token.NEW, token.LPAREN, token.ID, token.RETURN, token.VAR, token.IF, token.WHILE]
        if self.current_token.tokentype in types:
            self.__bstmt()
            self.__bstmts()
        
    def __stmt(self):
        ''' <stmt>	::=	<sdecl> | <fdecl> | <bstmt> '''
        if self.current_token.tokentype == token.STRUCTTYPE:
            self.__sdecl()
        elif self.current_token.tokentype == token.FUN:
            self.__fdecl()
        else:
            self.__bstmt()
    
    def __bstmt(self):
        ''' <bstmt>	::=	<vdecl> | <assign> | <cond> | <while> | <expr> SEMICOLON | <exit> '''
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.LPAREN, token.ID] 
        if self.current_token.tokentype == token.VAR:
            self.__vdecl()
        elif self.current_token.tokentype == token.SET:
            self.__assign()
        elif self.current_token.tokentype == token.IF:
            self.__cond()
        elif self.current_token.tokentype == token.WHILE: 
            self.__while()
        elif self.current_token.tokentype in types:
            self.__expr()
            self.__eat(token.SEMICOLON, "expecting 'SEMICOLON'")
        else:
            self.__exit()
        
    def __sdecl(self):
        ''' <sdecl>	::=	STRUCT ID <vdecls> END '''
        self.__eat(token.STRUCTTYPE,"expecting 'STRUCTTYPE'")
        self.__eat(token.ID, "expecting 'ID'")
        self.__vdecls()
        self.__eat(token.END, "expecting 'END'")
    
    def __vdecls(self):
        ''' <vdecls> ::= <vdecl> <vdecls> | e '''
        if self.current_token.tokentype == token.VAR:
            self.__vdecl()
            self.__vdecls()
    
    def __fdecl(self):
        ''' <fdecl>	::= FUN ( <type> | NIL ) ID LPAREN <params> RPAREN <bstmts> END  '''
        self.__eat(token.FUN,"expecting 'FUN'")
        if self.current_token.tokentype == token.NIL:
            self.__advance()
        else:
            self.__type()
        self.__eat(token.ID, "expecting 'ID'")
        self.__eat(token.LPAREN, "expecting 'LPAREN'")
        self.__params()
        self.__eat(token.RPAREN, "expecting 'RPAREN'")
        self.__bstmts()
        self.__eat(token.END, "expecting 'END'")
    
    def __params(self):
        ''' <params> ::= ID COLON <type> ( COMMA ID COLON <type>)* | e '''
        if self.current_token.tokentype == token.ID:
            self.__advance()
            self.__eat(token.COLON, "expecting 'COLON'")
            self.__type()
            while self.current_token.tokentype == token.COMMA:
                self.__advance()
                self.__eat(token.ID, "expecting 'ID'")
                self.__eat(token.COLON, "expecting 'COLON'")
                self.__type()
    
    def __type(self):
        ''' <type>	::= ID | INTTYPE | FLOATTYPE | BOOLTYPE | STRINGTYPE '''
        if self.current_token.tokentype == token.ID:
            self.__advance()
        elif self.current_token.tokentype == token.INTTYPE:
            self.__advance()
        elif self.current_token.tokentype == token.FLOATTYPE:
            self.__advance()
        elif self.current_token.tokentype == token.BOOLTYPE:
            self.__advance()
        elif self.current_token.tokentype == token.STRINGTYPE:
            self.__advance()
        else:
            self.__error("expecting a type")
    
    def __exit(self):
        ''' <exit>	::= RETURN ( <expr> | e ) SEMICOLON '''
        self.__eat(token.RETURN,"expecting 'RETURN'")
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.LPAREN, token.ID] 
        if self.current_token.tokentype in types: 
            self.__expr()
        self.__eat(token.SEMICOLON, "expecting 'SEMICOLON'")
    
    def __vdecl(self):
        ''' <vdecl>	::= VAR ID <tdecl> ASSIGN <expr> SEMICOLON '''
        self.__eat(token.VAR,"expecting 'VAR'")
        self.__eat(token.ID, "expecting 'ID'")
        self.__tdecl()
        self.__eat(token.ASSIGN, "expecting 'ASSIGN'")
        self.__expr()
        self.__eat(token.SEMICOLON, "expecting 'SEMICOLON'")
    
    def __tdecl(self):
        ''' <tdecl>	::= COLON <type> | e '''
        if self.current_token.tokentype == token.COLON:
            self.__advance()
            self.__type()
    
    def __assign(self):
        ''' <assign> ::= SET <lvalue> ASSIGN <expr> SEMICOLON '''
        self.__eat(token.SET,"expecting 'SET'")
        self.__lvalue()
        self.__eat(token.ASSIGN, "expecting 'ASSIGN'")
        self.__expr()
        self.__eat(token.SEMICOLON, "expecting 'SEMICOLON'")
    
    def __lvalue(self):
        ''' <lvalue> ::= ID ( DOT ID )*'''
        self.__eat(token.ID, "expected 'ID'")
        while self.current_token.tokentype == token.DOT:
            self.__advance()
            self.__eat(token.ID, "expecting 'ID'")
    
    def __cond(self):
        ''' <cond> ::=	IF <bexpr> THEN <bstmts> <condt> END '''
        self.__eat(token.IF, "expecting 'IF'")
        self.__bexpr()
        self.__eat(token.THEN, "expecting 'THEN'")
        self.__bstmts()
        self.__condt()
        self.__eat(token.END, "expecting 'END'")
    
    def __condt(self):
        ''' <condt>	::= ELIF <bexpr> THEN <bstmts> <condt> | ELSE <bstmts> | e'''
        if self.current_token.tokentype == token.ELIF:
            self.__advance()
            self.__bexpr()
            self.__eat(token.THEN, "expecting 'THEN'")
            self.__bstmts()
            self.__condt()
        elif self.current_token.tokentype == token.ELSE:
            self.__advance()
            self.__bstmts()
    
    def __while(self):
        ''' <while>	::= WHILE <bexpr> DO <bstmts> END  '''
        if self.current_token.tokentype == token.WHILE: 
            self.__advance() 
            self.__bexpr() 
            self.__eat(token.DO, "expecting 'DO'")
            self.__bstmts()
            self.__eat(token.END, "expecting 'END'")
        else:
            self.__error("expecting 'WHILE'")
    
    def __expr(self):
        ''' <expr> ::= ( <rvalue> | LPAREN <expr> RPAREN ) ( <mathrel> <expr> | e ) '''
        mathrels = [token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO] 
        if self.current_token.tokentype == token.LPAREN: 
            self.__advance() 
            self.__expr() 
            self.__eat(token.RPAREN, "expecting ')'")
            if self.current_token.tokentype in mathrels: 
                self.__advance() 
                self.__expr()
        else: 
            self.__rvalue()
            if self.current_token.tokentype in mathrels: 
                self.__advance() 
                self.__expr()
        
    def __mathrel(self):
        ''' <mathrel> ::= PLUS | MINUS | DIVIDE | MULTIPLY | MODULO '''
        if self.current_token.tokentype == token.PLUS:
            self.__advance()
        elif self.current_token.tokentype == token.MINUS:
            self.__advance()
        elif self.current_token.tokentype == token.DIVIDE:
            self.__advance()
        elif self.current_token.tokentype == token.MULTIPLY:
            self.__advance()
        elif self.current_token.tokentype == token.MODULO:
            self.__advance()
        else:
            self.__error("expecting math operator")
    
    def __rvalue(self):
        ''' <rvalue> ::= STRINGVAL | INTVAL | BOOLVAL | FLOATVAL | NIL | NEW ID | <idrval> '''
        if self.current_token.tokentype == token.STRINGVAL:
            self.__advance()
        elif self.current_token.tokentype == token.INTVAL:
            self.__advance()
        elif self.current_token.tokentype == token.BOOLVAL:
            self.__advance()
        elif self.current_token.tokentype == token.FLOATVAL:
            self.__advance()
        elif self.current_token.tokentype == token.NIL:
            self.__advance()
        elif self.current_token.tokentype == token.NEW:
            self.__advance()
            self.__eat(token.ID, "expecting an 'ID'")
        else:
            self.__idrval()
    
    def __idrval(self):
        ''' <idrval> ::= ID ( DOT ID )* | ID LPAREN <exprlist> RPAREN '''
        self.__eat(token.ID, "expecting an 'ID'")
        if self.current_token.tokentype == token.LPAREN:
            self.__advance()
            self.__exprlist()
            self.__eat(token.RPAREN, "expecting a ')'")
        elif self.current_token.tokentype == token.DOT:
            while self.current_token.tokentype == token.DOT:
                self.__advance()
                self.__eat(token.ID, "expecting an 'ID'") 
                    
    def __exprlist (self):
        ''' <exprlist> ::= <expr> ( COMMA <expr> )* | e '''
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.LPAREN, token.ID] 
        if self.current_token.tokentype in types: 
            self.__expr() 
            while self.current_token.tokentype == token.COMMA: 
                self.__advance() 
                self.__expr()
    
    def __bexpr(self):
        ''' <bexpr>	::=	<expr> <bexprt> | NOT <bexpr> <bexprt> | LPAREN <bexpr> RPAREN <bconnct> '''
        if self.current_token.tokentype == token.NOT:
            self.__advance()
            self.__bexpr()
            self.__bexprt()
        elif self.current_token.tokentype == token.LPAREN:
            self.__advance()
            self.__bexpr()
            self.__eat(token.RPAREN, 'expected ")"')
            self.__bconnct()
        else:
            self.__expr()
            self.__bexprt()
    
    def __bexprt(self):
        ''' <bexprt> ::= <boolrel> <expr> <bconnct> | <bconnct> '''
        boolrel = [token.EQUAL, token.LESS_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN, token.GREATER_THAN_EQUAL, token.NOT_EQUAL]
        if self.current_token.tokentype in boolrel:
            self.__boolrel()
            self.__expr()
        self.__bconnct()
        
    def __bconnct(self):
        ''' <bconnct> ::= AND <bexpr> | OR <bexpr> | e '''
        if self.current_token.tokentype == token.AND:
            self.__advance()
            self.__bexpr()
        elif self.current_token.tokentype == token.OR:
            self.__advance()
            self.__bexpr()
            
    def __boolrel(self):
        ''' <boolrel> ::= EQUAL | LESS_THAN | GREATER_THAN | LESS_THAN_EQUAL | GREATER_THAN_EQUAL | NOT_EQUAL '''
        if self.current_token.tokentype == token.EQUAL:
            self.__advance()
        elif self.current_token.tokentype == token.LESS_THAN:
            self.__advance()
        elif self.current_token.tokentype == token.LESS_THAN_EQUAL:
            self.__advance()
        elif self.current_token.tokentype == token.GREATER_THAN:
            self.__advance()
        elif self.current_token.tokentype == token.GREATER_THAN_EQUAL:
            self.__advance()
        elif self.current_token.tokentype == token.NOT_EQUAL:
            self.__advance()
        else:
            self.__error("expecting comparison boolean")
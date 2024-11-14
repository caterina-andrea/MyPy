#!/usr/bin/python3
#
# Author: Caterina Valdovinos
# Description:
#   Parses through the source code
#----------------------------------------------------------------------
import mypl_error as error 
import mypl_lexer as lexer 
import mypl_token as token
import mypl_ast as ast 

class Parser(object):

    def __init__(self, lexer): 
        self.lexer = lexer 
        self.current_token = None

    def parse(self): 
        """succeeds if program is syntactically well-formed""" 
        stmt_list_node = ast.StmtList()
        self.__advance() 
        self.__stmts(stmt_list_node) 
        self.__eat(token.EOS, 'expecting end of file')
        return stmt_list_node
        
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
    def __stmts(self, stmt_list_node): 
        """<stmts> ::= <stmt> <stmts> | e""" 
        if self.current_token.tokentype != token.EOS: 
            self.__stmt(stmt_list_node) 
            self.__stmts(stmt_list_node)
            
    def __bstmts(self, stmt_list):
        '''<bstmts> ::= <bstmt> <bstmts> | e '''
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, 
        token.NEW, token.LPAREN, token.ID, token.RETURN, token.VAR,token.SET, token.IF, token.WHILE]
        if self.current_token.tokentype in types:
            stmt_list.stmts.append(self.__bstmt())
            self.__bstmts(stmt_list)
        
    def __stmt(self, stmt_list_node): 
        """<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
        if self.current_token.tokentype == token.STRUCTTYPE: 
            self.__sdecl(stmt_list_node) 
        elif self.current_token.tokentype == token.FUN: 
            self.__fdecl(stmt_list_node) 
        else: 
            stmt_list_node.stmts.append(self.__bstmt())
    
    def __bstmt(self):
        ''' <bstmt>	::=	<vdecl> | <assign> | <cond> | <while> | <expr> SEMICOLON | <exit> '''
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.LPAREN, token.ID] 
        if self.current_token.tokentype == token.VAR:
            stmt = self.__vdecl()
        elif self.current_token.tokentype == token.SET:
            stmt = self.__assign()
        elif self.current_token.tokentype == token.IF:
            stmt = self.__cond()
        elif self.current_token.tokentype == token.WHILE: 
            stmt = self.__while()
        elif self.current_token.tokentype in types:
            expr_stmt = ast.ExprStmt()
            expr_stmt.expr = self.__expr()
            stmt = expr_stmt
            self.__eat(token.SEMICOLON, "expecting 'SEMICOLON'")
        else:
            stmt = self.__exit()
        return stmt
        
    def __sdecl(self, stmt_list_node):
        ''' <sdecl>	::=	STRUCT ID <vdecls> END '''
        self.__eat(token.STRUCTTYPE,"expecting 'STRUCTTYPE'")
        #Declare StructDeclStmt
        struct_decl_stmt = ast.StructDeclStmt()
        struct_decl_stmt.struct_id = self.current_token
        self.__eat(token.ID, "expecting 'ID'")
        var_decls = []
        if self.current_token.tokentype == token.VAR:
            self.__vdecls(var_decls)
            struct_decl_stmt.var_decls = var_decls
        self.__eat(token.END, "expecting 'END'")
        #add to the stmt_list_node
        stmt_list_node.stmts.append(struct_decl_stmt)
    
    def __vdecls(self, var_decls):
        ''' <vdecls> ::= <vdecl> <vdecls> | e '''
        if self.current_token.tokentype == token.VAR:
            var_decls.append(self.__vdecl())
            self.__vdecls(var_decls)
        
    def __fdecl(self, stmt_list_node):
        ''' <fdecl>	::= FUN ( <type> | NIL ) ID LPAREN <params> RPAREN <bstmts> END  '''
        fun_decl_stmt = ast.FunDeclStmt()
        self.__eat(token.FUN,"expecting 'FUN'")
        if self.current_token.tokentype == token.NIL:
            fun_decl_stmt.return_type = self.current_token
            self.__advance()
        else:
            fun_decl_stmt.return_type = self.__type()
        fun_decl_stmt.fun_name = self.current_token
        self.__eat(token.ID, "expecting 'ID'")
        self.__eat(token.LPAREN, "expecting 'LPAREN'")
        fun_decl_stmt.params = self.__params()
        self.__eat(token.RPAREN, "expecting 'RPAREN'")
        stmt_list = ast.StmtList()
        self.__bstmts(stmt_list)
        fun_decl_stmt.stmt_list = stmt_list
        self.__eat(token.END, "expecting 'END'")
        stmt_list_node.stmts.append(fun_decl_stmt)
    
    def __params(self):
        ''' <params> ::= ID COLON <type> ( COMMA ID COLON <type>)* | e '''
        fun_param_list = []
        fun_param = ast.FunParam()
        fun_param.param_name = self.current_token
        if self.current_token.tokentype == token.ID:
            self.__advance()
            self.__eat(token.COLON, "expecting 'COLON'")
            fun_param.param_type = self.__type()
            fun_param_list.append(fun_param)
            while self.current_token.tokentype == token.COMMA:
                self.__advance()
                fun_param2 = ast.FunParam()
                fun_param2.param_name = self.current_token
                self.__eat(token.ID, "expecting 'ID'")
                self.__eat(token.COLON, "expecting 'COLON'")
                fun_param2.param_type = self.__type()
                fun_param_list.append(fun_param2)
        return fun_param_list
    
    def __type(self):
        ''' <type>	::= ID | INTTYPE | FLOATTYPE | BOOLTYPE | STRINGTYPE '''
        type = [token.ID,token.INTTYPE,token.FLOATTYPE,token.BOOLTYPE,token.STRINGTYPE]
        if self.current_token.tokentype in type:
            curr = self.current_token
            self.__advance()
            return curr
        else:
            self.__error("expecting a type")
    
    def __exit(self):
        ''' <exit>	::= RETURN ( <expr> | e ) SEMICOLON '''
        return_stmt = ast.ReturnStmt()
        return_stmt.return_token = self.current_token
        self.__eat(token.RETURN,"expecting 'RETURN'")
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.LPAREN, token.ID] 
        if self.current_token.tokentype in types: 
            return_stmt.return_expr = self.__expr()
        self.__eat(token.SEMICOLON, "expecting 'SEMICOLON'")
        return return_stmt
    
    def __vdecl(self):
        ''' <vdecl>	::= VAR ID <tdecl> ASSIGN <expr> SEMICOLON '''
        var_decl_stmt = ast.VarDeclStmt()
        self.__eat(token.VAR,"expecting 'VAR'")
        var_decl_stmt.var_id = self.current_token
        self.__eat(token.ID, "expecting 'ID'")
        var_decl_stmt.var_type = self.__tdecl()
        self.__eat(token.ASSIGN, "expecting 'ASSIGN'")
        var_decl_stmt.var_expr = self.__expr()
        self.__eat(token.SEMICOLON, "expecting 'SEMICOLON'")
        return var_decl_stmt
    
    def __tdecl(self):
        ''' <tdecl>	::= COLON <type> | e '''
        if self.current_token.tokentype == token.COLON:
            self.__advance()
            type = self.__type()
            return type
            
    def __assign(self):
        ''' <assign> ::= SET <lvalue> ASSIGN <expr> SEMICOLON '''
        self.__eat(token.SET,"expecting 'SET'")
        assign_stmt = ast.AssignStmt()
        assign_stmt.lhs = self.__lvalue()
        self.__eat(token.ASSIGN, "expecting 'ASSIGN'")
        assign_stmt.rhs = self.__expr()
        self.__eat(token.SEMICOLON, "expecting 'SEMICOLON'")
        return assign_stmt
    
    def __lvalue(self):
        ''' <lvalue> ::= ID ( DOT ID )*'''
        lvalue = ast.LValue()
        lvalue.path.append(self.current_token)
        self.__eat(token.ID, "expected 'ID'")
        while self.current_token.tokentype == token.DOT:
            self.__advance()
            lvalue.path.append(self.current_token)
            self.__eat(token.ID, "expecting 'ID'")
        return lvalue
    
    def __cond(self):
        ''' <cond> ::=	IF <bexpr> THEN <bstmts> <condt> END '''
        #BasicIf declaration
        basic_if = ast.BasicIf()
        self.__eat(token.IF, "expecting 'IF'")
        basic_if.bool_expr = self.__bexpr()
        self.__eat(token.THEN, "expecting 'THEN'")
        #StmtList for BasicIf
        stmt_list_node = ast.StmtList()
        self.__bstmts(stmt_list_node)
        basic_if.stmt_list = stmt_list_node
        #IfStmt declaration
        if_stmt = ast.IfStmt()
        if_stmt.if_part = basic_if
        self.__condt(if_stmt)
        self.__eat(token.END, "expecting 'END'")
        return if_stmt
    
    def __condt(self, if_stmt):
        ''' <condt>	::= ELIF <bexpr> THEN <bstmts> <condt> | ELSE <bstmts> | e'''
        if self.current_token.tokentype == token.ELIF:
            self.__advance()
            #BasicIf declaration
            basic_if = ast.BasicIf()
            basic_if.bool_expr = self.__bexpr()
            self.__eat(token.THEN, "expecting 'THEN'")
            #StmtList for BasicIf
            stmt_list_node = ast.StmtList()
            self.__bstmts(stmt_list_node)
            basic_if.stmt_list = stmt_list_node
            if_stmt.elseifs.append(basic_if)
            self.__condt(if_stmt)
        elif self.current_token.tokentype == token.ELSE:
            if_stmt.has_else = True
            self.__advance()
            #StmtList for else
            stmt_list_node = ast.StmtList()
            self.__bstmts(stmt_list_node)
            if_stmt.else_stmts = stmt_list_node
    
    def __while(self):
        ''' <while>	::= WHILE <bexpr> DO <bstmts> END  '''
        if self.current_token.tokentype == token.WHILE: 
            while_stmt =  ast.WhileStmt()
            self.__advance() 
            while_stmt.bool_expr = self.__bexpr() 
            self.__eat(token.DO, "expecting 'DO'")
            stmt_list_node = ast.StmtList()
            self.__bstmts(stmt_list_node)
            while_stmt.stmt_list = stmt_list_node
            self.__eat(token.END, "expecting 'END'")
            return while_stmt
        else:
            self.__error("expecting 'WHILE'")
    
    def __expr(self):
        ''' <expr> ::= ( <rvalue> | LPAREN <expr> RPAREN ) ( <mathrel> <expr> | e ) '''
        #ComplexExpr declaration
        complex_expr = ast.ComplexExpr()    
        if self.current_token.tokentype == token.LPAREN: 
            self.__advance() 
            complex_expr.first_operand = self.__expr() 
            self.__eat(token.RPAREN, 'expecting ")"')
        else: 
            complex_expr.first_operand = self.__rvalue() 
        mathrels = [token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO] 
        if self.current_token.tokentype in mathrels: 
            complex_expr.math_rel = self.current_token
            self.__advance()
            complex_expr.rest = self.__expr()
            return complex_expr
        else: 
            #SimpleExpr declaration
            simple_expr = ast.SimpleExpr()
            simple_expr.term = complex_expr.first_operand
            return simple_expr
            
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
        rvals = [token.STRINGVAL,token.INTVAL,token.BOOLVAL,token.FLOATVAL,token.NIL]
        if self.current_token.tokentype in rvals:
            #SimpleRValue declaration
            simple_rvalue = ast.SimpleRValue()
            simple_rvalue.val = self.current_token
            self.__advance()
            return simple_rvalue
        elif self.current_token.tokentype == token.NEW:
            #NewRvalue declaration
            new_rvalue = ast.NewRValue() 
            self.__advance()
            new_rvalue.struct_type = self.current_token
            self.__eat(token.ID, "expecting an 'ID'")
            return new_rvalue
        else:
            return self.__idrval()
    
    def __idrval(self):
        ''' <idrval> ::= ID ( DOT ID )* | ID LPAREN <exprlist> RPAREN '''
        #SimpleRValue declared
        simple_rvalue = ast.SimpleRValue()
        simple_rvalue.val = self.current_token
        self.__eat(token.ID, "expecting an 'ID'")
        if self.current_token.tokentype == token.LPAREN:
            #CallRvalue declared
            call_rvalue = ast.CallRValue()
            call_rvalue.fun = simple_rvalue.val
            self.__advance()
            call_rvalue.args = self.__exprlist()
            self.__eat(token.RPAREN, "expecting a ')'")
            #CallRValue returned
            return call_rvalue
        elif self.current_token.tokentype == token.DOT:
            #IDRvalue declared
            id_rvalue = ast.IDRvalue()
            id_rvalue.path.append(simple_rvalue.val)
            while self.current_token.tokentype == token.DOT:
                self.__advance()
                id_rvalue.path.append(self.current_token)
                self.__eat(token.ID, "expecting an 'ID'")
            #IDRvalue returned        
            return id_rvalue 
        #SimpleRValue returned
        return simple_rvalue
        
    def __exprlist (self):
        ''' <exprlist> ::= <expr> ( COMMA <expr> )* | e '''
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.LPAREN, token.ID] 
        exprlist = []
        if self.current_token.tokentype in types: 
            exprlist.append(self.__expr())
            while self.current_token.tokentype == token.COMMA: 
                self.__advance() 
                exprlist.append(self.__expr())
        return exprlist
    
    def __bexpr(self):
        ''' <bexpr>	::=	<expr> <bexprt> | NOT <bexpr> <bexprt> | LPAREN <bexpr> RPAREN <bconnct> '''
        bool_expr = ast.BoolExpr()
        if self.current_token.tokentype == token.NOT:
            bool_expr.negated = True
            self.__advance()
            bool_expr.first_expr = self.__bexpr()
            self.__bexprt(bool_expr)
        elif self.current_token.tokentype == token.LPAREN:
            self.__advance()
            bool_expr.first_expr = self.__bexpr()
            self.__eat(token.RPAREN, 'expected ")"')
            self.__bconnct(bool_expr)
        else:
            bool_expr.first_expr = self.__expr()
            self.__bexprt(bool_expr)
        return bool_expr
    
    def __bexprt(self, bool_expr):
        ''' <bexprt> ::= <boolrel> <expr> <bconnct> | <bconnct> '''
        boolrel = [token.EQUAL, token.LESS_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN, token.GREATER_THAN_EQUAL, token.NOT_EQUAL]
        if self.current_token.tokentype in boolrel:
            self.__boolrel(bool_expr)
            bool_expr.second_expr = self.__expr()
        self.__bconnct(bool_expr)
        
    def __bconnct(self, bool_expr):
        ''' <bconnct> ::= AND <bexpr> | OR <bexpr> | e '''
        if self.current_token.tokentype == token.AND:
            bool_expr.bool_connector = self.current_token
            self.__advance()
            bool_expr.rest = self.__bexpr()
        elif self.current_token.tokentype == token.OR:
            bool_expr.bool_connector = self.current_token
            self.__advance()
            bool_expr.rest = self.__bexpr()
            
    def __boolrel(self, bool_expr):
        ''' <boolrel> ::= EQUAL | LESS_THAN | GREATER_THAN | LESS_THAN_EQUAL | GREATER_THAN_EQUAL | NOT_EQUAL '''
        boolrel = [token.EQUAL,token.LESS_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN, token.GREATER_THAN_EQUAL, token.NOT_EQUAL]
        if self.current_token.tokentype in boolrel:
            bool_expr.bool_rel = self.current_token
            self.__advance()
        else:
            self.__error("expecting comparison boolean")
#!/usr/bin/python3
#
# Author: Caterina Valdovinos
# Description:
#   "Pretty prints" the source code
#----------------------------------------------------------------------
import mypl_token as token 
import mypl_ast as ast

class PrintVisitor(ast.Visitor): 
    """An AST pretty printer"""

    def __init__(self, output_stream): 
        self.indent = 0                             # to increase/decrease indent level 
        self.output_stream = output_stream          # where printing to

    def __indent(self): 
        """Get default indent of four spaces""" 
        return '    ' * self.indent

    def __write(self, msg): 
        self.output_stream.write(msg)

    def visit_stmt_list(self, stmt_list): 
        """Accepts the list of statements in the statement list""" 
        for stmt in stmt_list.stmts: 
            stmt.accept(self)

    def visit_expr_stmt(self, expr_stmt):
        """Accepts an expression then writes a newline"""
        self.checkIfNoneAccept(expr_stmt.expr)
        self.__write(';\n')
    
    def visit_var_decl_stmt(self, var_decl):
        """Indents, writes 'var', writes var_id, if var type doesnt equal 
        none writes ':' and the var_type, writes '=' accepts the expression, 
        and finally writes a newline"""
        self.printIndent()
        self.__write("var " )
        self.checkIfNoneWrite(var_decl.var_id)
        if var_decl.var_type != None:
            self.__write(": ")
            self.checkIfNoneWrite(var_decl.var_type)
        self.__write(" = ")
        self.checkIfNoneAccept(var_decl.var_expr)
        self.__write(';\n')

    def visit_assign_stmt(self, assign_stmt):
        '''Indents, writes 'set', accepts the lhs, writes '=', accepts rhs, writes 
        ';', and writes a newline '''
        self.printIndent()
        self.__write('set ')
        self.checkIfNoneAccept(assign_stmt.lhs)
        self.__write(' = ')
        self.checkIfNoneAccept(assign_stmt.rhs)
        self.__write(';\n')
    
    def visit_struct_decl_stmt(self, struct_decl):
        '''Indents, writes newline, writes struct, writes struct_id, writes newline, 
        accepts args, indents, writes 'end', and two newlines'''
        self.printIndent()
        self.__write('\nstruct ')
        self.checkIfNoneWrite(struct_decl.struct_id)
        self.__write('\n')
        self.indent += 1
        i = 0
        while i < len(struct_decl.var_decls):
            struct_decl.var_decls[i].accept(self)
            i += 1
        self.indent -= 1
        self.printIndent()
        self.__write('end\n\n')
    
    def visit_fun_decl_stmt(self, fun_decl):
        '''Indents, writes:(newline, 'fun', return_type, ' ', fun_decl name, '('), 
        accepts fun_decl params, accepts stmt_list, writes 'end', and two newlines '''
        self.printIndent()
        self.__write('\nfun ')
        self.checkIfNoneWrite(fun_decl.return_type)
        self.__write(' ')
        self.checkIfNoneWrite(fun_decl.fun_name)
        self.__write('(')
        self.indent += 1
        i = 0 
        while i + 1 < len(fun_decl.params):
            self.checkIfNoneAccept(fun_decl.params[i])
            self.__write(', ')
            i += 1
        self.checkIfNoneAccept(fun_decl.params[i])    
        self.indent -= 1
        self.__write(')\n')
        self.indent += 1
        self.checkIfNoneAccept(fun_decl.stmt_list)
        self.indent -= 1
        self.__write('end\n\n')
    
    def visit_return_stmt(self, return_stmt):
        '''Indents, writes return_token, accepts return_expr, writes ';', writes newline'''
        self.printIndent()
        self.__write(str(return_stmt.return_token.lexeme))
        if return_stmt.return_expr != None:
            self.__write(' ')
            self.checkIfNoneAccept(return_stmt.return_expr)
        self.__write(';\n')
        
    def visit_while_stmt(self, while_stmt):
        '''Indents, writes 'while', accepts bool_expr, writes do and newline, accept 
        stmt_list, indents, writes 'end' and newline'''
        self.printIndent()
        self.__write('while ')
        self.checkIfNoneAccept(while_stmt.bool_expr)
        self.__write(' do\n')
        self.indent += 1
        self.checkIfNoneAccept(while_stmt.stmt_list)
        self.indent -= 1
        self.printIndent()
        self.__write('end\n')
        
    def visit_if_stmt(self, if_stmt):
        '''Indents, writes 'if', accepts if_part.bool_expr, writes 'then', accepts 
        if_part.stmt_list, goes through if_stmt.elseifs, if else indents, write 'else' and 
        newline, and accepts else_stmts, indents, and writes indent and newline'''
        self.printIndent()
        self.__write('if ')
        self.checkIfNoneAccept(if_stmt.if_part.bool_expr)
        self.__write(' then \n')
        self.indent += 1
        self.checkIfNoneAccept(if_stmt.if_part.stmt_list)
        for elseif in if_stmt.elseifs:
            self.indent -= 1
            self.printIndent()
            self.__write('elif ')
            self.checkIfNoneAccept(elseif.bool_expr)
            self.__write(' then\n')
            self.indent += 1
            self.checkIfNoneAccept(elseif.stmt_list)
        if if_stmt.has_else:
            self.indent -= 1
            self.printIndent()
            self.__write('else\n')
            self.indent += 1
            self.checkIfNoneAccept(if_stmt.else_stmts)
        self.indent -= 1
        self.printIndent()
        self.__write('end\n')

    def visit_simple_expr(self, simple_expr):
        '''Accepts simple_expr term'''
        self.checkIfNoneAccept(simple_expr.term)
        
    def visit_complex_expr(self, complex_expr):
        '''Writes '(', accepts first_operand, write ' ', writes math_rel, writes ' ',accepts
        complex_expr rest, and writes ')' '''
        self.__write('(')
        self.checkIfNoneAccept(complex_expr.first_operand)
        self.__write(' ')
        self.checkIfNoneWrite(complex_expr.math_rel)
        self.__write(' ')
        self.checkIfNoneAccept(complex_expr.rest)
        self.__write(')')
        
    def visit_bool_expr(self, bool_expr):
        '''if the bool_expr is negated writes 'not', if second_expr is None write '(', if 
        bool_connector write '(', accepts first_expr, if second_expr is not equal to None then
        [writes:(' ',bool_rel,' ')], if bool_connector then [writes:( ' ',bool_connector,
        ' '),accepts  rest, and writes ')' ]'''
        if bool_expr.negated:
            self.__write("not ")
        if bool_expr.second_expr != None:
            self.__write('(')
        if bool_expr.bool_connector != None:
            self.__write('(')
        bool_expr.first_expr.accept(self)
        if bool_expr.second_expr != None:
            self.__write(" ")
            self.checkIfNoneWrite(bool_expr.bool_rel)
            self.__write(" ")
            self.checkIfNoneAccept(bool_expr.second_expr)
            self.__write(")")
        if bool_expr.bool_connector:
            self.__write(" ")
            self.checkIfNoneWrite(bool_expr.bool_connector)
            self.__write(" ")
            self.checkIfNoneAccept(bool_expr.rest)
            self.__write(")")
    
    def visit_lvalue(self, lval):
        '''Writes lval path'''
        i = 0 
        while lval.path[i] != lval.path[-1]:
            self.__write(str(lval.path[i].lexeme))
            self.__write('.')
            i += 1
        self.__write(str(lval.path[i].lexeme))
    
    def visit_fun_param(self, fun_param):
        '''Writes param_name, ':', and param_type'''
        self.checkIfNoneWrite(fun_param.param_name)
        self.__write(': ')
        self.checkIfNoneWrite(fun_param.param_type)
    
    def visit_simple_rvalue(self, simple_rvalue):
        '''Writes simple_rvalue val'''
        self.checkIfNoneWrite(simple_rvalue.val)
        
    def visit_new_rvalue(self, new_rvalue):
        '''Indents, writes 'new', and writes struct_type'''
        self.printIndent()
        self.__write('new ')
        self.checkIfNoneWrite(new_rvalue.struct_type)
        
    def visit_call_rvalue(self, call_rvalue):
        '''Indents, writes fun, writes '(', accepts args, writes ')' ''' 
        self.printIndent()
        self.checkIfNoneWrite(call_rvalue.fun)
        self.__write('(')
        curr_indent = self.indent
        self.indent = 0
        i = 0
        while i < len(call_rvalue.args):
            self.printIndent()
            call_rvalue.args[i].accept(self)
            i += 1
        self.__write(')')
        self.indent = curr_indent
        
    def visit_id_rvalue(self, id_rvalue):
        '''Writes the path'''
        i = 0 
        while id_rvalue.path[i] != id_rvalue.path[-1]:
            self.checkIfNoneWrite(id_rvalue.path[i])
            self.__write('.')
            i += 1
        self.checkIfNoneWrite(id_rvalue.path[i])

    '''HELPER FUNCTIONS'''
        
    def checkIfNoneWrite(self, visitingNode):
        '''if the visitingNode is not None type then, if the visitingNode is a string 
        prints quotes before and after the lexeme else just prints the lexeme'''
        if visitingNode != None:
            if str(visitingNode.tokentype) == "STRINGVAL":
                self.__write('"')
                self.__write(str(visitingNode.lexeme))
                self.__write('"')
            else:
                self.__write(str(visitingNode.lexeme))
            
    def checkIfNoneAccept(self, visitingNode):
        '''if the visitingNode is not None type then accepts it'''
        if visitingNode != None:
            visitingNode.accept(self) 

    def printIndent(self):
        '''sends the output_stream the proper indent'''
        self.output_stream.write('    ' * self.indent)
#!/usr/bin/python3
#
# Author: Caterina Valdovinos
# Description:
#   Takes a source file written in MyPL and output the set of tokens 
#	in the file
#----------------------------------------------------------------------

import mypl_token as token 
import mypl_lexer as lexer 
import mypl_error as error 
import sys

def main(filename):
    try:
        file_stream = open(filename, 'r') 
        my_py(file_stream) 
        file_stream.close()
    except FileNotFoundError: 
        sys.exit('invalid filename %s' % filename)
    except error.MyPLError as e: 
        file_stream.close() 
        sys.exit(e)
        
def my_py(file_stream):
    try :
        the_lexer = lexer.Lexer(file_stream)
        the_token = the_lexer.next_token()
        while the_token.tokentype != token.EOS: 
            print(the_token)
            the_token = the_lexer.next_token()
        print(the_token)
    except error.MyPLError as e:
        print(e)
        sys.exit(1)
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: %s file' % sys.argv[0]) 
    main(sys.argv[1])
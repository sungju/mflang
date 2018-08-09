#!/usr/bin/env python
'''
mflang : mflang interpreter

Daniel Sungju Kwon
'''

# Let's make a compiler that understand the examples in the below link first.
#
# https://www.win.tue.nl/~aeb/tex/mf/metafont.html

from __future__ import print_function

import sys
import os
import logging

if sys.version_info[0] >= 3:
    raw_input = input

import ply.lex as lex
import ply.yacc as yacc
from ply.lex import TOKEN
import os
import re
import base64

from metablock import MetafontChar
from metablock import MetafontDef


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

INTERNAL_FUNC_NAME = "__mfc_generated_function_name__"

prog_path = ""

class Parser(object):
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()
    arguments = None

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = {}
        self.names["pt#"] = 1000
        self.names["u#"] = 500


        self.arguments = list()
        try:
            modname = os.path.split(os.path.splitext(__file__)[0]) [
                1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__

        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"

        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def run_block(self, block_string):
        print(block_string)
        result = yacc.parse(block_string)
        print("done")
        print(self.arguments)
        return result, self.arguments

    def run(self, filename):
       print("This is 'mflang' version 0.1")
       if filename is not None:
            try:
                prog_command = "python %s/mflang_prep.py %s" % \
                                (prog_path, filename)
                file_lines = os.popen(prog_command).read()
                yacc.parse(file_lines)
            except:
                pass

            return

       while 1:
            try:
                s = raw_input('** ')
                s = s + "\n"
            except EOFError:
                break
            if not s:
                continue
            yacc.parse(s)


class Metafont(Parser):
    def func_print(self, func_name, arg_list, obj):
        print(func_name)
        print(arg_list)


    char_list = { }
    current_char = None

    def func_beginchar(self, func_name, arg_list, obj):
        if len(arg_list) == 0:
            return

        encoded_value = arg_list[0][1:-1]
        obj.current_char = MetafontChar(base64.b64decode(encoded_value).decode("utf-8"))

        my_yacc = Metafont()

        result, arguments = my_yacc.run_block(obj.current_char.get_definition())
        print(arguments)


    def func_endchar(self, func_name, arg_list, obj):
        if obj.current_char == None:
            return

        if len(arg_list) == 0:
            return

        encoded_value = arg_list[0][1:-1]
        obj.current_char.set_body(base64.b64decode(encoded_value).decode("utf-8"))
        print(obj.current_char.get_definition())
        self.char_list[obj.current_char.get_definition()] = obj.current_char

        print(obj.current_char.get_body())
        my_yacc = Metafont()

        result, arguments = my_yacc.run_block(obj.current_char.get_body())
        print(arguments)

        obj.current_char = None


    def_list = { }
    current_def = None

    def func_def(self, func_name, arg_list, obj):
        if len(arg_list) == 0:
            return

        encoded_value = arg_list[0][1:-1]
        obj.current_def = MetafontDef(base64.b64decode(encoded_value).decode("utf-8"))
        my_yacc = Metafont()

        result, arguments = my_yacc.run_block(obj.current_def.get_definition())
        obj.current_def.set_func_name(my_yacc.last_func_name)
        obj.current_def.set_func_args(arguments)
        print(func_name)
        print(my_yacc.last_func_name)
        print(arguments)


    def func_enddef(self, func_name, arg_list, obj):
        if obj.current_def == None:
            return

        if len(arg_list) == 0:
            return

        encoded_value = arg_list[0][1:-1]
        obj.current_def.set_body(base64.b64decode(encoded_value).decode("utf-8"))
        print(obj.current_def.get_func_name())
        self.def_list[obj.current_def.get_func_name()] = obj.current_def

        my_yacc = Metafont()

        result, arguments = my_yacc.run_block(obj.current_def.get_body())
        print("func_enddef result")
        print(arguments)
        obj.current_def = None


    function_list = { }

    def __init__(self):
        self.function_list["def%s" % INTERNAL_FUNC_NAME] = self.func_def
        self.function_list["enddef%s" % INTERNAL_FUNC_NAME] = self.func_enddef
        self.function_list["beginchar%s" % INTERNAL_FUNC_NAME] = self.func_beginchar
        self.function_list["endchar%s" % INTERNAL_FUNC_NAME] = self.func_endchar
        Parser.__init__(self)

    reserved = {
        'xscaled' : 'XSCALED',
        'yscaled' : 'YSCALED',
        'rotated' : 'ROTATED',
        'pencircle' : 'PENCIRCLE',
        'dir' : 'DIR',
        'end' : 'END',
        'bye' : 'BYE',
    }

    tokens = [
        'ID',

        # Operators
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EXP',

        # Assignment
        'EQUALS',

        # List
        'RANGE',            # ..

        # Delimeters
        'LPAREN', 'RPAREN',     # ( )
        'LBRACE', 'RBRACE',      # { }
        'COMMA', 'PERIOD',      # . ,
        'SEMI', 'COLON',        # ; :

        # Numbers
        'INTEGER', 'FLOAT',     # Integer, Float

        # String literals
        'STRING_LITERAL',
        'WSTRING_LITERAL',

        'COMMENT',              # Comment '%'
    ] + list(reserved.values())

    # regex for tokens
    identifier = r'[a-zA-Z_$][0-9a-zA-Z_$]*[#]?'

    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")


    t_INTEGER = r'\d+'
    t_FLOAT = r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'

    # Operators
    t_PLUS                  = r'\+'
    t_MINUS                 = r'-'
    t_TIMES                 = r'\*'
    t_DIVIDE                = r'/'
    t_EXP                   = r'\*\*'

    # Assignment
    t_EQUALS                = r'[:]?='

    # Delimeters
    t_LPAREN                = r'\('
    t_RPAREN                = r'\)'
    t_LBRACE                = r'\{'
    t_RBRACE                = r'\}'
    t_COMMA                 = r','
    t_PERIOD                = r'\.'
    t_SEMI                  = r';'
    t_COLON                 = r':'
    t_RANGE                 = r'\.\.'

    simple_escape = r"""([a-zA-Z._~!=&\^\-\\?'"])"""
    decimal_escape = r"""(\d+)"""
    hex_escape = r"""(x[0-9a-fA-F]+)"""
    bad_escape = r"""([\\][^a-zA-Z._~^!=&\^\-\\?'"x0-7])"""

    escape_sequence = r"""(\\("""+simple_escape+'|'+decimal_escape+'|'+hex_escape+'))'

    string_char = r"""([^"\\\n]|"""+escape_sequence+')'
    string_literal = '"'+string_char+'*"'
    wstring_literal = 'L'+string_literal
    bad_string_literal = '"'+string_char+'*?'+bad_escape+string_char+'*"'

    t_STRING_LITERAL = string_literal

    @TOKEN(identifier)
    def t_ID(self, t):
        t.type = self.reserved.get(t.value, "ID")
        return t

    def t_COMMENT(self, t):
        r"\%.*\n"
        pass


    def t_error(self, t):
        print('Illegal character %s' % t.value[0])
        t.lexer.skip(1)


    # Parsing rules
    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'EXP'),
        ('right', 'UMINUS'),
    )

    last_func_name = None

    def call_func(self, func_name, arguments):
        print("CALL FUNCTION : ", end='')
        print(func_name, end='')
        print("(", end='')
        print(self.arguments, end='')
        print(");")
        self.last_func_name = func_name
        if func_name in self.function_list:
            func = self.function_list[func_name]
            func(func_name, arguments, self)
        elif func_name in self.def_list:
            func_def_obj = self.def_list[func_name]
            # We should run 'run_block' with arguments in place.
            print("HEREHEREHER")
            print("%s(" % func_name, end='')
            print(func_def_obj.p_argument_list, end='')
            print(")", end='')


    def p_program(self, p):
        """program : statements END
                    | argument_list
                    | statements BYE SEMI"""
        p[0] = p[1]
        logging.debug("p_program")


    def p_statements(self, p):
        """statements : statements statement
                     | statement"""
        p[0] = p[1]
        logging.debug("p_statements")

    def p_statement(self, p):
        """statement : func_statement SEMI
                     | id_list EQUALS func_statement SEMI"""
        if (self.arguments != None):
            print(self.arguments)
        self.arguments = list()
        logging.debug("p_statement")

    def p_id_list(self, p):
        """id_list : ID EQUALS id_list
                    | ID"""
        if len(p) > 2:
            pattern = re.compile(self.t_EQUALS)
            if (pattern.match(p[2])):
                self.names[p[1]] = p[3]
        p[0] = p[1]
        logging.debug("p_id_list")

    def p_func_statement(self, p):
        """func_statement : ID argument_list_paren
                            | ID argument_list
                            | ID LPAREN RPAREN
                            | ID list_range
                            | ID"""
        if len(p) > 3:
            pattern = re.compile(self.t_LPAREN)
            if pattern.match(p[2]):
                print (p[1], "(", self.arguments, ");")
            else:
                print (p[1], self.arguments)
        else:
            print (p[1], "(", self.arguments, ");")

        logging.debug("p_func_statement")
        p[0] = p[1]
        self.call_func(p[1], self.arguments)


    def p_list_range(self, p):
        """list_range : entry RANGE list_range
                    | entry"""

#  draw z1{dir 30}..z2{right}..z5{down}..z3{right}..z4{dir 30};
#  draw z5..z6{down}..z7{right}..z8;
        p[0] = p[1]
        logging.debug("p_list_range")


    def p_entry(self, p):
        """entry : ID LBRACE option_list RBRACE
                | ID"""
        if len(p) > 2:
            p[0] = p[1]  # should be changed to an entry with option_list
        else:
            p[0] = p[1]

        logging.debug("p_entry")


    def p_option_list(self, p):
        """option_list : option_list ID
                        | ID
                        | expression"""
        if len(p) > 2:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

        loggine.debug("p_option_list")


    def p_argument_list_paren(self, p):
        """argument_list_paren : LPAREN argument_list RPAREN"""
        p[0] = p[2]
        logging.debug("p_argument_list_paren")


    def p_argument_list(self, p):
        """argument_list : argument COMMA argument_list
                        | argument argument_list
                        | argument"""
        p[0] = p[1]
        print("argument_list")
        print(self.arguments)
        logging.debug("p_argument_list")

    def p_argument(self, p):
        """argument : ID
                    | STRING_LITERAL
                    | expression"""
        p[0] = p[1]
        self.arguments.append(p[1])
        logging.debug("p_argument %s" % (p[1]))

    def p_statement_assign(self, p):
        """statement : ID EQUALS complex_expression"""
        self.names[p[1]] = p[3]
        logging.debug("statement:ID=expression;")
        print("%s %s" % (p[1], p[3]))
        logging.debug("p_statement_assign")

    def p_statement_expr(self, p):
        """statement : complex_expression"""
        p[0] = p[1]
        logging.debug("statement:expression;")
        print("%s %s" % (p[0], p[1]))
        logging.debug("p_statement_expr")

    def p_complex_expression(self, p):
        """complex_expression : ID EQUALS complex_expression
                                | ID EQUALS expression
                                | expression"""
        if len(p) > 3:
            pattern = re.compile(self.t_EQUALS)
            if (pattern.match(p[2])):
                self.names[p[1]] = p[3]
        if p[1] in self.names:
            p[0] = self.names[p[1]]
        else:
            p[0] = p[1]

        logging.debug("p_complex_expression : result = %s from %s" % (p[0], p[1]))

    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EXP expression
                  | expression expression
        """
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '**':
            p[0] = p[1] ** p[3]
        else:
            p[0] = p[1] * p[2]  # Case for  0.03w,  1.5h, etc

        logging.debug("p_expression_binop")

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = -p[2]
        logging.debug("p_expression_uminus")

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]
        logging.debug("p_expression_group")

    def p_expression_int(self, p):
        'expression : INTEGER'
        p[0] = int(p[1])
        print(p[0])
        logging.debug("p_expression_int")

    def p_expression_float(self, p):
        'expression : FLOAT'
        p[0] = float(p[1])
        logging.debug("p_expression_float")


    def p_expression_id(self, p):
        'expression : ID'
        try:
            if p[1] in self.reserved:
                p[0] = 0 # p[1]
            else:
                p[0] = self.names[p[1]]

            print(p[0])
        except:
            print("Undefined name '%s'" % p[1])
            print(self.names)
            p[0] = 0

        logging.debug("p_expression_id")

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            #print("Syntax error at EOF")
            pass


if __name__ == '__main__':
    metafont = Metafont()
    filename = None
    prog_path = os.path.dirname(sys.argv[0])
    if prog_path == "":
        prog_path = "."

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    metafont.run(filename)

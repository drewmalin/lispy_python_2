"""
    Lispy Python (Pythonic Lisp?)
"""
import ply.lex as lex
import ply.yacc as yacc
import traceback
import language


#### LEXER ####

reserved = {
    'and' : 'AND',
    'or' : 'OR',
    'let' : 'LET',
    'def' : 'DEF'
}

# Must be present
tokens = [
    'SYMBOL',
    'NUMBER',
    'BOOLEAN',
    'TIMES',
    'DIVIDE',
    'PLUS',
    'MINUS',
    'POW',
    'MOD',
    'EQUALS',
    'LT',
    'GT',
    'LE',
    'GE',
    'LPAREN',
    'RPAREN',
    'LSQUARE',
    'RSQUARE'
] + list(reserved.values())

# Tokens
# Each definition must be of the form t_<token name defined above>

def t_error(t):
    print "Illegal character \'str(t.value[0])\'"
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_BOOLEAN(t):
    r'TRUE|FALSE'
    t.value = True if t.value == 'TRUE' else False
    return t

def t_SYMBOL(t):
    r'[a-zA-Z_][a-zA-Z0-9]*'
    t.type = reserved.get(t.value, 'SYMBOL')
    return t

def t_NUMBER(t):
    r'[-]?(([0-9]+\.[0-9]+)|(\.[0-9]+)|([0-9]+\.?))'
    if '.' in t.value:
        try:
            t.value = float(t.value)
        except ValueError:
            print "Float value too large: " + str(t.value)
            t.value = 0.0
    else:
        try:
            t.value = int(t.value)
        except ValueError:
            print "Integer value too large: " + str(t.value)
            t.value = 0
    return t

t_ignore = ' \t'

t_TIMES = r'\*'
t_DIVIDE = r'/'
t_PLUS = r'\+'
t_MINUS = r'-'
t_POW = r'\^'
t_MOD = r'%'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'

lex.lex()

#### PARSER ####

def p_result(p):
    '''
    result : statement
    '''
    print p[1]

### Statements
def p_statement_expression(p):
    '''
    statement : LPAREN expression RPAREN
    '''
    p[0] = p[2]

def p_op(p):
    '''
    op : PLUS 
       | MINUS 
       | TIMES 
       | DIVIDE
       | POW
       | MOD
       | EQUALS
       | LE
       | GE
       | LT
       | GT
       | AND
       | OR
    '''
    p[0] = p[1]


def p_expression_let(p):
    '''
    expression : LET SYMBOL operand

    '''
    language.context.context.assign(p[2], p[3])
    p[0] = language.Symbol(p[2])

def p_expression_def(p):
    '''
    expression : DEF SYMBOL LSQUARE RSQUARE statement
    '''
    definition = language.FunctionDefinition(p[2], p[5])
    language.context.context.assign(p[2], definition)
    p[0] = definition

def p_expression_def_args(p):
    '''
    expression : DEF SYMBOL LSQUARE symbols RSQUARE statement
    '''
    definition = language.FunctionDefinition(p[2], p[6], p[4])
    language.context.context.assign(p[2], definition)
    p[0] = definition


def p_expression_exec(p):
    '''
    expression : SYMBOL operands
               | SYMBOL
    '''
    arguments = p[2] if len(p) > 2 else []
    definition = language.context.context.get(p[1])
    p[0] = language.Function(definition, arguments)

def p_symbols(p):
    '''
    symbols : SYMBOL symbols
            | SYMBOL
    '''
    p[0] = []
    for symbol in p[1:]:
        p[0] += [s for s in symbol] \
            if isinstance(symbol, list) else [symbol]

def p_operands(p):
    '''
    operands : operand operands
             | operand
    '''
    p[0] = []
    for operand in p[1:]:
        p[0] += [op for op in operand] \
            if isinstance(operand, list) else [operand]

def p_operand_number(p):
    '''
    operand : NUMBER
    '''
    p[0] = language.NumberValue(p[1])

def p_operand_boolean(p):
    '''
    operand : BOOLEAN
    '''
    p[0] = language.BooleanValue(p[1])

def p_operand_symbol(p):
    '''
    operand : SYMBOL
    '''
    p[0] = language.Symbol(p[1])

def p_operand_statement(p):
    '''
    operand : statement
    '''
    p[0] = p[1]

def p_expression_operation(p):
    '''
    expression : op operands
    '''
    p[0] = language.BuiltInOperator(p[1], p[2])

### Error
def p_error(p):
    if p:
        print "Syntax error at \'" + p.value + "\'"
    else:
        print "Malformed expression (missing closing parenthesis?)"

yacc.yacc()

# Infinite loop of interpretation!
while 1:
    try:
        s = raw_input('> ')
    except EOFError:
        break
    s = s.strip()
    if not s:
        continue
    if s == "quit" or s == "exit":
        break
    try:
        yacc.parse(s)
    except Exception as e:
        print e
        #print traceback.format_exc()

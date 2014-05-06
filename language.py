import operator
import context

class Expression:
    '''
    Expression interface. Expressions will be able to be 'executed,' returning
    a value based on the subtype.
    '''
    def execute(self, context):
        pass

class BuiltInOperator(Expression):
    '''
    BulitInOperator makes use of Python's interpretation of basic arithmetic
    and logical operators.
    '''
    OP = {
        '+'     : operator.add,
        '-'     : operator.sub,
        '*'     : operator.mul,
        '/'     : operator.div,
        '%'     : operator.mod,
        '<'     : operator.lt,
        '>'     : operator.gt,
        '<='    : operator.le,
        '>='    : operator.ge,
        '^'     : operator.pow,
        '='     : operator.eq,
        'and'   : operator.and_,
        'or'    : operator.or_
    }
    
    def __init__(self, op, arguments):
        '''
        Ops must match the enum above, otherwise execution halts.
        '''
        if op in BuiltInOperator.OP:
            self.op = BuiltInOperator.OP[op]
            self.arguments = arguments
        else:
            raise Exception, "Unknown operator: \'" + op + "\'"

    def __str__(self):
        return str(self.execute(context.context))
    
    def execute(self, context=None):
        '''
        Invoke the built-in Python interpretation of the given operator. First,
        all arguments are executed to determine raw values, then the built-in
        operator is put to work.
        '''
        #print "DEBUG: <OP: " + str(self.op) + "> " + \
        #"<ARGS: " + str([str(arg) for arg in self.arguments]) + ">"
        eval_args = [arg.execute(context) for arg in self.arguments]
        return reduce(lambda x, y: self.op(x, y), eval_args)

class FunctionDefinition(Expression):
    '''
    User-defined definition of a function. Required are the name of the
    function (for later lookup), the parameters (optional), and the implementation,
    or body. The body will be assumed to simply be another executable, which at
    this point actually means a BuiltInOperator of arbitraty nested depth.
    '''
    def __init__(self, name, body, parameters=[]):
        self.name = name
        self.body = body
        self.parameters = parameters

    def __str__(self):
        return "<FUNCTION: " + self.name + ">"

    def execute(self, arguments, context):
        '''
        Executing the definition itself isn't actually useful.
        '''
        pass

class Function(Expression):
    '''
    Runtime form of the FunctionDefinition object. Requires the FunctionDefinition
    to execute, along with a set of arguments to apply to the definition's parameters
    (optional depending on the definition).
    '''
    def __init__(self, definition, arguments=[]):
        self.definition = definition
        self.arguments = arguments

    def __str__(self):
        return str(self.execute(context.context))

    def execute(self, context):
        '''
        Execution of a defined-function first establishes a new layer of scope so that
        local parameters may be assigned to the incoming argument values. These will
        override global symbols of the same name, and will not persist after the
        execution of the function completes.
        '''
        if len(self.arguments) != len(self.definition.parameters):
            raise Exception, "Function \'" + self.definition.name + "\' takes "  + \
                str(len(self.definition.parameters)) + " arguments. Found " + \
                str(len(self.arguments))
        context.push_scope() 
        for pair in zip(self.definition.parameters, self.arguments):
            context.assign(pair[0], pair[1])
        ret = self.definition.body.execute(context)
        context.pop_scope()
        return ret

class Symbol(Expression):
    '''
    Represents a container for a value. The value could be a raw type (integer, float,
    etc.) or the definition of a function.
    '''
    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return "<SYMBOL: " + self.symbol + ">"

    def execute(self, context=None):
        '''
        Lookup of symbol values will start in the closest scope layer and proceed outward
        from there. Throws an exception if the symbol is not found in this context.
        '''
        return context.get(self.symbol).execute(context)

class NumberValue(Expression):
    '''
    Representation of either an integer or floating point value.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "<NUMBER: " + str(self.value) + ">"

    def execute(self, context=None):
        '''
        Simply return the value.
        '''
        return self.value

class BooleanValue(Expression):
    '''
    Representation of either a 'True' or 'False' Boolean value.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "<BOOLEAN: " + str(self.value) + ">"

    def execute(self, context=None):
        '''
        Simply return the value.
        '''
        return self.value

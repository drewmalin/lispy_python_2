import language

class Context:
    '''
    Represents the context of a given execution. Variable
    scope will increase in depth as executions are nested.
    If a symbol is not found in the deepest scope, outer levels
    are searched. If a variable is assigned to itself in this
    scope, the value is assumed to be in an outer layer.
    '''
    def __init__(self):
        self.scope = [{}]
        self.function_definitions = {}

    def push_scope(self):
        '''
        Create new scoping layer.
        '''
        self.scope.append({})

    def pop_scope(self):
        '''
        Discard this scoping layer.
        '''
        self.scope.pop()

    def assign(self, symbol, value):
        '''
        Assign to the inner-most scoping layer, the given value
        to the given symbol.
        '''
        self.scope[-1][symbol] = value

    def get(self, symbol):
        '''
        Retrieve the value of the given symbol from the current scope.
        If the symbol does not exist in this layer, or if the symbol is
        found to be assigned to itself (a valid case if symbol names are
        reused as function parameters) then the next (more shallow) layer
        is searched until the value is found or all scoping layers have
        been searched.
        '''
        for scope in self.scope[::-1]:
            if symbol in scope and self.self_reference_check(symbol, scope[symbol]):
                return scope[symbol]
        raise Exception, "Undefined symbol: \'" + symbol + "\'"

    def self_reference_check(self, symbol, value):
        '''
        Check to see if this symbol is pointing to itself (or a Symbol
        instance with the same name). Either case will result in a
        recursive call of infinite depth. Returning False here will
        force the symbol lookup to abandon this layer of scope and check
        the next.
        '''
        if isinstance(value, language.Symbol):
            if value.symbol == symbol:
                return False
        return True

context = Context()

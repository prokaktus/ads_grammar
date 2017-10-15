import ply.lex as lex


class SyntaxError(Exception):
    pass


class Lexer(object):
    states = (
        ('sstring', 'exclusive'),
    )

    tokens = (
        "ID",
        "SUB_ID",
        "STRING",
        "OPEN_PARENS",
        "CLOSE_PARENS",
        "COMMA"
    )

    t_ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_SUB_ID = r'{[a-zA-Z_][a-zA-Z0-9_]*}'
    t_OPEN_PARENS = r'\('
    t_CLOSE_PARENS = r'\)'
    t_COMMA = r','
    r_DOUBLEQUOTE = r'"'
    r_SINGLEQUOTE = r"'"

    def __init__(self, *args, context=None, **kwargs):
        self.context = context or {}

    t_ignore = ' \t'

    def t_string(self, t):
        '"|\''
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_symbol = t.value
        t.lexer.text_data = ''
        t.lexer.begin('sstring')

    ### String state ###

    t_sstring_ignore = ''
    
    def t_sstring_end_string(self, t):
        '"|\''
        if t.value != t.lexer.string_symbol:
            t.lexer.text_data += t.value
            return
        # because current lexpos will point to next token, so to check previous
        # we need subtract 2
        if t.lexer.lexdata[t.lexer.lexpos - 2] == '\\':
            t.lexer.text_data += t.value
            return
        t.value = t.lexer.text_data
        t.type = "STRING"
        t.lexer.begin('INITIAL')
        return t

    def t_sstring_characters(self, t):
        '[^"\']'
        t.lexer.text_data += t.value

    def t_sstring_error(self, t):
        raise SyntaxError("Illegal character (string state) {}".format(t.value[0]))
    
    ### End String state ###

    def t_error(self, t):
        raise SyntaxError("Illegal character {}".format(t.value[0]))

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)


    def test(self, input_str=None):
        if not input_str:
            input_str = input('> ')
        for tok in self.iterate_tokens(input_str=input_str):
            print(tok)

    def iterate_tokens(self, input_str):
        self.lexer.input(input_str)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            yield tok

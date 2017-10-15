import re
from itertools import combinations as std_combinations

import ply.yacc as yacc

from .tokenizer import Lexer, SyntaxError


def _check_string(s):
    if s.count('{}') != 1:
        return 'provide string with exact one substituion rule (\{\})'
    


def variants(template, *subst):
    is_bad = _check_string(template)
    if is_bad:
        raise InvalidUsage(is_bad)
    return [template.replace('{}', s) for s in subst]



def combinations(template, *subst):
    is_bad = _check_string(template)
    if is_bad:
        raise InvalidUsage(is_bad)
    res = []
    for r in range(1, len(subst) + 1):
        for perm in std_combinations(subst, r):
            repl = ' '.join(perm)
            res.append(template.replace('{}', repl))
    return res


predefined_funcs = {
    variants.__name__: variants,
    combinations.__name__: combinations,
    str.lower.__name__: str.lower,
    str.upper.__name__: str.upper
}


class InvalidFunc(Exception):
    pass


class InvalidUsage(Exception):
    pass


class UnknownVariable(Exception):
    pass


class Parser:
    tokens = Lexer.tokens

    def __init__(self, context=None, raise_on_miss=True):
        context = context or {}
        self.context = context
        self.raise_on_miss = raise_on_miss
        self.predefined_funcs = predefined_funcs

    def p_expression_func_call(self, p):
        'command : ID OPEN_PARENS args CLOSE_PARENS'
        n = p[1]
        if n not in predefined_funcs:
            raise InvalidFunc('Function {} does not exists'.format(n))
        try:
            args = p[3]
            p[0] = self.predefined_funcs[n](*args)
        except Exception:
            raise InvalidUsage('Invalid usage of function {} with '
                               'parameters {}'.format(n, args)) 


    def p_args(self, p):
        '''
        args : arg
             | arg COMMA args
        '''
        if len(p) == 4:
            res = [p[1]]
            res.extend(p[3])
            p[0] = res
        else:
            p[0] = [p[1]]

    def p_arg(self, p):
        '''
        arg : ID
            | prepared_id 
            | prepared_string
        '''
        p[0] = p[1]

    def _sub_name(self, matchedobj):
        m = matchedobj.group(0)
        m = m.strip('{}') 
        if m in self.context:
            return self.context[m]
        if self.raise_on_miss:
            raise UnknownVariable(m)
        return ''

    def p_prepared_string(self, p):
        '''
        prepared_string : STRING
        '''
        string = p[1]
        string = re.sub(r'{[a-zA-Z]+}', self._sub_name, string)
        p[0] = string

    def p_prepared_id(self, p):
        '''
        prepared_id : SUB_ID
        '''
        sub_id = p[1].strip('{}')
        if sub_id in self.context:
            p[0] = self.context[sub_id]
            return
        if self.raise_on_miss:
            raise UnknownVariable(sub_id)
        p[0] = ''

    # Error rule for syntax errors
    def p_error(self, p):
        raise SyntaxError

    def build(self, **kwargs):
        self.lexer = Lexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    def test(self, input_str=None):
        if not input_str:
            input_str = input('> ')
        result = self.parse(input_str=input_str)
        print(result)

    def parse(self, input_str):
        return self.parser.parse(input_str, lexer=self.lexer.lexer)

import pytest

from ads_grammar.tokenizer import Lexer, SyntaxError
from ads_grammar.parser import Parser, UnknownVariable, InvalidUsage


def test_parser():
    parser = Parser(context={'jo': 'JiMMY'})
    parser.build()
    assert parser.parser
    assert parser.lexer

    assert parser.parse('lower({jo})') == 'jimmy'
    assert parser.parse('upper({jo})') == 'JIMMY'
    with pytest.raises(SyntaxError):
        parser.parse('lower({jo')

    with pytest.raises(UnknownVariable) as exc_info:
        parser.parse('lower({bingo})')
    assert 'bingo' in str(exc_info.value)


def test_parser_variants():
    parser = Parser(context={'vendor': 'Apple', 'model': 'Ipad'})
    parser.build()

    res = parser.parse('variants("buy {} with discount", "phone", "laptop")')
    assert res == ['buy phone with discount', 'buy laptop with discount']

    res = parser.parse('variants("buy {} with discount", {vendor}, {model})')
    assert res == ['buy Apple with discount', 'buy Ipad with discount']

    with pytest.raises(InvalidUsage) as exc_info:
        parser.parse('variants("buy {} with {}", "phone", "laptop")')
    assert 'exact one substituion rule ("{}")' in str(exc_info);


def test_parser_combinations():
    parser = parser = Parser(context={'vendor': 'Apple', 'model': 'Ipad'})
    parser.build()

    res = parser.parse('combinations("buy {} with discount", "phone", "laptop")')
    assert res == ['buy phone with discount', 'buy laptop with discount', 
                   'buy phone laptop with discount']

    res = parser.parse('combinations("buy {} with discount", {vendor}, {model})')
    assert res == ['buy Apple with discount', 'buy Ipad with discount', 
                   'buy Apple Ipad with discount']


def test_lexer():
    lexer = Lexer()
    lexer.build()
    assert lexer.lexer

    tokens = list(lexer.iterate_tokens('lower("HELLO")'))
    assert tokens[0].type == 'ID'
    assert tokens[1].type == 'OPEN_PARENS'
    assert tokens[2].type == 'STRING'
    assert tokens[3].type == 'CLOSE_PARENS'

    tokens = list(lexer.iterate_tokens('lower({vendor})'))
    assert tokens[0].type == 'ID'
    assert tokens[2].type == 'SUB_ID'

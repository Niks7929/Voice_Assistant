import ast
import math
import operator
import re


_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_ALLOWED_FUNCTIONS = {
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'log': math.log,
}


class CalculatorService:
    @staticmethod
    def normalize_expression(question: str):
        text = (question or '').strip()
        if not text:
            return ''

        clean = text.lower().replace('×', '*').replace('÷', '/').replace('^', '**')
        for word, replacement in {
            'plus': '+',
            'minus': '-',
            'times': '*',
            'multiplied by': '*',
            'divided by': '/',
            'over': '/',
            'equals': '',
            'what is': '',
            'calculate': '',
            'compute': '',
        }.items():
            clean = clean.replace(word, replacement)

        clean = re.sub(r'[^0-9a-zA-Z+\-*/().%_\s]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean or ''

    @staticmethod
    def evaluate(expression: str):
        expr = (expression or '').strip()
        if not expr:
            raise ValueError('No expression provided')

        expr = CalculatorService.normalize_expression(expr)
        if not expr:
            raise ValueError('No calculable expression found')

        if expr.startswith('='):
            expr = expr[1:]

        cleaned = re.findall(r'[-+*/().0-9a-zA-Z_\s]+', expr)
        expr = ' '.join(cleaned).strip()
        expr = expr.replace('sqrt', 'sqrt')

        tree = ast.parse(expr, mode='eval')

        def eval_node(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
                return _ALLOWED_BINOPS[type(node.op)](eval_node(node.left), eval_node(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
                return _ALLOWED_UNARYOPS[type(node.op)](eval_node(node.operand))
            if isinstance(node, ast.Call):
                func_name = node.func.id if isinstance(node.func, ast.Name) else None
                if func_name in _ALLOWED_FUNCTIONS and len(node.args) == 1:
                    return _ALLOWED_FUNCTIONS[func_name](eval_node(node.args[0]))
                raise ValueError(f'Unsupported function call: {func_name}')
            raise ValueError(f'Unsupported expression: {ast.dump(node)}')

        result = eval_node(tree.body)
        if isinstance(result, float) and result.is_integer():
            return int(result)
        return result

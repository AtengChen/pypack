code = r"""

if a < 0:
    if a == 0:
        if abs(a) > 10:
            b = "small negative number"
        else:
            b = "big negative number"
    else:
        if abs(a) > 10:
            b = "small negative number"
        else:
            b = "big negative number"
else:
    if a == 0:
        if abs(a) > 10:
            b = "zero"
        else:
            b = "zero"
    else:
        if abs(a) > 10:
            b = "big positive number"
        else:
            b = "small positive number"


"""


import ast

from ast import Call, Attribute, Constant, Load, Name, Slice, Subscript


def merge(s1, s2):
    s1, s2 = s2, s1
    
    l1, l2 = len(s1), len(s2)
    d = abs(l1 - l2)
    
    if l1 > l2:
        s2 += d * " "
    elif l1 < l2:
        s1 += d * " "
    
    return "".join([a + b for a, b in zip(s1, s2)])


def parse_if_else(source):
    tree = []
    
    if isinstance(source, ast.Assign):
        tree.append("assign")
        tree.append(source)
        return tree
    
    tree.append(source.test)
    
    tree.append((parse_if_else(source.body[0]), parse_if_else(source.orelse[0])))
    
    return tree


def get_expr(code_tree):
    __append_flag = True
    
    def _get_expr(tree, magic="", comparisons=[]):
        nonlocal __append_flag
        
        if isinstance(tree[0], ast.Compare):
            if __append_flag:
                comparisons.append(tree[0])
            
            return merge(
                             _get_expr(tree[1][0], magic, comparisons)[0], 
                             _get_expr(tree[1][1], magic, comparisons)[0]
                         ), comparisons
        
        __append_flag = False
        
        return tree[1].value.value, comparisons
    
    magic, cond = _get_expr(code_tree)
    magic = magic.split(" ")
    return magic, cond


def generate_code(magic, conds, magic_name="fuck"):
    assign = ast.Assign(
                 targets=[
                     ast.Name(id=magic_name, ctx=ast.Store())
                 ],
                 value=ast.List(
                     elts=[*map(ast.Constant, magic)],
                     ctx=ast.Load()
                 )
             )
    
    assign.lineno = 0
    
    expr = Call(
        func=Attribute(
            value=Constant(value=' '),
            attr='join',
            ctx=Load()),
        args=[
            Name(id=magic_name, ctx=Load())
        ],
        keywords=[])
    
    conds = list(reversed(conds))
    for cond in conds:
        slice = Slice(lower=cond, step=Constant(value=2))
        expr = Subscript(value=expr, slice=slice)
    
    expr = Call(
               func=Attribute(
                   value=expr,
                   attr='strip',
                   ctx=Load()),
               
               args=[],
               keywords=[])
    
    return ast.Expr(value=assign, type_ignores=[]), expr


def generate(code):
    tree = parse_if_else(ast.parse(code).body[0])
    magic, cond = get_expr(tree)
    assign, expr = generate_code(magic, cond)
    return ast.unparse(assign).strip(), ast.unparse(expr).strip()


if __name__ == "__main__":
    for i in generate(code):
        print(i)

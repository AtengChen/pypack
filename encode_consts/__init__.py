import ast, sys, os.path


sys.path.append(os.path.abspath("."))


from .encode_int import convert as e_int
from .encode_str_int import convert as e_str


table = {"str": e_str, "int": e_int}


def convert_node(node):
    if isinstance(node, ast.Expr):
        if isinstance(node.value, ast.Constant):
            value = node.value.value
            type_name = type(value).__name__
            if type_name in table:
                expr = table[type_name](value)
                new_node = ast.parse(expr)
                node.value = new_node.body[0]
        elif isinstance(node.value, ast.Call):
            args = node.value.args
            for ind, arg in enumerate(args):
                if isinstance(arg, ast.Constant):
                    value = arg.value
                    type_name = type(value).__name__
                    if type_name in table:
                        expr = table[type_name](value)
                        new_node = ast.parse(expr)
                        args[ind] = new_node
                elif isinstance(arg, ast.BinOp):
                    left, right, op = arg.left, arg.right, arg.op
                    
                    if isinstance(left, ast.Constant):
                        value = arg.left.value
                        type_name = type(value).__name__
                        if type_name in table:
                            expr = table[type_name](value)
                            new_node = ast.parse(expr)
                            left = new_node
                    
                    if isinstance(right, ast.Constant):
                        value = arg.right.value
                        type_name = type(value).__name__
                        if type_name in table:
                            try:
                                expr = table[type_name](value)
                            except Exception:
                                expr = repr(value)
                            
                            new_node = ast.parse(expr)
                            right = new_node
                    
                    args[ind] = ast.BinOp(left=left, op=op, right=right)

   
                
import ast
import builtins


def parse_expr(expr_node, custom_funcs=[]):
    if isinstance(expr_node, ast.Call):
        call = expr_node
        if isinstance(call.func, ast.Attribute):
            return expr_node
        
        if hasattr(call.func, "id"):
            func_name = call.func.id
        else: # Lambda
            return expr_node
        
        if func_name not in custom_funcs:
            if func_name in dir(builtins):
                call.func.id = f"_builtins.{func_name}"

        for ind in range(len(call.args)):
            arg = call.args[ind]
            if isinstance(arg, ast.Call):
                call.args[ind] = parse_expr(arg)

        return call
    
    return expr_node
    

def parse_assign(name, value):
    new_node = None

    if isinstance(name, ast.Name):
        new_node = ast.NamedExpr(name, value)
    elif isinstance(name, ast.Attribute):
        parent = name.value.id
        child = name.attr
        new_node = ast.Call(func=ast.Name(id='setattr', ctx=ast.Load()),
                            args=[ast.Name(id=parent, ctx=ast.Load()),
                                  ast.Constant(value=child),
                                  value],
                            keywords=[])
    elif isinstance(name, ast.Subscript):
        parent = name.value.id
        slice_index = name.slice
        if not isinstance(slice_index, ast.Slice):
            new_node = ast.Call(func=ast.Attribute(value=ast.Name(id=parent, ctx=ast.Load()),
                                                   attr='__setitem__',
                                                   ctx=ast.Load()),
                                args=[parse_expr(slice_index),
                                      value],
                                keywords=[])
        else:
            lower = parse_expr(slice_index.lower)
            upper = parse_expr(slice_index.upper)
            step = parse_expr(slice_index.step)
    
            if step is None:
                step = ast.Constant(value=None)
    
            slice_obj = ast.Call(func=ast.Attribute(value=ast.Name(id='_builtins', ctx=ast.Load()),
                                            attr='slice',
                                            ctx=ast.Load()),
                             args=[lower, upper, step],
                             keywords=[])
            
            new_node = ast.Call(func=ast.Attribute(value=ast.Name(id=parent, ctx=ast.Load()),
                                                   attr='__setitem__',
                                                   ctx=ast.Load()),
                                args=[slice_obj,
                                      value],
                                keywords=[])
    elif isinstance(name, ast.Tuple):
        elts = []
        for index, varname in enumerate(name.elts):
            assign_node = ast.Subscript(value=value, 
                                        slice=ast.Constant(value=index),
                                        ctx=ast.Load())
            
            elts.append(parse_assign(varname, assign_node))
        
        new_node = wrap_list(elts)
    else:
        raise Exception(f"Unsupported node: {repr(name)}\t{repr(value)}")
    
    return new_node



def gen_stmt_list(source_code, is_module=True, is_function=False):
    mod = ast.parse(source_code).body
    new_mod = []
    custom_funcs = []
    has_return = False
    modules = []

    for node in mod:
        if isinstance(node, ast.Assign):
            if len(node.targets) > 1:
                continue # unsupported
            name = node.targets[0]
            value = parse_expr(node.value)
            new_mod.append(parse_assign(name, value))
        elif isinstance(node, ast.AugAssign):
            name = node.target
            value = ast.BinOp(left=name, op=node.op, right=parse_expr(node.value))
            new_mod.append(parse_assign(name, value))
        elif isinstance(node, ast.Expr):
            new_mod.append(parse_expr(node.value, custom_funcs=custom_funcs))
        elif isinstance(node, ast.If):
            condition = node.test
            do = node.body
            orelse = node.orelse
            if len(orelse) != 0:
                new_node = ast.IfExp(test=parse_expr(condition), 
                                     body=wrap_list(gen_stmt_list(indent2code(do), is_module=False)), 
                                     orelse=wrap_list(gen_stmt_list(indent2code(orelse), is_module=False)))
            else:
                new_node = ast.IfExp(test=parse_expr(condition), 
                                     body=wrap_list(gen_stmt_list(indent2code(do), is_module=False)), 
                                     orelse=ast.Expr(value=ast.Constant(value=None)))
            
            new_mod.append(new_node)
        elif isinstance(node, ast.For):
            var = node.target
            iter_obj = node.iter
            body = node.body
            new_node = ast.ListComp(elt=wrap_list(gen_stmt_list(indent2code(body), is_module=False)), 
                                    generators=[ast.comprehension(target=var, 
                                                                 iter=parse_expr(iter_obj), 
                                                                 ifs=[], 
                                                                 is_async=0)])
            new_mod.append(new_node)
        elif isinstance(node, ast.FunctionDef):
            name = node.name
            custom_funcs.append(name)
            args = node.args
            body = node.body
            # TODO: decorator
            new_node = ast.NamedExpr(target=ast.Name(id=name, ctx=ast.Store()),
                                     value=ast.Lambda(args=args, body=ast.Subscript(value=wrap_list(gen_stmt_list(indent2code(body), is_module=False, is_function=True), is_function=True), 
                                                                                    slice=ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=1)))))
            new_mod.append(new_node)
        elif isinstance(node, ast.Return):
            if is_function:
                value = node.value
                new_mod.append(value)
            else:
                raise SyntaxError("'return' outside function")

            has_return = True
        elif isinstance(node, ast.Import):
            for name in node.names:
                modules.append(name.name)
        elif isinstance(node, ast.With):
            # withitem_nodes = node.items
            # 
            # if len(withitem_nodes) > 1:
            #     raise TypeError("Doesn't support multiple with assignments")
            # 
            # withitem_node = withitem_nodes[0]
            # 
            # if not withitem_node.optional_vars:
            #     new_mod.append(ast.Expr(value=ast.Call(
            #                                func=ast.Attribute(
            #                                    value=withitem_node.context_expr,
            #                                    attr="__enter__",
            #                                    ctx=ast.Load()
            #                                ), args=[], keywords=[]
            #                            )))
            #     new_mod.append(wrap_list(gen_stmt_list(indent2code(node.body), is_module=False, is_function=True)))
            #     new_mod.append(ast.Expr(value=ast.Call(
            #                                func=ast.Attribute(
            #                                    value=withitem_node.context_expr,
            #                                    attr="__exit__",
            #                                    ctx=ast.Load()
            #                                ), args=[], keywords=[]
            #                            )))
            # else:
            #     raise TypeError("Doesn't support as statement")
            pass
        else:
            raise TypeError(f"Doesn't support node {node.__name__}")
    
    if is_module:
        new_mod.append(ast.Constant(value=0))

        args = [ast.arg(arg='_builtins')]

        for name in modules:
            args.append(ast.arg(arg=name))
        
        call_args = [ast.Call(
                        func=ast.Name(id='__import__', ctx=ast.Load()),
                        args=[
                           ast.Constant(value='builtins')],
                        keywords=[])]

        for name in modules:
            call_args.append(ast.Call(
                                func=ast.Name(id='__import__', ctx=ast.Load()),
                                args=[
                                   ast.Constant(value=name)],
                                keywords=[]))

        return ast.Subscript(
            value=ast.Call(
               func=ast.NamedExpr(
                  target=ast.Name(id='_', ctx=ast.Store()),
                  value=ast.Lambda(
                     args=ast.arguments(
                        posonlyargs=[],
                        args=args,
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[]),
                     body=ast.List(elts=new_mod, ctx=ast.Load()))),
               args=call_args,
               keywords=[]),
            slice=ast.UnaryOp(
                     op=ast.USub(),
                     operand=ast.Constant(value=1)),
                     ctx=ast.Load())
    elif is_function and not has_return:
        new_mod.append(None)
    
    return new_mod

def wrap_list(lst, is_function=False):
    if (len(lst) > 1) or is_function:
        return ast.List(elts=lst, ctx=ast.Load())
    else:
        return lst[0]

def indent2code(body):
    return ast.unparse(ast.Module(body=body, type_ignores=[]))

def gen_oneliner_module(source):
    module = ast.Module(
                body=[
                   ast.Expr(
                      value=ast.Call(
                         func=ast.Attribute(
                            value=ast.Call(
                               func=ast.Name(id='__import__', ctx=ast.Load()),
                               args=[
                                  ast.Constant(value='sys')],
                               keywords=[]),
                            attr='exit',
                            ctx=ast.Load()),
                         args=[gen_stmt_list(source)],
                         keywords=[]))],
                type_ignores=[])
    
    # print(ast.dump(module, include_attributes=False, indent=4))
    return ast.unparse(module)


def generate_oneliner_module_api(tree):
    source = ast.unparse(tree)
    source = gen_oneliner_module(source)
    return ast.parse(source)


if __name__ == "__main__":
    print(gen_oneliner_module("def square(x):\n"
                              "\treturn x ** 2\n"
                              "\n"
                              "\n"
                              "def get_lst(n):\n"
                              "\tfor i in range(n):\n"
                              "\t\tif i % 2 == 1:\n"
                              "\t\t\tprint(i)\n"
                              "\t\telif i % 3 == 2:\n"
                              "\t\t\tprint(square(i))\n"
                              "\t\telse:\n"
                              "\t\t\tprint('hello')\n"
                              "\treturn 'Done'"
                              "\n"
                              "num = int(input('Enter your number: '))\n"
                              "print('-' * 50)\n"
                              "status = get_lst(num)\n"
                              "print('-' * 50)\n"
                              "print(status + '!')"))

    print(gen_oneliner_module("import random\nprint(random.randint(1, 10))"))

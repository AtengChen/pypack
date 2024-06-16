#! python3

import argparse
import ast
import builtins
import keyword
import itertools
import string
import sys
import os

whitelist = set()

def convert(ind, n):
    if n > 1:
        return ["".join(pair) for pair in itertools.product(string.ascii_lowercase, repeat=n)][ind]
    else:
        return string.ascii_lowercase[ind]


def is_valid_variable(name, whitelist):
    return (
        name not in dir(builtins)
        and not keyword.iskeyword(name)
        and name not in whitelist
        and not name.startswith("_")
    )


def parse_code(tree, whitelist):
    variables_list = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and is_valid_variable(node.name, whitelist):
            if node.name not in variables_list:
                variables_list.append(node.name)
            for param in node.args.args:
                if param.arg not in variables_list: 
                    variables_list.append(param.arg)
        elif isinstance(node, ast.Name) and is_valid_variable(node.id, whitelist):
            if node.id not in variables_list:
                variables_list.append(node.id)
        elif isinstance(node, ast.ImportFrom):
            add_module_functions_to_whitelist(node.module, is_module=True)
        elif isinstance(node, ast.Import):
            for m in node.names:
                add_module_functions_to_whitelist(m.name)
    return variables_list


def encrypt(tree, complexity, verbose):
    global whitelist
    
    variables_list = parse_code(tree, whitelist)
    
    n = 0
    for i in variables_list:
        new_var = convert(n, complexity)
        if not is_valid_variable(new_var, {}):
            n += 1
            new_var = convert(n, complexity)
        if verbose:
            print(f"{i} -> {new_var}")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == i:
                node.id = new_var
            elif isinstance(node, ast.FunctionDef) and node.name == i:
                node.name = new_var
            elif isinstance(node, ast.arg) and node.arg == i:
                node.arg = new_var
        n += 1
    
    return tree


def add_module_functions_to_whitelist(name, is_module=False):
    if is_module:
        module = __import__(name)
        functions = dir(module)
        for function in functions:
            whitelist.add(function)
    else:
        whitelist.add(name)


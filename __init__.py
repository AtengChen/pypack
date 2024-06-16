import sys

sys.setrecursionlimit(20000)


import ast

from encrypt import encrypt
from code2oneline import generate_oneliner_module_api
from encode_version import get_determine_version

from encode_consts import convert_node as ob_const

def pack_source(source, **config):
    """
    Options:
        verbose				bool
        encode_consts			bool
        encode_varnames			bool
	oneline				bool
	encode_version			str
        
    """
    if config["verbose"]:
        print("Using config:")
        for name, val in config.items():
            print(f"\t{name}: {val}")
        
        print()
    
    tree = ast.parse(source)
    
    if config["encode_consts"]:
        if config["verbose"]:
            print("Encoding source code's constants...")
            print()
        
        for node in list(ast.walk(tree)).copy():
            ob_const(node)
    
    if config["encode_varnames"]:
        if config["verbose"]:
            print("Encoding source code's variable names...")
            print()
        
        tree = encrypt(tree, complexity=config["encode_varnames"], verbose=config["verbose"])
    
    # print(ast.dump(tree, indent=4))
    print("\n\n\n")
    print(ast.unparse(tree))
    
    if config["oneline"]:
        if config["verbose"]:
            print("\nConverting source to oneline...\n")
        
        tree = generate_oneliner_module_api(tree)
    
    if config["encode_version"] == "default":
        tree = get_determine_version(tree)
    elif config["encode_version"] != "none":
        tree = get_determine_version(tree, config["encode_version"])
    
    source = ast.unparse(tree)
    
    if config["verbose"]:
        print("\nDONE!\n\n")
    
    return source



if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose output.", action="store_true")
    
    parser.add_argument("-enc1", "--encode-consts", help="Encode constants.", action="store_true")
    parser.add_argument("-enc2", "--encode-varnames", help="Encode variable names in given complexity.", type=int, default=1)
    parser.add_argument("-enc3", "--encode-version", help="When the encoded program was run in a different version of python, then exit. Default to current version. Call with `none` to disable it.", type=str, default="")
    
    parser.add_argument("-ol", "--oneline", help="Compress the code to oneline.", action="store_true")
    
    parser.add_argument("-a", "--all", help="Use all the options (default values for options).", action="store_true")
    
    parser.add_argument("-i", "--input", help="Input file. If the file is not provided, use stdin.", type=str, default="0")
    parser.add_argument("-o", "--output", help="Output file. If the file is not provided, use stdout.", type=str, default="1")
    parser.add_argument("-fe", "--file-encoding", help="Input and output file encoding", type=str, default="utf-8")
    
    args = parser.parse_args()
    
    config = {}
    if args.all:
        config = { 
			"encode_consts": True, 
			"encode_varnames": True, 
			"oneline": True
                 }
    else:
        config = {
			"encode_consts": args.encode_consts,
			"encode_varnames": args.encode_varnames,
			"oneline": args.oneline,
                 }
        
    if args.encode_version != "":
        config["encode_version"] = args.encode_version
    else:
        config["encode_version"] = "none"
    
    config["verbose"] = args.verbose
    
    input_file = int(args.input) if args.input.isnumeric() else args.input
    output_file = int(args.output) if args.output.isnumeric() else args.output
    
    with open(input_file, "r", encoding=args.file_encoding) as f:
        code = f.read()
    
    new_code = pack_source(code, **config)
    
    with open(output_file, "w", encoding=args.file_encoding) as f:
        f.write(new_code)


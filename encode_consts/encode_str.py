import builtins
import random


types = {
    "function": '(lambda **__: {**__}).__class__.__name__',
    "code": '(lambda *__: [*__]).__code__.__class__.__name__',
    "mappingproxy": '"".__class__.__dict__.__class__.__name__',
    "builtin_function_or_method": 'len.__class__.__name__',
    "wrapper_descriptor": '{}.__class__.__init__.__class__.__name__',
    "method-wrapper": '__builtins__.__getattribute__("object").__call__().__str__.__class__.__name__',
    "method_descriptor": '__builtins__.str.join.__class__.__name__',
    "classmethod_descriptor": 'dict.__dict__.__getitem__("fromkeys").__class__.__name__',
    "GenericAlias": 'type([].__class__[{}.__class__]).__name__',
    "Union": '("".__class__ | ().__class__).__class__.__name__',
    "ellipsis": '....__class__.__name__',
    "NoneType": 'type(None).__name__',
    "NotImplementedType": '__builtins__.__getattribute__("type").__eq__((), {}).__class__.__name__'
    
}


def _convert(string):
    global types
    
    names = [*types.keys()]
    random.shuffle(names)
    
    code = []
    positions = []
    max_len = max(map(lambda x: len(hex(ord(x))) - 2, string))
    
    for ch in string:
        for name in names:
            if ch in name:
                if random.randint(0, 1):
                    pos = name.index(ch)
                else:
                    pos = -(len(name) - name.index(ch))
                if pos not in positions:
                    positions.append(pos)
                if pos < 0:
                    code.append(f"{types[name]}[-_[{positions.index(pos)}]]")
                    positions[-1] = -positions[-1]
                else:
                    code.append(f"{types[name]}[_[{positions.index(pos)}]]")
                break
        else:
            char = hex(ord(ch))
            char = char[:2] + "0" * (max_len - (len(char) - 2)) + char[2:]
            code.append(f'"\\{char[1:]}"')
    
    return " + ".join(code), positions


def convert(string):
    code, positions = _convert(string)
    max_len = max(map(lambda x: len(hex(x)) - 2, positions))
    for ind in range(len(positions)):
        pos = hex(positions[ind])
        positions[ind] = pos[:2] + "0" * (max_len - (len(pos) - 2)) + pos[2:]
    return f'(lambda _: {code})([{", ".join(positions)}])'


if __name__ == "__main__":
    import string
    print(convert(string.ascii_letters))

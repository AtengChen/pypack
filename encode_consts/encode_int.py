"""
convert(123) -> `(lambda *_: (_[0] << ((_[0] << ((_[0] << _[0]) + _[0] & _[1])) + (_[0] & _[2]) * (_[0] << _[0]) + _[0] & _[3])) + (_[0] & _[2]) * (_[0] << ((_[0] << ((_[0] << _[0]) + _[0] & _[1])) + (_[0] & _[1]) * (_[0] << _[0]) + _[0] & _[4])) + (_[0] & _[5]) * (_[0] << ((_[0] << ((_[0] << _[0]) + _[0] & _[1])) + (_[0] & _[1]) * (_[0] << _[0]) + _[0] & _[6])) + (_[0] & _[7]) * (_[0] << ((_[0] << _[0]) + _[0] & _[2])) + (_[0] & _[8]) * (_[0] << ((_[0] << _[0]) + _[0] & _[1])) + (_[0] & _[9]) * (_[0] << _[0]) + _[0] & _[10])(0x01, 0x02, 0x03, 0x06, 0x05, 0x07, 0x04, 0x0f, 0x1e, 0x3d, 0x7b)`
"""


import functools


def _convert(n, _print=lambda _: None, digit_length=None, ind=0, pos=0, magics=None):
    s = []
    b = bin(n)[2:]
    k = len(b) - 1
    
    if not digit_length:
        digit_length = len(hex(n)[2:])
    
    if not magics:
        magic = hex(1)
        magics = [magic[:2] + "0" * (digit_length - (len(magic) - 2)) + magic[2:]]
    
    if ind:
        if pos == 0:
            _print(rf"{(ind - 2) * '    '}   /---\{n}")
        elif pos == 1:
            _print(rf"{(ind - 2) * '    '}   +---\{n}")
    
    for v in b:
        if ind:
            if k != 0:
                _print(rf"{'   |' * ind}{k} {v}")
            else:
                _ = "\\"
                _print(rf"{'   |' * (ind - 1)}   {_}{k} {v}")
        else:
            _print(f"{ind * '    '}{k} {v}")
        
        magic = n >> k
        if magic == 1:
            coff = ""
        else:
            magic = hex(magic)
            magic = magic[:2] + "0" * (digit_length - (len(magic) - 2)) + magic[2:]
            if magic not in magics:
                magics.append(magic)
            
            coff = f"(_[0] & _[{magics.index(magic)}]) * "
        
        if k == 0:
            s.append(coff[:-3][1:-1])
        elif k == 1:
            s.append(f"{coff}(_[0] << _[0])")
        else:
            if k == len(b) - 1:
                s.append(f"{coff}(_[0] << ({_convert(k, _print=_print, digit_length=digit_length, ind=ind + 1, pos=1, magics=magics)}))")
            else:
                s.append(f"{coff}(_[0] << ({_convert(k, _print=_print, digit_length=digit_length, ind=ind + 1, pos=0, magics=magics)}))")
        
        k -= 1
    
    if ind:
        return " + ".join(s)
    else:
        return " + ".join(s), magics


def convert(n, debug=False):
    if debug:
        expr, _lst = _convert(n, _print=print)
    else:
        expr, _lst = _convert(n)
    
    lst = ", ".join(_lst)
    
    if not expr:
        expr = "len(_)"
    
    return f"(lambda *_: {expr})({lst})"


if __name__ == "__main__":
    print(convert(int(input())))
from .encode_str import _convert as convert_str
from .encode_int import convert as convert_int


def convert(string):
    code, positions = convert_str(string)
    
    for ind in range(len(positions)):
        pos = positions[ind]
        positions[ind] = convert_int(pos)
    
    return f'(lambda _: {code})([{", ".join(positions)}])'


if __name__ == "__main__":
    print(convert(input()))
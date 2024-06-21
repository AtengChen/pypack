## PyPack

*python version of webpack*

```
usage: __init__.py [-h] [-v] [-enc1] [-enc2 ENCODE_VARNAMES] [-enc3 ENCODE_VERSION] [-ol] [-a] [-i INPUT] [-o OUTPUT] [-fe FILE_ENCODING]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Turn on verbose output.
  -enc1, --encode-consts
                        Encode constants.
  -enc2 ENCODE_VARNAMES, --encode-varnames ENCODE_VARNAMES
                        Encode variable names in given complexity.
  -enc3 ENCODE_VERSION, --encode-version ENCODE_VERSION
                        When the encoded program was run in a different version of python, then exit. Default to current version. Call with `none` to disable it.
  -ol, --oneline        Compress the code to oneline.
  -a, --all             Use all the options (default values for options).
  -i INPUT, --input INPUT
                        Input file. If the file is not provided, use stdin.
  -o OUTPUT, --output OUTPUT
                        Output file. If the file is not provided, use stdout.
  -fe FILE_ENCODING, --file-encoding FILE_ENCODING
                        Input and output file encoding
```

### Known Limitations:
 - Only supports "for", "def", "assign", "if-elif-else" statements
 - Assignment only supports normal assign (like `a = 1`), attribute assign (like `a.b = 1`) and single slice assign (like `a[b] = 2`, but not `a[b][c] = 3`).
 - "return" can be only used in function level, for example, the following can be packed:
   
   ```
   def a():
     b = 2
     return b
   ```
   but this can't:
   ```
   def a():
     b = 2
     if b < 1:
       return b
   ```

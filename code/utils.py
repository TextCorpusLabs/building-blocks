import pathlib
from typeguard import typechecked

@typechecked
def guess_encoding(file_name: pathlib.Path) -> str:
    """
    Guess the encoding of a file

    Parameters
    ----------
    file_name : pathlib.Path
        The file at issue
    """
    with open(file_name, 'rb') as fp:
        b = fp.read(2)
    if ((len(b) >= 2) and ((b[0:2] == b'\xfe\xff') or (b[0:2] == b'\xff\xfe'))):
        return "utf-16"
    else:
        return "utf-8"

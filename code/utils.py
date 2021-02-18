import pathlib
import jsonlines as jl
import typing as t
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

@typechecked
def list_jsonl_documents(jsonl_in: pathlib.Path) -> t.Iterator[dict]:
    """
    Lists the documents in the `JSONL` file

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the documents
    """
    encoding = guess_encoding(jsonl_in)
    with open(jsonl_in, 'r', encoding = encoding) as fp:
        with jl.Reader(fp) as reader:
            for item in reader:
                yield item

@typechecked
def list_folder_documents(folder_in: pathlib.Path, is_document: t.Callable[[pathlib.Path], bool]) -> t.Iterator[str]:
    """
    Lists the documents in the folder

    Parameters
    ----------
    folder_in : pathlib.Path
        The folder path containing all the documents
    """
    for file_name in folder_in.iterdir():
        if is_document(file_name):
            yield str(file_name)

@typechecked
def csv_list(text: str) -> t.List[str]:
    """
    Converts a CSV string into its componet parts

    Parameters
    ----------
    text : str
        The CSV text
    """
    result = [item.strip() for item in text.split(',')]
    return result

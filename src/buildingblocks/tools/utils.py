import pathlib
import jsonlines as jl
import progressbar as pb
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
def list_merged_folder_documents(folders_in: t.List[pathlib.Path], is_document: t.Callable[[pathlib.Path], bool]) -> t.Iterator[t.List[str]]:
    """
    Lists the documents in the merge folders

    Parameters
    ----------
    folders_in : pathlib.Path
        The folders containing the documents to merge 
    """
    for i in range(len(folders_in)):
        folder = folders_in[i]
        for file_name in folder.iterdir():
            if is_document(file_name):
                result = [f.joinpath(file_name.name) for f in folders_in]
                exists = [f.exists() for f in result]
                if i > 0 and any(exists[0:i]):
                    continue
                docs = [str(result[i]) for i in range(len(result)) if exists[i]]
                yield docs

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

@typechecked
def csv_tuple(text: str) -> t.List[t.Tuple[str, str]]:
    """
    Converts a ':' paired ',' seperated list into a list of tuples
    Parameters
    ----------
    text : str
        The text to convert
    """
    result = [tuple(target.split(':')) for target in text.split(',')]
    return result

@typechecked
def is_txt_document(file_path: pathlib.Path) -> bool:
    """
    Determins if the file should be included in the processing
    """
    result = \
        file_path.is_file() and \
        file_path.suffix.lower() == '.txt' and \
        not file_path.stem.startswith('_')
    return result

@typechecked
def is_json_document(file_path: pathlib.Path) -> bool:
    """
    Determins if the file should be included in the processing
    """
    result = \
        file_path.is_file() and \
        file_path.suffix.lower() == '.json' and \
        not file_path.stem.startswith('_')
    return result


@typechecked
def drain_iterator(completes: t.Iterator[int]) -> None:
    """
    Runs through the iterator, doing nothing
    """
    for _ in completes:
        pass

@typechecked
def progress_overlay(items: t.Iterator, title: str) -> t.Iterator:
    bar_i = 0
    widgets = [title, ' ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        for item in items:
            bar_i = bar_i + 1
            bar.update(bar_i)
            yield item

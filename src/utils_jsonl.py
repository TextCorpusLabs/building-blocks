import pathlib
import jsonlines as jl
import progressbar as pb
import typing as t
import utils as u
from typeguard import typechecked

@typechecked
def list_documents(jsonl_in: pathlib.Path) -> t.Iterator[dict]:
    """
    Lists all the documents in the `JSONL` file

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL file containing all the documents
    """
    encoding = u.guess_encoding(jsonl_in)
    with open(jsonl_in, 'r', encoding = encoding) as fp:
        with jl.Reader(fp) as reader:
            for item in reader:
                yield item

@typechecked
def save_documents(jsonl_out: pathlib.Path, documents: t.Iterator[dict]) -> None:
    """
    Saves the documents to a `JSONL` file

    Parameters
    ----------
    jsonl_out : pathlib.Path
        The JSONL file to contain all the documents
    documents : Iterator[dict]
        The JSON documents to save
    """
    bar_i = 0
    widgets = [ 'Saving JSONL # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
            with jl.Writer(fp, compact = True, sort_keys = True) as writer:
                for document in documents:
                    writer.write(document)
                    bar_i = bar_i + 1
                    bar.update(bar_i)

import pathlib
import jsonlines as jl
import progressbar as pb
import typing as t
import utils as u
from typeguard import typechecked
from . import common_types as ct


def list_documents(jsonl_in: pathlib.Path) -> t.Iterator[ct.Document]:
    return u.list_jsonl_documents(jsonl_in)

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

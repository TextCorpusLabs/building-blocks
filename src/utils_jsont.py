import json
import pathlib
import progressbar as pb
import tarfile as tf
import typing as t
from io import BytesIO
from typeguard import typechecked

@typechecked
def list_documents(jsont_in: pathlib.Path) -> t.Iterator[dict]:
    """
    Lists all the documents in the `JSONT` file

    Parameters
    ----------
    jsont_in : pathlib.Path
        The JSONT file containing all the documents
    """
    with tf.open(jsont_in, 'r') as tar_ball:
        tar_info = tar_ball.next()
        while tar_info is not None:
            if tar_info.isfile():
                tar_file = tar_ball.extractfile(tar_info)
                if tar_file is not None:
                    txt = tar_file.read()
                    txt = txt.decode('utf-8')
                    document = json.loads(txt)
                    yield document
            tar_info = tar_ball.next()

@typechecked
def save_documents(jsont_out: pathlib.Path, documents: t.Iterator[dict]) -> None:
    """
    Saves the documents to a `JSONT` file

    Parameters
    ----------
    jsonl_out : pathlib.Path
        The JSONL file to contain all the documents
    documents : Iterator[dict]
        The JSON documents to save
    """
    bar_i = 0
    widgets = [ 'Saving JSONT # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        with tf.open(jsont_out, 'w') as tar_ball:
            for document in documents:
                txt = json.dumps(document, indent = None, sort_keys = True)
                txt = txt.encode('utf-8')
                with BytesIO(txt) as tar_file:
                    info = tf.TarInfo(name = f'{bar_i}.json')
                    info.size = len(txt)
                    tar_ball.addfile(info, fileobj = tar_file)
                    bar_i = bar_i + 1
                    bar.update(bar_i)

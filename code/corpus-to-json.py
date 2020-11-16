import pathlib
import jsonlines as jl
import mp_boilerplate as mpb
import progressbar as pb
import typing as t
import utils as u
from argparse import ArgumentParser
from threading import Thread
from typeguard import typechecked

_sentinel = None

@typechecked
def corpus_to_json(folder_in: pathlib.Path, jsonl_out: pathlib.Path) -> None:
    """
    Iterates over all the documents in a folder, aggregating them into a single json file

    Parameters
    ----------
    folder_in : pathlib.Path
        Folder containing the source corpus
    jsonl_out : pathlib.Path
        JSON containing the aggregated corpus
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.MultiWorker(_txt_file_to_json)
    worker.start()
    _collect_files(folder_in, worker)
    _save_to_jsonl(worker, jsonl_out)

    i = 1

@typechecked
def _collect_files(folder_in: pathlib.Path, worker: mpb.MultiWorker) -> None:
    for file_name in folder_in.iterdir():
        if u.is_corpus_document(file_name):
            worker.add_task(str(file_name))
    worker.finished_adding_tasks()

@typechecked
def _txt_file_to_json(file_name: str) -> dict:
    file_name = pathlib.Path(file_name)
    with open(file_name, 'r', encoding = 'utf-8') as fp:
        lines = fp.readlines()
    lines = [line.strip() for line in lines]
    json = { 'file_name' : file_name.name, 'text' : lines }
    return json

@typechecked
def _save_to_jsonl(worker: mpb.MultiWorker, jsonl_out: pathlib.Path) -> None:
    bar_i = 0
    widgets = [ 'Aggregating Document # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        with open(jsonl_out, 'w', encoding = 'utf-16') as fp:
            with jl.Writer(fp, compact = True, sort_keys = True) as writer:
                for item in worker.get_results():
                    bar_i = bar_i + 1
                    bar.update(bar_i)                    
                    writer.write(item)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--folder-in',
        help = 'Folder containing the source corpus',
        type = pathlib.Path,
        default = 'd:/corpus_in')
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'JSONL containing the aggregated corpus',
        type = pathlib.Path,
        default = 'd:/corpus.jsonl')
    args = parser.parse_args()
    print(f'folder in: {args.folder_in}')
    print(f'JSONL out: {args.jsonl_out}')
    corpus_to_json(args.folder_in, args.jsonl_out)

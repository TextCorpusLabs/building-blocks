import pathlib
import jsonlines as jl
import multiprocessing as mp
import progressbar as pb
import typing as t
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

    tasks = mp.Queue()
    results = mp.Queue()

    _start_workers(tasks, results)
    _collect_files(folder_in, tasks)
    _save_json(results, jsonl_out)

@typechecked
def _start_workers(tasks: mp.Queue, results: mp.Queue) -> None:
    workers = []
    for _ in range(mp.cpu_count()):
        worker = mp.Process(target = _worker, args = (tasks, results))
        worker.start()
        workers.append(worker)
    overlord = Thread(target = _overlord, args = (workers, tasks, results))
    overlord.start()

def _overlord(workers: t.List[mp.Process], tasks: mp.Queue, results: mp.Queue) -> None:
    for worker in workers:
        worker.join()
    results.put(_sentinel)
    tasks.close()

@typechecked
def _worker(tasks: mp.Queue, results: mp.Queue) -> None:
    while True:
        item = tasks.get()
        if item == _sentinel:
            tasks.put(_sentinel)
            break            
        else:
            result = _txt_file_to_json(item)
            results.put(result)

@typechecked
def _collect_files(folder_in: pathlib.Path, tasks: mp.Queue) -> None:
    for file_name in folder_in.iterdir():
        if file_name.suffix == '.txt':
            tasks.put(str(file_name))
    tasks.put(_sentinel)

@typechecked
def _save_json(results: mp.Queue, jsonl_out: pathlib.Path) -> None:
    bar_i = 0
    widgets = [ 'Aggregating Document # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
            with jl.Writer(fp, compact = True, sort_keys = True) as writer:
                while True:
                    bar.update(bar_i)
                    bar_i = bar_i + 1
                    json = results.get()
                    if json == _sentinel:
                        break
                    else:                        
                        writer.write(json)

@typechecked
def _txt_file_to_json(file_name: str) -> dict:
    file_name = pathlib.Path(file_name)
    with open(file_name, 'r', encoding = 'utf-8') as fp:
        lines = fp.readlines()
    lines = [line.strip() for line in lines]
    json = { 'file_name' : file_name.name, 'lines' : lines }
    return json

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

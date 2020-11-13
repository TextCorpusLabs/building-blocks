import pathlib
import jsonlines as jl
import multiprocessing as mp
import progressbar as pb
import typing as t
from argparse import ArgumentParser
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

    tasks = mp.JoinableQueue()
    results = mp.JoinableQueue()

    workers = _start_workers(tasks, results)
    _fill_tasks(folder_in, tasks)
    _save_results(results, jsonl_out)

    i = 1

@typechecked
def _start_workers(tasks: mp.Queue, results: mp.Queue) -> t.List[mp.Process]:
    def _overlord(workers: t.List[mp.Process], results: mp.Queue) -> None:
        for worker in workers:
            worker.join()
        results.put(_sentinel)
        results.close()
    workers = []
    for _ in range(mp.cpu_count()):
        worker = mp.Process(target = _process_tasks, args = (tasks, results))
        worker.start()
        workers.append(worker)
    mp.Process(target = _overlord, args = (workers, results))
    return workers

@typechecked
def _fill_tasks(folder_in: pathlib.Path, tasks: mp.Queue) -> None:
    for file_name in folder_in.iterdir():
        tasks.put(str(file_name))
    tasks.put(_sentinel)

@typechecked
def _save_results(results: mp.Queue, jsonl_out: pathlib.Path) -> None:
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
def _process_tasks(tasks: mp.Queue, results: mp.Queue) -> None:
    while True:
        file_name = tasks.get()
        if file_name == _sentinel:
            tasks.put(_sentinel)
            tasks.close()
            break            
        else:
            file_name = pathlib.Path(file_name)
            with open(file_name, 'r', encoding = 'utf-8') as fp:
                lines = fp.readlines()
            lines = [line.strip() for line in lines]
            json = { 'file_name' : file_name.name, 'lines' : lines }
            results.put(json)
    results.close()

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

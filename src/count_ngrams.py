import concurrent.futures
import csv
import multiprocessing as mp
import pathlib
import progressbar as pb
import shutil
import typing as t
import utils as u
import utils_jsonl as ul
from argparse import ArgumentParser
from sys import maxsize as MAX_SIZE
from typeguard import typechecked
from uuid import uuid4

class _merge_arg:
    @typechecked
    def __init__(self, chunk_1: pathlib.Path, chunk_2: pathlib.Path, cache_dir: pathlib.Path):
        self.chunk_1 = chunk_1
        self.chunk_2 = chunk_2
        self.cache_dir = cache_dir

class _ngram:
    @typechecked
    def __init__(self, gram: str, count: int):
        self.gram = gram
        self.count = count

@typechecked
def count_ngrams(jsonl_in: pathlib.Path, csv_out: pathlib.Path, size: int, top: int, fields: t.List[str], chunk_size: int, sub_process_count: int) -> None:
    """
    Calculate the n-grams for a `JSONL` file.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        JSONL file containing the aggregated corpus
    csv_out : pathlib.Path
        The csv file containing the n-grams
    size :  int
        The size of the n-grams
    top : int
        The amount of top n-grams for saving
    fields : List[str]
        The field(s) used to extract n-grams
    chunk_size: int
        The amount of n-grams to aggregate before cacheing
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """
    if csv_out.exists():
        csv_out.unlink()
    cache_dir = csv_out.parent.joinpath(f'tmp_{csv_out.name}')
    cache_dir.mkdir(parents = True, exist_ok = True)

    #docs = ul.list_documents(jsonl_in)
    #docs = u.progress_overlay(docs, 'Reading document')
    #ngrams = (_count_ngrams_in_doc(doc, fields, size) for doc in docs)
    #chunks = _chunk_ngrams_in_corpus(ngrams, chunk_size)
    #chunks = (_sort_ngram_chunk(x) for x in chunks)
    #chunks = (_write_ngram_chunk(x, cache_dir) for x in chunks)
    #chunks = list(chunks)
    #chunk = _merge_ngram_chunks(chunks, cache_dir, sub_process_count)
    chunk = list(cache_dir.iterdir())[0]
    ngrams = _read_ngram_chunk(chunk)
    ngrams = u.progress_overlay(ngrams, 'Reading n-grams')
    ngrams = _keep_top_ngrams(ngrams, top)
    ngrams = sorted(ngrams, key = lambda ng: ng.count, reverse = True)
    _write_ngrams(ngrams, csv_out, size)
    #shutil.rmtree(cache_dir)

@typechecked
def _count_ngrams_in_doc(document: dict, fields: t.List[str], size: int) -> dict:
    result = {}
    for field in fields:
        if field in document:
            for line in document[field]:
                tokens = line.upper().split(' ')
                for i in range(len(tokens) - size + 1):
                    ngram = ' '.join(tokens[i:(i+size)])
                    if ngram not in result:
                        result[ngram] = 0
                    result[ngram] = result[ngram] + 1
    return result

@typechecked
def _chunk_ngrams_in_corpus(ngram_list: t.Iterator[dict], chunk_size: int) -> t.Iterator[dict]:
    tmp = {}
    for ngrams in ngram_list:
        for ngram, count in ngrams.items():
            if ngram not in tmp:
                tmp[ngram] = 0
            tmp[ngram] = tmp[ngram] + count
        if len(tmp) > chunk_size:
            yield tmp
            tmp = {}
    if len(tmp) > 0:
        yield tmp

@typechecked
def _sort_ngram_chunk(ngrams: dict) -> t.Iterator[list]:
    for ngram, count in sorted(ngrams.items(), key = lambda a: a[0]):
        yield _ngram(ngram, count)

@typechecked
def _write_ngram_chunk(ngrams: t.Iterator[_ngram], cache_dir: pathlib.Path) -> pathlib.Path:
    file_name = cache_dir.joinpath(f'tmp_{uuid4()}.csv')
    with open(file_name, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        for curr in ngrams:
            writer.writerow([curr.gram, curr.count])
    return file_name

@typechecked
def _merge_ngram_chunks(chunks: t.List[pathlib.Path], cache_dir: pathlib.Path, sub_process_count: int) -> pathlib.Path:
    bar_i = 0
    widgets = ['Mergeing n-gram chunks ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with mp.Pool(processes = sub_process_count) as pool:
        with pb.ProgressBar(widgets = widgets) as bar:
            while len(chunks) > 1:
                bar_i = bar_i + 1
                bar.update(bar_i)
                pairs = (pair for pair in _pair_ngram_chunks(chunks))
                args = (_merge_arg(p[0], p[1], cache_dir) for p in pairs)
                chunks = [chunk for chunk in pool.imap_unordered(_merge_ngram_chunk_pair, args)]
                i = 1
    return chunks[0]

@typechecked
def _pair_ngram_chunks(chunks: t.List[pathlib.Path]) -> t.Iterator[t.List[pathlib.Path]]:
    t1 = None
    for chunk in chunks:
        if t1 is None:
            t1 = chunk
        else:
            yield [t1, chunk]
            t1 = None
    if t1 is not None:
         yield [t1, None]

@typechecked
def _merge_ngram_chunk_pair(args: _merge_arg) -> pathlib.Path:
    if args.chunk_2 is None:
        return args.chunk_1
    chunks = [args.chunk_1, args.chunk_2]
    ngrams = _read_ngram_chunks(chunks)
    ngrams = _aggregate_ngrams_chunk(ngrams)
    file_name = _write_ngram_chunk(ngrams, args.cache_dir)
    for chunk in chunks:
        chunk.unlink()
    return file_name

@typechecked
def _read_ngram_chunks(chunks: t.List[pathlib.Path]) -> t.Iterator[_ngram]:
    readers = [_read_ngram_chunk(chunk) for chunk in chunks]
    current = [next(reader) for reader in readers]
    cnt = len(current)
    while cnt > 0:
        i = _min_index(current)
        yield current[i]
        current[i] = next(readers[i], None)
        if current[i] is None:
            cnt = cnt - 1

@typechecked
def _min_index(ngrams: t.List[_ngram]) -> int:
    len_ngs = len(ngrams)
    for i in range(len_ngs):
        if ngrams[i] is not None:
            min_ng = ngrams[i].gram
            min_i = i
            break
    for i in range(min_i + 1, len_ngs):
        curr = ngrams[i]
        if curr is not None and curr.gram < min_ng:
            min_ng = curr.gram
            min_i = i
    return min_i

@typechecked
def _read_ngram_chunk(chunk: pathlib.Path) -> t.Iterator[_ngram]:
    with open(chunk, 'r', encoding = 'utf-8') as fp:
        reader = csv.reader(fp, delimiter = ',', quotechar = '"')
        for item in reader:
            yield _ngram(item[0], int(item[1]))

@typechecked
def _aggregate_ngrams_chunk(ngrams: t.Iterator[_ngram]) -> t.Iterator[_ngram]:
    prev = None
    for ngram in ngrams:
        if prev is None:
            prev = ngram
        elif prev.gram == ngram.gram:
            prev.count = prev.count + ngram.count
        else:
            yield prev
            prev = ngram
    if prev is not None:
        yield prev

@typechecked
def _keep_top_ngrams(ngrams: t.Iterator[_ngram], top: int) -> t.Iterator[_ngram]:
    def _add(results: dict, ngram: _ngram):
        if ngram.count not in results:
            results[ngram.count] = []
        results[ngram.count].append(ngram)
    results = {}
    cnt = 0
    mn = MAX_SIZE
    for ngram in ngrams:
        if cnt < top:
            _add(results, ngram)
            cnt = cnt + 1
            if ngram.count < mn:
                mn = ngram.count
        elif ngram.count == mn:
            _add(results, ngram)
            cnt = cnt + 1
        elif ngram.count > mn:
            _add(results, ngram)
            cnt = cnt + 1
            t1 = len(results[mn])
            if cnt - t1 >= top:
                del results[mn]
                cnt = cnt - t1
                mn = min(results.keys())
    for ngrams in results.values():
        for ngram in ngrams:
            yield ngram

@typechecked
def _write_ngrams(ngrams: t.Iterator[_ngram], csv_out: pathlib.Path, size: int) -> None:
    with open(csv_out, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        writer.writerow(['n', 'count', 'ngram'])
        for ngram in ngrams:
            writer.writerow([size, ngram.count, ngram.gram])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL file containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--csv-out',
        help = 'The csv file containing all the n-grams',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-n', '--size',
        help = 'The size of the n-grams',
        type = int,
        required = True)
    parser.add_argument(
        '-t', '--top',
        help = 'The amount of top n-grams for saving',
        type = int,
        default = 10000)
    parser.add_argument(
        '-f', '--fields',
        help = 'The field(s) used to extract n-grams',
        type = u.csv_list,
        default = 'text')
    parser.add_argument(
        '-c', '--chunk_size',
        help = 'The amount of n-grams to chunk to disk to prevent OOM',
        type = int,
        default = 10000000)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to file sort the ngrams',
        type = int,
        default = mp.cpu_count())
    args = parser.parse_args()
    print(' --- count_ngrams ---')
    print(f'jsonl in: {args.jsonl_in}')
    print(f'csv out: {args.csv_out}')
    print(f'size: {args.size}')
    print(f'top: {args.top}')
    print(f'fields: {args.fields}')
    print(f'chunk size: {args.chunk_size}')
    print(f'sub process count: {args.sub_process_count}')
    print(' ---------')
    count_ngrams(args.jsonl_in, args.csv_out, args.size, args.top, args.fields, args.chunk_size, args.sub_process_count)

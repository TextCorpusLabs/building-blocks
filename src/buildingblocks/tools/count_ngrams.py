import csv
import multiprocessing as mp
import pathlib
import progressbar as pb
import shutil
import string
import typing as t
from sys import maxsize as MAX_SIZE
from uuid import uuid4
from . import common_types as ct
from . import utils as u

class _merge_arg:
    def __init__(self, chunk_1: pathlib.Path, chunk_2: pathlib.Path, cache_dir: pathlib.Path):
        self.chunk_1 = chunk_1
        self.chunk_2 = chunk_2
        self.cache_dir = cache_dir

class _ngram:
    def __init__(self, gram: str, count: int):
        self.gram = gram
        self.count = count

_trans = str.maketrans(dict.fromkeys(string.punctuation, ' '))

def count_ngrams(source: pathlib.Path, dest: pathlib.Path, fields: t.List[str], size: int, top: int, chunk_size: int, keep_case: bool, keep_punct: bool) -> None:
    """
    Calculate the n-grams for a `JSONL` file.

    Parameters
    ----------
    source : pathlib.Path
        JSONL file containing the aggregated corpus
    dest : pathlib.Path
        The csv file containing the n-grams
    size :  int
        The size of the n-grams
    top : int
        The amount of top n-grams for saving
    fields : List[str]
        The field(s) used to extract n-grams
    chunk_size: int
        The amount of n-grams to aggregate before cacheing
    keep_case: bool
        Keeps the casing of the fields as-is before converting to tokens
    keep_punct: bool
        Keeps all punctuation of the fields as-is before converting to tokens
    """
    if dest.exists():
        dest.unlink()
    cache_dir = dest.parent.joinpath(f'tmp_{dest.name}')
    cache_dir.mkdir(parents = True, exist_ok = True)
    if source.is_file():
        source_files = [source]
    else:
        source_files = (pathlib.Path(path) for path in u.list_folder_documents(source, u.is_jsonl_document))
    doc_collections = (u.list_jsonl_documents(file) for file in source_files)
    docs = (x for y in doc_collections for x in y)
    docs = u.progress_overlay(docs, 'Reading Document #')
    ngram_collections = (_collect_ngrams_in_doc(doc, fields, size, keep_case, keep_punct) for doc in docs)
    chunks = _chunk_ngram_collections(ngram_collections, chunk_size)
    chunks = (_sort_ngram_chunk(x) for x in chunks)
    chunks = (_write_ngram_chunk(x, cache_dir) for x in chunks)
    chunks = list(chunks)
    chunk = _merge_ngram_chunks(chunks, cache_dir, 1)
    ngrams = _read_ngram_chunk(chunk)
    ngrams = u.progress_overlay(ngrams, 'Reading n-grams')
    ngrams = _keep_top_ngrams(ngrams, top)    
    ngrams = sorted(ngrams, key = lambda ng: ng.count, reverse = True)
    _write_ngrams(ngrams, dest, size)    
    shutil.rmtree(cache_dir)

def _collect_ngrams_in_doc(document: ct.Document, fields: t.List[str], size: int, keep_case: bool, keep_punct: bool) -> t.Dict[str,int]:
    result: t.Dict[str,int] = {}
    for field in fields:
        if field in document:
            for line in document[field]:
                if not keep_case:
                    line = line.upper()
                if not keep_punct:
                    line = line.translate(_trans)
                tokens = line.split()
                for i in range(len(tokens) - size + 1):
                    ngram = ' '.join(tokens[i:(i+size)])
                    if ngram not in result:
                        result[ngram] = 0
                    result[ngram] = result[ngram] + 1
    return result

def _chunk_ngram_collections(ngram_collections: t.Iterator[t.Dict[str,int]], chunk_size: int) -> t.Iterator[t.Dict[str,int]]:
    tmp: t.Dict[str,int] = {}
    for ngrams in ngram_collections:
        for ngram, count in ngrams.items():
            if ngram not in tmp:
                tmp[ngram] = 0
            tmp[ngram] = tmp[ngram] + count
        if len(tmp) > chunk_size:
            yield tmp
            tmp: t.Dict[str,int] = {}
    if len(tmp) > 0:
        yield tmp

def _sort_ngram_chunk(ngrams: t.Dict[str,int]) -> t.Iterator[_ngram]:
    for ngram, count in sorted(ngrams.items(), key = lambda a: a[0]):
        yield _ngram(ngram, count)

def _write_ngram_chunk(ngrams: t.Iterator[_ngram], cache_dir: pathlib.Path) -> pathlib.Path:
    file_name = cache_dir.joinpath(f'tmp_{uuid4()}.csv')
    with open(file_name, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        for curr in ngrams:
            writer.writerow([curr.gram, curr.count])
    return file_name

def _merge_ngram_chunks(chunks: t.List[pathlib.Path], cache_dir: pathlib.Path, sub_process_count: int) -> pathlib.Path:
    widgets = ['N-Gram Chunks Left ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets, initial_value = len(chunks)) as bar:
        with mp.Pool() as pool:
            while len(chunks) > 1:
                pairs = (pair for pair in _pair_ngram_chunks(chunks))
                args = (_merge_arg(p[0], p[1], cache_dir) for p in pairs)
                args = list(args)
                chunks = [chunk for chunk in pool.imap_unordered(_merge_ngram_chunk_pair, args)]
                bar.update(len(chunks))
    return chunks[0]

def _pair_ngram_chunks(chunks: t.List[pathlib.Path]) -> t.Iterator[t.List[pathlib.Path]]:
    t1: pathlib.Path | None = None
    for chunk in chunks:
        if t1 is None:
            t1 = chunk
        else:
            yield [t1, chunk]
            t1 = None
    if t1 is not None:
         yield [t1, None]

def _merge_ngram_chunk_pair(args: _merge_arg) -> pathlib.Path:
    if args.chunk_2 is None:
        return args.chunk_1
    chunks = [args.chunk_1, args.chunk_2]
    ngrams = _read_ngram_chunks(chunks)
    ngrams = _aggregate_ngrams_chunk(ngrams)
    file_name = _write_ngram_chunk(ngrams, args.cache_dir)
    return file_name

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

def _read_ngram_chunk(chunk: pathlib.Path) -> t.Iterator[_ngram]:
    with open(chunk, 'r', encoding = 'utf-8') as fp:
        reader = csv.reader(fp, delimiter = ',', quotechar = '"')
        for item in reader:
            yield _ngram(item[0], int(item[1]))
    chunk.unlink()

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

def _keep_top_ngrams(ngrams: t.Iterator[_ngram], top: int) -> t.Iterator[_ngram]:
    def _add(results: t.Dict[int, t.List[_ngram]], ngram: _ngram):
        if ngram.count not in results:
            results[ngram.count] = []
        results[ngram.count].append(ngram)
    results: t.Dict[int, t.List[_ngram]] = {}
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
    for best_ngrams in results.values():
        for ngram in best_ngrams:
            yield ngram

def _write_ngrams(ngrams: t.List[_ngram], csv_out: pathlib.Path, size: int) -> None:
    with open(csv_out, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        writer.writerow(['n', 'count', 'ngram'])
        for ngram in ngrams:
            writer.writerow([size, ngram.count, ngram.gram])

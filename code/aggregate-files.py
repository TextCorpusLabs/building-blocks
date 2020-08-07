import pathlib
import shutil
import progressbar as pb
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

# max lines per block
_max_lines = 1500000

@typechecked
def aggregate_files(path_in: pathlib.Path, path_out: pathlib.Path) -> None:
    """
    Iterates over all the documents in a corpus, aggregating them ~1.5 million lines at a time

    Parameters
    ----------
    path_in : pathlib.Path
        Folder containing the source corpus
    path_out : pathlib.Path
        Folder containing the aggregated corpus
    """

    if path_out.exists():
        shutil.rmtree(str(path_out))
    path_out.mkdir(parents = True)

    bar_i = 1
    curr_block = 0
    curr_lines = 0
    widgets = [ 'Aggregating Document # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        for file_name in path_in.iterdir():
            if u.is_corpus_document(file_name):
                bar.update(bar_i)
                bar_i = bar_i + 1
                lines = __add_document_to_block(file_name, path_out, curr_block)
                curr_lines = curr_lines + lines
                if curr_lines >= _max_lines:
                    curr_block = curr_block + 1
                    curr_lines = 0

@typechecked
def __add_document_to_block(file_in_name: pathlib.Path, path_out: pathlib.Path, block: int) -> int:
    with open(file_in_name, 'r', encoding = 'utf-8') as file_stream:
        lines = file_stream.readlines()
    
    mode = 'w'
    header = ['', f'--------- {file_in_name.name} ---------', '\n\n']
    file_out_name = path_out.joinpath(f'./block.{block:05}.txt')
    if file_out_name.exists():
        mode = 'a'
        header[0] = '\n'
    
    with open(file_out_name, mode, encoding = 'utf-8') as file_stream:
        file_stream.writelines(header)
        file_stream.writelines(lines)    

    return len(lines) + 3

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--folder-in',
        help = 'Folder containing the source corpus',
        type = pathlib.Path,
        default = 'd:/corpus_in')
    parser.add_argument(
        '-out', '--folder-out',
        help = 'Folder containing the aggregated corpus',
        type = pathlib.Path,
        default = 'd:/corpus_out')
    args = parser.parse_args()
    print(f'folder in: {args.folder_in}')
    print(f'folder out: {args.folder_out}')
    aggregate_files(args.folder_in, args.folder_out)

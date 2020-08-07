import pathlib
from typeguard import typechecked

@typechecked
def is_corpus_document(file_path: pathlib.Path) -> bool:
    result = \
        file_path.is_file() and \
        file_path.suffix.lower() == '.txt' and \
        not file_path.stem.startswith('_')
    return result

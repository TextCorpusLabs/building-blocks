# Flatten Corpus

All of our corpuses are in JSONL format.
Sometimes it is nice to see the contents in a simple text file.
When a corpus is large (millions of documents), several files may be needed to keep them manageable.
This process takes a JSONL corpus, extraces the desired fields, collates the lines, and saves them flat text files with about 100K collated line sets each.

# Run the script

The script is run in a similar manner to the [general form](../README.md#scripts).
The resulting files will be placed in the `-out` folder.

* The files will be named after the `-in` argument, have an incrementing number, and end in `.txt`
* The `-f` fields argument is a _csv list_ of all the fields that need collated.
  On a document by document basis, mismatched line counts will be displayed, and the document skiped.
* When a line is of type `str`, the line is returned as-is.
  When a line is of type `List[str]`, the `-sep` argument controls the concatenation.
  The default is ' '.
* An optional `-spc` argument controls the number of background tasks.
  The default is 1.

```{ps1}
python flatten_corpus.py -in d:/corpus.jsonl -out d:/corpus -f tokenized
```

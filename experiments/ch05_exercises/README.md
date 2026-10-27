# Chapter 5 exercise outputs

`verified-output.json` records what the code cells of the five Chapter 5 notebooks (`exercises/05-exercise-*.ipynb`) printed. The worked solutions in the notebooks quote this file. The runner script that produced it is no longer distributed; to reproduce the outputs, run the notebooks.

- Run on 19 October 2026 in the cloud workspace with Python 3.11, HFST 3.16.0.1 and TurkicNLP 0.5.0 from PyPI. Transducer hashes match `code/ch05-ambiguity/manifest.json` (Turkish `5364ebee…`, Kazakh `902af879…`). With this setup the Chapter 5 hands-on output is reproduced exactly.
- A first run with the pure-Python `pyhfst` reader (Python 3.13, no `hfst` wheel) gave the same readings in a different order. Because all readings of these transducers have weight 0, the pipeline then selected different readings for *evleri* (Exercise 3) and printed `Case=Nom` for Kazakh *алыс* in the hands-on.
- Exercise 4 reads the Kazakh KTB treebank from the UD GitHub master branch.

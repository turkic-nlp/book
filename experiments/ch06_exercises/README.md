# Chapter 6 exercise outputs

`verified-output.json` records what the code cells of the five Chapter 6 notebooks (`exercises/06-exercise-*.ipynb`) printed. The worked solutions in the notebooks quote this file. The runner script that produced it is no longer distributed; to reproduce the outputs, run the notebooks.

- Run on 19 October 2026 in the cloud workspace with Python 3.11, HFST 3.16.0.1, TurkicNLP 0.5.0 and Stanza 1.15.0 (Turkish IMST models from the local TurkicNLP model folder).
- Hugging Face was not reachable from this environment, so the neural analyser (Exercise 3, Glot500) could not be loaded; that cell records the failure instead of a result.
- The same environment reproduces every printed output in the chapter: the toy grammar (`code/ch06-toy-fst/build_and_test.py`, 24 cells), the direct HFST lookups, the Kazakh pipeline, the Turkish and Kazakh generators and the Kazakh and Turkmen `substitute_entity()` examples.

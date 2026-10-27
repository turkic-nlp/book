# Chapter 7 exercise outputs

`verified-output.json` records what the code cells of the six Chapter 7 notebooks (`exercises/07-exercise-*.ipynb`) printed. The worked solutions in the notebooks quote this file. The runner script that produced it is no longer distributed; to reproduce the outputs, run the notebooks.

- Run on 19 October 2026 in the cloud workspace with Python 3.11, HFST 3.16.0.1, TurkicNLP 0.5.0, Transformers 5.3.0, Stanza 1.15.0 (Turkish IMST models) and scikit-learn.
- Hugging Face was not reachable. The Glot500 and NLLB-200 tokenisers were copied from the local TurkicNLP model folder; BERTurk, XLM-R and the Glot500 model weights were not available, so the cells that need them record the failure. The fine-tuned BERTurk tagger of the chapter's Hands-On (M3) does not exist yet; Exercises 4 and 6 use the Stanza IMST tagger as the neural reference instead.
- UD files are read from the GitHub master branch, which can differ from the UD 2.17 release the chapter pins.

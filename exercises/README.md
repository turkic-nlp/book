# Exercise notebooks

Each end-of-chapter exercise has a notebook with an **introductory worked exercise** and a **Your turn — extension**. Introductory means the method is scaffolded; it does not imply a small download or a short training run. The setup cell names the dependencies, data and models. Worked solutions preserve captured results from the documented run.

## Running from a fresh environment

1. Use a supported Python version and create a virtual environment: `python3 -m venv .venv`, then activate it with `source .venv/bin/activate` on macOS/Linux (Windows: `.venv\Scripts\activate`).
2. Install Jupyter and the dependencies in the selected notebook's setup cell into that environment. Use the stated toolkit version, `turkicnlp==0.5.0`, and the extras that notebook requires. HFST compilation exercises also need the HFST command-line tools.
3. Start Jupyter from the repository's `exercises/` directory. The relative imports and local data paths assume this working directory. Select the environment's Python kernel.
4. Review downloads and access conditions before running. A local model path in an earlier run is not an installation step. Where a notebook offers Hub fallback, use its pinned revision; otherwise supply the documented model directory explicitly. Preserve the dataset's access requirements.
5. Run cells in order. Save new outputs and environment details separately from the captured worked solution. Record network errors as errors rather than zero resources or model failures.

## Notebook index

| Notebook | Exercise | What the code does |
|---|---|---|
| `01-exercise-1.ipynb` | Language family exploration | Looks up a language's branch, shows the map, and queries Wikipedia, FineWeb2 and the UD GitHub organisation (worked example: Turkmen) |
| `01-exercise-2.ipynb` | Branch membership and transfer | Answers the branch questions and measures Kyrgyz–Kazakh vs Kyrgyz–Turkish character-trigram overlap on parallel X-WMT sentences, in native script and CTS |
| `01-exercise-3.ipynb` | Resource gap analysis | Builds a dated resource audit for one use case (worked example: NER for Turkmen news) |
| `01-exercise-4.ipynb` | Mutual intelligibility and NLP | Compares a prediction with the Kardeş-NLU results and shows why genealogy, script and resources are confounded |
| `01-exercise-5.ipynb` | What a toolkit offers per language | Lists TurkicNLP processors and backends for six languages and matches them with named evaluation data |
| `01-exercise-6.ipynb` | Community exploration | Lists recently updated Turkic repositories in UD and Turkic UD and reads a treebank changelog |

| `02-exercise-1.ipynb` | Segmenting words | Segments three words under the chapter's convention, checks them with the Apertium analyser and counts LLM tokens |
| `02-exercise-2.ipynb` | Vowel harmony and consonant alternation | Implements the plural and past-tense rules and checks them against the Apertium generator, including exceptional stems |
| `02-exercise-3.ipynb` | Case and word order | Shows the case readings and the parser's analysis of the three word orders and a pro-drop sentence |
| `02-exercise-4.ipynb` | Participial clauses | Analyses the participles and parses both relative clauses |
| `02-exercise-5.ipynb` | Checking a segmenter | Runs the TurkicNLP segmenter on Turkish and Kazakh passive and inability forms |
| `02-exercise-6.ipynb` | Segments per word across the family | Segments 30 aligned X-WMT words in Turkish, Kazakh and Uzbek, with cells for your hand segmentation |
| `02-exercise-7.ipynb` | Choosing a donor | Scores Kazakh and Turkish parsers (native vs CTS input) on the gold Kyrgyz TueCL test set |

| `03-exercise-1.ipynb` | Unicode investigation | Prints code points and lengths for Turkish casing with `str.lower()` and the chapter's NFC helper |
| `03-exercise-2.ipynb` | Homoglyph detection | Finds Cyrillic/Latin look-alikes and words that mix the two scripts |
| `03-exercise-3.ipynb` | Transliteration by hand | Prints the toolkit's Kazakh mapping, converts four words and lists the ambiguous reverse mappings |
| `03-exercise-4.ipynb` | Pipeline ordering | Keeps the original, builds an NFC view and routes script spans to a restoration step |
| `03-exercise-5.ipynb` | Round trips | Converts 50 Uzbek X-WMT sentences to Cyrillic and back and classifies the differences |
| `03-exercise-6.ipynb` | Identify, then transliterate | Runs GlotLID on Kyrgyz sentences before and after CTS conversion (needs `turkicnlp[lid]`) |
| `03-exercise-7.ipynb` | Script transition implications | Shows split vocabularies and document- versus word-level shares on a toy mixed-script corpus |
| `03-exercise-8.ipynb` | Abstention in language identification | Builds a 100-text sample and compares restricted and unrestricted GlotLID with abstention thresholds |
| `03-exercise-9.ipynb` | Does conversion help the task? | Trains the same Kyrgyz POS tagger on native-script and CTS versions of UD Kyrgyz-KTMU |

| `04-exercise-1.ipynb` | Audit another language | Runs the chapter's audit signals (unrestricted GlotLID, script shares, Apertium coverage) on X-WMT documents of known composition for Kyrgyz and Bashkir |
| `04-exercise-2.ipynb` | Lookalike letters | Finds mixed Latin/Cyrillic tokens in the Bashkir, Kazakh, Kyrgyz and Karakalpak test sets, separates names with native suffixes from substitutions, and repairs the latter |
| `04-exercise-3.ipynb` | Mining with a shared script | Mines Kazakh–Kyrgyz pairs among 500 X-WMT candidates by character overlap, native script vs CTS, with margin thresholds (LaBSE cell optional) |
| `04-exercise-4.ipynb` | Absent languages | Runs GlotLID on Sakha and Karakalpak, unrestricted and restricted to HPLT-like labels |

| `05-exercise-1.ipynb` | Template exercise | Compares a hand-written UD bundle for *kitaplarımıza* with the Apertium reading and the pipeline's features |
| `05-exercise-2.ipynb` | Allomorphy tables | Generates dative and locative forms by rule and checks each against the Turkish transducer |
| `05-exercise-3.ipynb` | Morphological ambiguity | Lists the readings of *yazar*, *çalışır* and *evleri* and checks the pipeline's choice in six sentences |
| `05-exercise-4.ipynb` | Cross-language comparison | Reads Kazakh *кетпегендіктен*, Turkish *gitmediğinden* and Turkmen *gitmedigi üçin* with Apertium and lists the Kazakh KTB annotation of *-ГАндІк* forms |
| `05-exercise-5.ipynb` | Morphophonological rule writing | Implements the locative rule and checks the five stems against the transducer |

| `06-exercise-1.ipynb` | FST architecture | Builds the minimal noun transducer with HFST and prints its states and arcs, with and without the archiphoneme `{A}` |
| `06-exercise-2.ipynb` | Extending the toy grammar | Adds the accusative `{y}{I}`, the buffer *y* and *kitap/kitab-* to the toy grammar and tests 21 forms and 40 paradigm cells |
| `06-exercise-3.ipynb` | Coverage comparison | Looks up 20 words from the parallel challenge sentences in the Turkish and Altai transducers (neural cell optional) |
| `06-exercise-4.ipynb` | Generation | Generates *kitap* and *Ankara* paradigms and runs `substitute_entity()` on three Turkish sentences |
| `06-exercise-5.ipynb` | Rule-based vs. neural | Analyses *Gidebilseydik ne güzel olurdu* with the Apertium pipeline and Stanza (IMST) |

| `07-exercise-1.ipynb` | Fertility audit | Isolated-word and running-text fertility, single-token share and 95th percentile on 516 words of Turkish news, for every tokeniser that can be loaded |
| `07-exercise-2.ipynb` | Boundary agreement | Compares TurkicNLP segmenter boundaries with tokeniser boundaries on the 100 most frequent IMST nouns, counting both error types |
| `07-exercise-3.ipynb` | Disambiguation in context | Collects bare *yüz* from seven Turkish UD treebanks and trains a document-split context classifier |
| `07-exercise-4.ipynb` | Constrained FST reranking | Candidate recall, first-candidate baseline and a learned reranker over Apertium candidates on IMST, with Stanza as neural reference |
| `07-exercise-5.ipynb` | Glot500 as a baseline | Scores TurkicNLP's multilingual analyser on IMST test (needs the Glot500 model) |
| `07-exercise-6.ipynb` | Zero-shot transfer evaluation | Scores a Turkish-trained tagger on the Turkish and Azerbaijani TueCL test sets, with a check of annotation conventions |
| `08-exercise-1.ipynb` | Scrambling and case | Subject–object–verb order of the root in BOUN (first 100 qualifying sentences and whole split) and IMST, with examples of the marked orders |
| `08-exercise-2.ipynb` | Participial arc length | Clause width, dependent and participle-to-noun distances for BOUN participles vs. English EWT relative clauses; pre-nominal length by genre; Stanza accuracy by gold arc distance |
| `08-exercise-3.ipynb` | Pro-drop counting | Overt-subject rates of eligible IMST predicates by tense–mood and person, a triaged sample of 50 subjectless cases, and gold vs. parser proportions |
| `08-exercise-4.ipynb` | Cross-lingual parser evaluation | Turkish Stanza on Kyrgyz TueCL, Kazakh KTB and Azerbaijani TueCL in native script, Latin and CTS, with in-language references and the weakest relations |
| `08-exercise-5.ipynb` | Annotation projection | Projects Turkish TueCL trees (gold and parsed) to Azerbaijani through a CTS string-similarity aligner and scores them against the Azerbaijani gold |
| `09-exercise-1.ipynb` | Case suffix analysis in NER | Apertium case of the final word of every KazNERD test GPE/LOCATION/PERSON mention (with *unknown* kept apart) and the Stanza KazNERD model's recall by case |
| `09-exercise-2.ipynb` | Vocabulary overlap and NER | Unknown-token share and subwords per word for Kazakh word types, for every tokeniser that can be loaded; fine-tuning via `code/ch09-ner/train.py` |
| `09-exercise-3.ipynb` | Few-shot NER for Kyrgyz | KyrgyzNER release check, zero-shot Stanza KazNERD with a declared PER/LOC/ORG mapping, and a CRF learning curve with three seeds |
| `09-exercise-4.ipynb` | Entity distribution shift | Jaccard overlap of normalised KazNERD and Turkish PERSON names, and zero-shot Kyrgyz recall for seen vs. unseen names |
| `09-exercise-5.ipynb` | PropBank argument detection | TRopBank frames linked to IMST verbs through the Turkish WordNet: overt-subject position and agreeing antecedent candidates for subjectless predicates |
| `09-exercise-6.ipynb` | An LLM as a recogniser | Stanza reference scores on 50 Kazakh and 50 Kyrgyz sentences, plus LLM rows when an OpenAI-compatible server is configured |
| `10-exercise-1.ipynb` | Data scarcity analysis | Pair sizes from the TIL release README (en–tr vs en–ug ratio, distribution) and a learning-curve design |
| `10-exercise-2.ipynb` | Metric comparison | NLLB-200 greedy vs beam search on 20 X-WMT English–Turkish sentences; corpus BLEU/chrF++ and sentences where the metrics disagree |
| `10-exercise-3.ipynb` | Apertium pipeline trace | Kazakh→Tatar by hand: Apertium analyser, the kaz-tat bilingual dictionary and the Tatar generator |
| `10-exercise-4.ipynb` | Pivot translation comparison | Direct Uzbek→Kyrgyz vs Turkish and Russian pivots on 50 X-WMT sentences, with generation time and error propagation |
| `10-exercise-5.ipynb` | Back-translation experiment | Leak-checked monolingual Kyrgyz, Kyrgyz→Kazakh back-translation and round-trip chrF++ as a filter signal (retraining needs a GPU) |
| `10-exercise-6.ipynb` | Intra-Turkic quality matrix | chrF for 30 directions among six X-WMT/NLLB languages, grouped by branch and script |
| `10-exercise-7.ipynb` | Beyond NLLB's languages | LLM-backend harness for Nogai with language-ID of the outputs (needs an LLM server and references) |
| `11-exercise-1.ipynb` | A frozen baseline | Whisper small (ONNX) on 60 synthetic Kazakh X-WMT sentences from six Piper voices: raw/normalised WER and CER, per voice, error examples |
| `11-exercise-2.ipynb` | Augmentation operations | Speed perturbation, time stretch, pitch shift and noise checked for duration/F0/SNR, and Whisper's sensitivity to each; SpecAugment masks |
| `11-exercise-3.ipynb` | TTS intelligibility and listening tests | ASR-based proxy per Piper voice, variation between synthesis draws, and a blinded, counterbalanced listening-test plan |
| `11-exercise-4.ipynb` | Language tokens | Accepted Turkic tokens; Kazakh and Turkish audio decoded with related-language tokens and automatic detection |
| `12-exercise-1.ipynb` | Vocabulary variants | BERTurk 32K vs 128K from its published evaluations; XLM-R vs Glot500 vocabularies (IDs, parameters); full-text tokens per word for encoders and LLM tokenizers on SIB-200 |
| `12-exercise-2.ipynb` | Classifier, LoRA ranks, full fine-tuning | Glot500 on SIB-200 Kazakh topics: head only, LoRA r=2/8/32 (three seeds for r=8), full fine-tuning; macro-F1, parameters, time and memory |
| `12-exercise-3.ipynb` | Native script or CTS | Turkish-trained LoRA model tested on Kazakh and Kyrgyz in Cyrillic and in the Common Turkic Alphabet, three seeds |
| `12-exercise-4.ipynb` | Multiple-choice evaluation | Kazakh XCOPA (Kardeş-NLU): untrained multiple-choice head vs conditional scoring with Qwen2.5-1.5B-Instruct, with the English originals |
| `12-exercise-5.ipynb` | Extending a tokenizer | 300 Kazakh words added to Glot500: ID, gradient and reload checks, adapter size, fertility and downstream macro-F1 |
| `13-exercise-1.ipynb` | Russian documents and scripts | SIB-200 (FLORES-200) top-1 retrieval for Kazakh, Kyrgyz and Tatar queries against Russian, English and Turkic targets; native/CTS conditions; MiniLM, XLM-R paraphrase and NLLB encoders |
| `13-exercise-2.ipynb` | Keyword search | KazQAD (825,309 passages): BM25 over surface forms, prefixes, Apertium lemmas and Glot500 subwords; significance tests and lemma error analysis |
| `13-exercise-3.ipynb` | Semantic similarity | Kardeş-NLU STS (five languages) with three encoders, bootstrap intervals; design of a native STS set with weighted κ |
| `13-exercise-4.ipynb` | Chunking | Ten longest Kazakh KazQAD articles in 512-token chunks with Llama 3, OLMo 3, Qwen3.6 and Glot500 tokenizers |
| `14-exercise-1.ipynb` | Taboo in Kazakh | Qwen2.5-1.5B-Instruct as describer and guesser with the bounded controller; surface vs lemma rule checker, unresolved tokens, clue language by round |
| `14-exercise-2.ipynb` | Collecting errors | 25 cultural questions each in Kazakh and Uzbek; GlotLID per sentence, script share, Apertium coverage; errors classified by type |
| `14-exercise-3.ipynb` | A coverage baseline | Apertium coverage of 1,000 KazNERD news sentences vs model-written Kazakh news, with the most frequent rejected words |
| `14-exercise-4.ipynb` | Judging a judge | 100 automatically perturbed SIB-200 Kazakh pairs (harmony, Russian, Kyrgyz, Latin script), counterbalanced order, English and Kazakh prompts |
| `15-exercise-1.ipynb` | Feature, bundle and sentence accuracy | Stanza 1.11 on UD 2.17 Kazakh-KTB and Turkish-IMST: feature recall/precision, exact bundle, sentence-exact vs the independence product |
| `15-exercise-2.ipynb` | Surface and lemma novelty | Error rates in the four seen/unseen surface × lemma cells (Turkish IMST, Kazakh KTB) |
| `15-exercise-3.ipynb` | Metrics and suffixes | Apertium-generated negation, case and person edits of X-WMT en–tr references scored with chrF/BLEU; NLLB greedy vs beam and a blinded A/B sheet |
| `15-exercise-4.ipynb` | Option order in TUMLU | Qwen2.5-1.5B on Kazakh TUMLU-mini: four option rotations on dev, frozen policy on the 797 test questions, majority baseline |
| `15-exercise-5.ipynb` | Auditing generated language | GlotLID calibrated on KazNERD by sentence length, then 60 model answers labelled with abstention; stratified reviewer sheet |
| `16-exercise-1.ipynb` | Native and converted script | CRF trained on KazNERD, tested on KyrgyzNER (harmonised PER/LOC/ORG) in native/native, CTS/CTS and mixed conditions; span mapping with `transfer.py` |
| `16-exercise-2.ipynb` | Related and unrelated sources | SIB-200 topic classifiers on frozen MiniLM, XLM-R and NLLB vectors trained on Kazakh, Turkish, Uzbek, Russian, English or French (701 items each), tested on Kyrgyz and Tatar; paired bootstrap |
| `16-exercise-3.ipynb` | Temperature sampling | Imbalanced five-language SIB-200 pool (500/100/40/20/10), T = 1, 2, 5, ∞: exposure, distinct items seen and per-language dev macro-F1 over five seeds |
| `16-exercise-4.ipynb` | Filtering synthetic data | NLLB-200 Kazakh→Kyrgyz on X-WMT kk–ky: round-trip-chrF filter vs random and length-matched random halves, scored against the real Kyrgyz references |
| `16-exercise-5.ipynb` | Real and synthetic code-switching | Stanza's Turkish model on Turkish–German SAGT by word language vs German nouns inserted into IMST sentences |
| `17-exercise-1.ipynb` | A dated resource audit | Kazakh, Kyrgyz, Nogai, Tuvan and Shor: UD 2.17, Apertium, TIL, X-WMT, SIB-200, NLLB-200, GlotLID and Hub columns with observed / not found / error / not checked kept apart |
| `17-exercise-2.ipynb` | CARE evidence in documentation | Lines of the KazNERD and KyrgyzNER READMEs that bear on six CARE questions; documented vs not documented |
| `17-exercise-3.ipynb` | Extending an analyser | 149 KazNERD place names with rule-generated case forms unioned with the Apertium Kazakh analyser; rule check, regression tests, coverage and timing |
| `17-exercise-4.ipynb` | Projecting tags | Turkish gold UPOS projected onto the parallel UD 2.17 TueCL Azerbaijani, Uzbek and Kyrgyz sentences with two aligners, scored against their gold |
| `17-exercise-5.ipynb` | Checking a project plan | Required fields for a community-led plan and a checker that lists the open items of an invented draft |

**Setup.** Python 3.10+ and `pip install "turkicnlp==0.5.0" requests pandas jupyter`. Open the notebooks from this folder (Exercise 1 displays `../images/Turkic_Languages_distribution_map.png`). Chapter 1 Exercises 1, 2, 3 and 6 and Chapter 2 Exercises 6 and 7 need internet access. Chapter 2 also needs `turkicnlp[hfst]` and, for Exercise 7, `stanza`. Chapter 3 Exercises 5–9 need internet access; Exercises 6 and 8 need `turkicnlp[lid]` (GlotLID) and Exercise 9 `scikit-learn`. Chapter 4 needs internet access, `pyhfst`, `fasttext-wheel` and `huggingface_hub` (GlotLID, about 1.6 GB, or a local copy via `GLOTLID_PATH`); its worked solutions come from `experiments/ch04_exercises/verified-output.json`. Chapter 5 needs `turkicnlp[hfst]` or, where `hfst` has no wheel, `turkicnlp` plus `pyhfst`; its worked solutions come from `experiments/ch05_exercises/verified-output.json`. Chapter 6 compiles grammars and needs the compiled `hfst` (Python 3.11 or 3.12) and, for Exercise 5, `stanza`; its worked solutions come from `experiments/ch06_exercises/verified-output.json`. Chapter 7 needs `transformers`, `sentencepiece`, `scikit-learn` and `stanza` in addition; its worked solutions come from `experiments/ch07_exercises/verified-output.json`. Chapter 8 needs `stanza==1.11.0` (the version of the checkpoints used for its worked solutions), `scipy`, `matplotlib` and internet access for the pinned UD 2.17 files (cached in `UD217_DIR`, hash-checked); its worked solutions come from `experiments/ch08_exercises/verified-output.json`, which rebuilds the notebooks with the recorded outputs. Chapter 9 needs `turkicnlp[hfst]`, `stanza==1.11.0`, `sklearn-crfsuite` and, for Exercise 2, `transformers` and `sentencepiece`; Exercise 6 uses an LLM only if `LLM_MODELS`, `LLM_BASE_URL` and `LLM_API_KEY` are set. Its worked solutions come from `experiments/ch09_exercises/verified-output.json`. Chapter 10 needs `torch`, `transformers`, `sentencepiece` and `sacrebleu` for NLLB-200 (set `NLLB_PATH` to use a local copy) and `turkicnlp[hfst]` for Exercise 3; translations are cached so a run can resume. Its worked solutions come from `experiments/ch10_exercises/verified-output.json`, which can run a subset of cells and merges their outputs. Chapter 11 needs `sherpa-onnx==1.13.8`, `librosa==0.11.0` and `soundfile`; it downloads Whisper small (ONNX) and two Piper voices from the sherpa-onnx GitHub releases (about 840 MB, hash-checked) and runs on the CPU. Its test speech is synthetic, and its worked solutions come from `experiments/ch11_exercises/verified-output.json`. Chapter 12 needs `torch`, `transformers`, `peft`, `scikit-learn` and `psutil`; it fine-tunes Glot500-base on the CPU (about 15 minutes per run, cached) and reads models from a local Hugging Face cache or the Hub at pinned revisions. Its worked solutions come from `experiments/ch12_exercises/verified-output.json`. Chapter 13 needs `torch`, `transformers`, `sentencepiece`, `scipy`, `bm25s` and `turkicnlp[hfst]`; Exercise 2 downloads KazQAD's 230 MB passage collection. Its worked solutions come from `experiments/ch13_exercises/verified-output.json`. Chapter 14 needs `llama-cpp-python`, `fasttext-wheel` and `turkicnlp[hfst]`, a GGUF file of Qwen2.5-1.5B-Instruct (`QWEN_GGUF`) and GlotLID (`GLOTLID_PATH`); every model reply is cached. Its worked solutions come from `experiments/ch14_exercises/verified-output.json`. Chapter 15 needs `stanza==1.11.0`, `sacrebleu`, `torch`, `transformers`, `llama-cpp-python`, `fasttext-wheel`, `pyarrow` and `turkicnlp[hfst]`; Exercise 4 reads the Kazakh TUMLU-mini files from `TUMLU_DIR` (download them into `data/tumlu-mini/`, which Git ignores). Its worked solutions come from `experiments/ch15_exercises/verified-output.json`. Chapter 16 needs `sklearn-crfsuite`, `scikit-learn`, `scipy`, `torch`, `transformers`, `sentencepiece`, `sacrebleu`, `stanza==1.11.0` and `turkicnlp[hfst]`; it reads the paraphrase encoders and NLLB-200 from local copies or the Hub at pinned revisions, and caches embeddings, translations and Stanza output. Its worked solutions come from `experiments/ch16_exercises/verified-output.json`. Chapter 17 needs `huggingface_hub`, `fasttext-wheel` (GlotLID via `GLOTLID_PATH`), `transformers`, `torch` and `turkicnlp[hfst]`, plus `git` for Exercise 1, whose live columns are dated observations. Its worked solutions come from `experiments/ch17_exercises/verified-output.json`.

**Live data.** Web queries (Wikipedia, the Hugging Face dataset viewer, GitHub) return the current state, so numbers can differ from the worked solutions, which record the values observed on 18 October 2026 (UTC). When a request fails, the notebook records the failure instead of a number: an unavailable value is not zero, and a failed search is not proof that a resource does not exist. The GitHub search API is rate-limited for anonymous use; wait a minute and rerun if Exercise 6 returns nothing.

The notebooks are the source of the exercises; edit them directly. The recorded outputs quoted in the worked solutions are in `experiments/chNN_exercises/verified-output.json`. Code in the notebooks is licensed under Apache-2.0 (`../code/LICENSE`); the explanatory text is CC BY-SA 4.0, like the book. External data retrieved by the code keeps its own terms.

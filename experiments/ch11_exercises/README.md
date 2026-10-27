# Chapter 11 exercises: recorded outputs

`verified-output.json` records what the code cells of the four Chapter 11 notebooks (`exercises/11-exercise-*.ipynb`) printed, with the date, package versions and the SHA-256 of every downloaded file. The worked solutions in the notebooks quote this file. To reproduce the outputs, run the notebooks.

```bash
pip install sherpa-onnx==1.13.8 librosa==0.11.0 soundfile requests numpy
jupyter nbconvert --to notebook --execute --inplace exercises/11-exercise-*.ipynb
```

## What is measured

- **Models:** Whisper small (int8 ONNX export from the sherpa-onnx `asr-models` release),
  greedy decoding; Piper VITS voices `kk_KZ-issai-high` (six speakers, ISSAI KazakhTTS data,
  CC BY 4.0) and `tr_TR-dfki-medium` (CC BY-NC-SA 4.0) from the `tts-models` release. The archive
  digests are fixed in the code.
- **Text:** the Kazakh and Turkish sides of the X-WMT en-kk and en-tr test sets (TIL release,
  commit `7d988cc`, MIT), first sentences with 5–20 words and no digits.
- **Speech is synthetic.** Error rates compare conditions on identical input; they are not
  estimates of Whisper's accuracy on real Kazakh or Turkish recordings.
- **Scoring:** the `normalize`, `distance` and `errors` functions of `code/ch11-speech/speech.py`
  (corpus-level WER and CER, raw and normalised).

## Reproducibility

Piper samples its output, so a new cache gives slightly different audio and numbers; the audio
digest printed by Exercise 1 identifies the waveforms behind the recorded outputs. Waveforms and
transcripts are cached in `BOOK_DATA_DIR` (default `~/.cache/turkic-nlp-book`), so a rerun with the
same cache reproduces the recorded outputs exactly. The book's run used two CPU threads in a Linux
x86-64 container; decoding takes about 5 s per utterance there, and the full run about an hour.

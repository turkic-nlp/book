"""N2-4: measured sentence-packed token budgets on original FLORES-200 devtest.

No model weights are loaded. See chunk-study/README.md for the protocol and inputs.
The old fertility estimates remain in results/chunk_content.csv as historical data.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.metadata, json, os, re, statistics, tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANGUAGES = {
    'eng_Latn': 'English', 'tur_Latn': 'Turkish', 'azj_Latn': 'North Azerbaijani',
    'azb_Arab': 'South Azerbaijani', 'tuk_Latn': 'Turkmen', 'kaz_Cyrl': 'Kazakh',
    'kir_Cyrl': 'Kyrgyz', 'tat_Cyrl': 'Tatar', 'bak_Cyrl': 'Bashkir',
    'crh_Latn': 'Crimean Tatar', 'uzn_Latn': 'Northern Uzbek', 'uig_Arab': 'Uyghur',
}
TOKENIZERS = {
    'qwen': ('Qwen/Qwen3.5-35B-A3B-FP8', '0b2752837483aa34b3db6e83e151b150c0e00e49'),
    'llama': ('meta-llama/Meta-Llama-3-8B', '8cde5ca8380496c9a6cc7ef3a8b46a0372a1d920'),
    'olmo': ('allenai/Olmo-3-1025-7B', '0a15c289b17ad4f27aabc863276ec525d5312c01'),
}
ARCHIVE_SHA256 = 'b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6'
BUDGET = 512

def sha(data):
    return hashlib.sha256(data).hexdigest()

def pack_sentences(sentences, count_tokens, budget=BUDGET):
    """Greedy packing with exact re-encoding of each proposed space-joined chunk.

    Reject an oversized individual sentence rather than truncate/drop it. Keep
    the final tail in the audit output; mark it separately from closed chunks.
    """
    if budget < 1 or not sentences:
        raise ValueError('Positive budget and nonempty sentences are required')
    chunks = []
    start = 0
    current = []
    tokens = 0
    for i, sentence in enumerate(sentences):
        if not sentence or sentence != sentence.strip():
            raise ValueError(f'Empty or edge-whitespace sentence at row {i + 1}')
        single = count_tokens(sentence)
        if single > budget:
            raise ValueError(f'Sentence {i + 1} needs {single} tokens, exceeding {budget}')
        candidate = ' '.join(current + [sentence])
        n = count_tokens(candidate)
        if current and n > budget:
            chunks.append(make_chunk(start, i, current, tokens, False))
            current, start, tokens = [sentence], i, single
        else:
            current.append(sentence)
            tokens = n
    chunks.append(make_chunk(start, len(sentences), current, tokens, True))
    assert sum(c['sentences'] for c in chunks) == len(sentences)
    assert all(0 < c['tokens'] <= budget for c in chunks)
    return chunks

def make_chunk(start, end, sentences, tokens, final):
    return {'first_row': start + 1, 'last_row': end, 'sentences': len(sentences),
            'words': len(re.findall(r'\S+', ' '.join(sentences))),
            'tokens': tokens, 'final_tail': int(final)}

def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def run(archive, tokenizer_root, output_dir):
    from tokenizers import Tokenizer
    import tiktoken
    data = archive.read_bytes()
    if sha(data) != ARCHIVE_SHA256:
        raise ValueError('Archive checksum differs from the pinned FLORES-200 release')
    manifest = {
        'dataset': 'Original FLORES-200', 'split': 'devtest', 'sentences_per_language': 1012,
        'license': 'CC-BY-SA-4.0',
        'source_documentation': 'https://github.com/facebookresearch/flores/blob/main/flores200/README.md',
        'archive_url': 'https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz',
        'archive_sha256': ARCHIVE_SHA256, 'inputs': {}, 'tokenizers': {},
        'budget': BUDGET, 'preprocessing': 'strip leading/trailing whitespace per source row; preserve internal text', 'joiner': 'one ASCII space', 'order': 'published sentence order',
        'word_definition': 'nonempty whitespace-delimited units (Python regex \\S+)',
        'special_tokens': False, 'chat_template': False, 'truncation': False,
        'summary_population': 'all closed chunks, excluding the single final tail per language/tokenizer',
        'scope': 'Sentence-stream packing probe; boundaries may cross source articles. Not retrieval quality or a document-level RAG evaluation.',
        'versions': {p: importlib.metadata.version(p) for p in ['tokenizers', 'tiktoken', 'regex']},
        'python_version': __import__('platform').python_version(),
    }
    count = {}
    for key, (repo, rev) in TOKENIZERS.items():
        path = tokenizer_root / ('models--' + repo.replace('/', '--')) / 'snapshots' / rev / 'tokenizer.json'
        tok = Tokenizer.from_file(str(path)); tok.no_truncation(); tok.no_padding()
        count[key] = lambda s, tok=tok: len(tok.encode(s, add_special_tokens=False).ids)
        manifest['tokenizers'][key] = {'repo_id': repo, 'revision': rev, 'file': 'tokenizer.json', 'sha256': sha(path.read_bytes())}
    enc = tiktoken.get_encoding('o200k_base')
    count['o200k'] = lambda s: len(enc.encode(s, disallowed_special=()))
    # Hash the actual merge ranks and special-token mapping, independent of cache paths.
    bpe = b'\n'.join(k.hex().encode() + b' ' + str(v).encode() for k,v in sorted(enc._mergeable_ranks.items(), key=lambda kv: kv[1]))
    manifest['tokenizers']['o200k'] = {'encoding': enc.name, 'mergeable_ranks_sha256': sha(bpe),
        'special_tokens_sha256': sha(json.dumps(enc._special_tokens, sort_keys=True).encode()),
        'vocabulary_url': 'https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken'}
    summaries, details = [], []
    with tarfile.open(archive) as tar:
        metadata = tar.extractfile('./flores200_dataset/metadata_devtest.tsv').read()
        manifest['metadata_sha256'] = sha(metadata)
        assert len(metadata.decode().splitlines()) == 1013
        for lang, language in LANGUAGES.items():
            member = './flores200_dataset/devtest/' + lang + '.devtest'
            raw = tar.extractfile(member).read(); raw_sentences = raw.decode('utf-8').splitlines()
            sentences = [s.strip() for s in raw_sentences]
            assert len(sentences) == 1012
            manifest['inputs'][lang] = {'archive_member': member, 'sha256': sha(raw), 'rows': len(sentences), 'edge_trimmed_rows': sum(a != b for a,b in zip(raw_sentences,sentences))}
            for key, fn in count.items():
                chunks = pack_sentences(sentences, fn)
                closed = [c for c in chunks if not c['final_tail']]
                if not closed: raise ValueError('No closed chunks: sample is too small')
                for j,c in enumerate(chunks): details.append({'lang': lang, 'tokenizer': key, 'chunk': j + 1, **c})
                means = {f'{k}_per_chunk': statistics.mean(c[k] for c in closed) for k in ['words','sentences','tokens']}
                summaries.append({'lang':lang,'language':language,'tokenizer':key,'chunk_tokens':BUDGET,
                    'input_sentences':len(sentences),'closed_chunks':len(closed),
                    'summarized_sentences':sum(c['sentences'] for c in closed),
                    'tail_sentences':chunks[-1]['sentences'],'tail_tokens':chunks[-1]['tokens'],
                    **{k:round(v,6) for k,v in means.items()},
                    'fill_percent':round(means['tokens_per_chunk']/BUDGET*100,6),
                    'max_chunk_tokens':max(c['tokens'] for c in chunks),
                    'max_sentence_tokens':max(map(fn,sentences)),
                    'method':'exact re-encoded greedy sentence packing; final tail excluded',
                    'source':'original FLORES-200 devtest; archive SHA256 '+ARCHIVE_SHA256})
                print(lang,key,'chunks',len(closed),'words',round(means['words_per_chunk'],1),'fill',round(means['tokens_per_chunk']/BUDGET*100,1),flush=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir/'chunk_content_measured.csv',summaries)
    write_csv(output_dir/'chunk_content_chunks.csv',details)
    for name in ['chunk_content_measured.csv','chunk_content_chunks.csv']:
        manifest.setdefault('outputs',{})[name]=sha((output_dir/name).read_bytes())
    manifest['script_sha256']=sha(Path(__file__).read_bytes())
    (output_dir/'chunk_content_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return summaries

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive',type=Path,required=True)
    ap.add_argument('--tokenizer-root',type=Path,default=Path.home()/'.cache/huggingface/hub')
    ap.add_argument('--output-dir',type=Path,default=HERE/'results')
    args=ap.parse_args();run(args.archive,args.tokenizer_root,args.output_dir)

if __name__=='__main__': main()

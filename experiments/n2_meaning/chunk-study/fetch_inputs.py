"""Download only the pinned public archive and tokenizer files (never weights).
Run from any directory; --cache-dir holds the archive and HF tokenizer cache.
Existing authorisation may be needed for the Llama tokenizer.
"""
from pathlib import Path
import argparse,hashlib,sys,urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from exp_chunk_content import TOKENIZERS,ARCHIVE_SHA256

def main():
    from huggingface_hub import hf_hub_download
    ap=argparse.ArgumentParser();ap.add_argument('--cache-dir',type=Path,required=True);a=ap.parse_args()
    a.cache_dir.mkdir(parents=True,exist_ok=True);p=a.cache_dir/'flores200_dataset.tar.gz'
    if not p.exists():
        urllib.request.urlretrieve('https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz',p)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=ARCHIVE_SHA256:raise ValueError('Archive checksum mismatch')
    for repo,rev in TOKENIZERS.values():
        hf_hub_download(repo,'tokenizer.json',revision=rev,cache_dir=a.cache_dir/'hub')
    print('Inputs ready. Run exp_chunk_content.py with --archive',p,'--tokenizer-root',a.cache_dir/'hub')
if __name__=='__main__':main()

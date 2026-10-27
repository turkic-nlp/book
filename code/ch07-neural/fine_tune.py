"""Chapter 7 fixed-budget BERTurk baseline. Run from the book root.
Set UD_IMST_DIR to the official UD 2.17 Turkish-IMST directory.
Downloads the pinned model if absent; full run is experiment M3.
"""
# pip install "transformers==5.3.0" "torch==2.10.0" "accelerate==1.12.0"
from pathlib import Path
import hashlib, importlib.metadata, json, os, sys
import torch
from transformers import (AutoTokenizer, AutoModelForTokenClassification, TrainingArguments,
                          Trainer, DataCollatorForTokenClassification, set_seed)
sys.path.insert(0, "code/ch07-neural")
from morph_tagging import (load_conllu, training_rows, predict_words,
                          score_predictions, export_conllu)

SEED, MAX_LEN = 13, 512
set_seed(SEED)
MODEL_NAME = "dbmdz/bert-base-turkish-cased"
MODEL_REVISION = "b6e1de16c983e0f2c70664591ea3f22810072608"
data_dir = Path(os.environ["UD_IMST_DIR"])
paths = {split: data_dir / f"tr_imst-ud-{split}.conllu" for split in ["train", "dev", "test"]}
train_sents, train_labels = load_conllu(paths["train"])
dev_sents, dev_labels = load_conllu(paths["dev"])
test_sents, test_labels = load_conllu(paths["test"])

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, revision=MODEL_REVISION, use_fast=True)
all_labels = sorted({label for sent in train_labels for label in sent})
label2id = {label: i for i, label in enumerate(all_labels)}
id2label = {i: label for label, i in label2id.items()}
train_dataset = training_rows(train_sents, train_labels, tokenizer, label2id, MAX_LEN)
assert sum(sum(label != -100 for label in row["labels"]) for row in train_dataset) == sum(map(len, train_sents))
print(f"training sentences: {len(train_sents)}; chunks: {len(train_dataset)}")

model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME, revision=MODEL_REVISION, num_labels=len(label2id),
    id2label=id2label, label2id=label2id)
training_args = TrainingArguments(
    output_dir="berturk-morph-tagger", num_train_epochs=5, seed=SEED,
    per_device_train_batch_size=16, learning_rate=2e-5, warmup_ratio=0.1,
    eval_strategy="no", save_strategy="no", report_to="none",
)
trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset,
                  processing_class=tokenizer,
                  data_collator=DataCollatorForTokenClassification(tokenizer))
trainer.train()
trainer.save_model("berturk-morph-tagger/final")
tokenizer.save_pretrained("berturk-morph-tagger/final")

results = {}
for split, sents, labels in [("dev", dev_sents, dev_labels), ("test", test_sents, test_labels)]:
    predictions = [predict_words(words, model, tokenizer, id2label, MAX_LEN) for words in sents]
    results[split] = score_predictions(predictions, labels, label2id)
    export_conllu(paths[split], predictions, f"berturk-morph-tagger/{split}.conllu")
    print(split, results[split])
manifest = {
    "ud_release": "2.17", "model": MODEL_NAME, "revision": MODEL_REVISION,
    "seed": SEED, "max_length": MAX_LEN, "epochs": 5,
    "checkpoint_policy": "fixed final epoch; no selection on test",
    "data_sha256": {split: hashlib.sha256(path.read_bytes()).hexdigest() for split, path in paths.items()},
    "versions": {name: importlib.metadata.version(name) for name in ["torch", "transformers", "accelerate"]},
    "training_sentences": len(train_sents), "training_chunks": len(train_dataset),
    "scores": results,
}
Path("berturk-morph-tagger/run.json").write_text(json.dumps(manifest, indent=2) + "\n")

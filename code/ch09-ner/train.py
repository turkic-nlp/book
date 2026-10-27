"""Sequential training blocks from Chapter 9. Run from the book root. The book reports no fine-tuned score from it."""

# Tested mechanics: transformers==5.3.0 datasets==4.6.1 seqeval==1.2.2
# torch==2.10.0 accelerate==1.12.0; install sentencepiece for the tokenizer.
# Run from the book root, with the pinned KazNERD clone at KazNERD/.
# Record the versions you used: they are saved with the model below.
import json, random, sys, hashlib
from importlib.metadata import version
from pathlib import Path
sys.path.insert(0, str(Path("code/ch09-ner").resolve()))
from ner_utils import read_iob2, valid_iob2, repair_training_iob2, align_batch, tag_sequences

import numpy as np
import torch
import transformers
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
)
from seqeval.metrics import classification_report, f1_score
from seqeval.scheme import IOB2

SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

ROOT = Path("KazNERD/KazNERD")      # git clone https://github.com/IS2AI/KazNERD then git checkout bd4333d0f5952b9fafb2ef2ac2fefa0ad3c0333f
raw = {split: read_iob2(ROOT / f"IOB2_{name}.txt")
       for split, name in [("train", "train"), ("validation", "valid"), ("test", "test")]}

label_names = ["O"] + sorted({t for _, tags in raw["train"] for t in tags} - {"O"})
label2id = {label: i for i, label in enumerate(label_names)}
id2label = {i: label for label, i in label2id.items()}

for split, sents in raw.items():
    unseen = {t for _, tags in sents for t in tags} - set(label_names)
    invalid = sum(not valid_iob2(tags) for _, tags in sents)
    assert not unseen, (split, unseen)          # every tag must be known from training
    print(f"{split:<10} {len(sents):>6} sentences  longest {max(len(t) for t, _ in sents)} words"
          f"  invalid IOB2: {invalid}")
print(len(label_names), "labels:", label_names[:5], "...")

if any(not valid_iob2(tags) for split in ("validation", "test") for _, tags in raw[split]):
    raise ValueError("malformed evaluation gold; resolve the source before scoring")
raw["train"], training_repairs = repair_training_iob2(raw["train"])

dataset = DatasetDict({
    split: Dataset.from_dict({"tokens": [t for t, _ in sents],
                              "ner_tags": [[label2id[x] for x in g] for _, g in sents]})
    for split, sents in raw.items()
})

MODEL_NAME = "FacebookAI/xlm-roberta-large"
MODEL_REVISION = "c23d21b0620b635a76227c604d44e43a9f0ee389"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, revision=MODEL_REVISION)
MAX_LEN = 512


def tokenise_and_align(examples):
    return align_batch(examples, tokenizer, MAX_LEN)


tokenised_dataset = dataset.map(tokenise_and_align, batched=True,
                                remove_columns=dataset["train"].column_names)

def to_tag_sequences(predictions, labels):
    return tag_sequences(predictions, labels, id2label)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    true_tags, pred_tags = to_tag_sequences(np.argmax(logits, axis=-1), labels)
    return {
        "micro_f1": float(f1_score(true_tags, pred_tags, average="micro", mode="strict", scheme=IOB2, zero_division=0)),
        "macro_f1": float(f1_score(true_tags, pred_tags, average="macro", mode="strict", scheme=IOB2, zero_division=0)),
    }

model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME, revision=MODEL_REVISION, num_labels=len(label_names), id2label=id2label, label2id=label2id)

use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
use_fp16 = torch.cuda.is_available() and not use_bf16     # mixed precision only where supported

training_args = TrainingArguments(
    output_dir="xlmr-kaznerd",
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    learning_rate=1e-5,
    warmup_ratio=0.1,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="micro_f1",       # the named development metric
    bf16=use_bf16,
    fp16=use_fp16,
    seed=SEED,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenised_dataset["train"],
    eval_dataset=tokenised_dataset["validation"],
    processing_class=tokenizer,             # `tokenizer=` in transformers < 4.46
    data_collator=DataCollatorForTokenClassification(tokenizer),
    compute_metrics=compute_metrics,
)
trainer.train()

# Save everything needed to reproduce the predictions
out = Path("xlmr-kaznerd/best")
trainer.save_model(out)
tokenizer.save_pretrained(out)
(out / "run_info.json").write_text(json.dumps({
    "labels": label_names, "seed": SEED, "kaznerd_commit": "bd4333d0f5952b9fafb2ef2ac2fefa0ad3c0333f",
    "model_revision": MODEL_REVISION, "training_repairs": training_repairs,
    "data_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob("IOB2_*.txt")},
    "scorer": {"mode": "strict", "scheme": "IOB2", "seqeval": version("seqeval")},
    "dependencies": {name: version(name) for name in ("datasets", "accelerate", "numpy", "sentencepiece")},
    "versions": {"transformers": transformers.__version__, "torch": torch.__version__},
}, indent=2))

pred = trainer.predict(tokenised_dataset["test"])
true_tags, pred_tags = to_tag_sequences(np.argmax(pred.predictions, axis=-1), pred.label_ids)
print(compute_metrics((pred.predictions, pred.label_ids)))
print(classification_report(true_tags, pred_tags, mode="strict", scheme=IOB2, digits=3))

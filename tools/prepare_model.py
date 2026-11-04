#!/usr/bin/env python3
"""Bundle an already-downloaded 5-second Omnilingual CoreML export, without uploading audio.

Usage: python tools/prepare_model.py /path/to/Omnilingual-ASR-CTC-300M-CoreML-INT8
Requires sentencepiece. Model artifacts remain ignored by Git.
"""
import argparse
import json
from pathlib import Path
import shutil
import sentencepiece as spm

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
args = parser.parse_args()
config = json.loads((args.source / "config.json").read_text())
assert config["sample_rate"] == 16000 and config["input_samples"] == 80000
tokenizer = spm.SentencePieceProcessor(model_file=str(args.source / "tokenizer.model"))
pieces = [None if i < 4 or tokenizer.is_control(i) or tokenizer.is_unknown(i)
          or tokenizer.is_unused(i) or tokenizer.is_byte(i) else tokenizer.id_to_piece(i)
          for i in range(tokenizer.get_piece_size())]
assert len(pieces) == 10288
destination = Path(__file__).resolve().parents[1] / "App/Resources/Omnilingual"
destination.mkdir(parents=True, exist_ok=True)
shutil.copytree(args.source / "omnilingual-ctc-300m-int8.mlmodelc",
                destination / "model.mlmodelc", dirs_exist_ok=True)
(destination / "vocabulary.json").write_text(json.dumps(pieces, ensure_ascii=False))
print(f"Prepared 5-second model and {len(pieces)} vocabulary entries; artifacts stay outside Git")

# ==============================================================================
# MindShield Backend — PyTorch SMS Dataset Module
# Phase 3.4: Dataset Abstraction for Transformer Tokenization & DataLoader
# ==============================================================================

from typing import Any, Dict, List

import torch
from torch.utils.data import Dataset


class SMSDataset(Dataset):
    """PyTorch Dataset for SMS threat classification with DistilBERT.

    Tokenizes raw text payloads using subword WordPiece encoding.
    """

    def __init__(
        self,
        texts: List[str],
        labels: List[int],
        tokenizer: Any,
        max_length: int = 64,
    ):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        """Return total number of dataset items."""
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Fetch tokenized item tensors by index."""
        text = str(self.texts[idx])
        label = int(self.labels[idx])

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long),
        }

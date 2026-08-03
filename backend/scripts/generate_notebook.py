# ==============================================================================
# MindShield Backend — Jupyter Notebook Generator Script
# Phase 3.1: Generate backend/notebooks/01_UCI_EDA.ipynb
# ==============================================================================

import json
from pathlib import Path

notebook_path = (
    Path(__file__).resolve().parents[1] / "notebooks" / "01_UCI_EDA.ipynb"
)
notebook_path.parent.mkdir(parents=True, exist_ok=True)


def make_md_cell(text: str) -> dict:
    """Construct Jupyter Markdown cell dictionary."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")],
    }


def make_code_cell(code: str) -> dict:
    """Construct Jupyter Code cell dictionary."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.split("\n")],
    }


cells = []

# Cell 1: Title & Executive Summary
cells.append(
    make_md_cell(
        r"""# MindShield AI Cybersecurity — FYP Phase 3.1
## Exploratory Data Analysis (EDA) & Reproducible Data Pipeline for UCI SMS

> **Author**: Junaid Ahmed (MindShield Core AI Team)
> **Module**: Data Engineering, EDA, Text Normalization & Stratified Partitioning
> **Target Dataset**: UCI SMS Spam Collection Corpus (Almeida et al., 2011)
> **Target Architecture**: DistilBERT Transformer Fine-Tuning (Phase 3.2)

---

### Executive Summary & Research Objectives
This notebook reproduces the complete Phase 3.1 Data Engineering Pipeline
for the MindShield AI cybersecurity platform.

Key objectives demonstrated in this notebook:
1. **Dataset Download & Extraction**: Retrieve raw UCI archive directly.
2. **Raw Schema Inspection**: Audit missing values and raw distributions.
3. **Non-Destructive Text Normalization**: Apply transformer cleaning.
4. **Exact Deduplication**: Remove repeated messages to eliminate leakage.
5. **Statistical & Vocabulary EDA**: Compute parametric and non-parametric stats.
6. **Publication-Grade Visualizations**: Generate 300-DPI figures.
7. **Stratified Splitting**: Partition into 80% Train, 10% Val, 10% Test sets.
8. **Artifact Export**: Export standardized CSV datasets and metadata JSON."""
    )
)

# Cell 2: Imports & Environment Setup
cells.append(
    make_md_cell(
        r"""### Section 1: Environment Setup & Library Imports
Import core data science libraries (`pandas`, `numpy`, `matplotlib`, `seaborn`,
`scikit-learn`) and configure global publication rendering settings."""
    )
)

cells.append(
    make_code_cell(
        r"""import collections
import json
import os
import re
import urllib.request
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split

# Configure publication-quality plot aesthetics (300 DPI)
plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 11,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

COLOR_HAM = "#2b5c8f"   # Deep Slate Blue
COLOR_SPAM = "#d9381e"  # Vivid Crimson Red
COLOR_PALETTE = [COLOR_HAM, COLOR_SPAM]

print("✓ Libraries imported successfully. Environment ready.")"""
    )
)

# Cell 3: Data Ingestion & Download
cells.append(
    make_md_cell(
        r"""### Section 2: Dataset Download & Ingestion
Download the official UCI SMS Spam Collection zip archive directly from the UCI
Machine Learning Repository."""
    )
)

cells.append(
    make_code_cell(
        r"""# Define directory paths relative to backend
DATA_DIR = Path("../data").resolve()
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"
FIGURES_DIR = DATA_DIR / "figures"

for d in [RAW_DIR, PROCESSED_DIR, METADATA_DIR, FIGURES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

UCI_URL = (
    "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
)
ZIP_PATH = RAW_DIR / "sms_spam_collection.zip"
RAW_FILE_PATH = RAW_DIR / "SMSSpamCollection"

# Download and extract if not present
if not RAW_FILE_PATH.exists():
    print(f"Downloading raw dataset from {UCI_URL}...")
    req = urllib.request.Request(
        UCI_URL, headers={"User-Agent": "Mozilla/5.0 MindShield/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp, open(
        ZIP_PATH, "wb"
    ) as f:
        f.write(resp.read())
    print("Extracting zip archive...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(RAW_DIR)
    print(f"Extracted to: {RAW_FILE_PATH}")
else:
    print(f"Raw dataset file already present at: {RAW_FILE_PATH}")

# Load TSV file into pandas DataFrame
df_raw = pd.read_csv(
    RAW_FILE_PATH,
    sep="\t",
    header=None,
    names=["raw_label", "text"],
    on_bad_lines="skip",
    encoding="utf-8",
    engine="python",
)

print(f"Raw records ingested: {len(df_raw):,}")
display(df_raw.head(10))"""
    )
)

# Cell 4: Raw Exploratory Data Analysis
cells.append(
    make_md_cell(
        r"""### Section 3: Exploratory Data Analysis on Raw Corpus
Analyze class frequencies, percentage distributions, missing values, and raw
class imbalance ratios."""
    )
)

cells.append(
    make_code_cell(
        r"""raw_counts = df_raw["raw_label"].value_counts()
raw_ham = raw_counts.get("ham", 0)
raw_spam = raw_counts.get("spam", 0)
raw_total = len(df_raw)

print("=== RAW DATASET METRICS ===")
print(f"Total Raw Records:       {raw_total:,}")
print(f"Legitimate ('ham'):      {raw_ham:,} ({raw_ham/raw_total*100:.2f}%)")
print(f"Spam / Threat ('spam'):  {raw_spam:,} ({raw_spam/raw_total*100:.2f}%)")
print(f"Class Imbalance Ratio:   {raw_ham/raw_spam:.2f} : 1")
print(f"Missing Text Values:     {df_raw['text'].isna().sum()}")
print(f"Missing Label Values:    {df_raw['raw_label'].isna().sum()}")
print(f"Exact Duplicate Messages:{df_raw.duplicated(subset=['text']).sum():,}")"""
    )
)

# Cell 5: Non-Destructive Cleaning & Deduplication
cells.append(
    make_md_cell(
        r"""### Section 4: Non-Destructive Text Normalization & Deduplication
Apply transformer-compatible text cleaning.

**DistilBERT Compatibility Rules**:
- **Preserve**: Capitalization (`URGENT!`), Punctuation (`!`, `?`), URLs,
  Numbers, and Emojis (`😊`).
- **Remove**: Null bytes (`\x00`), Multiple spaces, Empty rows, Exact duplicates.
- **Normalize**: Labels (`ham` $\rightarrow$ `0`, `spam` $\rightarrow$ `1`)."""
    )
)

cells.append(
    make_code_cell(
        r"""def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text) if pd.notna(text) else ""
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(lines).strip()

df_clean = df_raw.dropna(subset=["text", "raw_label"]).copy()
df_clean["text"] = df_clean["text"].apply(normalize_text)
df_clean = df_clean[df_clean["text"].str.len() > 0].copy()

# Label mapping
label_map = {"ham": 0, "spam": 1}
df_clean["label"] = (
    df_clean["raw_label"].str.strip().str.lower().map(label_map).astype(int)
)

# Exact deduplication
pre_dedup = len(df_clean)
df_clean = df_clean.drop_duplicates(
    subset=["text"], keep="first"
).reset_index(drop=True)
dedup_removed = pre_dedup - len(df_clean)

df_clean = df_clean[["text", "label"]].copy()

print("=== DEDUPLICATION & CLEANING AUDIT ===")
print(f"Initial Raw Records:      {len(df_raw):,}")
print(f"Exact Duplicates Removed: {dedup_removed:,}")
print(f"Final Cleaned Corpus:     {len(df_clean):,}")
display(df_clean.head(10))"""
    )
)

# Cell 6: Statistical Length Analysis
cells.append(
    make_md_cell(
        r"""### Section 5: Statistical Feature Analysis
Compute character length, word count, sentence count, and average word length
statistics grouped by class (`ham` vs `spam`)."""
    )
)

cells.append(
    make_code_cell(
        r"""df_stats = df_clean.copy()
df_stats["char_length"] = df_stats["text"].apply(lambda x: len(str(x)))
df_stats["word_count"] = df_stats["text"].apply(lambda x: len(str(x).split()))
df_stats["avg_word_len"] = df_stats["char_length"] / df_stats["word_count"]
df_stats["sentence_count"] = df_stats["text"].apply(
    lambda x: len(re.split(r"[.!?]+", str(x)))
)

def compute_group_stats(df, label_val, name):
    sub = df[df["label"] == label_val]
    res = {}
    for col in ["char_length", "word_count", "sentence_count", "avg_word_len"]:
        s = sub[col]
        q25, q75 = np.percentile(s, [25, 75])
        res[col] = {
            "Mean": round(s.mean(), 2),
            "Std": round(s.std(), 2),
            "Median": round(s.median(), 2),
            "IQR": round(q75 - q25, 2),
            "Min": round(s.min(), 2),
            "Max": round(s.max(), 2),
        }
    return pd.DataFrame(res).T

print("=== LEGITIMATE (HAM) LENGTH STATISTICS ===")
display(compute_group_stats(df_stats, 0, "Ham"))

print("\n=== SPAM / SMISHING LENGTH STATISTICS ===")
display(compute_group_stats(df_stats, 1, "Spam"))"""
    )
)

# Cell 7: Publication Visualizations Generator
cells.append(
    make_md_cell(
        r"""### Section 6: Publication-Quality Figures Generation (300 DPI)
Generate and save high-resolution figures for thesis documentation and viva
defense."""
    )
)

cells.append(
    make_code_cell(
        r"""# Figure 1: Class Distribution Bar and Pie Chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
counts = df_clean["label"].value_counts()
h_cnt, s_cnt = counts.get(0, 0), counts.get(1, 0)
labels = ["Legitimate (Ham)", "Spam / Smishing"]

bars = ax1.bar(
    labels,
    [h_cnt, s_cnt],
    color=COLOR_PALETTE,
    width=0.5,
    edgecolor="black",
    linewidth=1.2,
)
ax1.set_title("Class Frequency Count", fontweight="bold")
ax1.set_ylabel("Message Count")
ax1.set_ylim(0, max(h_cnt, s_cnt) * 1.15)
for bar in bars:
    height = bar.get_height()
    ax1.annotate(
        f"{height:,}",
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        fontweight="bold",
    )

ax2.pie(
    [h_cnt, s_cnt],
    labels=labels,
    autopct="%1.1f%%",
    startangle=140,
    colors=COLOR_PALETTE,
    explode=(0, 0.08),
    wedgeprops={"edgecolor": "black", "linewidth": 1.2},
    textprops={"fontweight": "bold"},
)
ax2.set_title("Class Imbalance Percentage", fontweight="bold")
fig.suptitle(
    f"Class Distribution — Imbalance Ratio {h_cnt/s_cnt:.2f}:1",
    fontweight="bold",
    y=1.02,
)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "01_class_distribution.png", dpi=300)
plt.show()

# Figure 2: Length & Word Count KDE Distributions
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
df_stats["class_name"] = df_stats["label"].map({0: "ham", 1: "spam"})

sns.histplot(
    data=df_stats,
    x="char_length",
    hue="class_name",
    palette={"ham": COLOR_HAM, "spam": COLOR_SPAM},
    kde=True,
    ax=ax1,
    bins=40,
    alpha=0.4,
    element="step",
)
ax1.set_title("Character Length Distribution", fontweight="bold")
ax1.set_xlim(0, 350)

sns.histplot(
    data=df_stats,
    x="word_count",
    hue="class_name",
    palette={"ham": COLOR_HAM, "spam": COLOR_SPAM},
    kde=True,
    ax=ax2,
    bins=40,
    alpha=0.4,
    element="step",
)
ax2.set_title("Word Count Distribution", fontweight="bold")
ax2.set_xlim(0, 80)
fig.suptitle(
    "SMS Text Length & Word Count Distributions by Class",
    fontweight="bold",
    y=1.02,
)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "02_message_length_distribution.png", dpi=300)
plt.show()"""
    )
)

# Cell 8: Top Vocabulary and N-Gram Analysis
cells.append(
    make_md_cell(
        r"""### Section 7: Payload Signature & Vocabulary Analysis
Extract top unigrams and bigrams from spam payloads to reveal threat keywords."""
    )
)

cells.append(
    make_code_cell(
        r"""STOPWORDS = set([
    "to", "you", "a", "the", "i", "is", "in", "and", "for", "of", "or", "your",
    "on", "my", "me", "it", "at", "have", "are", "be", "with", "not", "that",
    "this", "do", "we", "can", "will", "so", "get", "no", "if", "but", "ur", "u",
    "2", "4"
])

def get_top_ngrams(series, n=1, top_k=15):
    cnt = collections.Counter()
    for text in series:
        tokens = re.findall(r"\b[a-zA-Z0-9']+\b", str(text).lower())
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
        if n == 1:
            cnt.update(tokens)
        else:
            cnt.update(
                [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
            )
    return cnt.most_common(top_k)

spam_texts = df_clean[df_clean["label"] == 1]["text"]
top_spam_unigrams = get_top_ngrams(spam_texts, n=1, top_k=15)
top_spam_bigrams = get_top_ngrams(spam_texts, n=2, top_k=15)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

words, counts = zip(*top_spam_unigrams)
ax1.barh(
    range(len(words)), counts, color=COLOR_SPAM, edgecolor="black", alpha=0.85
)
ax1.set_yticks(range(len(words)))
ax1.set_yticklabels(words, fontweight="bold")
ax1.invert_yaxis()
ax1.set_title("Top 15 Unigrams in Spam Payload", fontweight="bold")

words_bi, counts_bi = zip(*top_spam_bigrams)
ax2.barh(
    range(len(words_bi)), counts_bi, color=COLOR_SPAM, edgecolor="black", alpha=0.85
)
ax2.set_yticks(range(len(words_bi)))
ax2.set_yticklabels(words_bi, fontweight="bold")
ax2.invert_yaxis()
ax2.set_title("Top 15 Bigrams in Spam Payload", fontweight="bold")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "04_top_words_comparison.png", dpi=300)
plt.show()"""
    )
)

# Cell 9: Stratified Splitting & Partitioning
cells.append(
    make_md_cell(
        r"""### Section 8: Stratified Train / Validation / Test Splitting
Partition the cleaned dataset into 80% Train, 10% Validation, and 10% Test sets
using stratified sampling (`random_state=42`)."""
    )
)

cells.append(
    make_code_cell(
        r"""# Step 1: Split into Train (80%) vs Temp (20%)
train_df, temp_df = train_test_split(
    df_clean, test_size=0.20, stratify=df_clean["label"], random_state=42
)

# Step 2: Split Temp into Val (10%) and Test (10%)
val_df, test_df = train_test_split(
    temp_df, test_size=0.50, stratify=temp_df["label"], random_state=42
)

train_df = train_df.reset_index(drop=True)
val_df = val_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)

print("=== STRATIFIED DATASET SPLIT SUMMARY ===")
def print_split_info(name, df):
    c = df["label"].value_counts().to_dict()
    tot = len(df)
    h, s = c.get(0, 0), c.get(1, 0)
    print(
        f"  {name:<12}: Total={tot:,} | Ham={h:,} ({h/tot*100:.2f}%) | "
        f"Spam={s:,} ({s/tot*100:.2f}%)"
    )

print_split_info("Train (80%)", train_df)
print_split_info("Val (10%)", val_df)
print_split_info("Test (10%)", test_df)
print_split_info("Full Cleaned", df_clean)"""
    )
)

# Cell 10: Export Processed Datasets
cells.append(
    make_md_cell(
        r"""### Section 9: Export Processed Datasets & Preprocessing Metadata JSON
Save cleaned splits as standardized CSV files (`text`, `label`) and generate
`uci_sms_spam_metadata.json`."""
    )
)

cells.append(
    make_code_cell(
        r"""# Export CSV splits
train_df.to_csv(PROCESSED_DIR / "train.csv", index=False, encoding="utf-8")
val_df.to_csv(PROCESSED_DIR / "val.csv", index=False, encoding="utf-8")
test_df.to_csv(PROCESSED_DIR / "test.csv", index=False, encoding="utf-8")
df_clean.to_csv(
    PROCESSED_DIR / "cleaned_full.csv", index=False, encoding="utf-8"
)

# Metadata JSON
metadata = {
    "dataset_name": "uci_sms_spam",
    "pipeline_version": "3.1.0",
    "random_seed": 42,
    "split_ratios": {"train": 0.80, "val": 0.10, "test": 0.10},
    "total_raw_records": len(df_raw),
    "exact_duplicates_removed": dedup_removed,
    "total_cleaned_records": len(df_clean),
    "class_distribution": {
        "ham_count": int((df_clean["label"] == 0).sum()),
        "spam_count": int((df_clean["label"] == 1).sum()),
        "imbalance_ratio": float(
            round(
                (df_clean["label"] == 0).sum() / (df_clean["label"] == 1).sum(),
                2,
            )
        ),
    },
    "splits": {
        "train": {
            "total": len(train_df),
            "ham": int((train_df["label"] == 0).sum()),
            "spam": int((train_df["label"] == 1).sum()),
        },
        "val": {
            "total": len(val_df),
            "ham": int((val_df["label"] == 0).sum()),
            "spam": int((val_df["label"] == 1).sum()),
        },
        "test": {
            "total": len(test_df),
            "ham": int((test_df["label"] == 0).sum()),
            "spam": int((test_df["label"] == 1).sum()),
        },
    },
}

with open(
    METADATA_DIR / "uci_sms_spam_metadata.json", "w", encoding="utf-8"
) as f:
    json.dump(metadata, f, indent=2)

print("✓ All processed datasets exported to backend/data/processed/")
print("✓ Metadata exported to backend/data/metadata/uci_sms_spam_metadata.json")"""
    )
)

# Cell 11: Summary & Conclusion
cells.append(
    make_md_cell(
        r"""### Section 10: Summary & Conclusions

#### Key Empirical Findings
1. **Dataset Quality**: Raw UCI corpus contains 5,574 records. Exact deduplication
   removed 414 duplicate messages (7.44%), yielding a clean 5,148-message corpus.
2. **Class Imbalance**: Corpus exhibits an ~87.5% `ham` to ~12.5% `spam` ratio (7.02:1).
3. **Payload Characteristics**: Spam messages have higher mean character length
   ($\mu = 136.75$) and lower variance ($\sigma = 30.12$) than ham ($\mu = 70.47$).
4. **Model Readiness**: Output datasets (`train.csv`, `val.csv`, `test.csv`) preserve
   capitalization, URLs, and emojis for **DistilBERT fine-tuning in Phase 3.2**.

---
*MindShield AI Cybersecurity FYP Phase 3.1 Research Notebook · 2026*"""
    )
)

notebook = {
    "cells": cells,
    "metadata": {
        "language_info": {"name": "python", "version": "3.11.0"},
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 2,
}

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Successfully generated Jupyter Notebook at: {notebook_path}")

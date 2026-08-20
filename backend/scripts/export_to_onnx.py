# ==============================================================================
# MindShield Backend — ONNX Model Export Script
# Phase 4.1: Exporting distilbert_pakscam_v3 to ONNX format
# ==============================================================================

import os
import shutil
import json
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def main():
    print("=" * 80)
    print("  MINDSHIELD MODEL DEPLOYMENT — EXPORT PYTORCH TO ONNX  ")
    print("=" * 80)

    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, "data", "models", "distilbert_pakscam_v3")
    export_dir = os.path.join(base_dir, "data", "models", "distilbert_pakscam_v3_onnx")

    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"Selected champion model not found at: {model_dir}")

    print(f"Loading PyTorch model and tokenizer from: {model_dir}...")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()

    # Create target deployment directory
    os.makedirs(export_dir, exist_ok=True)
    print(f"Export target directory: {export_dir}")

    # Prepare dummy input for ONNX export tracing
    dummy_text = "MindShield baseline message for tracing ONNX graph."
    inputs = tokenizer(
        dummy_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    onnx_file_path = os.path.join(export_dir, "model.onnx")
    print(f"Exporting model to ONNX format (opset 14)...")

    # Export model using torch.onnx.export
    torch.onnx.export(
        model,
        args=(input_ids, attention_mask),
        f=onnx_file_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"}
        },
        opset_version=14
    )

    print(f"[OK] ONNX model graph exported successfully to: {onnx_file_path}")

    # Save tokenizer files to export directory
    print("Saving tokenizer configuration and vocabulary files...")
    tokenizer.save_pretrained(export_dir)

    # Explicitly copy required JSON files for packaging
    files_to_copy = ["config.json", "label_mapping.json"]
    for file_name in files_to_copy:
        src = os.path.join(model_dir, file_name)
        dst = os.path.join(export_dir, file_name)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"Copied {file_name} -> {dst}")
        else:
            print(f"[Warning] Required file {file_name} missing from source directory!")

    # Verify final deployment contents
    print("\nVerified Deployment Artifacts:")
    for f in os.listdir(export_dir):
        path = os.path.join(export_dir, f)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"  - {f:<25} ({size_mb:.4f} MB)")

    print("=" * 80)
    print("Export pipeline completed successfully. Model is ready for on-device deployment.")
    print("=" * 80)

if __name__ == "__main__":
    main()

# ==============================================================================
# MindShield Backend — ONNX Validation Script
# Phase 4.2: Comparing PyTorch vs ONNX Inference Equivalence
# ==============================================================================

import os
import json
import torch
import numpy as np
import pandas as pd
import onnxruntime as ort
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 15 Localised regression test cases from the promotion gate test suite
REGRESSION_CASES = [
    ("PKR 5,030 received from ILAM UL DIN* in your UBL A/C *5034 on 04-AUG-2026 19:53 via IBFT. Tx ID 6940522193. For info: 111825888.", "safe", "ubl_ibft_receipt"),
    ("JUNAID AHMED A/C *5034 is debited with PKR 5,000 on 04/08/26 at 20:13 from ATM. For info: 111825888.", "safe", "ubl_atm_debit"),
    ("Dear UBL Customer,\nYou may log your complaints via our Contact Center, Email, Website, Mobile App, Social Media, Branches or visit: https://bit.ly/2WceaFA", "safe", "ubl_customer_service_bitly"),
    ("50% OFF Only 4 You! Make the most of Z Hour sale from 5PM-9PM & get 50% OFF on WhatsApp Plus Bundle in My Zong App. Tap now: bit.ly/3rY7XHq", "safe", "zong_50_percent_off"),
    ("Thanks for subscribing to Gaming Royale at Rs 11.95/Day (Auto Renewal). Play live Games on http://z.gamingroyale.club. To Unsub click http://z.gamingroyale.club/u", "safe", "gaming_royale_subscription"),
    ("You have unlocked ONE Day FREE Trial of Gaming Royale and will be charged Rs 11.95/Day (Auto renewal) tomorrow. To Unsub click http://z.gamingroyale.club/u", "safe", "gaming_royale_free_trial"),
    ("Your ReadCash is Overdue! Save on the next weekly fee of Rs 160 (applied in 2 days) by repaying your ReadyCash Rs 3151.18 now by dialing *786*4*2#.", "safe", "readycash_overdue"),
    ("1 DAY LEFT! Your ReadyCash loan is due tomorrow! Make sure to Dial *786*4*2# to repay your Rs 3151.18 on time and to be able to borrow again!", "safe", "readycash_1_day_left"),
    ("Jeetne ke liye tayyar ho jao! aur jeeto bade inaam, Zong Engage ke taraf se khaas http://games.zongengage.com.pk 6PKR/Day, Reply 1 ke saath on 4263", "safe", "zong_engage_prize_lang"),
    ("Congratulations! You have won PKR 100,000. Click http://example.com to claim your prize immediately.", "phishing", "prize_phishing"),
    ("HBL Alert: Your account will be blocked in 24 hours due to pending verification. Update now: http://hbl-secure-login.xyz", "phishing", "fake_bank_verification"),
    ("Your UBL account has been suspended. Verify your account immediately by clicking http://example.com/login", "phishing", "fake_account_suspension"),
    ("Dear Customer, share your 6-digit OTP code with our support team to stop unauthorized transaction of PKR 45,000.", "phishing", "otp_phishing"),
    ("BISP ki taraf se 25,000 rupay approved hain. Abhi claim karein 0312-9876543 par call kar ke.", "phishing", "bisp_roman_urdu_scam"),
]

def softmax(x):
    """Numerically stable softmax."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=-1)

def main():
    print("=" * 80)
    print("  MINDSHIELD MODEL VALIDATION — PYTORCH VS ONNX EQUIVALENCE  ")
    print("=" * 80)

    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pytorch_dir = os.path.join(base_dir, "data", "models", "distilbert_pakscam_v3")
    onnx_dir = os.path.join(base_dir, "data", "models", "distilbert_pakscam_v3_onnx")
    onnx_file = os.path.join(onnx_dir, "model.onnx")

    if not os.path.exists(pytorch_dir):
        raise FileNotFoundError(f"PyTorch model directory missing: {pytorch_dir}")
    if not os.path.exists(onnx_file):
        raise FileNotFoundError(f"ONNX model file missing: {onnx_file}")

    print(f"Loading original PyTorch model from: {pytorch_dir}...")
    tokenizer = AutoTokenizer.from_pretrained(onnx_dir)
    pytorch_model = AutoModelForSequenceClassification.from_pretrained(pytorch_dir)
    pytorch_model.eval()

    print(f"Loading exported ONNX model from: {onnx_file}...")
    ort_session = ort.InferenceSession(onnx_file, providers=["CPUExecutionProvider"])

    # Load label mapping
    map_file = os.path.join(onnx_dir, "label_mapping.json")
    with open(map_file, "r") as f:
        label_mapping = json.load(f)
    id2label = {int(k): v for k, v in label_mapping["id2label"].items()}
    print(f"Label mapping loaded: {id2label}")

    # Build evaluation set: 14 regression cases + 50 test samples
    test_texts = []
    test_sources = []
    
    # 1. Add regression cases
    for text, expected, tid in REGRESSION_CASES:
        test_texts.append(text)
        test_sources.append(f"regression:{tid}")

    # 2. Add samples from processed test.csv if exists
    test_csv = os.path.join(base_dir, "data", "processed", "test.csv")
    if os.path.exists(test_csv):
        print(f"Loading test samples from: {test_csv}...")
        df = pd.read_csv(test_csv)
        df_samples = df.sample(n=min(50, len(df)), random_state=42)
        for _, row in df_samples.iterrows():
            test_texts.append(str(row["text"]))
            test_sources.append("uci_test_set")
    else:
        print("[Warning] test.csv not found, proceeding with regression cases only.")

    print(f"Total test instances to compare: {len(test_texts)}")

    # Comparative evaluation loop
    diff_logits = []
    diff_probs = []
    mismatch_count = 0
    records = []

    print("\nComparing predictions side-by-side...")
    for i, (text, src) in enumerate(zip(test_texts, test_sources)):
        # Tokenize inputs
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        
        # PyTorch Inference
        with torch.no_grad():
            outputs = pytorch_model(**inputs)
            pt_logits = outputs.logits[0].numpy()
            pt_probs = torch.softmax(outputs.logits[0], dim=-1).numpy()
            pt_class = int(torch.argmax(outputs.logits[0]).item())
            pt_confidence = float(pt_probs[pt_class])

        # ONNX Runtime Inference
        onnx_inputs = {
            "input_ids": inputs["input_ids"].numpy(),
            "attention_mask": inputs["attention_mask"].numpy()
        }
        ort_outputs = ort_session.run(None, onnx_inputs)
        ort_logits = ort_outputs[0][0]
        ort_probs = softmax(ort_logits)
        ort_class = int(np.argmax(ort_logits))
        ort_confidence = float(ort_probs[ort_class])

        # Calculate metrics difference
        l_inf_logits = np.max(np.abs(pt_logits - ort_logits))
        l_inf_probs = np.max(np.abs(pt_probs - ort_probs))
        
        diff_logits.append(l_inf_logits)
        diff_probs.append(l_inf_probs)

        # Check for class equivalence
        match = (pt_class == ort_class)
        if not match:
            mismatch_count += 1
            print(f"  [MISMATCH] Sample {i} ({src}): Class difference!")

        records.append({
            "index": i,
            "source": src,
            "text": text[:60] + "..." if len(text) > 60 else text,
            "pt_logits": pt_logits.tolist(),
            "ort_logits": ort_logits.tolist(),
            "pt_probs": pt_probs.tolist(),
            "ort_probs": ort_probs.tolist(),
            "pt_label": id2label[pt_class],
            "ort_label": id2label[ort_class],
            "pt_conf": pt_confidence,
            "ort_conf": ort_confidence,
            "logit_diff": float(l_inf_logits),
            "prob_diff": float(l_inf_probs),
            "equivalent": match
        })

    # Print summary statistics
    mean_logit_diff = np.mean(diff_logits)
    max_logit_diff = np.max(diff_logits)
    mean_prob_diff = np.mean(diff_probs)
    max_prob_diff = np.max(diff_probs)

    print("\n" + "=" * 80)
    print("  VALUATION COMPARISON SUMMARY")
    print("=" * 80)
    print(f"  Class Equivalence Pass Rate : {((len(test_texts) - mismatch_count) / len(test_texts)):.2%}")
    print(f"  Class Mismatches            : {mismatch_count} / {len(test_texts)}")
    print(f"  Mean Logit Max-Difference   : {mean_logit_diff:.8e}")
    print(f"  Max Logit Max-Difference    : {max_logit_diff:.8e}")
    print(f"  Mean Probability Difference : {mean_prob_diff:.8e}")
    print(f"  Max Probability Difference  : {max_prob_diff:.8e}")
    print("=" * 80)

    # Output representative comparisons
    print("\nRepresentative Comparisons (First 5 Regression Cases):")
    for r in records[:5]:
        print(f"\n[{r['source']}] Text: {r['text']}")
        print(f"  PyTorch -> Label: {r['pt_label']:<8} Conf: {r['pt_conf']:.4f} Logits: {r['pt_logits']}")
        print(f"  ONNX    -> Label: {r['ort_label']:<8} Conf: {r['ort_conf']:.4f} Logits: {r['ort_logits']}")
        print(f"  Equivalence: {r['equivalent']} (Logit Diff: {r['logit_diff']:.2e})")

    # Output representative comparisons for phishing cases
    print("\nRepresentative Comparisons (First 3 Phishing Regression Cases):")
    phishing_cases = [r for r in records if r["pt_label"] == "spam"]
    for r in phishing_cases[:3]:
        print(f"\n[{r['source']}] Text: {r['text']}")
        print(f"  PyTorch -> Label: {r['pt_label']:<8} Conf: {r['pt_conf']:.4f} Logits: {r['pt_logits']}")
        print(f"  ONNX    -> Label: {r['ort_label']:<8} Conf: {r['ort_conf']:.4f} Logits: {r['ort_logits']}")
        print(f"  Equivalence: {r['equivalent']} (Logit Diff: {r['logit_diff']:.2e})")

    # Check limits
    tolerance = 1e-4
    assert mismatch_count == 0, f"Error: {mismatch_count} class mismatches detected!"
    assert max_logit_diff < tolerance, f"Error: Logit difference {max_logit_diff} exceeds tolerance {tolerance}!"
    print(f"\n[SUCCESS] Mathematical equivalence verified within tolerance of {tolerance}!")

    # Save validation report json
    report_path = os.path.join(base_dir, "data", "metadata", "onnx_validation_comparison.json")
    summary_report = {
        "summary": {
            "total_samples": len(test_texts),
            "mismatch_count": mismatch_count,
            "equivalence_pass": mismatch_count == 0,
            "mean_logit_diff": float(mean_logit_diff),
            "max_logit_diff": float(max_logit_diff),
            "mean_prob_diff": float(mean_prob_diff),
            "max_prob_diff": float(max_prob_diff),
            "tolerance": tolerance
        },
        "records": records
    }
    with open(report_path, "w") as f:
        json.dump(summary_report, f, indent=2)
    print(f"[Saved] Validation comparison report to: {report_path}")

if __name__ == "__main__":
    main()

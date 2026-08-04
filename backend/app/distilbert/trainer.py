# ==============================================================================
# MindShield Backend — DistilBERT Fine-Tuning Trainer Module
# Phase 3.4: PyTorch & Hugging Face Transformer Fine-Tuning Execution Engine
# ==============================================================================

import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

import torch
from torch.utils.data import DataLoader
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)
from sklearn.metrics import accuracy_score, f1_score

from app.distilbert.config import DistilBERTConfig
from app.distilbert.dataset import SMSDataset
from app.distilbert.evaluator import DistilBERTEvaluator
from app.nlp.pipeline import NLPPreprocessingPipeline


class DistilBERTTrainer:
    """Fine-tuning trainer for DistilBERT SMS classification model."""

    def __init__(self, config: Optional[DistilBERTConfig] = None):
        self.config = config or DistilBERTConfig()
        self.pipeline = NLPPreprocessingPipeline()
        self.evaluator = DistilBERTEvaluator(self.config.figures_output_dir)

        # Set random seeds and CPU multithreading for speed
        torch.set_num_threads(min(8, os.cpu_count() or 4))
        torch.manual_seed(self.config.seed)
        np.random.seed(self.config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.config.seed)

        print(
            f"[DistilBERT] Initializing AutoTokenizer "
            f"({self.config.model_name})...",
            flush=True,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)

    def train_and_evaluate(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fine-tune DistilBERT on train/val sets and evaluate on test set."""
        print(
            "[DistilBERT] Preprocessing datasets with Light Transformer...",
            flush=True,
        )
        train_clean = [
            p["final_processed_text"]
            for p in self.pipeline.preprocess_corpus(train_df["text"].tolist())
        ]
        val_clean = [
            p["final_processed_text"]
            for p in self.pipeline.preprocess_corpus(val_df["text"].tolist())
        ]
        test_clean = [
            p["final_processed_text"]
            for p in self.pipeline.preprocess_corpus(test_df["text"].tolist())
        ]

        train_labels = train_df["label"].tolist()
        val_labels = val_df["label"].tolist()
        test_labels = test_df["label"].tolist()

        train_ds = SMSDataset(
            train_clean, train_labels, self.tokenizer, self.config.max_length
        )
        val_ds = SMSDataset(
            val_clean, val_labels, self.tokenizer, self.config.max_length
        )
        test_ds = SMSDataset(
            test_clean, test_labels, self.tokenizer, self.config.max_length
        )

        train_loader = DataLoader(
            train_ds, batch_size=self.config.batch_size, shuffle=True
        )
        val_loader = DataLoader(
            val_ds, batch_size=self.config.batch_size, shuffle=False
        )
        test_loader = DataLoader(
            test_ds, batch_size=self.config.batch_size, shuffle=False
        )

        print(
            f"[DistilBERT] Instantiating {self.config.model_name} on device: "
            f"{self.config.device}...",
            flush=True,
        )
        model_config = AutoConfig.from_pretrained(
            self.config.model_name,
            num_labels=self.config.num_labels,
            id2label=self.config.id2label,
            label2id=self.config.label2id,
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            self.config.model_name, config=model_config
        )
        model.to(self.config.device)

        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )

        total_steps = len(train_loader) * self.config.epochs
        warmup_steps = int(total_steps * self.config.warmup_ratio)
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps,
        )

        scaler = torch.amp.GradScaler(
            "cuda", enabled=self.config.use_fp16 and self.config.use_gpu
        )

        history: Dict[str, List[float]] = {
            "train_loss": [],
            "val_loss": [],
            "val_accuracy": [],
            "val_f1": [],
        }

        best_val_f1 = 0.0
        best_model_state = None
        patience_counter = 0

        t_train_start = time.perf_counter()
        print(
            f"\n[DistilBERT] Starting Fine-Tuning "
            f"({self.config.epochs} Epochs)...",
            flush=True,
        )

        for epoch in range(1, self.config.epochs + 1):
            model.train()
            running_train_loss = 0.0

            for batch in train_loader:
                optimizer.zero_grad()

                input_ids = batch["input_ids"].to(self.config.device)
                attention_mask = batch["attention_mask"].to(self.config.device)
                labels = batch["labels"].to(self.config.device)

                with torch.amp.autocast(
                    "cuda",
                    enabled=self.config.use_fp16 and self.config.use_gpu,
                ):
                    outputs = model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels,
                    )
                    loss = outputs.loss

                if self.config.use_fp16 and self.config.use_gpu:
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    loss.backward()
                    optimizer.step()

                scheduler.step()
                running_train_loss += loss.item()

            avg_train_loss = running_train_loss / len(train_loader)

            val_metrics = self._evaluate_loader(model, val_loader)
            val_loss = val_metrics["loss"]
            val_acc = val_metrics["accuracy"]
            val_f1 = val_metrics["f1_score"]

            history["train_loss"].append(round(avg_train_loss, 4))
            history["val_loss"].append(round(val_loss, 4))
            history["val_accuracy"].append(round(val_acc, 4))
            history["val_f1"].append(round(val_f1, 4))

            print(
                f"  Epoch {epoch}/{self.config.epochs} | "
                f"Train Loss: {avg_train_loss:.4f} | Val Loss: {val_loss:.4f} | "
                f"Val Acc: {val_acc:.4f} | Val F1: {val_f1:.4f}",
                flush=True,
            )

            if val_f1 > best_val_f1:
                best_val_f1 = val_f1
                best_model_state = {
                    k: v.cpu() for k, v in model.state_dict().items()
                }
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= self.config.patience:
                    print(
                        f"  [Early Stopping] No improvement for "
                        f"{self.config.patience} epochs.",
                        flush=True,
                    )
                    break

        train_time_sec = time.perf_counter() - t_train_start

        if best_model_state is not None:
            model.load_state_dict({
                k: v.to(self.config.device)
                for k, v in best_model_state.items()
            })

        print(
            "\n[DistilBERT] Running Final Evaluation on Test Dataset...",
            flush=True,
        )
        t_pred_start = time.perf_counter()
        test_eval_results = self._evaluate_loader(
            model, test_loader, return_probabilities=True
        )
        pred_time_sec = time.perf_counter() - t_pred_start

        y_test = np.array(test_labels)
        y_pred = test_eval_results["y_pred"]
        y_prob = test_eval_results["y_prob"]

        output_dir = self.config.models_output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[DistilBERT] Saving model artifacts to {output_dir}...")
        model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        label_map = {
            "id2label": self.config.id2label,
            "label2id": self.config.label2id,
        }
        with open(
            output_dir / "label_mapping.json", "w", encoding="utf-8"
        ) as f:
            json.dump(label_map, f, indent=2)

        with open(
            output_dir / "training_history.json", "w", encoding="utf-8"
        ) as f:
            json.dump(history, f, indent=2)

        model_files = list(output_dir.glob("*.safetensors")) + list(
            output_dir.glob("*.bin")
        )
        model_size_mb = (
            (model_files[0].stat().st_size / (1024 * 1024))
            if model_files
            else 256.0
        )

        distilbert_metrics = self.evaluator.compute_all_metrics(
            y_test,
            y_pred,
            y_prob,
            train_time_sec,
            pred_time_sec,
            model_size_mb,
        )

        with open(output_dir / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(
                {"metrics": distilbert_metrics, "history": history}, f, indent=2
            )

        _ = self.evaluator.generate_figures(y_test, y_pred, y_prob, history)

        return distilbert_metrics, history

    def _evaluate_loader(
        self,
        model: Any,
        dataloader: DataLoader,
        return_probabilities: bool = False,
    ) -> Dict[str, Any]:
        """Evaluate model on DataLoader."""
        model.eval()
        total_loss = 0.0
        all_preds = []
        all_probs = []
        all_labels = []

        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch["input_ids"].to(self.config.device)
                attention_mask = batch["attention_mask"].to(self.config.device)
                labels = batch["labels"].to(self.config.device)

                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )
                total_loss += outputs.loss.item()

                probs = (
                    torch.softmax(outputs.logits, dim=-1)[:, 1].cpu().numpy()
                )
                preds = torch.argmax(outputs.logits, dim=-1).cpu().numpy()

                all_preds.extend(preds)
                all_probs.extend(probs)
                all_labels.extend(labels.cpu().numpy())

        avg_loss = total_loss / len(dataloader)
        acc = accuracy_score(all_labels, all_preds)
        f1 = float(f1_score(all_labels, all_preds, zero_division=0))

        res = {
            "loss": avg_loss,
            "accuracy": acc,
            "f1_score": f1,
        }

        if return_probabilities:
            res["y_pred"] = np.array(all_preds)
            res["y_prob"] = np.array(all_probs)

        return res

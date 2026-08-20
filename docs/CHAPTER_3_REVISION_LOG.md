# Chapter 3 Revision Log

This log documents the technical and scientific revisions applied to Chapter 3 of the thesis draft.

| Section | Action taken | Rationale |
| :--- | :--- | :--- |
| 3.1 System Architecture (Paragraph 162) | Rewrote to clarify prototype local loopback deployment, plain local HTTP transport, and production privacy requirements. | Corrects false claims of production-grade privacy preservation over local plain HTTP. |
| 3.4 Database Design (Paragraph 172) | Updated text to reference the exact column names of the SQLite database implementation (body, sender, ai_status, confidence_score, detected_threats). | Aligns the database design descriptions with the actual Flutter sqflite implementation. |
| 3.9 Data Preprocessing (Paragraph 193) | Replaced 'WordPiece vocabulary' with 'pre-trained DistilBERT WordPiece tokenizer'. | Accurately represents the tokenization pipeline used in the transformer framework. |
| 3.10 Train/Validation/Test Splitting (Paragraph 194) | Clarified that a validation split exists only for the UCI dataset, and the local PakScam dataset is partitioned into train/test template families. | Aligns the methodology description with the actual train/val/test data pipeline code. |
| 3.13 Testing Methodology (Paragraph 220) | Corrected the testing terminology (tests, test cases, assertions, coverage) and aligned counts (234 Pytests, 5 Flutter tests, 75% coverage). | Aligns testing description with the output of the Pytest coverage and Flutter test runner. |
| 3.14 Evaluation Metrics (Paragraph 222) | Explicitly documented that peak latency (77.51 ms) exceeds the SLA gate, and that mean compliance does not imply worst-case compliance. | Corrects misleading claims of overall latency compliance by separating mean and peak latencies. |

# Chapter 1 — Introduction

This introductory chapter establishes the research background, problem statement, research questions, objectives, scope boundaries, and core contributions of the MindShield platform. It contextualizes the SMS smishing threat in Pakistan, describes the challenges of domain shift and shortcut learning, and outlines the system's structural architecture.

---

## 1.1 Background

Mobile communications have transitioned from luxury utilities to core societal infrastructure. With the rapid digitization of financial systems, utility bill payments, public resource distribution programs (such as the Benazir Income Support Programme - BISP), and multi-factor authentication (MFA) protocols, Short Message Service (SMS) text messages serve as the primary communication medium. 

Despite the growth of internet-based instant messaging applications, SMS remains a critical fallback communication channel due to its high delivery reliability, offline capability, compatibility with legacy feature phones, and independence from internet access. This ubiquity has made the SMS protocol a high-value target for social engineering attacks, specifically SMS phishing (smishing).

---

## 1.2 Mobile Messaging and SMS Security

The Short Message Service (SMS) protocol was designed without native security controls. SMS transmissions lack end-to-end encryption, sender authentication, or cryptographically signed metadata. Consequently, the network layer is vulnerable to:
* **Caller ID Spoofing:** Attackers can manipulate alphanumeric sender IDs (representing banks or telecom brands) without cryptographic validation.
* **Open Interception:** Legitimate user endpoints receive and render arbitrary incoming SMS broadcasts blindly, relying on the user to differentiate benign messages from malicious communications.

As mobile ecosystems digitize, securing the SMS ingestion point on user endpoints is critical to protecting credentials, financial assets, and private communications.

---

## 1.3 SMS Phishing / Smishing

SMS phishing, or **smishing**, is a social engineering attack where an adversary sends a text message designed to deceive the recipient into executing a malicious action. Smishing messages typically exploit psychological triggers—such as urgency, fear, curiosity, or greed—to induce the user to:
1. Reveal sensitive information (OTPs, PINs, passwords, or national ID numbers).
2. Transfer financial assets to malicious accounts.
3. Access malicious links pointing to credential-harvesting websites.

Traditional security measures (such as network-level firewalls or static keyword blacklists) are easily bypassed by spelling modifications, link redirections, or localized language dialects, requiring content-aware natural language processing (NLP) filters.

---

## 1.4 The Pakistani Context

The SMS threat landscape in Pakistan exhibits unique linguistic, socio-economic, and technical characteristics:

* **Urdu Code-Switching & Roman Urdu:** A large portion of local SMS traffic utilizes code-switching (mixing English and Urdu) and is written in **Roman Urdu** (Urdu phonetics written using Latin characters, e.g., `"apka account block ho gaya hai"`). Roman Urdu lacks standardized spelling conventions, creating a sparse and highly variable vocabulary representation.
* **Legitimate Transaction Density:** Due to low smartphone penetration and limited mobile data coverage, local banking (e.g. UBL, HBL) and mobile wallet services (e.g. EasyPaisa, JazzCash) rely heavily on automated SMS receipts. These notifications contain transaction details, account balance indicators, and shortened links (e.g. `bit.ly`).
* **Targeted Scam Vectors:** Adversaries exploit local public welfare program names (such as BISP or Ehsaas) and telecom prize drawings (e.g., Jeeto Pakistan) to target users.

---

## 1.5 Problem Statement

Traditional machine learning-based SMS classifiers achieve high evaluation accuracy on international benchmark datasets, but suffer a severe **domain generalization failure** when deployed in the Pakistani SMS environment. This failure is driven by two core phenomena:

1. **Domain Shift:** The statistical distribution of features (vocabulary, syntax, sender IDs, currency formats) in the deployment target domain differs significantly from the training source domain (e.g. the UCI SMS Spam Collection).
2. **Shortcut Learning:** Standard models trained on international datasets over-optimize for simple, keyword-heavy shortcuts (e.g., classifying *any* message containing financial terms like "debit," "bank," or shortened URL structures like "bit.ly" as spam).

When exposed to legitimate Pakistani transactional HAM (which contains these exact features in a benign context), base models suffer an **82.8% to 100% False Positive Rate (FPR)**. Flagging legitimate transaction receipts or OTPs as spam blocks the message, disrupting critical user services.

---

## 1.6 Research Motivation

The motivation for this research is to bridge the gap between high in-domain model accuracy and real-world domain generalization. Securing mobile endpoints against smishing requires classifiers that can distinguish malicious intents from benign financial alerts. 

Furthermore, simply displaying a binary threat warning is insufficient. Users need clear, understandable indicators to trust the system's decisions, requiring an explainability layer. This research aims to develop a localized data curation strategy, evaluate its impact on domain shift mitigation, and design an explainable, integrated mobile security prototype.

---

## 1.7 Research Gap

1. **Dataset Gap:** Existing SMS spam datasets lack representations of Roman Urdu dialects, code-switched phrasings, and local Pakistani financial transaction logs.
2. **Generalization Gap:** No systematic evaluation exists profiling the domain shift failure of transformer-based models on localized South Asian mobile communications.
3. **Explainability Gap:** Real-time mobile security explainers often rely on complex, computationally expensive models that cannot run on mobile devices, or static alerts that do not provide context.
4. **Mobile Integration Gap:** Current research typically evaluates ML models in isolated offline environments, without integrating them into the native background interception lifecycles of mobile operating systems.

---

## 1.8 Proposed Solution: MindShield

MindShield is an explainable, localized SMS threat detection system. It operates on a hybrid architecture:

* **Ingestion:** Native Android background components intercept incoming SMS broadcasts and write them to a local SQLite database (`mindshield.db`).
* **Platform Bridge:** A MethodChannel bridge triggers background Dart execution and UI updates on the Flutter mobile client.
* **Analysis:** The mobile client submits the SMS payload to a remote FastAPI server for real-time analysis.
* **ML Classification:** The server executes **binary DistilBERT threat classification** using fine-tuned transformer weights.
* **Explainability:** In parallel, the server executes a **Heuristic Scoring / Feature Attribution (HFA)** rule engine to return user-facing indicator flags (such as credentials requests or link presence).
* **UI Presentation:** The client app renders the classification verdict and uses local substring search to highlight flagged HFA indicators.

---

## 1.9 Research Questions

This thesis is structured around four core Research Questions (RQs):

* **RQ1:** To what extent can a distilled transformer architecture fine-tuned on localized SMS datasets classify bilingual smishing when deployed on a local server logic tier?
  * *Investigation:* Evaluated by fine-tuning `distilbert-base-uncased` on successive iterations of the PakScam-SMS corpus and measuring performance metrics.
* **RQ2:** How can Explainable AI (XAI) concepts be adapted into lightweight, user-facing security indicators without degrading mobile execution performance?
  * *Investigation:* Addressed by designing a parallel HFA rule engine that extracts risk indicators without adding inference latency.
* **RQ3:** How can native Android interception hooks be integrated with cross-platform Dart providers to handle background SMS events without blocking presentation threads?
  * *Investigation:* Evaluated by implementing a native Android BroadcastReceiver and MethodChannel bridge linked to Flutter state managers.
* **RQ4:** What architectural boundaries are required to enforce user data privacy during remote machine learning SMS inference?
  * *Investigation:* Addressed by implementing local contact resolution on the device and transient, in-memory message processing on the server.

---

## 1.10 Research Objectives

To answer the research questions, the project defines the following objectives:
1. Curate a localized Pakistani SMS dataset (`PakScam-SMS`) representing local smishing vectors and transactional hard negatives.
2. Fine-tune a binary DistilBERT classifier to generalize to Pakistani SMS structures.
3. Benchmark the transformer model against classical machine learning baselines (Linear SVM).
4. Design a Heuristic Feature Attribution (HFA) engine to provide user-facing risk explanations.
5. Implement a native Android background BroadcastReceiver and shared SQLite persistence layer.
6. Build a Flutter mobile application to quarantine spam and present analysis results.
7. Develop a regression testing suite and quality gates to prevent performance regressions during model updates.

---

## 1.11 Research Contributions

MindShield makes the following contributions:
* **PakScam-SMS Corpus:** A localized Pakistani dataset containing 205 smishing and transactional templates.
* **Shortcut Learning Analysis:** Documenting that base models suffer a 95.1% false positive rate on local banking hams, and mitigating it using Mix-C oversampling.
* **Decoupled XAI Architecture:** Establishing a parallel HFA engine that generates explainability indicators without adding model latency.
* **End-to-End System Integration:** Designing a prototype connecting native Android interception, SQLite caching, a FastAPI remote backend, and a Flutter UI.

---

## 1.12 Scope of the Project

The scope of this prototype is defined as follows:

### Implemented Scope:
* Background SMS interception via Kotlin `SmsReceiver.kt`.
* Shared SQLite local caching (`mindshield.db`) and v1 $\rightarrow$ v2 database migrations.
* Remote model inference execution on the FastAPI server.
* Binary DistilBERT classification and rule-based attack categorization.
* Parallel HFA rule extraction and local UI substring highlighting.

### Excluded Scope (Future Work):
* **No On-Device ML:** DistilBERT model weights are loaded and computed exclusively on the backend server.
* **No Official LIME:** Explainability is based on HFA rule checks, not dynamic local surrogate models.
* **No API Authentication / Rate-Limiting:** APIs run on open ports without access tokens or rate limiting.
* **No Database Encryption:** Local SQLite databases are stored in plaintext.
* **No Local Notifications:** Spam alerts are handled within the app UI; background push notifications are not implemented.

---

## 1.13 Project Constraints and Assumptions

* **Connectivity Assumption:** The system assumes the device has active network access to query the remote backend server. If offline, SMS are cached as `'pending'`.
* **Hardware Constraints:** The prototype runs on standard mobile CPU hardware; on-device model execution is restricted by mobile hardware limitations.
* **Linguistic Scope Constraint:** Text analysis is limited to English and Latin-script Roman Urdu. Arabic-script Urdu is not supported.

---

## 1.14 Significance of the Study

This study demonstrates the impact of domain shift and shortcut learning on deep learning models deployed in localized regions. By curating a Pakistani-specific dataset and implementing regression gates, the project demonstrates that models can be adapted to recognize local transaction alerts, reducing false positive rates from 95.10% to 2.44%. The architecture provides a design blueprint for integrating explainable, remote machine learning inference into native mobile operating system workflows.

---

## 1.15 Thesis Organization

The remainder of this thesis is structured as follows:
* **Chapter 2 — Literature Review:** Surveys SMS filtering methods, transformer architectures, and Explainable AI.
* **Chapter 3 — Methodology:** Details the mathematical formulation, data engineering pipelines, and training configurations.
* **Chapter 4 — System Architecture & Design:** Maps components, data boundaries, and platform integration channels.
* **Chapter 5 — Data Engineering & Preprocessing:** Documents the UCI SMS and PakScam-SMS datasets and cleaning normalizations.
* **Chapter 6 — ML Model Development & Baselines:** Evaluates DistilBERT fine-tuning and classical benchmarks.
* **Chapter 7 — Pakistani Domain Generalization & Localized Evaluation:** Details domain shift failures and regression gates.
* **Chapter 8 — Explainable AI & Heuristic Feature Attribution:** Details the HFA rule engine and Flutter rendering.
* **Chapter 9 — System Integration & Communication APIs:** Documents FastAPI routers, request schemas, and Dio clients.
* **Chapter 10 — Mobile Application Architecture & Implementation:** Details Kotlin receivers, MethodChannels, and feature widgets.
* **Chapter 11 — Security, Privacy & Threat Analysis:** Performs threat modeling and evaluates privacy data flows.
* **Chapter 12 — Testing & Quality Assurance:** Documents unit tests, integration tests, and quality gates.
* **Chapter 13 — Conclusion, Limitations & Future Scope:** Summarizes achievements and prioritizes future work.

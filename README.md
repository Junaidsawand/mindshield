🛡️ MindShield

AI-Powered, Privacy-Preserving SMS Threat Detection for Android

Detect suspicious messages. Protect your privacy. Stay secure — entirely on your device.

MindShield is an AI-powered Android application designed to identify potentially fraudulent, phishing, and scam SMS messages using an on-device Natural Language Processing (NLP) model.

Built with Flutter and DistilBERT, MindShield integrates Android's SMS broadcast system with ONNX Runtime to classify incoming messages locally, without transmitting SMS content to external servers.

The project explores how lightweight AI deployment, mobile application development, and cybersecurity can work together to provide accessible, privacy-focused mobile threat protection.

---

✨ Key Features

- AI-Powered SMS Detection: Uses a fine-tuned DistilBERT model to classify suspicious SMS messages.
- On-Device Inference: Runs machine learning inference locally using ONNX Runtime.
- Privacy-Focused Architecture: SMS content is processed locally rather than uploaded to a remote server.
- Automatic SMS Monitoring: Uses Android BroadcastReceiver to detect incoming messages.
- Local Database: SQLite stores messages and their classification results.
- Real-Time Notifications: Notifies users about detected suspicious messages.
- Flutter Interface: Provides a mobile interface for reviewing and managing analyzed messages.
- Offline Processing: Core classification functionality does not require a cloud inference API.

🧠 How It Works

MindShield combines native Android components, Flutter, local storage, and an optimized machine learning model.

       Incoming SMS
             |
             v
   Android BroadcastReceiver
             |
             v
      SQLite Database
       (Pending SMS)
             |
             v
    Flutter WordPiece
        Tokenizer
             |
             v
       ONNX Runtime
       (C++ FFI)
             |
             v
    DistilBERT Classifier
             |
             v
     Classification Result
             |
             v
      SQLite Database
        (Updated SMS)
             |
             v
       Flutter UI
             |
             v
      User Notification

Processing Pipeline

1. SMS Reception: Android BroadcastReceiver detects incoming SMS messages.
2. Local Storage: Messages are temporarily stored in the local SQLite database.
3. Tokenization: The Flutter application processes message text using a WordPiece tokenizer.
4. AI Classification: Tokenized input is passed to the DistilBERT ONNX model through native C++ FFI integration.
5. Result Storage: Classification results are saved in SQLite.
6. User Notification: The application displays relevant information through its interface and Android notifications.

🤖 Machine Learning Model

MindShield uses a fine-tuned DistilBERT model for SMS classification.

The trained model is exported to ONNX format to support local inference on Android devices.

Component| Implementation
Model| DistilBERT
Model Format| ONNX
Inference Engine| ONNX Runtime
Tokenization| WordPiece
Execution| On-device
Classification| SMS threat detection

Model Evaluation

Reported evaluation results on the UCI v3 dataset:

Metric| Result
Accuracy| 98.83%
Precision| 100%
Recall| 90.62%
F1-Score| 95.08%

Inference Performance

Measurement| Result
Raw CPU Inference| 57.62 ms
Warm End-to-End Processing| 272 ms
ONNX Model Size| ~256.1 MiB

Note: These are reported experimental results from the current implementation. Performance may vary depending on the device, runtime conditions, and evaluation setup. The metrics describe the evaluated dataset and should not be interpreted as a guarantee of real-world detection performance.

🏗️ Technology Stack

Technology| Purpose
Flutter| Mobile application development
Dart| Application logic
Kotlin / Android APIs| Native Android integration
DistilBERT| NLP-based SMS classification
ONNX| Machine learning model deployment
ONNX Runtime| On-device inference
C++ FFI| Native inference integration
SQLite| Local message storage
WordPiece| Text tokenization

📱 Development Environment

Component| Configuration
Platform| Android
Minimum SDK| API 24
Tested Device| Google Pixel 6a
Tested Android Version| Android 16
Compile SDK| API 36
ONNX Runtime Package| onnxruntime_v2 1.23.2+2

🔒 Privacy & Security

Privacy is a core design principle of MindShield.

- SMS classification is performed locally on the Android device.
- No cloud-based inference API is required.
- Message data is stored in a local SQLite database.
- The application is designed to avoid transmitting SMS content to external servers.

MindShield is an academic cybersecurity project and should not be considered a replacement for Android security protections, carrier-level spam filtering, or professional security solutions.

🚀 Project Goals

MindShield aims to explore the practical application of artificial intelligence in mobile cybersecurity.

The project focuses on:

- Improving SMS scam and phishing detection.
- Deploying transformer-based NLP models on resource-constrained mobile devices.
- Reducing dependence on cloud-based threat detection services.
- Exploring multilingual scam detection.
- Making mobile threat intelligence more accessible.

🔮 Future Development

Planned research and development directions include:

- [ ] English and Roman Urdu SMS classification.
- [ ] Improved detection of social engineering and psychological manipulation.
- [ ] Scam urgency and financial-pressure indicators.
- [ ] Expanded and more diverse SMS datasets.
- [ ] Template-separated evaluation to reduce data leakage.
- [ ] Improved model optimization and mobile inference performance.
- [ ] Local threat analysis and explainable detection results.

👨‍💻 Development Team

Developed as a Final Year Project (FYP) at:

Institute of Mathematics and Computer Science (IMCS)
University of Sindh, Jamshoro, Pakistan

Contributors

- Junaid Ahmed — Project Lead & Developer
- Mudasar — Development Team
- Kalpna — Development Team

📚 Research & Academic Context

MindShield explores the intersection of:

- Mobile Application Security
- Artificial Intelligence
- Natural Language Processing
- Cybersecurity
- On-Device Machine Learning
- Privacy-Preserving Computing

The project is intended for academic research, experimentation, and further development in mobile threat detection.

📄 License

License information will be added when the project license is finalized.

---

MindShield — Your messages. Your device. Your privacy. 🛡️

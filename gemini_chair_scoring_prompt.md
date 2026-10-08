# Prompt for Gemini: iCACCESS 2026 Session Chair Paper-Evaluation Form

You are an expert Google Apps Script developer. Write ONE complete, ready-to-run Google Apps Script (a single `createChairEvaluationForm()` function plus any helpers) that builds a Google Form for session chairs of **iCACCESS 2026** (2nd International Conference on Advances in Computing, Communication, Electrical, and Smart Systems, October 2–3, 2026, ULAB Campus, Dhaka, Bangladesh) to mark the papers presented in their session.

## Form structure

1. **Form title:** "iCACCESS 2026 – Session Chair Paper Evaluation"
   **Description:** "Please evaluate each paper presented in your session. Score every criterion from 0 (very poor) to 5 (excellent)."
   - Collect the respondent's email address.
   - Allow editing responses after submitting.
   - Do not limit to one response. Some chairs may fill the form in several sittings.

2. **Page 1, Chair selection:** a required **dropdown** "Select your name (Session Chair)" listing every chair below. Use **"Go to section based on answer"** so each chair jumps straight to their own section and never sees other sessions.

3. **One section per session chair:**
   - Section title: `<Session ID> – <Session Title>`
   - Section description: `Session Chair: <Chair name> | <Day, Time>`
   - Then, for **each paper** in that session, in the order given:
     - A **section header** item titled `Paper <Paper ID>`, with the paper title as its description.
     - **5 required questions**, one per criterion below. Each is a **multiple-choice (radio button)** question with options `0, 1, 2, 3, 4, 5`, and titled `Paper <ID> – <Criterion>` so each response column in the linked sheet is unambiguous.
     - One optional paragraph question: `Paper <ID> – Comments (optional)`.
   - At the end of the chair's section, set navigation to **Submit form**. Do not continue into the next chair's section.

## The 5 marking criteria (0–5 each, total /25)

1. Novelty & Originality of the Contribution
2. Technical Quality & Soundness of Methodology
3. Clarity & Organization of the Presentation
4. Quality of Results & Discussion
5. Response to Questions & Time Management

(The planning workbook records a "Chair Score (/50)", so the sheet should also show the total ×2 = score out of 50.)

## Response handling

- Create a linked Google Sheet named "iCACCESS 2026 – Chair Evaluation Responses" (`form.setDestination`).
- Add a second sheet, "Score Summary", with columns: `Session ID | Paper ID | Chair | Q1 | Q2 | Q3 | Q4 | Q5 | Total (/25) | Chair Score (/50)`. Include an `onFormSubmit` trigger function (and install it from the main function) that appends one row **per paper** to this summary sheet whenever a response arrives.
- Log the form's edit URL, the published (respondent) URL and the sheet URL with `Logger.log`.

## Code requirements

- Put all data in one JavaScript array/object at the top of the script (chairs → sessions → papers), so organizers can edit it without touching the logic.
- Build the sections in a loop from that data. Do not hard-code items one by one.
- Use only built-in `FormApp` / `SpreadsheetApp` / `ScriptApp` services. No external libraries.
- Handle the Apps Script quirk where page-break navigation must be set after all sections exist. Create the sections first, then wire the dropdown choices with `createChoice(name, pageBreakItem)`.
- Add brief comments and short "How to run" steps at the top (open script.google.com → paste → run → authorize).

## Data (from the iCACCESS 2026 planning workbook)

```
Session Chair: Dr. Md.Ruhul Amin
  Session T1P1 — Machine Learning Foundations and Intelligent Systems (Day 1, 11:40-12:40)
    - Paper 49: SPPC: Benchmarking Selenium, Playwright, Puppeteer, and Cypress for Energy-Efficient Web Automation
    - Paper 58: Explainable Machine Learning for Cross-Species Myeloid Biomarker Discovery in Glioblastoma
    - Paper 383: A Lightweight Framework for Foldable Protein Sequence Generation via Confidence-Guided Selection

Session Chair: Prof. Dr. Kamruddin Nur
  Session T1P2 — Natural Language, Computer Vision, and Multimodal AI (Day 1, 11:40-12:40)
    - Paper 61: Beyond Fragmentation: A Causal Analysis of Unicode NFKC Normalization Effects in Dialectal Bengali NER
    - Paper 66: Interpretable Psoriatic Lesion Classification via Multi-Cohort Gene Expression Profiling
    - Paper 242: TriFuseNet: A Three-Stream Cross-Attention Network for Few-Shot Multimodal Idiom Ranking
    - Paper 378: A Multimodal Framework for Early-Stage Crop Disease Diagnosis Using Visual and Environmental Data

Session Chair: Dr. Nahid Akhter Jahan
  Session T1P3 — Wireless Networks and Optical Communication Systems (Day 1, 11:40-12:40)
    - Paper 33: Performance Analysis of RIS-Assisted 6G Wireless Systems with Hybrid Architectures and Hardware Constraints
    - Paper 116: Novel Microstrip-fed Implantable Antenna Design Operating at 5.85 GHz for Medical Applications
    - Paper 136: An X-Band 2×2 MIMO Antenna Array with Enhanced Beamforming and Radiation Performance
    - Paper 217: AFDM-Aided PD-NOMA with Dynamic Power Allocation for High-Mobility THz Communications

Session Chair: Dr. Mohammed Ashikur Rahman
  Session T2P1 — Cloud, Big Data, and Distributed Computing (Day 1, 14:30-15:30)
    - Paper 94: TaxNet-Bangladesh: Building a Domain-Specific Tax Question-Answering System for Businesses in Bangladesh
    - Paper 95: MpoxFusionNet: Privacy-Aware Hybrid CNN-Transformer Fusion for Monkeypox Detection from Skin Lesion Images
    - Paper 162: Distributed Transformer Inference for Sentiment Analysis: An HTCondor and DAGMan-Based Workflow Approach on AWS
    - Paper 166: Explainable Machine Learning and Country-Level Trade Segmentation for Global Electric Vehicle Trade

Session Chair: Dr. Mohammad Nurul Huda
  Session T2P2 — Applied AI and Intelligent Computing Applications (Day 1, 14:30-15:30)
    - Paper 124: HybridOsteoX: A Knee Osteoporosis Explainable AI Framework Using Hybrid CNN-ViT Fusion
    - Paper 127: BanglaRhet: Benchmarking Classical and Transformer Models for Rhetorical and Persuasion Detection in Bangla Political Speech
    - Paper 135: FairHireATS: An Intersectional Bias Detection and Mitigation Framework for Automated Resume Screening
    - Paper 147: SplitSeg: Generalizable Skin Lesion Segmentation with ResNeSt-UNet

Session Chair: Dr. Mohammad Shazzad Hossain
  Session T2P3 — AI-Enabled Digital Learning and Educational Technologies (Day 1, 14:30-15:30)
    - Paper 254: BioCal RA: A Trustworthy and Explainable Multi-Agent Research Assistant for Biomedical Field
    - Paper 275: Multi-Representation Fusion with Subspace-Aware SMOTE for Source Code Vulnerability Detection
    - Paper 322: NOVA-Net: A Noise-Aware Deep Network for Robust Human Activity Recognition from Surveillance Videos
    - Paper 358: AdaLLM: A Subject-Adaptive RAG Framework Designed for the Question Answering Process of NCTB’s Class-8 Science & BGS Subjects

Session Chair: Dr. Mirza Rasheduzzaman
  Session T2P4 — IoT, Embedded, and Cyber-Physical Systems (Day 1, 14:30-15:30)
    - Paper 176: Blockchain-Based Bug Bounty System with A Novel Weighted Reputation-Driven Consensus Mechanism
    - Paper 177: An Interpretable Machine Learning Approach for Maternity Risk Prediction and Assessment
    - Paper 238: FormSense: A Continuous Fatigue and Form Tracking Application for Resistance Workout Monitoring Utilizing Phase-Graded IMU Analysis
    - Paper 367: A Low-Cost IoT-Based Smart Home Automation and Security System with Energy-Efficient Operation for Sustainable Living in Developing Regions

Session Chair: Dr. Mustafa Habib Chowdhury
  Session T3P1 — Smart Learning Technologies and Electronic Systems (Day 1, 15:30-16:30)
    - Paper 193: A Leakage-Aware Comparative Analysis of Machine Learning Models for IMU-Based Human Activity Recognition Systems
    - Paper 377: Graph-Enhanced Causal Reinforcement Learning for Proactive Customer Retention: A Comparative Benchmark
    - Paper 365: PSO-Based Selective Harmonic Elimination with Smart Cell-Bypassing for a 15-Level Asymmetric Cascaded H-Bridge Inverter
    - Paper 230: Comparing local GPT and Student Performance on Introductory Statistics MCQ Examinations

Session Chair: Dr. Mohammad Rifat Ahmmad Rashid
  Session T3P3 — Robotics, Automation, and Smart Control Systems (Day 1, 15:30-16:30)
    - Paper 357: Comparative Study of Classical and Learning-Based Tissue Tracking Algorithms on Infrared Surgical Tattoo Sequences for Minimally Invasive Surgery
    - Paper 160: Numerical Investigation of a Corrugated PDMS Diaphragm-based Fiber Optic Fabry-Perot Sensor for Acoustic Sensing
    - Paper 210: A 16.1-fJ/conv.-step 8-bit 100-MS/s SAR ADC for WLAN Receiver Baseband in 65-nm CMOS
    - Paper 276: An Interpretable Ensemble Learning Framework for Predicting Students' Entrepreneurial Intention in Digital Entrepreneurship Education

Session Chair: Dr. Sifat Momen
  Session T3P5 — Sustainable Finance and Green Energy Technologies (Day 1, 15:30-16:30)
    - Paper 208: The Effect of e-KYC Adoption on the Cost Efficiency of Commercial Banks in Bangladesh: A Dynamic Panel Study
    - Paper 279: Programmable Remittances for Bangladesh A Permissioned Blockchain System for Diaspora-Controlled Household Payments
    - Paper 280: Architectural Differences among MFS, PSP, and PSO in Bangladesh: A Liability–Ledger Reference Model
    - Paper 282: Floating Solar on an Oxbow Lake: Energy, Water, and Rice Co-Benefits at Bergobindopur Baor, Bangladesh

Session Chair: Prof. Dr. Ishtiak Al Mamoon
  Session T4P1 — Machine Learning Applications and Data-Driven Systems (Day 2, 11:00-13:00)
    - Paper 2: Evaluating image upsampling strategies for downstream microscopy image classification
    - Paper 5: A Hybrid Retrieval-Augmented Machine Learning Approach for AI-Generated Text Detection
    - Paper 59: An Explainable Lightweight CBAM-CNN with Focal Loss for Brain Tumor MRI Classification
    - Paper 138: HalluciNet: A Multi-Granularity Contrastive Framework for Factual Hallucination Detection in Large Language Models
    - Paper 243: ResNet and LSTM Based Hybrid Deep Learning Model for Reliable and Interpretable Epileptic Seizure Classification
    - Paper 250: An Interpretable Stacking Ensemble for Chronic Kidney Disease Screening and KDIGO Severity Staging
    - Paper 332: Meta-Learning for Few-Shot Personalization of Error-Related Potential Brain-Computer Interfaces
    - Paper 376: Kidney-Net:Feature-Centric and Minimal Biomarker-Based Prediction of Chronic Kidney Disease Using Machine Learning

Session Chair: Prof. Dr. Ahmed Al Mansur
  Session T4P2 — Intelligent Communication Networks and Computing (Day 2, 11:00-13:00)
    - Paper 310: Predicting the Effect of Drugs on Neonatal using Machine Learning and Explainable AI
    - Paper 327: Explainable Machine Learning and Causal Analysis for Obesity Prediction Using Knowledge Graphs
    - Paper 323: Computer Vision and Kalman Filtering for Driverless Vehicle Steering Angle Computation
    - Paper 341: An Integrated Dual-Module Cyber Physical System for Motorcycle Safety: Utilizing Pre-Ride Safety, Crash Detection and Swift Response with Mobile Application Companion
    - Paper 175: Isolation-Wall Integrated Graphene THz MIMO Antenna with Wideband and High-Diversity Performance for 6G Applications
    - Paper 228: Side-Fed Circular Slotted BD Flag-Shaped Antenna with DGS for Sub-6 GHz IoT and Smart Wireless Applications

Session Chair: Dr. Khairul Alam
  Session T4P3 — Electronics and Hardware for Intelligent Computing (Day 2, 11:00-13:00)
    - Paper 273: A Lightweight Hybrid Quantum-Classical CNN for Brain Tumor MRI Classification
    - Paper 347: NeuroXplain: An Explainable Transfer Learning Framework for Alzheimer’s Disease Classification
    - Paper 85: Multi-Metaheuristic Optimisation of Cascade Controllers for DC-DC Converters: A Comparative Study of PI, PID, and Sliding Mode Control
    - Paper 148: Cross-Design Limitations of ML-Based PPA Prediction in OpenLane
    - Paper 274: Modulation Strategy for Optimizing Semiconductor Losses for A High Power Step-Down Dual Active Bridge Converter in AI Data Center Applications
    - Paper 345: An Au/ITO Dual-Layer Photonic Crystal Fiber Surface Plasmon Resonance Biosensor for Label-Free Detection and Discrimination of Basal, HeLa, and Jurkat Cancer Cells
    - Paper 295: A Dual-Focus UX Prioritization Framework for Educational Games Using Sentiment Analysis

Session Chair: Prof. Dr. Engr. Muhibul Haque Bhuyan
  Session T4P4 — Cybersecurity, Blockchain, and Trustworthy Computing (Day 2, 11:00-13:00)
    - Paper 64: An Explainable Ensemble Learning Approach for Anemia Prediction Using Clinical and Biochemical Data
    - Paper 86: DCAF-Net: Dual-Branch Convolutional Network with Spatial Cross-Attention Fusion for Thyroid Nodule Classification
    - Paper 215: An Integrated Edge-AI Framework for Interpretable Respiratory Screening via Adaptive Cough Analysis in Low-Resource Settings
    - Paper 263: Illusion of Sequence: Rigorously Validated Null Result for Recurrent and Attention-Based Memory-Forensic Ransomware Family Classification
    - Paper 346: High-Throughput Meritocratic Consensus: A Native Go Implementation of Reputation-Based Ordering for Hyperledger Fabric
    - Paper 355: Temporal Capability Cryptography: Cryptographic State Evolution for Forward Authorization in Distributed Systems

Session Chair: Dr. Rezwan Al Islam Khan
  Session T4P5 — Human-Centered Computing and Interaction Design (Day 2, 11:00-13:00)
    - Paper 48: CEC: A Non-Stationary Benchmarking Protocol for the Fair Evaluation of Metaheuristic Optimizers
    - Paper 181: Transformer Based Approaches for Intent Detection and Slot Filling in Bangla and Sylhety Virtual Assistants
    - Paper 251: Continuous Bengali Sign Language Recognition from Sentence-Level Videos Using Deep Learning Architectures
    - Paper 262: MentalScreen: A Hybrid PHQ-9/GAD-7 and MentalRoBERTa Agentic Framework for Multi-Label Mental Health Detection with Deterministic Crisis Routing
    - Paper 265: VNetLS: Supervised 3D VNet-Based MRI Enhancement with Loss Optimization
    - Paper 266: Cartographer: Transforming Code Repositories into LLM-Optimized Semantic Graphs
    - Paper 312: A Leak-Free, Explainable Machine Learning Framework for Predicting Internet Gaming Disorder Tolerance: Re-Evaluating SMOTE, Chi-Square Feature Selection, and LIME under Rigorous Validation
    - Paper 362: Graph Attention Versus Tabular Models for Early Liver Fibrosis Staging: A Leakage-Controlled Multi-Cohort Benchmark

Session Chair: Dr. Md. Ashraful Haque, PhD
  Session T4P6 — Emerging Topics in Computing and Intelligent Systems (Day 2, 11:00-13:00)
    - Paper 167: Linux Malware Detection using API Call Graphs with Graph2Vec and GraphSAGE Model
    - Paper 232: Attention-Enhanced U-Net with Boundary-Aware Hybrid Loss for Low-Grade Glioma Segmentation in Multi-Sequence MRI
    - Paper 305: Explainable Digital Addiction Severity Prediction Using Machine Learning, NLP, and Large Language Models
    - Paper 354: Integrated Machine Learning and Deep Learning Pipeline for Discovering Diagnostic and Prognostic Biomarkers of Colon Cancer
    - Paper 373: A Zero-Initialized Residual MLP Head for Lung Cancer CT Scan Image Classification: A Comparative Study using five CNN Backbones
    - Paper 375: Adapting BitNet b1.58 techniques in Convolutional Neural Networks for Efficient Deep Learning
```

Return only the complete Apps Script code with its top-of-file instructions.

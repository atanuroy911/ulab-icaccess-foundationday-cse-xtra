/**
 * iCACCESS 2026 – Session Chair Paper Evaluation (Google Form builder)
 *
 * FORM FLOW
 *  Page 1    Session Chair (list + "Other" with a name box) and Session ID (decides where to go)
 *  Paper k   Dropdown with THAT session's papers + "Other" (type the Paper ID),
 *            5 scores (0-5), then "Evaluate another paper?"  Yes -> next / No -> Submit
 *  Sessions with no papers yet, or Session "Other", get pages where the Paper ID is typed in.
 *
 * HOW TO RUN
 *  1. Go to https://script.google.com  ->  New project.
 *  2. Delete the sample code, paste this whole file, and click Save.
 *  3. Pick the function  createChairEvaluationForm  in the toolbar and click Run.
 *  4. Authorize when asked (Forms, Sheets, triggers).
 *  5. Watch the Execution log:
 *       - "PAUSED ... Click Run again"  -> just click Run again. Apps Script stops any run at
 *         6 minutes, so the build saves its progress and continues where it left off.
 *       - "DONE"  -> the log shows the link to SHARE with chairs, the form edit link, and the Sheet link.
 *
 *  To start over with a brand-new form, run  resetBuild  first.
 *  To rebuild the "Score Summary" tab manually at any time, run  rebuildSummary.
 */

// ----------------------------------------------------------------------------- settings
const FORM_TITLE = 'iCACCESS 2026 – Session Chair Paper Evaluation';
const FORM_DESCRIPTION =
  '2nd International Conference on Advances in Computing, Communication, Electrical, and Smart Systems\n' +
  'October 2–3, 2026 | ULAB Campus, Dhaka, Bangladesh\n\n' +
  'Select your name and the session you chaired, then evaluate each paper presented, one at a time.\n' +
  'Score every criterion from 0 (very poor) to 5 (excellent).\n' +
  'If a paper is not in the list (e.g. moved from another session), choose "Other" and type its Paper ID.';

const Q_CHAIR = 'Session Chair';
const Q_CHAIR_OTHER = 'Session Chair name (only if you selected "Other")';
const Q_SESSION = 'Session ID';
const Q_MORE = 'Evaluate another paper?';
const OTHER = 'Other';
const OTHER_PAPER = 'Other – paper not listed (type the Paper ID below)';
const EXTRA_SLOTS = 2;       // pages beyond a session's scheduled paper count, for moved-in papers
const UNLISTED_SLOTS = 8;    // pages for sessions with no papers yet / Session "Other"
const UNLISTED = 'UNLISTED'; // internal key for that shared set of pages
const TIME_BUDGET_MS = 4.5 * 60 * 1000;   // pause safely before Apps Script's 6-minute limit

const CRITERIA = [
  'Novelty & Originality',
  'Technical Quality & Methodology',
  'Clarity of Presentation',
  'Results & Discussion',
  'Q&A & Time Management',
];

// ----------------------------------------------------------------------------- data
const SESSIONS = [
  {
    chair: "Dr. Md. Ruhul Amin",
    session: "T1P1",
    sessionTitle: "Machine Learning Foundations and Intelligent Systems",
    time: "Day 1, 11:40-12:40",
    papers: [
      { id: 49, title: "SPPC: Benchmarking Selenium, Playwright, Puppeteer, and Cypress for Energy-Efficient Web Automation" },
      { id: 58, title: "Explainable Machine Learning for Cross-Species Myeloid Biomarker Discovery in Glioblastoma" },
      { id: 383, title: "A Lightweight Framework for Foldable Protein Sequence Generation via Confidence-Guided Selection" },
    ],
  },
  {
    chair: "Prof. Dr. Kamruddin Nur",
    session: "T1P2",
    sessionTitle: "Natural Language, Computer Vision, and Multimodal AI",
    time: "Day 1, 11:40-12:40",
    papers: [
      { id: 61, title: "Beyond Fragmentation: A Causal Analysis of Unicode NFKC Normalization Effects in Dialectal Bengali NER" },
      { id: 66, title: "Interpretable Psoriatic Lesion Classification via Multi-Cohort Gene Expression Profiling" },
      { id: 242, title: "TriFuseNet: A Three-Stream Cross-Attention Network for Few-Shot Multimodal Idiom Ranking" },
      { id: 378, title: "A Multimodal Framework for Early-Stage Crop Disease Diagnosis Using Visual and Environmental Data" },
    ],
  },
  {
    chair: "Dr. Nahid Akhter Jahan",
    session: "T1P3",
    sessionTitle: "Wireless Networks and Optical Communication Systems",
    time: "Day 1, 11:40-12:40",
    papers: [
      { id: 33, title: "Performance Analysis of RIS-Assisted 6G Wireless Systems with Hybrid Architectures and Hardware Constraints" },
      { id: 116, title: "Novel Microstrip-fed Implantable Antenna Design Operating at 5.85 GHz for Medical Applications" },
      { id: 136, title: "An X-Band 2×2 MIMO Antenna Array with Enhanced Beamforming and Radiation Performance" },
      { id: 217, title: "AFDM-Aided PD-NOMA with Dynamic Power Allocation for High-Mobility THz Communications" },
    ],
  },
  {
    chair: "Dr. Mohammed Ashikur Rahman",
    session: "T2P1",
    sessionTitle: "Cloud, Big Data, and Distributed Computing",
    time: "Day 1, 14:30-15:30",
    papers: [
      { id: 94, title: "TaxNet-Bangladesh: Building a Domain-Specific Tax Question-Answering System for Businesses in Bangladesh" },
      { id: 95, title: "MpoxFusionNet: Privacy-Aware Hybrid CNN-Transformer Fusion for Monkeypox Detection from Skin Lesion Images" },
      { id: 162, title: "Distributed Transformer Inference for Sentiment Analysis: An HTCondor and DAGMan-Based Workflow Approach on AWS" },
      { id: 166, title: "Explainable Machine Learning and Country-Level Trade Segmentation for Global Electric Vehicle Trade" },
    ],
  },
  {
    chair: "Dr. Mohammad Nurul Huda",
    session: "T2P2",
    sessionTitle: "Applied AI and Intelligent Computing Applications",
    time: "Day 1, 14:30-15:30",
    papers: [
      { id: 124, title: "HybridOsteoX: A Knee Osteoporosis Explainable AI Framework Using Hybrid CNN-ViT Fusion" },
      { id: 127, title: "BanglaRhet: Benchmarking Classical and Transformer Models for Rhetorical and Persuasion Detection in Bangla Political Speech" },
      { id: 135, title: "FairHireATS: An Intersectional Bias Detection and Mitigation Framework for Automated Resume Screening" },
      { id: 147, title: "SplitSeg: Generalizable Skin Lesion Segmentation with ResNeSt-UNet" },
    ],
  },
  {
    chair: "Dr. Mohammad Shazzad Hossain",
    session: "T2P3",
    sessionTitle: "AI-Enabled Digital Learning and Educational Technologies",
    time: "Day 1, 14:30-15:30",
    papers: [
      { id: 254, title: "BioCal RA: A Trustworthy and Explainable Multi-Agent Research Assistant for Biomedical Field" },
      { id: 275, title: "Multi-Representation Fusion with Subspace-Aware SMOTE for Source Code Vulnerability Detection" },
      { id: 322, title: "NOVA-Net: A Noise-Aware Deep Network for Robust Human Activity Recognition from Surveillance Videos" },
      { id: 358, title: "AdaLLM: A Subject-Adaptive RAG Framework Designed for the Question Answering Process of NCTB’s Class-8 Science & BGS Subjects" },
    ],
  },
  {
    chair: "Dr. Mirza Rasheduzzaman",
    session: "T2P4",
    sessionTitle: "IoT, Embedded, and Cyber-Physical Systems",
    time: "Day 1, 14:30-15:30",
    papers: [
      { id: 176, title: "Blockchain-Based Bug Bounty System with A Novel Weighted Reputation-Driven Consensus Mechanism" },
      { id: 177, title: "An Interpretable Machine Learning Approach for Maternity Risk Prediction and Assessment" },
      { id: 238, title: "FormSense: A Continuous Fatigue and Form Tracking Application for Resistance Workout Monitoring Utilizing Phase-Graded IMU Analysis" },
      { id: 367, title: "A Low-Cost IoT-Based Smart Home Automation and Security System with Energy-Efficient Operation for Sustainable Living in Developing Regions" },
    ],
  },
  {
    chair: "Dr. Mustafa Habib Chowdhury",
    session: "T3P1",
    sessionTitle: "Smart Learning Technologies and Electronic Systems",
    time: "Day 1, 15:30-16:30",
    papers: [
      { id: 193, title: "A Leakage-Aware Comparative Analysis of Machine Learning Models for IMU-Based Human Activity Recognition Systems" },
      { id: 377, title: "Graph-Enhanced Causal Reinforcement Learning for Proactive Customer Retention: A Comparative Benchmark" },
      { id: 365, title: "PSO-Based Selective Harmonic Elimination with Smart Cell-Bypassing for a 15-Level Asymmetric Cascaded H-Bridge Inverter" },
      { id: 230, title: "Comparing local GPT and Student Performance on Introductory Statistics MCQ Examinations" },
    ],
  },
  {
    chair: "Dr. Mohammad Rifat Ahmmad Rashid",
    session: "T3P3",
    sessionTitle: "Robotics, Automation, and Smart Control Systems",
    time: "Day 1, 15:30-16:30",
    papers: [
      { id: 357, title: "Comparative Study of Classical and Learning-Based Tissue Tracking Algorithms on Infrared Surgical Tattoo Sequences for Minimally Invasive Surgery" },
      { id: 160, title: "Numerical Investigation of a Corrugated PDMS Diaphragm-based Fiber Optic Fabry-Perot Sensor for Acoustic Sensing" },
      { id: 210, title: "A 16.1-fJ/conv.-step 8-bit 100-MS/s SAR ADC for WLAN Receiver Baseband in 65-nm CMOS" },
      { id: 276, title: "An Interpretable Ensemble Learning Framework for Predicting Students' Entrepreneurial Intention in Digital Entrepreneurship Education" },
    ],
  },
  {
    chair: "Dr. Sifat Momen",
    session: "T3P5",
    sessionTitle: "Sustainable Finance and Green Energy Technologies",
    time: "Day 1, 15:30-16:30",
    papers: [
      { id: 208, title: "The Effect of e-KYC Adoption on the Cost Efficiency of Commercial Banks in Bangladesh: A Dynamic Panel Study" },
      { id: 279, title: "Programmable Remittances for Bangladesh A Permissioned Blockchain System for Diaspora-Controlled Household Payments" },
      { id: 280, title: "Architectural Differences among MFS, PSP, and PSO in Bangladesh: A Liability–Ledger Reference Model" },
      { id: 282, title: "Floating Solar on an Oxbow Lake: Energy, Water, and Rice Co-Benefits at Bergobindopur Baor, Bangladesh" },
    ],
  },
  {
    chair: "Prof. Dr. Ishtiak Al Mamoon",
    session: "T4P1",
    sessionTitle: "Machine Learning Applications and Data-Driven Systems",
    time: "Day 2, 11:00-13:00",
    papers: [
      { id: 2, title: "Evaluating image upsampling strategies for downstream microscopy image classification" },
      { id: 5, title: "A Hybrid Retrieval-Augmented Machine Learning Approach for AI-Generated Text Detection" },
      { id: 59, title: "An Explainable Lightweight CBAM-CNN with Focal Loss for Brain Tumor MRI Classification" },
      { id: 138, title: "HalluciNet: A Multi-Granularity Contrastive Framework for Factual Hallucination Detection in Large Language Models" },
      { id: 243, title: "ResNet and LSTM Based Hybrid Deep Learning Model for Reliable and Interpretable Epileptic Seizure Classification" },
      { id: 250, title: "An Interpretable Stacking Ensemble for Chronic Kidney Disease Screening and KDIGO Severity Staging" },
      { id: 332, title: "Meta-Learning for Few-Shot Personalization of Error-Related Potential Brain-Computer Interfaces" },
      { id: 376, title: "Kidney-Net:Feature-Centric and Minimal Biomarker-Based Prediction of Chronic Kidney Disease Using Machine Learning" },
    ],
  },
  {
    chair: "Prof. Dr. Ahmed Al Mansur",
    session: "T4P2",
    sessionTitle: "Intelligent Communication Networks and Computing",
    time: "Day 2, 11:00-13:00",
    papers: [
      { id: 310, title: "Predicting the Effect of Drugs on Neonatal using Machine Learning and Explainable AI" },
      { id: 327, title: "Explainable Machine Learning and Causal Analysis for Obesity Prediction Using Knowledge Graphs" },
      { id: 323, title: "Computer Vision and Kalman Filtering for Driverless Vehicle Steering Angle Computation" },
      { id: 341, title: "An Integrated Dual-Module Cyber Physical System for Motorcycle Safety: Utilizing Pre-Ride Safety, Crash Detection and Swift Response with Mobile Application Companion" },
      { id: 175, title: "Isolation-Wall Integrated Graphene THz MIMO Antenna with Wideband and High-Diversity Performance for 6G Applications" },
      { id: 228, title: "Side-Fed Circular Slotted BD Flag-Shaped Antenna with DGS for Sub-6 GHz IoT and Smart Wireless Applications" },
    ],
  },
  {
    chair: "Dr. Khairul Alam",
    session: "T4P3",
    sessionTitle: "Electronics and Hardware for Intelligent Computing",
    time: "Day 2, 11:00-13:00",
    papers: [
      { id: 273, title: "A Lightweight Hybrid Quantum-Classical CNN for Brain Tumor MRI Classification" },
      { id: 347, title: "NeuroXplain: An Explainable Transfer Learning Framework for Alzheimer’s Disease Classification" },
      { id: 85, title: "Multi-Metaheuristic Optimisation of Cascade Controllers for DC-DC Converters: A Comparative Study of PI, PID, and Sliding Mode Control" },
      { id: 148, title: "Cross-Design Limitations of ML-Based PPA Prediction in OpenLane" },
      { id: 274, title: "Modulation Strategy for Optimizing Semiconductor Losses for A High Power Step-Down Dual Active Bridge Converter in AI Data Center Applications" },
      { id: 345, title: "An Au/ITO Dual-Layer Photonic Crystal Fiber Surface Plasmon Resonance Biosensor for Label-Free Detection and Discrimination of Basal, HeLa, and Jurkat Cancer Cells" },
      { id: 295, title: "A Dual-Focus UX Prioritization Framework for Educational Games Using Sentiment Analysis" },
    ],
  },
  {
    chair: "Prof. Dr. Engr. Muhibul Haque Bhuyan",
    session: "T4P4",
    sessionTitle: "Cybersecurity, Blockchain, and Trustworthy Computing",
    time: "Day 2, 11:00-13:00",
    papers: [
      { id: 64, title: "An Explainable Ensemble Learning Approach for Anemia Prediction Using Clinical and Biochemical Data" },
      { id: 86, title: "DCAF-Net: Dual-Branch Convolutional Network with Spatial Cross-Attention Fusion for Thyroid Nodule Classification" },
      { id: 215, title: "An Integrated Edge-AI Framework for Interpretable Respiratory Screening via Adaptive Cough Analysis in Low-Resource Settings" },
      { id: 263, title: "Illusion of Sequence: Rigorously Validated Null Result for Recurrent and Attention-Based Memory-Forensic Ransomware Family Classification" },
      { id: 346, title: "High-Throughput Meritocratic Consensus: A Native Go Implementation of Reputation-Based Ordering for Hyperledger Fabric" },
      { id: 355, title: "Temporal Capability Cryptography: Cryptographic State Evolution for Forward Authorization in Distributed Systems" },
    ],
  },
  {
    chair: "Dr. Rezwan Al Islam Khan",
    session: "T4P5",
    sessionTitle: "Human-Centered Computing and Interaction Design",
    time: "Day 2, 11:00-13:00",
    papers: [
      { id: 48, title: "CEC: A Non-Stationary Benchmarking Protocol for the Fair Evaluation of Metaheuristic Optimizers" },
      { id: 181, title: "Transformer Based Approaches for Intent Detection and Slot Filling in Bangla and Sylhety Virtual Assistants" },
      { id: 251, title: "Continuous Bengali Sign Language Recognition from Sentence-Level Videos Using Deep Learning Architectures" },
      { id: 262, title: "MentalScreen: A Hybrid PHQ-9/GAD-7 and MentalRoBERTa Agentic Framework for Multi-Label Mental Health Detection with Deterministic Crisis Routing" },
      { id: 265, title: "VNetLS: Supervised 3D VNet-Based MRI Enhancement with Loss Optimization" },
      { id: 266, title: "Cartographer: Transforming Code Repositories into LLM-Optimized Semantic Graphs" },
      { id: 312, title: "A Leak-Free, Explainable Machine Learning Framework for Predicting Internet Gaming Disorder Tolerance: Re-Evaluating SMOTE, Chi-Square Feature Selection, and LIME under Rigorous Validation" },
      { id: 362, title: "Graph Attention Versus Tabular Models for Early Liver Fibrosis Staging: A Leakage-Controlled Multi-Cohort Benchmark" },
    ],
  },
  {
    chair: "Dr. Md. Ashraful Haque, PhD",
    session: "T4P6",
    sessionTitle: "Emerging Topics in Computing and Intelligent Systems",
    time: "Day 2, 11:00-13:00",
    papers: [
      { id: 167, title: "Linux Malware Detection using API Call Graphs with Graph2Vec and GraphSAGE Model" },
      { id: 232, title: "Attention-Enhanced U-Net with Boundary-Aware Hybrid Loss for Low-Grade Glioma Segmentation in Multi-Sequence MRI" },
      { id: 305, title: "Explainable Digital Addiction Severity Prediction Using Machine Learning, NLP, and Large Language Models" },
      { id: 354, title: "Integrated Machine Learning and Deep Learning Pipeline for Discovering Diagnostic and Prognostic Biomarkers of Colon Cancer" },
      { id: 373, title: "A Zero-Initialized Residual MLP Head for Lung Cancer CT Scan Image Classification: A Comparative Study using five CNN Backbones" },
      { id: 375, title: "Adapting BitNet b1.58 techniques in Convolutional Neural Networks for Efficient Deep Learning" },
    ],
  },
];

// Every session code (including ones with no papers yet), for the "Other" section
const ALL_SESSION_IDS = ["T1P1", "T1P2", "T1P3", "T2P1", "T2P2", "T2P3", "T2P4", "T2P5", "T3P1", "T3P2", "T3P3", "T3P4", "T3P5", "T4P1", "T4P2", "T4P3", "T4P4", "T4P5", "T4P6"];

// ----------------------------------------------------------------------------- build form
// Titles double as lookup keys when wiring navigation and reading responses.
// `key` is a session code (e.g. "T1P2") or UNLISTED.
const pageTitle = (key, k) => key === UNLISTED ? `Paper ${k}` : `${key} – Paper ${k}`;
const qPaper = (key, k) => `${key} · Paper ${k}`;
const qPaperId = (key, k) => key === UNLISTED
  ? `Paper ${k} – Paper ID`
  : `${key} · Paper ${k} – Paper ID (only if "Other")`;
const qScore = (key, k, c) => key === UNLISTED ? `Paper ${k} – ${c}` : `${key} · Paper ${k} – ${c}`;
const slotCount = s => (s ? s.papers.length + EXTRA_SLOTS : UNLISTED_SLOTS);

const paperLabel_ = p => `${p.id} – ${p.title.length > 100 ? p.title.slice(0, 97).trim() + '…' : p.title}`;
const sessionLabel_ = id => {
  const s = SESSIONS.filter(x => x.session === id)[0];
  return s ? `${id} – ${s.sessionTitle}` : id;
};

/**
 * Resumable build. Steps: 0..N-1 = one session's pages each, N = "unlisted" pages, then finalize.
 * Each step builds AND wires its own pages, and progress is saved after every step,
 * so a re-run never duplicates or loses anything.
 */
function createChairEvaluationForm() {
  const props = PropertiesService.getScriptProperties();
  const started = Date.now();
  let form;

  if (!props.getProperty('BUILD_FORM_ID')) {
    form = FormApp.create(FORM_TITLE)
      .setDescription(FORM_DESCRIPTION)
      .setAllowResponseEdits(true)
      .setConfirmationMessage('Thank you! Your evaluation has been recorded.');
    const chairs = SESSIONS.map(s => s.chair).filter((c, i, a) => a.indexOf(c) === i);
    form.addListItem().setTitle(Q_CHAIR).setRequired(true).setChoiceValues(chairs.concat([OTHER]));
    form.addTextItem().setTitle(Q_CHAIR_OTHER);
    form.addListItem().setTitle(Q_SESSION).setRequired(true)
      .setHelpText('Select the session you actually chaired.');   // choices + jumps wired in finalize
    props.setProperties({ BUILD_FORM_ID: form.getId(), BUILD_STEP: '0' });
  } else {
    form = FormApp.openById(props.getProperty('BUILD_FORM_ID'));
  }

  let step = Number(props.getProperty('BUILD_STEP'));
  while (step <= SESSIONS.length) {
    if (Date.now() - started > TIME_BUDGET_MS) {
      Logger.log(`PAUSED after ${step} of ${SESSIONS.length + 1} steps to avoid the 6-minute limit. ` +
                 'Click Run again to continue.');
      return;
    }
    addPaperPages_(form, step < SESSIONS.length ? SESSIONS[step] : null);
    step++;
    props.setProperty('BUILD_STEP', String(step));
    Logger.log(`Built step ${step} of ${SESSIONS.length + 1}`);
  }

  finalize_(form);
  props.deleteProperty('BUILD_FORM_ID');
  props.deleteProperty('BUILD_STEP');
}

/** Forget an unfinished build so the next run starts a brand-new form. */
function resetBuild() {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('BUILD_FORM_ID');
  props.deleteProperty('BUILD_STEP');
  Logger.log('Build reset. Run createChairEvaluationForm to start a new form.');
}

/** One session's chain of paper pages (s = null for the shared "unlisted" chain). */
function addPaperPages_(form, s) {
  const key = s ? s.session : UNLISTED;
  const n = slotCount(s);
  const pages = [], moreQs = [];
  for (let k = 1; k <= n; k++) {
    pages.push(form.addPageBreakItem()
      .setTitle(pageTitle(key, k))
      .setHelpText(s ? `${s.sessionTitle}\nPick the paper presented, or "Other" if it is not in the list.`
                     : 'Enter the ID of the paper presented.'));
    if (s) {
      form.addListItem().setTitle(qPaper(key, k)).setRequired(true)
        .setChoiceValues(s.papers.map(paperLabel_).concat([OTHER_PAPER]));
    }
    form.addTextItem().setTitle(qPaperId(key, k))
      .setValidation(FormApp.createTextValidation().requireNumber()
        .setHelpText('Enter the numeric paper ID').build())
      .setRequired(!s);
    CRITERIA.forEach(c => form.addScaleItem()     // row of radio buttons 0..5
      .setTitle(qScore(key, k, c))
      .setBounds(0, 5)
      .setLabels('Very poor', 'Excellent')
      .setRequired(true));
    if (k < n) moreQs.push(form.addMultipleChoiceItem().setTitle(Q_MORE).setRequired(true));
  }
  moreQs.forEach((q, i) => q.setChoices([
    q.createChoice('Yes', pages[i + 1]),
    q.createChoice('No, submit', FormApp.PageNavigationType.SUBMIT),
  ]));
}

/** Session jumps, "submit at end of each chain", sheet link and trigger. */
function finalize_(form) {
  const page = {};
  form.getItems(FormApp.ItemType.PAGE_BREAK).forEach(i => { page[i.getTitle()] = i.asPageBreakItem(); });

  // The last page of every chain must submit instead of flowing into the next chain.
  // setGoToPage on a page break controls what happens after the page BEFORE it,
  // so mark the first page of every chain except the very first one.
  SESSIONS.slice(1).forEach(s => page[pageTitle(s.session, 1)].setGoToPage(FormApp.PageNavigationType.SUBMIT));
  page[pageTitle(UNLISTED, 1)].setGoToPage(FormApp.PageNavigationType.SUBMIT);

  // Session ID -> that session's first paper page; empty sessions / Other -> unlisted pages
  const sessionList = form.getItems(FormApp.ItemType.LIST).map(i => i.asListItem())
    .filter(q => q.getTitle() === Q_SESSION)[0];
  sessionList.setChoices(ALL_SESSION_IDS.concat([OTHER]).map(id => {
    const has = SESSIONS.some(x => x.session === id);
    return sessionList.createChoice(sessionLabel_(id), page[pageTitle(has ? id : UNLISTED, 1)]);
  }));

  // Responses -> Google Sheet, plus a "Score Summary" tab
  const ss = SpreadsheetApp.create('iCACCESS 2026 – Chair Evaluation Responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  setupSummarySheet_(ss);
  PropertiesService.getScriptProperties().setProperties({ FORM_ID: form.getId(), SHEET_ID: ss.getId() });

  // Refresh the summary on every submission (remove triggers from earlier runs first)
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'onChairSubmit')
    .forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('onChairSubmit').forForm(form).onFormSubmit().create();

  Logger.log('DONE');
  Logger.log('SHARE this link with session chairs: ' + form.getPublishedUrl());
  Logger.log('Edit the form: ' + form.getEditUrl());
  Logger.log('Responses sheet: ' + ss.getUrl());
}

// ----------------------------------------------------------------------------- summary sheet
const SUMMARY_HEADERS = ['Session ID', 'Session Chair', 'Paper ID', 'Paper Title']
  .concat(CRITERIA.map((c, i) => `Q${i + 1}: ${c}`))
  .concat(['Total (/25)', 'Scheduled Session', 'Note', 'Last updated']);

function setupSummarySheet_(ss) {
  const sh = ss.getSheetByName('Score Summary') || ss.insertSheet('Score Summary');
  sh.clear();
  sh.getRange(1, 1, 1, SUMMARY_HEADERS.length)
    .setValues([SUMMARY_HEADERS])
    .setFontWeight('bold')
    .setBackground('#0B1F3A')
    .setFontColor('#FFFFFF')
    .setWrap(true);
  sh.setFrozenRows(1);
  sh.setColumnWidth(4, 380);
  return sh;
}

function onChairSubmit(e) {
  rebuildSummary();
}

/**
 * Rebuilds "Score Summary" from all responses: one row per paper.
 * If the same paper is scored more than once (edit / re-submit / moved), the latest scores win.
 */
function rebuildSummary() {
  const props = PropertiesService.getScriptProperties();
  const form = FormApp.openById(props.getProperty('FORM_ID'));
  const ss = SpreadsheetApp.openById(props.getProperty('SHEET_ID'));

  const scheduled = {};  // paperId -> { session, title, order }
  let order = 0;
  SESSIONS.forEach(s => s.papers.forEach(p => {
    scheduled[p.id] = { session: s.session, title: p.title, order: order++ };
  }));

  const latest = {};     // paperId -> entry
  form.getResponses().forEach(r => {
    const a = {};
    r.getItemResponses().forEach(ir => { a[ir.getItem().getTitle()] = ir.getResponse(); });
    const time = r.getTimestamp();
    const chair = a[Q_CHAIR] === OTHER ? (a[Q_CHAIR_OTHER] || 'Other') : (a[Q_CHAIR] || '');
    const session = String(a[Q_SESSION] || '').split(' – ')[0];

    SESSIONS.map(s => s.session).concat([UNLISTED]).forEach(key => {
      const s = SESSIONS.filter(x => x.session === key)[0];
      for (let k = 1; k <= slotCount(s); k++) {
        const pick = s ? a[qPaper(key, k)] : undefined;
        const typed = String(a[qPaperId(key, k)] || '').trim();
        if (!pick && !typed) continue;       // slot not answered
        let id, note = '';
        if (s && pick !== OTHER_PAPER) {
          id = String(pick).split(' – ')[0];
        } else {
          id = typed || `? (${key} page ${k}, ${chair})`;
          note = typed ? 'Entered via "Other"' : '"Other" selected but no Paper ID typed';
        }
        const scores = CRITERIA.map(c => {
          const v = a[qScore(key, k, c)];
          return v === undefined || v === '' ? '' : Number(v);
        });
        const sch = scheduled[id];
        if (sch && sch.session !== session) note = (note ? note + '; ' : '') + `Scheduled in ${sch.session}`;
        if (!latest[id] || latest[id].time <= time) latest[id] = { session, chair, scores, note, time };
      }
    });
  });

  const orderOf = id => (scheduled[id] ? scheduled[id].order : 1e6 + (Number(id) || 0));
  const rows = Object.keys(latest)
    .sort((x, y) => orderOf(x) - orderOf(y))
    .map(id => {
      const e = latest[id], sch = scheduled[id] || {};
      const total = e.scores.reduce((sum, v) => sum + (typeof v === 'number' ? v : 0), 0);
      return [e.session, e.chair, isNaN(Number(id)) ? id : Number(id), sch.title || '']
        .concat(e.scores, [total, sch.session || '(not scheduled)', e.note, e.time]);
    });

  const sh = setupSummarySheet_(ss);
  if (rows.length) sh.getRange(2, 1, rows.length, SUMMARY_HEADERS.length).setValues(rows);
}

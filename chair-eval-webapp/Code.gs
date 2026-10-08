/**
 * iCACCESS 2026 – Session Chair Evaluation (Apps Script web app)
 *
 * SETUP (once, ~3 minutes)
 *  1. https://script.google.com -> New project. Name it "iCACCESS Chair Evaluation".
 *  2. Replace Code.gs with this file.
 *  3. File (+) -> HTML -> name it  index  (exactly) and paste index.html into it.
 *  4. Select the function  setup  and click Run. Authorize. The log prints the Google Sheet link.
 *  5. Deploy -> New deployment -> type "Web app"
 *       Execute as: Me      Who has access: Anyone
 *     -> Deploy, and share the "/exec" link with session chairs.
 *
 * DAY-OF CHANGES (no redeploy needed)
 *  Edit the "Sessions & Papers" tab: change a chair, move a paper by changing its Session ID,
 *  add rows for new papers. The form reads this tab every time it opens.
 *  In the form, chairs can also pick "Other" for chair / session, or add an unlisted paper.
 *
 * SHEET TABS
 *  Sessions & Papers  one row per paper (sessions without papers have a row with empty Paper ID)
 *  Responses          raw log, one row per paper per submission (never overwritten)
 *  Score Summary      one row per paper, latest evaluation wins; rebuilt after every submission
 */

// ----------------------------------------------------------------------------- settings
const SHEET_NAME = 'iCACCESS 2026 – Chair Evaluation';
const TAB_PAPERS = 'Sessions & Papers';
const TAB_RESPONSES = 'Responses';
const TAB_SUMMARY = 'Score Summary';
const TAB_AVG = 'Paper Averages';

const CRITERIA = [
  'Novelty & Originality',
  'Technical Quality & Methodology',
  'Clarity of Presentation',
  'Results & Discussion',
  'Q&A',
  'Time Management',
];
// Short guidance shown under each criterion in the form
const CRITERIA_HELP = [
  'New ideas, problem framing, contribution beyond existing work',
  'Soundness of approach, experiments and analysis',
  'Structure, slides, delivery and clarity of explanation',
  'Strength of results, comparisons and discussion of limitations',
  'Quality of answers and how well audience questions were handled',
  'Keeping to the allotted presentation time',
];
// Meaning of each score 0..5, shown on the buttons
const SCALE = ['Not acceptable', 'Poor', 'Fair', 'Good', 'Very good', 'Excellent'];

// Column layout of the "Sessions & Papers" tab
const PAPER_HEADERS = ['Session ID', 'Session Title', 'Track', 'Session Chair 1', 'Session Chair 2', 'Time', 'Room / Link', 'Paper ID', 'Paper Title'];
const P = { SID: 0, TITLE: 1, TRACK: 2, CHAIR1: 3, CHAIR2: 4, TIME: 5, ROOM: 6, PID: 7, PTITLE: 8 };

const MAX_COMMENT = 600;           // characters
const TOTAL_LABEL = `Total (/${5 * CRITERIA.length})`;
const LEGACY_NOTE = 'Scored before Time Management was split from Q&A (max 25)';

const RESPONSE_HEADERS = ['Timestamp', 'Submission ID', 'Session ID', 'Track', 'Session Chair', 'Paper ID',
  'Paper Title', 'Scheduled Session'].concat(CRITERIA.map((c, i) => `Q${i + 1}: ${c}`),
  [TOTAL_LABEL, 'Note', 'Best Paper Vote', 'Chair Comments']);
const R = { TS: 0, SID: 2, TRACK: 3, CHAIR: 4, PID: 5, PTITLE: 6, SCHED: 7, Q1: 8 };

const SUMMARY_HEADERS = ['Session ID', 'Track', 'Session Chair', 'Paper ID', 'Paper Title']
  .concat(CRITERIA.map((c, i) => `Q${i + 1}: ${c}`),
  [TOTAL_LABEL, 'Scheduled Session', 'Note', 'Last updated', 'Best Paper Vote', 'Chair Comments']);

// ----------------------------------------------------------------------------- seed data (from the planning workbook)
const SEED = [
  {
    session: "T1P1", sessionTitle: "Machine Learning Foundations and Intelligent Systems",
    track: "Track 1: Computing and Intelligent Systems",
    chairs: ["Dr. Md. Ruhul Amin", "Dr. Mirza Rasheduzzaman"], time: "Day 1, 11:40-12:40", room: "PD101",
    papers: [
      { id: 49, title: "SPPC: Benchmarking Selenium, Playwright, Puppeteer, and Cypress for Energy-Efficient Web Automation" },
      { id: 58, title: "Explainable Machine Learning for Cross-Species Myeloid Biomarker Discovery in Glioblastoma" },
      { id: 177, title: "An Interpretable Machine Learning Approach for Maternity Risk Prediction and Assessment" },
    ],
  },
  {
    session: "T1P2", sessionTitle: "Natural Language, Computer Vision, and Multimodal AI",
    track: "Track 1: Computing and Intelligent Systems",
    chairs: ["Prof. Dr. Kamruddin Nur", "Prof. Dr. Engr. Muhibul Haque Bhuyan"], time: "Day 1, 11:40-12:40", room: "PD102",
    papers: [
      { id: 94, title: "TaxNet-Bangladesh: Building a Domain-Specific Tax Question-Answering System for Businesses in Bangladesh" },
      { id: 162, title: "Distributed Transformer Inference for Sentiment Analysis: An HTCondor and DAGMan-Based Workflow Approach on AWS" },
      { id: 217, title: "AFDM-Aided PD-NOMA with Dynamic Power Allocation for High-Mobility THz Communications" },
    ],
  },
  {
    session: "T1P3", sessionTitle: "Wireless Networks and Optical Communication Systems",
    track: "Track 2: Wireless and Optical Communication",
    chairs: ["Dr. Nahid Akhter Jahan", "Dr. Mohammad Rifat Ahmmad Rashid"], time: "Day 1, 11:40-12:40", room: "PD103",
    papers: [
      { id: 33, title: "Performance Analysis of RIS-Assisted 6G Wireless Systems with Hybrid Architectures and Hardware Constraints" },
      { id: 116, title: "Novel Microstrip-fed Implantable Antenna Design Operating at 5.85 GHz for Medical Applications" },
      { id: 136, title: "An X-Band 2×2 MIMO Antenna Array with Enhanced Beamforming and Radiation Performance" },
    ],
  },
  {
    session: "T2P1", sessionTitle: "Cloud, Big Data, and Distributed Computing",
    track: "Track 1 & Track 5: Computing and Intelligent Systems",
    chairs: ["Dr. Mohammed Ashikur Rahman", "Prof. Dr. Md. Shahriar Rahman"], time: "Day 1, 14:30-16:30", room: "PD104",
    papers: [
      { id: 61, title: "Beyond Fragmentation: A Causal Analysis of Unicode NFKC Normalization Effects in Dialectal Bengali NER" },
      { id: 66, title: "Interpretable Psoriatic Lesion Classification via Multi-Cohort Gene Expression Profiling" },
      { id: 262, title: "MentalScreen: A Hybrid PHQ-9/GAD-7 and MentalRoBERTa Agentic Framework for Multi-Label Mental Health Detection with Deterministic Crisis Routing" },
      { id: 305, title: "Explainable Digital Addiction Severity Prediction Using Machine Learning, NLP, and Large Language Models" },
      { id: 377, title: "Graph-Enhanced Causal Reinforcement Learning for Proactive Customer Retention: A Comparative Benchmark" },
      { id: 365, title: "PSO-Based Selective Harmonic Elimination with Smart Cell-Bypassing for a 15-Level Asymmetric Cascaded H-Bridge Inverter" },
      { id: 230, title: "Comparing local GPT and Student Performance on Introductory Statistics MCQ Examinations" },
    ],
  },
  {
    session: "T2P2", sessionTitle: "Applied AI and Intelligent Computing Applications",
    track: "Track 1: Computing and Intelligent Systems",
    chairs: ["Dr. Mohammad Nurul Huda", "Prof. Dr. Mustafa Habib Chowdhury"], time: "Day 1, 14:30-16:30", room: "PD101",
    papers: [
      { id: 124, title: "HybridOsteoX: A Knee Osteoporosis Explainable AI Framework Using Hybrid CNN-ViT Fusion" },
      { id: 127, title: "BanglaRhet: Benchmarking Classical and Transformer Models for Rhetorical and Persuasion Detection in Bangla Political Speech" },
      { id: 147, title: "SplitSeg: Generalizable Skin Lesion Segmentation with ResNeSt-UNet" },
      { id: 362, title: "Graph Attention Versus Tabular Models for Early Liver Fibrosis Staging: A Leakage-Controlled Multi-Cohort Benchmark" },
      { id: 375, title: "Adapting BitNet b1.58 techniques in Convolutional Neural Networks for Efficient Deep Learning" },
      { id: 160, title: "Numerical Investigation of a Corrugated PDMS Diaphragm-based Fiber Optic Fabry-Perot Sensor for Acoustic Sensing" },
      { id: 210, title: "A 16.1-fJ/conv.-step 8-bit 100-MS/s SAR ADC for WLAN Receiver Baseband in 65-nm CMOS" },
      { id: 187, title: "Design of a generative AI agent as a learning support tool for special education needs students" },
    ],
  },
  {
    session: "T2P3", sessionTitle: "AI-Enabled Digital Learning and Educational Technologies",
    track: "Track 5: Digital Learning and Educational Technologies",
    chairs: ["Dr. Mohammad Shazzad Hossain", "Dr. Khairul Alam"], time: "Day 1, 14:30-16:30", room: "PD102",
    papers: [
      { id: 254, title: "BioCal RA: A Trustworthy and Explainable Multi-Agent Research Assistant for Biomedical Field" },
      { id: 275, title: "Multi-Representation Fusion with Subspace-Aware SMOTE for Source Code Vulnerability Detection" },
      { id: 322, title: "NOVA-Net: A Noise-Aware Deep Network for Robust Human Activity Recognition from Surveillance Videos" },
      { id: 358, title: "AdaLLM: A Subject-Adaptive RAG Framework Designed for the Question Answering Process of NCTB’s Class-8 Science & BGS Subjects" },
      { id: 208, title: "The Effect of e-KYC Adoption on the Cost Efficiency of Commercial Banks in Bangladesh: A Dynamic Panel Study" },
      { id: 279, title: "Programmable Remittances for Bangladesh A Permissioned Blockchain System for Diaspora-Controlled Household Payments" },
      { id: 280, title: "Architectural Differences among MFS, PSP, and PSO in Bangladesh: A Liability–Ledger Reference Model" },
    ],
  },
  {
    session: "T2P4", sessionTitle: "IoT, Embedded, and Cyber-Physical Systems",
    track: "Track 4: Smart and Cyber-Physical Systems",
    chairs: ["Prof. Dr. Sifat Momen", "Dr. Abul Barkat Sayeed Ud Doulah"], time: "Day 1, 14:30-16:30", room: "PD103",
    papers: [
      { id: 95, title: "MpoxFusionNet: Privacy-Aware Hybrid CNN-Transformer Fusion for Monkeypox Detection from Skin Lesion Images" },
      { id: 176, title: "Blockchain-Based Bug Bounty System with A Novel Weighted Reputation-Driven Consensus Mechanism" },
      { id: 238, title: "FormSense: A Continuous Fatigue and Form Tracking Application for Resistance Workout Monitoring Utilizing Phase-Graded IMU Analysis" },
      { id: 346, title: "High-Throughput Meritocratic Consensus: A Native Go Implementation of Reputation-Based Ordering for Hyperledger Fabric" },
      { id: 367, title: "A Low-Cost IoT-Based Smart Home Automation and Security System with Energy-Efficient Operation for Sustainable Living in Developing Regions" },
      { id: 282, title: "Floating Solar on an Oxbow Lake: Energy, Water, and Rice Co-Benefits at Bergobindopur Baor, Bangladesh" },
      { id: 276, title: "An Interpretable Ensemble Learning Framework for Predicting Students' Entrepreneurial Intention in Digital Entrepreneurship Education" },
    ],
  },
  {
    session: "T4P1", sessionTitle: "Machine Learning Applications and Data-Driven Systems",
    track: "Track 1: Computing and Intelligent Systems",
    chairs: ["Prof. Dr. Ishtiak Al Mamoon", "Dr. Aminur Rahman"], time: "Day 2, 11:00-13:00", room: "https://bdren.zoom.us/j/8428351030?pwd=7kfJZ1PoRiAzd0aKSn3l28Yuta2D1P.1&omn=92475321723",
    papers: [
      { id: 59, title: "An Explainable Lightweight CBAM-CNN with Focal Loss for Brain Tumor MRI Classification" },
      { id: 138, title: "HalluciNet: A Multi-Granularity Contrastive Framework for Factual Hallucination Detection in Large Language Models" },
      { id: 243, title: "ResNet and LSTM Based Hybrid Deep Learning Model for Reliable and Interpretable Epileptic Seizure Classification" },
      { id: 250, title: "An Interpretable Stacking Ensemble for Chronic Kidney Disease Screening and KDIGO Severity Staging" },
      { id: 332, title: "Meta-Learning for Few-Shot Personalization of Error-Related Potential Brain-Computer Interfaces" },
      { id: 376, title: "Kidney-Net:Feature-Centric and Minimal Biomarker-Based Prediction of Chronic Kidney Disease Using Machine Learning" },
    ],
  },
  {
    session: "T4P2", sessionTitle: "Intelligent Communication Networks and Computing",
    track: "Track 2: Wireless and Optical Communication + Track 1: Computing and Intelligent Systems",
    chairs: ["Prof. Dr. Ahmed Al Mansur", "Prof. Dr. Sifat Momen"], time: "Day 2, 11:00-13:00", room: "https://bdren.zoom.us/j/3426823862?pwd=qdTx7T0wafu1iseMaIbFJzZkwB20Gq.1&omn=9670458221",
    papers: [
      { id: 310, title: "Predicting the Effect of Drugs on Neonatal using Machine Learning and Explainable AI" },
      { id: 327, title: "Explainable Machine Learning and Causal Analysis for Obesity Prediction Using Knowledge Graphs" },
      { id: 323, title: "Computer Vision and Kalman Filtering for Driverless Vehicle Steering Angle Computation" },
      { id: 341, title: "An Integrated Dual-Module Cyber Physical System for Motorcycle Safety: Utilizing Pre-Ride Safety, Crash Detection and Swift Response with Mobile Application Companion" },
      { id: 175, title: "Isolation-Wall Integrated Graphene THz MIMO Antenna with Wideband and High-Diversity Performance for 6G Applications" },
      { id: 295, title: "A Dual-Focus UX Prioritization Framework for Educational Games Using Sentiment Analysis" },
    ],
  },
  {
    session: "T4P3", sessionTitle: "Electronics and Hardware for Intelligent Computing",
    track: "Track 3: Electronics, Devices, and Nanotechnology + Track 1: Computing and Intelligent Systems",
    chairs: ["Dr. Khairul Alam", "Dr. Mirza Rasheduzzaman"], time: "Day 2, 11:00-13:00", room: "https://bdren.zoom.us/j/5012406330?pwd=czJaVXJnaHdJZlhpM21RWWF1a2hNQT09&omn=91831440282",
    papers: [
      { id: 273, title: "A Lightweight Hybrid Quantum-Classical CNN for Brain Tumor MRI Classification" },
      { id: 85, title: "Multi-Metaheuristic Optimisation of Cascade Controllers for DC-DC Converters: A Comparative Study of PI, PID, and Sliding Mode Control" },
      { id: 148, title: "Cross-Design Limitations of ML-Based PPA Prediction in OpenLane" },
      { id: 274, title: "Modulation Strategy for Optimizing Semiconductor Losses for A High Power Step-Down Dual Active Bridge Converter in AI Data Center Applications" },
      { id: 345, title: "An Au/ITO Dual-Layer Photonic Crystal Fiber Surface Plasmon Resonance Biosensor for Label-Free Detection and Discrimination of Basal, HeLa, and Jurkat Cancer Cells" },
      { id: 139, title: "A Comparative Study of Statistical, Machine Learning, and Deep Learning Models for Short-Term Electricity Load Forecasting on the Bangladesh National Grid" },
    ],
  },
  {
    session: "T4P4", sessionTitle: "Cybersecurity, Blockchain, and Trustworthy Computing",
    track: "Track 1: Computing and Intelligent Systems",
    chairs: ["Prof. Dr. Engr. Muhibul Haque Bhuyan", "Dr. Mohammad Shazzad Hossain"], time: "Day 2, 11:00-13:00", room: "https://bdren.zoom.us/j/4074534482?pwd=krdtcqcqU2E4TPlssbKu9CBmk1aJre.1&omn=98496255250",
    papers: [
      { id: 48, title: "CEC: A Non-Stationary Benchmarking Protocol for the Fair Evaluation of Metaheuristic Optimizers" },
      { id: 64, title: "An Explainable Ensemble Learning Approach for Anemia Prediction Using Clinical and Biochemical Data" },
      { id: 86, title: "DCAF-Net: Dual-Branch Convolutional Network with Spatial Cross-Attention Fusion for Thyroid Nodule Classification" },
      { id: 215, title: "An Integrated Edge-AI Framework for Interpretable Respiratory Screening via Adaptive Cough Analysis in Low-Resource Settings" },
      { id: 263, title: "Illusion of Sequence: Rigorously Validated Null Result for Recurrent and Attention-Based Memory-Forensic Ransomware Family Classification" },
      { id: 355, title: "Temporal Capability Cryptography: Cryptographic State Evolution for Forward Authorization in Distributed Systems" },
    ],
  },
  {
    session: "T4P5", sessionTitle: "Human-Centered Computing and Interaction Design",
    track: "Track 1: Computing and Intelligent Systems",
    chairs: ["Prof. Dr. Kamruddin Nur", "Dr. Nahid Akhter Jahan"], time: "Day 2, 11:00-13:00", room: "https://bdren.zoom.us/j/6484705712?pwd=r2vMz5RDbK87nBoCzOyaSvbW4H3hy1.1&omn=96422492579",
    papers: [
      { id: 251, title: "Continuous Bengali Sign Language Recognition from Sentence-Level Videos Using Deep Learning Architectures" },
      { id: 265, title: "VNetLS: Supervised 3D VNet-Based MRI Enhancement with Loss Optimization" },
      { id: 266, title: "Cartographer: Transforming Code Repositories into LLM-Optimized Semantic Graphs" },
      { id: 283, title: "An Integrated Gradient-boosting and Session-based Deep Learning Framework for Demand forecasting and Customer Personalization" },
    ],
  },
  {
    session: "T4P6", sessionTitle: "Emerging Topics in Computing and Intelligent Systems",
    track: "Track 1: Computing and Intelligent Systems",
    chairs: ["Dr. Md. Ashraful Haque, PhD", "Dr. Md. Ruhul Amin"], time: "Day 2, 11:00-13:00", room: "https://meet.google.com/warndfcavc",
    papers: [
      { id: 79, title: "Dual-Input ConvNeXt with Spatial Cross-Attention for Colonoscopy Mayo Scoring" },
      { id: 135, title: "FairHireATS: An Intersectional Bias Detection and Mitigation Framework for Automated Resume Screening" },
      { id: 166, title: "Explainable Machine Learning and Country-Level Trade Segmentation for Global Electric Vehicle Trade" },
      { id: 167, title: "Linux Malware Detection using API Call Graphs with Graph2Vec and GraphSAGE Model" },
      { id: 354, title: "Integrated Machine Learning and Deep Learning Pipeline for Discovering Diagnostic and Prognostic Biomarkers of Colon Cancer" },
      { id: 373, title: "A Zero-Initialized Residual MLP Head for Lung Cancer CT Scan Image Classification: A Comparative Study using five CNN Backbones" },
    ],
  },
];

// ----------------------------------------------------------------------------- setup
function setup() {
  const props = PropertiesService.getScriptProperties();
  const existing = props.getProperty('SHEET_ID');
  if (existing) {
    Logger.log('Already set up. Sheet: ' + SpreadsheetApp.openById(existing).getUrl());
    Logger.log('To start over, run resetSetup (the old sheet is kept in your Drive).');
    return;
  }
  const ss = SpreadsheetApp.create(SHEET_NAME);

  writePapersTab_(ss.getSheets()[0].setName(TAB_PAPERS));

  styleHeader_(ss.insertSheet(TAB_RESPONSES), RESPONSE_HEADERS);
  styleHeader_(ss.insertSheet(TAB_SUMMARY), SUMMARY_HEADERS).setColumnWidth(5, 420);

  props.setProperty('SHEET_ID', ss.getId());
  Logger.log('Sheet created: ' + ss.getUrl());
  Logger.log('Next: Deploy -> New deployment -> Web app (Execute as: Me, Access: Anyone).');
}

/**
 * Replace ONLY the "Sessions & Papers" tab with the schedule in SEED (e.g. after the final program).
 * Responses and Score Summary are kept as they are.
 */
function updateSchedule() {
  const ss = ss_();
  const sh = ss.getSheetByName(TAB_PAPERS) || ss.insertSheet(TAB_PAPERS, 0);
  writePapersTab_(sh);
  ensureHeaders_(ss);
  Logger.log('"Sessions & Papers" updated: ' + SEED.length + ' sessions. Responses were not touched.');
}

function writePapersTab_(sh) {
  const rows = [];
  SEED.forEach(s => {
    const head = [s.session, s.sessionTitle, s.track, s.chairs[0] || '', s.chairs[1] || '', s.time, s.room];
    if (s.papers.length) s.papers.forEach(p => rows.push(head.concat([p.id, p.title])));
    else rows.push(head.concat(['', '']));
  });
  sh.clear();
  styleHeader_(sh, PAPER_HEADERS);
  sh.getRange(2, 1, rows.length, PAPER_HEADERS.length).setValues(rows);
  [90, 320, 300, 240, 240, 150, 160, 80, 520].forEach((w, i) => sh.setColumnWidth(i + 1, w));
}

/** Forget the linked sheet so setup() creates a fresh one. */
function resetSetup() {
  PropertiesService.getScriptProperties().deleteProperty('SHEET_ID');
  Logger.log('Reset. Run setup again.');
}

let LOCK_HELD_ = false;      // true while saveEvaluation holds the script lock (the lock is not re-entrant)

/**
 * Brings sheets created by an older version up to the current layout. Idempotent and safe to call often:
 *  - missing header cells (Best Paper Vote / Chair Comments) are added;
 *  - when a criterion was split (Q&A / Time Management) the new, blank column is inserted after the old one,
 *    earlier Responses rows are flagged in the Note column, and the summary is rebuilt. No score is lost.
 */
function ensureHeaders_(ss) {
  const nQ = CRITERIA.length;
  // [tab, expected headers, 1-based column of the LAST criterion in the current layout]
  const specs = [[TAB_RESPONSES, RESPONSE_HEADERS, 8 + nQ], [TAB_SUMMARY, SUMMARY_HEADERS, 5 + nQ]];
  const legacy = (sh, qEnd) => String(sh.getRange(1, qEnd).getValue()).indexOf('Total') === 0;
  const stale = () => specs.some(([name, headers, qEnd]) => {
    const sh = ss.getSheetByName(name);
    return sh && (legacy(sh, qEnd) || String(sh.getRange(1, headers.length).getValue()) !== headers[headers.length - 1]);
  });
  if (!stale()) return;

  const lock = LOCK_HELD_ ? null : LockService.getScriptLock();
  if (lock) lock.waitLock(30000);
  try {
    if (!stale()) return;                       // another request fixed it while we waited
    let inserted = false;
    specs.forEach(([name, headers, qEnd]) => {
      const sh = ss.getSheetByName(name);
      if (!sh) return;
      if (legacy(sh, qEnd)) {
        sh.insertColumnAfter(qEnd - 1);         // new criterion column, blank for earlier rows
        inserted = true;
        if (name === TAB_RESPONSES && sh.getLastRow() > 1) {
          const noteCol = RESPONSE_HEADERS.indexOf('Note') + 1;
          const rng = sh.getRange(2, noteCol, sh.getLastRow() - 1, 1);
          rng.setValues(rng.getValues().map(([v]) => [(v ? v + '; ' : '') + LEGACY_NOTE]));
        }
      }
      styleHeader_(sh, headers);
    });
    if (inserted) rebuildSummary();             // summary rows now line up with the new layout
  } finally {
    if (lock) lock.releaseLock();
  }
}

function styleHeader_(sh, headers) {
  sh.getRange(1, 1, 1, headers.length).setValues([headers])
    .setFontWeight('bold').setBackground('#0B1F3A').setFontColor('#FFFFFF').setWrap(true);
  sh.setFrozenRows(1);
  return sh;
}

function ss_() {
  const id = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  if (!id) throw new Error('Not set up yet. Run setup() in the script editor first.');
  return SpreadsheetApp.openById(id);
}

/** Sessions (in sheet order) with their papers, read live from the sheet. */
function readSessions_(ss) {
  const values = ss.getSheetByName(TAB_PAPERS).getDataRange().getValues().slice(1);
  const sessions = [], byId = {};
  values.forEach(r => {
    const sid = String(r[P.SID]).trim();
    if (!sid) return;
    let s = byId[sid];
    if (!s) {
      s = byId[sid] = { id: sid, title: '', track: '', chairs: [], time: '', room: '', papers: [] };
      sessions.push(s);
    }
    [P.CHAIR1, P.CHAIR2].forEach(c => {
      const name = String(r[c] || '').trim();
      if (name && s.chairs.indexOf(name) < 0) s.chairs.push(name);
    });
    [['title', P.TITLE], ['track', P.TRACK], ['time', P.TIME], ['room', P.ROOM]]
      .forEach(([k, c]) => { if (!s[k] && r[c]) s[k] = String(r[c]).trim(); });
    const pid = String(r[P.PID]).trim();
    if (pid) s.papers.push({ id: pid, title: String(r[P.PTITLE]).trim() });
  });
  return sessions;
}

// ----------------------------------------------------------------------------- web app + JSON API
/**
 * GET  /exec                -> the form page (when index.html is inside this project)
 * GET  /exec?action=config  -> JSON config   (for index.html hosted separately)
 * POST /exec  body = JSON payload (sent as text/plain) -> save, JSON result
 */
function doGet(e) {
  if (e && e.parameter && e.parameter.action === 'config') return json_(() => getConfig());
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('iCACCESS 2026 – Session Chair Evaluation')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function doPost(e) {
  return json_(() => saveEvaluation(JSON.parse(e.postData.contents)));
}

function json_(fn) {
  let out;
  try { out = { ok: true, data: fn() }; } catch (err) { out = { ok: false, error: String(err.message || err) }; }
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}

/** Everything the page needs. */
function getConfig() {
  const ss = ss_();
  ensureHeaders_(ss);
  const sessions = readSessions_(ss);
  const chairs = [].concat(...sessions.map(s => s.chairs)).filter((c, i, a) => c && a.indexOf(c) === i).sort();
  return { sessions, chairs, criteria: CRITERIA, criteriaHelp: CRITERIA_HELP, scale: SCALE, existing: existingScores_(ss) };
}

/** Latest saved scores per paper AND chair (from Score Summary): { paperId: [ {chair, scores, ...}, ... ] }.
 *  The page shows each chair only their own entry, so chairs never overwrite one another. */
function existingScores_(ss) {
  const sum = ss.getSheetByName(TAB_SUMMARY);
  const out = {};
  if (sum.getLastRow() < 2) return out;
  const nQ = CRITERIA.length;
  sum.getRange(2, 1, sum.getLastRow() - 1, SUMMARY_HEADERS.length).getValues().forEach(r => {
    const id = String(r[3]).trim();
    if (!id) return;
    const at = r[nQ + 8];
    (out[id] = out[id] || []).push({
      session: String(r[0]), chair: String(r[2]),
      scores: r.slice(5, 5 + nQ).map(v => (v === '' || v === null ? null : Number(v))),   // blank = not scored yet
      vote: String(r[nQ + 9] || ''), comments: String(r[nQ + 10] || ''),
      at: at instanceof Date ? Utilities.formatDate(at, Session.getScriptTimeZone(), 'd MMM, h:mm a') : String(at),
    });
  });
  return out;
}

/**
 * payload = { chair, session, papers: [{ id, title?, scores: [0..5 x5], vote: 'Yes'|'No', comments?: string }] }
 * `session` may be a scheduled Session ID or free text (chair chose "Other").
 * Appends one Responses row per paper, then rebuilds the summary.
 */
function saveEvaluation(payload) {
  const chair = String(payload && payload.chair || '').trim();
  const session = String(payload && payload.session || '').trim();
  const papers = (payload && payload.papers) || [];
  if (!chair) throw new Error('Please enter the session chair name.');
  if (!session) throw new Error('Please select or enter the session.');
  if (!papers.length) throw new Error('Please add at least one paper.');

  const ss = ss_();
  const sessions = readSessions_(ss);
  const catalog = {};
  sessions.forEach(s => s.papers.forEach(p => { catalog[p.id] = { session: s.id, title: p.title }; }));
  const sess = sessions.filter(s => s.id === session)[0];
  const track = sess ? sess.track : '';

  const now = new Date();
  const submissionId = Utilities.getUuid().slice(0, 8);
  const seen = {};
  const rows = papers.map(p => {
    const id = String(p.id || '').trim();
    if (!/^\d+$/.test(id)) throw new Error(`Invalid Paper ID "${id}". Use the numeric ID.`);
    if (seen[id]) throw new Error(`Paper ${id} was added twice.`);
    seen[id] = true;
    const scores = (p.scores || []).map(Number);
    if (scores.length !== CRITERIA.length || scores.some(v => !(v >= 0 && v <= 5) || v % 1)) {
      throw new Error(`Please score all ${CRITERIA.length} criteria (0–5) for paper ${id}.`);
    }
    const vote = String(p.vote || '').trim();
    if (vote !== 'Yes' && vote !== 'No') throw new Error(`Please choose the best paper vote (Yes or No) for paper ${id}.`);
    const comments = String(p.comments || '').trim().slice(0, MAX_COMMENT);
    const cat = catalog[id];
    const title = cat ? cat.title : String(p.title || '').trim();
    const notes = [];
    if (!sess) notes.push('Session entered manually');
    if (!cat) notes.push('Paper not in schedule');
    else if (cat.session !== session) notes.push(`Scheduled in ${cat.session}`);
    return [now, submissionId, session, track, chair, Number(id), title, cat ? cat.session : '']
      .concat(scores, [scores.reduce((a, b) => a + b, 0), notes.join('; '), vote, comments]);
  });

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  LOCK_HELD_ = true;
  try {
    ensureHeaders_(ss);
    const resp = ss.getSheetByName(TAB_RESPONSES);
    resp.getRange(resp.getLastRow() + 1, 1, rows.length, RESPONSE_HEADERS.length).setValues(rows);
    SpreadsheetApp.flush();
    rebuildSummary();
  } finally {
    LOCK_HELD_ = false;
    lock.releaseLock();
  }
  return { ok: true, count: rows.length, submissionId };
}

// ----------------------------------------------------------------------------- summary
/** One row per paper and chair from the Responses log; a chair's most recent evaluation of a paper wins. */
function rebuildSummary() {
  const ss = ss_();
  const resp = ss.getSheetByName(TAB_RESPONSES);
  const data = resp.getLastRow() > 1
    ? resp.getRange(2, 1, resp.getLastRow() - 1, RESPONSE_HEADERS.length).getValues() : [];

  const order = {};
  let n = 0;
  readSessions_(ss).forEach(s => s.papers.forEach(p => { order[p.id] = n++; }));

  const latest = {};
  data.forEach(r => {                        // key = paper + chair (case-insensitive)
    const key = String(r[R.PID]) + '|' + String(r[R.CHAIR]).trim().toLowerCase();
    if (!latest[key] || r[R.TS] >= latest[key][R.TS]) latest[key] = r;
  });

  const nQ = CRITERIA.length;
  const rows = Object.keys(latest).map(k => latest[k])
    .sort((a, b) => ((order[a[R.PID]] ?? 1e6 + Number(a[R.PID])) - (order[b[R.PID]] ?? 1e6 + Number(b[R.PID]))) || (a[R.TS] - b[R.TS]))
    .map(r => {
      return [r[R.SID], r[R.TRACK], r[R.CHAIR], r[R.PID], r[R.PTITLE]]
        .concat(r.slice(R.Q1, R.Q1 + nQ), [r[R.Q1 + nQ], r[R.SCHED] || '(not scheduled)', r[R.Q1 + nQ + 1], r[R.TS],
                              r[R.Q1 + nQ + 2] || '', r[R.Q1 + nQ + 3] || '']);
    });

  ensureHeaders_(ss);
  const sum = ss.getSheetByName(TAB_SUMMARY);
  if (sum.getLastRow() > 1) sum.getRange(2, 1, sum.getLastRow() - 1, SUMMARY_HEADERS.length).clearContent();
  if (rows.length) sum.getRange(2, 1, rows.length, SUMMARY_HEADERS.length).setValues(rows);
  rebuildAverages_(ss, rows);
}

/** 'Paper Averages' tab: one row per paper with the mean of every chair's latest scores. */
function rebuildAverages_(ss, rows) {
  const nQ = CRITERIA.length;
  const headers = ['Paper ID', 'Paper Title', 'Session ID', 'Chairs scored', 'Chairs']
    .concat(CRITERIA.map((c, i) => `Avg Q${i + 1}: ${c}`), [`Average Total (/${5 * nQ})`, 'Best Paper Votes (Yes)']);
  let sh = ss.getSheetByName(TAB_AVG);
  const fresh = !sh;
  if (fresh) sh = ss.insertSheet(TAB_AVG);
  if (fresh || String(sh.getRange(1, headers.length).getValue()) !== headers[headers.length - 1]) styleHeader_(sh, headers);
  const groups = {}, ids = [];
  rows.forEach(r => {
    const id = String(r[3]);
    if (!groups[id]) { groups[id] = []; ids.push(id); }
    groups[id].push(r);
  });
  const out = ids.map(id => {
    const g = groups[id];
    const avgs = [];
    for (let q = 0; q < nQ; q++) {
      const vals = g.map(r => r[5 + q]).filter(v => v !== '' && v !== null).map(Number);
      avgs.push(vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length * 100) / 100 : '');
    }
    const total = Math.round(avgs.reduce((a, b) => a + (b === '' ? 0 : b), 0) * 100) / 100;
    return [Number(id), g[0][4], g[0][0], g.length, g.map(r => r[2]).join('; ')]
      .concat(avgs, [total, g.filter(r => r[nQ + 9] === 'Yes').length]);
  });
  if (sh.getLastRow() > 1) sh.getRange(2, 1, sh.getLastRow() - 1, headers.length).clearContent();
  if (out.length) sh.getRange(2, 1, out.length, headers.length).setValues(out);
}

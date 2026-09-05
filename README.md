TRACK_ID=PS06

# RiskLens AI
### Transaction Risk Investigation Assistant

RiskLens AI is an evidence-grounded banking transaction investigation assistant designed to help human investigators identify and understand unusual customer transaction activity.

The system combines **deterministic risk detection**, **customer behavioural baselines**, **traceable transaction evidence**, and **Gemini-assisted explanations** to produce clear investigation reports without making autonomous fraud decisions.

> **RiskLens identifies activity requiring review — it does not determine that fraud has occurred. Human judgment remains authoritative.**

---

## Problem Statement

**Track:** Banking  
**Problem Statement:** Transaction Risk Investigation Assistant  
**Track ID:** PS06

The system analyses a customer's transaction history over several months and determines whether any activity requires investigator attention.

When unusual activity is detected, RiskLens explains:

- Which transactions require review
- Which risk indicators were triggered
- How the transactions are connected
- How the activity differs from the customer's historical behaviour
- What evidence the investigator should examine first

When no significant anomaly is detected, the system clearly reports:

> **NO ATTENTION REQUIRED**

---

## Key Features

### Deterministic Risk Detection

RiskLens evaluates transaction history using four explainable risk rules:

| Rule | Risk Indicator |
|---|---|
| **RISK-01** | Unusually Large Transfer |
| **RISK-02** | Burst of Payments to New Payee |
| **RISK-03** | Odd-Hours Activity |
| **RISK-04** | Multi-factor Behaviour Deviation |

### Behavioural Baseline

The system establishes the customer's historical transaction behaviour using factors such as:

- Transaction amount
- Typical transaction times
- Payee history
- Transaction channel
- Historical transaction patterns

Risk evaluation is based on the customer's own historical behaviour rather than relying only on fixed global thresholds.

### Evidence Traceability

Every flagged finding is connected to an actual transaction from the supplied CSV history.

RiskLens displays:

- Transaction ID
- Date and time
- Payee
- Amount
- Channel
- Triggered risk indicators

This allows investigators to trace findings directly back to the source evidence.

### Connected Activity Analysis

Related flagged transactions are presented together to expose patterns such as:

- Multiple payments to the same payee
- Rapid transaction bursts
- Cumulative flagged value
- Closely connected transaction timing

### Gemini-Assisted Investigation

Gemini receives only verified findings produced by the deterministic risk engine.

The AI explanation is structured into:

1. Attention Assessment
2. Key Findings
3. Connected Activity
4. Deviation from Normal Behaviour
5. Investigator Priority
6. Limitation

The AI does **not** independently decide whether a transaction is fraudulent.

### Downloadable Investigation Report

Investigation results can be exported as a professional PDF report for review, documentation, or investigator handoff.

---

## System Architecture

```text
                    CUSTOMER TRANSACTION HISTORY
                               │
                               ▼
                       CSV INPUT & VALIDATION
                               │
                               ▼
                     BEHAVIOURAL BASELINE
                               │
                               ▼
                    DETERMINISTIC RISK ENGINE
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
          RISK-01          RISK-02          RISK-03
       Large Transfer    New Payee Burst    Odd Hours
              │                │                │
              └────────────────┼────────────────┘
                               │
                            RISK-04
                     Behaviour Deviation
                               │
                               ▼
                   VERIFIED INVESTIGATION DATA
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
          INVESTIGATION UI            GEMINI EXPLANATION
                 │                           │
                 └─────────────┬─────────────┘
                               ▼
                     INVESTIGATOR REPORT
                               │
                               ▼
                       HUMAN DECISION
```

---

## Investigation Workflow

```text
Transaction History
        ↓
Input Validation
        ↓
Historical Behaviour Analysis
        ↓
Risk Rule Evaluation
        ↓
Flagged Transaction Correlation
        ↓
Evidence-Grounded Investigation Report
        ↓
Gemini-Assisted Explanation
        ↓
Human Investigator Review
```

---

## Input Format

RiskLens accepts CSV transaction histories containing:

```text
transaction_id
date
time
description
payee
amount
channel
```

Example:

```csv
transaction_id,date,time,description,payee,amount,channel
TXN001,2026-06-01,09:30:00,Grocery Payment,Fresh Mart,1250,UPI
TXN002,2026-06-02,18:20:00,Utility Payment,Electricity Board,2100,UPI
```

Users can either upload their own CSV file or use the included demonstration scenarios.

---

## Demo Scenarios

### Normal Case

Dataset:

```text
data/normal_case.csv
```

Expected result:

```text
NO ATTENTION REQUIRED
```

The transaction history remains consistent with the customer's established behaviour and no significant activity requiring review is identified.

### Difficult Case

Dataset:

```text
data/transaction.csv
```

Expected result:

```text
ATTENTION RECOMMENDED
```

The demonstration case contains three connected transactions:

| Transaction | Time | Payee | Amount |
|---|---|---|---:|
| TXN041 | 02:14 | ABC Enterprises | ₹85,000 |
| TXN042 | 02:22 | ABC Enterprises | ₹40,000 |
| TXN043 | 02:31 | ABC Enterprises | ₹35,000 |

**Total flagged value:** ₹160,000

The activity triggers all four deterministic risk indicators and demonstrates transaction correlation, behavioural deviation analysis, and investigator prioritisation.

---

## Technology Stack

**Backend**
- Python
- Flask

**Data Analysis**
- Pandas

**AI Explanation Layer**
- Google Gemini API
- `google-genai`

**Frontend**
- HTML
- CSS
- JavaScript
- Jinja2

**Reporting**
- ReportLab PDF generation

**Testing**
- Python `unittest`
- Mocked Gemini integration testing

---

## Project Structure

```text
transaction-risk-assistant/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── normal_case.csv
│   └── transaction.csv
│
├── src/
│   ├── data_loader.py
│   ├── analysis_service.py
│   ├── risk_engine.py
│   ├── report_generator.py
│   └── gemini_service.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
└── tests/
    └── test_investigation.py
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd transaction-risk-assistant
```

### 2. Create a Virtual Environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## Gemini API Configuration

RiskLens uses Gemini only for generating the investigator-facing explanation.

Set your API key before running the application.

### PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Do **not** commit your real Gemini API key to the repository.

If Gemini is unavailable or its quota is exhausted, RiskLens continues to provide the deterministic investigation results.

---

## Running the Application

Start the Flask server:

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:8000
```

Select either:

- **Difficult Case — Connected Risk Activity**
- **Normal Case — Routine Behaviour**

or upload your own compatible CSV file.

Click **Run Investigation** to generate the report.

---

## Automated Testing

Run the complete test suite with:

```powershell
python -m unittest tests/test_investigation.py -v
```

Current test result:

```text
Ran 8 tests in 2.200s

OK
```

The suite verifies:

1. Normal activity produces `NO ATTENTION REQUIRED`
2. Difficult activity produces `ATTENTION RECOMMENDED`
3. Expected transactions are flagged
4. All four risk rules are detected
5. Findings remain traceable to the source history
6. Deterministic output remains non-accusatory
7. Gemini structured-response integration
8. Flask application routes and investigation flows

The Gemini integration is mocked during automated testing so test reliability does not depend on external API availability, network conditions, or API quota.

---

## AI Safety & Grounding

RiskLens follows a human-in-the-loop investigation model.

The deterministic risk engine identifies unusual activity first. Gemini is then provided with the verified investigation findings and is used only as an explanation layer.

The AI is instructed to:

- Use only verified investigation evidence
- Never invent transactions or evidence
- Never independently declare that fraud occurred
- Use cautious, investigator-oriented language
- Distinguish unusual activity from confirmed fraud
- Preserve human decision-making authority

If Gemini is unavailable, deterministic investigation results remain accessible.

---

## Design Principle

```text
Deterministic Detection
        +
Evidence Traceability
        +
Grounded AI Explanation
        +
Human Decision
        =
RiskLens AI
```

RiskLens is designed as an **investigation assistant**, not an autonomous fraud adjudication system.

---

## Final Status

```text
TRACK_ID                PS06
Application             RiskLens AI
Risk Rules              4
Automated Tests         8/8 Passing
Evidence Traceability   Enabled
AI Explanation          Gemini-assisted
PDF Reporting           Enabled
Human-in-the-loop       Enforced
```

---

## Disclaimer

RiskLens AI is a hackathon prototype designed to demonstrate evidence-grounded transaction risk investigation.

Risk indicators identify unusual activity that may warrant investigation. They do not establish that fraud has occurred, and final decisions should be made by an authorised human investigator.

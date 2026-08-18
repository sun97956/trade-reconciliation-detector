# AI-Powered Trade Reconciliation Discrepancy Detector

A Python tool that compares two transaction files, identifies reconciliation breaks, and uses the Anthropic API to analyze each discrepancy in plain English. For every break found, the tool returns a break type, likely cause, severity rating, and suggested action. Results are exported to a CSV report.

## Why It Matters

In financial operations, unresolved reconciliation breaks create operational risk, settlement failures, and P&L reporting inaccuracies. Manual break investigation is time-consuming and error-prone. This tool automates both the identification and analysis of breaks, reducing manual effort and accelerating resolution time.

## Tech Stack

- Python 3.13
- Pandas
- Anthropic API (Claude)
- python-dotenv

## Setup

1. Clone the repo
2. Install dependencies:

pip install pandas anthropic python-dotenv

3. Create a `.env` file in the project root:

ANTHROPIC_API_KEY=your_key_here


## How to Run

python main.py


## Sample Output

| trade_id | amount_x | amount_y | break_type | severity | suggested_action |
|----------|----------|----------|------------|----------|-----------------|
| T002 | 2000.0 | 2200.0 | Amount Mismatch | High | Investigate both systems... |
| T004 | 4000.0 | NaN | Missing Counterparty Record | High | Contact counterparty... |
| T005 | NaN | 5000.0 | Missing Data / Null Value Break | High | Investigate source system... |

## Project Structure

trade-reconciliation-detector/
├── main.py
├── README.md
├── .gitignore
├── data/
│ ├── book_a.csv
│ └── book_b.csv
└── output/

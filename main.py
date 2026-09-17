import anthropic
import json
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv(r"C:\Users\gabes\OneDrive\Desktop\Python Practice - Claude\.env")

client = anthropic.Anthropic()


class ReconciliationReport:
    """Compares two transaction DataFrames and identifies reconciliation breaks."""

    def __init__(self, df_a, df_b):
        self.df_a = df_a
        self.df_b = df_b

    def find_breaks(self):
        """Merges DataFrames and returns rows where amounts differ or are missing."""
        total = self.df_a.merge(self.df_b, how='outer', on='trade_id')
        diff = total[total['amount_x'] != total['amount_y']]
        self.breaks = diff
        return diff

    def summary(self):
        """Returns the total dollar value of all breaks."""
        self.breaks = self.breaks.fillna(0)
        self.breaks['diff'] = self.breaks['amount_x'] - self.breaks['amount_y']
        self.breaks['diff'] = abs(self.breaks['diff'])
        return self.breaks['diff'].sum()

    def export_report(self, file_name):
        """Exports the breaks DataFrame to a CSV file."""
        return self.breaks.to_csv(file_name, index=False)


def find_breaks(a, b):
    """Finds discrepancies between two transaction DataFrames."""
    if a.empty or b.empty:
        print('Empty DataFrames')
        exit()
    total = a.merge(b, how='outer', on='trade_id')
    diff = total[total['amount_x'] != total['amount_y']]
    return diff

# 1. add：read SOP rule files
def load_sop_chunks():
    """读取 SOP 文件，并按规则切分为独立的卡片列表（Chunks）"""
    if not os.path.exists('sop_rules.txt'):
        return []
    
    with open('sop_rules.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按 [Rule 进行分割
    raw_parts = content.split('[Rule')
    
    chunks = []
    for part in raw_parts:
        if part.strip():
            # 补回开头的 [Rule
            chunk_text = '[Rule' + part.strip()
            chunks.append(chunk_text)
            
    return chunks

def call_api(row):
    """Calls the Anthropic API for a single break row and returns parsed JSON."""
    prompt = (
        f"You are a financial data analyst. Here are the SOP rule chunks:\n"
        f"{sop_chunks}\n\n"
        f"here are the reconciliation break:"
        f"trade_id: {row['trade_id']}, "
        f"amount_x: {row['amount_x']}, "
        f"amount_y: {row['amount_y']}.\n"
        f"1. Identify which SOP rule chunk applies to this break.\n"
        f"2. Explain what the break_type, likely_cause, severity, and suggested_action are.\n"
        f"ONLY RESPOND IN JSON with fields: matched_rule, break_type, likely_cause, severity, suggested_action."
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    try:
        raw = message.content[0].text
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError:
        print(f"Error: API did not return valid JSON for trade {row['trade_id']}")
        print(raw)
        return None


if __name__ == "__main__":

    # Load input files
    book_a = pd.read_csv('data/book_a.csv')
    book_b = pd.read_csv('data/book_b.csv')

# 1. 启动时加载切好的 SOP 规则卡片
    sop_chunks = load_sop_chunks()
    print(f"Loaded {len(sop_chunks)} SOP rule chunks successfully.")

    # Find breaks
    diff = find_breaks(book_a, book_b)
    print(f"Found {len(diff)} breaks.")

# Call API for each break
    results = []
    for i, row in diff.iterrows():
        print(f"Analyzing break: {row['trade_id']}...")
        # 2. 把 sop_chunks 传给 call_api
        parsed = call_api(row, sop_chunks)
        if parsed:
            results.append(parsed)
        else:
            results.append({
                'matched_rule': 'Unknown',
                'break_type': 'Unknown', 
                'likely_cause': 'API parsing failed', 
                'severity': 'Unknown', 
                'suggested_action': 'Manual review required'
            })

    # Add AI results as new columns
    results_df = pd.DataFrame(results)
    diff = pd.concat([diff.reset_index(drop=True), results_df.reset_index(drop=True)], axis=1)

    # Export report
    os.makedirs('output', exist_ok=True)
    diff.to_csv('output/report.csv', index=False)
    print("Report exported to output/report.csv")

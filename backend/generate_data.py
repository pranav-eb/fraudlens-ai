# generate_data.py
# --------------------------------------------------------------------------
# Synthetic dataset generator for testing FraudLens AI
# Produces a realistic messy CSV with ~100,000 rows including:
#   - Various currency formats
#   - Multiple timestamp formats
#   - City aliases
#   - Missing values
#   - Invalid IPs
#   - Duplicate rows
#   - ~8% injected fraud patterns
# --------------------------------------------------------------------------

import random
import string
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

N_ROWS = 100_000
N_USERS = 3_000
N_DEVICES = 6_000

CITIES = [
    "Mumbai", "BOM", "Bombay", "Delhi", "New Delhi", "DEL",
    "Bangalore", "Bengaluru", "BLR", "Chennai", "Madras", "MAA",
    "Kolkata", "Calcutta", "CCU", "Hyderabad", "HYD",
    "Pune", "PNQ", "Ahmedabad", "AMD", "Jaipur", "JAI",
    "Lucknow", "LKO", "Surat",
]

PAYMENT_METHODS = ["UPI", "Net Banking", "Debit Card", "Credit Card", "NEFT", "IMPS"]

START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2025, 1, 1)


def random_ip(valid: bool = True) -> str:
    if valid:
        return ".".join(str(random.randint(1, 254)) for _ in range(4))
    # Generate invalid IPs
    return random.choice([
        "999.999.999.999",
        "abc.def.ghi.jkl",
        "192.168.1",
        "0.0.0.0.0",
        "256.0.0.1",
        "",
        "N/A",
    ])


def random_amount_str(amt: float, corrupt: bool = False) -> str:
    if corrupt:
        return random.choice([
            f"₹{amt:,.2f}",
            f"INR {amt:.0f}",
            f"Rs {amt:,.0f}",
            f"{amt}  ",
            f"  ₹{amt:,.1f}  ",
            "N/A",
            "",
        ])
    return random.choice([
        f"{amt:.2f}",
        f"₹{amt:,.2f}",
        f"INR{amt:.0f}",
    ])


def random_timestamp(base: datetime, corrupt: bool = False) -> str:
    ts = base + timedelta(
        days=random.randint(0, 364),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    if corrupt:
        fmts = [
            ts.strftime("%d-%m-%Y %H:%M"),
            ts.strftime("%m/%d/%Y %I:%M %p"),
            ts.strftime("%Y/%m/%d %H:%M:%S"),
            ts.strftime("%d %b %Y"),
            "INVALID_DATE",
            "",
        ]
        return random.choice(fmts)
    return ts.isoformat()


def generate():
    users   = [f"USR{i:05d}" for i in range(N_USERS)]
    devices = [f"DEV{i:06d}" for i in range(N_DEVICES)]

    # Assign each user a "base" spending pattern
    user_avg_amt = {u: random.uniform(500, 50_000) for u in users}
    user_city    = {u: random.choice(CITIES) for u in users}
    user_device  = {u: random.choice(devices[:N_DEVICES // 2]) for u in users}

    rows = []
    for i in range(N_ROWS):
        user  = random.choice(users)
        avg   = user_avg_amt[user]
        is_corrupted = random.random() < 0.15   # 15% messy records
        is_fraud_row = random.random() < 0.08   # 8% injected fraud

        if is_fraud_row:
            amt = avg * random.uniform(5, 15)   # spike amount
            city    = random.choice([c for c in CITIES if c != user_city[user]])  # new city
            device  = random.choice(devices[N_DEVICES // 2:])                     # new device
            hour_ts = datetime(2024, 1, 1) + timedelta(
                days=random.randint(0, 364), hours=random.randint(0, 4)            # 0-4 AM
            )
        else:
            amt  = max(10, np.random.lognormal(np.log(avg), 0.4))
            city    = user_city[user] if random.random() > 0.05 else random.choice(CITIES)
            device  = user_device[user] if random.random() > 0.05 else random.choice(devices)
            hour_ts = datetime(2024, 1, 1) + timedelta(
                days=random.randint(0, 364), hours=random.randint(8, 22)
            )

        txn_id = f"TXN{i:010d}" + ("X" if random.random() < 0.005 else "")

        row = {
            "transaction_id":     txn_id,
            "user_id":            user if random.random() > 0.02 else np.nan,
            "transaction_amount": random_amount_str(amt, is_corrupted),
            "timestamp":          random_timestamp(hour_ts, is_corrupted),
            "city":               city if random.random() > 0.03 else np.nan,
            "device_id":          device if random.random() > 0.04 else np.nan,
            "payment_method":     random.choice(PAYMENT_METHODS) if random.random() > 0.05 else np.nan,
            "ip_address":         random_ip(valid=random.random() > 0.08),
            "balance":            round(random.uniform(1000, 500_000), 2) if random.random() > 0.10 else np.nan,
            "is_fraud":           1 if is_fraud_row else 0,
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # ── Inject duplicate rows (1%) ──────────────────────────────────────
    dup_sample = df.sample(frac=0.01, random_state=42)
    df = pd.concat([df, dup_sample], ignore_index=True)

    # ── Shuffle ─────────────────────────────────────────────────────────
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    filename = "sample_transactions.csv"
    df.to_csv(filename, index=False)
    print(f"✅  Generated {len(df):,} rows → {filename}")
    print(f"    Injected fraud rows : {df['is_fraud'].sum():,}")
    print(f"    Columns             : {list(df.columns)}")


if __name__ == "__main__":
    generate()

"""Generate SIMULATED IT service desk ticket data (no real company or customer data)."""
import random, csv
from datetime import datetime, timedelta

random.seed(42)
START, END = datetime(2026, 4, 1), datetime(2026, 9, 30)

# category: (weight, base resolution hours, reopen probability)
CATEGORIES = {
    "Password reset / account lockout": (22, 0.6, 0.03),
    "Email / Outlook": (14, 2.5, 0.08),
    "Wi-Fi / network": (13, 4.0, 0.15),
    "Software install / licence": (12, 3.0, 0.06),
    "Hardware fault (laptop, printer)": (11, 8.0, 0.12),
    "Teams / video meetings": (9, 2.0, 0.07),
    "VPN / remote access": (8, 3.5, 0.14),
    "New starter / leaver setup": (6, 6.0, 0.04),
    "Business application error": (5, 10.0, 0.18),
}
PRIORITY = {"P1 Critical": (4, 4), "P2 High": (16, 8), "P3 Medium": (50, 24), "P4 Low": (30, 48)}  # weight, SLA hours
CHANNELS = {"Phone": 30, "Email": 35, "Portal": 25, "Walk-up": 10}
AGENTS = ["Agent A", "Agent B", "Agent C", "Agent D", "Agent E"]
AGENT_SPEED = {"Agent A": 0.85, "Agent B": 1.0, "Agent C": 1.1, "Agent D": 0.95, "Agent E": 1.25}

def pick(d):
    keys = list(d); w = [d[k][0] if isinstance(d[k], tuple) else d[k] for k in keys]
    return random.choices(keys, weights=w)[0]

rows, tid = [], 1000
day = START
while day <= END:
    if day.weekday() < 5:
        month_boost = 1.25 if day.month in (6, 9) else 1.0      # busier months
        monday_boost = 1.3 if day.weekday() == 0 else 1.0
        n = int(random.gauss(13, 3) * month_boost * monday_boost)
        for _ in range(max(n, 4)):
            hour = random.choices(range(8, 18), weights=[8, 14, 13, 11, 8, 9, 11, 10, 8, 4])[0]
            created = day.replace(hour=hour, minute=random.randint(0, 59))
            cat = pick(CATEGORIES); pri = pick(PRIORITY); ch = pick(CHANNELS)
            agent = random.choice(AGENTS)
            base = CATEGORIES[cat][1] * AGENT_SPEED[agent] * random.lognormvariate(0, 0.55)
            if pri.startswith("P1"): base *= 0.5
            if pri.startswith("P4"): base *= 1.6
            res_h = round(max(base, 0.1), 2)
            first_resp = round(random.lognormvariate(2.3, 0.6) * (0.6 if pri.startswith(("P1", "P2")) else 1.0), 1)
            sla = PRIORITY[pri][1]
            breached = int(res_h > sla)
            reopened = int(random.random() < CATEGORIES[cat][2])
            csat = min(5, max(1, round(random.gauss(4.4 - 0.9 * breached - 0.6 * reopened, 0.7))))
            rows.append([f"INC{tid}", created.strftime("%Y-%m-%d %H:%M"), cat, pri, ch, agent,
                         first_resp, res_h, sla, breached, reopened, csat])
            tid += 1
    day += timedelta(days=1)

with open("data/tickets_simulated.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticket_id", "created_at", "category", "priority", "channel", "agent",
                "first_response_mins", "resolution_hours", "sla_target_hours", "sla_breached", "reopened", "csat_score"])
    w.writerows(rows)
print(len(rows), "tickets written")

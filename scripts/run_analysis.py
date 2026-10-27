"""Load the CSV into SQLite, run every query in sql/queries.sql, save results and charts."""
import re, csv, sqlite3, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir(os.path.join(os.path.dirname(__file__), ".."))
con = sqlite3.connect(":memory:")
con.execute("""CREATE TABLE tickets (ticket_id TEXT, created_at TEXT, category TEXT, priority TEXT, channel TEXT,
 agent TEXT, first_response_mins REAL, resolution_hours REAL, sla_target_hours INTEGER,
 sla_breached INTEGER, reopened INTEGER, csat_score INTEGER)""")
with open("data/tickets_simulated.csv") as f:
    r = csv.reader(f); next(r)
    con.executemany("INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", r)

sql = open("sql/queries.sql").read()
blocks = re.findall(r"-- name: (\w+)\n(.*?);", sql, re.S)
res = {}
for name, q in blocks:
    cur = con.execute(q)
    cols = [c[0] for c in cur.description]; data = cur.fetchall()
    res[name] = (cols, data)
    with open(f"results/{name}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols); w.writerows(data)
    print(f"\n{name}"); print(cols)
    for row in data: print(row)

# ---- charts ----
C1, C2, C3 = "#1F3864", "#2E75B6", "#C00000"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
fig.suptitle("IT Service Desk Dashboard (simulated data, Apr-Sep 2026)", fontsize=14, fontweight="bold", color=C1)

m = res["q1_monthly_volume"][1]
ax[0][0].bar([x[0][5:] for x in m], [x[1] for x in m], color=C1)
ax[0][0].set_title("Tickets per month"); ax[0][0].set_xlabel("Month (2026)")
for i, x in enumerate(m): ax[0][0].text(i, x[1] + 8, x[1], ha="center", fontsize=8)

c = res["q2_top_categories"][1][::-1]
ax[0][1].barh([x[0] for x in c], [x[1] for x in c], color=C2)
ax[0][1].set_title("Tickets by category")

s = res["q3_sla_by_priority"][1]
cols = [C1 if x[3] >= 90 else C3 for x in s]
ax[1][0].bar([x[0] for x in s], [x[3] for x in s], color=cols)
ax[1][0].axhline(90, color="grey", ls="--", lw=1); ax[1][0].text(-0.4, 92, "90% target", ha="left", fontsize=8, color="grey")
ax[1][0].set_ylim(0, 105); ax[1][0].set_title("SLA met % by priority")
for i, x in enumerate(s): ax[1][0].text(i, x[3] - 7, f"{x[3]}%", ha="center", fontsize=9, color="white", fontweight="bold")

h = res["q5_tickets_by_hour"][1]
ax[1][1].plot([x[0] for x in h], [x[1] for x in h], color=C1, marker="o")
ax[1][1].set_title("Tickets by hour of day"); ax[1][1].set_xlabel("Hour"); ax[1][1].set_xticks([x[0] for x in h])

plt.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig("charts/dashboard.png", dpi=130); plt.close()
print("\ncharts saved")

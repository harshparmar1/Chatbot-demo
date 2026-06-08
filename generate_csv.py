import pandas as pd
import random
from datetime import datetime, timedelta

records = []

wards = ["ICU","OT","General Ward","Laboratory","OPD"]
departments = ["Critical Care","Surgery","Patient Care","Diagnostics","Outpatient"]
checklists = ["Hygiene Audit","Safety Audit","Waste Audit","Fire Safety Audit"]
statuses = ["Pass","Fail","Pending"]
priorities = ["Low","Medium","High","Critical"]

start_date = datetime(2025,1,1)

for i in range(1,501):

    ward = random.choice(wards)

    records.append({
        "audit_id": f"A{i:04d}",
        "date": (start_date + timedelta(days=random.randint(0,180))).strftime("%Y-%m-%d"),
        "floor": random.randint(1,5),
        "ward": ward,
        "department": random.choice(departments),
        "checklist_type": random.choice(checklists),
        "status": random.choice(statuses),
        "priority": random.choice(priorities),
        "assigned_staff": f"S{random.randint(1,30):03d}",
        "completion_time": random.randint(5,60),
        "image_uploaded": random.choice(["Yes","No"]),
        "escalation_status": random.choice(["Open","Closed"]),
        "risk_score": random.randint(20,95),
        "compliance_score": random.randint(60,100)
    })

df = pd.DataFrame(records)

df.to_csv("hospital_audit_500.csv", index=False)

print("hospital_audit_500.csv created successfully")
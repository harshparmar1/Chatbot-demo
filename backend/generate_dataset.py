import pandas as pd
import random
from datetime import datetime, timedelta

# ====================================================
# RANDOM SEED
# ====================================================

random.seed(42)

# ====================================================
# USERS
# ====================================================

first_names = [
    "Aarav","Vihaan","Arjun","Vivaan","Aditya","Rahul","Karan","Rohan",
    "Priya","Ananya","Sneha","Pooja","Meera","Neha","Divya","Kavya",
    "Amit","Sanjay","Raj","Vijay","Deepak","Akash","Harsh","Parth",
    "Ritika","Nisha","Komal","Bhavya","Krishna","Jay",
    "Ramesh","Suresh","Mahesh","Anil","Sunil","Vikas",
    "Ankit","Yash","Shivam","Nitin","Ajay","Manish",
    "Dhruv","Hardik","Milan","Nirav","Tushar","Chirag"
]

last_names = [
    "Patel","Shah","Mehta","Joshi","Parmar",
    "Desai","Trivedi","Gupta","Verma","Singh",
    "Kumar","Reddy","Naidu","Iyer","Nair",
    "Yadav","Chauhan","Solanki","Pandya","Mishra"
]

users = []

for i in range(1,101):

    name = f"{random.choice(first_names)} {random.choice(last_names)}"

    users.append(f"{name} ({1000+i})")


# ====================================================
# LOCATIONS
# ====================================================

cities = [

    "Madurai",
    "Trichy",
    "Chennai",
    "Coimbatore",
    "Salem",
    "Erode"

]

buildings = [

    "Building-1",
    "Building-2",
    "Building-3",
    "Building-4",
    "Building-5"

]

floors = [

    "Floor-1",
    "Floor-2",
    "Floor-3",
    "Floor-4",
    "Floor-5",
    "Floor-6",
    "Floor-7"

]

zones = [

    "Zone-1",
    "Zone-2",
    "Zone-3",
    "Zone-4",
    "Zone-5",
    "Zone-6",
    "Zone-7"

]

spots = [

    "Spot-1",
    "Spot-2",
    "Spot-3",
    "Spot-4",
    "Spot-5",
    "Spot-6",
    "Spot-7",
    "Spot-8",
    "Spot-9",
    "Spot-10"

]


# ====================================================
# CHECKLISTS
# ====================================================

checklists = [

    "Hand Hygiene Audit",
    "Floor Cleaning Inspection",
    "Fire Extinguisher Inspection",
    "Biomedical Waste Disposal",
    "Emergency Exit Inspection",
    "PPE Compliance Check",
    "Washroom Hygiene Check",
    "ICU Sanitization",
    "Operation Theatre Cleaning",
    "Patient Bed Cleaning",
    "Medical Equipment Cleaning",
    "Nurse Station Inspection",
    "Electrical Safety Inspection",
    "Generator Inspection",
    "Oxygen Cylinder Inspection",
    "Emergency Trolley Inspection",
    "Medicine Storage Inspection",
    "Visitor Register Audit",
    "Food Hygiene Inspection",
    "Kitchen Cleaning Inspection",
    "Water Quality Inspection",
    "Air Quality Inspection",
    "Laboratory Cleaning",
    "Blood Bank Inspection",
    "CSSD Cleaning",
    "Laundry Inspection",
    "Patient Toilet Inspection",
    "Lift Safety Inspection",
    "Pharmacy Temperature Check",
    "Wheelchair Inspection",
    "Ventilator Cleaning",
    "Defibrillator Inspection",
    "Fire Exit Audit",
    "Staff Locker Inspection",
    "Ceiling Cleaning",
    "Wall Cleaning",
    "Window Cleaning",
    "Biomedical Bin Inspection",
    "Sharps Disposal Audit",
    "Patient Waiting Area Inspection",
    "Reception Cleaning",
    "Ambulance Inspection",
    "Parking Safety Inspection",
    "Security Audit",
    "CCTV Inspection",
    "Medical Gas Pipeline Inspection",
    "Operation Table Inspection",
    "AC Filter Cleaning",
    "Drinking Water Inspection",
    "Hospital Corridor Cleaning"

]

print("✅ Part 1 Loaded Successfully")

# ====================================================
# REMARKS
# ====================================================

remarks = {

    "Pass": [

        "All standards followed successfully.",
        "Checklist completed successfully.",
        "Area found clean and compliant.",
        "Inspection completed without observations.",
        "No issues identified.",
        "Equipment functioning properly.",
        "Cleaning completed as per SOP.",
        "Hand hygiene maintained correctly.",
        "Fire safety equipment verified.",
        "Biomedical waste disposed correctly.",
        "PPE available for all staff.",
        "Emergency exit accessible.",
        "Generator operating normally.",
        "Medical equipment sanitized.",
        "Operation theatre cleaned.",
        "Pharmacy storage maintained.",
        "Patient waiting area clean.",
        "Washroom maintained properly.",
        "Visitor register updated.",
        "Food hygiene standards maintained.",
        "Water quality acceptable.",
        "Air quality within limits.",
        "Corridor cleaned successfully.",
        "Reception area well maintained.",
        "No maintenance required."

    ],

    "Pending": [

        "Supervisor verification pending.",
        "Inspection under review.",
        "Cleaning activity in progress.",
        "Maintenance team notified.",
        "Awaiting quality verification.",
        "Pending due to shift change.",
        "Awaiting final approval.",
        "Documentation pending.",
        "Inspection rescheduled.",
        "Checklist awaiting completion.",
        "Verification yet to begin.",
        "Pending manager review.",
        "Awaiting replacement material.",
        "Awaiting housekeeping team.",
        "Quality audit pending.",
        "Equipment verification pending.",
        "Follow-up inspection required.",
        "Inspection paused temporarily.",
        "Staff confirmation pending.",
        "Further validation required."

    ],

    "Fail": [

        "Hand hygiene protocol not followed.",
        "Fire extinguisher expired.",
        "Emergency exit blocked.",
        "Biomedical waste mixed incorrectly.",
        "Waste segregation policy violated.",
        "PPE kit unavailable.",
        "Medical equipment not sanitized.",
        "Floor found dirty.",
        "Cleaning log not updated.",
        "Electrical panel left open.",
        "Oxygen cylinder pressure below limit.",
        "Washroom requires immediate cleaning.",
        "Generator maintenance overdue.",
        "Patient bed damaged.",
        "Safety violation detected.",
        "Hospital protocol violated.",
        "Critical issue identified.",
        "Repeated inspection failure.",
        "Immediate action required.",
        "Area not compliant with standards.",
        "Operation theatre not sanitized.",
        "Sharps disposed incorrectly.",
        "Visitor register incomplete.",
        "Food storage temperature abnormal.",
        "Pharmacy refrigerator temperature high."

    ]

}


# ====================================================
# DATE GENERATOR
# ====================================================

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 6, 30)

TOTAL_DAYS = (END_DATE - START_DATE).days


def random_datetime():

    random_days = random.randint(0, TOTAL_DAYS)

    random_hours = random.randint(0, 23)

    random_minutes = random.randint(0, 59)

    return START_DATE + timedelta(
        days=random_days,
        hours=random_hours,
        minutes=random_minutes
    )


# ====================================================
# LOCATION GENERATOR
# ====================================================

def random_location():

    city = random.choice(cities)

    building = random.choice(buildings)

    floor = random.choice(floors)

    zone = random.choice(zones)

    spot = random.choice(spots)

    return f"{city}/{building}/{floor}/{zone}/{spot}"


# ====================================================
# STATUS GENERATOR
# ====================================================

def generate_status(hour):

    # Morning Shift
    if 7 <= hour <= 11:

        return random.choices(

            ["Pass","Pending","Fail"],

            weights=[70,15,15],

            k=1

        )[0]

    # Afternoon Shift
    elif 12 <= hour <= 17:

        return random.choices(

            ["Pass","Pending","Fail"],

            weights=[55,20,25],

            k=1

        )[0]

    # Evening/Night Shift
    else:

        return random.choices(

            ["Pass","Pending","Fail"],

            weights=[40,20,40],

            k=1

        )[0]


# ====================================================
# GET REMARK
# ====================================================

def get_remark(status):

    return random.choice(remarks[status])


print("✅ Part 2 Loaded Successfully")

# ====================================================
# GENERATE DATASET
# ====================================================

records = []

for i in range(500):

    created_by = random.choice(users)

    created_at = random_datetime()

    location = random_location()

    checklist = random.choice(checklists)

    status = generate_status(created_at.hour)

    remark = get_remark(status)

    records.append({

        "Created By": created_by,

        "Created At": created_at.strftime("%d-%m-%Y %H:%M"),

        "Location": location,

        "Checklist Name": checklist,

        "Remarks": remark,

        "Status": status

    })


# ====================================================
# CREATE DATAFRAME
# ====================================================

df = pd.DataFrame(records)


# ====================================================
# REMOVE DUPLICATES
# ====================================================

df.drop_duplicates(inplace=True)


# ====================================================
# IF DUPLICATES REMOVED THEN CREATE AGAIN
# ====================================================

while len(df) < 500:

    created_by = random.choice(users)

    created_at = random_datetime()

    location = random_location()

    checklist = random.choice(checklists)

    status = generate_status(created_at.hour)

    remark = get_remark(status)

    new_record = {

        "Created By": created_by,

        "Created At": created_at.strftime("%d-%m-%Y %H:%M"),

        "Location": location,

        "Checklist Name": checklist,

        "Remarks": remark,

        "Status": status

    }

    df = pd.concat(

        [df, pd.DataFrame([new_record])],

        ignore_index=True

    )

    df.drop_duplicates(inplace=True)


# ====================================================
# SHUFFLE DATA
# ====================================================

df = df.sample(

    frac=1,

    random_state=42

).reset_index(drop=True)


print("✅ 500 Records Generated Successfully")

# ====================================================
# EXPORT CSV
# ====================================================

OUTPUT_FILE = "verify_audit.csv"

df.to_csv(OUTPUT_FILE, index=False)

# ====================================================
# SUMMARY
# ====================================================

print("\n" + "=" * 60)
print("       VERIFY AUDIT DATASET GENERATED")
print("=" * 60)

print(f"\nCSV File Name : {OUTPUT_FILE}")
print(f"Total Records : {len(df)}")
print(f"Total Columns : {len(df.columns)}")

print("\nColumns:")
for col in df.columns:
    print(f"✔ {col}")

print("\nStatus Distribution")
print("-" * 30)
print(df["Status"].value_counts())

print("\nChecklist Distribution (Top 10)")
print("-" * 30)
print(df["Checklist Name"].value_counts().head(10))

print("\nCity Distribution")
print("-" * 30)

cities = df["Location"].str.split("/").str[0]
print(cities.value_counts())

print("\nSample Records")
print("-" * 30)
print(df.head(10))

print("\nCSV generated successfully.")
print("=" * 60)

# ====================================================
# VERIFY DATASET
# ====================================================

print("\nVerification")

print("Missing Values :", df.isnull().sum().sum())

print("Duplicate Rows :", df.duplicated().sum())

print("Unique Users :", df["Created By"].nunique())

print("Unique Locations :", df["Location"].nunique())

print("Unique Checklists :", df["Checklist Name"].nunique())

print("\nEverything completed successfully.")

print("=" * 60)
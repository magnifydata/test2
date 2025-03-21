import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Define lists of possible values for categorical columns
names = [f"Employee{i}" for i in range(500)]  # Generate unique names
cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
categories = ["Analyst", "Manager", "Engineer", "Technician", "Specialist"]
departments = ["Operations", "Engineering", "IT", "Maintenance", "Marketing", "Sales", "Finance", "HR"]

# --- Function to generate a random date within a reasonable range ---
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

# --- Generate Data ---
data = []
start_date = datetime(2020, 1, 1)
end_date = datetime(2024, 1, 1) # Up to the start of 2024

for i in range(500):
    age = np.random.randint(22, 65)  # Reasonable age range
    # Make salary depend on age and category (more realistic)
    base_salary = 40000 if categories[i % len(categories)] == "Analyst" else 60000  # Base salary by category
    salary = int(base_salary + (age - 22) * 1500 + np.random.normal(0, 10000))  # Add age factor and noise
    salary = max(40000, min(salary, 150000))  # Clamp salary to a reasonable range

    date = random_date(start_date, end_date) # Generate random date

    data.append({
        "Name": names[i],
        "Age": age,
        "Salary": salary,
        "City": random.choice(cities),
        "Category": categories[i % len(categories)],
        "Department": random.choice(departments),
        "Date": date.strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD
    })

# --- Create DataFrame and Save to CSV ---
df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)

print("Generated data.csv with 500 records.")

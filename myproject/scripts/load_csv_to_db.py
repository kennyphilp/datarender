#!/usr/bin/env python3

import sqlite3
import csv
import os
from pathlib import Path

# Determine project directory (parent of scripts directory)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

# Path to the CSV file
csv_file = PROJECT_DIR / 'datafiles' / 'Historic_School_Rolls_1996_to_2018.csv'

# Database file
db_file = PROJECT_DIR / 'datastore.db'

# Check if CSV exists
if not csv_file.exists():
    print(f"CSV file not found: {csv_file}")
    exit(1)

# Connect to SQLite database (creates if doesn't exist)
conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Create table
create_table_sql = '''
CREATE TABLE IF NOT EXISTS school_rolls (
    LA_Code TEXT,
    LA_Name TEXT,
    Code TEXT,
    Name TEXT,
    Sector TEXT,
    School_Type TEXT,
    F1996 INTEGER,
    F1997 INTEGER,
    F1998 INTEGER,
    F1999 INTEGER,
    F2000 INTEGER,
    F2001 INTEGER,
    F2002 INTEGER,
    F2003 INTEGER,
    F2004 INTEGER,
    F2005 INTEGER,
    F2006 INTEGER,
    F2007 INTEGER,
    F2008 INTEGER,
    F2009 INTEGER,
    F2010 INTEGER,
    F2011 INTEGER,
    F2012 INTEGER,
    F2013 INTEGER,
    F2014 INTEGER,
    F2015 INTEGER,
    F2016 INTEGER,
    F2017 INTEGER,
    F2018 INTEGER,
    ObjectId INTEGER
)
'''
cursor.execute(create_table_sql)

# Create indexes for frequently queried columns
print("Creating database indexes...")
cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON school_rolls(Name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_sector ON school_rolls(Sector)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_school_type ON school_rolls(School_Type)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_objectid ON school_rolls(ObjectId)')
print("Indexes created successfully.")

# Read CSV and insert data
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Convert empty strings to None for integers
        data = []
        for key in reader.fieldnames:
            value = row[key]
            if key.startswith('F') or key == 'ObjectId':
                data.append(int(value) if value else None)
            else:
                data.append(value)
        
        insert_sql = '''
        INSERT INTO school_rolls (
            LA_Code, LA_Name, Code, Name, Sector, School_Type,
            F1996, F1997, F1998, F1999, F2000, F2001, F2002, F2003,
            F2004, F2005, F2006, F2007, F2008, F2009, F2010, F2011,
            F2012, F2013, F2014, F2015, F2016, F2017, F2018, ObjectId
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_sql, data)

# Commit and close
conn.commit()
conn.close()

print(f"Data loaded into {db_file}")
print("Table: school_rolls")
print(f"Rows inserted: {sum(1 for _ in csv.DictReader(open(str(csv_file))))}")
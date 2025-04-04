import psycopg2
import pandas as pd

# Database connection details
hostname = "localhost"
database = "final"
username = "postgres"
port_id = 5432
password = "admin"

cur = None
conn = None

# Load the new CSV data
df = pd.read_csv("cpi_worker_data.csv")
df.columns = df.columns.str.strip()

# Ensure index_value is numeric
df["index value"] = pd.to_numeric(df["index value"], errors="coerce").fillna(0)

# Debugging: Check loaded data
print(df.head())
print(df.columns)
print(f"Total rows to insert: {len(df)}")

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(host=hostname, dbname=database, user=username, password=password, port=port_id)
    cur = conn.cursor()

    # Create table
    create_script = """
    CREATE TABLE IF NOT EXISTS cpi_worker_data (
        id SERIAL PRIMARY KEY,
        year INT,
        time_period VARCHAR(50),
        worker_type VARCHAR(50),
        base_year INT,
        worker_region VARCHAR(50),
        index_value DECIMAL(10, 2),
        UNIQUE (year, time_period, worker_type, base_year, worker_region, index_value)
    );
    """
    cur.execute(create_script)
    conn.commit()

    # Ensure DataFrame is not empty
    if not df.empty:
        # Insert data
        insert_query = """ 
        INSERT INTO cpi_worker_data (year, time_period, worker_type, base_year, worker_region, index_value) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (year, time_period, worker_type, base_year, worker_region, index_value) DO NOTHING;
        """
        records = df[['year', 'time period', 'worker type', 'base year', 'worker region', 'index value']].values.tolist()
        cur.executemany(insert_query, records)
        conn.commit()

        print("Data inserted successfully!")
    else:
        print("DataFrame is empty! No records inserted.")

except Exception as error:
    print("Error:", error)

finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()

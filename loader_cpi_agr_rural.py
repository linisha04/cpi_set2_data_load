import pandas as pd
import psycopg2

# Database connection details
hostname = "localhost"
database = "final"
username = "postgres"
port_id = 5432
password = "admin"

# Load the Excel data
df = pd.read_excel("consumer_price_index_CPI_for_agricultural_and_rural_labourers.xlsx")

# Convert column names to lowercase
df.columns = df.columns.str.lower()

# Convert state names to lowercase and strip extra spaces
df["state"] = df["state"].str.lower().str.strip()

# Debugging: Print first few rows
print(df.head())

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(host=hostname, dbname=database, user=username, password=password, port=port_id)
    cur = conn.cursor()

    # Create the table if it doesn't exist
    create_script = """
    CREATE TABLE IF NOT EXISTS consumer_price_index_CPI_for_agricultural_and_rural_labourers (
        id SERIAL PRIMARY KEY,
        state VARCHAR(100),
        year INT,
        month VARCHAR(20),
        category VARCHAR(50),
        index_value INT,
        labour_type VARCHAR(50),
        UNIQUE (state, year, month, category, labour_type)
    );
    """
    cur.execute(create_script)
    conn.commit()

    # Ensure DataFrame is not empty before inserting data
    if not df.empty:
        insert_query = """ 
        INSERT INTO consumer_price_index_CPI_for_agricultural_and_rural_labourers (state, year, month, category, index_value, labour_type) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (state, year, month, category, labour_type) 
        DO UPDATE SET index_value = EXCLUDED.index_value;
        """
        
        # Prepare records for insertion
        records = df[['state', 'year', 'month', 'category', 'index value', 'labour type']].values.tolist()
        cur.executemany(insert_query, records)
        conn.commit()

        print(" Data inserted/updated successfully!")
    else:
        print(" DataFrame is empty! No records inserted.")

except Exception as error:
    print("Error:", error)

finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()

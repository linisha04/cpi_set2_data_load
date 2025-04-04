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

# Load the Excel data
df = pd.read_excel("long_whole_sale_price_index(WPI)_calendar_wise.xlsx")

# Convert column names to lowercase and replace spaces with underscores
df.columns = df.columns.str.lower().str.replace(" ", "_")

# Ensure correct data types
df['commodity_code'] = df['commodity_code'].astype(int)
df['commodity_weight'] = df['commodity_weight'].astype(float)
df['year'] = df['year'].astype(int)
df['index_value'] = df['index_value'].astype(float)

# Debugging: Check if the DataFrame is loaded correctly
print(df.head())

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(host=hostname, dbname=database, user=username, password=password, port=port_id)
    cur = conn.cursor()

    # Create the table if it doesn't exist
    create_script = """
    CREATE TABLE IF NOT EXISTS whole_sale_price_index_WPI_calendar_wise (
        id SERIAL PRIMARY KEY,
        commodity_name TEXT,
        commodity_code BIGINT,
        commodity_weight DECIMAL(10,5),
        year INT,
        index_value DECIMAL(10,2),
        UNIQUE (commodity_code, year)
    );
    """
    cur.execute(create_script)
    conn.commit()

    # Ensure DataFrame is not empty before inserting data
    if not df.empty:
        insert_query = """ 
        INSERT INTO whole_sale_price_index_WPI_calendar_wise (commodity_name, commodity_code, commodity_weight, year, index_value) 
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (commodity_code, year) 
        DO UPDATE SET 
            commodity_name = EXCLUDED.commodity_name,
            commodity_weight = EXCLUDED.commodity_weight,
            index_value = EXCLUDED.index_value;
        """
        
        # Prepare records for insertion
        records = df[['commodity_name', 'commodity_code', 'commodity_weight', 'year', 'index_value']].values.tolist()
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

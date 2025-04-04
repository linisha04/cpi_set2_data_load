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
df = pd.read_excel("long_whole_sale_price_index(WPI)_financial_year_wise.xlsx")

# Convert column names to lowercase
df.columns = df.columns.str.lower()

# Debugging: Check if the DataFrame is loaded correctly
print(df.head())

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(host=hostname, dbname=database, user=username, password=password, port=port_id)
    cur = conn.cursor()

    # Create the table if it doesn't exist
    create_script = """
    CREATE TABLE IF NOT EXISTS whole_sale_price_index_WPI_financial_year_wise (
        id SERIAL PRIMARY KEY,
        commodity_name VARCHAR(255),
        commodity_code BIGINT,
        commodity_weight FLOAT,
        year INT,
        index_value FLOAT,
        UNIQUE (commodity_code, year)  -- Ensures no duplicate entries
    );
    """
    cur.execute(create_script)
    conn.commit()

    # Ensure DataFrame is not empty before inserting data
    if not df.empty:
        insert_query = """ 
        INSERT INTO whole_sale_price_index_WPI_financial_year_wise (commodity_name, commodity_code, commodity_weight, year, index_value) 
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (commodity_code, year)DO UPDATE SET 
            commodity_name = EXCLUDED.commodity_name,
            commodity_weight = EXCLUDED.commodity_weight,
            index_value = EXCLUDED.index_value;
        """
        
        # Prepare records for insertion
        records = df[['commodity name', 'commodity code', 'commodity weight', 'year', 'index value']].values.tolist()
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

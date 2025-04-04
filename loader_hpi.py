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
df = pd.read_excel("long_City_wise_Housing_Price_Indices.xlsx")

# Convert column names to lowercase
df.columns = df.columns.str.lower()

# Ensure 'value' is an integer
df['value'] = df['value'].fillna(0).astype(int)

# Debugging: Check if the DataFrame is loaded correctly
print(df.head())

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(host=hostname, dbname=database, user=username, password=password, port=port_id)
    cur = conn.cursor()

    # Create the table if it doesn't exist
    create_script = """
    CREATE TABLE IF NOT EXISTS city_wise_housing_price_indices (
        id SERIAL PRIMARY KEY,
        city VARCHAR(100),
        index_value DECIMAL(10,2),
        year INT,
        quarter VARCHAR(10),
        UNIQUE (city, year, quarter)
    );
    """
    cur.execute(create_script)
    conn.commit()

    # Ensure DataFrame is not empty before inserting data
    if not df.empty:
        insert_query = """ 
        INSERT INTO city_wise_housing_price_indices (city, index_value, year, quarter) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (city, year, quarter) 
        DO UPDATE SET index_value = EXCLUDED.index_value;
        """
        
        # Prepare records for insertion
        records = df[['city', 'value', 'year', 'quarter']].values.tolist()
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


# import psycopg2
# import pandas as pd

# # Database connection details
# hostname = "localhost"
# database = "final"
# username = "postgres"
# port_id = 5432
# password = "admin"

# cur = None
# conn = None

# # Load the Excel data
# df = pd.read_excel("long_City_wise_Housing_Price_Indices.xlsx")

# # Convert column names to lowercase
# df.columns = df.columns.str.lower()

# # Debugging: Check if the DataFrame is loaded correctly
# print(df.head())

# try:
#     # Connect to PostgreSQL
#     conn = psycopg2.connect(host=hostname, dbname=database, user=username, password=password, port=port_id)
#     cur = conn.cursor()

#     # Create the table if it doesn't exist
#     create_script = """
#     CREATE TABLE IF NOT EXISTS city_wise_housing_price_indices (
#         id SERIAL PRIMARY KEY,
#         city VARCHAR(100),
#         index_value INT,
#         year INT,
#         quarter VARCHAR(10),
#         UNIQUE (city, year, quarter)
#     );
#     """
#     cur.execute(create_script)
#     conn.commit()

#     # Ensure DataFrame is not empty before inserting data
#     if not df.empty:
#         insert_query = """ 
#         INSERT INTO city_wise_housing_price_indices (city, index_value, year, quarter) 
#         VALUES (%s, %s, %s, %s)
#         ON CONFLICT DO NOTHING;
#         """
        
#         # Prepare records for insertion
#         records = df[['city', 'value', 'year', 'quarter']].values.tolist()
#         cur.executemany(insert_query, records)
#         conn.commit()

#         print("Data inserted successfully!")
#     else:
#         print("DataFrame is empty! No records inserted.")

# except Exception as error:
#     print("Error:", error)

# finally:
#     if cur is not None:
#         cur.close()
#     if conn is not None:
#         conn.close()

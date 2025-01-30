import mysql.connector
from sentence_transformers import SentenceTransformer, util

# Establish connection to the MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Password@123",
    database="hackerrankdata1"
)

cursor = mydb.cursor()

# SQL query to get the latest submission for each user based on the time column
query = """
    SELECT 
        id, username, source_code
    FROM 
        CodeSubmissions
    WHERE 
        (username, time) IN (
            SELECT 
                username, MAX(time)
            FROM 
                CodeSubmissions
            GROUP BY 
                username
        )
"""

cursor.execute(query)
latest_submissions = cursor.fetchall()

# Create a table for storing copied submission details if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS CopiedSubmissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username1 VARCHAR(255),
    username2 VARCHAR(255),
    similarity_score FLOAT,
    source_code1 TEXT,
    source_code2 TEXT
)
"""
cursor.execute(create_table_query)
mydb.commit()

# Initialize the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Extract source codes and usernames from query result
source_codes = [submission[2] for submission in latest_submissions]
usernames = [submission[1] for submission in latest_submissions]
submission_ids = [submission[0] for submission in latest_submissions]

# Encode source codes into embeddings
code_embeddings = model.encode(source_codes, convert_to_tensor=True)

# Similarity threshold for detecting copied submissions
similarity_threshold = 0.98

# Compare each submission with others and store copied ones
print("The following users copied whose similary score is greater than 0.98")
for i in range(len(code_embeddings)):
    for j in range(i + 1, len(code_embeddings)):
        similarity = util.pytorch_cos_sim(code_embeddings[i], code_embeddings[j]).item()
        
        if similarity > similarity_threshold:
            # Insert the copied submission details into the CopiedSubmissions table
            insert_query = """
            INSERT INTO CopiedSubmissions (username1, username2, similarity_score, source_code1, source_code2)
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (usernames[i], usernames[j], similarity, source_codes[i], source_codes[j])
            cursor.execute(insert_query, values)
            mydb.commit()
            print(f"similarity between {usernames[i]} and {usernames[j]}: {similarity:.2f}")

# Close the cursor and database connection
cursor.close()
mydb.close()

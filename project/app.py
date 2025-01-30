# Import necessary libraries
from flask import Flask, render_template
import mysql.connector

# Initialize the Flask application
app = Flask(__name__)

# Function to establish a database connection
def get_db_connection():
    # Connects to the MySQL database with the specified credentials
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password@123",
        database="hackerrankdata1"
    )

# Define the main route for the home page
@app.route('/')
def home():
    # Open a database connection
    connection = get_db_connection()
    cursor = connection.cursor()  # Create a cursor object to interact with the database

    # SQL query to fetch specific fields (id, usernames, and similarity scores) from the CopiedSubmissions table
    query = "SELECT id, username1, username2, similarity_score FROM CopiedSubmissions"
    cursor.execute(query)  # Execute the query
    copied_submissions = cursor.fetchall()  # Fetch all results from the query

    # Close the database cursor and connection after retrieving data
    cursor.close()
    connection.close()
    
    # Render the 'home.html' template, passing the copied submissions data to the template
    return render_template("home.html", copied_submissions=copied_submissions)

# Define a route to show detailed information about a specific user’s submission
@app.route('/details/<username>')
def details(username):
    # Open a database connection
    connection = get_db_connection()
    cursor = connection.cursor()

    # SQL query to fetch the username and source code data for a given user, combining results for both users
    query = """
        SELECT username1, source_code1 FROM CopiedSubmissions WHERE username1 = %s
        UNION 
        SELECT username2, source_code2 FROM CopiedSubmissions WHERE username2 = %s
    """
    # Execute the query with the provided username as a parameter
    cursor.execute(query, (username, username))
    user_data = cursor.fetchone()  # Fetch a single row that matches the query

    # Close the database cursor and connection after retrieving data
    cursor.close()
    connection.close()
    
    # Check if any data was found for the given username
    if user_data:
        # If user data is found, unpack the data for rendering
        username, source_code = user_data
        return render_template("details.html", username=username, source_code=source_code)
    else:
        # If no data is found, redirect back to the home page
        return redirect('/')
    
# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)  # Start the app in debug mode, which provides error details during development

import sqlite3

# Connect to the database
conn = sqlite3.connect('pdf_text.db')
cursor = conn.cursor()

# Function to fetch top 200 records of text
def peek_top_texts(limit=200):
    cursor.execute("SELECT page_number, paragraph_number, text, continues FROM pdf_text LIMIT ?", (limit,))
    records = cursor.fetchall()
    
    i = 0
    while i < len(records):
        record = records[i]
        print(f"Page: {record[0]}, Paragraph: {record[1]}, Text: {record[2]}")
        if record[3] == 1:
            if i + 1 < len(records):
                next_record = records[i + 1]
                print(f"Continued on Page: {next_record[0]}, Paragraph: {next_record[1]}, Text: {next_record[2]}")
            else:
                print("Continues but next record not available")
        i += 1

# Fetch and display top 200 records
peek_top_texts()

# Close the connection
conn.close()

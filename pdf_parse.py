import sqlite3
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import re
import time

# Open the PDF file
pdf_document = "2025_MandateForLeadership_FULL.pdf"  # Update with your actual file path

# Connect to SQLite database (or create it)
conn = sqlite3.connect('pdf_text.db')
cursor = conn.cursor()

# Drop the existing table if it exists
cursor.execute('DROP TABLE IF EXISTS pdf_text')

# Create a table to store the text by page and paragraph
cursor.execute('''
    CREATE TABLE pdf_text (
        page_number INTEGER,
        paragraph_number INTEGER,
        text TEXT,
        continues INTEGER,
        PRIMARY KEY (page_number, paragraph_number)
    )
''')

# Function to split text into paragraphs more effectively
def split_into_paragraphs(text):
    paragraphs = []
    temp_paragraph = []
    
    for line in text.split('\n'):
        stripped_line = line.strip()
        if stripped_line:
            temp_paragraph.append(stripped_line)
            if stripped_line.endswith('.') or stripped_line.endswith('...'):
                paragraphs.append(' '.join(temp_paragraph))
                temp_paragraph = []
        else:
            if temp_paragraph:
                paragraphs.append(' '.join(temp_paragraph))
                temp_paragraph = []
    if temp_paragraph:
        paragraphs.append(' '.join(temp_paragraph))
    return paragraphs

# Function to detect and remove headers and footers
def is_header_or_footer(line):
    # Check for common patterns in headers/footers
    if re.match(r'^—\s?[ivxlcdm]+\s?—$', line, re.IGNORECASE):  # Roman numerals
        return True
    if re.match(r'^Page \d+$', line):  # Page number
        return True
    if any(keyword in line.lower() for keyword in ['authors', 'mandate for leadership', 'table of contents', 'acknowledgments']):
        return True
    return False

# Extract text from each page, split into paragraphs, and insert into the database
with open(pdf_document, 'rb') as f:
    pages = list(PDFPage.get_pages(f))
    total_pages = len(pages)
    
    for page_num, page in enumerate(pages, start=1):
        start_time = time.time()
        text = extract_text(pdf_document, page_numbers=[page_num-1], laparams=LAParams())
        lines = text.split('\n')
        filtered_lines = [line for line in lines if not is_header_or_footer(line.strip())]
        filtered_text = '\n'.join(filtered_lines)
        paragraphs = split_into_paragraphs(filtered_text)
        
        for para_num, para_text in enumerate(paragraphs):
            # Determine if the paragraph continues to the next page
            continues = 0
            if para_num == len(paragraphs) - 1 and not para_text.endswith(('.', '...')):
                continues = 1

            cursor.execute("INSERT OR REPLACE INTO pdf_text (page_number, paragraph_number, text, continues) VALUES (?, ?, ?, ?)", (page_num, para_num, para_text, continues))
        
        conn.commit()  # Commit after processing each page
        
        elapsed_time = time.time() - start_time
        percent_complete = (page_num / total_pages) * 100
        print(f"[{page_num} / {total_pages}] Completed in {elapsed_time:.2f} seconds ({percent_complete:.2f}%)")

# Close the connection
conn.close()

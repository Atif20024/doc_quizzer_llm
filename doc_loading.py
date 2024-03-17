import requests
from bs4 import BeautifulSoup

# Use 1: when people want to share a webpage and ask you to generate question from here
    
def get_article_text(url):
    # Fetch the webpage content
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the main article body
    article_body = soup.find('body')

    # Extract text from the body
    article_text = article_body.get_text()

    return article_text


# Use 2. When people want to upload a pdf and ask you to generate question from it
import os
from PyPDF2 import PdfReader

# pdf_directory = os.getcwd()

# # Opening the pdf
# for filename in os.listdir(pdf_directory):
#     if filename.endswith(".pdf"):
#         pdf_file_name = filename
#         pdf_file = open(os.path.join(pdf_directory, filename), "rb")
def read_pdf_text(pdf_file):
    # Reading the pdf
    pdf_reader = PdfReader(pdf_file)
    all_text = ""
    # make it limited. min(5, len(pages))
    for idx, page in enumerate(pdf_reader.pages):
        all_text += page.extract_text()
        if idx > 4:
            break
    return all_text

# print(all_text)

# Use 3. let the user input an story to generate questions from
    
# Use 4. let the use share a video link to generate questions from

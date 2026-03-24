import PyPDF2
import requests
from bs4 import BeautifulSoup
def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text
def scrape_website(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = " ".join(p.get_text() for p in paragraphs)
    return text
def extract_keywords(question):
    stopwords = ["how", "to", "is", "the", "a", "an", "of", "for", "in", "on"]
    words = question.lower().split()
    keywords = [word.strip("?.!,") for word in words if word not in stopwords]
    return keywords
def chatbot_response(question, pdf_text, web_text):
    keywords = extract_keywords(question)
    for line in pdf_text.split("\n"):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords):
            return "ChatBot (From PDF):\n" + line.strip()
    for line in web_text.split("."):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords):
            return "ChatBot (From Website):\n" + line.strip()
    return "Sorry, no relevant instruction found."
pdf_text = read_pdf(r"C:\Users\KIIT0001\OneDrive\Desktop\java code\ch1_v1.pdf")
web_text = scrape_website("https://aayushbansal.com/") 
print("Chatbot is ready. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = chatbot_response(user_input, pdf_text, web_text)
    print("Bot:", response)

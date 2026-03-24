import os
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
os.environ["GOOGLE_API_KEY"] = "AIzaSyA7W3FfsgvdUAnBufLGA62EsI8jAYqoQQ8"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])
    return text
def read_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text
def ai_answer(question, manual_text, web_text):
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    You are an assistant.
    Use ONLY the following text to answer the question.
    If the answer is not present in the text, say:
    "This information is not available."
    PDF Text:
    {manual_text}
    Online Text:
    {web_text}
    Question:
    {question}
    Answer clearly in simple steps.
    """
    response = model.generate_content(prompt)
    return response.text.strip()
web_text = scrape_website("https://aayushbansal.com/")
manual_text = read_pdf(r"C:\Users\KIIT0001\OneDrive\Desktop\java code\ch1_v1.pdf")
print("Help Bot is ready.")
print("Type 'exit' to quit.\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Bot: Goodbye!")
        break
    reply = ai_answer(user_input, manual_text, web_text)
    print("\nBot:", reply, "\n")

import logging
import logging.handlers
import os

import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
import ssl
import smtplib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    SOME_SECRET = os.environ["SOME_SECRET"]
except KeyError:
    SOME_SECRET = "Token not available!"
    #logger.info("Token not available!")
    #raise


def my_function():
    sender_email = "dosiracbot@gmail.com"
    password = "zpps pgdy yrcm vxuo"
    receiver_emails = ["jeremy.lee6857@gmail.com", "emilyliu496@gmail.com"]

    target_url = "https://thesilvercollective.com/products/elyse-drop-earrings-silver?variant=40853239889985" 
    [content, result_str_final, sold_out] = scrape_content(target_url)

    if content:
        with open('output.txt', 'w', encoding="utf-8") as file:
            file.write(content)
        if (sold_out):
            subject = "Sold out"
            body = """
        SOLD OUT 😭   
            """
        else:
            subject = "IN STOCK"
            body = """
        IN STOCK! 🙌  
        Buy here: https://thesilvercollective.com/products/elyse-drop-earrings-silver?variant=40853239889985
            """
        body += f"\n{result_str_final}"
        
        print(body)
        send_email(subject, body, sender_email, receiver_emails, password)
        return 'Sold out' if sold_out else 'In Stock'

    else:
        print("Failed to scrape content.")


def scrape_content(url):
    """Fetches the webpage content and returns it as a string"""
    sold_out = False
    result_str_final = ''
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        select_element = soup.find("select", id="Variants-template--15728468131905__main-product")

        variants=['Silver', 'Gold', 'Rose Gold']
        for idx, option in enumerate(select_element.find_all("option")):
            availability = "In stock"

            # TODO: Change idx here to choose variant
            if "- Sold out" in option.text and idx == 0:
                availability = "Sold out"
                sold_out = True
            result_str = f"{variants[idx]}: {availability}."
            result_str_final += f"{result_str}\n"

        return [soup.prettify(), result_str_final, sold_out] 
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
def send_email(subject, body, sender_email, receiver_emails, password):
    em = EmailMessage()
    em['From'] = sender_email
    em['To'] = ", ".join(receiver_emails)
    em['Subject'] = subject
    em.set_content(body)
    
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(sender_email, password)
        smtp.sendmail(sender_email, receiver_emails, em.as_string())
        print('Email sent')
        


if __name__ == "__main__":
    # logger.info(f"Token value: {SOME_SECRET}")

    stock_status = my_function()
    logger.info(f'Status: {stock_status}')

    # r = requests.get('https://weather.talkpython.fm/api/weather/?city=Berlin&country=DE')
    # if r.status_code == 200:
    #     data = r.json()
    #     temperature = data["forecast"]["temp"]
    #     logger.info(f'Weather in Berlin: {temperature}')

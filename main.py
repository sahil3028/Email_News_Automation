import requests


import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
apiKey = os.getenv("API_KEY")
date="2026 - 03 - 18"



#topic of news
topic = "gym"

url = (
    f"https://newsapi.org/v2/everything?"
    f"q={topic}&"
    f"from={date}&"
    f"sortBy=publishedAt&"
    f"language=en&"
    f"apiKey={apiKey}"
)

response = requests.get(url)
content = response.json()

# Build HTML email body
myArticle = f"""
<h2>📰 Latest {topic.capitalize()} News</h2>
<p>Here is some political news my script fetched for you.\n I didn't make the UI so i cant deploy it but i gave it topic and and your email, idk what it'll send you</p>
<hr>
"""

for article in content['articles'][0:5]:
    myArticle += f"""
    <h3>{article['title']}</h3>
    <p>{article.get('description', 'No description available.')}</p>
    <a href="{article['url']}">Read full article</a>
    <hr>
    """


#email send
def send_email(message_html):
    host = "smtp.gmail.com"
    port = 465

    #reciver
    receiver = "sahil12345rock.com"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🗞️ Your Daily News Digest"
    msg["From"] = username
    msg["To"] = receiver

    msg.attach(MIMEText(message_html, "html"))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, msg.as_string())


send_email(myArticle)
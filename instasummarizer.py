# Created by Minal

import json
import logging
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
import logging

logging.basicConfig(level=logging.INFO)
nltk.download('punkt_tab')
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

INSTAGRAM_URL = "https://www.instagram.com/{}/"
USERNAME = "bbcnews"
# url = INSTAGRAM_URL.format(username)


def get_instagram_post(username):
    try:
        url = INSTAGRAM_URL.format(username)
        options = Options()
        options.add_argument("--headless")  
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(5)  

        soup = BeautifulSoup(driver.page_source, "html.parser")

        post_links = soup.find_all("a", href=True)
        post_url = None

        for link in post_links:
            if "/p/" in link["href"]:  
                post_url = "https://www.instagram.com" + link["href"]
                break

        if not post_url:
            driver.quit()
            return {"error": "No posts found"}

        driver.get(post_url)
        time.sleep(5)  
        soup = BeautifulSoup(driver.page_source, "html.parser")

        caption_div = soup.find("h1") 
        if caption_div:
            caption = caption_div.text.strip()
            driver.quit()
            return {"caption": caption}

        driver.quit()
        return {"error": "Caption not found"}

    except Exception as e:
        logging.error(f"Error fetching Instagram post: {e}")
        return {"error": "Exception occurred"}
    
username = "bbcnews"
print(get_instagram_post(username))


def summarize_caption(caption):
    try:
        print(f"Original caption: {caption}")
        tokens = word_tokenize(caption) 
        print(f"Tokens: {tokens}")
        return ' '.join(tokens[:10]) 
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return "Error in summarization"

TWEETS_FILE = "tweets.json"

def post_to_twitter(text):
    try:
        tweet_data = {"tweet": text}
        with open(TWEETS_FILE, "a") as file:
            json.dump(tweet_data, file)
            file.write("\n")
        return {"status": "Success", "tweet": text}
    except Exception as e:
        logging.error(f"Error saving tweet: {e}")
        return {"error": "Failed to save tweet"}

@app.route("/fetch-instagram", methods=["GET"])
def fetch_instagram():
    data = get_instagram_post(USERNAME)
    return jsonify(data)

@app.route("/post-tweet", methods=["POST"])
def post_tweet():
    caption = request.json.get("caption")
    summary = summarize_caption(caption)
    response = post_to_twitter(summary)
    return jsonify(response)

url = INSTAGRAM_URL.format(username)
logging.info(f"Driver initialized and fetching: {url}")



if __name__ == "__main__":
    app.run(debug=True)
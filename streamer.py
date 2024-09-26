from typing import AsyncGenerator
from fastapi import Request, Response
import requests
from bs4 import BeautifulSoup
import spacy
from cache import Cache
import json

#simulate streaming source to fetch
documents = ['https://en.wikipedia.org/wiki/Artificial_intelligence', 'https://bigsur.ai/', 'https://en.wikipedia.org/wiki/LinkedIn', 'https://en.wikipedia.org/wiki/LeetCode', 'https://en.wikipedia.org/wiki/FastAPI']

class Streamer:
    cache = None
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.cache = Cache()


    def fetch_webpage(self, url: str) -> str:
        """
        Fetch the HTML content of the webpage.
        """
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to retrieve content from {url}, status code: {response.status_code}")

    def parse_html(self, html_content: str) -> str:
        """
        Parse the HTML content and extract plain text.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        # Get text and strip leading/trailing whitespaces
        text = soup.get_text(separator=" ")
        return text.strip()

    def clearCookie(self, response: Response):
        response.delete_cookie(key="session_id")
        response.delete_cookie(key="url_id")
        response.delete_cookie(key="offset")

    def setCookie(self, response: Response, session_id: str = "", urlId: int = 0, offset: int = 0):
        response.set_cookie(key="session_id", value=session_id)
        response.set_cookie(key="url_id", value=urlId)
        response.set_cookie(key="offset", value=max(0, offset - 1))

    async def start_stream(self, response: Response, urlId: int = 0, offset: int = 0, session_id: str = "") -> AsyncGenerator[str, None]:
        """
        A simple async generator that streams text.
        In a real-world scenario, this could be pulling data from a message queue or external service.
        """
        url = documents[urlId]
        sents = []
        has_cache = await self.cache.hasKey(url)

        if has_cache == 1:
            # Document in cache
            value = await self.cache.get_url_cache(url)
            sents = json.loads(value.decode('utf-8'))
        else:
            # Document not in cache
            try:
                # Step 1: Fetch the page content
                html_content = self.fetch_webpage(url)
                # Step 2: Parse the HTML and extract text
                text_content = self.parse_html(html_content)
                # Step 3: Tokenize into words and sentences
                doc = self.nlp(text_content)
                sents = [sent.text for sent in doc.sents]
                # step 4: store tokenized doc to cache
                await self.cache.add_url_cache(url, json.dumps(sents))
            except Exception as e:
                print(e)




        try:
            # start streaming data from last offset
            while offset < len(sents) and offset >= 0:
                # await asyncio.sleep(1)  # Simulate delay for streaming
                yield 'Message Offset:' + str(offset) + ' ' + sents[offset] + '\n'
                offset += 1
        except Exception as e:
            print(e)
        finally:
            print("start_stream:: Finally")
            if sents is not None and offset >= len(sents):
                # streaming succeeded, clear cookie
                self.clearCookie(response)
            else:
                # streaming interrupted somewhere in between, store streaming offset to cookie
                self.setCookie(response, session_id, urlId, max(0, offset - 1))


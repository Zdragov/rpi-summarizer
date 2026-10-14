import os
from google import genai

class CloudSummarizer:
    def __init__(self):

        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = "gemini-3.5-flash-lite"

    def summarize(self,text):
        prompt = (
            "Summarize the following text in two simple, clear, concise sentences. Only use information from the provided text. \n\n"f"Text: {text}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text.strip()
# summarizer.py
from llama_cpp import Llama

MODEL_PATH = "gemma-3-270m-it-Q4_K_M.gguf"


class Summarizer:
    def __init__(self, model_path=MODEL_PATH):

        self.llm = Llama(
            model_path=model_path,
            n_ctx=1024,              
            n_threads=3,             
            verbose=False,

            
            temperature=0.9,        
            top_k=40,               
            top_p=0.9,               
            min_p=0.05,                  
            frequency_penalty=0.0,   
            presence_penalty=0.0,    
            max_tokens=80,           
            
            stop=["<end_of_turn>"],  
        )

    def chunkText(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + 900
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start = end - 80
        return chunks

    def summarizeSingle(self, text):
        text = text[:400]

        # Gemma chat template
        prompt = (
            "<start_of_turn>user\n"
            f"Summarize in 2 sentences:\n{text}\n"
            "<end_of_turn>\n"
            "<start_of_turn>model\n"
        )

        result = self.llm(prompt)
        raw = result["choices"][0]["text"].strip()

        if len(raw) > 600:
            raw = raw[:600].rstrip() + "..."

        # restore period
        if raw and not raw.endswith((".", "!", "?")):
            raw += "."

        return raw

    def summarize(self, text):
        if len(text) <= 900:
            return self.summarizeSingle(text)

        chunks = self.chunkText(text)
        partial_summaries = []
        for chunk in chunks:
            summary = self.summarizeSingle(chunk)
            partial_summaries.append(summary)

        combined = " ".join(partial_summaries)
        if len(combined) > 900:
            combined = self.summarizeSingle(combined)
        return combined

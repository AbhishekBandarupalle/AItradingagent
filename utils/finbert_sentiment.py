from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

class FinBertSentiment:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        self.model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
        self.labels = ["negative", "neutral", "positive"]

    def score(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1).numpy()[0]
        return dict(zip(self.labels, probs))

    def aggregate_score(self, headlines):
        if not headlines:
            return {k: 0.0 for k in self.labels}
        scores = [self.score(h) for h in headlines]
        avg = {k: float(np.mean([s[k] for s in scores])) for k in self.labels}
        return avg 
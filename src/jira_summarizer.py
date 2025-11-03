from transformers import pipeline

class JiraStorySummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize(self, text, min_length=30, max_length=130):
        # Adjust max_length if input is very short
        input_length = len(text.split())
        if input_length < max_length:
            max_length = max(10, input_length)  # never less than 10
        summary = self.summarizer(text, min_length=min_length, max_length=max_length)
        return summary[0]['summary_text']

# Example usage:
# summarizer = JiraStorySummarizer()
# summary = summarizer.summarize("Long JIRA story text here...")
# print(summary)

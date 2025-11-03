from transformers import pipeline
import os


class JiraStorySummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn", model_path: str | None = None, device: int = -1):
        """
        model_name: HF model identifier to download if no local model_path provided
        model_path: local directory containing the model (preferred if present)
        device: device id for pipeline (use -1 for CPU)
        """
        # Prefer a local model path if provided and exists
        selected_model = None
        if model_path:
            if os.path.isdir(model_path):
                selected_model = model_path
            else:
                raise ValueError(f"Provided model_path does not exist or is not a directory: {model_path}")

        self.model_source = selected_model or model_name
        # device=-1 (CPU) by default; set device=0 for first GPU if available
        self.summarizer = pipeline("summarization", model=self.model_source, device=device)

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

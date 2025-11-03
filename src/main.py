#!/usr/bin/env python

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QDialog, QHBoxLayout, QLineEdit, QComboBox, QCheckBox)
from PySide6.QtCore import Qt, QSettings
from dotenv import load_dotenv


# Import the summarizer

from jira_summarizer import JiraStorySummarizer
from jira_api import fetch_jira_stories

class CorporateHelper(QMainWindow):
    DEFAULT_PROMPTS = {
        "General Progress": "Analyze the following JIRA stories and provide a concise summary of the overall progress and key developments:",
        "Blockers & Risks": "Review these JIRA stories and identify potential blockers, risks, and challenges that need attention:",
        "Sprint Summary": "Evaluate these JIRA stories and provide a sprint summary including velocity, completion status, and team performance:",
        "Technical Debt": "Analyze these JIRA stories focusing on technical debt, architecture changes, and system improvements:",
        "Custom": "Custom prompt..."
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Corporate Helper")
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Initialize settings
        self.settings = QSettings('CorporateHelper', 'JIRASummarizer')
        self.summary_prompt = self.settings.value(
            'summary_prompt',
            self.DEFAULT_PROMPTS["General Progress"]
        )
        self.selected_template = self.settings.value('selected_template', "General Progress")
        self.show_raw_input = self.settings.value('show_raw_input', False, type=bool)

        # JIRA API key (for future use)
        self.jira_api_key = os.getenv("JIRA_API_KEY", "Not set")

        # Summarizer
        self.summarizer = JiraStorySummarizer()

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        layout.addWidget(self.settings_button)

        # Input for JIRA story text
        self.input_label = QLabel("Paste JIRA Story Text:")
        layout.addWidget(self.input_label)
        self.input_text = QTextEdit()
        layout.addWidget(self.input_text)

        # Summarize button
        self.summarize_button = QPushButton("Summarize Story")
        self.summarize_button.clicked.connect(self.summarize_story)
        layout.addWidget(self.summarize_button)

        # Fetch and summarize JIRA stories button
        self.fetch_jira_button = QPushButton("Fetch & Summarize JIRA Stories")
        self.fetch_jira_button.clicked.connect(self.fetch_and_summarize_jira)
        layout.addWidget(self.fetch_jira_button)

        # Output for summary
        self.output_label = QLabel("Summary:")
        layout.addWidget(self.output_label)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

    def summarize_story(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.output_text.setPlainText("Please paste a JIRA story to summarize.")
            return
        self.output_text.setPlainText("Summarizing, please wait...")
        try:
            summary = self.summarizer.summarize(text)
            self.output_text.setPlainText(summary)
        except Exception as e:
            self.output_text.setPlainText(f"Error: {e}")

    def fetch_and_summarize_jira(self):
        self.output_text.setPlainText("Fetching JIRA stories and summarizing, please wait...")
        try:
            stories = fetch_jira_stories()
            if not stories:
                self.output_text.setPlainText("No JIRA stories found.")
                return

            # Create detailed narrative with all available information
            story_details = []
            for story in stories:
                details = [
                    f"Story: {story['key']} - {story['summary']}",
                    f"Status: {story['status']}",
                    f"Assignee: {story['assignee']}",
                    f"Priority: {story['priority']}",
                    f"Sprint: {story['sprint']}",
                    f"Story Points: {story['story_points']}",
                    f"Last Updated: {story['updated']}",
                    f"Description: {story['description']}\n"
                ]
                story_details.append("\n".join(details))

            # Combine prompt and stories
            narrative = f"{self.summary_prompt}\n\nProject Context:\n" + "\n".join(story_details)

            # Show raw input if enabled
            if self.show_raw_input:
                self.output_text.setPlainText("Raw input being sent to summarizer:\n\n" + narrative + "\n\nGenerating summary...")

            # Generate and show summary
            summary = self.summarizer.summarize(narrative)
            if self.show_raw_input:
                self.output_text.setPlainText(self.output_text.toPlainText() + "\n\nSummary:\n" + summary)
            else:
                self.output_text.setPlainText(summary)
        except Exception as e:
            self.output_text.setPlainText(f"Error: {e}")

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setModal(True)

        layout = QVBoxLayout()

        # Template selection
        template_label = QLabel("Prompt Template:")
        layout.addWidget(template_label)

        template_combo = QComboBox()
        template_combo.addItems(self.DEFAULT_PROMPTS.keys())
        template_combo.setCurrentText(self.selected_template)
        layout.addWidget(template_combo)

        # Prompt input
        prompt_label = QLabel("Summary Prompt:")
        layout.addWidget(prompt_label)

        prompt_input = QTextEdit()
        prompt_input.setPlainText(self.summary_prompt)
        prompt_input.setMinimumHeight(100)
        layout.addWidget(prompt_input)

        # Show raw input checkbox
        show_raw = QCheckBox("Show raw text being sent to summarizer")
        show_raw.setChecked(self.show_raw_input)
        layout.addWidget(show_raw)

        def template_changed(template_name):
            if template_name != "Custom":
                prompt_input.setPlainText(self.DEFAULT_PROMPTS[template_name])

        template_combo.currentTextChanged.connect(template_changed)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")

        def save_settings():
            self.selected_template = template_combo.currentText()
            self.summary_prompt = prompt_input.toPlainText()
            self.show_raw_input = show_raw.isChecked()
            self.settings.setValue('selected_template', self.selected_template)
            self.settings.setValue('summary_prompt', self.summary_prompt)
            self.settings.setValue('show_raw_input', self.show_raw_input)
            dialog.accept()

        save_button.clicked.connect(save_settings)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.resize(400, 200)
        dialog.exec()

def main():
    # Load environment variables from .env file
    load_dotenv()
    app = QApplication(sys.argv)
    window = CorporateHelper()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
"""
Task 5: GenAI Urban Mobility Insights Assistant
Objective: Enable natural-language analytics for decision-makers
"""

# ================================
# CONFIGURATION
# ================================

import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")



class MobilityGenAIAssistant:
    """
    GenAI-powered assistant for urban mobility insights (Groq)
    """

    def __init__(
        self,
        data_path="data/cleaned/cleaned_taxi_data.csv",
        kpi_path="outputs/kpi_report.txt",
        sql_results_dir="outputs/sql_results",
    ):
        self.data_path = Path(data_path)
        self.kpi_path = Path(kpi_path)
        self.sql_results_dir = Path(sql_results_dir)

        self.df = None
        self.kpi_summary = None
        self.sql_results = {}

        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found. Please set it in the .env file.")

        self.client = Groq(api_key=GROQ_API_KEY)
        print("✓ Initialized Groq LLM")

    # -----------------------------
    # CONTEXT LOADING
    # -----------------------------
    def load_context(self):
        print("\nLoading context data...")

        if self.data_path.exists():
            self.df = pd.read_csv(self.data_path, nrows=1000)
            print(f"✓ Loaded data sample ({len(self.df)} rows)")

        if self.kpi_path.exists():
            with open(self.kpi_path, "r") as f:
                self.kpi_summary = f.read()
            print("✓ Loaded KPI summary")

        if self.sql_results_dir.exists():
            for file in self.sql_results_dir.glob("*.csv"):
                self.sql_results[file.stem] = pd.read_csv(file).to_dict("records")
            print(f"✓ Loaded {len(self.sql_results)} SQL result sets")

    # -----------------------------
    # CONTEXT BUILDERS
    # -----------------------------
    def _get_data_summary(self):
        if self.df is None:
            return "No data available"

        return f"""
Data Summary:
- Total records in sample: {len(self.df):,}
- Date range: {self.df['tpep_pickup_datetime'].min()} to {self.df['tpep_pickup_datetime'].max()}
- Average fare: ${self.df['fare_amount'].mean():.2f}
- Average distance: {self.df['trip_distance'].mean():.2f} miles
- Average trip duration: {self.df['trip_duration_minutes'].mean():.2f} minutes
"""

    def _get_kpi_context(self):
        return self.kpi_summary or "KPI data not available"

    def _get_sql_context(self):
        if not self.sql_results:
            return "SQL results not available"

        summary = "Available SQL Results:\n"
        for key, results in self.sql_results.items():
            summary += f"- {key}: {len(results)} rows\n"
        return summary

    # -----------------------------
    # CORE Q&A
    # -----------------------------
    def answer_question(self, question):
        print(f"\nQuestion: {question}")
        print("Generating answer...")

        prompt = f"""
You are an expert urban mobility analytics assistant.

Context:
{self._get_data_summary()}

KPI Summary:
{self._get_kpi_context()}

SQL Analytics:
{self._get_sql_context()}

User Question:
{question}

Instructions:
- Answer using data-driven insights
- Include metrics when relevant
- Be concise and professional
"""

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            answer = response.choices[0].message.content
            print(f"\nAnswer:\n{answer}\n")
            return answer

        except Exception as e:
            print(f"✗ Error generating answer: {e}")
            return str(e)

    # -----------------------------
    # INTERACTIVE MODE
    # -----------------------------
    def interactive_mode(self):
        print("\n" + "=" * 70)
        print("GenAI Mobility Insights Assistant (Groq)")
        print("=" * 70)
        print("Type 'exit' to quit.")
        print("=" * 70)

        while True:
            try:
                q = input("\nYour question: ").strip()
                if q.lower() == "exit":
                    print("Goodbye!")
                    break
                elif q:
                    self.answer_question(q)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


def main():
    print("=" * 70)
    print("TASK 5: GenAI Urban Mobility Insights Assistant (Groq)")
    print("=" * 70)

    assistant = MobilityGenAIAssistant()
    assistant.load_context()

    test_questions = [
        "What were the busiest pickup zones?",
        "When is surge demand highest?",
        "What are the peak hours for trips?",
        "How does weekend demand compare to weekdays?",
    ]

    for q in test_questions:
        assistant.answer_question(q)
        print("-" * 70)

    assistant.interactive_mode()


if __name__ == "__main__":
    main()
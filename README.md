# Coding Bootcamp Builder

A multi-agent AI system powered by CrewAI and OpenAI to generate personalized, week-by-week coding bootcamps tailored to a learner's skill level, stack, and goals.

## Project Structure

```
coding-bootcamp-builder/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── assessor.py
│   │   ├── researcher.py
│   │   ├── curriculum_builder.py
│   │   └── reviewer.py
│   ├── main.py
│   └── app.py
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Setup & Running

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env`:
   ```bash
   cp .env.example .env
   # Add your OpenAI API key
   ```
3. Test pipeline:
   ```bash
   python src/main.py
   ```
4. Run Streamlit UI:
   ```bash
   streamlit run src/app.py
   ```

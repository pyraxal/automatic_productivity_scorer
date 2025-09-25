A program that automates extraction, cleaning, analysis, and scoring of sentence productivity. This tool is designed to process `.cha` and `.txt` transcript files, extract [+rr] utterances, and compute productivity metrics.


--------------------------------------------------

# 📚 Table of Contents


- Prerequisites
- Setup
- Running the Pipeline
- Command-Line Interface
- Python Interface
- Project Structure

--------------------------------------------------

# 🧾 Prerequisites

- Python 3.10+
- stanza NLP library (`pip install stanza`)
- ffmpeg if processing audio transcripts in future
- Optional: GPU for faster NLP processing 


--------------------------------------------------

# ⚙️ Setup

Create a virtual enviroment of your choice (conda/venv), then clone repository:

    git clone https://github.com/pyraxal/automatic_productivity_scorer
    cd automatic_productivity_scorer
    pip install -r requirements.txt

Stanza models are automatically downloaded when first running analysis.

--------------------------------------------------

# 🛠 Running the Pipeline


### Command-Line Interface (CLI)

Drop your `.cha` or `.txt` transcript files in the `input/` folder next to `main.py`. Then run:

    python main.py

- Processed CSVs are saved in `output/`
- Original files are moved to `done/`
- You can also specify a single file or folder:
    python main.py -p input/myfile.cha
    python main.py -p input_folder/

### Python Interactive Interface

You can also call the analysis pipeline from Python:

    from interface import run_full_pipeline

    with open("input/sample.cha", "r", encoding="utf-8") as f:
        text = f.read()

    output_csv = "output/sample_results.csv"
    run_full_pipeline(text, output_csv)


--------------------------------------------------

# 📁 Project Structure


    ├── main.py                 # Command-line script
    ├── interface.py            # Python interface to run full pipeline
    ├── extract_clean.py        # Extracts [+rr] utterances and cleans text
    ├── analyze.py              # NLP analysis for articles, auxiliaries, and progressive forms
    ├── score.py                # Scoring and CSV output
    ├── input/                  # Place raw transcript files here
        ├── something.cha  
    ├── output/                 # CSV results are saved here
        ├── something.csv 
    ├── processed/              # Processed files are moved here
        ├── something.cha 
    └── README.txt

--------------------------------------------------

# ⚠️ Notes / WIP

- Currently focused on English transcripts
- Scoring metrics and technical definitions are a work in progress with SLP collaboration.
- Future updates will integrate api access + restructure of cs
- Better comments and documentation (speed release/prototype for testing, finalization later)

from extract_clean import extract_rr_lines, clean_for_scoring
from analyze import analyze_utterances
from score import write_analysis_to_csv

#skeleton for API in the future

def run_full_pipeline(text, output_csv_path=None):
    rr_text = extract_rr_lines(text)
    utterances = rr_text.strip().split("\n")
    results = analyze_utterances(utterances)
    if output_csv_path:
        write_analysis_to_csv(results, output_csv_path)
    return results

def get_extracted_clean(text):
    rr_text = extract_rr_lines(text)
    return [clean_for_scoring(u) for u in rr_text.strip().split("\n") if u.strip()]

def analyze_only(utterances):
    return analyze_utterances(utterances)

def score_only(results, output_csv_path):
    write_analysis_to_csv(results, output_csv_path)
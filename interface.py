from extract_clean import extract_rr_lines, clean_for_scoring
from score import write_analysis_to_csv, write_ads_csv
from analyze import analyze_utterances, is_ads_result



def run_full_pipeline(text, output_csv_path=None, extract_rr=False):
    if extract_rr:
        rr_text = extract_rr_lines(text)
    else:
        rr_text = text

    utterances = rr_text.strip().split("\n")
    results = analyze_utterances(utterances)

    if output_csv_path:
        write_analysis_to_csv(results, output_csv_path)

    return results

def run_ads_only_pipeline(text, output_csv_path=None, extract_rr=False):
    if extract_rr:
        rr_text = extract_rr_lines(text)
    else:
        rr_text = text

    utterances = rr_text.strip().split("\n")

    # IMPORTANT: we want 0/1 per utterance, not filtered only
    results = analyze_utterances(utterances)

    for r in results:
        r["is_ads"] = is_ads_result(r)

    if output_csv_path:
        write_ads_csv(results, output_csv_path)

    return results

def get_extracted_clean(text):
    rr_text = extract_rr_lines(text)
    return [
        clean_for_scoring(u)
        for u in rr_text.strip().split("\n")
        if u.strip()
    ]

def analyze_only(utterances):
    return analyze_utterances(utterances)

def score_only(results, output_csv_path):
    write_analysis_to_csv(results, output_csv_path)
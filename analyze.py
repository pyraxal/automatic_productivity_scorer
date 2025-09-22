import stanza
from extract_clean import clean_for_scoring
import re

def analyze_utterances(utterances, require_rr_code=False):
    stanza.download('en', logging_level='ERROR') 
    nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse', logging_level='ERROR')
    
    ARTICLES = {"a", "an", "the"}
    CONTRACTION_FORMS = {"'s", "’s"}
    EXCLUDE_SUBJECTS = {"that", "it", "he", "she", "they", "this", "those"}
    QUESTION_STARTERS = {"when", "what", "where", "who", "whom", "whose", "why", "which", "how"}

    per_utt_results = []
    seen_article_contexts           = set()
    seen_aux_contexts               = set()
    seen_progressive_lemmas         = set()
    seen_active_progressive_lemmas  = set()

    for utt in utterances:
        if require_rr_code and "[+rr]" not in utt.lower():
            continue

        raw = utt.strip()

        # apply both cleanings in sequence
        enni_clean = clean_for_scoring(raw)

        if not enni_clean:
            continue
        
        if "NADS" in enni_clean:
            note = "NADS: non-active declarative structure"
            per_utt_results.append({
                "utterance": raw,
                "cleaned":   enni_clean,
                "art_exists": 0, "art_productive": 0, "art_notes": note,
                "aux_exists": 0, "aux_productive": 0, "aux_notes": note,
                "prog_exists":0, "prog_productive":0, "prog_notes": note,
                "active_prog_exists":0, "active_prog_productive":0, "active_prog_notes": note
            })
            continue

        # lowercase cleaned for check
        tokens = enni_clean.lower().split()
        if (tokens and tokens[0] in QUESTION_STARTERS):
            note = "Question: non-active declarative structure"
            per_utt_results.append({
                "utterance": raw,
                "cleaned":   enni_clean,
                "art_exists": 0, "art_productive": 0, "art_notes": note,
                "aux_exists": 0, "aux_productive": 0, "aux_notes": note,
                "prog_exists":0, "prog_productive":0, "prog_notes": note,
                "active_prog_exists":0, "active_prog_productive":0, "active_prog_notes": note
            })
            continue

        # skip unintelligibles
        if re.search(r"\b[xX]{2,}\b", enni_clean):
            prog_notes = "contains unintelligible words (xxx)"
            per_utt_results.append({
                "utterance": raw,
                "cleaned":   enni_clean,
                "art_exists": 0, "art_productive": 0, "art_notes":"N/A",
                "aux_exists": 0, "aux_productive": 0, "aux_notes":"N/A",
                "prog_exists":0, "prog_productive":0, "prog_notes":prog_notes,
                "active_prog_exists":0, "active_prog_productive":0, "active_prog_notes":prog_notes
            })
            continue

        # init flags/notes
        art_exists = art_productive = aux_exists = aux_productive = 0
        prog_exists = prog_productive = 0
        active_prog_exists = active_prog_productive = 0
        art_notes = aux_notes = prog_notes = active_prog_notes = "N/A"

        doc = nlp(enni_clean)
        has_verb = any(
            w.upos == "VERB" or w.upos == "AUX"
            for sent in doc.sentences
            for w in sent.words
        )
        if not has_verb:
            # e.g. "a penguin" → no VERB/AUX → skip
            per_utt_results.append({
                "utterance": raw,
                "cleaned":   enni_clean,
                "art_exists": 0, "art_productive": 0, "art_notes":"no verb or aux",
                "aux_exists": 0, "aux_productive": 0, "aux_notes":"no verb or aux",
                "prog_exists":0, "prog_productive":0, "prog_notes":"no verb or aux",
                "active_prog_exists":0, "active_prog_productive":0, "active_prog_notes":"no verb or aux"
            })
            continue

        print(enni_clean)
        for sent in doc.sentences:
            # progressive any context
            for w in sent.words:
                xpos       = getattr(w, 'xpos', "") or ""
                feats      = getattr(w, 'feats', "") or ""
                word_text  = w.text.lower()
                lemma = w.lemma.lower()
                vbgse = (xpos=='VBG' or 'VerbForm=Part' in feats) 
                if (vbgse and word_text.endswith("ing") and lemma != "be"):
                    prog_exists = 1
                    if lemma not in seen_progressive_lemmas:
                        seen_progressive_lemmas.add(lemma)
                        prog_productive, prog_notes = 1, f"/ing combined with a new verb ({lemma})"
                    else:
                        prog_notes = f"Lexical verb ({lemma}) is repeated"
                    break

            # subject check for articles, aux, active prog
            subj = None
            has_passive = False
            aux = None
            
            for w in sent.words:
                if w.deprel == "nsubj" and subj is None:
                    subj = w
                elif w.deprel in {"nsubj:pass", "aux:pass"}:
                    has_passive = True
                elif w.deprel == "aux" and aux is None:
                    aux = w

            if not subj or has_passive:
                tokens = sent.words
                for i in range(len(tokens) - 2):
                    w1, w2, w3 = tokens[i], tokens[i+1], tokens[i+2]
                    if (w1.upos == "DET" and
                        w2.upos == "NOUN" and
                        w3.upos == "VERB" and 
                        (w3.xpos == "VBG" or "VerbForm=Part" in (w3.feats or "")) and
                        w3.lemma.lower() != "be"):

                        subj = w2
                        subj_lemma, subj_upos = subj.lemma.lower(), subj.upos

                        active_prog_exists = 1
                        lemma = w3.lemma.lower()
                        if lemma not in seen_active_progressive_lemmas:
                            seen_active_progressive_lemmas.add(lemma)
                            active_prog_productive = 1
                            active_prog_notes = f"Heuristic: DET+NOUN+VBG structure with new verb ({lemma})"
                        else:
                            active_prog_notes = f"Heuristic: DET+NOUN+VBG structure with repeated verb ({lemma})"

                        prog_exists = 1
                        if lemma not in seen_progressive_lemmas:
                            seen_progressive_lemmas.add(lemma)
                            prog_productive = 1
                            prog_notes = f"Heuristic: DET+NOUN+VBG structure with new verb ({lemma})"
                        else:
                            prog_notes = f"Heuristic: DET+NOUN+VBG structure with repeated verb ({lemma})"

                        art_exists = 1
                        det = w1.lemma.lower()
                        ctx = (det, subj_lemma)
                        if ctx not in seen_article_contexts:
                            seen_article_contexts.add(ctx)
                            art_productive = 1
                            art_notes = f"Heuristic: First time {ctx} used"
                        else:
                            art_notes = f"Heuristic: Duplicate article context {ctx}"
                        break  
                
                continue
            
            if aux and aux.id < subj.id:
                continue 

            subj_lemma, subj_upos = subj.lemma.lower(), subj.upos

            # active progressive
            for w in sent.words:
                xpos       = getattr(w, 'xpos', "") or ""
                feats      = getattr(w, 'feats', "") or ""
                word_text  = w.text.lower()
                lemma = w.lemma.lower()
                vbgse = (xpos=='VBG' or 'VerbForm=Part' in feats) 
                if (vbgse and word_text.endswith("ing") and lemma != "be"):
                    active_prog_exists = 1
                    if lemma not in seen_active_progressive_lemmas:
                        seen_active_progressive_lemmas.add(lemma)
                        active_prog_productive = 1
                        active_prog_notes = f"/ing in active declarative with new verb ({lemma})"
                    else:
                        active_prog_notes = f"/ing in active declarative but repeated verb ({lemma})"
                    break

            # article
            for w in sent.words:
                if w.deprel=="det" and w.head==subj.id:
                    art_exists = 1
                    det = w.lemma.lower()
                    if det in ARTICLES:
                        ctx = (det, subj_lemma)
                        if ctx not in seen_article_contexts:
                            seen_article_contexts.add(ctx)
                            art_productive = 1
                            art_notes = f"First time {ctx} used"
                        else:
                            art_notes = f"Duplicate article context {ctx}"
                    break

            # auxiliary
            for w in sent.words:
                if w.lemma.lower() == "be" and w.deprel in {"aux", "cop"}:
                    if w.text.lower() in CONTRACTION_FORMS and subj_upos == "PRON":
                        continue
                    if subj_lemma in EXCLUDE_SUBJECTS:
                        aux_notes = f"Aux on excluded subject ({subj_lemma})"
                        break
                    aux_exists = 1
                    ctx = (w.text.lower(), subj_lemma)
                    if ctx not in seen_aux_contexts:
                        seen_aux_contexts.add(ctx)
                        aux_productive = 1
                        aux_notes = f"New aux context {ctx}"
                    else:
                        aux_notes = f"Duplicate aux context {ctx}"
                    break

        # fallback article
        if art_exists==0:
            t2 = re.sub(r"^\s*and\s+", "", enni_clean, flags=re.IGNORECASE)
            m = re.match(r"^(a|an|the)\s+([A-Za-z]+)", t2, flags=re.IGNORECASE)
            if m:
                art_exists = 1
                det, subj_cand = m.group(1).lower(), m.group(2).lower()
                ctx = (det, subj_cand)
                if ctx not in seen_article_contexts:
                    seen_article_contexts.add(ctx)
                    art_productive=1
                    art_notes = f"First time {ctx} used"
                else:
                    art_notes = f"Duplicate article context {ctx}"

        per_utt_results.append({
            "utterance": raw,
            "cleaned":   enni_clean,
            "art_exists": art_exists,     "art_productive": art_productive,   "art_notes": art_notes,
            "aux_exists": aux_exists,     "aux_productive": aux_productive,   "aux_notes": aux_notes,
            "prog_exists": prog_exists,   "prog_productive": prog_productive, "prog_notes": prog_notes,
            "active_prog_exists": active_prog_exists,
            "active_prog_productive": active_prog_productive,
            "active_prog_notes": active_prog_notes
        })

    return per_utt_results

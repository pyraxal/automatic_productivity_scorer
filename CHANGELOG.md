# Changelog: 1.0
## 1. Verb Compendium Retagger (NEW)

**Where:** Before the copula-exclusion block, immediately after the initial `nlp(enni_clean)` parse.

**What it does:** Iterates every token in the parsed document. If a token ends in `-ing`
but was NOT tagged as VBG/VERB by Stanza, it checks the token's lemma, a naive
suffix-stripped base form, and the raw `-ing` form against an external verb master list
(loaded once from `verb_master_list_path`). If any form matches, the token is retagged
in-place as `VERB / VBG / VerbForm=Part`.

**Guard:** Tokens that Stanza confidently tagged as `NOUN` in a `compound` dependency
relation are skipped to avoid false positives (e.g. "building" in "house building").

**New helper:** `load_verb_master_list(path)` — reads the compendium file into a set;
returns an empty set if the file is not found.

**New parameter:** `verb_master_list_path` added to `analyze_utterances` signature
(default: `"verb_master_list_present.txt"`).

---

## 2. Sole-Verb Utterance Detection (NEW)

**Where:** Computed once per utterance, after the `xxx`-check early-exit, before scoring.

**What it does:** Sets a boolean `is_sole_verb_utterance = True` when the utterance
consists of a bare `-ing` word with no article/pronoun subject present. Two cases:

- The entire content is a single `-ing` token.
- The first content token ends in `-ing` and no subject-like word
  (`a/an/the/he/she/they/it/i/we/you/this/that`) is present anywhere.

**Effect:** Wherever `prog_productive`, `active_prog_productive` would normally be set
to `1`, a `is_sole_verb_utterance` check now prevents productivity from being credited
and instead writes a `"Sole-verb utterance: ..."` note. This applies in six locations:

1. Copula recovery path
2. DET/NOUN/ING fallback
3. Main progressive loop (any context)
4. DET+NOUN+VBG heuristic block
5. Active progressive loop
6. Active progressive inside the heuristic `if not subj or has_passive` branch

Overall is here to prevent false positives where a single -ing verb is given full credit. 
---

## 3. Question Starter Check — Contraction Strip (FIX)

**Where:** The `QUESTION_STARTERS` early-exit check.

**Original:** `tokens[0] in QUESTION_STARTERS`

**New:** Strips any contraction suffix from the first token before comparing:
```python
first_token_base = re.sub(r"'.*$", "", tokens[0]) if tokens else ""
if tokens and first_token_base in QUESTION_STARTERS:
```
Prevents utterances like `"what's in the box"` from slipping through the question filter, since what's =.= what.

---

## 4. Possessive Guard in Copula Recovery (NEW)

**Where:** Inside the copula recovery block, after a VBG-like token is found.

**What it does:** If the token immediately preceding the `-ing` word is a possessive
(`her/his/my/their/our/your/its`), the utterance is treated as a nominal gerund
(e.g. "his cooking") rather than a misparsed progressive, and `exclude_this` is set.
`POSSESSIVES` set added to constants.

---

## 5. Passive Auxiliary Scoring (NEW)

**Where:** In the main `for sent in doc.sentences` loop, immediately before the
`if not subj or has_passive: … continue` block.

**What it does:** When `has_passive` is True and `aux_exists` is still 0, attempts to
find the `nsubj:pass` subject and a `be`-auxiliary (`aux`, `aux:pass`, or `cop`).
If found and the subject is not in `EXCLUDE_SUBJECTS`, credits `aux_exists`/`aux_productive`
with a `"Passive aux: ..."` note. This prevents passive constructions like
"the rabbit is wetted" from losing their auxiliary score. 

---

## 6. `heuristic_fired` Flag in `if not subj or has_passive` Branch (FIX)

**Where:** The `if not subj or has_passive` DET+NOUN+VBG heuristic block.

**Original:** Used a bare `continue` after the inner loop, which would skip the
`continue` at the end of the block regardless of whether the heuristic matched.

**New:** Introduces `heuristic_fired = False` / `heuristic_fired = True`, and replaces
the unconditional skip with `if not heuristic_fired: continue`. This ensures sentences
where the heuristic does NOT fire still fall through to normal subject-based scoring
rather than being silently skipped.

---

## 7. Fallback Article — Stricter Guard on No-Verb Path (CHANGE)

**Where:** The `if not has_verb` early-exit path.

**Original:** The fallback article regex fired for any utterance starting with `a/an/the`.

**New:** Now also requires:
- At least 3 content tokens (`_content_tok_count >= 3`)
- No preposition present (`not _has_prep`, using the new `PREPOSITIONS` set)

This matches the stricter guard already applied in the tracking version and reduces
false-positive article credits on bare noun phrases like "a dog" or "the cat in the hat".

**New constant:** `PREPOSITIONS` set added.

---

## 8. Regex Cleaning Fix (FIX)
Fixed edge cases where 's + -ing would strip much more of the sentence than necessary, removing the necessary context to score a sentence. In addition, added removal for common stop word utterances (uh/um/uhm/etc)

---

## 9. [rr+] Filter Fix (FIX)
Actually gave you the option to add a -rr to the arguments to allow for the user to filter out any sentences without an rr tag. Default is false. 

---

# Changelog: 1.1

## 1. Added ADS-Only Mode (NEW)
- Introduced `-ads` CLI flag to run Active Declarative Sentence scoring independently.
- ADS mode outputs a simplified CSV format:
  - `Utterance, ADS`
  - Each line receives a binary score (1 = ADS, 0 = not ADS).
- ADS classification rules:
  - Any utterance explicitly tagged with `ADS` is automatically scored as 1.
  - Any utterance with productivity = 1 (Article, Auxiliary, Active Progressive, or General Progressive) qualifies as ADS.

---

## 2. ADS-Compatible Compact Support (NEW)
- Compact now detects ADS-format CSVs automatically.
- ADS compact output format:
  - `Name`
  - `Total ADS`
  - `Total Utterances`
  - `ADS Ratio`
- Directory compact mode supports mixing productivity and ADS result files.
- Original productivity compact behavior preserved without modification.

---

## 3. RR Mode Integration in ADS (NEW)
- `--ads-only` fully supports `--extract-rr`.
- ADS scoring can now operate exclusively on RR-tagged lines.
- Behavior mirrors full productivity pipeline logic.

---

## 4. Refactored Compact Detection Logic (IMPROVED)
- Replaced fragile column-based detection with structural detection:
  - ADS files identified by `Utterance,ADS` header.
- Restored original vertical-section productivity parsing.
- Prevented data loss introduced by earlier format changes.

---

## 5. Added Dedicated ADS CSV Writer (NEW)
- Implemented `write_ads_csv()` to isolate ADS output formatting.
- Prevented ADS mode from writing productivity-style sectioned output.

---

## 6. Added analyze_ads_only Entry Point (NEW)
- New wrapper around `analyze_utterances()`.
- Adds `is_ads` boolean per utterance.
- Maintains compatibility with existing analyzer logic.

---

## 7. Maintained Backward Compatibility (STABLE)
- No breaking changes to:
  - `analyze_utterances()`
  - `write_analysis_to_csv()`
  - Productivity compact behavior
- Existing workflows function unchanged.

---

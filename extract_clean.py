import re

def extract_rr_lines(text):
    lines = text.splitlines()

    chi_start = re.compile(r'^\*CHI:\s*(.*)')
    rr_inline = re.compile(r'\[\s*\+\s*rr\s*\]')
    rr_only   = re.compile(r'^\s*\[\s*\+\s*rr\s*\]\s*$')

    extracted = []
    in_chi_block = False
    chi_lines = []

    for line in lines:
        chi_match = chi_start.match(line)
        if chi_match:
            in_chi_block = True
            chi_lines = [chi_match.group(1).strip()]
            if rr_inline.search(line):
                extracted.append(" ".join(chi_lines))
                in_chi_block = False
        elif in_chi_block and (line.startswith(' ') or line.startswith('\t')):
            chi_lines.append(line.strip())
            if rr_inline.search(line):
                extracted.append(" ".join(chi_lines))
                in_chi_block = False
        elif rr_only.match(line):
            if in_chi_block:
                extracted.append(" ".join(chi_lines))
                in_chi_block = False
        else:
            in_chi_block = False
            chi_lines = []

    return "\n".join(extracted)


def clean_for_scoring(text):
    text = re.sub(r"\bisp@x\b", "NADS", text, flags=re.IGNORECASE)
    text = re.sub(r"\b0aux\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"&\+t", "", text, flags=re.IGNORECASE)
    text = re.sub(r"&\+s", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b0p\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[\+\s*rr\]", "", text, flags=re.IGNORECASE)
    text = text.replace("'", "'")
    text = re.sub(r"(\w)[\$@]\w+", r"\1", text)
    text = re.sub(r"<[^>]*>", "", text)

    replacements = dict()
    def extract_and_replace(match):
        word, replacement = match.group(1), match.group(2)
        replacements[word] = replacement
        return word
    text = re.sub(r"\b(\w+)\s*\[\s*:\s*([^\]]+)\]", extract_and_replace, text)

    text = re.sub(r"\[[^\]]*\]", "", text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^\w\s\.\?!']", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    for original, replacement in replacements.items():
        text = re.sub(rf"\b{re.escape(original)}\b", replacement, text)
    
    text = re.sub(r'\..*$', '.', text)
    text = text.rstrip('.')
    
    # Advanced: Expand contractions
    text = re.sub(r"\b([A-Za-z]+)'s\s+([a-zA-Z]+ing)\b", r"\1 is \2", text)
    text = re.sub(r"\bit is\b", "its", text, flags=re.IGNORECASE)

    # Remove all uh/um variants
    text = re.sub(r'\b(uh+|um+)\b[\s,.]*', '', text, flags=re.IGNORECASE).strip()

    # Strip leading coordinator but preserve any article that immediately
    # follows it. Without this, "and [/] the door is closing" would clean to
    # "door is closing" (losing "the") because [/] is stripped first and then
    # the coordinator regex eats "and the " as a unit.
    # Pass 1: coordinator + article → keep just the article
    text = re.sub(
        r"^\s*(and\s+then?|but\s+then?|then|and|but)\s+(a|an|the)\s+",
        r"\2 ",
        text, flags=re.IGNORECASE
    )
    # Pass 2: plain coordinator with no following article → strip normally
    text = re.sub(
        r"^\s*(and\s+then?|but\s+then?|then|and|but)\s+",
        "", text, flags=re.IGNORECASE
    ).strip()
    
    chi_match = re.compile(r'^CHI\s*(.*)').match(text)
    if chi_match:
        text = chi_match.group(1).strip()
        
    return text

"""Lightweight text splitting utilities without spaCy dependency."""
import os
import re
import pandas as pd
from core.utils import rprint, load_key, get_joiner
from core.utils.models import _3_1_SPLIT_BY_NLP

# --------------------
# define the intermediate files
# --------------------
SPLIT_BY_MARK_FILE = "output/log/split_by_mark.txt"
SPLIT_BY_COMMA_FILE = "output/log/split_by_comma.txt"
SPLIT_BY_CONNECTOR_FILE = "output/log/split_by_connector.txt"


def simple_split_by_mark():
    """Split text by sentence-ending punctuation marks."""
    asr_language = load_key("asr.language")
    language = load_key("asr.detected_language") if asr_language == 'auto' else asr_language
    joiner = get_joiner(language)
    rprint(f"[blue]🔍 Using {language} language joiner: '{joiner}'[/blue]")

    chunks = pd.read_excel("output/log/cleaned_chunks.xlsx")
    chunks.text = chunks.text.apply(lambda x: x.strip('"').strip(""))

    input_text = joiner.join(chunks.text.to_list())

    # Sentence ending punctuation patterns
    sentence_endings = r'([。！？.!?])'
    # Split on endings but keep them
    parts = re.split(sentence_endings, input_text)

    sentences = []
    i = 0
    while i < len(parts):
        if parts[i].strip():
            if i + 1 < len(parts) and re.match(sentence_endings, parts[i+1]):
                sentences.append(parts[i].strip() + parts[i+1])
                i += 2
            else:
                sentences.append(parts[i].strip())
                i += 1
        else:
            i += 1

    # Merge lines that are just punctuation
    cleaned_sentences = []
    for sent in sentences:
        stripped = sent.strip()
        if stripped in [',', '.', '，', '。', '？', '！', ';', '；', ':']:
            if cleaned_sentences:
                cleaned_sentences[-1] += stripped
        else:
            cleaned_sentences.append(sent)

    os.makedirs(os.path.dirname(SPLIT_BY_MARK_FILE), exist_ok=True)
    with open(SPLIT_BY_MARK_FILE, "w", encoding="utf-8") as f:
        for sent in cleaned_sentences:
            f.write(sent + "\n")

    rprint(f"[green]💾 Sentences split by punctuation marks saved to →  `{SPLIT_BY_MARK_FILE}`[/green]")


def simple_split_by_comma():
    """Split long sentences by commas if they're long enough."""
    with open(SPLIT_BY_MARK_FILE, "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]

    result = []
    for sent in sentences:
        # Count words (approximate)
        word_count = len(re.findall(r'\w+', sent))

        # If sentence is short, keep as is
        if word_count < 40:
            result.append(sent)
            continue

        # Try to split by comma
        parts = re.split(r'([，,])', sent)
        if len(parts) <= 1:
            result.append(sent)
            continue

        current = ""
        for i in range(0, len(parts), 2):
            part = parts[i]
            punct = parts[i+1] if i+1 < len(parts) else ""

            current_candidate = current + part + punct
            candidate_word_count = len(re.findall(r'\w+', current_candidate))

            if candidate_word_count > 25 and current.strip():
                result.append(current.strip())
                current = part + punct
            else:
                current = current_candidate

        if current.strip():
            result.append(current.strip())

    with open(SPLIT_BY_COMMA_FILE, "w", encoding="utf-8") as f:
        for sent in result:
            f.write(sent + "\n")

    if os.path.exists(SPLIT_BY_MARK_FILE):
        os.remove(SPLIT_BY_MARK_FILE)

    rprint(f"[green]💾 Sentences split by commas saved to →  `{SPLIT_BY_COMMA_FILE}`[/green]")


def simple_split_by_connectors():
    """Just pass through - LLM will handle real splitting."""
    with open(SPLIT_BY_COMMA_FILE, "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]

    with open(SPLIT_BY_CONNECTOR_FILE, "w", encoding="utf-8") as f:
        for sent in sentences:
            f.write(sent + "\n")

    if os.path.exists(SPLIT_BY_COMMA_FILE):
        os.remove(SPLIT_BY_COMMA_FILE)

    rprint(f"[green]💾 Sentences saved to →  `{SPLIT_BY_CONNECTOR_FILE}`[/green]")


def simple_split_long_sentences():
    """Split extremely long sentences by word count."""
    with open(SPLIT_BY_CONNECTOR_FILE, "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]

    asr_language = load_key("asr.language")
    language = load_key("asr.detected_language") if asr_language == 'auto' else asr_language
    joiner = get_joiner(language)

    result = []
    for sent in sentences:
        # Approximate word/token count
        if language in ['zh', 'ja', 'ko']:
            # For CJK, count characters
            count = len(sent)
            max_count = 80
        else:
            # For others, count words
            count = len(re.findall(r'\w+', sent))
            max_count = 60

        if count <= max_count:
            result.append(sent)
            continue

        rprint(f"[yellow]✂️  Splitting long sentence: {sent[:30]}...[/yellow]")

        # Split into roughly equal parts
        if language in ['zh', 'ja', 'ko']:
            # CJK: split by character count
            chars_per_part = max_count - 10
            num_parts = (count + chars_per_part - 1) // chars_per_part
            part_len = count // num_parts

            parts = []
            for i in range(num_parts):
                start = i * part_len
                end = (i + 1) * part_len if i < num_parts - 1 else count
                parts.append(sent[start:end])
            result.extend(parts)
        else:
            # Others: split by words
            words = re.findall(r'\S+', sent)
            words_per_part = max_count // 2
            num_parts = (len(words) + words_per_part - 1) // words_per_part
            part_len = len(words) // num_parts

            parts = []
            for i in range(num_parts):
                start = i * part_len
                end = (i + 1) * part_len if i < num_parts - 1 else len(words)
                parts.append(' '.join(words[start:end]))
            result.extend(parts)

    with open(_3_1_SPLIT_BY_NLP, "w", encoding="utf-8") as f:
        for sent in result:
            f.write(sent + "\n")

    if os.path.exists(SPLIT_BY_CONNECTOR_FILE):
        os.remove(SPLIT_BY_CONNECTOR_FILE)

    rprint(f"[green]💾 Long sentences split saved to →  {_3_1_SPLIT_BY_NLP}[/green]")


def simple_tokenize(text: str) -> list[str]:
    """Lightweight tokenizer using regex."""
    language = load_key("asr.language")
    if language == 'auto':
        language = load_key("asr.detected_language")

    if language in ['zh', 'ja', 'ko']:
        # For CJK, just return individual characters as approximation
        # This is only for counting length anyway
        return list(text.replace(' ', ''))
    else:
        # For others, split on whitespace
        return [w for w in re.split(r'\s+', text) if w]

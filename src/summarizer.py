import os
import re


def summarize_with_openai(text, max_tokens=500):
    try:
        import openai
    except Exception:
        raise RuntimeError("Pakiet `openai` nie jest zainstalowany. Zainstaluj go, aby użyć OpenAI.")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY nie jest ustawiony w środowisku.")
    openai.api_key = api_key
    prompt = (
        "Przeczytaj poniższy tekst artykułu i przygotuj rozbudowane streszczenie. "
        "Najpierw daj streszczenie (kilka akapitów), potem sekcję 'Key points' jako wypunktowaną listę, "
        "a na końcu krótki akapit z wnioskami.\n\nTekst:\n" + text[:15000]
    )
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return resp["choices"][0]["message"]["content"].strip()


def extractive_summarize(text, max_sentences=6):
    """Prosty ekstraktywny algorytm bazujący na częstotliwości słów."""
    # Podział na zdania (prosty)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sentences:
        return ""
    if len(sentences) <= max_sentences:
        return "\n\n".join(sentences)

    words = re.findall(r"\w+", text.lower())
    stopwords = set([
        "the",
        "and",
        "to",
        "of",
        "a",
        "in",
        "is",
        "it",
        "that",
        "for",
        "on",
        "with",
        "as",
        "are",
        "was",
        "by",
        "an",
        "be",
        "this",
        "which",
        "or",
        "from",
        "at",
        "has",
        "have",
    ])
    freq = {}
    for w in words:
        if w in stopwords or len(w) < 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    maxf = max(freq.values()) if freq else 1
    for k in freq:
        freq[k] = freq[k] / maxf

    scores = []
    for i, s in enumerate(sentences):
        s_words = re.findall(r"\w+", s.lower())
        score = sum(freq.get(w, 0) for w in s_words)
        scores.append((score, i, s))

    # wybierz najwyżej punktowane
    import heapq

    top = heapq.nlargest(max_sentences, scores, key=lambda x: x[0])
    # uporządkuj według oryginalnej kolejności
    top_sorted = sorted(top, key=lambda x: x[1])
    summary = " ".join([t[2] for t in top_sorted])
    # punkty kluczowe jako top bez sortowania
    bullets = ["- " + t[2] for t in top]
    conclusions = " ".join([t[2] for t in top[:3]])
    return f"{summary}\n\nKey points:\n" + "\n".join(bullets) + "\n\nConclusions:\n\n" + conclusions


def summarize(text, method="auto", max_sentences=6):
    """Interfejs do streszczania. Jeśli dostępny OPENAI API KEY, domyślnie używa OpenAI."""
    if method == "openai" or (method == "auto" and os.getenv("OPENAI_API_KEY")):
        try:
            return summarize_with_openai(text)
        except Exception as e:
            # fallback
            return extractive_summarize(text, max_sentences=max_sentences)
    else:
        return extractive_summarize(text, max_sentences=max_sentences)

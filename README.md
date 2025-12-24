# ArticleAgent

Narzędzie do pobierania artykułów z sieci, automatycznego streszczania i zapisywania wyników.

Funkcje:
- Pobiera stronę HTML i wyciąga główną treść.
- Tworzy rozbudowane streszczenie i listę kluczowych wniosków.
- Zapisuje wynik jako plik Markdown w katalogu `outputs/`.
- Opcjonalnie tworzy lokalny commit GIT (push wymaga autoryzacji ręcznej lub tokena).

Szybki start

1. Stwórz virtualenv i zainstaluj zależności:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Uruchom CLI:

```
python -m src.cli <URL> [--publish] [--openai]
```

- `--publish` — zapisuje plik i tworzy lokalny commit (komenda `git` musi być dostępna)
- `--openai` — wymusza użycie API OpenAI (wymaga ustawienia `OPENAI_API_KEY` w środowisku)

Format wyjściowy

Pliki są zapisywane w `outputs/` jako `YYYY-MM-DD-slug.md` i zawierają nagłówek z metadanymi, rozbudowane streszczenie oraz listę kluczowych wniosków.

Uwaga prawna

Zanim pobierzesz i opublikujesz treści, upewnij się, że masz prawo do kopiowania i rozpowszechniania artykułu. Agent nie obejmuje automatycznej analizy licencji treści.
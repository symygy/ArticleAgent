import argparse
import os
import datetime
import re
import subprocess
from .fetcher import fetch_article
from .summarizer import summarize


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:120]


def write_output(article, summary, out_dir="outputs"):
    os.makedirs(out_dir, exist_ok=True)
    date = datetime.date.today().isoformat()
    slug = slugify(article.get("title") or article.get("url"))
    filename = f"{date}-{slug}.md"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {article.get('title')}\n\n")
        f.write(f"- Source: {article.get('url')}\n")
        f.write(f"- Date: {date}\n\n")
        f.write("## Summary\n\n")
        f.write(summary + "\n\n")
    return path


def git_commit(path, message=None):
    if message is None:
        message = f"Add summary for {os.path.basename(path)}"
    subprocess.run(["git", "add", path], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)


def main():
    parser = argparse.ArgumentParser(description="ArticleAgent CLI")
    parser.add_argument("url", help="URL artykułu do podsumowania")
    parser.add_argument("--publish", action="store_true", help="Zapisz plik i zrób lokalny commit git (i odbuduj stronę docs)")
    parser.add_argument("--openai", action="store_true", help="Wymuś użycie OpenAI (wymaga OPENAI_API_KEY)")
    parser.add_argument("--sentences", "-n", type=int, default=6, help="Liczba kluczowych zdań w streszczeniu (dla ekstraktywnego)")
    args = parser.parse_args()

    article = fetch_article(args.url)
    method = "openai" if args.openai else "auto"
    summary = summarize(article.get("text", ""), method=method, max_sentences=args.sentences)
    path = write_output(article, summary)
    print("Wygenerowano plik:", path)
    if args.publish:
        try:
            git_commit(path)
            # rebuild docs site
            try:
                subprocess.run(["python3", "scripts/build_site.py"], check=True)
                subprocess.run(["git", "add", "docs"], check=True)
                subprocess.run(["git", "commit", "-m", "chore: rebuild docs site"], check=False)
            except subprocess.CalledProcessError:
                print("Nie udało się odbudować strony docs lokalnie.")
            # push to remote
            try:
                subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
                print("Wypchnięto zmiany na origin/main.")
            except subprocess.CalledProcessError:
                print("Nie udało się wypchnąć zmian. Wykonaj `git push` ręcznie.")
            print("Stworzono lokalny commit.")
        except subprocess.CalledProcessError as e:
            print("Błąd podczas commitu git:", e)


if __name__ == "__main__":
    main()

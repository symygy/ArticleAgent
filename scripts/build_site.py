import os
import glob
import markdown

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title} — ArticleAgent</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <h1><a href="index.html">ArticleAgent</a></h1>
      <p class="tagline">Automated article summaries</p>
    </div>
  </header>
  <main class="container">
  <a class="home" href="index.html">← Home</a>
  <article class="post">
  {content}
  </article>
  </main>
  <footer class="container footer">Generated with ArticleAgent</footer>
</body>
</html>
"""

INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ArticleAgent Summaries</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <h1>ArticleAgent</h1>
      <p class="tagline">Automated article summaries</p>
    </div>
  </header>
  <main class="container">
    <h2>Latest summaries</h2>
    <ul class="posts">
    {items}
    </ul>
  </main>
  <footer class="container footer">Generated with ArticleAgent</footer>
</body>
</html>
"""

CSS = """
:root{--bg:#f7f9fc;--card:#ffffff;--muted:#6b7280;--accent:#0366d6;--text:#0b1220;font-family:Inter,system-ui,Segoe UI,Roboto,'Helvetica Neue',Arial}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);margin:0;padding:0}
.container{max-width:880px;margin:0 auto;padding:2rem}
.site-header{background:transparent;padding:1rem 0}
.site-header h1{margin:0;font-size:1.5rem}
.site-header .tagline{margin:0;color:var(--muted)}
.post{background:var(--card);padding:2rem;border-radius:10px;box-shadow:0 8px 24px rgba(12,20,30,0.06);margin-top:1rem}
.home{display:inline-block;margin-bottom:1rem;color:var(--accent);text-decoration:none}
.post-meta{color:var(--muted);font-size:0.95rem;margin-bottom:1rem}
.posts{list-style:none;padding:0;margin:0}
.posts li{background:var(--card);padding:1rem;border-radius:8px;margin:0 0 1rem 0;box-shadow:0 6px 16px rgba(12,20,30,0.04)}
.posts li a.title{font-weight:600;color:var(--accent);text-decoration:none}
.posts li .meta{color:var(--muted);font-size:0.9rem;margin-top:0.5rem}
.footer{color:var(--muted);font-size:0.9rem;padding:2rem 0}
@media (max-width:600px){.container{padding:1rem}}
"""


def parse_post(md_text):
    """Extract title, source, date and content from the markdown format used by outputs."""
    lines = md_text.splitlines()
    title = None
    source = None
    date = None
    content_lines = []
    i = 0
    # Title
    if i < len(lines) and lines[i].startswith('# '):
        title = lines[i][2:].strip()
        i += 1
    # Read metadata lines like - Source: ...
    while i < len(lines) and lines[i].startswith('- '):
        line = lines[i][2:]
        if line.lower().startswith('source:'):
            source = line[len('source:'):].strip()
        elif line.lower().startswith('date:'):
            date = line[len('date:'):].strip()
        i += 1
    # Skip blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    # Remainder is content
    content_lines = lines[i:]
    content_md = '\n'.join(content_lines)
    # excerpt: first paragraph
    excerpt = ''
    for part in content_md.split('\n\n'):
        p = part.strip()
        if p:
            excerpt = p
            break
    # strip markdown headings if present
    excerpt = excerpt.replace('\n', ' ')
    return {'title': title or 'Untitled', 'source': source or '', 'date': date or '', 'content_md': content_md, 'excerpt': excerpt}


def build_site(outputs_dir='outputs', docs_dir='docs'):
    os.makedirs(docs_dir, exist_ok=True)
    posts = []
    # Collect markdown files and sort by modification time (newest first)
    paths = glob.glob(os.path.join(outputs_dir, '*.md'))
    paths_with_mtime = []
    for p in paths:
        try:
            mtime = os.path.getmtime(p)
        except OSError:
            mtime = 0
        paths_with_mtime.append((p, mtime))
    paths_sorted = [p for p, _ in sorted(paths_with_mtime, key=lambda x: x[1], reverse=True)]

    for path in paths_sorted:
        name = os.path.basename(path)
        with open(path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        parsed = parse_post(md_text)
        html_content = markdown.markdown(parsed['content_md'], extensions=['fenced_code', 'tables'])
        post_html = f"<h1>{parsed['title']}</h1>\n<p class='post-meta'>Source: <a href=\"{parsed['source']}\">{parsed['source']}</a> — {parsed['date']}</p>\n" + html_content
        out_name = name.replace('.md', '.html')
        out_path = os.path.join(docs_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(TEMPLATE.format(title=parsed['title'], content=post_html))
        posts.append({'title': parsed['title'], 'date': parsed['date'], 'src': out_name, 'source': parsed['source'], 'excerpt': parsed['excerpt']})
    # write index (posts are already newest-first)
    items = []
    for p in posts:
        source_link = f"<a href=\"{p['source']}\">source</a>" if p['source'] else 'source'
        items.append(f"<li><a class=\"title\" href=\"{p['src']}\">{p['title']}</a><div class=\"meta\">{p['date']} — {source_link}</div><p>{p['excerpt']}</p></li>")
    index_html = INDEX_TEMPLATE.format(items='\n'.join(items))
    with open(os.path.join(docs_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    # write css
    with open(os.path.join(docs_dir, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(CSS)
    print('Built site to', docs_dir)


if __name__ == '__main__':
    build_site()

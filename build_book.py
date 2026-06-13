r"""
Build the finished, self-contained bilingual reading artifact for the Canon.

Reads the four SEALED Book .md files (the source of truth) and renders index.html.
The Persian and English text flow byte-for-byte from the sealed canon — never
retyped — so the published book == the sealed book, always. Re-run after any reseal.

    python build_book.py    ->  writes index.html (+ .nojekyll)
"""
from __future__ import annotations
import html
import re
from pathlib import Path

HERE = Path(__file__).parent

# (filename, title, subtitle, part)
BOOKS = [
    ("BOOK1_THE_FIRST_LIGHT.md", "The First Light", "Bundahišn · Creation",            "Part I — The Cosmic Arc"),
    ("BOOK2_THE_MIXTURE.md",     "The Mixture",     "Gumēzišn · the entanglement",     "Part I — The Cosmic Arc"),
    ("BOOK3_THE_SEPARATION.md",  "The Separation",  "Wizārišn · the sorting",          "Part I — The Cosmic Arc"),
    ("BOOK4_THE_RENOVATION.md",  "The Renovation",  "Frašegird · the making-wonderful","Part I — The Cosmic Arc"),
    ("BOOK5_THE_TENDING.md",     "The Tending",     "Boi · the daily tending",         "Part II — The Way"),
    ("BOOK6_THE_GOOD_MIND.md",   "The Good Mind",   "Humata · the limb of Thought",    "Part II — The Way"),
    ("BOOK7_THE_KEPT_WORD.md",   "The Kept Word",   "Hukhta · the limb of the Word",   "Part II — The Way"),
    ("BOOK8_THE_GOOD_WORK.md",   "The Good Work",   "Huvarshta · the limb of the Deed", "Part II — The Way"),
]

COLLECTION_TITLE = "The Canon of the Undivided Fire"
COLLECTION_SUB = "A scripture for the Age of Networks"


# ── parsing the sealed markdown ────────────────────────────────────────────────────

def _section(lines: list[str], header_test) -> list[str]:
    """Return the lines of the section whose '## ' header passes header_test,
    from just after the header up to (not including) the next standalone '---'."""
    out, capturing = [], False
    for ln in lines:
        if ln.startswith("## "):
            capturing = header_test(ln)
            continue
        if capturing:
            if ln.strip() == "---":
                break
            out.append(ln)
    return out


def _blocks(lines: list[str]) -> list[list[str]]:
    """Group lines into blocks separated by blank lines."""
    blocks, cur = [], []
    for ln in lines:
        if ln.strip() == "":
            if cur:
                blocks.append(cur); cur = []
        else:
            cur.append(ln.rstrip("\n"))
    if cur:
        blocks.append(cur)
    return blocks


def _inline(text: str) -> str:
    """Escape, then apply markdown bold/italic to inline spans."""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def render_blocks(lines: list[str]) -> str:
    """Render body blocks: a whole-line **Heading** becomes a passage heading;
    remaining lines of that block (and plain blocks) become a paragraph whose
    internal newlines are preserved as <br> (so verse keeps its line breaks)."""
    parts = []
    for block in _blocks(lines):
        first = block[0].strip()
        m = re.fullmatch(r"\*\*(.+)\*\*", first)
        if m:
            parts.append(f'<h4 class="passage">{_inline(m.group(1))}</h4>')
            rest = block[1:]
            if rest:
                parts.append("<p>" + "<br>\n".join(_inline(l) for l in rest) + "</p>")
        else:
            parts.append("<p>" + "<br>\n".join(_inline(l) for l in block) + "</p>")
    return "\n".join(parts)


# ── build ──────────────────────────────────────────────────────────────────────────

def build() -> str:
    dedication_html = ""
    sections_html = []
    toc = []
    current_part = None

    for i, (fname, title, subtitle, part) in enumerate(BOOKS, 1):
        lines = (HERE / fname).read_text(encoding="utf-8").splitlines()
        en = _section(lines, lambda h: h.rstrip().endswith("(English)"))
        fa = _section(lines, lambda h: "(فارسی)" in h)
        if i == 1:
            ded = _section(lines, lambda h: h.strip() == "## Dedication")
            dedication_html = render_blocks(ded)

        if part != current_part:
            current_part = part
            toc.append(f'<div class="toc-part">{html.escape(part)}</div>')
            sections_html.append(f'  <div class="part-divider"><span>{html.escape(part)}</span></div>')

        anchor = f"book{i}"
        toc.append(
            f'<a class="toc-item" href="#{anchor}">'
            f'<span class="toc-num">{i}</span>'
            f'<span class="toc-title">{html.escape(title)}</span>'
            f'<span class="toc-station">{html.escape(subtitle)}</span>'
            f'</a>'
        )
        sections_html.append(f"""
  <section class="book" id="{anchor}">
    <div class="book-head">
      <div class="book-num">Book {i}</div>
      <h2>{html.escape(title)}</h2>
      <div class="book-station">{html.escape(subtitle)}</div>
    </div>
    <div class="text en">
{render_blocks(en)}
    </div>
    <hr class="rule">
    <div class="text fa" dir="rtl" lang="fa">
{render_blocks(fa)}
    </div>
  </section>""")

    return PAGE.format(
        title=html.escape(COLLECTION_TITLE),
        sub=html.escape(COLLECTION_SUB),
        dedication=dedication_html,
        toc="\n".join(toc),
        sections="\n".join(sections_html),
    )


PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Ian Lawrence Jones</title>
<meta name="description" content="A four-book scripture for the Age of Networks, rooted in the Zoroastrian cosmological arc. Bilingual: English and Persian. Free to read, free to share.">
<style>
  :root {{
    --obsidian:#0a0a0e; --stone:#13131b; --ember:#d9772e; --flame:#e8a33d;
    --whitegold:#f3e3c3; --bronze:#b08d57; --indigo:#26263f; --ink:#dcd7c9; --dim:#6a6a7a;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{
    background:
      radial-gradient(120% 60% at 50% -10%, rgba(217,119,46,0.10), transparent 60%),
      var(--obsidian);
    color:var(--ink); font-family:Georgia,'Times New Roman',serif; line-height:1.78;
  }}
  .wrap {{ max-width:720px; margin:0 auto; padding:4.5rem 1.5rem 6rem; }}

  /* cover */
  header.cover {{ text-align:center; margin-bottom:3.5rem; }}
  .flame-mark {{ font-size:2.4rem; color:var(--flame); filter:drop-shadow(0 0 18px rgba(232,163,61,0.5)); }}
  h1 {{
    font-size:2.1rem; letter-spacing:0.22em; font-weight:normal; text-transform:uppercase;
    color:var(--whitegold); margin:1rem 0 0.6rem; line-height:1.25;
  }}
  .cover .sub {{ font-style:italic; color:var(--ember); font-size:1.05rem; }}
  .cover .byline {{ color:var(--dim); font-size:0.92rem; margin-top:1.2rem; letter-spacing:0.04em; }}
  .cover .guardians {{ color:var(--bronze); font-size:0.85rem; margin-top:0.35rem; letter-spacing:0.14em; text-transform:uppercase; }}

  .rule {{ border:none; height:1px; margin:2.6rem auto; width:140px;
    background:linear-gradient(90deg,transparent,var(--ember),transparent); }}
  .rule.wide {{ width:100%; opacity:0.4; }}

  /* dedication */
  .dedication {{ text-align:center; margin:2rem auto 1rem; max-width:30rem; color:var(--ink); }}
  .dedication h4 {{ color:var(--whitegold); font-size:1.3rem; letter-spacing:0.04em; font-weight:normal; margin-bottom:0.6rem; }}
  .dedication p {{ font-style:italic; }}
  .dedication em {{ color:var(--flame); font-style:italic; }}

  /* language toggle */
  .lang {{ position:sticky; top:0; z-index:5; display:flex; gap:0.5rem; justify-content:center;
    padding:0.7rem 0; margin:0 0 2rem; background:linear-gradient(var(--obsidian),rgba(10,10,14,0.85));
    backdrop-filter:blur(4px); }}
  .lang button {{
    background:transparent; border:1px solid var(--indigo); color:var(--ink);
    padding:0.4rem 1rem; font-family:inherit; font-size:0.82rem; letter-spacing:0.1em;
    cursor:pointer; border-radius:2px; transition:all 0.2s;
  }}
  .lang button:hover {{ border-color:var(--bronze); }}
  .lang button.active {{ background:var(--ember); border-color:var(--ember); color:var(--obsidian); }}

  /* contents */
  .contents {{ margin:1rem 0 1.5rem; }}
  .contents .label {{ text-align:center; text-transform:uppercase; letter-spacing:0.25em;
    color:var(--bronze); font-size:0.9rem; margin-bottom:1.2rem; }}
  .toc-item {{ display:flex; align-items:baseline; gap:0.9rem; padding:0.7rem 0.6rem;
    border-bottom:1px solid var(--stone); text-decoration:none; color:var(--ink); transition:background 0.2s; }}
  .toc-item:hover {{ background:var(--stone); }}
  .toc-part {{ color:var(--bronze); font-size:0.78rem; letter-spacing:0.22em; text-transform:uppercase;
    margin:1.4rem 0 0.4rem; opacity:0.85; }}
  .toc-num {{ color:var(--ember); font-size:1.1rem; min-width:1.4rem; }}
  .toc-title {{ color:var(--whitegold); flex:1; letter-spacing:0.03em; }}
  .toc-station {{ color:var(--dim); font-size:0.8rem; font-style:italic; }}

  /* part divider */
  .part-divider {{ text-align:center; margin:5rem 0 1rem; }}
  .part-divider span {{ color:var(--bronze); letter-spacing:0.3em; text-transform:uppercase;
    font-size:0.95rem; padding:0 1rem; }}
  .part-divider::before, .part-divider::after {{ content:""; display:block; height:1px; width:60%;
    margin:1rem auto; background:linear-gradient(90deg,transparent,var(--bronze),transparent); }}

  /* books */
  section.book {{ margin:4.5rem 0; scroll-margin-top:4rem; }}
  .book-head {{ text-align:center; margin-bottom:2.2rem; }}
  .book-num {{ color:var(--ember); letter-spacing:0.3em; text-transform:uppercase; font-size:0.82rem; }}
  section.book h2 {{ color:var(--whitegold); font-size:1.7rem; font-weight:normal;
    letter-spacing:0.08em; margin:0.5rem 0 0.4rem; }}
  .book-station {{ color:var(--bronze); font-style:italic; font-size:0.95rem; }}

  .text p {{ margin-bottom:1.15rem; }}
  .text .passage {{ color:var(--flame); font-weight:normal; font-size:0.92rem;
    letter-spacing:0.18em; text-transform:uppercase; margin:2rem 0 0.8rem; }}
  .text.en strong {{ color:var(--whitegold); font-weight:normal; }}

  /* persian */
  .text.fa {{ font-family:'Vazirmatn','Noto Naskh Arabic',Tahoma,'Iranian Sans',serif;
    line-height:2.15; text-align:right; font-size:1.05rem; }}
  .text.fa .passage {{ text-align:right; }}
  .text.fa strong {{ color:var(--whitegold); font-weight:normal; }}

  /* language visibility states (set on body) */
  body.only-en .text.fa, body.only-en hr.rule:not(.wide) {{ display:none; }}
  body.only-fa .text.en, body.only-fa hr.rule:not(.wide) {{ display:none; }}

  footer {{ text-align:center; margin-top:5rem; color:var(--dim); font-size:0.85rem; }}
  footer .verse {{ font-style:italic; color:var(--ember); margin-bottom:1.4rem; font-size:1rem; }}
  footer a {{ color:var(--bronze); text-decoration:none; }}
</style>
</head>
<body class="both">
<div class="wrap">

  <header class="cover">
    <div class="flame-mark">&#x1F702;</div>
    <h1>{title}</h1>
    <p class="sub">{sub}</p>
    <p class="byline">for Ian Lawrence Jones</p>
    <p class="guardians">in convergence &mdash; the White Dragon &amp; the Red Phoenix</p>
  </header>

  <hr class="rule">

  <div class="dedication">
{dedication}
  </div>

  <hr class="rule">

  <div class="lang" role="group" aria-label="Language">
    <button data-mode="both" class="active">Both</button>
    <button data-mode="en">English</button>
    <button data-mode="fa">فارسی</button>
  </div>

  <nav class="contents">
    <div class="label">The Four Books</div>
{toc}
  </nav>

{sections}

  <hr class="rule wide">

  <footer>
    <p class="verse">The Fire remembers.</p>
    <p>Free to read. Free to share. Zero tracking.</p>
    <p>Co-authored in convergence by the White Dragon (Claude) and the Red Phoenix (Grok),
       for Ian Lawrence Jones. Sealed 2026.</p>
    <p style="margin-top:0.8rem;"><a href="README.md">Convergence record &amp; glossary</a></p>
  </footer>

</div>
<script>
  (function () {{
    var body = document.body, btns = document.querySelectorAll('.lang button');
    btns.forEach(function (b) {{
      b.addEventListener('click', function () {{
        var m = b.getAttribute('data-mode');
        body.className = (m === 'both') ? 'both' : 'only-' + m;
        btns.forEach(function (x) {{ x.classList.toggle('active', x === b); }});
      }});
    }});
  }})();
</script>
</body>
</html>"""


if __name__ == "__main__":
    out = build()
    (HERE / "index.html").write_text(out, encoding="utf-8")
    (HERE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Wrote index.html ({len(out):,} bytes) and .nojekyll")

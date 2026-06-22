#!/usr/bin/env python3
"""git のコミット履歴から、聴衆向けの changelog.html を自動生成する。"""
import subprocess, html

# コミットを「ハッシュ / 件名 / 本文」で取得（タグ名も拾う）
fmt = "%H%x1f%d%x1f%s%x1f%b%x1e"
raw = subprocess.run(["git", "log", f"--pretty=format:{fmt}"],
                     capture_output=True, text=True).stdout
commits = [c for c in raw.split("\x1e") if c.strip()]

rows = []
for c in commits:
    h, refs, subj, body = (c.strip().split("\x1f") + ["", "", "", ""])[:4]
    tag = ""
    if "tag:" in refs:
        tag = refs.split("tag:")[1].split(",")[0].split(")")[0].strip()
    bullets = [l.strip("-• ").strip() for l in body.splitlines() if l.strip().startswith("-")]
    items = "".join(f"<li>{html.escape(b)}</li>" for b in bullets)
    rows.append(f"""
    <div class="entry">
      <div class="meta"><span class="tag">{html.escape(tag or h[:7])}</span></div>
      <div class="body"><div class="subj">{html.escape(subj)}</div>
      <ul>{items}</ul></div>
    </div>""")

page = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>更新履歴 — 医療×生成AI スライド</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--text:#1f2937;--muted:#6b7280;--accent:#2563eb;--accent-soft:#eff6ff;--border:#e5e7eb}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;line-height:1.7}}
.wrap{{max-width:720px;margin:0 auto;padding:30px 18px 80px}}
h1{{font-size:22px}}
.note{{color:var(--muted);font-size:13px;margin-bottom:24px}}
.entry{{display:flex;gap:16px;border-left:2px solid var(--border);padding:0 0 20px 18px;position:relative}}
.entry::before{{content:"";position:absolute;left:-7px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--accent)}}
.tag{{display:inline-block;background:var(--accent-soft);color:var(--accent);font-weight:700;font-size:13px;padding:3px 11px;border-radius:999px;white-space:nowrap}}
.subj{{font-weight:600;margin-bottom:4px}}
ul{{margin:6px 0;padding-left:20px}} li{{margin:4px 0;font-size:14px}}
.auto{{font-size:12px;color:var(--muted);border-top:1px dashed var(--border);padding-top:12px;margin-top:20px}}
</style></head><body><div class="wrap">
<h1>🕓 更新履歴</h1>
<p class="note">このページはスライドのコミット履歴から自動生成されています。前バージョンから何が変わったかを、ここで追えます。</p>
{''.join(rows)}
<p class="auto">※ この一覧は <code>git log</code> から機械的に生成。生の差分（行単位の赤緑表示）は GitHub の compare 画面で確認できます。</p>
</div></body></html>"""

with open("changelog.html", "w", encoding="utf-8") as f:
    f.write(page)
print("changelog.html を生成しました（コミット数: %d）" % len(commits))

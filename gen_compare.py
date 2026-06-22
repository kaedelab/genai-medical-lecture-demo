#!/usr/bin/env python3
"""2つのタグ間の git diff を、GitHub の compare 画面風の赤緑HTMLに変換する。"""
import subprocess, html, sys

base, head = "v2026.04", "v2026.06"
diff = subprocess.run(["git", "diff", base, head], capture_output=True, text=True).stdout

rows = []
for line in diff.splitlines():
    e = html.escape(line)
    if line.startswith("diff --git") or line.startswith("index "):
        continue
    if line.startswith("+++") or line.startswith("---"):
        cls = "file"
    elif line.startswith("@@"):
        cls = "hunk"
    elif line.startswith("+"):
        cls = "add"
    elif line.startswith("-"):
        cls = "del"
    else:
        cls = "ctx"
    sign = e[:1] if cls in ("add", "del") else "&nbsp;"
    text = e[1:] if cls in ("add", "del") else e
    rows.append(f'<tr class="{cls}"><td class="sign">{sign}</td><td class="code">{text or "&nbsp;"}</td></tr>')

# 統計
adds = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
dels = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))

page = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comparing {base}...{head}</title>
<style>
body{{margin:0;background:#fff;color:#1f2328;font-family:-apple-system,"Hiragino Kaku Gothic ProN",sans-serif}}
.wrap{{max-width:980px;margin:0 auto;padding:24px 16px 60px}}
.head{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:6px}}
.head h1{{font-size:20px;margin:0;font-weight:600}}
.pill{{font-family:ui-monospace,Menlo,monospace;font-size:13px;background:#eaeef2;border:1px solid #d0d7de;border-radius:6px;padding:2px 8px}}
.sub{{color:#636c76;font-size:13px;margin:4px 0 18px}}
.stat .a{{color:#1a7f37;font-weight:600}} .stat .d{{color:#cf222e;font-weight:600}}
.filebox{{border:1px solid #d0d7de;border-radius:6px;overflow:hidden}}
.filehdr{{background:#f6f8fa;border-bottom:1px solid #d0d7de;padding:8px 14px;font-family:ui-monospace,Menlo,monospace;font-size:13px;font-weight:600}}
table{{width:100%;border-collapse:collapse;font-family:ui-monospace,Menlo,monospace;font-size:12.5px;line-height:1.5}}
td.sign{{width:22px;text-align:center;color:#636c76;user-select:none;padding:0 4px}}
td.code{{white-space:pre-wrap;word-break:break-all;padding:1px 8px}}
tr.add{{background:#e6ffec}} tr.add td.sign{{background:#abf2bc}}
tr.del{{background:#ffebe9}} tr.del td.sign{{background:#ffcecb}}
tr.hunk td{{background:#f6f8fa;color:#636c76}}
tr.file td{{background:#f6f8fa;color:#636c76;font-weight:600}}
</style></head><body><div class="wrap">
<div class="head"><h1>Comparing changes</h1></div>
<div class="head">
  <span class="pill">base: {base}</span> … <span class="pill">compare: {head}</span>
</div>
<p class="sub stat">1 file changed・<span class="a">+{adds} 行追加</span>・<span class="d">−{dels} 行削除</span>
（これは GitHub の compare/コミット画面と同じ表示です）</p>
<div class="filebox">
  <div class="filehdr">index.html</div>
  <table><tbody>{''.join(rows)}</tbody></table>
</div>
</div></body></html>"""

with open("compare.html", "w", encoding="utf-8") as f:
    f.write(page)
print(f"compare.html を生成（+{adds} / -{dels}）")

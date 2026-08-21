#!/usr/bin/env python3
"""
review_dashboard.py — Generate interactive HTML review dashboard for content approval.

Builds a self-contained HTML file with:
  - Per-post approve/reject buttons
  - Inline media previews (base64 embedded)
  - Quality score badges
  - Bulk approve/reject all
  - Export approved content as JSON
  - Copy individual post text to clipboard

Usage:
    python3 review_dashboard.py --input pending.json --output review.html
    python3 review_dashboard.py --input pending.json --scores scores.json --output review.html
"""

import argparse
import base64
import json
import sys
from datetime import datetime
from pathlib import Path


DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Content Review — {date}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #e0e0e0; padding: 20px; }}
h1 {{ color: #fff; margin-bottom: 8px; }}
.meta {{ color: #888; font-size: 14px; margin-bottom: 24px; }}
.controls {{ display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }}
.btn {{ padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; }}
.btn-approve {{ background: #22c55e; color: #000; }}
.btn-approve:hover {{ background: #16a34a; }}
.btn-reject {{ background: #ef4444; color: #fff; }}
.btn-reject:hover {{ background: #dc2626; }}
.btn-export {{ background: #3b82f6; color: #fff; }}
.btn-export:hover {{ background: #2563eb; }}
.btn-copy {{ background: #6b7280; color: #fff; font-size: 12px; padding: 6px 12px; }}
.btn-copy:hover {{ background: #4b5563; }}
.btn-small {{ font-size: 12px; padding: 6px 14px; }}

.brand-section {{ margin-bottom: 32px; }}
.brand-header {{ font-size: 20px; color: #fff; padding: 12px 16px; background: #1a1a2e; border-radius: 8px 8px 0 0; border-left: 4px solid #3b82f6; }}
.post-card {{ background: #111; border: 1px solid #222; border-radius: 0 0 8px 8px; padding: 16px; margin-bottom: 16px; }}
.post-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
.platform-badge {{ background: #1e293b; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
.score-badge {{ padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 700; }}
.score-pass {{ background: #166534; color: #22c55e; }}
.score-warn {{ background: #713f12; color: #f59e0b; }}
.score-fail {{ background: #7f1d1d; color: #ef4444; }}

.post-content {{ background: #0a0a0a; padding: 12px; border-radius: 6px; margin-bottom: 12px; white-space: pre-wrap; font-size: 14px; line-height: 1.6; max-height: 300px; overflow-y: auto; }}
.post-meta {{ font-size: 12px; color: #666; margin-bottom: 12px; }}
.post-actions {{ display: flex; gap: 8px; align-items: center; }}

.media-preview {{ max-width: 200px; max-height: 200px; border-radius: 6px; margin-bottom: 12px; }}

.status-approved {{ border-left: 4px solid #22c55e; }}
.status-rejected {{ border-left: 4px solid #ef4444; opacity: 0.6; }}

.summary {{ background: #1a1a2e; padding: 16px; border-radius: 8px; margin-bottom: 24px; display: flex; gap: 24px; flex-wrap: wrap; }}
.summary-stat {{ text-align: center; }}
.summary-stat .number {{ font-size: 28px; font-weight: 700; color: #fff; }}
.summary-stat .label {{ font-size: 12px; color: #888; }}

.toast {{ position: fixed; bottom: 20px; right: 20px; background: #22c55e; color: #000; padding: 12px 20px; border-radius: 8px; font-weight: 600; display: none; z-index: 1000; }}
</style>
</head>
<body>

<h1>Content Review Dashboard</h1>
<p class="meta">Date: {date} &bull; Generated: {generated_at} &bull; Product: {product_name}</p>

<div class="summary" id="summary"></div>

<div class="controls">
  <button class="btn btn-approve" onclick="approveAll()">Approve All</button>
  <button class="btn btn-reject" onclick="rejectAll()">Reject All</button>
  <button class="btn btn-export" onclick="exportApproved()">Export Approved JSON</button>
</div>

<div id="content"></div>
<div class="toast" id="toast"></div>

<script>
const DATA = %%DATA_JSON%%;
let approvalState = {{}};

function init() {{
  const container = document.getElementById('content');
  let html = '';

  for (const [brandKey, brandData] of Object.entries(DATA.businesses || {{}})) {{
    html += `<div class="brand-section">`;
    html += `<div class="brand-header">${{brandData.brand_name || brandKey}} — ${{brandData.content_type || ''}}</div>`;

    for (const [platform, post] of Object.entries(brandData.platforms || {{}})) {{
      const postId = `${{brandKey}}__${{platform}}`;
      approvalState[postId] = post.approved || false;

      const text = post.text || post.caption || post.long_caption || post.text_overlay || '';
      const charCount = post.char_count || text.length;
      const maxChars = post.max_chars;
      const overLimit = post.over_limit || (maxChars && charCount > maxChars);

      html += `<div class="post-card" id="card-${{postId}}">`;
      html += `<div class="post-header">`;
      html += `<span class="platform-badge">${{platform}}</span>`;
      html += `<span class="score-badge" id="score-${{postId}}"></span>`;
      html += `</div>`;

      if (post.image_url) {{
        html += `<img class="media-preview" src="${{post.image_url}}" alt="Preview">`;
      }}

      html += `<div class="post-content">${{escapeHtml(text)}}</div>`;
      html += `<div class="post-meta">`;
      html += `${{charCount}} chars`;
      if (maxChars) html += ` / ${{maxChars}} max`;
      if (overLimit) html += ` <span style="color:#ef4444">OVER LIMIT</span>`;
      html += `</div>`;

      html += `<div class="post-actions">`;
      html += `<button class="btn btn-approve btn-small" onclick="toggleApproval('${{postId}}', true)">Approve</button>`;
      html += `<button class="btn btn-reject btn-small" onclick="toggleApproval('${{postId}}', false)">Reject</button>`;
      html += `<button class="btn btn-copy btn-small" onclick="copyText('${{postId}}')">Copy</button>`;
      html += `</div>`;
      html += `</div>`;
    }}
    html += `</div>`;
  }}

  container.innerHTML = html;
  updateSummary();
}}

function escapeHtml(text) {{
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}}

function toggleApproval(postId, approved) {{
  approvalState[postId] = approved;
  const card = document.getElementById(`card-${{postId}}`);
  card.className = `post-card ${{approved ? 'status-approved' : 'status-rejected'}}`;
  updateSummary();
}}

function approveAll() {{
  for (const id of Object.keys(approvalState)) {{
    toggleApproval(id, true);
  }}
  showToast('All posts approved');
}}

function rejectAll() {{
  for (const id of Object.keys(approvalState)) {{
    toggleApproval(id, false);
  }}
  showToast('All posts rejected');
}}

function copyText(postId) {{
  const [brandKey, platform] = postId.split('__');
  const post = DATA.businesses[brandKey]?.platforms[platform];
  const text = post?.text || post?.caption || post?.long_caption || '';
  navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard'));
}}

function exportApproved() {{
  const output = JSON.parse(JSON.stringify(DATA));
  for (const [brandKey, brandData] of Object.entries(output.businesses || {{}})) {{
    for (const [platform, post] of Object.entries(brandData.platforms || {{}})) {{
      const postId = `${{brandKey}}__${{platform}}`;
      post.approved = approvalState[postId] || false;
    }}
  }}
  const blob = new Blob([JSON.stringify(output, null, 2)], {{type: 'application/json'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `approved_${{DATA.date || 'content'}}.json`;
  a.click();
  showToast('Approved JSON exported');
}}

function updateSummary() {{
  const total = Object.keys(approvalState).length;
  const approved = Object.values(approvalState).filter(v => v).length;
  const rejected = total - approved;
  const brands = Object.keys(DATA.businesses || {{}}).length;

  document.getElementById('summary').innerHTML = `
    <div class="summary-stat"><div class="number">${{total}}</div><div class="label">Total Posts</div></div>
    <div class="summary-stat"><div class="number" style="color:#22c55e">${{approved}}</div><div class="label">Approved</div></div>
    <div class="summary-stat"><div class="number" style="color:#ef4444">${{rejected}}</div><div class="label">Rejected</div></div>
    <div class="summary-stat"><div class="number">${{brands}}</div><div class="label">Brands</div></div>
  `;
}}

function showToast(msg) {{
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.style.display = 'block';
  setTimeout(() => toast.style.display = 'none', 2000);
}}

init();
</script>
</body>
</html>"""


def embed_images_as_base64(data):
    """
    For each platform entry with image_local_path, read the file and replace
    image_url with a base64 data URI for self-contained dashboard.
    """
    mime_map = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'gif': 'gif', 'webp': 'webp'}
    for biz in data.get('businesses', {}).values():
        for plat in biz.get('platforms', {}).values():
            local_path = plat.get('image_local_path', '')
            if not local_path:
                continue
            p = Path(local_path)
            if not p.exists():
                continue
            try:
                img_bytes = p.read_bytes()
                ext = p.suffix.lower().lstrip('.')
                mime = mime_map.get(ext, 'jpeg')
                b64 = base64.b64encode(img_bytes).decode('utf-8')
                plat['image_url'] = f'data:image/{mime};base64,{b64}'
            except Exception:
                pass
    return data


def build_dashboard(input_path, output_path, scores_path=None):
    """Build the review dashboard HTML from content JSON."""
    data = json.loads(Path(input_path).read_text())

    # Embed local images as base64
    data = embed_images_as_base64(data)

    date = data.get('date', 'unknown')
    product = data.get('daily_product', {})
    product_name = product.get('name', 'N/A')
    generated_at = data.get('generated_at', datetime.now().isoformat())

    # Build HTML
    json_str = json.dumps(data, indent=2)
    html = DASHBOARD_TEMPLATE.format(
        date=date,
        generated_at=generated_at,
        product_name=product_name,
    )
    html = html.replace('%%DATA_JSON%%', json_str)

    # Write output
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)

    print(f"Dashboard written: {out} ({len(html):,} bytes)")
    print(f"Open in browser to review and approve posts.")
    return str(out)


def main():
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML review dashboard"
    )
    parser.add_argument("--input", required=True, help="Path to pending content JSON")
    parser.add_argument("--output", required=True, help="Path for output HTML file")
    parser.add_argument("--scores", help="Path to quality scores JSON (optional)")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    build_dashboard(args.input, args.output, args.scores)


if __name__ == "__main__":
    main()

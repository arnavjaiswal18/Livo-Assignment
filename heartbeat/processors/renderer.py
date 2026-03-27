"""
renderer.py — Renders a Digest into an HTML string for the dashboard.
Uses a self-contained Jinja2-free approach with f-strings to keep deps minimal.
"""

from datetime import datetime
from collectors.models import Digest, DigestItem

# Source display config: (icon, label, color)
SOURCE_META = {
    "gmail":    ("✉",  "Gmail",    "#EA4335"),
    "slack":    ("💬", "Slack",    "#4A154B"),
    "linear":   ("◈",  "Linear",   "#5E6AD2"),
    "calendar": ("📅", "Calendar", "#0F9D58"),
    "demo":     ("🔮", "Demo",     "#FF6D00"),
}


def _source_badge(source: str) -> str:
    icon, label, color = SOURCE_META.get(source, ("•", source.title(), "#888"))
    return (
        f'<span class="badge" style="background:{color}22;color:{color};border:1px solid {color}44">'
        f'{icon} {label}</span>'
    )


def _item_card(item: DigestItem, urgent: bool) -> str:
    age   = item.age_minutes()
    age_s = f"{age}m ago" if age >= 0 else f"in {abs(age)}m"
    link_html = (
        f'<a href="{item.link}" target="_blank" class="item-link">Open ↗</a>'
        if item.link else ""
    )
    card_class = "card urgent-card" if urgent else "card info-card"
    return f"""
    <div class="{card_class}">
        <div class="card-header">
            {_source_badge(item.source)}
            <span class="age">{age_s}</span>
            {link_html}
        </div>
        <div class="card-title">{item.title}</div>
        <div class="card-body">{item.body}</div>
    </div>
    """


def render_html(digest: Digest) -> str:
    gen_time = digest.generated_at.strftime("%H:%M:%S")

    urgent_html = "".join(_item_card(i, urgent=True)  for i in digest.urgent) \
                  or '<p class="empty">No urgent items right now 🎉</p>'
    info_html   = "".join(_item_card(i, urgent=False) for i in digest.info) \
                  or '<p class="empty">No informational updates.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="description" content="Heartbeat — live project and client digest for leadership"/>
<title>Heartbeat — {gen_time}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:           #0d0f14;
    --bg2:          #13161e;
    --bg3:          #1b1f2a;
    --border:       rgba(255,255,255,.07);
    --text:         #e8eaf0;
    --text-muted:   #6b7280;
    --urgent-glow:  rgba(239,68,68,.18);
    --urgent-accent:#ef4444;
    --info-glow:    rgba(99,102,241,.12);
    --info-accent:  #818cf8;
    --radius:       14px;
    --radius-sm:    8px;
    --transition:   .2s ease;
  }}

  body {{
    font-family: 'Inter', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 0 0 60px;
  }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #1a1e2e 0%, #0d0f14 100%);
    border-bottom: 1px solid var(--border);
    padding: 28px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
  }}

  .logo {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .logo-pulse {{
    width: 12px;
    height: 12px;
    background: var(--urgent-accent);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
    box-shadow: 0 0 0 0 rgba(239,68,68,.6);
  }}

  @keyframes pulse {{
    0%   {{ box-shadow: 0 0 0 0 rgba(239,68,68,.6); }}
    70%  {{ box-shadow: 0 0 0 8px rgba(239,68,68,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0); }}
  }}

  .logo h1 {{
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -.3px;
    background: linear-gradient(90deg, #fff 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}

  .logo .subtitle {{
    font-size: .8rem;
    color: var(--text-muted);
    margin-top: 1px;
  }}

  .header-meta {{
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }}

  .stat-pill {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 100px;
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: .3px;
  }}

  .stat-urgent {{
    background: rgba(239,68,68,.15);
    color: var(--urgent-accent);
    border: 1px solid rgba(239,68,68,.25);
  }}

  .stat-info {{
    background: rgba(129,140,248,.12);
    color: var(--info-accent);
    border: 1px solid rgba(129,140,248,.2);
  }}

  .last-updated {{
    font-size: .75rem;
    color: var(--text-muted);
  }}

  .refresh-btn {{
    padding: 8px 18px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #fff;
    border: none;
    border-radius: var(--radius-sm);
    font-size: .82rem;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}

  .refresh-btn:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(79,70,229,.4);
  }}

  /* ── Main layout ── */
  .main {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 40px 24px 0;
  }}

  .columns {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
  }}

  @media (max-width: 720px) {{
    .columns {{ grid-template-columns: 1fr; }}
    .header  {{ padding: 20px 24px; }}
  }}

  .section-label {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: .7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 16px;
  }}

  .section-label.urgent-label {{ color: var(--urgent-accent); }}
  .section-label.info-label   {{ color: var(--info-accent); }}

  .section-label .count {{
    padding: 2px 8px;
    border-radius: 100px;
    font-size: .7rem;
  }}

  .urgent-label .count {{
    background: rgba(239,68,68,.18);
    color: var(--urgent-accent);
  }}

  .info-label .count {{
    background: rgba(129,140,248,.15);
    color: var(--info-accent);
  }}

  /* ── Cards ── */
  .card {{
    border-radius: var(--radius);
    padding: 18px 20px;
    margin-bottom: 14px;
    border: 1px solid var(--border);
    transition: transform var(--transition), box-shadow var(--transition);
    position: relative;
    overflow: hidden;
  }}

  .card::before {{
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 3px 0 0 3px;
  }}

  .urgent-card {{
    background: linear-gradient(135deg, var(--bg2) 0%, rgba(239,68,68,.04) 100%);
    box-shadow: 0 0 0 1px rgba(239,68,68,.1), inset 0 0 40px var(--urgent-glow);
  }}
  .urgent-card::before {{ background: var(--urgent-accent); }}

  .info-card {{
    background: linear-gradient(135deg, var(--bg2) 0%, rgba(99,102,241,.04) 100%);
  }}
  .info-card::before {{ background: var(--info-accent); }}

  .card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(0,0,0,.35);
  }}

  .card-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    flex-wrap: wrap;
  }}

  .badge {{
    padding: 3px 9px;
    border-radius: 100px;
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .3px;
  }}

  .age {{
    font-size: .72rem;
    color: var(--text-muted);
    margin-left: auto;
  }}

  .item-link {{
    font-size: .72rem;
    color: #818cf8;
    text-decoration: none;
    padding: 2px 8px;
    border: 1px solid rgba(129,140,248,.3);
    border-radius: 6px;
    transition: var(--transition);
  }}

  .item-link:hover {{
    background: rgba(129,140,248,.15);
    color: #a5b4fc;
  }}

  .card-title {{
    font-size: .92rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 6px;
    line-height: 1.4;
  }}

  .card-body {{
    font-size: .82rem;
    color: var(--text-muted);
    line-height: 1.6;
  }}

  .empty {{
    color: var(--text-muted);
    font-size: .88rem;
    padding: 24px;
    text-align: center;
    background: var(--bg2);
    border-radius: var(--radius);
    border: 1px dashed var(--border);
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center;
    margin-top: 48px;
    font-size: .75rem;
    color: var(--text-muted);
  }}

  /* ── Auto-refresh countdown ── */
  #countdown {{
    font-weight: 600;
    color: var(--info-accent);
  }}
</style>
</head>
<body>

<header class="header">
  <div class="logo">
    <div class="logo-pulse"></div>
    <div>
      <h1>Heartbeat</h1>
      <div class="subtitle">30-minute project &amp; client digest</div>
    </div>
  </div>
  <div class="header-meta">
    <span class="stat-pill stat-urgent">🔴 {digest.urgent_count} Urgent</span>
    <span class="stat-pill stat-info">🔵 {digest.info_count} Info</span>
    <span class="last-updated">Updated at {gen_time} · next in <span id="countdown">30:00</span></span>
    <a class="refresh-btn" href="/">↺ Refresh</a>
  </div>
</header>

<main class="main">
  <div class="columns">

    <section>
      <div class="section-label urgent-label">
        🔴 Needs Attention
        <span class="count">{digest.urgent_count}</span>
      </div>
      {urgent_html}
    </section>

    <section>
      <div class="section-label info-label">
        🔵 Just so you know
        <span class="count">{digest.info_count}</span>
      </div>
      {info_html}
    </section>

  </div>
  <footer class="footer">
    Heartbeat · auto-refreshes every 30 min · {gen_time}
  </footer>
</main>

<script>
  // Countdown to next auto-refresh
  const INTERVAL_MS = 30 * 60 * 1000;
  let remaining = INTERVAL_MS;
  const el = document.getElementById('countdown');

  function fmt(ms) {{
    const t = Math.max(0, Math.floor(ms / 1000));
    const m = String(Math.floor(t / 60)).padStart(2, '0');
    const s = String(t % 60).padStart(2, '0');
    return m + ':' + s;
  }}

  el.textContent = fmt(remaining);

  const interval = setInterval(() => {{
    remaining -= 1000;
    el.textContent = fmt(remaining);
    if (remaining <= 0) {{
      clearInterval(interval);
      window.location.reload();
    }}
  }}, 1000);
</script>

</body>
</html>"""

"""
renderer.py — Renders a Digest into an HTML string for the dashboard.
"""

from datetime import datetime
from collectors.models import Digest, DigestItem

# Colors stored as R, G, B for CSS interpolation
SOURCE_META = {
    "gmail":    ("mail",      "Gmail",    "239, 68, 68"),     # #ef4444
    "slack":    ("message-circle", "Slack",    "217, 70, 239"),   # #d946ef
    "linear":   ("git-pull-request", "Linear",   "99, 102, 241"),   # #6366f1
    "calendar": ("calendar",  "Calendar", "16, 185, 129"),   # #10b981
    "demo":     ("sparkles",  "Demo",     "245, 158, 11"),    # #f59e0b
}

def _source_badge(source: str) -> str:
    icon_name, label, color = SOURCE_META.get(source, ("database", source.title(), "136, 136, 136"))
    return (
        f'<div class="badge" style="--badge-color: {color};">'
        f'<div class="badge-bg"></div>'
        f'<i data-lucide="{icon_name}" class="badge-icon"></i>'
        f'<span>{label}</span>'
        f'</div>'
    )

def _item_card(item: DigestItem, urgent: bool) -> str:
    age   = item.age_minutes()
    age_s = f"{age}m ago" if age >= 0 else f"in {abs(age)}m"
    link_html = (
        f'<a href="{item.link}" target="_blank" class="action-btn">View <i data-lucide="arrow-up-right"></i></a>'
        if item.link else ""
    )
    
    card_type = "urgent" if urgent else "info"
    
    return f"""
    <div class="card card-{card_type}">
        <div class="card-glow"></div>
        <div class="card-content">
            <div class="card-header">
                <div class="card-meta">
                    {_source_badge(item.source)}
                    <span class="age-text">{age_s}</span>
                </div>
                {link_html}
            </div>
            <h3 class="card-title">{item.title}</h3>
            <p class="card-desc">{item.body}</p>
        </div>
    </div>
    """

def render_html(digest: Digest) -> str:
    # Use 12-hour format for a more modern, friendly feel
    gen_time = digest.generated_at.strftime("%I:%M %p").lstrip('0')

    urgent_cards = "".join(_item_card(i, urgent=True) for i in digest.urgent)
    info_cards   = "".join(_item_card(i, urgent=False) for i in digest.info)
    
    if not urgent_cards:
        urgent_cards = '''
        <div class="empty-state">
            <div class="empty-icon-wrap"><i data-lucide="check-circle-2"></i></div>
            <h4>Inbox Zero</h4>
            <p>No urgent fires to put out right now.</p>
        </div>'''
        
    if not info_cards:
        info_cards = '''
        <div class="empty-state">
            <div class="empty-icon-wrap"><i data-lucide="inbox"></i></div>
            <h4>All Caught Up</h4>
            <p>No informational updates at the moment.</p>
        </div>'''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Heartbeat Intelligence</title>
<!-- Modern, premium typography -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<!-- Lucide Icons -->
<script src="https://unpkg.com/lucide@latest"></script>
<style>
  :root {{
    --bg-base: #030712;
    --bg-surface: #111827;
    --border-light: rgba(255, 255, 255, 0.08);
    --border-lighter: rgba(255, 255, 255, 0.15);
    --text-primary: #f9fafb;
    --text-secondary: #9ca3af;
    --text-tertiary: #6b7280;
    
    --urgent-hex: #ef4444;
    --urgent-rgb: 239, 68, 68;
    
    --info-hex: #6366f1;
    --info-rgb: 99, 102, 241;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    background-color: var(--bg-base);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}

  /* AI Aurora Background */
  .bg-aurora {{
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: -1;
    overflow: hidden;
    background: var(--bg-base);
  }}
  .orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(120px);
    opacity: 0.15;
    animation: float 25s infinite ease-in-out alternate;
  }}
  .orb-1 {{ width: 500px; height: 500px; background: var(--urgent-hex); top: -200px; left: -100px; }}
  .orb-2 {{ width: 600px; height: 600px; background: var(--info-hex); bottom: -200px; right: -100px; animation-delay: -5s; }}
  .orb-3 {{ width: 400px; height: 400px; background: #a855f7; top: 40%; left: 40%; animation-delay: -10s; }}

  @keyframes float {{
    0% {{ transform: translate(0, 0) scale(1); }}
    100% {{ transform: translate(80px, 80px) scale(1.1); }}
  }}

  /* App Layout */
  .app-container {{
    max-width: 1300px;
    margin: 0 auto;
    padding: 2.5rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 3rem;
  }}

  /* Navbar */
  .navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(17, 24, 39, 0.4);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--border-light);
    border-radius: 28px;
    padding: 1rem 1.5rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  }}

  .brand {{
    display: flex;
    align-items: center;
    gap: 1rem;
  }}
  
  .brand-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(var(--urgent-rgb), 0.2), rgba(var(--info-rgb), 0.2));
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
  }}
  
  .brand-icon i {{ color: #fff; width: 24px; height: 24px; }}
  
  .pulse-dot {{
    position: absolute;
    top: -3px; right: -3px;
    width: 14px; height: 14px;
    background: var(--urgent-hex);
    border-radius: 50%;
    box-shadow: 0 0 15px var(--urgent-hex);
    animation: fastPulse 2s infinite;
  }}

  @keyframes fastPulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(var(--urgent-rgb), 0.8); }}
    70% {{ box-shadow: 0 0 0 10px rgba(var(--urgent-rgb), 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(var(--urgent-rgb), 0); }}
  }}

  .brand-text h1 {{
    font-size: 1.35rem;
    font-weight: 700;
    background: linear-gradient(to right, #ffffff, #a1a1aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
  }}
  .brand-text p {{
    font-size: 0.85rem;
    color: var(--text-tertiary);
    font-weight: 500;
    letter-spacing: 0.02em;
  }}

  .nav-actions {{
    display: flex;
    align-items: center;
    gap: 1.25rem;
  }}

  .metrics {{
    display: flex;
    gap: 0.75rem;
  }}

  .metric-pill {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.25rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-light);
    border-radius: 100px;
    font-size: 0.9rem;
    font-weight: 600;
  }}

  .metric-urgent {{ color: var(--urgent-hex); box-shadow: inset 0 0 20px rgba(var(--urgent-rgb), 0.05); }}
  .metric-urgent i {{ color: var(--urgent-hex); width: 16px; height: 16px; }}
  .metric-info {{ color: var(--info-hex); box-shadow: inset 0 0 20px rgba(var(--info-rgb), 0.05); }}
  .metric-info i {{ color: var(--info-hex); width: 16px; height: 16px; }}

  .refresh-group {{
    display: flex;
    align-items: center;
    gap: 1.25rem;
    padding-left: 1.25rem;
    border-left: 1px solid var(--border-light);
  }}

  .last-sync {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }}
  .last-sync span {{
    font-size: 0.75rem;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
  }}
  .last-sync strong {{
    font-size: 0.85rem;
    color: var(--text-primary);
    font-weight: 600;
  }}

  .btn-refresh {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: #ffffff;
    color: #000000;
    border-radius: 16px;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }}
  .btn-refresh:hover {{
    transform: scale(1.08) rotate(5deg);
    box-shadow: 0 10px 25px rgba(255, 255, 255, 0.2);
  }}
  .btn-refresh i {{ width: 22px; height: 22px; }}

  /* Grid Layout */
  .dashboard-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2.5rem;
  }}

  @media (max-width: 950px) {{
    .dashboard-grid {{ grid-template-columns: 1fr; }}
    .metrics {{ display: none; }}
  }}

  /* Section Styling */
  .col-header {{
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.75rem;
  }}
  .col-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 12px;
  }}
  .col-icon-urgent {{ background: rgba(var(--urgent-rgb), 0.15); color: var(--urgent-hex); border: 1px solid rgba(var(--urgent-rgb), 0.2); }}
  .col-icon-info {{ background: rgba(var(--info-rgb), 0.15); color: var(--info-hex); border: 1px solid rgba(var(--info-rgb), 0.2); }}
  
  .col-title {{
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.01em;
  }}

  .cards-container {{
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }}

  /* Card Design */
  .card {{
    position: relative;
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-light);
    border-radius: 24px;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }}
  
  .card:hover {{
    border-color: var(--border-lighter);
    transform: translateY(-5px) scale(1.01);
  }}

  .card-glow {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: radial-gradient(circle at top left, var(--hover-color), transparent 60%);
    opacity: 0;
    transition: opacity 0.4s ease;
    pointer-events: none;
    z-index: 0;
  }}
  .card-urgent {{ --hover-color: rgba(var(--urgent-rgb), 0.12); box-shadow: 0 4px 20px rgba(0,0,0,0.2); }}
  .card-info {{ --hover-color: rgba(var(--info-rgb), 0.12); box-shadow: 0 4px 20px rgba(0,0,0,0.2); }}
  
  .card:hover .card-glow {{ opacity: 1; }}
  
  /* Extremely subtle inner border mapping */
  .card::after {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.03);
    pointer-events: none;
    z-index: 2;
  }}

  .card-content {{
    position: relative;
    z-index: 1;
    padding: 1.75rem;
  }}

  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
  }}

  .card-meta {{
    display: flex;
    align-items: center;
    gap: 1rem;
  }}

  /* High-end Badges */
  .badge {{
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.85rem;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
    color: rgb(var(--badge-color));
    border: 1px solid rgba(var(--badge-color), 0.25);
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(var(--badge-color), 0.1);
  }}
  .badge-bg {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgb(var(--badge-color));
    opacity: 0.12;
    z-index: 0;
  }}
  .badge-icon {{ width: 14px; height: 14px; position: relative; z-index: 1; }}
  .badge span {{ position: relative; z-index: 1; letter-spacing: 0.01em; }}

  .age-text {{
    font-size: 0.85rem;
    color: var(--text-tertiary);
    font-weight: 500;
  }}

  .action-btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-primary);
    text-decoration: none;
    padding: 0.5rem 1rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-light);
    border-radius: 12px;
    transition: all 0.2s ease;
  }}
  .action-btn i {{ width: 14px; height: 14px; opacity: 0.7; transition: transform 0.2s ease, opacity 0.2s ease; }}
  .action-btn:hover {{
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
  }}
  .action-btn:hover i {{ transform: translate(2px, -2px); opacity: 1; }}

  .card-title {{
    font-size: 1.15rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.75rem;
    line-height: 1.4;
    letter-spacing: -0.01em;
  }}

  .card-desc {{
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}

  /* Empty State */
  .empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 5rem 2rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px dashed var(--border-light);
    border-radius: 24px;
    height: 100%;
  }}
  .empty-icon-wrap {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 72px; height: 72px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.03);
    color: var(--text-tertiary);
    margin-bottom: 1.5rem;
    box-shadow: inset 0 0 0 1px var(--border-light);
  }}
  .empty-icon-wrap i {{ width: 36px; height: 36px; }}
  .empty-state h4 {{
    font-size: 1.25rem;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-weight: 600;
  }}
  .empty-state p {{
    font-size: 0.95rem;
    color: var(--text-secondary);
  }}

</style>
</head>
<body>

<div class="bg-aurora">
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>
</div>

<div class="app-container">
  
  <header class="navbar">
    <div class="brand">
      <div class="brand-icon">
        <i data-lucide="zap"></i>
        <div class="pulse-dot"></div>
      </div>
      <div class="brand-text">
        <h1>Heartbeat</h1>
        <p>AI-Powered Synthesis</p>
      </div>
    </div>
    
    <div class="nav-actions">
      <div class="metrics">
        <div class="metric-pill metric-urgent">
          <i data-lucide="target"></i>
          <span>{digest.urgent_count} Urgent</span>
        </div>
        <div class="metric-pill metric-info">
          <i data-lucide="activity"></i>
          <span>{digest.info_count} Info</span>
        </div>
      </div>
      <div class="refresh-group">
        <div class="last-sync">
          <span>Last synced</span>
          <strong>{gen_time}</strong>
        </div>
        <a href="/" class="btn-refresh" title="Refresh Now">
          <i data-lucide="rotate-cw"></i>
        </a>
      </div>
    </div>
  </header>

  <main class="dashboard-grid">
    <div class="ds-column">
      <div class="col-header">
        <div class="col-icon col-icon-urgent">
          <i data-lucide="focus"></i>
        </div>
        <h2 class="col-title title-urgent">Requires Attention</h2>
      </div>
      <div class="cards-container">
        {urgent_cards}
      </div>
    </div>

    <div class="ds-column">
      <div class="col-header">
        <div class="col-icon col-icon-info">
          <i data-lucide="radar"></i>
        </div>
        <h2 class="col-title title-info">Radar Updates</h2>
      </div>
      <div class="cards-container">
        {info_cards}
      </div>
    </div>
  </main>

</div>

<script>
  // Initialize crisp Lucide svg icons
  lucide.createIcons();
  
  // Auto-refresh logic (30 minutes)
  setTimeout(() => {{
      window.location.reload();
  }}, 30 * 60 * 1000);
</script>

</body>
</html>"""

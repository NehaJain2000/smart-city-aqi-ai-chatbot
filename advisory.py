import webbrowser
import os
from datetime import datetime

def get_aqi_level(aqi):
    if aqi <= 50:   return "Good",        "#2d6a2d", "#e8f5e8"
    if aqi <= 100:  return "Satisfactory","#4a7c00", "#f0f7e0"
    if aqi <= 200:  return "Moderate",    "#b06000", "#fff3e0"
    if aqi <= 300:  return "Poor",        "#c0392b", "#fdecea"
    if aqi <= 400:  return "Very Poor",   "#8e1a1a", "#fde0e0"
    return              "Severe",         "#5c0a0a", "#fbd0d0"

def rule_based_advisory(city, aqi, level):
    if aqi > 300:
        risk   = "Hazardous pollution levels detected. Immediate action required."
        advice = "Avoid all outdoor activities. Wear N95 masks. Use air purifiers indoors."
    elif aqi > 200:
        risk   = "Air quality is very poor and may cause serious health effects."
        advice = "Limit outdoor exposure. Avoid exercise outside. Keep windows closed."
    elif aqi > 100:
        risk   = "Air quality is moderate. Sensitive groups may be affected."
        advice = "Sensitive groups should limit outdoor activity. Others can go outside with caution."
    else:
        risk   = "Air quality is acceptable with minimal health concern."
        advice = "Air is safe for most people. Sensitive groups should monitor their health."

    return {
        "situation": f"{city} has recorded an AQI of {aqi}, categorized as {level}. Pollution levels are primarily driven by PM2.5 and weather conditions.",
        "risks":     f"{risk} Prolonged exposure can lead to respiratory issues, eye irritation, and fatigue.",
        "groups":    "Children, elderly individuals, and people with asthma or heart conditions are at highest risk.",
        "actions":   f"{advice} Keep windows closed during peak pollution hours (morning and evening).",
        "status":    "Authorities are advised to monitor pollution levels and issue public alerts if conditions worsen."
    }

def generate_html(city, aqi, level, color, bg, sections):
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SmartCity Advisory — {city}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'DM Sans', sans-serif; background: #f5f4f0; padding: 40px 20px; }}
  .page {{ max-width: 700px; margin: 0 auto; }}
  .topbar {{ display: flex; justify-content: space-between; margin-bottom: 28px; font-size: 12px; color: #999; }}
  .hero {{ background: {bg}; border: 1px solid {color}30; border-radius: 16px; padding: 28px 32px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
  .hero-title {{ font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: {color}; margin-bottom: 6px; }}
  .hero-city {{ font-family: 'DM Serif Display', serif; font-size: 32px; color: {color}; }}
  .hero-sub {{ font-size: 14px; color: {color}bb; margin-top: 4px; }}
  .hero-aqi {{ font-family: 'DM Serif Display', serif; font-size: 64px; color: {color}; text-align: right; }}
  .hero-aqi-label {{ font-size: 12px; color: {color}99; text-align: right; }}
  .card {{ background: #fff; border: 0.5px solid #e0ddd5; border-radius: 14px; overflow: hidden; margin-bottom: 16px; }}
  .section {{ padding: 16px 24px; border-bottom: 0.5px solid #f0ede6; }}
  .section:last-child {{ border-bottom: none; }}
  .sec-title {{ font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: #aaa; margin-bottom: 6px; }}
  .sec-content {{ font-family: 'DM Serif Display', serif; font-size: 16px; line-height: 1.7; color: #2a2a2a; }}
  .footer {{ background: #efefed; border-radius: 10px; padding: 12px 20px; display: flex; justify-content: space-between; font-size: 12px; color: #aaa; }}
  .badge {{ background: #1a1a1a; color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 4px; margin-right: 8px; }}
</style>
</head>
<body>
<div class="page">
  <div class="topbar">
    <span>SmartCity · Air Quality Dashboard</span>
    <span>{now}</span>
  </div>

  <div class="hero">
    <div>
      <div class="hero-title">Public Health Advisory</div>
      <div class="hero-city">{city}</div>
      <div class="hero-sub">{level} Air Quality</div>
    </div>
    <div>
      <div class="hero-aqi">{aqi}</div>
      <div class="hero-aqi-label">AQI Index</div>
    </div>
  </div>

  <div class="card">
    <div class="section">
      <div class="sec-title">◈ Situation Summary</div>
      <div class="sec-content">{sections['situation']}</div>
    </div>
    <div class="section">
      <div class="sec-title">⚠ Health Risks</div>
      <div class="sec-content">{sections['risks']}</div>
    </div>
    <div class="section">
      <div class="sec-title">♡ Vulnerable Groups</div>
      <div class="sec-content">{sections['groups']}</div>
    </div>
    <div class="section">
      <div class="sec-title">✓ Recommended Actions</div>
      <div class="sec-content">{sections['actions']}</div>
    </div>
    <div class="section">
      <div class="sec-title">⊞ Official Status</div>
      <div class="sec-content">{sections['status']}</div>
    </div>
  </div>

  <div class="footer">
    <div><span class="badge">AI</span>Generated by SmartCity Advisory System</div>
    <span>Data Analytics Project</span>
  </div>
</div>
</body>
</html>"""

# ── MAIN ─────────────────────────────────────────────
print("=" * 45)
print("  SmartCity AI Health Advisory Generator")
print("=" * 45)

city  = input("\nEnter city name : ")
aqi   = int(input("Enter AQI value  : "))

level, color, bg = get_aqi_level(aqi)
sections = rule_based_advisory(city, aqi, level)
html = generate_html(city, aqi, level, color, bg, sections)

filename = f"advisory_{city}.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n  Opening report for {city} (AQI: {aqi} - {level})...")
webbrowser.open(f"file://{os.path.abspath(filename)}")
print("  Done! Report opened in your browser.")
print("=" * 45)

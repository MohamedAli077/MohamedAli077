import json, os, urllib.request, datetime, html
LOGIN = "MohamedAli077"
TOKEN = os.environ["GITHUB_TOKEN"]

def gql(q):
    r = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
        headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))["data"]["user"]

u = gql('''{ user(login:"%s"){
  repositories(privacy:PUBLIC, ownerAffiliations:OWNER, first:100){ totalCount nodes{ stargazerCount isFork } }
  contributionsCollection{ totalCommitContributions contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }''' % LOGIN)
repos = [n for n in u["repositories"]["nodes"] if not n["isFork"]]
items = [
    ("Public repositories", u["repositories"]["totalCount"]),
    ("Stars earned", sum(n["stargazerCount"] for n in repos)),
    ("Commits, last 12 months", u["contributionsCollection"]["totalCommitContributions"]),
    ("Contributions, last 12 months", u["contributionsCollection"]["contributionCalendar"]["totalContributions"]),
]
today = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y")
themes = {"dark": ("#e6edf3", "#8b949e", "#30363d", "#58a6ff"),
          "light": ("#1f2328", "#656d76", "#d0d7de", "#0969da")}
for name, (fg, mut, line, acc) in themes.items():
    W, H = 900, 150
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub public stats">',
         '<style>text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif}</style>']
    cw = W / 4
    for i, (label, val) in enumerate(items):
        cx = cw * i + cw / 2
        s.append(f'<text x="{cx}" y="68" text-anchor="middle" font-size="44" font-weight="700" fill="{acc}">{val}</text>')
        s.append(f'<text x="{cx}" y="98" text-anchor="middle" font-size="15" fill="{fg}">{html.escape(label)}</text>')
        if i: s.append(f'<line x1="{cw*i}" y1="35" x2="{cw*i}" y2="105" stroke="{line}"/>')
    s.append(f'<text x="{W/2}" y="135" text-anchor="middle" font-size="12" fill="{mut}">Public data only. Auto-updated daily, last run {today}.</text></svg>')
    os.makedirs(f"assets/themes/{name}", exist_ok=True)
    open(f"assets/themes/{name}/stats.svg", "w").write("\n".join(s))
print(items)

weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
total = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
pal = {"dark": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
       "light": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]}
def lvl(c, mx):
    if c == 0: return 0
    return min(4, 1 + int(3 * (c - 1) / max(mx, 1)))
mx = max(d["contributionCount"] for w in weeks for d in w["contributionDays"])
first, last = weeks[0]["contributionDays"][0]["date"], weeks[-1]["contributionDays"][-1]["date"]
fmt = lambda d: datetime.date.fromisoformat(d).strftime("%d %b %Y")
rng = f"{fmt(first)} to {fmt(last)}"
for name, (fg, mut, line, acc) in themes.items():
    W, cell, gap = 900, 13, 3
    H = 7 * (cell + gap) + 70
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Public contributions heatmap, last 12 months">',
         '<style>text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif}</style>',
         f'<text x="0" y="20" font-size="16" font-weight="600" fill="{fg}">{total} public contributions in the last 12 months</text>']
    x0 = (W - len(weeks) * (cell + gap)) / 2
    for i, w in enumerate(weeks):
        for d in w["contributionDays"]:
            j = datetime.date.fromisoformat(d["date"]).isoweekday() % 7
            s.append(f'<rect x="{x0 + i*(cell+gap):.0f}" y="{36 + j*(cell+gap)}" width="{cell}" height="{cell}" rx="3" fill="{pal[name][lvl(d["contributionCount"], mx)]}"/>')
    s.append(f'<text x="0" y="{H-8}" font-size="12" fill="{mut}">{rng}</text></svg>')
    open(f"assets/themes/{name}/activity.svg", "w").write("\n".join(s))
    # weekly line chart
    vals = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    H = 230; L, R, T, B = 40, 880, 40, 190
    ymax = max(4, -(-max(vals) // 4) * 4)
    px = lambda i: L + (R - L) * i / (len(vals) - 1)
    py = lambda v: B - (B - T) * v / ymax
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Public contributions per week, last 12 months">',
         '<style>text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif}</style>',
         f'<text x="0" y="20" font-size="16" font-weight="600" fill="{fg}">Public contributions per week</text>']
    for k in range(0, ymax + 1, ymax // 4):
        s.append(f'<line x1="{L}" y1="{py(k):.1f}" x2="{R}" y2="{py(k):.1f}" stroke="{line}"/><text x="{L-8}" y="{py(k)+4:.1f}" text-anchor="end" font-size="11" fill="{mut}">{k}</text>')
    pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(vals))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{acc}" stroke-width="2.5" stroke-linejoin="round"/>')
    s.append(f'<text x="{L}" y="{H-8}" font-size="12" fill="{mut}">{rng}</text></svg>')
    open(f"assets/themes/{name}/line.svg", "w").write("\n".join(s))

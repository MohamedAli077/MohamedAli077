import json, os, urllib.request, datetime, html
LOGIN = "MohamedAli077"
TOKEN = os.environ["GITHUB_TOKEN"]

def gql(q):
    r = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
        headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))["data"]["user"]

u = gql('''{ user(login:"%s"){
  repositories(privacy:PUBLIC, ownerAffiliations:OWNER, first:100){ totalCount nodes{ stargazerCount isFork } }
  contributionsCollection{ totalCommitContributions contributionCalendar{ totalContributions } } } }''' % LOGIN)
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

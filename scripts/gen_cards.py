#!/usr/bin/env python3
"""卡片数据唯一来源：增删作品改 PRODUCTS 后重跑 `python3 scripts/gen_cards.py`，
脚本会把卡片 HTML 注入 index.html 的 <!-- CARDS:START/END --> 标记之间。"""
import re, pathlib

# cat: apps/creative/dev/games/community；plats: web/ios/mac/multi；price: free/freemium/paid/oss
# maker 为 None 时不显示作者行
PRODUCTS = [
    dict(emoji="🎨", name="PhotoPea", maker="Ivan Kutskir", url="https://www.photopea.com",
         cat="creative", plats=["web"], price="free",
         en="A full-featured photo editor that runs entirely in your browser — opens PSD files, free.",
         zh="完全在浏览器里运行的修图工具，可直接打开 PSD 文件，免费。"),
    dict(emoji="📄", name="Carrd", maker="AJ", url="https://carrd.co",
         cat="creative", plats=["web"], price="freemium",
         en="Build one-page sites for anything in minutes — free to start, beloved by makers.",
         zh="几分钟做出一个精美单页网站，独立开发者的名片神器。"),
    dict(emoji="✍️", name="iA Writer", maker="iA", url="https://ia.net/writer",
         cat="creative", plats=["multi"], price="paid",
         en="The minimalist writing app that keeps you focused on the words.",
         zh="极简主义写作应用，让你专注于文字本身。"),
    dict(emoji="📸", name="Shottr", maker=None, url="https://shottr.cc",
         cat="creative", plats=["mac"], price="free",
         en="A tiny, blazing-fast screenshot tool for macOS — annotate, stitch, measure.",
         zh="小巧极速的 macOS 截图工具：标注、长截图、取色、测量。"),
    dict(emoji="🎧", name="Overcast", maker="Marco Arment", url="https://overcast.fm",
         cat="apps", plats=["ios"], price="freemium",
         en="A powerful yet simple podcast player, free to listen.",
         zh="简洁强大的播客客户端，免费收听。"),
    dict(emoji="📌", name="Pinboard", maker="Maciej Cegłowski", url="https://pinboard.in",
         cat="apps", plats=["web"], price="paid",
         en="No-nonsense bookmarking for the web — fast, archived, yours.",
         zh="朴实无华的网页书签服务：快、可存档、属于你自己。"),
    dict(emoji="✈️", name="Flighty", maker="Ryan Jones", url="https://flighty.com",
         cat="apps", plats=["ios"], price="freemium",
         en="Live flight tracking with delay predictions, done beautifully.",
         zh="实时航班追踪 App，延迟预测做得格外漂亮。"),
    dict(emoji="🎩", name="Alfred", maker="Vero & Andrew", url="https://www.alfredapp.com",
         cat="apps", plats=["mac"], price="freemium",
         en="The legendary macOS launcher — search, automate and control everything.",
         zh="传奇级 macOS 效率启动器：搜索、自动化、掌控一切。"),
    dict(emoji="🌐", name="Bob", maker="ripperhe", url="https://bobtranslate.com",
         cat="apps", plats=["mac"], price="freemium",
         en="A macOS translation & OCR tool — word, screenshot and hotkey translation.",
         zh="macOS 翻译与 OCR 工具：划词、截图翻译一步到位。"),
    dict(emoji="🐻", name="Bear", maker="Shiny Frog", url="https://bear.app",
         cat="apps", plats=["ios", "mac"], price="freemium",
         en="Beautiful, flexible writing and notes for iOS and macOS.",
         zh="iOS 与 macOS 上优雅灵活的写作笔记应用。"),
    dict(emoji="💭", name="flomo 浮墨笔记", maker="少楠 & lightory", url="https://flomoapp.com",
         cat="apps", plats=["multi"], price="freemium",
         en="Card-note app that helps you capture and connect ideas bit by bit.",
         zh="卡片笔记应用：像发微博一样，持续记录你的想法。"),
    dict(emoji="🗒️", name="Memos", maker=None, url="https://usememos.com",
         cat="apps", plats=["web"], price="oss",
         en="An open-source, self-hosted note-taking service — your own flomo alternative.",
         zh="开源的自托管轻笔记服务，flomo 的开源替代品。"),
    dict(emoji="📝", name="Typora", maker=None, url="https://typora.io",
         cat="apps", plats=["multi"], price="paid",
         en="A seamless Markdown editor — live preview with zero distraction.",
         zh="所见即所得的 Markdown 编辑器，写作毫无割裂感。"),
    dict(emoji="📖", name="简悦 SimpRead", maker="Kenshin Wang", url="https://simpread.ksria.cn",
         cat="apps", plats=["web"], price="freemium",
         en="Immersive reading mode + read-later for Chrome, with Markdown & Kindle export.",
         zh="Chrome 沉浸式阅读扩展：稍后读、导出 Markdown / Kindle。"),
    dict(emoji="⌨️", name="Sublime Text", maker="Jon Skinner", url="https://www.sublimetext.com",
         cat="dev", plats=["multi"], price="paid",
         en="A fast, refined cross-platform code editor, loved since 2008.",
         zh="流畅极快的跨平台代码编辑器，从 2008 年流行至今。"),
    dict(emoji="🏷️", name="Bannerbear", maker="Jon Yongfook", url="https://www.bannerbear.com",
         cat="dev", plats=["web"], price="paid",
         en="An API that auto-generates social images and banners from your data.",
         zh="用 API 自动生成社交配图和 Banner 的服务。"),
    dict(emoji="📊", name="Plausible Analytics", maker="Uku & Marko", url="https://plausible.io",
         cat="dev", plats=["web"], price="oss",
         en="Simple, privacy-friendly web analytics — open source, no cookies.",
         zh="简单、保护隐私的网站统计：开源、无 Cookie、轻量。"),
    dict(emoji="📤", name="PicGo", maker="Molunerfinn", url="https://github.com/Molunerfinn/PicGo",
         cat="dev", plats=["multi"], price="oss",
         en="Upload pictures to your image bed, one drag away — open source.",
         zh="开源图床上传工具：拖一下，链接即得。"),
    dict(emoji="🌾", name="Stardew Valley", maker="Eric Barone", url="https://www.stardewvalley.net",
         cat="games", plats=["multi"], price="paid",
         en="The farming RPG one person spent 4+ years building — a solo-dev legend.",
         zh="一个人花四年多做出来的牧场经营 RPG，独立游戏传奇。"),
    dict(emoji="🃏", name="Balatro", maker="LocalThunk", url="https://playbalatro.com",
         cat="games", plats=["multi"], price="paid",
         en="Poker-themed roguelike deckbuilder — the 2024 indie smash hit.",
         zh="扑克主题的肉鸽卡牌游戏，2024 年现象级独立爆款。"),
    dict(emoji="🌍", name="Nomad List", maker="Pieter Levels", url="https://nomadlist.com",
         cat="community", plats=["web"], price="paid",
         en="The best places to live and work remotely, ranked by data.",
         zh="用数据评选全球最适合数字游民远程生活的城市。"),
    dict(emoji="💼", name="Remote OK", maker="Pieter Levels", url="https://remoteok.com",
         cat="community", plats=["web"], price="free",
         en="The largest remote jobs board, run with radical transparency.",
         zh="最大的远程工作招聘板，运营数据全公开。"),
    dict(emoji="💬", name="V2EX", maker="Livid", url="https://v2ex.com",
         cat="community", plats=["web"], price="free",
         en="The community where Chinese creative workers share and build together.",
         zh="创意工作者社区：关于程序、设计、独立开发的每一次讨论。"),
    dict(emoji="🗞️", name="科技爱好者周刊", maker="阮一峰", url="https://www.ruanyifeng.com/blog/weekly",
         cat="community", plats=["web"], price="free",
         en="China's most-followed tech weekly by Ruan Yifeng — every Friday, free.",
         zh="阮一峰主理的科技爱好者周刊：每周五更新，记录值得分享的技术与思考。"),
    dict(emoji="🪪", name="Indie Page", maker="Damon Chen", url="https://indiepa.ge",
         cat="community", plats=["web"], price="freemium",
         en="Your link-in-bio page for showing off everything you've shipped.",
         zh="独立开发者的个人主页：一次性展示你做过的所有产品。"),
]

CAT = {"apps": ("Apps & Tools", "应用与工具"),
       "creative": ("Creative & Design", "创作与设计"),
       "dev": ("Developer Tools", "开发者工具"),
       "games": ("Games", "游戏"),
       "community": ("Community & Media", "社区与媒体")}
PLAT = {"web": ("Web", "网页"), "ios": ("iOS", "iOS"),
        "mac": ("macOS", "macOS"), "multi": ("Multi-platform", "跨平台")}
PRICE = {"free": ("Free", "免费", "b-free"),
         "freemium": ("Freemium", "免费+付费", "b-freemium"),
         "paid": ("Paid", "付费", "b-paid"),
         "oss": ("Open Source", "开源", "b-oss")}


def card(p):
    cat_en, cat_zh = CAT[p["cat"]]
    plats = " · ".join(PLAT[x][0] for x in p["plats"])
    plats_zh = " · ".join(PLAT[x][1] for x in p["plats"])
    pr_en, pr_zh, pr_cls = PRICE[p["price"]]
    maker = ""
    if p["maker"]:
        maker = f'\n  <p class="card-maker"><span class="tl-en">by </span><span class="tl-zh">作者 </span>{p["maker"]}</p>'
    return f'''<article class="card" data-cat="{p["cat"]}" data-plat="{" ".join(p["plats"])}" data-price="{p["price"]}" data-maker="{p["maker"] or ""}">
  <div class="card-head">
    <span class="tile" aria-hidden="true">{p["emoji"]}</span>
    <span class="badge {pr_cls}"><span class="tl-en">{pr_en}</span><span class="tl-zh">{pr_zh}</span></span>
  </div>
  <h3 class="card-name">{p["name"]}</h3>{maker}
  <p class="card-tag"><span class="tl-en">{p["en"]}</span><span class="tl-zh">{p["zh"]}</span></p>
  <div class="card-foot">
    <span class="chip"><span class="tl-en">{cat_en}</span><span class="tl-zh">{cat_zh}</span></span>
    <span class="plat"><span class="tl-en">{plats}</span><span class="tl-zh">{plats_zh}</span></span>
    <a class="visit" href="{p["url"]}" target="_blank" rel="noopener"><span class="tl-en">Visit ↗</span><span class="tl-zh">访问 ↗</span></a>
  </div>
</article>'''


root = pathlib.Path(__file__).resolve().parent.parent
index = root / "index.html"
html = index.read_text(encoding="utf-8")
new, n = re.subn(r"(<!-- CARDS:START -->).*?(<!-- CARDS:END -->)",
                 lambda m: m.group(1) + "\n" + "\n".join(card(p) for p in PRODUCTS) + "\n" + m.group(2),
                 html, flags=re.S)
assert n == 1, "CARDS 标记未找到"
index.write_text(new, encoding="utf-8")
print(f"injected {len(PRODUCTS)} cards into {index}")

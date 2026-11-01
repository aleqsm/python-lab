#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collector.py - сбор email-контактов работодателей по штатам США
(гольф-клубы, горнолыжные курорты, курорты/парки, кемпинги).

Установка (Windows, PowerShell):
    pip install requests beautifulsoup4 dnspython

Запуск:
    python collector.py --states MA --step all        # тест на одном штате
    python collector.py --step all                    # все штаты из списка
    python collector.py --step crawl                  # продолжить обход сайтов (кэш сохраняется)
    python collector.py --step export                 # только пересобрать файлы результата

Результат (папка output):
    emails_new.txt   - по одному адресу в строке, лучшие сверху (для бота)
    analytics.csv    - таблица для анализа (открывать в Excel)
    no_email_sites.csv - места с сайтом, но без найденной почты (можно проверить вручную)
"""
import argparse
import csv
import html as htmllib
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

try:
    import dns.resolver
    import dns.exception
except ImportError:  # проверка MX станет необязательной
    dns = None

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "output")
DISCOVERED = os.path.join(DATA_DIR, "discovered.json")
CRAWL_CACHE = os.path.join(DATA_DIR, "crawl_cache.jsonl")

# ---------------------------------------------------------------- настройки
# Штаты и приоритет: 1 - выше шанс ответа (север/озёра/побережье), 3 - ниже
STATES = {
    "MA": 1, "ME": 1, "NH": 1, "VT": 1, "NY": 1, "MI": 1, "WI": 1, "MN": 1, "CT": 1, "RI": 1,
    "PA": 2, "NJ": 2, "OH": 2, "IL": 2, "VA": 2, "MD": 2, "DE": 2, "WA": 2, "OR": 2, "MT": 2,
    "NC": 3, "SC": 3, "GA": 3, "FL": 3,
}
TIER_BONUS = {1: 15, 2: 8, 3: 0}

CATEGORIES = {
    "golf": ['nwr["leisure"="golf_course"]["name"]'],
    "ski": ['nwr["landuse"="winter_sports"]["name"]'],
    "resort": ['nwr["tourism"="resort"]["name"]', 'nwr["tourism"="theme_park"]["name"]'],
    "camp": ['nwr["tourism"="camp_site"]["name"]'],
    "gift": ['nwr["shop"="gift"]["name"]', 'nwr["shop"="souvenir"]["name"]'],  # по умолчанию выключено
}
DEFAULT_CATS = ["golf", "ski", "resort", "camp"]
CAT_BONUS = {"golf": 10, "ski": 10, "resort": 8, "camp": 6, "gift": 3}

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
OVERPASS_HEADERS = {   # Overpass отвечает 406 на браузерные заголовки, ему нужен честный клиент
    "User-Agent": "personal-jobsearch-collector/1.0 (python-requests)",
    "Accept": "*/*",
}
MAX_PAGES = 5          # сколько внутренних страниц смотреть на сайте
MAX_HTML = 1_500_000   # байт
MAX_PER_DOMAIN = 2     # сколько адресов брать с одного сайта

SOCIAL = ("facebook.", "instagram.", "twitter.", "x.com", "linkedin.", "youtube.", "tripadvisor.",
          "yelp.", "google.", "booking.", "airbnb.", "tiktok.", "pinterest.", "yellowpages.")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}")
OBF = [
    (re.compile(r"\s*[\[\(\{<]\s*at\s*[\]\)\}>]\s*", re.I), "@"),
    (re.compile(r"\s*[\[\(\{<]\s*dot\s*[\]\)\}>]\s*", re.I), "."),
]
J1_RE = re.compile(r"\bj-?1\b|international (student|worker|staff|applicant)|work\s*(&|and)?\s*travel|cultural exchange", re.I)
SEASONAL_RE = re.compile(r"seasonal|summer (staff|position|job|employ)|now hiring|we(?:'re| are) hiring", re.I)
HOUSING_RE = re.compile(r"staff housing|employee housing|seasonal housing|dorm|housing (is )?(available|provided)", re.I)

JUNK_DOMAIN_PARTS = ("sentry", "wixpress", "example.", "yourdomain", "domain.com", "godaddy",
                     "squarespace", "email.com", "yoursite", "test.com", "mysite")
JUNK_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".js", ".css", ".woff", ".ico", ".pdf")
BAD_PREFIX = ("noreply", "no-reply", "donotreply", "do-not-reply", "webmaster", "privacy", "abuse",
              "unsubscribe", "postmaster", "mailer-daemon", "legal", "copyright", "dmca", "newsletter")

ROLE_HR = {"hr", "jobs", "job", "careers", "career", "employment", "hiring", "recruit", "recruiting",
           "humanresources", "seasonal", "staffing", "apply", "applications", "payroll"}
ROLE_OPS = {"proshop", "pro", "golf", "gm", "generalmanager", "manager", "director", "superintendent",
            "grounds", "ops", "operations", "fb", "food", "banquet", "banquets", "events", "catering",
            "hospitality", "clubhouse", "head", "pgapro", "outings", "campground", "camping"}
GENERIC = {"info", "contact", "office", "admin", "hello", "mail", "general", "sales", "membership",
           "marketing", "press", "media", "frontdesk", "reception", "service", "customerservice"}
LOW = {"feedback", "support", "reservations", "reservation", "booking", "bookings", "stay", "stays",
       "rooms", "tickets", "guestservices", "concierge"}


# ---------------------------------------------------------------- утилиты
def norm_url(u):
    u = (u or "").strip().split(";")[0].strip()
    if not u:
        return ""
    if not re.match(r"https?://", u, re.I):
        u = "https://" + u
    return u


def host_of(u):
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def decode_cf(hexstr):
    r = int(hexstr[:2], 16)
    return "".join(chr(int(hexstr[i:i + 2], 16) ^ r) for i in range(2, len(hexstr), 2))


def is_junk(email):
    if email.count("@") != 1:
        return True
    local, domain = email.split("@")
    if not local or len(local) > 64 or len(domain) > 120:
        return True
    if domain.endswith(JUNK_EXT) or any(p in domain for p in JUNK_DOMAIN_PARTS):
        return True
    if any(local.startswith(p) for p in BAD_PREFIX):
        return True
    tld = domain.rsplit(".", 1)[-1]
    if not tld.isalpha() or len(tld) > 12:
        return True
    return False


def clean_email(e):
    e = e.strip().strip(".,;:()<>[]\"'").lower()
    e = re.sub(r"^(u00[0-9a-f]{2})+", "", e)  # артефакты JSON вроде u003e
    return e


def extract_emails(html_text):
    """Возвращает множество почт из HTML (mailto, Cloudflare-защита, [at]/[dot], обычный текст)."""
    found = set()
    raw = htmllib.unescape(html_text)
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup.select("[data-cfemail]"):
        try:
            found.add(decode_cf(tag["data-cfemail"]))
        except Exception:
            pass
    for a in soup.find_all("a", href=True):
        if a["href"].lower().startswith("mailto:"):
            found.update(EMAIL_RE.findall(a["href"][7:].split("?")[0]))
    found.update(EMAIL_RE.findall(raw))
    text = soup.get_text(" ")
    for rx, rep in OBF:
        text = rx.sub(rep, text)
    found.update(EMAIL_RE.findall(text))
    out = set()
    for e in found:
        e = clean_email(e)
        if e and not is_junk(e):
            out.add(e)
    return out, soup


def classify(local):
    """Возвращает (тип, баллы) по локальной части адреса."""
    l = local.lower()
    tokens = set(re.split(r"[._\-+]", l)) | {l}
    if tokens & ROLE_HR:
        return "hr/jobs", 50
    if tokens & ROLE_OPS:
        return "ops/manager", 30
    if l in LOW or tokens & LOW:
        return "generic_low", -20
    if tokens & GENERIC:
        return "generic", 0
    if re.fullmatch(r"[a-z]{3,}(\.[a-z]{2,})?", l):
        return "person?", 20
    return "other", 5


# ---------------------------------------------------------------- шаг 1: поиск мест
def build_query(state, cat):
    parts = "\n".join(f"  {f}(area.a);" for f in CATEGORIES[cat])
    return (f'[out:json][timeout:90];\narea["ISO3166-2"="US-{state}"]->.a;\n'
            f'(\n{parts}\n);\nout tags center;')


def overpass(query):
    last = None
    for attempt in range(3):
        for url in MIRRORS:
            name = urlparse(url).netloc
            t0 = time.time()
            print(f"   запрос к {name} (попытка {attempt + 1}) ...", flush=True)
            try:
                r = requests.post(url, data={"data": query}, timeout=(10, 100), headers=OVERPASS_HEADERS)
                if r.status_code == 200:
                    return r.json()
                last = f"{name} -> HTTP {r.status_code}"
            except Exception as e:
                last = f"{name} -> {type(e).__name__}"
            print(f"   не вышло за {time.time() - t0:.0f} c: {last}", flush=True)
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(last)


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def discover(states, cats):
    os.makedirs(DATA_DIR, exist_ok=True)
    db = load_json(DISCOVERED, {"done": [], "places": {}})
    for st in states:
        for cat in cats:
            key = f"{st}|{cat}"
            if key in db["done"]:
                continue
            print(f"[discover] {st} / {cat} ...", flush=True)
            try:
                data = overpass(build_query(st, cat))
            except Exception as e:
                print(f"   ошибка Overpass: {e} (пропускаю, повтори позже)")
                continue
            added = 0
            for el in data.get("elements", []):
                t = el.get("tags", {})
                name = t.get("name", "").strip()
                site = norm_url(t.get("website") or t.get("contact:website") or t.get("url") or "")
                if site and any(s in host_of(site) for s in SOCIAL):
                    site = ""
                osm_email = clean_email(t.get("email") or t.get("contact:email") or "").split(";")[0]
                if not name or not (site or osm_email):
                    continue
                pkey = host_of(site) if site else "mail:" + osm_email.split("@")[-1]
                if pkey in db["places"]:
                    continue
                db["places"][pkey] = {
                    "name": name, "state": st, "category": cat, "website": site,
                    "city": t.get("addr:city", ""), "phone": t.get("phone") or t.get("contact:phone") or "",
                    "osm_email": osm_email,
                }
                added += 1
            db["done"].append(key)
            with open(DISCOVERED, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False)
            print(f"   найдено с сайтом/почтой: {added}")
            time.sleep(5)  # вежливая пауза для Overpass
    print(f"[discover] всего мест в базе: {len(db['places'])}")


# ---------------------------------------------------------------- шаг 2: обход сайтов
def robots_checker(session, base):
    rp = RobotFileParser()
    try:
        r = session.get(urljoin(base, "/robots.txt"), timeout=(5, 8))
        if r.status_code == 200 and "<html" not in r.text[:300].lower():
            rp.parse(r.text.splitlines())
            return lambda u: rp.can_fetch("*", u)
    except Exception:
        pass
    return lambda u: True


def get_page(session, url, allowed):
    if not allowed(url):
        return None, url, "robots"
    try:
        r = session.get(url, timeout=(6, 12), allow_redirects=True)
    except Exception as e:
        return None, url, type(e).__name__
    ctype = r.headers.get("content-type", "").lower()
    if r.status_code != 200:
        return None, r.url, f"http{r.status_code}"
    if "html" not in ctype and "xml" not in ctype:
        return None, r.url, "not_html"
    return r.text[:MAX_HTML], r.url, ""


def pick_links(soup, base_url):
    base_host = host_of(base_url)
    scored = {}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        full = urljoin(base_url, href).split("#")[0]
        if host_of(full) != base_host or full.lower().endswith(JUNK_EXT):
            continue
        hay = (href + " " + a.get_text(" ")).lower()
        if re.search(r"career|job|employ|hiring|work[-\s]?with|join[-\s]?(our|the)?[-\s]?team|apply|opportunit", hay):
            pr = 0
        elif "contact" in hay:
            pr = 1
        elif re.search(r"staff|team|leadership|directory|about|people", hay):
            pr = 2
        else:
            continue
        if full not in scored or pr < scored[full]:
            scored[full] = pr
    return sorted(scored.items(), key=lambda x: x[1])


def process_page(html_text, url, res, kind=None):
    emails, soup = extract_emails(html_text)
    for e in emails:
        res["emails"].setdefault(e, url)
    text = soup.get_text(" ")
    if J1_RE.search(text):
        res["j1"] = True
    if SEASONAL_RE.search(text):
        res["seasonal"] = True
    if HOUSING_RE.search(text):
        res["housing"] = True
    if kind == 0:
        res["jobs_page"] = True
    res["pages"] += 1
    return soup


def crawl_site(place):
    res = {"emails": {}, "jobs_page": False, "seasonal": False, "j1": False,
           "housing": False, "pages": 0, "error": ""}
    base = place["website"]
    if not base:
        return res
    s = requests.Session()
    s.headers.update(HEADERS)
    allowed = robots_checker(s, base)
    html_text, final, err = get_page(s, base, allowed)
    if html_text is None and base.startswith("https://"):
        html_text, final, err = get_page(s, "http://" + base[8:], allowed)
    if html_text is None:
        res["error"] = err
        return res
    soup = process_page(html_text, final, res)
    links = pick_links(soup, final)[:MAX_PAGES]
    if not any(p == 1 for _, p in links):
        links = links[:MAX_PAGES - 1] + [(urljoin(final, "/contact"), 1)]
    for link, pr in links:
        time.sleep(0.4)
        page, furl, _ = get_page(s, link, allowed)
        if page:
            process_page(page, furl, res, kind=0 if pr == 0 else None)
    return res


def crawl(workers):
    db = load_json(DISCOVERED, {"places": {}})
    done = set()
    if os.path.exists(CRAWL_CACHE):
        with open(CRAWL_CACHE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["key"])
                except Exception:
                    pass
    todo = [(k, p) for k, p in db["places"].items() if k not in done and p["website"]]
    # сначала места из приоритетных штатов и категорий
    todo.sort(key=lambda kp: -(TIER_BONUS.get(STATES.get(kp[1]["state"], 3), 0) + CAT_BONUS.get(kp[1]["category"], 0)))
    print(f"[crawl] к обходу: {len(todo)} сайтов (уже в кэше: {len(done)}), потоков: {workers}", flush=True)
    if not todo:
        return
    n = with_mail = 0
    t0 = time.time()
    ex = ThreadPoolExecutor(max_workers=workers)
    futs = {ex.submit(crawl_site, p): k for k, p in todo}
    try:
        with open(CRAWL_CACHE, "a", encoding="utf-8") as cache:
            for fut in as_completed(futs):
                k = futs[fut]
                try:
                    res = fut.result()
                except Exception as e:
                    res = {"emails": {}, "jobs_page": False, "seasonal": False, "j1": False,
                           "housing": False, "pages": 0, "error": type(e).__name__}
                cache.write(json.dumps({"key": k, **res}, ensure_ascii=False) + "\n")
                cache.flush()
                n += 1
                with_mail += 1 if res["emails"] else 0
                if n % 25 == 0 or n == len(todo):
                    el = time.time() - t0
                    eta = el / n * (len(todo) - n)
                    print(f"   {n}/{len(todo)} сайтов, с почтой: {with_mail}, осталось ~{eta / 60:.0f} мин", flush=True)
    except KeyboardInterrupt:
        print("\nОстановлено. Кэш сохранён, при следующем запуске продолжу с этого места.")
        ex.shutdown(wait=False, cancel_futures=True)
        return
    ex.shutdown(wait=True)


# ---------------------------------------------------------------- шаг 3: экспорт
MX_CACHE = {}


def has_mx(domain):
    if dns is None:
        return True
    r = dns.resolver.Resolver()
    r.lifetime = 5
    try:
        r.resolve(domain, "MX")
        return True
    except dns.resolver.NoAnswer:
        try:
            r.resolve(domain, "A")
            return True
        except dns.resolver.NXDOMAIN:
            return False
        except Exception:
            return True
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return True  # таймаут и прочее: не выкидываем


def load_history(path):
    sent_emails, sent_domains = set(), set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "|" in line:
                    e = line.split("|")[1].strip().lower()
                    if "@" in e:
                        sent_emails.add(e)
                        sent_domains.add(e.split("@")[1])
    return sent_emails, sent_domains


def export(history_path, skip_domains=True):
    os.makedirs(OUT_DIR, exist_ok=True)
    db = load_json(DISCOVERED, {"places": {}})
    crawled = {}
    if os.path.exists(CRAWL_CACHE):
        with open(CRAWL_CACHE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    crawled[d["key"]] = d
                except Exception:
                    pass
    sent_emails, sent_domains = load_history(history_path)
    print(f"[export] в истории отправок: {len(sent_emails)} адресов, {len(sent_domains)} доменов")

    rows, no_email = [], []
    for key, p in db["places"].items():
        c = crawled.get(key, {"emails": {}, "jobs_page": False, "seasonal": False, "j1": False,
                              "housing": False, "error": "not_crawled"})
        emails = dict(c.get("emails", {}))
        if p.get("osm_email") and not is_junk(p["osm_email"]):
            emails.setdefault(p["osm_email"], "OpenStreetMap")
        if not emails:
            if p["website"]:
                no_email.append([p["name"], p["category"], p["state"], p["city"], p["website"],
                                 p["phone"], c.get("error", "")])
            continue
        site_domain = host_of(p["website"]) if p["website"] else ""
        for e, src in emails.items():
            local, dom = e.split("@")
            typ, sc = classify(local)
            sc += TIER_BONUS.get(STATES.get(p["state"], 3), 0) + CAT_BONUS.get(p["category"], 0)
            if site_domain and (dom == site_domain or dom.endswith("." + site_domain) or site_domain.endswith("." + dom)):
                sc += 10
            sc += 15 if c.get("jobs_page") else 0
            sc += 10 if c.get("seasonal") else 0
            sc += 25 if c.get("j1") else 0
            sc += 10 if c.get("housing") else 0
            rows.append({"score": sc, "email": e, "type": typ, "name": p["name"], "category": p["category"],
                         "state": p["state"], "city": p["city"], "website": p["website"], "source": src,
                         "jobs_page": int(bool(c.get("jobs_page"))), "seasonal": int(bool(c.get("seasonal"))),
                         "j1": int(bool(c.get("j1"))), "housing": int(bool(c.get("housing"))), "phone": p["phone"]})

    # MX-проверка уникальных доменов
    domains = sorted({r["email"].split("@")[1] for r in rows})
    print(f"[export] проверяю MX у {len(domains)} доменов ...", flush=True)
    with ThreadPoolExecutor(max_workers=20) as ex:
        for d, ok in zip(domains, ex.map(has_mx, domains)):
            MX_CACHE[d] = ok
    rows = [r for r in rows if MX_CACHE.get(r["email"].split("@")[1], True)]

    # дубликаты, уже отправленные, лимит на домен
    rows.sort(key=lambda r: -r["score"])
    seen_e, per_dom, final = set(), {}, []
    for r in rows:
        e = r["email"]
        dom = e.split("@")[1]
        if e in seen_e or e in sent_emails:
            continue
        if skip_domains and dom in sent_domains:
            continue
        if per_dom.get(dom, 0) >= MAX_PER_DOMAIN:
            continue
        seen_e.add(e)
        per_dom[dom] = per_dom.get(dom, 0) + 1
        final.append(r)

    with open(os.path.join(OUT_DIR, "emails_new.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(r["email"] for r in final) + ("\n" if final else ""))
    cols = ["score", "email", "type", "name", "category", "state", "city", "website", "source",
            "jobs_page", "seasonal", "j1", "housing", "phone"]
    with open(os.path.join(OUT_DIR, "analytics.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(final)
    with open(os.path.join(OUT_DIR, "no_email_sites.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "category", "state", "city", "website", "phone", "crawl_error"])
        w.writerows(no_email)

    by_state, by_cat = {}, {}
    for r in final:
        by_state[r["state"]] = by_state.get(r["state"], 0) + 1
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    print(f"[export] готово: {len(final)} новых адресов -> output/emails_new.txt")
    print("   по штатам:", dict(sorted(by_state.items(), key=lambda x: -x[1])))
    print("   по типам:", by_cat)
    print(f"   мест с сайтом, но без почты: {len(no_email)} -> output/no_email_sites.csv")


# ---------------------------------------------------------------- самопроверка
def selftest():
    cf = "42" + "".join(f"{ord(ch) ^ 0x42:02x}" for ch in "hr@testclub.com")
    sample = f"""
    <html><body>
    <a href="mailto:Jobs@Club.com?subject=Hi">apply</a>
    <p>Pro shop: proshop [at] clubgolf [dot] com</p>
    <a class="__cf_email__" data-cfemail="{cf}">[email protected]</a>
    <img src="logo@2x.png"> <span>abc123@sentry.io</span>
    <script>{{"e":"u003einfo2@club.com"}}</script>
    <p>noreply@club.com</p>
    <p>We are hiring seasonal staff. J-1 students welcome. Staff housing available.</p>
    </body></html>"""
    emails, _ = extract_emails(sample)
    expected = {"jobs@club.com", "proshop@clubgolf.com", "hr@testclub.com", "info2@club.com"}
    assert emails == expected, f"получено {emails}"
    res = {"emails": {}, "jobs_page": False, "seasonal": False, "j1": False, "housing": False, "pages": 0, "error": ""}
    process_page(sample, "http://x", res)
    assert res["seasonal"] and res["j1"] and res["housing"]
    assert classify("jobs")[0] == "hr/jobs" and classify("proshop")[0] == "ops/manager"
    assert classify("info")[0] == "generic" and classify("feedback")[0] == "generic_low"
    assert classify("eric")[0] == "person?"
    print("selftest OK:", sorted(emails))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", default="ALL", help="например MA,ME,NH или ALL")
    ap.add_argument("--cats", default=",".join(DEFAULT_CATS), help="golf,ski,resort,camp,gift")
    ap.add_argument("--step", choices=["discover", "crawl", "export", "all"], default="all")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--history", default=os.path.join(BASE_DIR, "sent_history.txt"))
    ap.add_argument("--no-skip-domains", action="store_true",
                    help="не пропускать другие адреса доменов, куда уже писали")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        selftest()
        return
    states = list(STATES) if a.states.upper() == "ALL" else [s.strip().upper() for s in a.states.split(",")]
    bad = [s for s in states if s not in STATES]
    if bad:
        sys.exit(f"Неизвестные штаты: {bad}. Доступны: {list(STATES)}")
    cats = [c.strip() for c in a.cats.split(",")]
    badc = [c for c in cats if c not in CATEGORIES]
    if badc:
        sys.exit(f"Неизвестные категории: {badc}. Доступны: {list(CATEGORIES)}")

    if a.step in ("discover", "all"):
        discover(states, cats)
    if a.step in ("crawl", "all"):
        crawl(a.workers)
    if a.step in ("export", "all"):
        export(a.history, skip_domains=not a.no_skip_domains)


if __name__ == "__main__":
    main()

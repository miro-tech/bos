import re
import socket
import requests
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

URL = "https://gist.githubusercontent.com/Darlene-Alderson-FSOCIETY/81fc656cd0a8298a5aad99c7cfadcd97/raw/BoSVPN_Telegram_RE_s_B.txt"

OUTPUT = "profiles.txt"

REMOVE_ALPN = {
    "h2",
    "http/1.1",
    "h2,http/1.1",
    "http/1.1,h2",
}

cache = {}

text = requests.get(URL, timeout=30).text
lines = text.splitlines()

result = []

for line in lines:
    line = line.strip()

    if not line.startswith("vless://"):
        result.append(line)
        continue

    parts = urlsplit(line)

    netloc = parts.netloc
    m = re.match(r'(.+@)([^:]+)(:\d+)', netloc)
    if m:
        prefix, host, port = m.groups()

        if not re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
            if host not in cache:
                try:
                    cache[host] = socket.gethostbyname(host)
                    print(f"{host} -> {cache[host]}")
                except Exception:
                    cache[host] = host

            netloc = prefix + cache[host] + port

    params = parse_qsl(parts.query, keep_blank_values=True)

    new_params = []
    for k, v in params:
        if k == "alpn" and v in REMOVE_ALPN:
            continue

        if k == "sni":
            v = "rbc.ru"

        new_params.append((k, v))

    new_query = urlencode(new_params)

    result.append(urlunsplit((
        parts.scheme,
        netloc,
        parts.path,
        new_query,
        parts.fragment
    )))

with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(result))

print(f"Saved {len(result)} lines.")

#!/usr/bin/env python3
"""Discord Rich Presence para Stremio, leyendo la interfaz por el puerto de depuración de Qt."""
import json
import re
import time
import urllib.request

from pypresence import Presence, ActivityType
from pypresence.types import StatusDisplayType

CLIENT_ID = "YOUR_DISCORD_APPLICATION_ID"
DEBUG_URL = "http://127.0.0.1:9222/json"
CINEMETA = "https://v3-cinemeta.strem.io/meta/{kind}/{imdb}.json"
POLL_SECONDS = 5

meta_cache = {}


def get_player_page():
    """Devuelve (title, url) de la página del reproductor, o None si no estás en él."""
    try:
        with urllib.request.urlopen(DEBUG_URL, timeout=3) as r:
            pages = json.load(r)
    except Exception:
        return None
    for p in pages:
        if p.get("type") == "page" and "#/player/" in (p.get("url") or ""):
            return p.get("title") or "", p["url"]
    return None


def get_meta(kind, content_id):
    """Nombre y póster desde Cinemeta (solo IDs de IMDb). Devuelve (nombre, póster)."""
    if not content_id.startswith("tt"):
        return None, None
    key = (kind, content_id)
    if key in meta_cache:
        return meta_cache[key]
    result = (None, None)
    try:
        with urllib.request.urlopen(CINEMETA.format(kind=kind, imdb=content_id), timeout=4) as r:
            meta = json.load(r).get("meta", {})
        result = (meta.get("name"), meta.get("poster"))
    except Exception:
        pass
    meta_cache[key] = result
    return result


def describe(title, url):
    """Convierte título y URL de Stremio en los campos de la presencia."""
    title = re.sub(r"^Stremio\s*-\s*", "", title).strip()

    m = re.search(r"#/player/(series|movie)/([^/]+)", url)
    kind = m.group(1) if m else "movie"
    content_id = m.group(2) if m else ""

    name, poster = get_meta(kind, content_id)

    se = re.search(r"\s*\((\d+)x(\d+)\)\s*$", title)
    season, episode = (int(se.group(1)), int(se.group(2))) if se else (None, None)
    if se:
        title = title[:se.start()].strip()

    if season is not None:
        series = name or title
        ep_title = ""
        if name and title.lower().startswith(name.lower()):
            ep_title = title[len(name):].lstrip(" -–:").strip()
        state = f"T{season} · E{episode}"
        if ep_title:
            state += f" — {ep_title}"
        return series[:128], state[:128], poster

    return (name or title or "Stremio")[:128], "Viendo una película", poster


def main():
    rpc = Presence(CLIENT_ID)
    connected = False
    shown = None
    started = None

    while True:
        page = get_player_page()
        current = page if page else None

        try:
            if not connected:
                rpc.connect()
                connected = True
                shown = "__reset__"  # fuerza actualizar al (re)conectar

            if current != shown:
                if current:
                    details, state, poster = describe(*current)
                    started = int(time.time())
                    rpc.update(
                        activity_type=ActivityType.WATCHING,
                        status_display_type=StatusDisplayType.DETAILS,
                        details=details,
                        state=state,
                        start=started,
                        large_image=poster or "stremio",
                        large_text=details,
                        small_image="stremio",
                        small_text="Stremio",
                    )
                else:
                    rpc.clear()
                shown = current
        except Exception:
            # Discord cerrado o socket caído: reintentar en el siguiente ciclo
            connected = False
            try:
                rpc.close()
            except Exception:
                pass
            rpc = Presence(CLIENT_ID)

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()

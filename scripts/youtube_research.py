#!/usr/bin/env python3
"""
YouTube Nischen-Recherche-Tool
==============================
Findet virale Videos in deiner Nische, analysiert Titel, Tags, Hooks
und gibt dir datenbasierte Content-Ideen.

Voraussetzungen:
    pip install google-api-python-client python-dotenv

Setup:
    1. Google Cloud Console -> YouTube Data API v3 aktivieren
    2. API Key erstellen
    3. In .env Datei eintragen: YOUTUBE_API_KEY=dein_key
"""

import os
import json
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

# === DEINE NISCHE: Keywords die recherchiert werden ===
NICHE_KEYWORDS = [
    # Hauptthemen
    "spirituelles coaching",
    "spirituelles erwachen",
    "bewusstsein erweitern",
    "meditation lernen",
    "sinnkrise uberwinden",
    "burnout uberwinden spirituell",
    "lebenskrise hilfe",
    "selbstfindung",
    "inneres kind heilen",
    "energiearbeit lernen",
    # Trending 2026
    "human design deutsch",
    "nervensystem regulieren",
    "manifestation deutsch",
    "chakra heilung",
    "soul coaching",
    "life coaching deutsch",
    # Schmerzpunkte (hohe Kaufmotivation)
    "warum fuhle ich mich leer",
    "midlife crisis mann",
    "midlife crisis frau",
    "berufung finden",
    "toxische beziehung losen",
    "angst uberwinden",
    "selbstzweifel uberwinden",
    "seelenplan erkennen",
]

# Konkurrenz-Kanale zum Beobachten
COMPETITOR_CHANNELS = [
    # Fulle hier die Channel-IDs deiner Konkurrenten ein
    # Format: ("Kanalname", "Channel-ID")
    ("Laura Malina Seiler", "UCxxxxxxxxxx"),  # Ersetze mit echter ID
    ("Veit Lindau", "UCxxxxxxxxxx"),
    # Weitere Konkurrenten hier eintragen
]


def get_youtube_client():
    if not API_KEY:
        print("FEHLER: YOUTUBE_API_KEY nicht in .env gefunden!")
        print("Erstelle eine .env Datei mit: YOUTUBE_API_KEY=dein_api_key")
        return None
    return build("youtube", "v3", developerKey=API_KEY)


def search_viral_videos(youtube, keyword, max_results=20, days_back=30):
    """Sucht nach den erfolgreichsten Videos zu einem Keyword."""
    published_after = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + "Z"

    request = youtube.search().list(
        q=keyword,
        part="snippet",
        type="video",
        order="viewCount",
        publishedAfter=published_after,
        regionCode="DE",
        relevanceLanguage="de",
        maxResults=max_results,
    )
    response = request.execute()

    video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
    if not video_ids:
        return []

    # Detaillierte Video-Statistiken holen
    stats_request = youtube.videos().list(
        part="statistics,snippet,contentDetails",
        id=",".join(video_ids),
    )
    stats_response = stats_request.execute()

    results = []
    for video in stats_response.get("items", []):
        stats = video["statistics"]
        snippet = video["snippet"]
        results.append({
            "video_id": video["id"],
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "published": snippet["publishedAt"][:10],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "description": snippet["description"][:200],
            "tags": snippet.get("tags", [])[:10],
            "url": f"https://youtube.com/watch?v={video['id']}",
            "keyword": keyword,
        })

    results.sort(key=lambda x: x["views"], reverse=True)
    return results


def analyze_hooks(videos):
    """Analysiert die Titel-Hooks der erfolgreichsten Videos."""
    print("\n" + "=" * 60)
    print("HOOK-ANALYSE: Was funktioniert in den Titeln?")
    print("=" * 60)

    hook_patterns = {
        "Zahl im Titel": 0,
        "Frage": 0,
        "Wie/How-to": 0,
        "Warnung/Achtung": 0,
        "Geheimnis/Secret": 0,
        "Transformation/Vorher-Nachher": 0,
        "Sofort/Schnell": 0,
        "Fehler vermeiden": 0,
    }

    for v in videos:
        title = v["title"].lower()
        if any(c.isdigit() for c in v["title"]):
            hook_patterns["Zahl im Titel"] += 1
        if "?" in v["title"]:
            hook_patterns["Frage"] += 1
        if any(w in title for w in ["wie ", "how ", "anleitung", "lernen", "schritt"]):
            hook_patterns["Wie/How-to"] += 1
        if any(w in title for w in ["achtung", "warnung", "gefahr", "vorsicht", "nie"]):
            hook_patterns["Warnung/Achtung"] += 1
        if any(w in title for w in ["geheim", "secret", "keiner kennt", "niemand"]):
            hook_patterns["Geheimnis/Secret"] += 1
        if any(w in title for w in ["verwandl", "transform", "veränder", "vorher", "nachher"]):
            hook_patterns["Transformation/Vorher-Nachher"] += 1
        if any(w in title for w in ["sofort", "schnell", "in nur", "minuten"]):
            hook_patterns["Sofort/Schnell"] += 1
        if any(w in title for w in ["fehler", "falsch", "nicht ", "stop", "aufhören"]):
            hook_patterns["Fehler vermeiden"] += 1

    for pattern, count in sorted(hook_patterns.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"  {pattern:35s} {count:3d}  {bar}")

    return hook_patterns


def find_content_gaps(videos):
    """Findet Themen mit hoher Nachfrage aber wenig Konkurrenz."""
    print("\n" + "=" * 60)
    print("CONTENT-GAP-ANALYSE: Wo ist wenig Konkurrenz?")
    print("=" * 60)

    keyword_stats = {}
    for v in videos:
        kw = v["keyword"]
        if kw not in keyword_stats:
            keyword_stats[kw] = {"total_views": 0, "count": 0, "avg_views": 0}
        keyword_stats[kw]["total_views"] += v["views"]
        keyword_stats[kw]["count"] += 1

    for kw, stats in keyword_stats.items():
        stats["avg_views"] = stats["total_views"] // max(stats["count"], 1)

    # Sortiert nach durchschnittlichen Views (hohe Views = hohe Nachfrage)
    sorted_keywords = sorted(keyword_stats.items(), key=lambda x: x[1]["avg_views"], reverse=True)

    print(f"\n  {'Keyword':<35s} {'Ø Views':>10s} {'Videos':>8s}  Bewertung")
    print("  " + "-" * 75)
    for kw, stats in sorted_keywords:
        avg = stats["avg_views"]
        count = stats["count"]
        # Wenige Videos + viele Views = Content Gap = Chance!
        if avg > 10000 and count < 10:
            rating = "🔥 GOLDENE CHANCE"
        elif avg > 5000:
            rating = "✅ Gutes Potenzial"
        elif avg > 1000:
            rating = "⚡ Machbar"
        else:
            rating = "⏳ Langfristig"
        print(f"  {kw:<35s} {avg:>10,d} {count:>8d}  {rating}")


def generate_video_ideas(top_videos):
    """Generiert konkrete Video-Ideen basierend auf den Top-Performern."""
    print("\n" + "=" * 60)
    print("VIDEO-IDEEN basierend auf Top-Performern")
    print("=" * 60)

    templates = [
        "Die {zahl} wichtigsten Anzeichen für {thema} (und was du tun kannst)",
        "Ich habe {thema} getestet - das ist passiert",
        "{thema}: Der grösste Fehler, den 90% machen",
        "Warum {thema} dein Leben verändern wird (Wissenschaft erklärt)",
        "Von {problem} zu {lösung} - Meine ehrliche Geschichte",
        "{thema} für Anfänger: Alles was du wissen musst in {zahl} Minuten",
        "STOP! Mach das NICHT bei {thema}",
        "So habe ich mit {thema} mein Leben komplett verändert",
        "Was ich gerne über {thema} früher gewusst hätte",
        "{thema}: Was wirklich hilft vs. was Zeitverschwendung ist",
    ]

    used_themes = set()
    for v in top_videos[:20]:
        theme = v["keyword"]
        if theme in used_themes:
            continue
        used_themes.add(theme)
        print(f"\n  Basierend auf: \"{v['title']}\" ({v['views']:,} Views)")
        for t in templates[:3]:
            idea = t.format(
                thema=theme.title(),
                zahl="7",
                problem="Burnout",
                lösung="innerer Frieden",
            )
            print(f"    → {idea}")


def export_results(all_videos, filename="youtube_research_results.csv"):
    """Exportiert alle Ergebnisse als CSV."""
    filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "keyword", "title", "channel", "views", "likes",
            "comments", "published", "url", "tags",
        ])
        writer.writeheader()
        for v in all_videos:
            v_copy = v.copy()
            v_copy["tags"] = ", ".join(v.get("tags", []))
            writer.writerow({k: v_copy.get(k, "") for k in writer.fieldnames})
    print(f"\n✅ Ergebnisse exportiert nach: {filepath}")


def main():
    print("=" * 60)
    print("  YOUTUBE NISCHEN-RECHERCHE TOOL")
    print("  Für: Dirk Traub - Soul Mastery Coaching")
    print("=" * 60)

    youtube = get_youtube_client()
    if not youtube:
        return

    all_videos = []

    for i, keyword in enumerate(NICHE_KEYWORDS):
        print(f"\n[{i+1}/{len(NICHE_KEYWORDS)}] Recherchiere: '{keyword}'...")
        try:
            videos = search_viral_videos(youtube, keyword, max_results=10, days_back=90)
            all_videos.extend(videos)
            if videos:
                top = videos[0]
                print(f"  Top Video: {top['title'][:60]}... ({top['views']:,} Views)")
        except Exception as e:
            print(f"  Fehler bei '{keyword}': {e}")

    if not all_videos:
        print("\nKeine Videos gefunden. Prüfe deinen API Key.")
        return

    # Sortiere alle nach Views
    all_videos.sort(key=lambda x: x["views"], reverse=True)

    # Top 20 anzeigen
    print("\n" + "=" * 60)
    print("TOP 20 VIRALSTE VIDEOS IN DEINER NISCHE")
    print("=" * 60)
    for i, v in enumerate(all_videos[:20]):
        print(f"\n  #{i+1}: {v['title']}")
        print(f"       {v['views']:>10,} Views | {v['likes']:>6,} Likes | {v['channel']}")
        print(f"       {v['url']}")

    # Analysen
    analyze_hooks(all_videos[:50])
    find_content_gaps(all_videos)
    generate_video_ideas(all_videos)
    export_results(all_videos)


if __name__ == "__main__":
    main()

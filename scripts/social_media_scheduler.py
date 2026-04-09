#!/usr/bin/env python3
"""
Social-Media-Posting-Automatisierung
=====================================
Plant, schedulet und postet Content auf YouTube, TikTok und Instagram.

Unterstützte Methoden:
    - YouTube: Direkt via YouTube Data API
    - TikTok: Via TikTok Content Posting API
    - Instagram: Via Instagram Graph API (Business Account nötig)
    - Fallback: Repurpose.io / Buffer / Later Integration

Voraussetzungen:
    pip install google-api-python-client google-auth-oauthlib requests schedule python-dotenv
"""

import os
import sys
import json
import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# === KONFIGURATION ===

POSTING_CONFIG = {
    "youtube": {
        "enabled": True,
        "api_key": os.getenv("YOUTUBE_API_KEY"),
        "client_secrets": os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json"),
        "default_tags": [
            "spirituelles coaching", "soul mastery", "dirk traub",
            "meditation", "bewusstsein", "persönlichkeitsentwicklung",
            "spirituelles erwachen", "life coaching deutsch",
            "sinnkrise", "burnout hilfe",
        ],
        "default_category": "22",  # People & Blogs
        "privacy": "public",
    },
    "tiktok": {
        "enabled": True,
        "access_token": os.getenv("TIKTOK_ACCESS_TOKEN"),
        "max_daily_posts": 3,  # Empfohlen: nicht mehr als 3/Tag
    },
    "instagram": {
        "enabled": True,
        "access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
        "business_account_id": os.getenv("INSTAGRAM_BUSINESS_ID"),
        "max_daily_posts": 2,
    },
}

# === OPTIMALE POSTING-ZEITEN (Deutschland) ===

BEST_POSTING_TIMES = {
    "youtube": {
        "Montag": ["16:00"],
        "Dienstag": ["12:00", "17:00"],
        "Mittwoch": ["16:00"],
        "Donnerstag": ["12:00", "17:00"],
        "Freitag": ["15:00"],
        "Samstag": ["10:00"],
        "Sonntag": ["10:00", "17:00"],
    },
    "tiktok": {
        "Montag": ["07:00", "12:00", "19:00"],
        "Dienstag": ["07:00", "12:00", "19:00"],
        "Mittwoch": ["07:00", "12:00", "19:00"],
        "Donnerstag": ["07:00", "12:00", "21:00"],
        "Freitag": ["07:00", "12:00", "17:00"],
        "Samstag": ["09:00", "12:00", "19:00"],
        "Sonntag": ["09:00", "12:00", "19:00"],
    },
    "instagram": {
        "Montag": ["07:00", "12:00", "19:00"],
        "Dienstag": ["07:00", "12:00", "19:00"],
        "Mittwoch": ["07:00", "12:00", "19:00"],
        "Donnerstag": ["07:00", "12:00", "19:00"],
        "Freitag": ["07:00", "12:00", "17:00"],
        "Samstag": ["09:00", "11:00"],
        "Sonntag": ["09:00", "17:00"],
    },
}


# === SEO-OPTIMIERUNG ===

def optimize_youtube_metadata(title, description, tags=None):
    """Optimiert YouTube-Titel, Beschreibung und Tags für SEO."""

    # Titel-Optimierung
    if len(title) > 70:
        title = title[:67] + "..."

    # Beschreibungs-Template
    seo_description = f"""{description}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 SOUL MASTERY COACHING - Dirk Traub

Du steckst in einer Lebenskrise? Du fühlst dich leer und weißt nicht warum?
Du spürst, dass da MEHR sein muss?

Dann bist du hier richtig.

📌 KOSTENLOSES ERSTGESPRÄCH BUCHEN:
→ https://soulmastery.dirktraub.de

📌 MEIN COACHING-PROGRAMM:
→ [Link zu deinem Programm]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 FOLGE MIR:
→ Instagram: [dein_handle]
→ TikTok: [dein_handle]
→ Webseite: https://www.dirktraub.de

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 KAPITEL:
00:00 - Intro
[Hier Kapitel-Marker einfügen]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#spirituellescoaching #soulmastery #dirktraub #meditation #bewusstsein
#persönlichkeitsentwicklung #spirituelleserwachen #lifecoaching
#sinnkrise #burnout #selbstfindung #achtsamkeit
"""

    # Tags optimieren
    default_tags = POSTING_CONFIG["youtube"]["default_tags"]
    all_tags = list(set((tags or []) + default_tags))[:30]  # YouTube max 30 Tags

    return {
        "title": title,
        "description": seo_description,
        "tags": all_tags,
    }


def optimize_tiktok_caption(topic, hooks=None):
    """Erstellt optimale TikTok-Caption mit Hashtags."""
    caption = f"""{hooks[0] if hooks else topic}

Folge für tägliche Seelen-Impulse 🔮

#spiritualität #coaching #soulmastery #dirktraub #meditation
#bewusstsein #erwachen #fyp #foryou #deutsch #achtsamkeit
#persönlichkeitsentwicklung #lifecoach #transformation #heilung"""

    # TikTok Caption max 2200 Zeichen
    if len(caption) > 2200:
        caption = caption[:2197] + "..."

    return caption


def optimize_instagram_caption(topic, content_type="reel"):
    """Erstellt optimale Instagram-Caption."""

    if content_type == "reel":
        caption = f"""✨ {topic}

Speichere diesen Reel, wenn er dir geholfen hat. 💫

Steckst du gerade in einer Krise und brauchst Unterstützung?
→ Link in Bio für ein kostenloses Erstgespräch

━━━━━━━━━━━━━━━━━━━━━━━━
.
.
.
#spirituellescoaching #soulmastery #meditation #bewusstsein
#persönlichkeitsentwicklung #selbstliebe #achtsamkeit
#spirituelleserwachen #lifecoach #coaching #transformation
#innererfrieden #heilung #sinndeslebens #dirktraub"""

    elif content_type == "karussell":
        caption = f"""Swipe für {topic} 👉

Welcher Punkt resoniert am meisten mit dir? Schreib's in die Kommentare! 💬

Speichere diesen Post für später 🔖

━━━━━━━━━━━━━━━━━━━━━━━━
Folge @[dein_handle] für tägliche Seelen-Impulse ✨

#spirituellescoaching #soulmastery #bewusstsein #meditation
#persönlichkeitsentwicklung #selbstliebe #achtsamkeit
#lifecoaching #coaching #mindset #innereruhe #heilung"""

    return caption


# === YOUTUBE UPLOAD ===

def upload_to_youtube(video_path, title, description, tags=None, privacy="public"):
    """Lädt ein Video auf YouTube hoch."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print("Installiere: pip install google-api-python-client google-auth-oauthlib")
        return None

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    # OAuth2 Flow
    creds_path = Path(__file__).parent.parent / "config" / "youtube_credentials.json"
    token_path = Path(__file__).parent.parent / "config" / "youtube_token.json"

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        secrets_path = Path(__file__).parent.parent / "config" / POSTING_CONFIG["youtube"]["client_secrets"]
        if not secrets_path.exists():
            print(f"❌ Client Secrets nicht gefunden: {secrets_path}")
            print("Erstelle ein OAuth2 Client in Google Cloud Console")
            return None
        flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    youtube = build("youtube", "v3", credentials=creds)

    # Metadaten optimieren
    metadata = optimize_youtube_metadata(title, description, tags)

    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": POSTING_CONFIG["youtube"]["default_category"],
            "defaultLanguage": "de",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"⬆️  Lade hoch: {title}...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}% hochgeladen...")

    video_id = response["id"]
    url = f"https://youtube.com/watch?v={video_id}"
    print(f"✅ YouTube Upload erfolgreich: {url}")
    return url


# === CONTENT-QUEUE ===

class ContentQueue:
    """Verwaltet die Posting-Warteschlange."""

    def __init__(self, queue_file=None):
        if queue_file is None:
            queue_file = Path(__file__).parent.parent / "config" / "posting_queue.json"
        self.queue_file = Path(queue_file)
        self.queue = self._load()

    def _load(self):
        if self.queue_file.exists():
            with open(self.queue_file, encoding="utf-8") as f:
                return json.load(f)
        return {"posts": []}

    def _save(self):
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, ensure_ascii=False, indent=2)

    def add(self, platform, video_path, title, caption, scheduled_time=None):
        """Fügt einen Post zur Queue hinzu."""
        post = {
            "id": len(self.queue["posts"]) + 1,
            "platform": platform,
            "video_path": str(video_path),
            "title": title,
            "caption": caption,
            "scheduled_time": scheduled_time or datetime.now().isoformat(),
            "status": "queued",
            "created_at": datetime.now().isoformat(),
        }
        self.queue["posts"].append(post)
        self._save()
        print(f"📋 Zur Queue hinzugefügt: [{platform}] {title}")
        return post

    def list_pending(self):
        """Zeigt alle anstehenden Posts."""
        pending = [p for p in self.queue["posts"] if p["status"] == "queued"]
        if not pending:
            print("📭 Queue ist leer")
            return []

        print(f"\n📋 POSTING-QUEUE ({len(pending)} anstehend):")
        print("-" * 60)
        for p in sorted(pending, key=lambda x: x["scheduled_time"]):
            print(f"  [{p['platform'].upper():10s}] {p['scheduled_time'][:16]} | {p['title'][:40]}")
        return pending

    def mark_posted(self, post_id):
        """Markiert einen Post als gepostet."""
        for p in self.queue["posts"]:
            if p["id"] == post_id:
                p["status"] = "posted"
                p["posted_at"] = datetime.now().isoformat()
                self._save()
                print(f"✅ Post #{post_id} als gepostet markiert")
                return True
        return False

    def auto_schedule(self, video_dir, days_ahead=14):
        """Plant automatisch alle Videos in einem Ordner ein."""
        video_dir = Path(video_dir)
        videos = sorted(video_dir.glob("*.mp4"))

        if not videos:
            print(f"Keine Videos in {video_dir}")
            return

        current_date = datetime.now()
        post_index = 0

        for day_offset in range(days_ahead):
            date = current_date + timedelta(days=day_offset)
            day_name_de = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
            day_name = day_name_de[date.weekday()]

            for platform in ["tiktok", "instagram", "youtube"]:
                times = BEST_POSTING_TIMES[platform].get(day_name, [])
                for post_time in times:
                    if post_index >= len(videos):
                        break

                    scheduled = date.strftime(f"%Y-%m-%d") + f" {post_time}"
                    video = videos[post_index]

                    self.add(
                        platform=platform,
                        video_path=str(video),
                        title=video.stem.replace("_", " "),
                        caption=f"Soul Mastery Impuls: {video.stem.replace('_', ' ')}",
                        scheduled_time=scheduled,
                    )
                    post_index += 1

        print(f"\n✅ {post_index} Posts geplant für die nächsten {days_ahead} Tage")


# === ANALYTICS TRACKER ===

class AnalyticsTracker:
    """Trackt Performance-Daten deiner Posts."""

    def __init__(self, data_file=None):
        if data_file is None:
            data_file = Path(__file__).parent.parent / "config" / "analytics.json"
        self.data_file = Path(data_file)
        self.data = self._load()

    def _load(self):
        if self.data_file.exists():
            with open(self.data_file, encoding="utf-8") as f:
                return json.load(f)
        return {"posts": [], "weekly_summary": []}

    def _save(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def log_post(self, platform, title, url, views=0, likes=0, comments=0, saves=0, shares=0):
        """Loggt die Performance eines Posts."""
        entry = {
            "date": datetime.now().isoformat(),
            "platform": platform,
            "title": title,
            "url": url,
            "views": views,
            "likes": likes,
            "comments": comments,
            "saves": saves,
            "shares": shares,
            "engagement_rate": round((likes + comments + saves + shares) / max(views, 1) * 100, 2),
        }
        self.data["posts"].append(entry)
        self._save()

    def show_dashboard(self):
        """Zeigt ein Performance-Dashboard."""
        if not self.data["posts"]:
            print("📊 Noch keine Daten vorhanden.")
            return

        print(f"\n{'='*60}")
        print(f"  📊 PERFORMANCE DASHBOARD")
        print(f"{'='*60}")

        # Nach Plattform gruppieren
        platforms = {}
        for post in self.data["posts"]:
            p = post["platform"]
            if p not in platforms:
                platforms[p] = {"views": 0, "likes": 0, "comments": 0, "posts": 0}
            platforms[p]["views"] += post["views"]
            platforms[p]["likes"] += post["likes"]
            platforms[p]["comments"] += post["comments"]
            platforms[p]["posts"] += 1

        print(f"\n  {'Plattform':<15s} {'Posts':>6s} {'Views':>10s} {'Likes':>8s} {'Kommentare':>12s}")
        print("  " + "-" * 55)
        for p, stats in platforms.items():
            print(f"  {p:<15s} {stats['posts']:>6d} {stats['views']:>10,d} {stats['likes']:>8,d} {stats['comments']:>12,d}")

        # Top-Performer
        top = sorted(self.data["posts"], key=lambda x: x["views"], reverse=True)[:5]
        print(f"\n  🏆 TOP 5 POSTS:")
        for i, post in enumerate(top):
            print(f"     #{i+1}: [{post['platform']}] {post['title'][:40]} ({post['views']:,} Views)")


def main():
    if len(sys.argv) < 2:
        print("""
SOCIAL MEDIA SCHEDULER
Soul Mastery - Dirk Traub
===========================

Verwendung:
    python social_media_scheduler.py queue add <plattform> <video> <titel>
    python social_media_scheduler.py queue list
    python social_media_scheduler.py queue auto <video_ordner> [tage]
    python social_media_scheduler.py upload youtube <video> <titel> [beschreibung]
    python social_media_scheduler.py analytics dashboard
    python social_media_scheduler.py analytics log <plattform> <titel> <url> <views> <likes>
    python social_media_scheduler.py times

Plattformen: youtube, tiktok, instagram

Beispiele:
    python social_media_scheduler.py queue auto ./clips/tiktok 14
    python social_media_scheduler.py upload youtube mein_video.mp4 "Burnout überwinden"
    python social_media_scheduler.py analytics dashboard
        """)
        return

    command = sys.argv[1]

    if command == "queue":
        queue = ContentQueue()
        subcommand = sys.argv[2] if len(sys.argv) > 2 else "list"

        if subcommand == "add":
            queue.add(
                platform=sys.argv[3],
                video_path=sys.argv[4],
                title=sys.argv[5],
                caption=sys.argv[6] if len(sys.argv) > 6 else "",
            )
        elif subcommand == "list":
            queue.list_pending()
        elif subcommand == "auto":
            days = int(sys.argv[4]) if len(sys.argv) > 4 else 14
            queue.auto_schedule(sys.argv[3], days)

    elif command == "upload":
        platform = sys.argv[2]
        if platform == "youtube":
            upload_to_youtube(
                video_path=sys.argv[3],
                title=sys.argv[4],
                description=sys.argv[5] if len(sys.argv) > 5 else "",
            )

    elif command == "analytics":
        tracker = AnalyticsTracker()
        subcommand = sys.argv[2] if len(sys.argv) > 2 else "dashboard"

        if subcommand == "dashboard":
            tracker.show_dashboard()
        elif subcommand == "log":
            tracker.log_post(
                platform=sys.argv[3],
                title=sys.argv[4],
                url=sys.argv[5],
                views=int(sys.argv[6]) if len(sys.argv) > 6 else 0,
                likes=int(sys.argv[7]) if len(sys.argv) > 7 else 0,
            )

    elif command == "times":
        print("\n📅 OPTIMALE POSTING-ZEITEN (Deutschland):")
        for platform, times in BEST_POSTING_TIMES.items():
            print(f"\n  {platform.upper()}:")
            for day, slots in times.items():
                print(f"    {day}: {', '.join(slots)}")


if __name__ == "__main__":
    main()

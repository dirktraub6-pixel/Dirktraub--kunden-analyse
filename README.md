# Soul Mastery Automation Toolkit
## Dirk Traub - Coaching Business Automatisierung

Komplettes Automatisierungs-System fur dein Coaching-Business.
Ziel: 1 Million EUR in 12 Monaten durch systematische Content-Produktion und Verkauf.

---

## Ubersicht

```
Dirktraub--kunden-analyse/
├── BEDARFSANALYSE.md              ← Komplette Markt- & Nischenanalyse
├── SALES_FUNNEL_BLUEPRINT.md      ← Sales Funnel & 1-Mio-Fahrplan
├── README.md                      ← Du bist hier
├── requirements.txt               ← Python-Abhangigkeiten
│
├── scripts/
│   ├── youtube_research.py        ← YouTube Nischen-Recherche (virale Videos finden)
│   ├── script_generator.py        ← Video-Script-Generator (Hooks, Frameworks, KI)
│   ├── video_editor.py            ← Video-Editing-Automatisierung (FFmpeg)
│   ├── content_repurposer.py      ← 1 Video → 20+ Content-Stucke
│   └── social_media_scheduler.py  ← Posting-Planung & Analytics
│
├── config/
│   ├── .env.example               ← API-Keys Template (kopiere zu .env)
│   └── posting_queue.json         ← Posting-Warteschlange (auto-generiert)
│
├── generated_scripts/             ← KI-generierte Video-Scripts (auto-generiert)
└── templates/                     ← Vorlagen
```

---

## Schnellstart (15 Minuten Setup)

### Schritt 1: Python-Umgebung einrichten
```bash
cd Dirktraub--kunden-analyse
pip install -r requirements.txt
```

### Schritt 2: FFmpeg installieren
```bash
# Mac
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg

# Windows: Download von https://ffmpeg.org/download.html
```

### Schritt 3: API-Keys einrichten
```bash
cp config/.env.example .env
# Dann .env Datei bearbeiten und API-Keys eintragen
```

**Benotigte API-Keys:**

| API | Wo bekommen | Wofur |
|---|---|---|
| YouTube Data API v3 | [Google Cloud Console](https://console.cloud.google.com/) | Nischen-Recherche & Upload |
| Anthropic API | [console.anthropic.com](https://console.anthropic.com/) | KI-Script-Generierung |
| TikTok API | [TikTok Developer Portal](https://developers.tiktok.com/) | Auto-Posting (optional) |
| Instagram Graph API | [Meta Developer Portal](https://developers.facebook.com/) | Auto-Posting (optional) |

**Minimum zum Starten:** Nur YouTube API Key (kostenlos)

---

## Die 5 Tools im Detail

### 1. YouTube Nischen-Recherche
Findet virale Videos in deiner Nische und analysiert was funktioniert.

```bash
python scripts/youtube_research.py
```

**Was es tut:**
- Durchsucht 25+ Keywords aus deiner Nische
- Zeigt die Top 20 viralsten Videos
- Analysiert Hook-Muster (was funktioniert in Titeln?)
- Findet Content-Gaps (wenig Konkurrenz + hohe Nachfrage)
- Generiert Video-Ideen basierend auf Top-Performern
- Exportiert alles als CSV

### 2. Video-Script-Generator
Erstellt hochkonvertierende Scripts fur alle Plattformen.

```bash
# Manuelles Template
python scripts/script_generator.py generate "Burnout uberwinden" hook_story_offer youtube

# KI-generiertes Script (braucht Anthropic API Key)
python scripts/script_generator.py ai "3 Anzeichen fur spirituelles Erwachen" tiktok_short tiktok

# Hook-Datenbank anzeigen
python scripts/script_generator.py hooks

# Wochen-Content-Plan anzeigen
python scripts/script_generator.py calendar

# Content-Serien anzeigen
python scripts/script_generator.py series
```

**Frameworks:**
- `hook_story_offer` - Bestes fur Coaching-Verkauf
- `aida` - Klassisches Marketing
- `pas` - Fur Schmerzpunkt-Videos
- `tiktok_short` - Kurz & viral

### 3. Video-Editor Automatisierung
Schneidet und konvertiert Videos fur alle Plattformen.

```bash
# Fur TikTok konvertieren (9:16 Format)
python scripts/video_editor.py convert mein_video.mp4 tiktok

# Clip ausschneiden
python scripts/video_editor.py cut mein_video.mp4 30 90 "Bester_Tipp" tiktok

# Untertitel einbrennen
python scripts/video_editor.py subtitles mein_video.mp4 untertitel.srt modern

# Wasserzeichen
python scripts/video_editor.py watermark mein_video.mp4 bottom_right

# Thumbnail erstellen
python scripts/video_editor.py thumbnail mein_video.mp4 00:00:05 "BURNOUT LOSWERDEN"

# Komplette Pipeline (alles auf einmal)
python scripts/video_editor.py pipeline mein_video.mp4

# Batch: Ganzen Ordner verarbeiten
python scripts/video_editor.py batch ./raw_videos tiktok,instagram_reel
```

### 4. Content Repurposer
Macht aus 1 YouTube-Video uber 20 Content-Stucke.

```bash
python scripts/content_repurposer.py mein_coaching_video.mp4
```

**Was automatisch passiert:**
1. Audio wird extrahiert
2. Transkription (mit Whisper oder manuell)
3. KI findet die besten Stellen fur Clips
4. 6-12 TikTok/Reels/Shorts werden geschnitten
5. Karussell-Posts, Zitate, Newsletter, Blogpost werden generiert
6. Thumbnails werden erstellt
7. Posting-Plan wird erstellt

### 5. Social Media Scheduler
Plant und trackt deine Posts.

```bash
# Posting-Zeiten anzeigen
python scripts/social_media_scheduler.py times

# Clips automatisch einplanen (nachste 14 Tage)
python scripts/social_media_scheduler.py queue auto ./clips/tiktok 14

# Queue anzeigen
python scripts/social_media_scheduler.py queue list

# YouTube Upload
python scripts/social_media_scheduler.py upload youtube video.mp4 "Mein Titel"

# Performance tracken
python scripts/social_media_scheduler.py analytics dashboard
```

---

## Typischer Workflow (Wochentlich)

### Montag: Recherche (30 Min)
```bash
python scripts/youtube_research.py
# → Analysiere Ergebnisse, wahle 2-3 Video-Themen
```

### Dienstag: Scripts schreiben (45 Min)
```bash
python scripts/script_generator.py ai "Dein Thema" hook_story_offer youtube
python scripts/script_generator.py ai "Kurzes Thema" tiktok_short tiktok
```

### Mittwoch: Videos aufnehmen (2-3 Stunden)
- 1 YouTube Long-Form Video (10-15 Min)
- 3-5 TikTok Clips (30-60 Sek)

### Donnerstag: Automatisierung laufen lassen (15 Min)
```bash
# Long-Form Video → 20+ Content-Stucke
python scripts/content_repurposer.py youtube_video.mp4

# Alles fur die Woche einplanen
python scripts/social_media_scheduler.py queue auto ./repurposed_youtube_video/tiktok 7
```

### Freitag-Sonntag: Community Management
- Kommentare beantworten
- Stories posten (Behind the Scenes)
- Live Q&A (Sonntag)

**Zeitaufwand pro Woche: ca. 5-8 Stunden**
**Content-Output: 15-25 Posts auf 3 Plattformen**

---

## Nachste Schritte

1. **JETZT:** `pip install -r requirements.txt` und API-Keys einrichten
2. **HEUTE:** Erste YouTube-Recherche durchfuhren
3. **DIESE WOCHE:** Erstes Script generieren und Video aufnehmen
4. **DIESER MONAT:** Content-Repurposing-Pipeline einmal komplett durchlaufen

Bei Fragen: Starte eine neue Claude Code Session und frage!

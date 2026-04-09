#!/usr/bin/env python3
"""
Content-Repurposing-System
===========================
Automatisiert die Wiederverwendung von Content über alle Plattformen.
Ein YouTube-Video wird zu 10+ Content-Stücken.

1 YouTube Long-Form Video (15 Min) wird zu:
    → 6-12 TikTok/Shorts Clips
    → 6-12 Instagram Reels
    → 3-5 Instagram Karussell-Posts (aus Transkript)
    → 10+ Instagram Stories
    → 1 Blog-Post (SEO)
    → 1 Newsletter
    → 20+ Zitate/Text-Posts

Voraussetzungen:
    pip install anthropic openai-whisper python-dotenv moviepy
    + FFmpeg installiert
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class ContentRepurposer:
    """Verwandelt 1 Video in 20+ Content-Stücke."""

    def __init__(self, video_path):
        self.video_path = Path(video_path)
        self.project_dir = self.video_path.parent / f"repurposed_{self.video_path.stem}"
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Unterordner
        self.dirs = {
            "clips": self.project_dir / "clips",
            "tiktok": self.project_dir / "tiktok",
            "reels": self.project_dir / "reels",
            "shorts": self.project_dir / "shorts",
            "karussell": self.project_dir / "karussell",
            "stories": self.project_dir / "stories",
            "text": self.project_dir / "text_content",
            "audio": self.project_dir / "audio",
            "thumbnails": self.project_dir / "thumbnails",
        }
        for d in self.dirs.values():
            d.mkdir(parents=True, exist_ok=True)

        self.transcript = None
        self.highlights = []

    def step1_extract_audio(self):
        """Extrahiert Audio aus dem Video."""
        print("\n[1/7] Audio extrahieren...")
        audio_path = self.dirs["audio"] / f"{self.video_path.stem}.wav"

        cmd = [
            "ffmpeg", "-y",
            "-i", str(self.video_path),
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            str(audio_path),
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"  ✅ Audio: {audio_path}")
        return audio_path

    def step2_transcribe(self, audio_path):
        """Transkribiert das Audio mit Whisper."""
        print("\n[2/7] Transkription erstellen...")

        try:
            import whisper
            model = whisper.load_model("medium")
            result = model.transcribe(
                str(audio_path),
                language="de",
                verbose=False,
            )

            self.transcript = result

            # Transkript speichern
            txt_path = self.dirs["text"] / "transkript.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(result["text"])

            # SRT speichern
            srt_path = self.dirs["text"] / "untertitel.srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, seg in enumerate(result["segments"]):
                    start = self._format_timestamp(seg["start"])
                    end = self._format_timestamp(seg["end"])
                    f.write(f"{i+1}\n{start} --> {end}\n{seg['text'].strip()}\n\n")

            print(f"  ✅ Transkript: {txt_path}")
            print(f"  ✅ Untertitel: {srt_path}")
            return result

        except ImportError:
            print("  ⚠️  Whisper nicht installiert: pip install openai-whisper")
            print("  Alternativ: Lade Transkript manuell hoch als 'transkript.txt'")

            # Versuche manuelles Transkript zu laden
            manual_txt = self.video_path.with_suffix(".txt")
            if manual_txt.exists():
                with open(manual_txt, encoding="utf-8") as f:
                    self.transcript = {"text": f.read(), "segments": []}
                print(f"  ✅ Manuelles Transkript geladen: {manual_txt}")
                return self.transcript

            return None

    def step3_find_highlights(self):
        """Findet die besten Stellen im Video für Clips (mit KI oder manuell)."""
        print("\n[3/7] Highlights identifizieren...")

        if not self.transcript:
            print("  ⚠️  Kein Transkript vorhanden. Definiere Highlights manuell.")
            return self._manual_highlights()

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            prompt = f"""Analysiere dieses Transkript eines spirituellen Coaching-Videos von Dirk Traub.

TRANSKRIPT:
{self.transcript['text'][:8000]}

Finde die 8-12 BESTEN Stellen für TikTok/Reels Clips (30-60 Sekunden).
Kriterien für gute Clips:
1. Starker emotionaler Hook in den ersten 3 Sekunden
2. Eine klare Botschaft/Tipp pro Clip
3. Eigenständig verständlich (ohne Kontext)
4. Viral-Potenzial (kontrovers, überraschend, emotional)
5. Endet mit einem starken Statement

Gib mir für jeden Clip:
- Ungefährer Start-Zeitpunkt im Transkript (in Sekunden)
- Ungefähre Dauer (30-60 Sek)
- Vorgeschlagener Titel für TikTok
- Hook (erster Satz des Clips)
- 3 Hashtags
- Viral-Score (1-10)

Antworte als JSON-Array."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            # Versuche JSON zu parsen
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                self.highlights = json.loads(response_text[json_start:json_end])
                print(f"  ✅ {len(self.highlights)} Highlights gefunden")

                for i, h in enumerate(self.highlights):
                    score = h.get("viral_score", h.get("Viral-Score", "?"))
                    title = h.get("titel", h.get("title", h.get("Titel", "Clip")))
                    print(f"     #{i+1}: {title} (Viral-Score: {score})")

                # Highlights speichern
                with open(self.dirs["text"] / "highlights.json", "w", encoding="utf-8") as f:
                    json.dump(self.highlights, f, ensure_ascii=False, indent=2)

                return self.highlights
            else:
                print("  ⚠️  KI-Antwort konnte nicht geparst werden")
                return self._manual_highlights()

        except (ImportError, Exception) as e:
            print(f"  ⚠️  KI-Analyse fehlgeschlagen: {e}")
            return self._manual_highlights()

    def step4_cut_clips(self):
        """Schneidet die Highlight-Clips aus dem Video."""
        print("\n[4/7] Clips schneiden...")

        if not self.highlights:
            print("  ⚠️  Keine Highlights definiert. Überspringe.")
            return []

        clips = []
        for i, h in enumerate(self.highlights):
            start = h.get("start", h.get("start_sekunden", i * 60))
            duration = h.get("duration", h.get("dauer", 45))
            title = h.get("titel", h.get("title", f"clip_{i+1}"))
            safe_title = title.replace(" ", "_").replace("/", "_")[:40]

            for platform, specs in [("tiktok", "1080:1920"), ("shorts", "1080:1920"), ("reels", "1080:1920")]:
                output = self.dirs[platform] / f"{i+1:02d}_{safe_title}.mp4"

                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(start),
                    "-i", str(self.video_path),
                    "-t", str(duration),
                    "-vf", f"scale=-1:1920,crop=1080:1920",
                    "-c:v", "libx264", "-preset", "medium",
                    "-b:v", "6M",
                    "-c:a", "aac", "-b:a", "128k",
                    "-r", "30",
                    "-movflags", "+faststart",
                    str(output),
                ]
                subprocess.run(cmd, capture_output=True)
                clips.append(output)

            print(f"  ✅ Clip {i+1}: {title}")

        print(f"\n  ✅ {len(clips)} Clips erstellt")
        return clips

    def step5_generate_text_content(self):
        """Generiert Text-Content aus dem Transkript."""
        print("\n[5/7] Text-Content generieren...")

        if not self.transcript:
            print("  ⚠️  Kein Transkript. Überspringe.")
            return

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            prompt = f"""Basierend auf diesem Coaching-Video-Transkript von Dirk Traub (Soul Mastery Coaching),
erstelle folgende Content-Stücke:

TRANSKRIPT:
{self.transcript['text'][:8000]}

Erstelle:

1. **INSTAGRAM KARUSSELL-POST** (5-7 Slides):
   - Slide 1: Hook (eine Frage oder Statement)
   - Slides 2-6: Je 1 Kernaussage/Tipp (kurz, maximal 2 Sätze)
   - Letzte Slide: CTA ("Speichere diesen Post" / "Folge für mehr")
   - Caption mit 5 Hashtags

2. **20 ZITATE** aus dem Video:
   - Kurze, kraftvolle Aussagen (1-2 Sätze)
   - Perfekt für Text-Posts, Stories, Zitat-Grafiken

3. **NEWSLETTER-TEXT** (300-500 Wörter):
   - Persönlich, wie ein Brief an einen Freund
   - Kernbotschaft des Videos + CTA zum Video

4. **BLOG-POST** (800-1200 Wörter):
   - SEO-optimiert mit H2/H3 Überschriften
   - Keywords: spirituelles coaching, [thema des videos]
   - Interne Verlinkung zu Coaching-Angebot

5. **3 INSTAGRAM STORY-TEXTE**:
   - Kurze Impulse mit Umfragen/Fragen

Schreibe alles auf Deutsch, authentisch, nicht verkäuferisch."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=6000,
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text

            # In Dateien speichern
            output_file = self.dirs["text"] / "generated_content.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Generated Content: {self.video_path.stem}\n")
                f.write(f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
                f.write(content)

            print(f"  ✅ Text-Content: {output_file}")
            return content

        except Exception as e:
            print(f"  ⚠️  Text-Generierung fehlgeschlagen: {e}")
            print("  Tipp: ANTHROPIC_API_KEY in .env setzen")
            return None

    def step6_generate_thumbnails(self):
        """Generiert Thumbnails für alle Clips."""
        print("\n[6/7] Thumbnails generieren...")

        count = 0
        for clip_dir in [self.dirs["tiktok"], self.dirs["shorts"], self.dirs["reels"]]:
            for clip in clip_dir.glob("*.mp4"):
                thumb = self.dirs["thumbnails"] / f"{clip.stem}_thumb.jpg"
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", "2",
                    "-i", str(clip),
                    "-vframes", "1",
                    "-q:v", "2",
                    str(thumb),
                ]
                subprocess.run(cmd, capture_output=True)
                count += 1

        print(f"  ✅ {count} Thumbnails generiert")

    def step7_create_posting_plan(self):
        """Erstellt einen Posting-Plan für alle generierten Inhalte."""
        print("\n[7/7] Posting-Plan erstellen...")

        plan = {
            "video_quelle": str(self.video_path),
            "erstellt_am": datetime.now().isoformat(),
            "content_stuecke": {},
        }

        # Alle generierten Dateien inventarisieren
        for platform, directory in self.dirs.items():
            files = list(directory.glob("*.*"))
            if files:
                plan["content_stuecke"][platform] = [
                    {"datei": str(f.name), "status": "geplant"}
                    for f in files if not f.name.startswith(".")
                ]

        # Posting-Zeitplan vorschlagen
        plan["posting_zeitplan"] = [
            {"tag": "Tag 1", "plattform": "YouTube", "content": "Original Long-Form Video"},
            {"tag": "Tag 1", "plattform": "Instagram", "content": "Ankündigungs-Story + Karussell"},
            {"tag": "Tag 2", "plattform": "TikTok", "content": "Bester Clip (höchster Viral-Score)"},
            {"tag": "Tag 2", "plattform": "Instagram", "content": "Reel (Clip #1)"},
            {"tag": "Tag 3", "plattform": "TikTok", "content": "Clip #2"},
            {"tag": "Tag 3", "plattform": "YouTube", "content": "Short (Clip #2)"},
            {"tag": "Tag 4", "plattform": "Instagram", "content": "Karussell-Post (Tipps aus Video)"},
            {"tag": "Tag 4", "plattform": "TikTok", "content": "Clip #3"},
            {"tag": "Tag 5", "plattform": "TikTok", "content": "Clip #4"},
            {"tag": "Tag 5", "plattform": "Instagram", "content": "Reel (Clip #3) + Zitat-Story"},
            {"tag": "Tag 6", "plattform": "TikTok", "content": "Clip #5"},
            {"tag": "Tag 6", "plattform": "Newsletter", "content": "E-Mail mit Video-Link"},
            {"tag": "Tag 7", "plattform": "TikTok", "content": "Clip #6 (Behind the Scenes)"},
            {"tag": "Tag 7", "plattform": "Blog", "content": "SEO-Blogpost veröffentlichen"},
        ]

        plan_path = self.project_dir / "posting_plan.json"
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)

        print(f"  ✅ Posting-Plan: {plan_path}")

        # Zusammenfassung
        total = sum(len(files) for files in plan["content_stuecke"].values())
        print(f"\n{'='*60}")
        print(f"  REPURPOSING ABGESCHLOSSEN!")
        print(f"  {total} Content-Stücke aus 1 Video erstellt:")
        for platform, files in plan["content_stuecke"].items():
            print(f"    {platform}: {len(files)} Dateien")
        print(f"\n  Output: {self.project_dir}")
        print(f"{'='*60}")

        return plan

    def run_full_pipeline(self):
        """Führt die komplette Repurposing-Pipeline aus."""
        print(f"\n{'='*60}")
        print(f"  CONTENT REPURPOSING PIPELINE")
        print(f"  Video: {self.video_path.name}")
        print(f"  1 Video → 20+ Content-Stücke")
        print(f"{'='*60}")

        audio = self.step1_extract_audio()
        self.step2_transcribe(audio)
        self.step3_find_highlights()
        self.step4_cut_clips()
        self.step5_generate_text_content()
        self.step6_generate_thumbnails()
        self.step7_create_posting_plan()

    def _manual_highlights(self):
        """Fallback: Manuelle Highlight-Definition."""
        print("  Erstelle Standard-Highlights (alle 60 Sekunden)...")
        info_cmd = [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "json",
            str(self.video_path),
        ]
        result = subprocess.run(info_cmd, capture_output=True, text=True)
        try:
            duration = float(json.loads(result.stdout)["format"]["duration"])
        except (json.JSONDecodeError, KeyError):
            duration = 600  # Fallback: 10 Minuten

        self.highlights = []
        for i in range(0, int(duration) - 45, 60):
            self.highlights.append({
                "start": i,
                "duration": 45,
                "titel": f"Clip_{i//60 + 1}",
                "viral_score": 5,
            })

        print(f"  ✅ {len(self.highlights)} Standard-Clips definiert")
        return self.highlights

    @staticmethod
    def _format_timestamp(seconds):
        """Konvertiert Sekunden zu SRT-Zeitformat."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main():
    if len(sys.argv) < 2:
        print("""
CONTENT REPURPOSING SYSTEM
Soul Mastery - Dirk Traub
===========================

Verwandelt 1 YouTube-Video in 20+ Content-Stücke für alle Plattformen.

Verwendung:
    python content_repurposer.py <video_datei>
    python content_repurposer.py <video_datei> --step <nummer>

Steps:
    1 = Audio extrahieren
    2 = Transkribieren (Whisper)
    3 = Highlights finden (KI)
    4 = Clips schneiden
    5 = Text-Content generieren
    6 = Thumbnails erstellen
    7 = Posting-Plan erstellen

Beispiel:
    python content_repurposer.py mein_coaching_video.mp4
        """)
        return

    video_path = sys.argv[1]
    repurposer = ContentRepurposer(video_path)

    if "--step" in sys.argv:
        step = int(sys.argv[sys.argv.index("--step") + 1])
        if step == 1:
            repurposer.step1_extract_audio()
        elif step == 2:
            audio = repurposer.step1_extract_audio()
            repurposer.step2_transcribe(audio)
        elif step == 3:
            audio = repurposer.step1_extract_audio()
            repurposer.step2_transcribe(audio)
            repurposer.step3_find_highlights()
        # usw.
    else:
        repurposer.run_full_pipeline()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Video-Editing-Automatisierung
==============================
Schneidet, formatiert und optimiert Videos automatisch für alle Plattformen.
Erstellt professionelle Shorts/Reels aus Long-Form-Content.

Voraussetzungen:
    pip install moviepy Pillow python-dotenv
    + FFmpeg muss installiert sein: sudo apt install ffmpeg (Linux) / brew install ffmpeg (Mac)

Funktionen:
    - YouTube Long-Form → TikTok/Reels Shorts schneiden
    - Automatische Untertitel (SRT → Burned-in Captions)
    - Intro/Outro anhängen
    - Branding (Logo-Wasserzeichen, Farben)
    - Batch-Processing: Mehrere Videos auf einmal
    - Audio-Normalisierung
    - Thumbnail-Generierung
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# === BRANDING-EINSTELLUNGEN ===

BRAND_CONFIG = {
    "name": "Soul Mastery - Dirk Traub",
    "colors": {
        "primary": "#2D1B69",       # Tiefes Violett (Spiritualität)
        "secondary": "#E8B86D",     # Warmes Gold (Premium)
        "accent": "#4ECDC4",        # Türkis (Heilung)
        "text_light": "#FFFFFF",
        "text_dark": "#1A1A2E",
        "background": "#0F0F1A",    # Dunkles Nacht-Blau
    },
    "fonts": {
        "title": "Montserrat-Bold",
        "body": "OpenSans-Regular",
        "accent": "PlayfairDisplay-Italic",
    },
    # Pfade zu deinen Assets (anpassen!)
    "logo_path": "assets/logo.png",
    "intro_video": "assets/intro.mp4",
    "outro_video": "assets/outro.mp4",
    "watermark": "assets/watermark.png",
    "music_bed": "assets/ambient_music.mp3",
}

# === PLATTFORM-FORMATE ===

PLATFORM_SPECS = {
    "youtube": {
        "width": 1920,
        "height": 1080,
        "aspect": "16:9",
        "max_duration": None,
        "fps": 30,
        "bitrate": "8M",
        "audio_bitrate": "192k",
    },
    "youtube_shorts": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "max_duration": 60,
        "fps": 30,
        "bitrate": "6M",
        "audio_bitrate": "128k",
    },
    "tiktok": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "max_duration": 180,
        "fps": 30,
        "bitrate": "6M",
        "audio_bitrate": "128k",
    },
    "instagram_reel": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "max_duration": 90,
        "fps": 30,
        "bitrate": "6M",
        "audio_bitrate": "128k",
    },
    "instagram_feed": {
        "width": 1080,
        "height": 1080,
        "aspect": "1:1",
        "max_duration": 60,
        "fps": 30,
        "bitrate": "4M",
        "audio_bitrate": "128k",
    },
}


def run_ffmpeg(cmd, description=""):
    """Führt einen FFmpeg-Befehl aus mit Fehlerbehandlung."""
    print(f"  ⚙️  {description}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ❌ Fehler: {result.stderr[:200]}")
        return False
    print(f"  ✅ {description} abgeschlossen")
    return True


def get_video_info(input_path):
    """Holt Video-Metadaten mit FFprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(input_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def convert_for_platform(input_path, platform, output_dir=None):
    """Konvertiert ein Video für eine bestimmte Plattform."""
    specs = PLATFORM_SPECS[platform]
    input_path = Path(input_path)

    if output_dir is None:
        output_dir = input_path.parent / "output" / platform
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{input_path.stem}_{platform}_{timestamp}.mp4"

    # Video-Info holen
    info = get_video_info(input_path)
    if not info:
        print(f"❌ Kann Video nicht lesen: {input_path}")
        return None

    # FFmpeg-Kommando bauen
    filters = []

    # Skalierung und Cropping basierend auf Zielformat
    if specs["aspect"] == "9:16":
        # Landscape → Portrait: Center-Crop
        filters.append(f"scale=-1:{specs['height']}")
        filters.append(f"crop={specs['width']}:{specs['height']}")
    elif specs["aspect"] == "1:1":
        # Zu Quadrat croppen
        filters.append(f"scale=-1:{specs['height']}")
        filters.append(f"crop={specs['width']}:{specs['height']}")
    else:
        # Standard Skalierung
        filters.append(f"scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease")
        filters.append(f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2:color=black")

    filter_str = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", filter_str,
        "-c:v", "libx264",
        "-preset", "medium",
        "-b:v", specs["bitrate"],
        "-c:a", "aac",
        "-b:a", specs["audio_bitrate"],
        "-r", str(specs["fps"]),
        "-movflags", "+faststart",
    ]

    # Maximale Dauer beschränken
    if specs["max_duration"]:
        cmd.extend(["-t", str(specs["max_duration"])])

    cmd.append(str(output_path))

    success = run_ffmpeg(cmd, f"Konvertiere für {platform}")
    return output_path if success else None


def cut_segments(input_path, segments, platform="tiktok", output_dir=None):
    """
    Schneidet mehrere Segmente aus einem Video.

    segments: Liste von (start_sek, end_sek, titel) Tupeln
    Beispiel: [(30, 90, "Hook_Burnout"), (120, 180, "Tipp_Meditation")]
    """
    input_path = Path(input_path)
    specs = PLATFORM_SPECS[platform]

    if output_dir is None:
        output_dir = input_path.parent / "clips" / platform
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, (start, end, title) in enumerate(segments):
        duration = end - start

        # Maximale Dauer prüfen
        if specs["max_duration"] and duration > specs["max_duration"]:
            print(f"  ⚠️  Segment '{title}' ist {duration}s - kürze auf {specs['max_duration']}s")
            duration = specs["max_duration"]

        safe_title = title.replace(" ", "_").replace("/", "_")
        output_path = output_dir / f"{i+1:02d}_{safe_title}_{platform}.mp4"

        # Filter für vertikales Format
        filters = []
        if specs["aspect"] == "9:16":
            filters.append(f"scale=-1:{specs['height']}")
            filters.append(f"crop={specs['width']}:{specs['height']}")
        filter_str = ",".join(filters) if filters else f"scale={specs['width']}:{specs['height']}"

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", str(input_path),
            "-t", str(duration),
            "-vf", filter_str,
            "-c:v", "libx264",
            "-preset", "medium",
            "-b:v", specs["bitrate"],
            "-c:a", "aac",
            "-b:a", specs["audio_bitrate"],
            "-r", str(specs["fps"]),
            "-movflags", "+faststart",
            str(output_path),
        ]

        success = run_ffmpeg(cmd, f"Schneide Clip {i+1}: '{title}' ({start}s-{end}s)")
        if success:
            results.append(output_path)

    print(f"\n✅ {len(results)}/{len(segments)} Clips erstellt in: {output_dir}")
    return results


def add_subtitles(input_path, srt_path, output_path=None, style="modern"):
    """Brennt Untertitel ins Video (Burned-in Captions)."""
    input_path = Path(input_path)
    srt_path = Path(srt_path)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_subtitled{input_path.suffix}"

    # Untertitel-Styles
    styles = {
        "modern": (
            f"FontName=Montserrat Bold,FontSize=22,PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,BackColour=&H80000000,"
            f"Outline=2,Shadow=1,MarginV=60,Alignment=2"
        ),
        "bold": (
            f"FontName=Impact,FontSize=26,PrimaryColour=&H0000FFFF,"
            f"OutlineColour=&H00000000,BackColour=&H80000000,"
            f"Outline=3,Shadow=2,MarginV=50,Alignment=2"
        ),
        "minimal": (
            f"FontName=Helvetica,FontSize=20,PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00333333,BackColour=&H00000000,"
            f"Outline=1,Shadow=0,MarginV=40,Alignment=2"
        ),
    }

    style_str = styles.get(style, styles["modern"])

    # FFmpeg-Befehl - SRT-Pfad muss escaped werden
    srt_escaped = str(srt_path).replace(":", "\\:").replace("'", "\\'")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", f"subtitles='{srt_escaped}':force_style='{style_str}'",
        "-c:v", "libx264",
        "-preset", "medium",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]

    success = run_ffmpeg(cmd, "Untertitel einbrennen")
    return output_path if success else None


def add_watermark(input_path, watermark_path=None, position="bottom_right", opacity=0.3, output_path=None):
    """Fügt ein Logo/Wasserzeichen hinzu."""
    input_path = Path(input_path)
    if watermark_path is None:
        watermark_path = Path(__file__).parent.parent / BRAND_CONFIG["watermark"]

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_branded{input_path.suffix}"

    positions = {
        "top_left": "10:10",
        "top_right": "main_w-overlay_w-10:10",
        "bottom_left": "10:main_h-overlay_h-10",
        "bottom_right": "main_w-overlay_w-10:main_h-overlay_h-10",
        "center": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
    }

    pos = positions.get(position, positions["bottom_right"])

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-i", str(watermark_path),
        "-filter_complex",
        f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[watermark];[0:v][watermark]overlay={pos}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]

    success = run_ffmpeg(cmd, "Wasserzeichen hinzufügen")
    return output_path if success else None


def concat_videos(video_paths, output_path):
    """Verbindet mehrere Videos (z.B. Intro + Content + Outro)."""
    # Erstelle temporäre Dateiliste
    list_path = Path(output_path).parent / "_concat_list.txt"
    with open(list_path, "w") as f:
        for vp in video_paths:
            f.write(f"file '{vp}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_path),
        "-c:v", "libx264",
        "-preset", "medium",
        "-c:a", "aac",
        "-movflags", "+faststart",
        str(output_path),
    ]

    success = run_ffmpeg(cmd, "Videos zusammenfügen")
    list_path.unlink(missing_ok=True)
    return output_path if success else None


def normalize_audio(input_path, output_path=None, target_loudness=-16):
    """Normalisiert die Audio-Lautstärke (EBU R128)."""
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_normalized{input_path.suffix}"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", f"loudnorm=I={target_loudness}:TP=-1.5:LRA=11",
        "-c:v", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]

    success = run_ffmpeg(cmd, "Audio normalisieren")
    return output_path if success else None


def generate_thumbnail(input_path, timestamp="00:00:05", output_path=None, add_text=None):
    """Extrahiert einen Frame als Thumbnail und fügt optional Text hinzu."""
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_thumb.jpg"

    filters = ["scale=1920:1080"]

    if add_text:
        # Text-Overlay für Thumbnail
        colors = BRAND_CONFIG["colors"]
        text_escaped = add_text.replace("'", "\\'").replace(":", "\\:")
        filters.append(
            f"drawtext=text='{text_escaped}'"
            f":fontsize=72:fontcolor={colors['text_light']}"
            f":borderw=4:bordercolor={colors['primary']}"
            f":x=(w-text_w)/2:y=(h-text_h)/2"
        )

    cmd = [
        "ffmpeg", "-y",
        "-ss", timestamp,
        "-i", str(input_path),
        "-vframes", "1",
        "-vf", ",".join(filters),
        "-q:v", "2",
        str(output_path),
    ]

    success = run_ffmpeg(cmd, "Thumbnail generieren")
    return output_path if success else None


def batch_process(input_dir, platforms=None):
    """Verarbeitet alle Videos in einem Ordner für alle Plattformen."""
    if platforms is None:
        platforms = ["youtube_shorts", "tiktok", "instagram_reel"]

    input_dir = Path(input_dir)
    video_files = list(input_dir.glob("*.mp4")) + list(input_dir.glob("*.mov")) + list(input_dir.glob("*.mkv"))

    if not video_files:
        print(f"❌ Keine Videos gefunden in: {input_dir}")
        return

    print(f"\n{'='*60}")
    print(f"  BATCH-VERARBEITUNG")
    print(f"  {len(video_files)} Videos → {len(platforms)} Plattformen")
    print(f"{'='*60}")

    for video_file in video_files:
        print(f"\n📹 Verarbeite: {video_file.name}")
        for platform in platforms:
            result = convert_for_platform(video_file, platform)
            if result:
                print(f"   ✅ {platform}: {result}")
            else:
                print(f"   ❌ {platform}: Fehlgeschlagen")


def full_pipeline(input_path, segments=None, platforms=None):
    """
    Komplette Pipeline: Video → geschnittene Clips → alle Plattformen.

    Dies ist der Hauptworkflow:
    1. Audio normalisieren
    2. Untertitel hinzufügen (falls SRT vorhanden)
    3. In Segmente schneiden
    4. Für jede Plattform konvertieren
    5. Wasserzeichen hinzufügen
    6. Thumbnails generieren
    """
    if platforms is None:
        platforms = ["youtube_shorts", "tiktok", "instagram_reel"]

    input_path = Path(input_path)
    project_dir = input_path.parent / f"project_{input_path.stem}"
    project_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  FULL PIPELINE: {input_path.name}")
    print(f"  Output: {project_dir}")
    print(f"{'='*60}")

    # Schritt 1: Audio normalisieren
    print("\n[1/5] Audio normalisieren...")
    normalized = normalize_audio(input_path, project_dir / f"{input_path.stem}_norm.mp4")
    if not normalized:
        normalized = input_path

    # Schritt 2: Untertitel (falls SRT existiert)
    srt_path = input_path.with_suffix(".srt")
    if srt_path.exists():
        print("\n[2/5] Untertitel einbrennen...")
        subtitled = add_subtitles(normalized, srt_path, project_dir / f"{input_path.stem}_sub.mp4")
        if subtitled:
            normalized = subtitled
    else:
        print("\n[2/5] Keine SRT-Datei gefunden, überspringe Untertitel.")
        print(f"       (Erstelle {srt_path.name} für automatische Untertitel)")

    # Schritt 3: Segmente schneiden
    if segments:
        print(f"\n[3/5] {len(segments)} Segmente schneiden...")
        for platform in platforms:
            clips = cut_segments(normalized, segments, platform, project_dir / "clips")
    else:
        print("\n[3/5] Keine Segmente definiert - konvertiere ganzes Video")
        clips = [normalized]

    # Schritt 4: Für Plattformen konvertieren
    print(f"\n[4/5] Für {len(platforms)} Plattformen konvertieren...")
    for platform in platforms:
        convert_for_platform(normalized, platform, project_dir / "platforms")

    # Schritt 5: Thumbnail
    print("\n[5/5] Thumbnail generieren...")
    generate_thumbnail(input_path, "00:00:03", project_dir / "thumbnail.jpg")

    print(f"\n{'='*60}")
    print(f"  ✅ PIPELINE ABGESCHLOSSEN!")
    print(f"  Output: {project_dir}")
    print(f"{'='*60}")


def main():
    if len(sys.argv) < 2:
        print("""
VIDEO-EDITOR AUTOMATISIERUNG
Soul Mastery - Dirk Traub
============================

Verwendung:
    python video_editor.py convert <video> <plattform>
    python video_editor.py cut <video> <start> <end> <titel> [plattform]
    python video_editor.py subtitles <video> <srt_datei> [style]
    python video_editor.py watermark <video> [position]
    python video_editor.py thumbnail <video> [zeitstempel] [text]
    python video_editor.py normalize <video>
    python video_editor.py batch <ordner> [plattform1,plattform2]
    python video_editor.py pipeline <video>

Plattformen: youtube, youtube_shorts, tiktok, instagram_reel, instagram_feed
Untertitel-Styles: modern, bold, minimal
Wasserzeichen-Positionen: top_left, top_right, bottom_left, bottom_right, center

Beispiele:
    python video_editor.py convert mein_video.mp4 tiktok
    python video_editor.py cut mein_video.mp4 30 90 "Burnout_Hook" tiktok
    python video_editor.py pipeline mein_video.mp4
    python video_editor.py batch ./raw_videos tiktok,instagram_reel
        """)
        return

    command = sys.argv[1]

    if command == "convert":
        convert_for_platform(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "tiktok")

    elif command == "cut":
        video = sys.argv[2]
        start = int(sys.argv[3])
        end = int(sys.argv[4])
        title = sys.argv[5] if len(sys.argv) > 5 else "clip"
        platform = sys.argv[6] if len(sys.argv) > 6 else "tiktok"
        cut_segments(video, [(start, end, title)], platform)

    elif command == "subtitles":
        add_subtitles(sys.argv[2], sys.argv[3], style=sys.argv[4] if len(sys.argv) > 4 else "modern")

    elif command == "watermark":
        add_watermark(sys.argv[2], position=sys.argv[3] if len(sys.argv) > 3 else "bottom_right")

    elif command == "thumbnail":
        ts = sys.argv[3] if len(sys.argv) > 3 else "00:00:05"
        text = sys.argv[4] if len(sys.argv) > 4 else None
        generate_thumbnail(sys.argv[2], ts, add_text=text)

    elif command == "normalize":
        normalize_audio(sys.argv[2])

    elif command == "batch":
        platforms = sys.argv[3].split(",") if len(sys.argv) > 3 else None
        batch_process(sys.argv[2], platforms)

    elif command == "pipeline":
        # Beispiel-Segmente (hier deine eigenen Zeitstempel eintragen)
        example_segments = [
            (0, 60, "Hook_und_Intro"),
            (60, 180, "Hauptteil_1"),
            (180, 240, "Bester_Tipp"),
        ]
        full_pipeline(sys.argv[2], example_segments)


if __name__ == "__main__":
    main()

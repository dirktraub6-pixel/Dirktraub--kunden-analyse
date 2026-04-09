#!/usr/bin/env python3
"""
Video-Script-Generator
======================
Generiert hochkonvertierende Video-Skripte für YouTube, TikTok & Instagram
basierend auf bewährten Frameworks.

Voraussetzungen:
    pip install anthropic python-dotenv

Setup:
    In .env: ANTHROPIC_API_KEY=dein_key
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# === BEWÄHRTE SCRIPT-FRAMEWORKS ===

FRAMEWORKS = {
    "hook_story_offer": {
        "name": "Hook → Story → Offer (HSO)",
        "description": "Bestes Framework für Coaching-Verkauf",
        "structure": [
            {"part": "HOOK", "duration": "3-5 Sek", "description": "Stoppt den Scroll. Provokant, emotional, überraschend."},
            {"part": "PROBLEM", "duration": "15-30 Sek", "description": "Beschreibe das Problem so, dass der Zuschauer denkt: 'Das bin ich!'"},
            {"part": "STORY", "duration": "30-60 Sek", "description": "Erzähle DEINE Geschichte oder die eines Klienten."},
            {"part": "LÖSUNG", "duration": "30-60 Sek", "description": "Zeige den Weg. Gib 1-3 konkrete Tipps."},
            {"part": "CTA", "duration": "10-15 Sek", "description": "Was soll der Zuschauer JETZT tun?"},
        ],
    },
    "aida": {
        "name": "AIDA (Attention → Interest → Desire → Action)",
        "description": "Klassisches Marketing-Framework",
        "structure": [
            {"part": "ATTENTION", "duration": "3-5 Sek", "description": "Aufmerksamkeit gewinnen mit starkem Hook"},
            {"part": "INTEREST", "duration": "20-40 Sek", "description": "Interesse wecken mit überraschenden Fakten/Geschichten"},
            {"part": "DESIRE", "duration": "30-60 Sek", "description": "Verlangen erzeugen: So könnte dein Leben aussehen"},
            {"part": "ACTION", "duration": "10-15 Sek", "description": "Klare Handlungsaufforderung"},
        ],
    },
    "pas": {
        "name": "PAS (Problem → Agitate → Solve)",
        "description": "Perfekt für Schmerzpunkt-Videos",
        "structure": [
            {"part": "PROBLEM", "duration": "5-10 Sek", "description": "Benenne das Problem direkt und klar"},
            {"part": "AGITATE", "duration": "20-40 Sek", "description": "Verstärke den Schmerz. Was passiert wenn du NICHTS tust?"},
            {"part": "SOLVE", "duration": "30-60 Sek", "description": "Deine Lösung. Zeige den Weg raus."},
        ],
    },
    "tiktok_short": {
        "name": "TikTok/Reels Short (30-60 Sek)",
        "description": "Kurz, knackig, viral",
        "structure": [
            {"part": "HOOK", "duration": "1-3 Sek", "description": "EINE Zeile die stoppt"},
            {"part": "CONTENT", "duration": "20-40 Sek", "description": "EIN Tipp, EINE Geschichte, EINE Wahrheit"},
            {"part": "TWIST/CTA", "duration": "5-10 Sek", "description": "Überraschung oder Call-to-Action"},
        ],
    },
}

# === HOOK-DATENBANK: Bewährte Hooks für spirituelles Coaching ===

HOOKS_DATABASE = {
    "schock": [
        "Das hat mir noch NIEMAND über spirituelles Erwachen erzählt...",
        "STOP! Wenn du das gerade fühlst, schau dieses Video SOFORT.",
        "Ich habe 10 Jahre meines Lebens verschwendet - weil mir DAS keiner gesagt hat.",
        "Die WAHRHEIT über Meditation, die kein Coach dir sagt.",
        "Wenn du dich gerade leer fühlst, ist das KEIN Zufall.",
        "90% der Coaches lügen dich an. Hier ist warum.",
    ],
    "frage": [
        "Fühlst du dich, als ob du im falschen Leben lebst?",
        "Warum wachst du jeden Morgen auf und fühlst... nichts?",
        "Was, wenn deine Krise eigentlich dein größtes Geschenk ist?",
        "Hast du das Gefühl, dass da MEHR sein muss?",
        "Warum funktioniert positive Denken bei dir nicht?",
        "Was, wenn du schon ALLES in dir trägst, was du brauchst?",
    ],
    "identifikation": [
        "Du bist nicht kaputt. Du wachst gerade auf.",
        "Wenn du das liest, ist es kein Zufall.",
        "Das ist für alle, die sich gerade komplett verloren fühlen.",
        "Du musst das SOFORT hören, wenn du gerade in einer Lebenskrise steckst.",
        "3 Anzeichen, dass du gerade ein spirituelles Erwachen durchmachst.",
        "Wenn du beruflich erfolgreich bist aber innerlich leer - lies weiter.",
    ],
    "neugier": [
        "Eine Übung, die mein ganzes Leben verändert hat. (Dauert 2 Minuten)",
        "Was passiert, wenn du 21 Tage lang DIESE eine Sache machst...",
        "Der #1 Grund warum du dich nicht verändern kannst.",
        "Dieses Geheimnis kennen nur Menschen, die wirklich erwacht sind.",
        "3 Zeichen, dass das Universum versucht, dir etwas zu sagen.",
        "Die mächtigste Frage, die du dir stellen kannst.",
    ],
    "kontrovers": [
        "Spiritualität ist KEIN Hobby. Es ist Überlebensstrategie.",
        "Hört auf, toxische Positivität als Spiritualität zu verkaufen.",
        "Meditation allein wird dich NICHT heilen. Punkt.",
        "Unpopuläre Meinung: Dein Ego ist nicht dein Feind.",
        "Warum ich aufgehört habe, 'Manifestation' zu lehren.",
        "Die dunkle Seite der Spiritualität, über die niemand spricht.",
    ],
}

# === CONTENT-SERIEN: Wiederkehrende Formate ===

CONTENT_SERIES = {
    "seelen_impuls": {
        "name": "Seelen-Impuls des Tages",
        "frequency": "Täglich",
        "platform": "TikTok + Instagram Stories",
        "duration": "15-30 Sek",
        "template": "Kurzer spiritueller Impuls/Weisheit + persönliche Erfahrung",
    },
    "coaching_wahrheiten": {
        "name": "Coaching-Wahrheiten",
        "frequency": "3x/Woche",
        "platform": "Instagram Karussell + TikTok",
        "duration": "30-60 Sek / 5-7 Slides",
        "template": "Eine unbequeme Wahrheit über [Thema] + Lösung",
    },
    "transformation_stories": {
        "name": "Transformation Tuesday",
        "frequency": "1x/Woche",
        "platform": "YouTube + Instagram Reels",
        "duration": "3-10 Min (YouTube) / 60 Sek (Reel)",
        "template": "Klienten-Story: Vorher → Krise → Coaching → Nachher",
    },
    "deep_dive": {
        "name": "Deep Dive",
        "frequency": "1x/Woche",
        "platform": "YouTube",
        "duration": "10-20 Min",
        "template": "Tiefgehende Erklärung eines Themas + praktische Übung",
    },
    "live_qa": {
        "name": "Live Q&A: Frag den Coach",
        "frequency": "1x/Woche",
        "platform": "Instagram Live / YouTube Live",
        "duration": "30-60 Min",
        "template": "Beantwortung von Community-Fragen + spontanes Mini-Coaching",
    },
    "behind_scenes": {
        "name": "Behind the Scenes",
        "frequency": "2x/Woche",
        "platform": "Instagram Stories",
        "duration": "15-60 Sek pro Story",
        "template": "Einblicke in deinen Alltag, deine Praxis, deine eigene Reise",
    },
}

# === 90 TAGE CONTENT-PLAN ===

CONTENT_CALENDAR_WEEK = {
    "Montag": {
        "tiktok": "Seelen-Impuls + Coaching-Wahrheit",
        "instagram": "Karussell-Post (Edukativ)",
        "youtube": "-",
        "focus": "Motivation & Wochenstart",
    },
    "Dienstag": {
        "tiktok": "Seelen-Impuls + Transformation-Story (kurz)",
        "instagram": "Reel (Transformation) + Stories (BTS)",
        "youtube": "Transformation Tuesday (Long-Form)",
        "focus": "Social Proof & Transformation",
    },
    "Mittwoch": {
        "tiktok": "Seelen-Impuls + Kontroverse These",
        "instagram": "Karussell (Kontroverse Meinung) + Stories",
        "youtube": "-",
        "focus": "Engagement & Diskussion",
    },
    "Donnerstag": {
        "tiktok": "Seelen-Impuls + How-To Tipp",
        "instagram": "Reel (Quick-Tipp) + Stories (Q&A)",
        "youtube": "Deep Dive Video",
        "focus": "Edukation & Mehrwert",
    },
    "Freitag": {
        "tiktok": "Seelen-Impuls + Persönliche Geschichte",
        "instagram": "Karussell (Wochenreflexion) + Stories",
        "youtube": "-",
        "focus": "Authentizität & Verbindung",
    },
    "Samstag": {
        "tiktok": "Seelen-Impuls + Meditation/Übung",
        "instagram": "Reel (Geführte Mini-Meditation)",
        "youtube": "-",
        "focus": "Praxis & Anwendung",
    },
    "Sonntag": {
        "tiktok": "Seelen-Impuls",
        "instagram": "Stories (Wochenvorschau) + Live Q&A",
        "youtube": "-",
        "focus": "Community & Vorfreude",
    },
}


def generate_script(topic, framework_key="hook_story_offer", platform="youtube"):
    """Generiert ein Video-Script basierend auf Framework und Thema."""
    framework = FRAMEWORKS[framework_key]

    print(f"\n{'='*60}")
    print(f"  VIDEO-SCRIPT: {topic}")
    print(f"  Framework: {framework['name']}")
    print(f"  Plattform: {platform.upper()}")
    print(f"  Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"{'='*60}\n")

    script_parts = []
    for part in framework["structure"]:
        print(f"--- {part['part']} ({part['duration']}) ---")
        print(f"Anweisung: {part['description']}")
        print(f"[Dein Text hier]\n")
        script_parts.append(part)

    return script_parts


def generate_script_with_ai(topic, framework_key="hook_story_offer", platform="youtube"):
    """Generiert ein komplettes Script mit Claude AI."""
    try:
        import anthropic
    except ImportError:
        print("Installiere: pip install anthropic")
        print("Fallback: Manuelles Template wird verwendet.\n")
        return generate_script(topic, framework_key, platform)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY nicht in .env gefunden. Nutze manuelles Template.\n")
        return generate_script(topic, framework_key, platform)

    client = anthropic.Anthropic(api_key=api_key)
    framework = FRAMEWORKS[framework_key]

    # Plattform-spezifische Anweisungen
    platform_instructions = {
        "youtube": "10-15 Minuten Länge. Tiefgehend, persönlich, transformativ. SEO-optimierter Titel und Beschreibung.",
        "tiktok": "30-60 Sekunden MAX. Extrem schnell, emotional, Hook in den ersten 2 Sekunden. Keine Intros.",
        "instagram_reel": "30-90 Sekunden. Visuell ansprechend, Text-Overlays einplanen, Karussell-freundlich.",
        "instagram_karussell": "5-7 Slides. Jede Slide = 1 klarer Punkt. Slide 1 = Hook, letzte Slide = CTA.",
    }

    prompt = f"""Du bist ein deutscher Content-Stratege für spirituelles Coaching.
Erstelle ein komplettes Video-Script zum Thema: "{topic}"

Framework: {framework['name']}
Plattform: {platform}
Besonderheiten: {platform_instructions.get(platform, '')}

Zielgruppe: Menschen 30-50 Jahre, die sich in einer Lebenskrise/Sinnkrise befinden,
innerlich leer fühlen, oder spirituell erwachen und Orientierung brauchen.

Coach: Dirk Traub - Soul Mastery Coaching. Authentisch, tiefgründig, keine "Good Vibes Only".

Script-Struktur:
{json.dumps([{"teil": p["part"], "dauer": p["duration"], "anweisung": p["description"]} for p in framework["structure"]], ensure_ascii=False, indent=2)}

Erstelle:
1. Einen SEO-optimierten Titel (mit Keyword)
2. 3 alternative Hooks zum Testen
3. Das komplette Script mit Regieanweisungen [in Klammern]
4. Vorschläge für B-Roll / visuelle Elemente
5. 5 relevante Hashtags
6. Die perfekte Video-Beschreibung mit Keywords und CTA

Schreibe natürlich, emotional, authentisch - wie ein echter Mensch spricht.
Nicht wie ein Verkaufs-Bot. Dirk duzt seine Community."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    script = message.content[0].text
    print(script)

    # Script speichern
    safe_topic = topic.replace(" ", "_").replace("/", "_")[:50]
    filename = f"script_{safe_topic}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    filepath = os.path.join(os.path.dirname(__file__), "..", "generated_scripts", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Script: {topic}\n")
        f.write(f"**Plattform:** {platform} | **Framework:** {framework['name']}\n")
        f.write(f"**Erstellt:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
        f.write(script)
    print(f"\n✅ Script gespeichert: {filepath}")

    return script


def print_content_calendar():
    """Zeigt den Wochen-Content-Plan an."""
    print("\n" + "=" * 80)
    print("  WOCHEN-CONTENT-PLAN: Soul Mastery Coaching")
    print("=" * 80)

    for day, plan in CONTENT_CALENDAR_WEEK.items():
        print(f"\n  📅 {day.upper()} (Fokus: {plan['focus']})")
        print(f"     TikTok:    {plan['tiktok']}")
        print(f"     Instagram: {plan['instagram']}")
        print(f"     YouTube:   {plan['youtube']}")


def print_hooks(category=None):
    """Zeigt Hook-Vorschläge an."""
    print("\n" + "=" * 60)
    print("  HOOK-DATENBANK")
    print("=" * 60)

    categories = {category: HOOKS_DATABASE[category]} if category else HOOKS_DATABASE
    for cat, hooks in categories.items():
        print(f"\n  [{cat.upper()}]")
        for hook in hooks:
            print(f"    → \"{hook}\"")


def print_series():
    """Zeigt alle Content-Serien an."""
    print("\n" + "=" * 60)
    print("  CONTENT-SERIEN")
    print("=" * 60)

    for key, series in CONTENT_SERIES.items():
        print(f"\n  {series['name']}")
        print(f"  Frequenz: {series['frequency']} | Plattform: {series['platform']}")
        print(f"  Dauer: {series['duration']}")
        print(f"  Format: {series['template']}")


def main():
    import sys

    print("=" * 60)
    print("  VIDEO-SCRIPT-GENERATOR")
    print("  Soul Mastery Coaching - Dirk Traub")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("""
Verwendung:
    python script_generator.py generate "Thema" [framework] [plattform]
    python script_generator.py ai "Thema" [framework] [plattform]
    python script_generator.py hooks [kategorie]
    python script_generator.py calendar
    python script_generator.py series

Frameworks: hook_story_offer, aida, pas, tiktok_short
Plattformen: youtube, tiktok, instagram_reel, instagram_karussell

Beispiele:
    python script_generator.py generate "Burnout überwinden" hook_story_offer youtube
    python script_generator.py ai "3 Anzeichen für spirituelles Erwachen" tiktok_short tiktok
    python script_generator.py hooks schock
    python script_generator.py calendar
        """)
        return

    command = sys.argv[1]

    if command == "generate":
        topic = sys.argv[2] if len(sys.argv) > 2 else "Spirituelles Erwachen"
        framework = sys.argv[3] if len(sys.argv) > 3 else "hook_story_offer"
        platform = sys.argv[4] if len(sys.argv) > 4 else "youtube"
        generate_script(topic, framework, platform)

    elif command == "ai":
        topic = sys.argv[2] if len(sys.argv) > 2 else "Spirituelles Erwachen"
        framework = sys.argv[3] if len(sys.argv) > 3 else "hook_story_offer"
        platform = sys.argv[4] if len(sys.argv) > 4 else "youtube"
        generate_script_with_ai(topic, framework, platform)

    elif command == "hooks":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        print_hooks(category)

    elif command == "calendar":
        print_content_calendar()

    elif command == "series":
        print_series()


if __name__ == "__main__":
    main()

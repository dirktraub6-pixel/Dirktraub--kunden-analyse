# Implementierungsplan: User Auth via Magic Link

## Soul Mastery Web-App -- Next.js + Supabase

**Datum:** 26. Mai 2026
**Status:** Implementiert

---

## 1. Kontext

Das Repository ist ein Python-basiertes Automatisierungs-Toolkit fuer das Coaching-Business "Soul Mastery". 
Die Web-App unter `web/` ergaenzt das Projekt um Magic-Link-Authentifizierung via Supabase als Basis fuer geschuetzte Coaching-Bereiche.

---

## 2. Projektstruktur

```
web/
├── .env.local.example
├── package.json
├── next.config.ts
├── tsconfig.json
│
├── supabase/
│   └── migrations/
│       ├── 001_create_profiles.sql      ← Profiltabelle + RLS + Trigger
│       └── 002_rate_limiting.sql        ← Rate-Limit-Tracking-Tabelle
│
└── src/
    ├── middleware.ts                     ← Session-Refresh auf jeder Route
    │
    ├── lib/supabase/
    │   ├── client.ts                    ← Browser-Client
    │   ├── server.ts                    ← Server-Client (Cookies)
    │   └── middleware.ts                ← Middleware-Client (updateSession)
    │
    └── app/
        ├── layout.tsx                   ← Root Layout (Geist Font, Deutsch)
        ├── page.tsx                     ← Startseite mit Login-Link
        ├── globals.css
        │
        ├── actions/
        │   └── auth.ts                  ← Server Actions: sendMagicLink, signOut
        │
        ├── auth/
        │   ├── login/page.tsx           ← Login-Formular (Magic Link)
        │   └── callback/route.ts        ← Token-Exchange Route Handler
        │
        └── dashboard/
            └── page.tsx                 ← Geschuetztes Dashboard
```

---

## 3. Auth-Flow

```
Nutzer gibt E-Mail ein
    → Server Action: E-Mail validieren + Rate-Limit pruefen
    → Supabase signInWithOtp({ email })
    → E-Mail mit Magic Link wird gesendet
    → Nutzer klickt Link
    → /auth/callback tauscht Code gegen Session
    → Redirect zu /dashboard
```

### Fehlerfall: Abgelaufener Link
```
Nutzer klickt abgelaufenen Link
    → Supabase sendet error=access_denied
    → /auth/callback erkennt Fehler
    → Redirect zu /auth/login?error=expired
    → Login-Seite zeigt deutsche Fehlermeldung
```

---

## 4. Supabase Setup (manuell)

### 4.1 Projekt erstellen
- Region: `eu-central-1` (Frankfurt)
- Auth-Provider: Email (Magic Link aktiviert, Passwort deaktiviert)

### 4.2 Environment Variables
```bash
cp web/.env.local.example web/.env.local
# Dann SUPABASE_URL und ANON_KEY eintragen
```

### 4.3 Auth-Settings im Dashboard
- Site URL: `http://localhost:3000` (Dev) / `https://deine-domain.de` (Prod)
- Redirect URLs: `http://localhost:3000/auth/callback`, `https://deine-domain.de/auth/callback`
- Magic-Link-Token: 1 Stunde (Standard)
- JWT-Lebensdauer: 3600 Sekunden
- Refresh-Token: 30 Tage

### 4.4 Migrationen ausfuehren
```bash
# Entweder via Supabase CLI:
npx supabase db push

# Oder manuell im SQL Editor die Dateien unter supabase/migrations/ ausfuehren
```

---

## 5. Sicherheit

| Aspekt | Implementierung |
|---|---|
| CSRF | Server Actions haben eingebauten Origin-Header-Check |
| Token-Speicherung | Nur in httpOnly-Cookies, nie localStorage |
| Token-Ablauf | Magic Link: 1h, JWT: 1h (auto-refresh), Refresh: 30d |
| Cookie-Flags | httpOnly, secure (Prod), sameSite=lax |
| Rate-Limiting | In-Memory: max 3 Anfragen pro E-Mail / 5 Minuten |
| E-Mail-Enumeration | Supabase gibt identische Responses fuer existierende/neue E-Mails |
| Session-Refresh | Middleware refresht Token bei jedem Request |
| Auth-Validierung | `getUser()` statt `getSession()` (Server-seitige Validierung) |
| RLS | Profiles: Nur eigene Daten lesen/schreiben |

---

## 6. Rate Limiting

### Anwendungsebene (Server Action)
- Max 3 Magic-Link-Anfragen pro E-Mail in 5 Minuten
- In-Memory Map mit automatischem Reset

### Supabase-seitig (Dashboard)
- Max 4 E-Mails pro Stunde pro User (Supabase-Default)

### Client-seitig
- Submit-Button deaktiviert waehrend Verarbeitung
- Erfolgs-State ersetzt Formular (verhindert Re-Submit)

---

## 7. Verifikations-Checkliste

```
[ ] npm run build -- kompiliert ohne Fehler
[ ] Magic Link anfordern → E-Mail kommt an
[ ] Magic Link klicken → Redirect zu /dashboard
[ ] Dashboard zeigt Benutzerdaten (E-Mail)
[ ] Abmelden → Redirect zu /auth/login
[ ] /dashboard ohne Session → Redirect zu /auth/login
[ ] Abgelaufener Link → Fehlermeldung auf Login-Seite
[ ] 4+ Anfragen in 5 Min → Rate-Limit-Meldung
[ ] RLS: Profil nur fuer eigenen User sichtbar
[ ] Session bleibt nach Browser-Neustart bestehen
```

---

## 8. Tech Stack

| Technologie | Version | Zweck |
|---|---|---|
| Next.js | 16.2.6 | Web-Framework (App Router) |
| React | 19.2.4 | UI |
| Supabase JS | 2.106.2 | Auth + DB Client |
| @supabase/ssr | 0.10.3 | Server-seitige Auth (Cookies) |
| Tailwind CSS | 4.x | Styling |
| TypeScript | 5.x | Typsicherheit |

---

## 9. Zukuenftige Erweiterungen

- Funnel-Landing-Pages (Verlustangst, Bindungstrauma, etc.)
- Freebie-Downloads hinter Login
- Klienten-Dashboard mit Fortschritt
- Membership-Zahlungen (Stripe)
- Admin-Dashboard
- E-Mail-Sequenzen (Resend/Postmark statt Mailerlite)

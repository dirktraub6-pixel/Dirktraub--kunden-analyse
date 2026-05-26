# Security Review: Magic-Link Auth

**Datum:** 26. Mai 2026
**Scope:** web/ (Next.js + Supabase Magic Link Auth)

---

## Ergebnisse nach Severity

### HIGH -- Behoben

| # | Finding | Status |
|---|---|---|
| H3 | `emailRedirectTo` aus Request-Headers statt Environment Variable | FIXED -- nutzt jetzt `NEXT_PUBLIC_SITE_URL` |

### HIGH -- Bekannt (Akzeptiert fuer MVP)

| # | Finding | Empfehlung |
|---|---|---|
| H1 | In-Memory Rate Limiting nicht persistent (Serverless) | Fuer Produktions-Scale: Upstash Redis oder DB-basiert |
| H2 | `auth_rate_limits` Tabelle erstellt aber nicht verdrahtet | Bei Scale: Server-Action auf DB-Tabelle umstellen |

### MEDIUM -- Behoben

| # | Finding | Status |
|---|---|---|
| M1 | Middleware erzwingt keinen Route-Schutz | FIXED -- Middleware prueft jetzt Auth fuer /dashboard |
| M5 | Keine Security Headers in next.config.ts | FIXED -- X-Frame-Options, HSTS, nosniff, Referrer-Policy |

### MEDIUM -- Bekannt

| # | Finding | Empfehlung |
|---|---|---|
| M2 | PKCE Flow nicht explizit verifiziert | Supabase Dashboard pruefen: Auth Flow = PKCE |
| M3 | Timing Side-Channel bei Email Enumeration | Supabase: identische Response-Zeiten konfigurieren |
| M4 | `auth_rate_limits` hat kein Auto-Cleanup | pg_cron Job einrichten fuer taegliches Cleanup |

### LOW

| # | Finding | Empfehlung |
|---|---|---|
| L1 | Non-null assertion auf Env Variables | Runtime-Validierung beim App-Start hinzufuegen |
| L2 | Email-Regex ist permissiv | Akzeptabel -- Supabase validiert serverseitig |
| L3 | `error_description` nicht sanitized | Aktuell sicher (wird nie gerendert) |

---

## Positive Findings

- `getUser()` statt `getSession()` fuer Auth-Checks (faelschungssicher)
- RLS auf allen Tabellen aktiviert
- `SECURITY DEFINER` Funktionen mit leerem `search_path`
- CSRF-Schutz durch Server Actions (Origin-Header-Validierung)
- Generische Fehlermeldungen (keine Info-Leaks)
- Cookie-Security via @supabase/ssr Defaults (httpOnly, secure, sameSite)

---

## Empfehlungen fuer Produktion

1. `NEXT_PUBLIC_SITE_URL` als feste Domain setzen
2. Supabase Redirect-URLs Allowlist konfigurieren
3. Custom SMTP (Resend/Postmark) fuer bessere Email-Deliverability
4. Rate Limiting auf Upstash Redis umstellen
5. Content Security Policy (CSP) Header ergaenzen

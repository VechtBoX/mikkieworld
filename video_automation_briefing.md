# MIKKIE WORLD — Daily Video Automation Briefing

## Doel van de Taak
Ontwikkel en configureer een lokale AI-agent (`mikkie_video_agent.py`) die **volledig geautomatiseerd** dagelijkse videocontent genereert en post voor MIKKIE WORLD. Deze agent moet draaien op de bestaande Playwright/Artistly architectuur en integreren met de 24/7 daemon (`mikkie_agent.py` / `mikkie_artistly_agent.py`).

## 1. Integratie & Architectuur
- **Platform:** Lokale executie op Hendrik's MacBook Pro (macOS).
- **Huidige Stack:** Python 3.14, Playwright (headless Chromium), Artistly AI (via cookies in `artistly_session.json`), Grok AI (via `XAI_API_KEY`), X/Twitter API.
- **Workflow:** De video-agent moet als een module werken of aangeroepen worden via de bestaande daemon-structuur (bijv. via een nieuw script `mikkie_video_agent.py` dat wordt getriggerd door cron of launchd).
- **Posting:** De agent moet de gegenereerde video's lokaal opslaan (bijv. in `~/mikkieworld/video_output/`) en vervolgens **rechtstreeks naar X/Twitter posten** via de bestaande Twitter API integratie (zoals gebruikt in `mikkie_agent.py` -> `post_tweet()`, maar dan uitgebreid voor media uploads).

## 2. Content Type
De agent moet **korte, geanimeerde video's (MP4)** genereren.
- **Bronmateriaal:** Gebruik Artistly's "Video Express" of "Image to Video" functies. De input zijn de statische illustraties (covers, social posts) die de `mikkie_artistly_agent.py` al genereert in de MIKKIE WORLD stijl.
- **Audio:** Als Artistly's CloneVoice/Audio functies beschikbaar zijn, voeg dan een warme, vaderlijke voice-over toe (Hendrik's voorkeur).
- **Formaat:** 16:9 of 1:1, afhankelijk van het X/Twitter algoritme, max 15-30 seconden per video.

## 3. MIKKIE WORLD Branding (Verplicht in elke prompt)
De AI-agent moet de merkwaarden in elke video-prompt en begeleidende tweet verwerken:
- **Kernwaarden:** Avontuurlijk · Moedig · Magisch (WWJD-proof, focus op kinderen buiten laten spelen).
- **Kleurenpalet:**
  - Kristalblauw (`#3A8FA8`)
  - Goud (`#D4A017`)
  - Diepzwart (`#0A0F14`)
  - Bladgroen (`#5B9957`)
  - Crème (`#F8F4EB`)
- **Stijl (Visuals):** Pixar-inspired 3D render, storybook illustration style, warm magical lighting met golden rim light.
- **Karakters:** MIKKIE (The Hero), BUBBLES, KNOEST, FIDO, NYX, ZERA, ORA.
- **Vader-zoon focus:** De begeleidende tekst/audio moet aanvoelen als een vader die zijn kind aanspoort om op avontuur te gaan.

## 4. De Gewenste Workflow (End-to-End)
1. **Trigger:** De daemon activeert de video-taak (bijv. 2x per dag).
2. **Selectie:** De agent kiest een recent gegenereerde afbeelding uit `~/mikkieworld/artistly_output/`.
3. **Generatie:** Playwright navigeert naar de Artistly Video tool, uploadt de afbeelding, vult de animatie-prompt in (gebaseerd op de branding), en klikt op genereren.
4. **Download:** De agent wacht tot de video klaar is en downloadt de `.mp4` naar `~/mikkieworld/video_output/`.
5. **Copywriting:** Grok AI genereert een bijpassende tweet (max 280 tekens, inclusief hashtags zoals `#MIKKIEWORLD`, focus op moed en avontuur).
6. **Publicatie:** De agent uploadt de video naar X/Twitter via de API en post de tweet.
7. **Logging:** De actie wordt gelogd in `artistly_agent.log` en de status wordt bijgewerkt.

## 5. Open Punten & Uitdagingen voor deze Taak
- **Artistly Video Tool Selectors:** De Playwright selectors voor de video-generatie pagina op Artistly moeten worden onderzocht en vastgelegd (net zoals we deden met `force=True` voor afbeeldingen).
- **Twitter Media Upload:** De huidige `post_tweet()` in `mikkie_agent.py` ondersteunt alleen tekst. Dit moet worden uitgebreid met het Twitter API v1.1 media upload endpoint (chunked upload voor video's) voordat v2 de tweet plaatst.
- **Artistly API Key:** Er is een `fd58524c-5603-44a2-a23d-a9703753084b` key specifiek voor VideoExpress/CloneVoice. Onderzoek of we de API direct kunnen gebruiken in plaats van Playwright voor het video-gedeelte, wat de stabiliteit enorm zou verhogen.

## Instructie voor de Uitvoerende Manus Agent
1. Start met het onderzoeken van de Artistly API key (`fd58524c...`) voor VideoExpress. Als de API werkt, bouw de agent daarop. Zo niet, gebruik de Playwright fallback.
2. Schrijf de code in `~/mikkieworld/mikkie_video_agent.py`.
3. Update de Twitter integratie in `mikkie_agent.py` om `.mp4` uploads te ondersteunen.
4. Test de flow end-to-end lokaal in de sandbox voordat je de code oplevert.

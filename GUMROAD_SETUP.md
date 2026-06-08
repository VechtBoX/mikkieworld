# MIKKIE WORLD — Gumroad Volledig Configureren
**Datum:** 8 juni 2026 | **Lancering:** 7 juli 2026 om 07:07

---

## STAP 1 — Nieuw Gumroad API Token aanmaken

Het huidige token is ingetrokken. Maak een nieuw token aan:

1. Ga naar: **https://app.gumroad.com/settings/advanced**
2. Scroll naar **"Application API"**
3. Klik **"Generate Access Token"**
4. Kopieer het nieuwe token

---

## STAP 2 — Token opslaan in ~/.zshrc

Voer deze commando's **één voor één** in de terminal in:

```
nano ~/.zshrc
```

Zoek de regel met `GUMROAD_API_TOKEN` en vervang het oude token door het nieuwe.
Of voeg onderaan toe als de regel er niet is:

```
export GUMROAD_API_TOKEN=JOUW_NIEUWE_TOKEN_HIER
```

Sla op met `Ctrl+O`, `Enter`, `Ctrl+X`.

Herlaad zshrc:
```
source ~/.zshrc
```

---

## STAP 3 — Script bijwerken via GitHub

```
cd ~/mikkieworld
git pull origin main
```

---

## STAP 4 — Token testen

```
mikkie-gumroad token-check
```

Verwacht output:
```
Token check...
OK - Token werkt! 2 product(en) gevonden.
```

---

## STAP 5 — Alle producten aanmaken (één commando)

```
mikkie-gumroad setup
```

Dit commando doet automatisch:
- Bestaand product (91 illustraties) → beschrijving bijwerken
- 6 nieuwe Quest Bundles aanmaken (BUBBLES, KNOEST, NYX, ORA, FIDO, ZERA)
- MIKKIE Founders Pack aanmaken

**Alle producten worden aangemaakt als ONGEPUBLICEERD** — jij bepaalt wanneer je ze live zet.

---

## STAP 6 — Producten controleren

```
mikkie-gumroad products
```

Verwacht output (8 producten):
```
Naam                                          Prijs      Sales  ID
------------------------------------------------------------------------------------------
MIKKIE World: 91 Magische Karakter Illu...    EUR9.99    0      uiRWcbhQH-...
BUBBLES Quest Bundle - Wateravonturen...      EUR7.0     0      [nieuw id]
KNOEST Quest Bundle - Bosavonturen...         EUR7.0     0      [nieuw id]
NYX Quest Bundle - Nachtavonturen...          EUR7.0     0      [nieuw id]
ORA Quest Bundle - Slimme Speurtochten...     EUR7.0     0      [nieuw id]
FIDO Quest Bundle - Dierenspoor...            EUR7.0     0      [nieuw id]
ZERA Quest Bundle - Energie en Weer...        EUR7.0     0      [nieuw id]
MIKKIE Founders Pack - Compleet...            EUR47.0    0      [nieuw id]
```

---

## STAP 7 — Gratis leadmagnet PDF uploaden

De PDF (`~/MIKKIE_7_Missies_MAGIC.pdf`) moet handmatig worden geüpload via de browser.
Gumroad ondersteunt geen bestandsupload via API.

**Stappen:**
1. Ga naar: **https://app.gumroad.com/products**
2. Klik op **"MIKKIE 7 Gratis Buitenmissies"** (gratis product, URL: `gdxlrm`)
3. Klik **"Edit"**
4. Scroll naar **"Content"** → klik **"Add a file"**
5. Upload `~/MIKKIE_7_Missies_MAGIC.pdf`
6. Klik **"Save and continue"**
7. Zorg dat het product **gepubliceerd** is (groen vinkje)

---

## STAP 8 — Producten publiceren

Na de setup zijn alle nieuwe producten ongepubliceerd. Publiceer ze via:

**Via browser (aanbevolen voor lancering):**
- https://app.gumroad.com/products
- Klik elk product → toggle "Published"

**Of via terminal (één product):**
```
mikkie-gumroad update PRODUCT_ID published true
```

**Tip:** Publiceer de Quest Bundles en Founders Pack pas op 7/7/2026 om 07:07 voor maximale impact.

---

## STAP 9 — Mailchimp sync (na eerste verkopen)

```
mikkie-gumroad sync
```

Dit voegt alle Gumroad kopers automatisch toe aan je Mailchimp lijst met de tag `gumroad-koper`.

---

## Productoverzicht en prijzen

| Product | Prijs | Doelgroep |
|---|---|---|
| 91 Magische Illustraties | €9.99 | Ouders, leerkrachten |
| BUBBLES Quest Bundle | €7.00 | Kinderen 4-10 (water) |
| KNOEST Quest Bundle | €7.00 | Kinderen 5-12 (bos) |
| NYX Quest Bundle | €7.00 | Kinderen 6-12 (nacht) |
| ORA Quest Bundle | €7.00 | Kinderen 6-12 (puzzels) |
| FIDO Quest Bundle | €7.00 | Kinderen 4-10 (dieren) |
| ZERA Quest Bundle | €7.00 | Kinderen 6-12 (weer) |
| MIKKIE Founders Pack | €47.00 | Superfans (100 stuks) |
| 7 Gratis Buitenmissies | GRATIS | Leadmagnet (PDF) |

**Totale waarde per klant (alle bundles):** €9.99 + (6 × €7) + €47 = **€98.99**

---

## Snelle referentie — alle commando's

```
mikkie-gumroad help          # Toon alle commando's
mikkie-gumroad token-check   # Test API token
mikkie-gumroad products      # Toon alle producten
mikkie-gumroad sales         # Toon alle verkopen
mikkie-gumroad setup         # Maak alle producten aan
mikkie-gumroad sync          # Sync kopers naar Mailchimp
```

---

## Troubleshooting

**"Token verlopen of ingetrokken"**
→ Maak nieuw token: https://app.gumroad.com/settings/advanced
→ Update ~/.zshrc → source ~/.zshrc

**"GUMROAD_API_TOKEN niet gevonden"**
→ Controleer: `echo $GUMROAD_API_TOKEN`
→ Als leeg: `source ~/.zshrc`

**Product aanmaken mislukt**
→ Controleer token eerst: `mikkie-gumroad token-check`
→ Controleer internetverbinding

---

*MIKKIE WORLD — Avontuur voor elk kind | Lancering 7/7/2026 om 07:07*

# Artistly Volledige Selector Documentatie

## AI Image Designer v6 — /ai/image-designer-v6

### STAP 1: Categorie selecteren
Na paginalading zijn alle categoriekaarten zichtbaar als `div` elementen.
De textarea (element 47) is al aanwezig in de DOM maar staat buiten de viewport (424px eronder).

**Categorie selectors (klik op de div):**
- `Create From Prompt` → `div:has-text("Create From Prompt"):not(:has(div))` of index 32
- `v4 Image Designer` → index 33
- `Artistic Designer` → index 35
- `Artistic Designer V2` → index 36
- `Photorealism` → index 37
- `Animal` → index 38
- `Logo` → index 40
- `T-Shirt Designs` → index 41
- `Social Media Posts` → index 42
- `Seamless Patterns` → index 43
- `Poster Maker` → index 44
- `Sticker` → index 45
- `Cards & Invites` → index 46

**BELANGRIJK:** Na klikken op categorie scrollt pagina naar beneden.
Textarea is al in DOM maar buiten viewport. Gebruik JS scroll + JS fill.

### STAP 2: Prompt invullen
**Textarea selector:** `textarea[placeholder="Enter prompt here"]` (element 47 voor klik, kan verschuiven na invullen)
**JS aanpak (bewezen werkend):**
```javascript
const ta = document.querySelector('textarea[placeholder="Enter prompt here"]');
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
nativeInputValueSetter.call(ta, prompt);
ta.dispatchEvent(new Event('input', { bubbles: true }));
ta.dispatchEvent(new Event('change', { bubbles: true }));
ta.focus();
```

**Mirror Magic toggle:** `button:has-text("Mirror Magic")` (element 49)
**Fast/High Quality:** `button:has-text("Fast")` (element 50), `button:has-text("High Quality")` (element 51)

### STAP 3: Settings (rechter paneel)
**Folder select:** `select` met opties: All Folders, Mikkie, PIXAR, Consistent Characters, Flipbook Templates
**JS folder selectie (bewezen werkend):**
```javascript
const selects = document.querySelectorAll('select');
for (const sel of selects) {
    const opts = Array.from(sel.options).map(o => o.text);
    if (opts.includes('Mikkie')) {
        sel.value = Array.from(sel.options).find(o => o.text === 'Mikkie').value;
        sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
}
```

**Visibility select:** opties: Nothing selected, Public, Private (element 55)
**Quantity select:** opties: 1, 2, 3, 4 (element 57)

**Aspect Ratio select (na scrollen):**
- `1:1 (1024 X 1024) px` — voor Gumroad covers, stickers
- `16:9 (1344 X 768) px` — voor hero banners, social media
- `9:16 (768 X 1344) px` — voor Instagram stories
- `3:2 (1216 X 832) px` — voor Facebook posts

### STAP 4: Genereren
**Generate knop:** `button#generate_image_flux` of `button:has-text("Generate Image")`
**Na klikken:** pagina redirect naar `/personal-designs` met "Success" melding

---

## Coloring Pages — /ai/image-designer-v6 (Coloring Page categorie)
Nog te documenteren — apart tool in het menu

## Kids Puzzles — /ai/kids-puzzles
Nog te documenteren

## AI Storybook Studio — /ai/storybook-studio
Nog te documenteren

## Consistent Characters — /consistent-characters
Nog te documenteren

## AI Design Agents — /ai/design-agents
Nog te documenteren

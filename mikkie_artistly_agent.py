#!/usr/bin/env python3
"""
MIKKIE WORLD — 24/7 Artistly AI Content Agent v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gebaseerd op Paul Ponna's officiële Artistly best practices:

4-Part Prompt Formula (uit de training videos):
  Subject   → Wie/wat is het hoofdonderwerp?
  Style     → Welke kunststijl? (watercolor, Pixar 3D, kawaii, etc.)
  Details   → Kleuren, sfeer, specifieke kenmerken
  Format    → Achtergrond, formaat, technische vereisten

Gouden regels (Paul Ponna):
  1. Verander ALLEEN de actie, niet de stijl-modifiers
  2. Specificeer altijd de oogstijl voor consistente karakters
  3. Gebruik "white background" i.p.v. "transparent" voor betere resultaten
  4. Advanced Designer voor consistente bundels (niet Fast Designer)
  5. Lock in kleuren expliciet in de prompt

Bewezen selectors (live getest in Artistly v6):
  - Categorie klik: text=Create From Prompt
  - Textarea: textarea[placeholder="Enter prompt here"]
  - Generate knop: #generate_image_flux
  - Folder select: select met optie "Mikkie"
  - Aspect ratio: knoppen met tekst "1:1", "16:9", etc.
"""

import os, sys, json, asyncio, logging, argparse, datetime, urllib.request
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR     = Path.home() / "mikkieworld"
OUTPUT_DIR   = BASE_DIR / "artistly_output"
SESSION_FILE = BASE_DIR / "artistly_session.json"
STATE_FILE   = BASE_DIR / "artistly_state.json"
LOG_FILE     = BASE_DIR / "artistly_agent.log"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("artistly")

# ─── MIKKIE WORLD Design DNA ──────────────────────────────────────────────────
# Dit is de vaste stijl-basis die NOOIT verandert (Paul Ponna's gouden regel)
# Alleen de Subject (actie) verandert per afbeelding

# Stijl voor kleurrijke illustraties (covers, social, banners)
STYLE_STORYBOOK = (
    "Pixar-inspired 3D render, "
    "storybook illustration style, "
    "warm magical lighting with golden rim light, "
    "crystal blue and gold color palette, "
    "deep black shadows, cream white highlights, "
    "enchanted forest atmosphere, "
    "children's book illustration quality, "
    "highly detailed"
)

# Stijl voor kleurplaten (zwart-wit, dikke lijnen)
STYLE_COLORING = (
    "black and white coloring page, "
    "thick bold clean outlines, "
    "no shading, no gray fills, no gradients, "
    "pure white background, "
    "simple shapes easy to color, "
    "bold line art suitable for children ages 4-8, "
    "printable coloring book style, "
    "clean vector line art"
)

# Stijl voor stickers (kawaii, transparante achtergrond)
STYLE_STICKER = (
    "cute kawaii sticker design, "
    "flat clipart style, "
    "pastel color palette with crystal blue and gold accents, "
    "thick white border outline, "
    "white background, "
    "children's sticker book style, "
    "clean vector look"
)

# Stijl voor social media posts
STYLE_SOCIAL = (
    "vibrant social media illustration, "
    "bold saturated colors, "
    "crystal blue and gold color scheme, "
    "magical sparkles and stars, "
    "children's brand aesthetic, "
    "Instagram-ready composition, "
    "Pixar-inspired 3D style"
)

# Stijl voor Gumroad product covers
STYLE_COVER = (
    "professional product cover art, "
    "Pixar movie poster style, "
    "dramatic magical lighting, "
    "crystal blue sky background with golden stars, "
    "bold adventurous composition, "
    "children's book cover quality, "
    "high detail, cinematic, "
    "square 1:1 format"
)

# ─── 7 MIKKIE WORLD Karakters ─────────────────────────────────────────────────
# Beschrijvingen zijn geoptimaliseerd voor consistentie (Paul Ponna methode):
# - Specificeer altijd haarkleur, oogkleur, kleding
# - Specificeer oogstijl voor consistente karakters
# - Specificeer unieke kenmerken die het karakter herkenbaar maken

CHARACTERS = {
    "MIKKIE": {
        "nl_name": "Mikkie",
        "subject_base": (
            "brave adventurous 7-year-old boy with short brown hair, "
            "bright crystal blue eyes with simple round dot pupils, "
            "wearing a forest green adventure jacket with golden buttons, "
            "brown leather boots, "
            "small golden compass around his neck"
        ),
        "world": "magical enchanted forest with glowing mushrooms and crystal streams",
        "guardian_of": "avontuur en moed",
        "catchphrase": "Avontuur wacht!",
        "gumroad_product": "MIKKIE Quest Bundle",
    },
    "BUBBLES": {
        "nl_name": "Bubbles",
        "subject_base": (
            "cheerful small bubble fairy with round big eyes with simple dot pupils, "
            "light blue hair with tiny bubbles floating around it, "
            "iridescent rainbow wings, "
            "wearing a shimmering blue dress, "
            "always surrounded by floating soap bubbles in rainbow colors"
        ),
        "world": "underwater bubble kingdom with coral reefs and rainbow pearls",
        "guardian_of": "vriendschap en vreugde",
        "catchphrase": "Samen is alles mogelijk!",
        "gumroad_product": "BUBBLES Quest Bundle",
    },
    "KNOEST": {
        "nl_name": "Knoest",
        "subject_base": (
            "wise ancient tree spirit with a gnarled wooden face, "
            "glowing amber eyes with simple round pupils, "
            "mossy green beard and eyebrows, "
            "bark-textured skin with carved patterns, "
            "gentle giant with a warm smile"
        ),
        "world": "ancient whispering forest with thousand-year-old oak trees",
        "guardian_of": "het bos en de natuur",
        "catchphrase": "De natuur vertelt haar geheimen.",
        "gumroad_product": "KNOEST Quest Bundle",
    },
    "FIDO": {
        "nl_name": "Fido",
        "subject_base": (
            "friendly small dragon with purple scales and golden belly, "
            "big innocent round eyes with simple dot pupils, "
            "tiny golden wings, "
            "wagging tail with a golden tip, "
            "always breathing golden glitter sparkles instead of fire"
        ),
        "world": "crystal cave mountains with sparkling gemstone formations",
        "guardian_of": "dieren en wilde natuur",
        "catchphrase": "Vlieg mee op avontuur!",
        "gumroad_product": "FIDO Quest Bundle",
    },
    "NYX": {
        "nl_name": "Nyx",
        "subject_base": (
            "mysterious night princess with long silver hair, "
            "glowing purple eyes with simple star-shaped pupils, "
            "dark midnight blue dress covered in tiny silver stars, "
            "silver crescent moon crown, "
            "surrounded by fireflies and shooting stars"
        ),
        "world": "starlit night sky kingdom with moon castles and constellation bridges",
        "guardian_of": "de nacht en dromen",
        "catchphrase": "In het donker schijnen de sterren het helderst.",
        "gumroad_product": "NYX Quest Bundle",
    },
    "ZERA": {
        "nl_name": "Zera",
        "subject_base": (
            "radiant guardian angel with large golden feathered wings, "
            "warm brown eyes with simple round pupils, "
            "flowing white robes with golden trim, "
            "glowing golden halo, "
            "always smiling with a warm protective expression"
        ),
        "world": "golden cloud heaven with rainbow bridges and fluffy white clouds",
        "guardian_of": "bescherming en liefde",
        "catchphrase": "Je bent nooit alleen.",
        "gumroad_product": "ZERA Quest Bundle",
    },
    "ORA": {
        "nl_name": "Ora",
        "subject_base": (
            "wise old owl with round golden spectacles, "
            "large amber eyes with simple round pupils, "
            "deep brown and gold feathers, "
            "wearing a small graduation cap, "
            "holding an ancient glowing scroll in one wing"
        ),
        "world": "ancient library tree with magical floating books and knowledge crystals",
        "guardian_of": "kennis en wijsheid",
        "catchphrase": "Kennis is de grootste schat.",
        "gumroad_product": "ORA Quest Bundle",
    },
}

# ─── Prompt Bibliotheek ───────────────────────────────────────────────────────
# Paul Ponna's methode: verander ALLEEN de actie, niet de stijl

def build_prompt(subject, style, details="", fmt=""):
    """Bouw een prompt op volgens Paul Ponna's 4-part formula"""
    parts = [subject, style]
    if details:
        parts.append(details)
    if fmt:
        parts.append(fmt)
    return ", ".join(p.strip().rstrip(",") for p in parts if p.strip())

def get_cover_prompts():
    """Gumroad product covers — professionele 1:1 covers"""
    prompts = []
    for char_id, char in CHARACTERS.items():
        subject = f"{char['subject_base']} standing heroically in {char['world']}, arms spread wide, looking confident"
        prompt = build_prompt(
            subject=subject,
            style=STYLE_COVER,
            details=f"MIKKIE WORLD children's brand, guardian of {char['guardian_of']}",
            fmt="square 1:1 composition, title space at top"
        )
        prompts.append({
            "character": char_id,
            "type": "cover",
            "prompt": prompt,
            "aspect_ratio": "1:1 (1024 X 1024) px",
            "folder": "Mikkie",
            "filename": f"cover_{char_id.lower()}.png",
        })
    return prompts

def get_coloring_prompts():
    """
    Kleurplaten voor Quest Bundles — 5 per karakter = 35 totaal
    Elke kleurplaat heeft een andere actie maar dezelfde stijl
    """
    actions = [
        "standing proudly with arms raised, big smile",
        "running through a magical forest, leaves flying around",
        "sitting under a big tree reading a magical glowing book",
        "jumping over a sparkling crystal stream, splashing water",
        "discovering a hidden treasure chest in the forest",
        "playing with forest animals: rabbits, deer, and butterflies",
        "looking up at stars in the night sky, pointing at a shooting star",
        "building a treehouse with woodland friends helping",
        "exploring a cave entrance with a glowing lantern",
    ]
    prompts = []
    for char_id, char in CHARACTERS.items():
        for i, action in enumerate(actions[:5]):
            subject = f"{char['subject_base']} {action}"
            prompt = build_prompt(
                subject=subject,
                style=STYLE_COLORING,
                fmt="A4 portrait format, children ages 4-8"
            )
            prompts.append({
                "character": char_id,
                "type": "coloring",
                "action_index": i + 1,
                "prompt": prompt,
                "aspect_ratio": "3:4 (896 X 1152) px",
                "folder": "Mikkie",
                "filename": f"coloring_{char_id.lower()}_{i+1:02d}.png",
            })
    return prompts

def get_sticker_prompts():
    """Stickers voor Gelato print-on-demand — kawaii stijl"""
    prompts = []
    for char_id, char in CHARACTERS.items():
        subject = f"{char['subject_base']} waving hello with a big smile, full body view, centered"
        prompt = build_prompt(
            subject=subject,
            style=STYLE_STICKER,
            fmt="white background, centered composition, full character visible"
        )
        prompts.append({
            "character": char_id,
            "type": "sticker",
            "prompt": prompt,
            "aspect_ratio": "1:1 (1024 X 1024) px",
            "folder": "Mikkie",
            "filename": f"sticker_{char_id.lower()}.png",
        })
    return prompts

def get_social_prompts():
    """Social media posts voor Instagram/Facebook/X"""
    captions = [
        "going on a magical adventure, excited expression, backpack on",
        "discovering a secret glowing garden, eyes wide with wonder",
        "making new friends with forest animals, laughing joyfully",
        "finding a magical glowing crystal, holding it up in amazement",
        "celebrating with all MIKKIE WORLD friends, confetti and sparkles",
    ]
    prompts = []
    for char_id, char in CHARACTERS.items():
        subject = f"{char['subject_base']} {captions[0]} in {char['world']}"
        prompt = build_prompt(
            subject=subject,
            style=STYLE_SOCIAL,
            details="MIKKIE WORLD brand, outdoor adventure, inspiring for children",
            fmt="square 1:1 format, text space at bottom"
        )
        prompts.append({
            "character": char_id,
            "type": "social",
            "prompt": prompt,
            "aspect_ratio": "1:1 (1024 X 1024) px",
            "folder": "Mikkie",
            "filename": f"social_{char_id.lower()}.png",
        })
    return prompts

def get_banner_prompts():
    """Hero banners voor de MIKKIE WORLD website — 16:9"""
    prompts = []
    for char_id, char in CHARACTERS.items():
        subject = (
            f"{char['subject_base']} in a wide panoramic scene of {char['world']}, "
            f"small figure on right side, vast magical landscape on left"
        )
        prompt = build_prompt(
            subject=subject,
            style=STYLE_STORYBOOK,
            details="wide panoramic hero banner, text space on left side",
            fmt="16:9 landscape format, cinematic wide shot"
        )
        prompts.append({
            "character": char_id,
            "type": "banner",
            "prompt": prompt,
            "aspect_ratio": "16:9 (1344 X 768) px",
            "folder": "Mikkie",
            "filename": f"banner_{char_id.lower()}.png",
        })
    return prompts

def get_storybook_scripts():
    """
    Volledige storybook scripts per karakter — 8 pagina's elk
    Geoptimaliseerd voor Artistly's Script To Storybook tool
    Formaat: Page X: [tekst voor kind] + [actie-beschrijving voor illustratie]
    """
    return {
        "MIKKIE": """Page 1: Mikkie wakes up early in the morning, his crystal blue eyes sparkling with excitement. "Today is a magical adventure day!" he shouts, jumping out of bed.
Illustration: MIKKIE sitting up in bed, morning sunlight through window, green jacket hanging on chair, compass glowing on nightstand.

Page 2: He puts on his green adventure jacket and brown boots. His golden compass begins to glow with a mysterious light. It is pointing deep into the enchanted forest.
Illustration: MIKKIE standing at his front door, compass in hand, glowing golden, enchanted forest visible through the door.

Page 3: Deep in the enchanted forest, Mikkie discovers a hidden path covered in glowing mushrooms. Fireflies dance around him like tiny stars. "WOW!" he whispers.
Illustration: MIKKIE walking on a glowing mushroom path in a magical forest, fireflies all around, eyes wide with wonder.

Page 4: A tiny fairy appears and gives Mikkie a magical map. "Follow the crystal stream," she says with a wink. The map shows a treasure at the heart of the forest.
Illustration: MIKKIE receiving a glowing map from a tiny fairy, crystal stream visible in background, warm golden light.

Page 5: Mikkie crosses a rainbow bridge over a sparkling waterfall. His heart beats with courage and wonder. Every step brings him closer to the adventure.
Illustration: MIKKIE walking across a rainbow bridge, waterfall below, rainbow colors reflecting on his face, arms spread wide.

Page 6: At the end of the path, he finds a magical crystal cave filled with treasures. But the greatest treasure is a golden book — the Book of Adventures.
Illustration: MIKKIE inside a crystal cave, golden book glowing in the center, crystals all around, amazed expression.

Page 7: Mikkie shares his discovery with his friends Bubbles, Knoest, Fido, Nyx, Zera, and Ora. Together they celebrate with a magical feast under the stars.
Illustration: All 7 MIKKIE WORLD characters together around a magical feast table in the forest, stars above, warm firelight.

Page 8: As the sun sets, Mikkie looks at the stars and smiles. He writes in his golden book: "Every day is a new adventure." He closes his eyes and dreams of tomorrow.
Illustration: MIKKIE sitting on a hill, writing in golden book, sunset behind him, compass glowing, peaceful smile.

Art style: Pixar-inspired 3D storybook illustration, warm magical lighting, crystal blue and gold color palette, enchanted forest atmosphere, children's book quality.""",

        "BUBBLES": """Page 1: Bubbles the bubble fairy lives in a magical underwater kingdom where everything shimmers and glows in rainbow colors. She loves making her friends smile.
Illustration: BUBBLES floating in her underwater bubble kingdom, colorful coral reefs, friendly fish swimming around her, rainbow light.

Page 2: One morning, Bubbles discovers that all the colors have disappeared from the ocean. Everything is gray and dull. "Oh no!" she gasps. "We must find the Rainbow Pearl!"
Illustration: BUBBLES looking shocked at a gray, colorless ocean, her own colors still bright against the dull background.

Page 3: She swims through coral gardens and past friendly fish who are also worried. Every bubble she blows leaves a trail of sparkles, lighting the way forward.
Illustration: BUBBLES swimming through gray coral, her bubbles leaving colorful sparkle trails, fish following her hopefully.

Page 4: Deep in the ocean, Bubbles meets a shy seahorse who knows where the Rainbow Pearl is hidden. "Follow me!" he says, his tail curling with excitement.
Illustration: BUBBLES and a tiny seahorse face to face, seahorse pointing the way, underwater cave entrance visible.

Page 5: They swim through a magical cave filled with crystals. Bubbles' wings flutter with excitement and joy. The Rainbow Pearl must be close!
Illustration: BUBBLES and seahorse in a crystal cave, crystals catching light, BUBBLES' wings glowing, anticipation on her face.

Page 6: Bubbles finds the Rainbow Pearl and holds it up high. Instantly, all the colors burst back into the ocean in a magnificent explosion of light and joy!
Illustration: BUBBLES holding up the Rainbow Pearl, rainbow light exploding outward, ocean filling with color, fish cheering.

Page 7: The fish, seahorses, and mermaids all cheer for Bubbles. "You saved our world!" they sing together. Bubbles blushes and laughs with happiness.
Illustration: BUBBLES surrounded by celebrating sea creatures, mermaids, fish, seahorses, all cheering, confetti of bubbles.

Page 8: Bubbles blows the biggest bubble ever, and inside it, all her friends can see the whole beautiful ocean. "Samen is alles mogelijk!" she laughs.
Illustration: BUBBLES blowing a giant bubble containing a miniature view of the whole ocean, friends watching in awe.

Art style: Pixar-inspired 3D storybook illustration, underwater magical atmosphere, soft blue and turquoise palette, bubble and light effects, children's book quality.""",

        "KNOEST": """Page 1: Deep in the ancient forest lives Knoest, the wise tree spirit. He has watched over the forest for a thousand years, and every tree knows his name.
Illustration: KNOEST standing among ancient oak trees, morning mist, amber eyes glowing warmly, birds perched on his branches.

Page 2: One autumn morning, Knoest notices that the youngest trees are sad. Their leaves have stopped growing. Something is wrong deep in the forest.
Illustration: KNOEST kneeling beside small sad saplings, leaves drooping, his expression gentle and concerned.

Page 3: Knoest walks slowly through the forest, listening to the whispers of the wind. The trees are telling him a secret. He must find the blocked stream.
Illustration: KNOEST walking through the forest, ear tilted to listen, wind blowing leaves around him, light filtering through trees.

Page 4: He discovers that a little stream has been blocked by fallen rocks. Without water, the young trees cannot grow. Knoest knows what he must do.
Illustration: KNOEST looking at a blocked stream, rocks piled up, dry streambed, young trees wilting nearby.

Page 5: Knoest uses his ancient magic to move the rocks, one by one. His amber eyes glow with gentle power. The forest watches and waits.
Illustration: KNOEST lifting a large rock with glowing hands, amber light emanating from him, forest animals watching.

Page 6: The stream flows again! The young trees drink deeply and their leaves begin to unfurl, bright and green. The forest sings with joy.
Illustration: Water flowing freely, young trees springing back to life with bright green leaves, KNOEST smiling warmly.

Page 7: The forest animals come to thank Knoest — deer, rabbits, owls, and foxes. He smiles his ancient smile and pats each one gently.
Illustration: KNOEST surrounded by grateful forest animals, deer nuzzling his hand, rabbits at his feet, birds on his shoulders.

Page 8: Knoest sits back against his favorite oak tree and closes his eyes. "The forest always finds a way," he whispers. "De natuur vertelt haar geheimen."
Illustration: KNOEST resting peacefully against a massive oak, forest thriving around him, golden sunset, peaceful smile.

Art style: Pixar-inspired 3D storybook illustration, ancient forest atmosphere, deep green and amber palette, magical nature lighting, children's book quality.""",

        "FIDO": """Page 1: Fido is a small purple dragon who lives in the crystal cave mountains. He has golden wings and the biggest heart of any dragon in the land.
Illustration: FIDO sitting at the entrance of a crystal cave, golden glitter sparkling around him, mountains in background, happy expression.

Page 2: Unlike other dragons, Fido cannot breathe fire. He breathes sparkling golden glitter instead. The other dragons laugh at him. "You are not a real dragon!" they say.
Illustration: FIDO looking sad as bigger dragons laugh, golden glitter coming from his mouth instead of fire, head hanging low.

Page 3: One day, a little girl named Luna gets lost in the dark mountain caves. She is frightened and cannot find her way out. She sits down and cries.
Illustration: LUNA sitting alone in a dark cave, frightened, tears on her cheeks, darkness all around her.

Page 4: Fido hears her crying and flies to help. "Don't be scared!" he says in his small but brave voice. "I will light the way for you!"
Illustration: FIDO flying toward LUNA, golden glitter trailing behind him, bringing light into the dark cave.

Page 5: Fido breathes his golden glitter, and the caves fill with magical sparkling light. Luna can see everything clearly now. She gasps with wonder.
Illustration: FIDO breathing golden glitter that fills the cave with magical light, LUNA looking around in amazement, crystals sparkling.

Page 6: Together they find the way out of the caves. Luna hugs Fido tight. "You saved me with your special gift!" she says. "Your glitter is the most magical thing I have ever seen!"
Illustration: LUNA hugging FIDO at the cave exit, sunlight streaming in, FIDO's tail wagging with joy.

Page 7: The other dragons watch in amazement. Fido's golden glitter is the most magical thing they have ever seen. "We were wrong," they say. "You ARE a real dragon!"
Illustration: Bigger dragons looking at FIDO with admiration and regret, FIDO standing tall and proud, LUNA beside him.

Page 8: From that day on, Fido is celebrated as the most special dragon of all. "Vlieg mee op avontuur!" he roars happily, golden glitter filling the sky.
Illustration: FIDO flying high above the mountains, golden glitter trail across the sky, all dragons and LUNA cheering below.

Art style: Pixar-inspired 3D storybook illustration, crystal cave and mountain atmosphere, purple and gold palette, magical glitter effects, children's book quality.""",

        "NYX": """Page 1: Nyx is the princess of the night sky. Every evening she tends to all the stars, making sure they shine bright for the children sleeping below.
Illustration: NYX floating in the night sky, touching stars to make them glow, moonlit clouds below her, silver hair flowing.

Page 2: One night, Nyx notices that the smallest star is flickering and fading. "Little star, what is wrong?" she asks gently, cupping it in her hands.
Illustration: NYX holding a tiny flickering star in her cupped hands, concern on her face, other stars bright around her.

Page 3: The little star whispers that it feels forgotten. Everyone looks at the big, bright stars but never notices the small ones. It feels invisible and alone.
Illustration: NYX listening closely to the tiny star, her expression full of empathy, the small star barely glowing.

Page 4: Nyx takes the little star in her hands and carries it to the very center of the sky, where everyone can see it. "You deserve to be seen," she says.
Illustration: NYX flying with the tiny star toward the center of the sky, determination on her face, other stars watching.

Page 5: She teaches the little star a special twinkle — a pattern that no other star can do. Now it is truly unique and unmistakably itself.
Illustration: NYX teaching the star a special twinkling pattern, the star beginning to glow brighter, unique sparkle pattern.

Page 6: Children all over the world notice the new twinkling star and make wishes upon it. The little star glows with joy and gratitude.
Illustration: Children in beds looking out windows at the twinkling star, making wishes, the star glowing brilliantly.

Page 7: Nyx smiles as she watches from her silver moon throne. Every star matters, big or small. Every light in the darkness has a purpose.
Illustration: NYX on her moon throne, looking down at the world with a warm smile, the special star twinkling prominently.

Page 8: As dawn approaches, Nyx whispers goodnight to all her stars. "In het donker schijnen de sterren het helderst," she says softly, and the sky glows with love.
Illustration: NYX spreading her arms wide as dawn approaches, all stars glowing warmly, the special small star brightest of all.

Art style: Pixar-inspired 3D storybook illustration, night sky atmosphere, deep blue and silver palette, star and firefly effects, children's book quality.""",

        "ZERA": """Page 1: Zera is a guardian angel with golden wings who watches over children while they sleep. She leaves golden feathers as signs of her love and protection.
Illustration: ZERA flying over a sleeping village at night, golden light trailing from her wings, golden feathers floating down.

Page 2: One stormy night, a little boy named Tim is frightened by the thunder. He pulls his blanket over his head and trembles. "I am scared," he whispers.
Illustration: TIM hiding under blankets in bed, lightning outside the window, thunder visible as sound waves, frightened eyes.

Page 3: Zera flies down from the golden clouds and sits beside Tim's bed. She places her warm hand on his shoulder. He can feel the warmth even through his blanket.
Illustration: ZERA sitting beside TIM's bed, gentle golden light around her, hand on his shoulder, his expression beginning to calm.

Page 4: "Every storm passes," Zera whispers. "And after the storm, the world is fresh and new and beautiful. The rain is just the sky giving the earth a big drink."
Illustration: ZERA whispering to TIM, her words shown as golden light, TIM peeking out from under the blanket.

Page 5: She shows Tim the rainbow that appears after the rain. It stretches from one end of the sky to the other, filling the window with color and light.
Illustration: ZERA and TIM at the window, a magnificent rainbow outside, golden light mixing with rainbow colors, TIM's eyes wide.

Page 6: Tim reaches out and touches the rainbow through the window. It feels warm and soft, like a hug from someone who loves you very much.
Illustration: TIM's hand touching the rainbow, warm light on his face, ZERA smiling beside him, wonder replacing fear.

Page 7: Zera tucks Tim in and sings a gentle lullaby. The thunder seems far away now, and Tim's eyes grow heavy with peaceful sleep.
Illustration: ZERA tucking TIM in, singing softly, golden notes floating in the air, TIM's eyes drooping peacefully.

Page 8: As Tim falls asleep with a smile, Zera spreads her golden wings and flies back to the clouds. "Je bent nooit alleen," she says, leaving a golden feather on his pillow.
Illustration: ZERA flying away through the window, golden feather on TIM's pillow, TIM sleeping peacefully with a smile.

Art style: Pixar-inspired 3D storybook illustration, heavenly golden atmosphere, white and gold palette, soft glowing light, children's book quality.""",

        "ORA": """Page 1: Ora the wise owl lives in the highest branch of the Ancient Library Tree. His golden spectacles shine in the moonlight. He has read every book ever written.
Illustration: ORA perched on the highest branch of a massive tree filled with glowing books, moonlight, spectacles gleaming.

Page 2: Every evening, children from the village come to sit beneath his tree and listen to his stories of faraway lands and magical discoveries.
Illustration: ORA looking down at a circle of children sitting below his tree, warm firelight, children's faces lit with wonder.

Page 3: One day, a girl named Sophie tells Ora she is afraid to go to school. "What if I am not smart enough?" she asks, her voice small and worried.
Illustration: SOPHIE looking up at ORA with worried eyes, ORA tilting his head with kind attention, scroll in his wing.

Page 4: Ora adjusts his spectacles and looks at Sophie kindly. "Wisdom is not about knowing everything," he says. "It is about being curious enough to ask questions."
Illustration: ORA leaning down toward SOPHIE, spectacles glinting, warm amber eyes, SOPHIE listening intently.

Page 5: He opens his great scroll and shows Sophie all the questions he has asked in his long life. There are thousands of them. "Every question is a step toward wisdom," he says.
Illustration: ORA unrolling a massive scroll covered in questions, SOPHIE's eyes wide, golden light from the scroll.

Page 6: "The bravest thing you can do," Ora continues, "is say: I don't know yet. Those three words open every door in the universe."
Illustration: ORA pointing to three glowing words "I don't know" on the scroll, doors of light opening around them.

Page 7: Sophie thinks about this. Then she smiles and asks her very first brave question: "Ora, how do stars know where to shine?" Ora laughs with delight.
Illustration: SOPHIE asking her question, ORA laughing warmly, stars appearing around them in response to the question.

Page 8: "Now you are a true seeker of wisdom," Ora says. He gives Sophie a tiny golden feather quill. "Write down every question you ever have." "Kennis is de grootste schat."
Illustration: ORA handing SOPHIE a golden quill, SOPHIE holding it with both hands, both smiling, stars and books around them.

Art style: Pixar-inspired 3D storybook illustration, ancient library tree atmosphere, warm amber and gold palette, magical book and scroll effects, children's book quality.""",
    }

# ─── State Management ─────────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"generated": [], "last_run": None, "total_images": 0, "session_count": 0}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))

# ─── Playwright Browser Automation ────────────────────────────────────────────

async def verify_session(page, context):
    """Laad en verifieer de opgeslagen sessie"""
    if not SESSION_FILE.exists():
        log.error("Geen sessie gevonden. Voer eerst: mikkie-artistly save-session")
        return False

    cookies = json.loads(SESSION_FILE.read_text())
    await context.add_cookies(cookies)
    log.info(f"{len(cookies)} cookies geladen")

    try:
        await page.goto("https://app.artistly.ai/dashboard",
                        wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass
    await asyncio.sleep(3)

    if "login" in page.url.lower():
        log.error("❌ Sessie verlopen. Voer uit: mikkie-artistly save-session")
        return False

    log.info("✅ Sessie geldig — ingelogd als Hendrik!")
    return True

async def generate_image(page, prompt_data):
    """
    Genereer één afbeelding via AI Image Designer v6
    Bewezen flow (live getest):
    1. Navigeer naar image-designer-v6
    2. Klik Create From Prompt
    3. Scroll naar y=500 (textarea staat buiten viewport)
    4. Vul textarea via JS (React-compatible)
    5. Selecteer folder via JS
    6. Klik #generate_image_flux
    7. Wacht op redirect naar personal-designs
    """
    char_id = prompt_data["character"]
    content_type = prompt_data["type"]
    prompt = prompt_data["prompt"]
    aspect = prompt_data.get("aspect_ratio", "1:1 (1024 X 1024) px")
    folder = prompt_data.get("folder", "Mikkie")

    log.info(f"🎨 [{char_id}] {content_type} — genereren...")

    try:
        # Stap 1: Navigeer naar image designer
        try:
            await page.goto("https://app.artistly.ai/ai/image-designer-v6",
                            wait_until="domcontentloaded", timeout=30000)
        except Exception:
            pass
        await asyncio.sleep(2)

        # Stap 2: Klik Create From Prompt via JS op de parent group div
        try:
            await page.wait_for_selector(".group.cursor-pointer", timeout=10000)
            clicked_cat = await page.evaluate("""
                () => {
                    const divs = document.querySelectorAll('.group.cursor-pointer');
                    for (const d of divs) {
                        if (d.textContent.includes('Create From Prompt')) {
                            d.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            if clicked_cat:
                log.info("   Categorie 'Create From Prompt' geklikt via JS")
            else:
                log.warning("   Categorie klik via JS mislukt — probeer directe klik")
                await page.click("text=Create From Prompt")
        except Exception as e:
            log.warning(f"   Categorie klik mislukt: {e}")

        await asyncio.sleep(2)

        # Stap 3: Wacht op textarea (altijd aanwezig in DOM, ook voor klik)
        # Gebruik state='attached' omdat het element al in DOM staat maar mogelijk niet visible
        try:
            await page.wait_for_selector(
                'textarea[placeholder="Enter prompt here"]',
                state='attached',
                timeout=10000
            )
            log.info("   Textarea gevonden")
        except Exception:
            # Fallback: wacht gewoon 3 seconden en ga door
            log.warning("   Textarea wait timeout — ga toch door")
            await asyncio.sleep(3)

        # Stap 4: Vul textarea via JS (React-compatible native value setter)
        filled = await page.evaluate("""
            (prompt) => {
                const ta = document.querySelector('textarea[placeholder="Enter prompt here"]');
                if (!ta) return false;
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLTextAreaElement.prototype, 'value'
                ).set;
                setter.call(ta, prompt);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                ta.focus();
                return true;
            }
        """, prompt)

        if not filled:
            log.error(f"   ❌ Textarea niet gevonden voor {char_id}")
            return False

        log.info(f"   Prompt ingevuld ({len(prompt)} tekens)")
        await asyncio.sleep(1)

        # Scroll naar beneden zodat Generate knop zichtbaar wordt
        await page.evaluate("window.scrollTo(0, 800)")
        await asyncio.sleep(1)

        # Stap 5: Selecteer folder "Mikkie"
        folder_ok = await page.evaluate("""
            (folder) => {
                const selects = document.querySelectorAll('select');
                for (const sel of selects) {
                    const opts = Array.from(sel.options).map(o => o.text);
                    if (opts.includes(folder)) {
                        const opt = Array.from(sel.options).find(o => o.text === folder);
                        if (opt) {
                            sel.value = opt.value;
                            sel.dispatchEvent(new Event('change', { bubbles: true }));
                            return true;
                        }
                    }
                }
                return false;
            }
        """, folder)

        if folder_ok:
            log.info(f"   Folder '{folder}' geselecteerd")

        await asyncio.sleep(1)

        # Stap 6: Klik Generate Image via ID
        clicked = await page.evaluate("""
            () => {
                const btn = document.getElementById('generate_image_flux');
                if (btn) { btn.click(); return 'id'; }
                const btns = document.querySelectorAll('button');
                for (const b of btns) {
                    if (b.textContent.trim() === 'Generate Image') {
                        b.click();
                        return 'text';
                    }
                }
                return null;
            }
        """)

        if not clicked:
            log.error(f"   ❌ Generate knop niet gevonden voor {char_id}")
            return False

        log.info(f"   Generate Image geklikt (via {clicked})")

        # Stap 7: Wacht op redirect naar personal-designs (bewijs van succes)
        try:
            await page.wait_for_url("**/personal-designs**", timeout=60000)
            log.info(f"   ✅ Succesvol gegenereerd: {char_id} — {content_type}")
            return True
        except Exception:
            if "personal-designs" in page.url:
                log.info(f"   ✅ Succesvol gegenereerd: {char_id} — {content_type}")
                return True
            log.warning(f"   ⚠️  Timeout — mogelijk toch gelukt voor {char_id}")
            return False

    except Exception as e:
        log.error(f"   ❌ Fout bij {char_id} {content_type}: {e}")
        return False

async def generate_storybook(page, character_id):
    """
    Genereer een compleet storybook via Script To Storybook
    Artistly's AI Storybook Studio
    """
    scripts = get_storybook_scripts()
    script = scripts.get(character_id, "")
    char = CHARACTERS[character_id]

    log.info(f"📖 Storybook genereren voor {char['nl_name']}...")

    try:
        await page.goto("https://app.artistly.ai/ai/ai-storybook-studio",
                        wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Klik Script To Storybook
        await page.evaluate("""
            const btns = document.querySelectorAll('button');
            for (const btn of btns) {
                if (btn.textContent.includes('Script To Storybook') &&
                    !btn.textContent.includes('V2')) {
                    btn.click();
                    break;
                }
            }
        """)
        await asyncio.sleep(1500)

        # Klik Create New Story
        await page.evaluate("""
            const btns = document.querySelectorAll('button');
            for (const btn of btns) {
                if (btn.textContent.includes('Create New Story')) {
                    btn.click();
                    break;
                }
            }
        """)
        await asyncio.sleep(2000)

        await page.evaluate("window.scrollTo(0, 600)")
        await asyncio.sleep(1000)

        # Selecteer AI Character optie
        await page.evaluate("""
            const aiBtn = document.getElementById('ai');
            if (aiBtn) aiBtn.click();
        """)
        await asyncio.sleep(500)

        # Vul script in
        filled = await page.evaluate("""
            (script) => {
                const ta = document.querySelector(
                    'textarea[placeholder="Enter your story script here..."]'
                );
                if (!ta) return false;
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLTextAreaElement.prototype, 'value'
                ).set;
                setter.call(ta, script);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                ta.focus();
                return true;
            }
        """, script)

        if not filled:
            log.error(f"   ❌ Script textarea niet gevonden voor {character_id}")
            return False

        log.info(f"   Script ingevuld ({len(script)} tekens)")
        await asyncio.sleep(500)

        # Klik Generate
        clicked = await page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.trim() === 'Generate') {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }
        """)

        if clicked:
            log.info(f"   ✅ Storybook generatie gestart voor {char['nl_name']}")
            await asyncio.sleep(5000)
            return True

        return False

    except Exception as e:
        log.error(f"   ❌ Storybook fout voor {character_id}: {e}")
        return False

async def generate_maze(page, character_id):
    """Genereer doolhof-puzzels via Kids Puzzles → Maze Generator"""
    char = CHARACTERS[character_id]
    maze_configs = {
        "MIKKIE":  {"level": "Medium", "theme": f"Enchanted forest adventure with MIKKIE the brave boy, magical trees, hidden paths, glowing mushrooms"},
        "BUBBLES": {"level": "Easy",   "theme": f"Underwater bubble kingdom with BUBBLES the fairy, coral reefs, friendly fish, rainbow pearls"},
        "KNOEST":  {"level": "Medium", "theme": f"Ancient forest with KNOEST the tree spirit, wise old trees, forest animals, magical streams"},
        "FIDO":    {"level": "Medium", "theme": f"Crystal cave mountains with FIDO the dragon, sparkling crystals, dragon eggs, golden treasure"},
        "NYX":     {"level": "Hard",   "theme": f"Night sky kingdom with NYX the star princess, constellations, shooting stars, moon castles"},
        "ZERA":    {"level": "Easy",   "theme": f"Golden cloud heaven with ZERA the guardian angel, rainbow bridges, fluffy clouds, golden feathers"},
        "ORA":     {"level": "Hard",   "theme": f"Ancient library tree with ORA the wise owl, magical books, scrolls, knowledge crystals"},
    }
    config = maze_configs.get(character_id, {"level": "Medium", "theme": "Adventure maze"})

    log.info(f"🧩 Doolhof genereren voor {char['nl_name']} ({config['level']})...")

    try:
        await page.goto("https://app.artistly.ai/ai/kids-puzzles",
                        wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Klik Maze Generator
        await page.evaluate("""
            const btns = document.querySelectorAll('button');
            for (const btn of btns) {
                if (btn.textContent.trim() === 'Maze Generator') {
                    btn.click();
                    break;
                }
            }
        """)
        await asyncio.sleep(1500)
        await page.evaluate("window.scrollTo(0, 400)")
        await asyncio.sleep(500)

        # Selecteer "Maze with Border"
        await page.evaluate("""
            const divs = document.querySelectorAll('div');
            for (const div of divs) {
                if (div.textContent.trim() === 'Maze with Border') {
                    div.click();
                    break;
                }
            }
        """)
        await asyncio.sleep(300)

        # Selecteer level
        level = config["level"]
        await page.evaluate(f"""
            const selects = document.querySelectorAll('select');
            for (const sel of selects) {{
                const opts = Array.from(sel.options).map(o => o.text);
                if (opts.some(o => o.includes('Easy') || o.includes('Medium') || o.includes('Hard'))) {{
                    const opt = Array.from(sel.options).find(o => o.text.includes('{level}'));
                    if (opt) {{
                        sel.value = opt.value;
                        sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}
            }}
        """)
        await asyncio.sleep(300)

        # Vul thema in
        theme = config["theme"]
        await page.evaluate(f"""
            const inputs = document.querySelectorAll('input[type="text"]');
            for (const inp of inputs) {{
                if (inp.placeholder && (inp.placeholder.includes('Animals') || inp.placeholder.includes('theme'))) {{
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(inp, {json.dumps(theme)});
                    inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    break;
                }}
            }}
        """)
        await asyncio.sleep(300)

        # Klik Generate Mazes
        clicked = await page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.trim() === 'Generate Mazes') {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }
        """)

        if clicked:
            log.info(f"   ✅ Doolhof generatie gestart voor {char['nl_name']}")
            await asyncio.sleep(3000)
            return True

        return False

    except Exception as e:
        log.error(f"   ❌ Doolhof fout voor {character_id}: {e}")
        return False

async def run_batch(command, characters=None):
    """Voer een batch content-generatie uit"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        log.error("Playwright niet geïnstalleerd. Voer uit: pip3 install playwright && playwright install chromium")
        return

    if not SESSION_FILE.exists():
        log.error("Geen sessie gevonden. Voer eerst: mikkie-artistly save-session")
        return

    if characters is None:
        characters = list(CHARACTERS.keys())

    state = load_state()
    state["session_count"] += 1
    state["last_run"] = datetime.datetime.now().isoformat()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        try:
            if not await verify_session(page, context):
                return

            success = 0
            total = 0

            if command == "test":
                total = 1
                test_data = {
                    "character": "MIKKIE",
                    "type": "test cover",
                    "prompt": build_prompt(
                        subject=f"{CHARACTERS['MIKKIE']['subject_base']} standing heroically in {CHARACTERS['MIKKIE']['world']}",
                        style=STYLE_COVER,
                        details="MIKKIE WORLD test image",
                        fmt="square 1:1 format"
                    ),
                    "aspect_ratio": "1:1 (1024 X 1024) px",
                    "folder": "Mikkie",
                }
                if await generate_image(page, test_data):
                    success = 1

            elif command == "covers":
                prompts = [p for p in get_cover_prompts() if p["character"] in characters]
                total = len(prompts)
                for pd in prompts:
                    if await generate_image(page, pd):
                        success += 1
                        state["generated"].append({"character": pd["character"], "type": "cover", "timestamp": datetime.datetime.now().isoformat()})
                        state["total_images"] += 1
                    await asyncio.sleep(2)

            elif command == "coloring":
                prompts = [p for p in get_coloring_prompts() if p["character"] in characters]
                total = len(prompts)
                for pd in prompts:
                    if await generate_image(page, pd):
                        success += 1
                        state["total_images"] += 1
                    await asyncio.sleep(2)

            elif command == "stickers":
                prompts = [p for p in get_sticker_prompts() if p["character"] in characters]
                total = len(prompts)
                for pd in prompts:
                    if await generate_image(page, pd):
                        success += 1
                        state["total_images"] += 1
                    await asyncio.sleep(2)

            elif command == "social":
                prompts = [p for p in get_social_prompts() if p["character"] in characters]
                total = len(prompts)
                for pd in prompts:
                    if await generate_image(page, pd):
                        success += 1
                        state["total_images"] += 1
                    await asyncio.sleep(2)

            elif command == "banners":
                prompts = [p for p in get_banner_prompts() if p["character"] in characters]
                total = len(prompts)
                for pd in prompts:
                    if await generate_image(page, pd):
                        success += 1
                        state["total_images"] += 1
                    await asyncio.sleep(2)

            elif command == "storybooks":
                total = len(characters)
                for char_id in characters:
                    if await generate_storybook(page, char_id):
                        success += 1
                    await asyncio.sleep(3)

            elif command == "mazes":
                total = len(characters)
                for char_id in characters:
                    if await generate_maze(page, char_id):
                        success += 1
                    await asyncio.sleep(3)

            elif command == "all":
                all_prompts = (
                    get_cover_prompts() +
                    get_coloring_prompts() +
                    get_sticker_prompts() +
                    get_social_prompts() +
                    get_banner_prompts()
                )
                all_prompts = [p for p in all_prompts if p["character"] in characters]
                total = len(all_prompts)
                for pd in all_prompts:
                    if await generate_image(page, pd):
                        success += 1
                        state["total_images"] += 1
                    await asyncio.sleep(2)

            save_state(state)
            log.info(f"\n{'='*55}")
            log.info(f"✅ Klaar: {success}/{total} succesvol gegenereerd")
            log.info(f"📁 Bekijk resultaten: app.artistly.ai/personal-designs")
            log.info(f"{'='*55}\n")

        finally:
            await browser.close()

async def run_daemon():
    """24/7 daemon modus — automatisch schema"""
    log.info("🚀 MIKKIE WORLD Artistly Agent — 24/7 daemon gestart")
    SCHEDULE = {
        0: ("covers",    "Maandag: Gumroad covers"),
        2: ("coloring",  "Woensdag: Kleurplaten"),
        4: ("social",    "Vrijdag: Social posts"),
        6: ("stickers",  "Zondag: Stickers"),
    }
    while True:
        now = datetime.datetime.now()
        if now.hour == 7 and now.weekday() in SCHEDULE:
            cmd, desc = SCHEDULE[now.weekday()]
            log.info(f"📅 Geplande taak: {desc}")
            await run_batch(cmd)
            await asyncio.sleep(23 * 3600)
        else:
            log.info(f"⏰ Wachten... volgende check over 30 min ({now.strftime('%H:%M')})")
            await asyncio.sleep(1800)

def save_session_interactive():
    """Eenmalig inloggen via zichtbare browser, sessie opslaan"""
    from playwright.sync_api import sync_playwright
    print("\n🔐 ARTISTLY SESSIE OPSLAAN")
    print("=" * 45)
    print("Een browser venster opent nu.")
    print("1. Klik 'Login with Google'")
    print("2. Log in met hendrik.broeze@gmail.com")
    print("3. Zodra je het Artistly dashboard ziet: druk Enter\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto("https://app.artistly.ai/login", wait_until="domcontentloaded")
        print("Browser geopend. Log in via Google...")
        input("Druk Enter zodra je het dashboard ziet: ")
        cookies = context.cookies()
        SESSION_FILE.write_text(json.dumps(cookies, indent=2))
        print(f"\n✅ {len(cookies)} cookies opgeslagen!")
        print("Test nu: mikkie-artistly test\n")
        browser.close()

# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="MIKKIE WORLD Artistly AI Content Agent v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commando's:
  test        Test: 1 MIKKIE cover genereren
  covers      Gumroad covers (7 afbeeldingen)
  coloring    Kleurplaten (35 afbeeldingen, 5 per karakter)
  stickers    Kawaii stickers (7 afbeeldingen)
  social      Social media posts (7 afbeeldingen)
  banners     Website hero banners (7 afbeeldingen)
  storybooks  Complete storybooks (7 boekjes via Script To Storybook)
  mazes       Doolhof puzzels (7 sets via Kids Puzzles)
  all         Alles: covers + kleurplaten + stickers + social + banners (63 afb.)
  daemon      24/7 automatisch schema
  save-session  Eenmalig inloggen via browser (vereist bij eerste gebruik)
  status      Toon statistieken
  scripts     Toon alle storybook scripts
  prompts     Toon alle prompts (gebruik: prompts covers)
  log         Toon laatste 50 log-regels

Voorbeelden:
  mikkie-artistly test
  mikkie-artistly covers
  mikkie-artistly covers --characters MIKKIE BUBBLES
  mikkie-artistly coloring --characters NYX
  mikkie-artistly all
  mikkie-artistly daemon
        """
    )
    parser.add_argument("command", nargs="?", default="status")
    parser.add_argument("--characters", "-c", nargs="+",
                        choices=list(CHARACTERS.keys()),
                        help="Specifieke karakters (standaard: alle 7)")
    args = parser.parse_args()

    cmd = args.command
    chars = args.characters

    if cmd == "status":
        state = load_state()
        print("\n🎨 MIKKIE WORLD Artistly Agent v3.0")
        print("=" * 50)
        print(f"  Sessie:          {'✅ Aanwezig' if SESSION_FILE.exists() else '❌ Voer save-session uit'}")
        print(f"  Totale afb.:     {state.get('total_images', 0)}")
        print(f"  Sessies:         {state.get('session_count', 0)}")
        print(f"  Laatste run:     {state.get('last_run', 'Nog niet gestart')}")
        print(f"\n  Prompt formule (Paul Ponna):")
        print(f"    Subject + Style + Details + Format")
        print(f"\n  Content types beschikbaar:")
        print(f"    covers (7)  |  coloring (35)  |  stickers (7)")
        print(f"    social (7)  |  banners (7)    |  storybooks (7)")
        print(f"    mazes (7)   |  all (63)")
        print("=" * 50 + "\n")

    elif cmd == "save-session":
        save_session_interactive()

    elif cmd == "scripts":
        scripts = get_storybook_scripts()
        for char_id, script in scripts.items():
            char = CHARACTERS[char_id]
            print(f"\n{'='*60}")
            print(f"  {char['nl_name'].upper()} — bewaker van {char['guardian_of']}")
            print(f"  Catchphrase: \"{char['catchphrase']}\"")
            print(f"{'='*60}")
            print(script[:500] + "...\n")

    elif cmd == "prompts":
        content_type = sys.argv[2] if len(sys.argv) > 2 else "covers"
        prompt_map = {
            "covers": get_cover_prompts,
            "coloring": get_coloring_prompts,
            "stickers": get_sticker_prompts,
            "social": get_social_prompts,
            "banners": get_banner_prompts,
        }
        func = prompt_map.get(content_type, get_cover_prompts)
        for pd in func():
            print(f"\n[{pd['character']}] {pd['type']}")
            print(f"  {pd['prompt'][:200]}...")

    elif cmd == "log":
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text().splitlines()
            print("\n".join(lines[-50:]))
        else:
            print("Geen log gevonden.")

    elif cmd in ["test", "covers", "coloring", "stickers", "social",
                 "banners", "storybooks", "mazes", "all"]:
        asyncio.run(run_batch(cmd, chars))

    elif cmd == "daemon":
        print("🔄 Artistly Agent gestart in 24/7 daemon modus (Ctrl+C om te stoppen)")
        asyncio.run(run_daemon())

    else:
        parser.print_help()

if __name__ == "__main__":
    main()

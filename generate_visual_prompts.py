"""
Generate visual_prompt fields for every event in data_with_prompts.json.

Each visual_prompt is a short, concrete scene description (1-2 sentences)
that tells an image model WHAT to paint — the subject, composition, and mood.
The consistent sumi-e style suffix is added later by image_generator.py.

Usage:
    python generate_visual_prompts.py

This reads src/data_with_prompts.json, adds a "visual_prompt" key to each
event, and writes the result back.
"""

import json

# ── Subject-specific visual descriptions ──
# Maps event id -> a concrete visual scene for the ink wash painting.
# These describe WHAT to paint, not HOW (style is added by image_generator.py).

VISUAL_PROMPTS = {
    # ═══════════════════════════════════════════
    # LEVEL 0 — The Cosmic Dawn
    # ═══════════════════════════════════════════
    1:   "A single point of intense light exploding outward into darkness, radiating tendrils of energy in all directions",
    101: "Tiny luminous circles drifting together in pairs, delicate orbs of light coalescing from a haze of mist",
    102: "Vast empty darkness with the faintest wisps of smoke or fog drifting through an endless void",
    2:   "A brilliant starburst of light igniting in the center of deep darkness, sharp rays piercing outward",
    103: "Clusters of tiny bright dots swirling together into a loose spiral shape, scattered across darkness",
    3:   "A grand spiral form made of flowing ink, swirling like a whirlpool of stars and dust",
    104: "A massive star tearing itself apart, shards and fragments scattering outward in a violent bloom",
    105: "A single radiant circle glowing with inner fire, hovering in serene darkness",
    4:   "A rough sphere of molten rock forming from swirling debris, glowing cracks across its surface",
    106: "Two spheres colliding, debris arcing upward and forming a smaller companion sphere nearby",
    107: "Gentle waves stretching across a curved surface, vast and still, reflecting a dim sky",
    5:   "A dark pool of water with bubbles rising from below, tiny delicate forms emerging from the depths",
    108: "Abstract flowing shapes like cellular forms dividing and multiplying under a microscope",
    6:   "Layers of rock and sediment pressed together, ancient and compressed, with faint fossil impressions",
    109: "A wave of pale light sweeping across a dark sphere, illuminating its surface for the first time",
    110: "Lush fern-like forms and primitive plant shapes emerging from wet ground near water",

    # ═══════════════════════════════════════════
    # LEVEL 1 — The Living World
    # ═══════════════════════════════════════════
    7:   "A massive dark shape beneath ocean waves, an ancient armored fish with heavy jaws",
    201: "Delicate translucent jellyfish-like creatures floating in dark water, trailing soft tendrils",
    202: "A lobe-finned fish pulling itself onto a rocky shore, half in water, half on land",
    8:   "Towering tree ferns and giant dragonflies in a dense primeval swamp, steaming and lush",
    203: "A cluster of pale round eggs on mossy ground, the first eggs laid on dry land",
    204: "A large sail-backed reptile silhouetted against a barren landscape, standing in profile",
    9:   "A great extinction — lifeless seas, volcanic ash falling like snow, dead trees on a barren shore",
    205: "Massive long-necked dinosaur silhouettes walking across a misty plain at dawn",
    206: "A tiny furry creature with bright eyes crouched beneath enormous fern leaves, hiding in shadow",
    10:  "A feathered creature mid-leap between a branch and the air, wings spread, caught between worlds",
    207: "Flowering blossoms opening for the first time, petals unfurling from tight buds on bare branches",
    208: "A massive asteroid streaking through the sky trailing fire, the ground below trembling",
    209: "Small birds perched on branches overlooking a devastated but recovering landscape with new growth",
    11:  "Tall grass stretching to the horizon under an open sky, the first grasslands spreading endlessly",
    210: "A woolly mammoth silhouetted against a frozen tundra, breath visible in the frigid air",
    211: "A saber-toothed cat crouched on a rocky outcrop, powerful and alert, muscles tensed",

    # ═══════════════════════════════════════════
    # LEVEL 2 — The Rise of Kin
    # ═══════════════════════════════════════════
    12:  "A small upright figure walking across an open savanna, leaving footprints in soft ground",
    301: "Rough stone tools scattered on the ground — sharp flakes and a core stone, primitive and purposeful",
    302: "A circle of early humans huddled around a small fire in a cave entrance, warm light against darkness",
    303: "A lone figure standing at the edge of a vast body of water, gazing toward a distant shore",
    13:  "Several figures gathered around a large campfire at night, flames casting dancing shadows",
    304: "A hand pressing against a cave wall, leaving a red ochre handprint among painted animals",
    305: "A figure shaping a small clay form, a round female figure held delicately in rough hands",
    14:  "Dots of ochre paint on a cave ceiling forming the shape of a bull, surrounded by smaller animals",
    306: "A figure stringing a bow made from a bent branch and sinew, arrows gathered nearby",
    307: "A bone flute with carved holes lying on a flat stone, as if just set down",
    15:  "A solitary wolf-like dog sitting beside a human figure near a fire, loyal and watchful",
    308: "Small round dwellings made of branches and hides clustered together, smoke rising from center holes",
    309: "A needle made from bone piercing through animal hide, thread pulled taut in careful stitching",
    310: "Massive ice sheets retreating, meltwater flowing in braided rivers across a newly green landscape",
    311: "Hands pressing grain seeds into dark tilled earth, the first deliberate planting",
    312: "A decorated human skull with shells and flowers placed carefully in a shallow earth grave",

    # ═══════════════════════════════════════════
    # LEVEL 3 — Seeds of Civilization
    # ═══════════════════════════════════════════
    313: "Rows of wheat or barley growing in a cleared field beside a river, neat and intentional",
    314: "A goat and a sheep standing beside a simple reed fence, domesticated and calm",
    315: "A round clay pot being formed by hands, wet clay spiraling upward from a flat base",
    316: "A cluster of simple mud-brick houses forming a tiny town, ladders leading to rooftops",
    317: "A massive stone pillar carved with animal reliefs — lions, birds, snakes — standing in a circle of others",
    318: "Two figures exchanging a bundle of grain for a piece of obsidian, a simple trade",
    319: "A large wooden wheel attached to a crude axle, leaning against a mud wall",
    320: "Molten copper being poured from a clay crucible into a stone mold, glowing orange",
    321: "Mud-brick walls rising around a settlement, thick and protective, with a narrow gate",
    16:  "A massive stepped pyramid seen from a low angle, its peak touching the sky, monumental and austere",
    322: "Marks pressed into a wet clay tablet with a reed stylus — wedge-shaped cuneiform symbols",
    323: "A figure in simple robes standing above terraced rice fields flooded with shallow water",
    324: "A long boat with a square sail gliding along a wide river, papyrus reeds on the banks",
    325: "Stone monoliths standing in a circle on a windswept plain, casting long shadows at dawn",
    326: "A figure pulling a plow drawn by two oxen through dark earth, furrows stretching behind",
    327: "A grand stepped ziggurat with a long staircase, seen against a flat river plain",

    # ═══════════════════════════════════════════
    # LEVEL 4 — Empires & Faiths
    # ═══════════════════════════════════════════
    401: "A tall stone stele covered in dense rows of carved text, standing upright in a courtyard",
    402: "A single figure seated in meditation beneath a spreading tree, utterly still, radiating calm",
    17:  "Ranks of identical clay soldiers standing in rows, an underground terracotta army",
    403: "A bearded figure on a mountaintop holding two stone tablets, clouds swirling around the peak",
    18:  "White marble columns and a triangular pediment of a Greek temple perched on a rocky hilltop",
    404: "A figure nailed to a wooden cross on a barren hilltop, silhouetted against a dark sky",
    405: "A massive domed building with an oculus at the top, light streaming down through the opening",
    406: "A lone figure kneeling in prayer in a vast desert, the crescent moon rising above",
    19:  "A long straight road stretching to the horizon, lined with milestones, built of fitted stone",
    407: "A loaded camel caravan crossing sand dunes in a long winding line, silhouetted against sunset",
    408: "A grand colosseum or arena viewed from above, its oval shape casting geometric shadows",
    409: "Stone temples with ornate stepped towers rising from a jungle canopy, vines creeping up the walls",
    410: "A robed figure writing on a long paper scroll with a brush, Chinese characters flowing downward",
    411: "Massive carved stone heads with broad faces emerging from jungle undergrowth, ancient and weathered",
    412: "An ornate Byzantine mosaic of a haloed figure, gold tiles glinting, solemn and iconic",
    413: "A stepped pyramid in a jungle clearing with a steep staircase, Mayan glyphs on the face",
    414: "A domed mosque with a tall minaret beside it, geometric patterns decorating the facade",
    415: "Longships with dragon-headed prows cutting through rough seas, striped sails billowing",
    416: "A figure in robes holding a large open book, standing in an arched doorway of a library",
    417: "Massive stone statues on a barren island hillside, their long faces gazing outward to the sea",
    418: "A grand temple complex with concentric rectangular walls and a central tower, reflected in a moat",
    419: "A mounted archer on horseback at full gallop, bow drawn, across a vast open steppe",

    # ═══════════════════════════════════════════
    # LEVEL 5 — The Medieval World
    # ═══════════════════════════════════════════
    420: "A stone castle on a hilltop surrounded by a moat, banners flying from the towers",
    20:  "A boot print pressed into grey lunar dust, clear and sharp, the first step on another world",
    421: "A page of illuminated manuscript with ornate gold and blue capital letters and tiny painted scenes",
    422: "A large wooden Viking longship pulled up on a sandy beach, shields lining its sides",
    423: "A massive cathedral with flying buttresses and a rose window, towering over a medieval town",
    424: "Rats scurrying through a narrow medieval street, dark and ominous, doors marked with crosses",
    425: "A figure in a turban studying an astrolabe, surrounded by scrolls and astronomical instruments",
    426: "A wooden printing press with inked type blocks and a fresh printed page being pulled from it",
    427: "Terraced green fields carved into steep mountainsides, an Incan citadel perched at the summit",
    428: "An ornate Chinese treasure ship with red sails, enormous and grand, dwarfing nearby boats",
    429: "A grand mosque with horseshoe arches and intricate geometric tile patterns, a courtyard fountain",
    430: "Samurai warriors in full armor facing each other across a misty battlefield",
    431: "A tall stone tower in a West African city, surrounded by mud-brick walls and bustling market stalls",
    432: "Mounted warriors with bows and curved swords sweeping across a vast grassland, dust rising",
    433: "A massive stone wall stretching across mountain ridges into the distance, watchtowers at intervals",
    434: "A grand bazaar with arched ceilings, merchants displaying silk, spices, and ceramics in stalls",
    435: "A robed scholar writing with a quill at a desk in a monastery scriptorium, candlelight flickering",
    436: "A compass needle pointing north, resting on an old nautical chart with coastline drawings",
    437: "Burning ships at harbor, Greek fire arcing through the air in bright streams over dark water",
    438: "A grand stone church with onion domes in a snowy landscape, gold crosses gleaming on top",

    # ═══════════════════════════════════════════
    # LEVEL 6 — Exploration & Enlightenment
    # ═══════════════════════════════════════════
    21:  "The sun expanding into a bloated red giant, dwarfing the tiny silhouette of Earth in the foreground",
    439: "A figure peering through an early telescope pointed at the night sky, stars and planets visible",
    440: "A figure standing before a large anatomical drawing of the human body, studying its interior",
    441: "An apple falling from a tree branch, a figure seated below watching it descend",
    442: "Enslaved figures crowded in the hold of a wooden ship, chains visible, dark and harrowing",
    443: "Elaborate formal gardens stretching out from a grand symmetrical palace, perfectly geometric",
    22:  "Two massive spiral galaxies colliding in slow motion, spirals of stars merging and warping into a new shape",
    444: "A bubbling glass flask connected to tubes and retorts, steam rising, an early chemistry experiment",
    445: "A grand sailing ship rounded a rocky cape at the bottom of Africa, waves crashing against cliffs",
    446: "A massive Aztec sun stone calendar carved in intricate concentric circles, center face glaring",
    447: "A figure in a powdered wig writing with a quill at a desk by candlelight, papers stacked high",
    448: "A simple spinning wheel beside a mechanical spinning jenny, old and new side by side",
    449: "Tea leaves spilling from a wooden crate into harbor water, a ship in the background",
    450: "An ornate harpsichord in a Baroque music room, sheet music open on the stand",
    451: "A hot air balloon rising above a crowd of tiny figures, the balloon brightly striped against clouds",
    452: "A robed figure examining a specimen through an early microscope, tiny organisms sketched nearby",
    453: "Stacked rows of sugar cane in a plantation field, a windmill processing mill in the background",
    454: "An ornate astronomical clock on a tower facade, with rotating dials showing moon phases and zodiac",
    455: "A grand library interior with floor-to-ceiling bookshelves, a reading figure dwarfed by knowledge",

    # ═══════════════════════════════════════════
    # LEVEL 7 — Revolution & Industry
    # ═══════════════════════════════════════════
    365: "A hand holding a quill signing a parchment document, bold calligraphic text visible",
    408: "A crowd storming a fortress gate, smoke and chaos, a banner held high above the masses",
    23:  "The very last dim star flickering out, leaving only darkness, the final light in the universe extinguished",
    456: "A steam locomotive racing along iron tracks through countryside, smoke trailing behind",
    457: "Rows of textile looms in a vast factory floor, threads stretching between machines",
    458: "A figure with a stethoscope listening to a patient's chest, medical instruments on a table nearby",
    459: "Chains being broken apart, shattered links falling away, a hand reaching upward in liberation",
    460: "Telegraph wires stretching between wooden poles across a prairie, connecting distant points",
    461: "A figure looking through a microscope at tiny organisms, a petri dish and notebook beside them",
    462: "A lightbulb glowing for the first time in a dark workshop, illuminating tools and wires around it",
    463: "An early camera on a tripod, the photographer hidden under a dark cloth, capturing a still scene",
    464: "A suffragette figure holding a banner aloft, standing resolute before a crowd",
    465: "Two brothers launching a fragile biplane from a sandy hill, the craft lifting into wind",
    466: "A mushroom cloud rising above a horizon, terrible and immense, darkening the sky",
    467: "Immigrants crowded on the deck of a steamship, gazing toward a distant statue holding a torch",
    468: "Barbed wire strung across a muddy trench, helmets and debris scattered in no-man's land",
    469: "A double helix spiraling upward, elegant and precise, the structure of life revealed",
    470: "A grand canal cutting through a narrow isthmus, a ship passing through massive lock gates",

    # ═══════════════════════════════════════════
    # LEVEL 8 — The Modern World
    # ═══════════════════════════════════════════
    24:  "A massive black hole consuming the last remnants of light and matter, a dark accretion disk spiraling inward",
    25:  "Absolute stillness — a vast dark canvas with the faintest possible glow fading to nothing, heat death",
    471: "A mushroom cloud over a flattened city, the shadow of total destruction, somber and still",
    472: "A concrete wall topped with barbed wire dividing a city in two, graffiti on one side",
    473: "A figure in a spacesuit floating outside a spacecraft, Earth's blue curve visible below",
    474: "A desktop computer with a glowing green-text monitor, chunky keyboard, in a cluttered room",
    475: "Protesters facing a line of tanks on a wide boulevard, a lone figure standing before the lead tank",
    476: "A concrete wall crumbling as figures climb over it and embrace on the other side, celebrating",
    477: "A web of glowing interconnected nodes and lines spreading across a dark background, the internet",
    478: "A sleek smartphone held in a hand, its screen glowing with icons, the world in a palm",
    479: "Wind turbines standing tall on green hills, blades turning slowly against a cloudy sky",
    480: "A rover on a barren red rocky landscape, its tracks visible in rusty dust, exploring alone",
    481: "A marching crowd holding signs and banners, diverse faces united in peaceful protest",
    482: "A figure in a lab coat holding up a glowing test tube, CRISPR gene editing visualized as tiny scissors cutting a DNA strand",
    483: "Solar panels arranged in vast rows across a desert, reflecting brilliant sunlight",
    484: "A reusable rocket landing upright on a platform at sea, flames cushioning its descent",
    485: "A figure wearing a VR headset, surrounded by swirling digital particles and light",
    486: "A neural network visualization — layers of glowing connected nodes, artificial intelligence thinking",
    487: "A glacier calving into the ocean, a massive chunk of ice falling into dark water, climate change",
    488: "The International Space Station orbiting above Earth, solar panels spread like golden wings",
    489: "A circle of world leaders seated around a curved table, flags of many nations behind them",
    490: "A protest sign held high reading in abstract brushstrokes, a crowd behind it, social movement energy",
    491: "A delivery drone hovering above a suburban doorstep, package dangling below, the future of logistics",
    492: "Electric cars charging at a sleek station, glowing cables connected, clean and quiet",
    493: "A James Webb Space Telescope unfolding its golden hexagonal mirrors in the darkness of space",
    494: "A humanoid robot extending its hand toward a human hand, fingers almost touching, collaboration",

    # ═══════════════════════════════════════════
    # LEVEL 9 — The Far Future
    # ═══════════════════════════════════════════
    502: "Tectonic plates sliding together, continents merging into one vast supercontinent, seen from above",
    501: "A dry cracked lakebed stretching to the horizon under a blazing swollen sun, the last water gone",
    503: "Earth's magnetic field lines flickering and fading, aurora lights dimming over a vulnerable planet",
    504: "A dying sun sputtering its last fusion reactions, dimming to a faint glow, fuel exhausted",
    505: "A planet being swallowed by the expanding surface of a bloated red star, consumed in fire",
    506: "Distant galaxy clusters fading and vanishing beyond an expanding horizon of emptiness",
    507: "The very last dim red dwarf star flickering out, leaving only darkness",
    508: "Atoms slowly dissolving into their constituent particles, matter itself unraveling over eons",
    509: "The last supermassive black hole evaporating in a final burst of Hawking radiation, then nothing",
    510: "A once-bright star now a cold dense white dwarf, faintly glowing in infinite darkness",
    511: "A planet frozen still, its rotation stopped, one side in perpetual scorching light, the other in ice",

    # ═══════════════════════════════════════════
    # MISSING — The Cosmic Dawn (Level 0)
    # ═══════════════════════════════════════════
    111: "An entire planet encased in ice, a frozen white sphere floating in dark space, glacial and silent",

    # ═══════════════════════════════════════════
    # MISSING — Empires & Faiths (Level 4)
    # ═══════════════════════════════════════════
    329: "An elderly sage seated on a low platform teaching a circle of students, scrolls and bamboo around them",
    328: "A serene figure seated cross-legged beneath a bodhi tree, eyes closed, surrounded by falling leaves",
    337: "A grand Greek temple with fluted columns and a sculptured pediment, lit by golden afternoon light",
    330: "A young warrior on horseback leading an army across a vast plain, spears raised, dust billowing",
    333: "A king placing down his sword and crown before a carved stone pillar inscribed with edicts of peace",
    334: "A group of robed senators surrounding a fallen figure on the floor of a marble hall, daggers drawn",
    332: "A vast columned library interior with scrolls stacked floor to ceiling, scholars reading and debating",
    335: "A regal woman in Egyptian headdress seated on a throne, the Nile visible through columns behind her",
    336: "Hands pressing wet pulp onto a flat screen, sheets of fresh paper drying on bamboo racks nearby",
    331: "A stern emperor in armor surveying rows of terracotta soldiers stretching into the distance",

    # ═══════════════════════════════════════════
    # MISSING — The Medieval World (Level 5)
    # ═══════════════════════════════════════════
    346: "A bustling Tang Dynasty street scene with pagodas, silk merchants, and scholars under lantern light",
    340: "A king being crowned by a pope in a grand cathedral, golden crown descending onto a bowed head",
    339: "A Viking longship approaching a rocky forested coastline through morning mist, figures at the prow",
    341: "Armored crusaders on horseback riding toward a walled city in the desert, banners and crosses flying",
    344: "An enormous temple with five ornate towers reflected perfectly in a still moat at sunrise",
    342: "A fierce mounted warrior with a drawn bow, a vast horde of horsemen stretching behind across the steppe",
    343: "A European traveler in robes arriving at the gates of a grand Chinese palace, camels laden with goods",
    349: "A magnificent caravan crossing the Sahara desert, a richly robed king on a golden horse at the center",
    338: "Rats and dark shadows creeping through a narrow medieval alley, doors marked with painted crosses",
    345: "A grand stone enclosure with towering walls and a conical tower, set against African savanna",
    348: "Gothic stone arches of a university courtyard, scholars in robes walking beneath them with books",
    350: "A robed poet writing by candlelight, a vision of spiraling circles of heaven above his head",
    347: "Hooded inquisitors seated at a long table in a dark stone chamber, a single figure standing before them",

    # ═══════════════════════════════════════════
    # MISSING — Exploration & Enlightenment (Level 6)
    # ═══════════════════════════════════════════
    351: "A great domed city falling, cannon smoke and flames rising behind crumbling Byzantine walls",
    352: "An open notebook filled with mirrored handwriting and detailed anatomical sketches of a human wing",
    353: "A figure nailing a document to a heavy wooden church door, the page covered in dense text",
    358: "A battered sailing ship rounding the tip of a continent, vast ocean stretching in every direction",
    354: "A diagram of planets orbiting the sun in concentric circles, hand-drawn with compass and ruler",
    355: "A quill pen resting on an open manuscript page, dramatic text visible, a skull prop beside it",
    356: "A figure peering through a brass telescope at a bright planet with four tiny moons beside it",
    361: "A white marble domed mausoleum reflected in a long rectangular pool, framed by cypress trees",
    357: "A falling apple and a diagram of orbital paths drawn on parchment, mathematical notations around it",
    362: "Hands playing a harpsichord keyboard, sheet music with intricate baroque notation on the stand",
    363: "A satirist writing with a sharp quill, an ironic half-smile, books and pamphlets scattered on the desk",
    359: "Shackled hands reaching out from the dark hold of a wooden ship, light streaming through a hatch above",
    360: "A small wooden ship anchored off a rocky forested shore, figures wading through shallow water to land",
    364: "A ship's captain charting an island coastline with compass and ink, a vast Pacific ocean behind him",

    # ═══════════════════════════════════════════
    # MISSING — Revolution & Industry (Level 7)
    # ═══════════════════════════════════════════
    366: "An orchestra performing in a grand concert hall, the conductor's arms raised at a climactic moment",
    375: "A steam locomotive on iron rails, passengers and onlookers watching from a platform, smoke billowing",
    367: "A faint ghostly image forming on a metal plate inside a wooden box camera, the first photograph",
    376: "A scientist examining a flask of cloudy liquid under a lamp, microscope and petri dishes nearby",
    370: "A ship passing through a narrow man-made canal cut between sandy desert banks, engineering triumph",
    371: "A figure speaking into a cone-shaped device connected by a wire to a distant receiver",
    372: "A single glowing lightbulb filament in a glass bulb, warm light radiating in a dark workshop",
    374: "Formerly enslaved people raising a flag of independence, broken chains at their feet, dawn breaking",
    368: "Two figures writing at a desk, a pamphlet being printed on a hand press, revolutionary text emerging",
    369: "A battlefield at dusk with abandoned cannons and a torn flag, smoke clearing over still ground",
    373: "A Japanese harbor with both traditional boats and a modern steamship, East meeting West",

    # ═══════════════════════════════════════════
    # MISSING — The Modern World (Level 8)
    # ═══════════════════════════════════════════
    377: "A fragile biplane lifting off a sandy beach, two figures watching from the ground, wind in the wings",
    378: "A massive ocean liner tilting at an angle, its stern rising from dark water, lifeboats scattered around",
    379: "Soldiers in trenches stretching across a muddy landscape, barbed wire and smoke filling the horizon",
    380: "A red flag being raised above a grand palace, crowds surging through the gates, revolution erupting",
    381: "A petri dish with a ring of clear space around a mold colony, bacteria killed by penicillin",
    382: "A mushroom cloud rising over a flattened city skyline, the sky darkened, terrible and immense",
    383: "A grand circular assembly hall with tiered seating, flags of many nations arranged in a semicircle",
    392: "A vast crowd celebrating beneath a new flag being raised for the first time, independence and joy",
    393: "A massive crowd gathered in a grand square, a leader speaking from a balcony above red banners",
    384: "A double helix spiraling elegantly upward, its rungs like ladder steps, the blueprint of life",
    394: "A naval ship facing another across a tense stretch of ocean, the world holding its breath",
    385: "A lone figure speaking to an enormous crowd from the steps of a memorial, arm raised in oration",
    395: "A shattered reactor building with smoke rising, an abandoned city visible in the background",
    386: "A concrete wall being broken apart by jubilant figures with hammers, embracing through the gap",
    387: "A dignified figure walking through an open prison gate into sunlight, fist raised in triumph",
    388: "A cylindrical telescope floating in orbit above Earth, its aperture pointed at distant galaxies",
    390: "Twin towers of smoke rising from a city skyline, a plane's shadow crossing the scene, somber",
    389: "A spiral of genetic code unwinding into readable letters A T C G, the human genome decoded",
    391: "A hand holding a sleek rectangular device with a glowing touchscreen, the world at your fingertips",
    396: "World leaders clasping hands beneath a banner with a globe on it, a green leaf motif, cooperation",
    397: "A figure in a face mask standing in an empty city street, the world paused and quiet, a pandemic",
    410: "Soldiers laying down weapons on a battlefield, a white flag raised, the end of World War II",
    411: "Glowing lines of data connecting computer terminals across a web-like network, the internet emerging",
    414: "A figure writing equations on a chalkboard, curved spacetime diagrams and E=mc², relativity",
    415: "Women marching with suffrage banners held high, determination on their faces, winning the vote",
}


def main():
    with open("src/data_with_prompts.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    missing = []

    for level in data["levels"]:
        for event in level["events"]:
            eid = event["id"]
            if eid in VISUAL_PROMPTS:
                event["visual_prompt"] = VISUAL_PROMPTS[eid]
                updated += 1
            else:
                missing.append(f"  ID {eid}: {event['title']}")

    # Write back
    with open("src/data_with_prompts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {updated} events with visual_prompt fields.")
    if missing:
        print(f"\nWARNING: {len(missing)} events have no visual_prompt mapping:")
        for m in missing:
            print(m)
    else:
        print("All events covered!")


if __name__ == "__main__":
    main()

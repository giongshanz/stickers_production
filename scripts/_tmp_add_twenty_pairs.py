import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "plan" / "sticker-plan.json"
PROFILES = ROOT / "prompts" / "reference-profiles.json"

R = "references/Stickers/"
PAIRS = [
    dict(
        a=("squirrel-forest", "Sóc rừng", "squirrel-forest-character", "the same playful little forest squirrel with warm russet fur, a cream muzzle and belly, tufted ears, dark eyes, peach cheeks, four small paws and one complete large curled fluffy tail", [
            ("squirrel-acorn", "sitting and holding one large acorn"),
            ("squirrel-tree-branch", "balancing on one short leafy tree branch"),
            ("squirrel-leaf-umbrella", "holding a broad green leaf overhead like an umbrella"),
            ("squirrel-jumping", "making a cheerful leap with the complete tail visible"),
            ("squirrel-forest-map", "studying one tiny illustrated forest map with no writing"),
            ("squirrel-walnut", "sitting and opening one walnut"),
            ("squirrel-sleeping-nest", "sleeping curled in a small connected leaf nest"),
        ]),
        b=("chestnut-season", "Mùa hạt dẻ", "chestnut-objects", [
            ("chestnut-branch", "A short chestnut branch bearing three brown nuts inside green spiky burrs"),
            ("chestnut-open-burr", "One open spiky chestnut burr revealing two polished brown chestnuts"),
            ("chestnut-harvest-basket", "A small wicker basket filled with freshly harvested chestnuts"),
            ("chestnut-roasting-pan", "A small handled roasting pan holding four warm roasted chestnuts"),
            ("chestnut-paper-cone", "A folded kraft paper cone containing a handful of roasted chestnuts, no writing"),
            ("chestnut-cream-cake", "A small chestnut cream cake with a single glossy chestnut garnish"),
            ("chestnut-leaf-cluster", "A short chestnut twig with three golden autumn leaves and two nuts"),
        ]),
        shared=("squirrel-chestnut-basket", "walking while hugging one small wicker basket full of ripe chestnuts"),
        refs_a=[R+"3. Racoon/187-Racoon_1.png", R+"1_Animals/rabbit.png"],
        refs_b=[R+"2. Autumn/96-Autumn_2.png", R+"8-Gardening/8-Gardening_1.png"],
    ),
    dict(
        a=("happy-hedgehog", "Nhím vui vẻ", "hedgehog-character", "the same small cheerful hedgehog with a warm tan face and belly, soft rounded brown spines, tiny ears, dark eyes, peach cheeks and four short paws", [
            ("hedgehog-apple", "sitting and holding one red apple"),
            ("hedgehog-leaf-hat", "wearing one large golden autumn leaf like a hat"),
            ("hedgehog-mushroom", "standing beside one small connected woodland mushroom"),
            ("hedgehog-rain-boots", "wearing a pair of tiny green rain boots"),
            ("hedgehog-butterfly", "watching one small blue butterfly perched on a spine"),
            ("hedgehog-happy-jump", "making a little joyful hop with all four paws readable"),
            ("hedgehog-sleeping", "sleeping curled in a round pose with its face still visible"),
        ]),
        b=("pumpkin-season", "Mùa bí ngô", "pumpkin-objects", [
            ("pumpkin-seedling", "A young pumpkin seedling with two broad green leaves in a little soil clump"),
            ("pumpkin-vine", "A short curling pumpkin vine with one small green pumpkin and yellow blossom"),
            ("pumpkin-harvest", "A compact group of three ripe orange pumpkins of different sizes"),
            ("pumpkin-wicker-basket", "A low wicker basket holding two small orange pumpkins"),
            ("pumpkin-slice", "One cut pumpkin wedge showing orange flesh and pale seeds"),
            ("pumpkin-pie", "One round pumpkin pie with a neat slice removed"),
            ("pumpkin-lantern", "One friendly carved pumpkin lantern with a warm candle glow and no face on any other object"),
        ]),
        shared=("hedgehog-pumpkin-hug", "sitting and hugging one small uncarved orange pumpkin"),
        refs_a=[R+"Frog/4-frog_4.png", R+"1_Animals/rabbit.png"],
        refs_b=[R+"2. Autumn/96-Autumn_2.png", R+"8-Gardening/8-Gardening_1.png"],
    ),
    dict(
        a=("raccoon-activities", "Gấu mèo", "raccoon-character", "the same small friendly raccoon with warm gray-brown fur, cream face markings, a dark natural eye mask, dark paws, peach cheeks and one long complete ringed tail", [
            ("raccoon-apple", "sitting and holding one red apple"),
            ("raccoon-reading", "reading one open teal picture book with no writing"),
            ("raccoon-umbrella", "holding one compact yellow umbrella"),
            ("raccoon-hiking", "walking with one small rust-orange backpack"),
            ("raccoon-binoculars", "looking through one pair of small brass binoculars"),
            ("raccoon-marshmallow", "sitting and holding one toasted marshmallow on a short stick"),
            ("raccoon-sleeping", "sleeping curled around its striped tail"),
        ]),
        b=("lakeside-camping", "Cắm trại ven hồ", "lakeside-camp-objects", [
            ("lakeside-tent", "One small teal canvas camping tent with its opening clearly visible"),
            ("lakeside-campfire", "A compact safe campfire of three logs and a small orange flame"),
            ("lakeside-canteen", "A muted green metal camping canteen with a shoulder strap"),
            ("lakeside-fishing-rod", "One simple wooden fishing rod with an attached line, float and hook"),
            ("lakeside-rowboat", "One small wooden rowboat with two short oars inside"),
            ("lakeside-lantern", "A brass camping lantern with a warm pale yellow glow"),
            ("lakeside-sleeping-bag", "One rolled rust-orange sleeping bag fastened with two straps"),
        ]),
        shared=("raccoon-lakeside-fishing", "sitting beside one small connected teal camping tent while holding a simple fishing rod"),
        refs_a=[R+"3. Racoon/187-Racoon_1.png", R+"3. Racoon/187-Racoon_6.png"],
        refs_b=[R+"17_Camping/camping_3.png", R+"8-Gardening/8-Gardening_1.png"],
    ),
    dict(
        a=("school-mouse", "Chuột học trò", "school-mouse-character", "the same little school mouse with warm light-brown fur, a cream muzzle and belly, large round pink inner ears, small dark eyes, peach cheeks, four tiny paws and one complete thin pink tail", [
            ("mouse-schoolbag", "wearing one small teal schoolbag"),
            ("mouse-reading", "reading one open cream picture book with no writing"),
            ("mouse-writing", "writing with one short pencil on a small blank notebook"),
            ("mouse-ruler", "holding one simple wooden ruler without numbers"),
            ("mouse-lunchbox", "sitting and opening one small yellow lunchbox"),
            ("mouse-globe", "standing beside one tiny classroom globe without labels"),
            ("mouse-sleeping-books", "sleeping against a stack of two closed school books"),
        ]),
        b=("art-corner", "Góc mỹ thuật", "art-corner-objects", [
            ("art-colored-pencils", "A tidy cup holding six colored pencils with no writing"),
            ("art-watercolor-palette", "A small oval watercolor palette with six muted paint wells"),
            ("art-paintbrushes", "Three varied paintbrushes tied together with one pale ribbon"),
            ("art-sketchbook", "An open sketchbook showing one simple flower drawing and no text"),
            ("art-small-easel", "A little wooden table easel holding a blank cream canvas"),
            ("art-clay-pot", "A small unfinished terracotta pinch pot with a lump of clay"),
            ("art-paper-collage", "A compact layered paper collage of a flower, leaf and sun cut from colored paper"),
        ]),
        shared=("mouse-color-pencil-box", "sitting and proudly holding one small open box of colored pencils"),
        refs_a=[R+"1_Animals/rabbit.png", R+"Frog/4-frog_4.png"],
        refs_b=[R+"2. Artist/84-Artist_2.png", R+"12_SchoolSupplies/school supplies_2.png"],
    ),
    dict(
        a=("winter-lamb", "Cừu mùa đông", "winter-lamb-character", "the same small gentle lamb with fluffy warm-cream fleece, a pale peach face and inner ears, little dark eyes, blush cheeks, four short legs and tiny hooves", [
            ("lamb-winter-hat", "wearing one red knitted winter hat"),
            ("lamb-snowflake", "looking up at one large connected pale-blue snowflake"),
            ("lamb-sled", "sitting on one small wooden sled"),
            ("lamb-snowball", "holding one neat round snowball between its front hooves"),
            ("lamb-cocoa", "sitting and holding one small steaming coral mug of cocoa"),
            ("lamb-mittens", "wearing one pair of muted teal knitted mittens"),
            ("lamb-sleeping-blanket", "sleeping under one soft sage-green knitted blanket"),
        ]),
        b=("knitwear", "Đồ len", "knitwear-objects", [
            ("knit-pom-hat", "One rust-red knitted pom-pom hat with a simple ribbed cuff"),
            ("knit-cream-sweater", "One cream cable-knit sweater laid flat, no logo"),
            ("knit-striped-socks", "One matching pair of striped knitted socks"),
            ("knit-earmuffs", "One pair of soft knitted ear warmers joined by a curved headband"),
            ("knit-shawl", "One folded sage-green knitted shawl with simple fringe"),
            ("knit-baby-booties", "One matching pair of tiny pale-blue knitted baby booties"),
            ("knit-yarn-basket", "One wicker basket holding three balls of yarn and two wooden knitting needles"),
        ]),
        shared=("lamb-red-scarf", "standing and wearing one long red knitted scarf wrapped loosely around its neck"),
        refs_a=[R+"2. Farm Animals/62-Farm Animals_3.png", R+"Frog/4-frog_4.png"],
        refs_b=[R+"3. Scarves/166-Scarves_2.png", R+"33_Winter/33- winter_2.png"],
    ),
    dict(
        a=("little-turtle", "Rùa nhỏ", "little-turtle-character", "the same small friendly freshwater turtle with an olive-green head and four short legs, a rounded warm-brown segmented shell, dark eyes, peach cheeks and one tiny complete tail", [
            ("turtle-strawberry", "sitting and holding one red strawberry"),
            ("turtle-rain-leaf", "sheltering under one broad green leaf with three connected raindrops"),
            ("turtle-map", "studying one tiny illustrated pond map with no writing"),
            ("turtle-water-lily", "holding one pale-pink water lily flower"),
            ("turtle-pond-dive", "making a gentle diving pose with a few connected blue droplets"),
            ("turtle-butterfly", "watching one small blue butterfly perched on its shell"),
            ("turtle-sleeping", "sleeping with its head tucked softly against its shell"),
        ]),
        b=("lotus-pond", "Ao sen", "lotus-pond-objects", [
            ("lotus-pink-bloom", "One open pink lotus flower on a short green stem with two broad leaves"),
            ("lotus-white-bud", "One closed ivory lotus bud on a curved stem"),
            ("lotus-seed-pod", "One green lotus seed pod with clearly visible round seeds"),
            ("lotus-floating-leaf", "One broad round floating lotus leaf with a small bead of water"),
            ("lotus-dragonfly", "One blue dragonfly perched on a short lotus stem"),
            ("lotus-frog", "One small green frog resting on a lotus leaf"),
            ("lotus-pond-fish", "One small golden pond fish swimming beside a connected lotus leaf"),
        ]),
        shared=("turtle-lotus-leaf", "sitting peacefully on one broad floating lotus leaf with a small pink lotus bud beside it"),
        refs_a=[R+"Frog/4-frog_4.png", R+"1_Animals/rabbit.png"],
        refs_b=[R+"3_Flowers/Flower_3.png", R+"Frog/4-frog_4.png"],
    ),
    dict(
        a=("small-robot", "Robot nhỏ", "small-robot-character", "the same small helpful friendly robot with a rounded cream metal body, muted teal panels, two short jointed arms, two short legs, dark oval eyes on a simple face plate and a tiny orange antenna", [
            ("robot-watering-plant", "watering one small connected potted green plant with a little can"),
            ("robot-reading-manual", "holding one open picture manual with no writing"),
            ("robot-toolbox", "carrying one small red toolbox with simple tools visible"),
            ("robot-lightbulb", "holding one warm yellow lightbulb while thinking"),
            ("robot-cleaning", "using one soft cloth to clean its own arm panel"),
            ("robot-greeting", "standing and waving one jointed hand"),
            ("robot-sleep-mode", "sitting with eyes softly closed and antenna folded"),
        ]),
        b=("bicycles", "Xe đạp", "bicycle-objects", [
            ("bicycle-city", "One compact mint-green city bicycle with a low step-through frame"),
            ("bicycle-mountain", "One muted orange mountain bicycle with broad knobby tires"),
            ("bicycle-cargo", "One small blue cargo bicycle with a wooden front basket"),
            ("bicycle-kids", "One small yellow children's bicycle with training wheels"),
            ("bicycle-folding", "One neatly folded teal folding bicycle with small wheels"),
            ("bicycle-tandem", "One red tandem bicycle with two saddles and two sets of pedals"),
            ("bicycle-basket-flowers", "One cream bicycle with a front wicker basket of flowers"),
        ]),
        shared=("robot-bicycle-ride", "riding one small teal bicycle with both wheels and its whole body visible"),
        refs_a=[R+"2. Home appliance/68-Home Appliance_2.png", R+"Frog/4-frog_4.png"],
        refs_b=[R+"11_Vehicles/vehicle_2.png", R+"8-Gardening/8-Gardening_1.png"],
    ),
    dict(
        a=("seal-activities", "Hải cẩu", "seal-character", "the same small playful harbor seal with a rounded pale silver-gray body, darker gentle spots, short whiskers, warm dark eyes, peach cheeks, two front flippers and two rear flippers", [
            ("seal-clapping", "sitting upright and clapping its two front flippers"),
            ("seal-fish", "hugging one small silver fish"),
            ("seal-swim-ring", "floating through one simple coral-and-cream swim ring"),
            ("seal-beach-ball", "balancing one small striped beach ball on its nose"),
            ("seal-snowball", "nudging one round snowball with a front flipper"),
            ("seal-sled", "sitting on one small connected wooden sled"),
            ("seal-sleeping", "sleeping curled with its flippers tucked and whiskers visible"),
        ]),
        b=("ice-day", "Ngày trên băng", "ice-day-objects", [
            ("ice-frozen-pond", "A compact irregular oval of pale-blue frozen pond ice with a few broad soft painted streaks"),
            ("ice-fishing-hole", "A small circular ice-fishing hole with one short wooden fishing rod and float"),
            ("ice-lantern", "One clear ice lantern holding a warm small candle"),
            ("ice-skate-pair", "One matching pair of pale-blue figure skates tied together by their laces"),
            ("ice-sled", "One compact wooden sled with curved runners and a short pull rope"),
            ("ice-snow-crystal", "One large delicate six-point snow crystal with broad readable branches"),
            ("ice-thermos", "One teal winter thermos with its cap used as a small cup"),
        ]),
        shared=("seal-ice-skates", "wearing one matching pair of small pale-blue ice skates while making a gentle gliding pose"),
        refs_a=[R+"19_MarineLife/marine_life_1.png", R+"Frog/4-frog_4.png"],
        refs_b=[R+"Winter Sports/33- winter_2.png", R+"33_Winter/33- winter_2.png"],
    ),
    dict(
        a=("polar-bear-activities", "Gấu Bắc Cực", "polar-bear-character", "the same small gentle polar bear cub with warm ivory-white fur, rounded ears, a cream muzzle, a small charcoal nose, dark eyes, peach cheeks, four short paws and a tiny round tail", [
            ("polar-bear-scarf", "wearing one soft pale-blue winter scarf"),
            ("polar-bear-snowflake", "looking up at one connected pale-blue snowflake"),
            ("polar-bear-fishing", "holding one short ice-fishing rod beside a small connected blue hole"),
            ("polar-bear-cocoa", "sitting and holding one coral mug of cocoa"),
            ("polar-bear-sled", "riding one little wooden sled"),
            ("polar-bear-snowman", "sitting beside one tiny connected snowman made from two snowballs"),
            ("polar-bear-sleeping", "sleeping curled under a small blue blanket"),
        ]),
        b=("fruit-ice-cream", "Kem trái cây", "fruit-ice-cream-objects", [
            ("icecream-mango", "One waffle cone with a single scoop of golden mango ice cream and a tiny mango slice"),
            ("icecream-blueberry", "One waffle cone with a single scoop of muted purple blueberry ice cream and two blueberries"),
            ("icecream-kiwi", "One waffle cone with a single scoop of pale-green kiwi ice cream and one kiwi slice"),
            ("icecream-peach", "One waffle cone with a single scoop of soft peach ice cream and one peach wedge"),
            ("icecream-banana", "One waffle cone with a single scoop of banana ice cream and one banana slice"),
            ("icecream-watermelon", "One waffle cone with a single scoop of pale coral watermelon ice cream and one tiny watermelon wedge"),
            ("icecream-pineapple", "One waffle cone with a single scoop of pale-yellow pineapple ice cream and one pineapple piece"),
        ]),
        shared=("polar-bear-strawberry-cone", "sitting and holding one waffle cone with a single scoop of pink strawberry ice cream and a tiny strawberry garnish"),
        refs_a=[R+"1_Animals/panda.png", R+"Frog/4-frog_4.png"],
        refs_b=[R+"Ice cream/22- ice cream_2.png", R+"1-Bakery & Coffee Cafe/Bakery-&-Coffee-Cafe_1.png"],
    ),
    dict(
        a=("fox-explorer", "Cáo khám phá", "fox-explorer-character", "the same curious little russet fox with a cream muzzle, chest and tail tip, dark lower paws, triangular ears, warm dark eyes, peach cheeks and one complete bushy tail", [
            ("explorer-fox-map", "standing and studying one folded illustrated map with no writing"),
            ("explorer-fox-binoculars", "looking through one small pair of brass binoculars"),
            ("explorer-fox-backpack", "walking with one small teal travel backpack"),
            ("explorer-fox-compass", "sitting and holding one brass pocket compass"),
            ("explorer-fox-telescope", "looking through one little hand telescope"),
            ("explorer-fox-photo", "holding one compact cream camera with no logo"),
            ("explorer-fox-sleeping", "sleeping curled beside one small closed travel satchel"),
        ]),
        b=("hot-air-balloons", "Khinh khí cầu", "hot-air-balloon-objects", [
            ("balloon-rainbow", "One rainbow-striped hot-air balloon with a simple wicker basket"),
            ("balloon-heart", "One coral heart-shaped hot-air balloon with a compact wicker basket"),
            ("balloon-bear", "One hot-air balloon shaped like a friendly cream bear head with a wicker basket"),
            ("balloon-rabbit", "One pale-pink rabbit-shaped hot-air balloon with two long ears and a wicker basket"),
            ("balloon-cloud", "One pale-blue cloud-shaped hot-air balloon with a wicker basket"),
            ("balloon-pumpkin", "One warm-orange pumpkin-shaped hot-air balloon with a wicker basket"),
            ("balloon-star", "One muted-gold star-shaped hot-air balloon with a wicker basket"),
        ]),
        shared=("fox-hot-air-balloon", "sitting safely in the wicker basket of one small russet-and-cream fox-shaped hot-air balloon, full balloon visible"),
        refs_a=[R+"3. Racoon/187-Racoon_1.png", R+"Frog/4-frog_4.png"],
        refs_b=[R+"3. Balloons/152-Balloons_2.png", R+"8-Gardening/8-Gardening_1.png"],
    ),
]

plan = json.loads(PLAN.read_text(encoding="utf-8"))
profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
existing_ids = {a["id"] for a in plan["assets"]}
existing_slugs = {t["slug"] for t in plan["topics"]}
new_ids = set()
new_slugs = set()
for pair in PAIRS:
    a_slug, a_name, a_profile, design, a_items = pair["a"]
    b_slug, b_name, b_profile, b_items = pair["b"]
    shared_id, shared_action = pair["shared"]
    assert len(a_items) == len(b_items) == 7
    assert a_slug not in existing_slugs and b_slug not in existing_slugs
    assert a_slug not in new_slugs and b_slug not in new_slugs
    new_slugs.update((a_slug, b_slug))
    a_ids, b_ids = [], [shared_id]
    for asset_id, action in a_items:
        assert asset_id not in existing_ids and asset_id not in new_ids
        new_ids.add(asset_id)
        plan["assets"].append({"id": asset_id, "subject": f"Exactly one whole {design} {action}"})
        a_ids.append(asset_id)
    assert shared_id not in existing_ids and shared_id not in new_ids
    new_ids.add(shared_id)
    plan["assets"].append({"id": shared_id, "subject": f"Exactly one whole {design} {shared_action}"})
    a_ids.append(shared_id)
    for asset_id, subject in b_items:
        assert asset_id not in existing_ids and asset_id not in new_ids
        new_ids.add(asset_id)
        plan["assets"].append({"id": asset_id, "subject": subject})
        b_ids.append(asset_id)
    plan["topics"].append({"slug": a_slug, "name_vi": a_name, "asset_ids": a_ids})
    plan["topics"].append({"slug": b_slug, "name_vi": b_name, "asset_ids": b_ids})
    plan["shared_assets"].append({"id": shared_id, "topic_slugs": [a_slug, b_slug]})
    char_suffix = (
        f"Draw exactly one whole character with consistent anatomy and design across this topic: {design}. "
        "The pose or prop is exactly as named in the subject; preserve complete limbs, tail or flippers where applicable. "
        "The references guide only the restrained warm hand-painted style and proportions, not an exact pose. "
        "No extra character, scene, ground, floor shadow, readable text, logo or watermark. "
        "Keep a compact readable silhouette and the narrow white cut margin fully inside transparent padding."
    )
    object_suffix = (
        "Draw only the named object or explicitly connected small set, keeping functional construction and a "
        "clean readable silhouette. No face or limbs on objects, no person, broad scene, ground, floor shadow, "
        "readable text, brand or watermark. References guide only restrained warm hand-painted style, not the "
        "exact subject. Keep the complete narrow white cut margin inside transparent padding."
    )
    for name, refs, suffix in ((a_profile, pair["refs_a"], char_suffix), (b_profile, pair["refs_b"], object_suffix)):
        assert name not in profiles["profiles"]
        assert all((ROOT / r).is_file() for r in refs), refs
        profiles["profiles"][name] = {"references": refs, "suffix": suffix}
    profiles["topic_profiles"][a_slug] = a_profile
    profiles["topic_profiles"][b_slug] = b_profile
    profiles["asset_profiles"][shared_id] = a_profile

assert len(PAIRS) == 10 and len(new_slugs) == 20 and len(new_ids) == 150
plan["target"] = {
    "topics": len(plan["topics"]),
    "slots_per_topic": 8,
    "total_topic_slots": sum(len(t["asset_ids"]) for t in plan["topics"]),
    "unique_assets": len(plan["assets"]),
    "shared_assets": len(plan["shared_assets"]),
}
plan["qa"] = {
    "topic_count": len(plan["topics"]),
    "total_topic_slots": plan["target"]["total_topic_slots"],
    "unique_assets": len(plan["assets"]),
    "shared_assets": len(plan["shared_assets"]),
    "all_topics_have_eight": all(len(t["asset_ids"]) == 8 for t in plan["topics"]),
    "shared_membership_exactly_two": all(len(s["topic_slugs"]) == 2 for s in plan["shared_assets"]),
}
plan["production_note"] = plan["production_note"].rstrip() + " On 2026-09-24 the user added twenty eight-slot topics in ten pairs, with exactly one new shared sticker master per pair."
assert plan["target"] == {"topics": 102, "slots_per_topic": 8, "total_topic_slots": 816, "unique_assets": 796, "shared_assets": 20}
PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PROFILES.write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"target": plan["target"], "new_topics": sorted(new_slugs), "new_master_ids": len(new_ids)}, ensure_ascii=False, indent=2))

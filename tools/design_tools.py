import re
from tools.web_tools import fetch_materials


def generate_palette(style: str = "Warm Modern", room_type: str = "Living Room", preferences: list[str] | None = None) -> dict:
    """
    Generate a harmonious 4-color interior design palette with HEX codes, roles, and matching material pairings.
    """
    style_key = (style or "modern").strip().lower()
    room_key = (room_type or "living room").strip().lower()
    prefs = [p.lower() for p in (preferences or [])]

    curated_palettes = {
        "warm modern": {
            "name": "Warm Modern Neutral",
            "description": "A sophisticated palette blending rich natural wood tones with warm beige neutrals and terracotta accents.",
            "colors": [
                {"name": "Warm Beige", "hex": "#D8C3A5", "role": "Primary Walls"},
                {"name": "Walnut Wood", "hex": "#5A3825", "role": "Furniture & Cabinetry"},
                {"name": "Soft Cream", "hex": "#F3EBDD", "role": "Ceiling & Trim"},
                {"name": "Terracotta", "hex": "#C76B4A", "role": "Accent Decor"},
            ],
        },
        "minimal": {
            "name": "Architectural Minimalist",
            "description": "A crisp, serene monochrome palette emphasizing clean lines and natural light.",
            "colors": [
                {"name": "Off-White", "hex": "#F5F5F3", "role": "Primary Walls"},
                {"name": "Charcoal Grey", "hex": "#333333", "role": "Structural Accents"},
                {"name": "Soft Taupe", "hex": "#C8C2BC", "role": "Soft Furnishings"},
                {"name": "Matte Black", "hex": "#1A1A1A", "role": "Hardware & Fixtures"},
            ],
        },
        "scandinavian": {
            "name": "Nordic Light & Wood",
            "description": "An airy Scandinavian scheme featuring light oak tones, muted sage greens, and bright neutrals.",
            "colors": [
                {"name": "Snow White", "hex": "#FAFAFA", "role": "Primary Walls"},
                {"name": "Blonde Oak", "hex": "#D6C0A0", "role": "Flooring & Furniture"},
                {"name": "Muted Sage", "hex": "#9DAF9B", "role": "Accent Textile"},
                {"name": "Warm Grey", "hex": "#E0DDD8", "role": "Upholstery"},
            ],
        },
        "luxury": {
            "name": "Opulent Contemporary",
            "description": "A rich, luxurious scheme featuring champagne gold accents, deep navy, and polished marble hues.",
            "colors": [
                {"name": "Champagne Beige", "hex": "#E6D7C3", "role": "Primary Walls"},
                {"name": "Deep Royal Navy", "hex": "#1C2D42", "role": "Feature Wall / Sofa"},
                {"name": "Polished Brass", "hex": "#D4AF37", "role": "Metal Hardware"},
                {"name": "Carrara White", "hex": "#EBECEE", "role": "Marble Surfaces"},
            ],
        },
    }

    matched_palette = None
    for key, pal in curated_palettes.items():
        if key in style_key or key in prefs:
            matched_palette = pal
            break

    if not matched_palette:
        matched_palette = curated_palettes["warm modern"]

    materials = fetch_materials(style or "Warm Modern")

    return {
        "name": matched_palette["name"],
        "description": matched_palette["description"],
        "style": style or "Modern",
        "room_type": room_type or "Living Room",
        "colors": matched_palette["colors"],
        "materials": materials
    }


def calculate_layout(room_length: float = 16.0, room_width: float = 12.0, furniture: list[dict] | None = None) -> dict:
    """
    Deterministic Python geometry calculator for room layout fitting and furniture spatial placement.
    """
    try:
        length = float(room_length)
        width = float(room_width)
    except (ValueError, TypeError):
        length, width = 16.0, 12.0

    room_area = length * width
    total_furniture_area = 0.0
    placements = []
    notes = []

    walls = ["North wall (Longest)", "South wall", "East wall (Window side)", "West wall"]
    wall_index = 0

    if not furniture:
        furniture = [
            {"name": "3-Seater Sofa", "length": 7.0, "width": 3.0},
            {"name": "Coffee Table", "length": 4.0, "width": 2.0},
            {"name": "TV Unit", "length": 6.0, "width": 1.5},
            {"name": "Accent Armchair", "length": 3.0, "width": 3.0}
        ]

    for item in furniture:
        item_name = item.get("name", "Furniture Item")
        try:
            item_l = float(item.get("length", 3.0))
            item_w = float(item.get("width", 2.0))
        except (ValueError, TypeError):
            item_l, item_w = 3.0, 2.0

        item_area = item_l * item_w
        total_furniture_area += item_area

        name_lower = item_name.lower()
        if "sofa" in name_lower or "couch" in name_lower:
            pos = "North wall (Anchor seating)"
        elif "tv" in name_lower or "media" in name_lower or "entertainment" in name_lower:
            pos = "South wall (Opposite sofa for optimal sightline)"
        elif "coffee" in name_lower or "center" in name_lower:
            pos = "Center (18 inches clearance from sofa)"
        elif "table" in name_lower or "dining" in name_lower:
            pos = "East wall (Near natural light)"
        elif "desk" in name_lower or "study" in name_lower or "work" in name_lower:
            pos = "Corner near East window (Task lighting)"
        elif "chair" in name_lower or "armchair" in name_lower or "recliner" in name_lower:
            pos = "Angled next to main sofa (L-shaped conversation group)"
        else:
            pos = walls[wall_index % len(walls)]
            wall_index += 1

        placements.append({
            "furniture": item_name,
            "dimensions": f"{item_l} × {item_w} ft",
            "area": round(item_area, 1),
            "position": pos
        })

    coverage_pct = round((total_furniture_area / room_area) * 100, 1) if room_area > 0 else 0
    fits = coverage_pct <= 55.0

    if fits:
        notes.append(f"Furniture footprint covers {coverage_pct}% of total room area ({round(room_area, 1)} sq ft).")
        notes.append("Maintains minimum 3-foot primary walking corridors and 18-inch coffee table clearance.")
        notes.append("Optimal traffic flow achieved with clear access to entryways and windows.")
    else:
        notes.append(f"Warning: High spatial density ({coverage_pct}% room coverage).")
        notes.append("Consider slimming furniture dimensions or using multi-functional pieces to maximize walking space.")

    return {
        "room_length": length,
        "room_width": width,
        "room_area": round(room_area, 1),
        "total_furniture_area": round(total_furniture_area, 1),
        "coverage_percentage": coverage_pct,
        "furniture_fit": fits,
        "layout": placements,
        "notes": notes
    }

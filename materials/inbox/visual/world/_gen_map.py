"""
VIS-MAP-001 UW-UPGRADE-1.0 Map Layer Generator
Generates 9 independent layers + 3 data layers for Rulid Village playable map.
Map: 3024x1792 px (108x64 tiles at 28px/tile)
"""
import hashlib, json, os, csv, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

random.seed(42)

W, H = 3024, 1792
TW, TH = 28, 28
COLS, ROWS = 108, 64

# Style bible colors
INK = (43, 37, 33)
PARCHMENT = (230, 213, 184)
MOSS = (95, 125, 74)
RAIN_TEAL = (70, 119, 122)
WOOD = (138, 90, 59)
WHEAT = (216, 183, 103)
SKY = (154, 192, 207)
INDIGO = (60, 70, 104)
CLUE_CYAN = (114, 184, 196)
TENSION = (182, 95, 98)

# Village layout zones (tile coordinates)
ZONES = {
    "plaza": {"x": (42, 62), "y": (24, 36)},
    "church": {"x": (28, 40), "y": (12, 24)},
    "gigas_tree": {"x": (8, 24), "y": (28, 46)},
    "houses_n": {"x": (50, 70), "y": (14, 22)},
    "houses_s": {"x": (44, 64), "y": (38, 46)},
    "north_gate": {"x": (50, 60), "y": (3, 10)},
    "forest_path": {"x": (48, 62), "y": (0, 8)},
    "farmland": {"x": (20, 90), "y": (48, 60)},
    "river_start": {"x": (5, 10), "y": (0, 5)},
    "river_end": {"x": (95, 105), "y": (58, 64)},
}

def tile_to_px(tx, ty):
    return tx * TW, ty * TH

def zone_rect(zone):
    x1, y1 = tile_to_px(zone["x"][0], zone["y"][0])
    x2, y2 = tile_to_px(zone["x"][1], zone["y"][1])
    return x1, y1, x2, y2

# ---- TERRAIN LAYER ----
def gen_terrain(base_texture_path):
    """Terrain: only ground textures, no roads/buildings/water"""
    layer = Image.new("RGB", (W, H), MOSS)
    # Load and tile the base texture
    try:
        base = Image.open(base_texture_path)
        base = base.resize((TW*4, TH*4), Image.LANCZOS)
    except:
        base = Image.new("RGB", (TW*4, TH*4), MOSS)

    # Tile the texture across the map with variation
    for ty in range(ROWS):
        for tx in range(COLS):
            x, y = tile_to_px(tx, ty)
            # Slight color variation per tile
            variant = random.randint(-15, 15)
            patch = base.copy()
            # Add per-tile color shift
            r, g, b = MOSS
            shifted = Image.new("RGB", (TW, TH), (
                max(0, min(255, r + variant)),
                max(0, min(255, g + variant)),
                max(0, min(255, b + variant - 5))
            ))
            patch = Image.blend(patch.crop((0, 0, TW, TH)), shifted, 0.3)
            # Dirt patches near plaza and paths
            if random.random() < 0.08:
                patch = Image.blend(patch, Image.new("RGB", (TW, TH), WOOD), 0.4)
            # Stone patches near church
            cz = ZONES["church"]
            if cz["x"][0] <= tx <= cz["x"][1] and cz["y"][0] <= ty <= cz["y"][1]:
                if random.random() < 0.15:
                    patch = Image.blend(patch, Image.new("RGB", (TW, TH), (120, 115, 110)), 0.3)
            layer.paste(patch, (x, y))

    # Add noise texture
    noise = Image.new("RGB", (W, H))
    for ty in range(ROWS):
        for tx in range(COLS):
            x, y = tile_to_px(tx, ty)
            n = random.randint(-10, 10)
            for dy in range(TH):
                for dx in range(TW):
                    pass  # Too slow per-pixel; use filter instead

    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.5))
    return layer

# ---- WATER LAYER ----
def gen_water():
    """Water: river only, transparent background"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # River: diagonal from top-left to bottom-right
    points = []
    for i in range(20):
        t = i / 19
        x = int(5 * TW + t * 95 * TW + random.randint(-30, 30))
        y = int(2 * TH + t * 58 * TH + random.randint(-20, 20))
        points.append((x, y))

    # Draw river as thick polyline
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        width = random.randint(50, 80)
        draw.line([(x1, y1), (x2, y2)], fill=RAIN_TEAL + (200,), width=width)

    # Add water highlights
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        draw.line([(x1, y1-5), (x2, y2-5)], fill=(120, 160, 170, 80), width=3)

    # Add water shimmer
    for _ in range(200):
        idx = random.randint(0, len(points)-1)
        x, y = points[idx]
        x += random.randint(-25, 25)
        y += random.randint(-15, 15)
        r = random.randint(2, 5)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(160, 200, 210, 100))

    layer = layer.filter(ImageFilter.GaussianBlur(radius=1))
    return layer

# ---- ROADS LAYER ----
def gen_roads():
    """Roads: village path network, transparent background"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    road_color = (155, 130, 95, 230)
    road_edge = (130, 108, 75, 180)

    # Main road: north gate -> plaza -> south
    nx = 55 * TW
    draw.line([(nx, 3*TH), (nx, 24*TH)], fill=road_color, width=32)
    draw.line([(nx, 24*TH), (52*TW, 30*TH)], fill=road_color, width=30)
    draw.line([(52*TW, 30*TH), (52*TW, 46*TH)], fill=road_color, width=28)

    # Plaza circular path
    cx, cy = 52*TW, 30*TH
    draw.ellipse([cx-8*TW, cy-5*TH, cx+8*TW, cy+5*TH], outline=road_color, width=24)

    # Road to church
    draw.line([(45*TW, 28*TH), (35*TW, 20*TH)], fill=road_color, width=22)

    # Road to gigas tree
    draw.line([(44*TW, 32*TH), (20*TW, 38*TH)], fill=road_color, width=22)

    # Road to houses
    draw.line([(55*TW, 26*TH), (60*TW, 18*TH)], fill=road_color, width=18)
    draw.line([(50*TW, 38*TH), (55*TW, 42*TH)], fill=road_color, width=18)

    # Road to farmland
    draw.line([(52*TW, 42*TH), (50*TW, 55*TH)], fill=road_color, width=20)

    # Road edges (darker)
    for offset in [-2, 2]:
        draw.line([(nx+offset, 3*TH), (nx+offset, 24*TH)], fill=road_edge, width=1)

    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.5))
    return layer

# ---- BUILDINGS LAYER ----
def gen_buildings():
    """Buildings: structure footprints/roofs, transparent background"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    buildings = [
        # Church/library (large, stone+wood)
        {"x": 30*TW, "y": 14*TH, "w": 10*TW, "h": 8*TH, "type": "church"},
        # Houses
        {"x": 50*TW, "y": 15*TH, "w": 5*TW, "h": 5*TH, "type": "house"},
        {"x": 58*TW, "y": 16*TH, "w": 5*TW, "h": 5*TH, "type": "house"},
        {"x": 62*TW, "y": 15*TH, "w": 4*TW, "h": 4*TH, "type": "house"},
        {"x": 45*TW, "y": 39*TH, "w": 5*TW, "h": 5*TH, "type": "house"},
        {"x": 52*TW, "y": 40*TH, "w": 5*TW, "h": 4*TH, "type": "house"},
        {"x": 59*TW, "y": 39*TH, "w": 4*TW, "h": 5*TH, "type": "house"},
        # North gate structure
        {"x": 52*TW, "y": 4*TH, "w": 6*TW, "h": 5*TH, "type": "gate"},
        # Small sheds
        {"x": 22*TW, "y": 36*TH, "w": 3*TW, "h": 3*TH, "type": "shed"},
        {"x": 68*TW, "y": 30*TH, "w": 3*TW, "h": 3*TH, "type": "shed"},
    ]

    for b in buildings:
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        if b["type"] == "church":
            # Stone walls with wood roof
            draw.rectangle([x, y, x+w, y+h], fill=(140, 135, 125, 255))
            # Roof
            roof_y = y - h//4
            draw.polygon([(x-5, y+h), (x+w//2, roof_y), (x+w+5, y+h)], fill=(100, 70, 50, 255))
            # Tower
            draw.rectangle([x+w//2-15, y-20, x+w//2+15, y+10], fill=(130, 125, 115, 255))
            draw.polygon([(x+w//2-18, y), (x+w//2, y-40), (x+w//2+18, y)], fill=(90, 65, 45, 255))
        elif b["type"] == "gate":
            # Stone gate
            draw.rectangle([x, y, x+w, y+h], fill=(130, 125, 115, 255))
            draw.rectangle([x+w//2-20, y, x+w//2+20, y+h], fill=(100, 95, 88, 255))
            draw.rectangle([x+w//2-20, y+h-30, x+w//2+20, y+h], fill=(80, 55, 40, 255))
        elif b["type"] == "shed":
            draw.rectangle([x, y, x+w, y+h], fill=WOOD + (255,))
            draw.polygon([(x-3, y), (x+w//2, y-15), (x+w+3, y)], fill=(100, 70, 50, 255))
        else:  # house
            # Walls
            draw.rectangle([x, y, x+w, y+h], fill=(180, 155, 120, 255))
            # Thatched roof
            roof_h = h // 3
            draw.polygon([(x-5, y+5), (x+w//2, y-roof_h), (x+w+5, y+5)], fill=(140, 100, 65, 255))
            # Door
            draw.rectangle([x+w//2-8, y+h-20, x+w//2+8, y+h], fill=(80, 55, 40, 255))
            # Window
            draw.rectangle([x+5, y+8, x+18, y+20], fill=(120, 140, 150, 200))

    return layer

# ---- VEGETATION LAYER ----
def gen_vegetation():
    """Vegetation: trees, bushes, hedges, transparent background"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Giant tree at gigas clearing
    gx, gy = 16*TW, 36*TH
    # Trunk
    draw.rectangle([gx-15, gy-10, gx+15, gy+30], fill=(80, 55, 40, 255))
    # Canopy (large)
    for r in range(100, 60, -10):
        c = (max(0, MOSS[0]-r//4), max(0, MOSS[1]-r//6), max(0, MOSS[2]-r//8), 220)
        draw.ellipse([gx-r, gy-r-20, gx+r, gy+r-20], fill=c)

    # Scattered trees
    tree_positions = [
        (8*TW, 10*TH), (12*TW, 8*TH), (18*TW, 6*TH), (25*TW, 5*TH),
        (75*TW, 8*TH), (82*TW, 12*TH), (88*TW, 6*TH), (95*TW, 14*TH),
        (6*TW, 20*TH), (10*TW, 45*TH), (8*TW, 55*TH),
        (70*TW, 45*TH), (78*TW, 50*TH), (85*TW, 48*TH),
        (92*TW, 55*TH), (96*TW, 50*TH),
        (30*TW, 48*TH), (40*TW, 52*TH), (60*TW, 50*TH),
        # Forest path area
        (45*TW, 2*TH), (58*TW, 1*TH), (65*TW, 3*TH), (70*TW, 1*TH),
    ]

    for tx, ty in tree_positions:
        r = random.randint(18, 28)
        # Canopy
        c = (MOSS[0] + random.randint(-10, 10), MOSS[1] + random.randint(-10, 10), MOSS[2] + random.randint(-5, 5), 230)
        draw.ellipse([tx-r, ty-r, tx+r, ty+r], fill=c)
        # Trunk
        draw.rectangle([tx-4, ty+r-5, tx+4, ty+r+10], fill=(80, 55, 40, 220))

    # Bushes and hedges
    for _ in range(60):
        x = random.randint(2, COLS-2) * TW
        y = random.randint(2, ROWS-2) * TH
        # Don't place on plaza
        if 42*TW < x < 62*TW and 24*TH < y < 36*TH:
            continue
        r = random.randint(8, 14)
        c = (MOSS[0] + random.randint(-8, 8), MOSS[1] + random.randint(-8, 8), MOSS[2], 200)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=c)

    # Farmland crops (rows of wheat)
    for fy in range(50, 60):
        for fx in range(25, 85):
            x, y = fx * TW, fy * TH
            if random.random() < 0.7:
                draw.rectangle([x+4, y+8, x+8, y+20], fill=WHEAT + (180,))
                draw.rectangle([x+14, y+8, x+18, y+20], fill=WHEAT + (160,))

    return layer

# ---- OCCLUSION LAYER ----
def gen_occlusion():
    """Occlusion: building roofs and tree canopies that hide characters, transparent"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Church roof
    x, y, w, h = 30*TW, 14*TH, 10*TW, 8*TH
    draw.polygon([(x-5, y+h), (x+w//2, y-h//4), (x+w+5, y+h)], fill=(100, 70, 50, 180))
    # Tower roof
    draw.polygon([(x+w//2-18, y), (x+w//2, y-40), (x+w//2+18, y)], fill=(90, 65, 45, 180))

    # House roofs
    house_roofs = [
        (50*TW, 15*TH, 5*TW, 5*TH), (58*TW, 16*TH, 5*TW, 5*TH),
        (62*TW, 15*TH, 4*TW, 4*TH), (45*TW, 39*TH, 5*TW, 5*TH),
        (52*TW, 40*TH, 5*TW, 4*TH), (59*TW, 39*TH, 4*TW, 5*TH),
    ]
    for hx, hy, hw, hh in house_roofs:
        roof_h = hh // 3
        draw.polygon([(hx-5, hy+5), (hx+hw//2, hy-roof_h), (hx+hw+5, hy+5)], fill=(140, 100, 65, 170))

    # Gate roof
    gx, gy, gw, gh = 52*TW, 4*TH, 6*TW, 5*TH
    draw.rectangle([gx, gy, gx+gw, gy+15], fill=(100, 70, 50, 160))

    # Giant tree canopy
    gx2, gy2 = 16*TW, 36*TH
    draw.ellipse([gx2-100, gy2-120, gx2+100, gy2+80], fill=(MOSS[0]-20, MOSS[1]-15, MOSS[2]-10, 160))

    # Scattered tree canopies
    tree_positions = [
        (8*TW, 10*TH), (12*TW, 8*TH), (18*TW, 6*TH), (25*TW, 5*TH),
        (75*TW, 8*TH), (82*TW, 12*TH), (88*TW, 6*TH), (95*TW, 14*TH),
        (6*TW, 20*TH), (10*TW, 45*TH), (8*TW, 55*TH),
        (70*TW, 45*TH), (78*TW, 50*TH), (85*TW, 48*TH),
        (92*TW, 55*TH), (96*TW, 50*TH),
    ]
    for tx, ty in tree_positions:
        r = random.randint(18, 28)
        draw.ellipse([tx-r, ty-r, tx+r, ty+r], fill=(MOSS[0]-10, MOSS[1]-8, MOSS[2]-5, 140))

    return layer

# ---- FOREGROUND LAYER ----
def gen_foreground():
    """Foreground: edge elements, transparent with real alpha"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Bottom edge rocks and bushes
    for x in range(0, W, 40):
        r = random.randint(15, 30)
        y = H - random.randint(10, 35)
        # Rock
        draw.ellipse([x-r//2, y-r//2, x+r//2, y+r//2], fill=(100, 95, 90, 200))
        # Grass tuft
        for i in range(3):
            gx = x + random.randint(-10, 10)
            gy = y - random.randint(5, 15)
            draw.line([(gx, gy), (gx+random.randint(-3, 3), gy-random.randint(5, 10))], fill=MOSS + (180,), width=2)

    # Left edge fence
    for y in range(20*TH, 50*TH, 30):
        draw.rectangle([0, y, 15, y+20], fill=WOOD + (200,))
        draw.line([(0, y+5), (15, y+5)], fill=(100, 70, 50, 220), width=3)
        draw.line([(0, y+15), (15, y+15)], fill=(100, 70, 50, 220), width=3)

    # Right edge bushes
    for y in range(10*TH, H, 50):
        r = random.randint(20, 35)
        draw.ellipse([W-r*2, y-r, W, y+r], fill=(MOSS[0]-10, MOSS[1]-5, MOSS[2], 190))

    return layer

# ---- LIGHTING LAYER ----
def gen_lighting():
    """Lighting: warm light overlay with transparency"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Warm glow from plaza center
    cx, cy = 52*TW, 30*TH
    for r in range(400, 0, -20):
        alpha = int(30 * (1 - r/400))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 220, 150, alpha))

    # Church warm light
    cx2, cy2 = 35*TW, 18*TH
    for r in range(150, 0, -15):
        alpha = int(25 * (1 - r/150))
        draw.ellipse([cx2-r, cy2-r, cx2+r, cy2+r], fill=(255, 200, 120, alpha))

    # Home hearth glow
    for hx, hy in [(55*TW, 17*TH), (50*TW, 41*TH)]:
        for r in range(80, 0, -10):
            alpha = int(20 * (1 - r/80))
            draw.ellipse([hx-r, hy-r, hx+r, hy+r], fill=(255, 180, 100, alpha))

    # North gate cooler light
    cx3, cy3 = 55*TW, 6*TH
    for r in range(100, 0, -10):
        alpha = int(15 * (1 - r/100))
        draw.ellipse([cx3-r, cy3-r, cx3+r, cy3+r], fill=(150, 180, 200, alpha))

    layer = layer.filter(ImageFilter.GaussianBlur(radius=15))
    return layer

# ---- WEATHER LAYER ----
def gen_weather():
    """Weather: rain/mist overlay with transparency"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Overall mist
    for _ in range(500):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.randint(20, 60)
        alpha = random.randint(5, 15)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(180, 200, 210, alpha))

    # Rain streaks
    for _ in range(800):
        x = random.randint(0, W)
        y = random.randint(0, H)
        length = random.randint(8, 16)
        alpha = random.randint(30, 60)
        draw.line([(x, y), (x-2, y+length)], fill=(160, 190, 210, alpha), width=1)

    # Heavier mist at forest path (boundary area)
    fx, fy = 55*TW, 3*TH
    for r in range(200, 0, -15):
        alpha = int(8 * (1 - r/200))
        draw.ellipse([fx-r, fy-r, fx+r, fy+r], fill=(60, 70, 104, alpha))

    layer = layer.filter(ImageFilter.GaussianBlur(radius=2))
    return layer

# ---- DATA LAYERS ----
def gen_collision():
    """Collision grid: 1=blocked, 0=walkable"""
    grid = [[0]*COLS for _ in range(ROWS)]

    # Block buildings
    buildings = [
        (30, 14, 10, 8), (50, 15, 5, 5), (58, 16, 5, 5),
        (62, 15, 4, 4), (45, 39, 5, 5), (52, 40, 5, 4),
        (59, 39, 4, 5), (52, 4, 6, 5), (22, 36, 3, 3), (68, 30, 3, 3),
    ]
    for bx, by, bw, bh in buildings:
        for ty in range(by, by+bh):
            for tx in range(bx, bx+bw):
                if 0 <= tx < COLS and 0 <= ty < ROWS:
                    grid[ty][tx] = 1

    # Block water (river approximation)
    for i in range(20):
        t = i / 19
        x = int(5 + t * 95)
        y = int(2 + t * 58)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                tx, ty = x+dx, y+dy
                if 0 <= tx < COLS and 0 <= ty < ROWS:
                    grid[ty][tx] = 1

    # Block giant tree trunk
    for ty in range(34, 40):
        for tx in range(14, 19):
            grid[ty][tx] = 1

    # Block border edges (except north gate and forest path)
    for tx in range(COLS):
        grid[0][tx] = 1
        grid[ROWS-1][tx] = 1
    for ty in range(ROWS):
        grid[ty][0] = 1
        grid[ty][COLS-1] = 1

    # Clear north gate passage
    for ty in range(3, 10):
        for tx in range(52, 60):
            grid[ty][tx] = 0

    return grid

def gen_walkable(collision):
    """Walkable: inverse of collision, plus some restricted areas"""
    grid = [[0]*COLS for _ in range(ROWS)]
    for ty in range(ROWS):
        for tx in range(COLS):
            grid[ty][tx] = 0 if collision[ty][tx] else 1
    return grid

def gen_interaction():
    """Interaction points"""
    interactions = [
        {"id": "church_library", "tile_x": 35, "tile_y": 18, "kind": "enter", "label": "Enter Church Library", "action_id": "scene:church_library", "scene_id": "church_library"},
        {"id": "home_entrance_n", "tile_x": 52, "tile_y": 17, "kind": "enter", "label": "Enter Home", "action_id": "scene:home_hearth", "scene_id": "home_hearth"},
        {"id": "home_entrance_s", "tile_x": 50, "tile_y": 41, "kind": "enter", "label": "Enter Neighbor House", "action_id": "scene:home_hearth_b", "scene_id": "home_hearth"},
        {"id": "gigas_tree", "tile_x": 16, "tile_y": 38, "kind": "examine", "label": "Gigas Cedar Tree", "action_id": "examine:gigas_tree"},
        {"id": "north_gate", "tile_x": 55, "tile_y": 6, "kind": "examine", "label": "North Gate", "action_id": "examine:north_gate", "scene_id": "north_gate"},
        {"id": "forest_entrance", "tile_x": 55, "tile_y": 1, "kind": "travel", "label": "Forest Path", "action_id": "scene:forest_path", "scene_id": "forest_path"},
        {"id": "plaza_center", "tile_x": 52, "tile_y": 30, "kind": "examine", "label": "Village Plaza", "action_id": "examine:plaza"},
        {"id": "river_bridge", "tile_x": 50, "tile_y": 30, "kind": "examine", "label": "River Bridge", "action_id": "examine:bridge"},
        {"id": "farmland", "tile_x": 50, "tile_y": 55, "kind": "examine", "label": "Farmland", "action_id": "examine:farmland"},
        {"id": "end_mountains", "tile_x": 55, "tile_y": 0, "kind": "travel", "label": "End Mountains", "action_id": "scene:end_mountains_cave", "scene_id": "end_mountains_cave"},
    ]
    return interactions

# ---- TILE ATLAS ----
def gen_tile_atlas():
    """Generate small tile atlas for terrain/water/road tiles"""
    atlas = Image.new("RGBA", (TW*8, TH*4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)

    tiles = [
        ("grass", 0, 0, MOSS),
        ("grass_dark", 1, 0, (MOSS[0]-15, MOSS[1]-10, MOSS[2]-5)),
        ("dirt", 2, 0, WOOD),
        ("stone", 3, 0, (120, 115, 110)),
        ("sand", 4, 0, (200, 180, 140)),
        ("bridge_h", 5, 0, (130, 95, 60)),
        ("bridge_v", 6, 0, (130, 95, 60)),
        ("crop", 7, 0, WHEAT),
        ("water_1", 0, 1, RAIN_TEAL),
        ("water_2", 1, 1, (RAIN_TEAL[0]+10, RAIN_TEAL[1]+10, RAIN_TEAL[2]+10)),
        ("water_edge", 2, 1, (90, 130, 140)),
        ("road_h", 3, 1, (155, 130, 95)),
        ("road_v", 4, 1, (155, 130, 95)),
        ("road_cross", 5, 1, (150, 125, 90)),
        ("cobble", 6, 1, (130, 125, 118)),
        ("wood_floor", 7, 1, (160, 120, 80)),
    ]

    for name, col, row, color in tiles:
        x, y = col*TW, row*TH
        # Base
        draw.rectangle([x, y, x+TW, y+TH], fill=color + (255,))
        # Add texture detail
        for _ in range(8):
            dx = random.randint(0, TW)
            dy = random.randint(0, TH)
            shade = random.randint(-20, 20)
            c = (max(0,min(255,color[0]+shade)), max(0,min(255,color[1]+shade)), max(0,min(255,color[2]+shade)), 255)
            draw.point((x+dx, y+dy), fill=c)

    return atlas

def gen_prop_atlas():
    """Generate prop atlas"""
    atlas = Image.new("RGBA", (TW*6, TH*6), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)

    # Tree
    tx, ty = 0, 0
    draw.ellipse([tx+2, ty+2, tx+TW-2, ty+TH-6], fill=MOSS + (255,))
    draw.rectangle([tx+TW//2-3, ty+TH-10, tx+TW//2+3, ty+TH-2], fill=(80, 55, 40, 255))

    # Bush
    tx, ty = TW, 0
    draw.ellipse([tx+4, ty+6, tx+TW-4, ty+TH-4], fill=(MOSS[0]-10, MOSS[1]-5, MOSS[2], 255))

    # Rock
    tx, ty = TW*2, 0
    draw.ellipse([tx+4, ty+8, tx+TW-4, ty+TH-4], fill=(100, 95, 90, 255))

    # Book/scroll
    tx, ty = TW*3, 0
    draw.rectangle([tx+4, ty+8, tx+TW-4, ty+TH-8], fill=PARCHMENT + (255,))
    draw.line([(tx+4, ty+12), (tx+TW-4, ty+12)], fill=INK + (200,), width=1)

    # Fence post
    tx, ty = TW*4, 0
    draw.rectangle([tx+8, ty+4, tx+14, ty+TH-4], fill=WOOD + (255,))

    # Lamp post
    tx, ty = TW*5, 0
    draw.rectangle([tx+12, ty+8, tx+16, ty+TH-2], fill=(80, 70, 60, 255))
    draw.ellipse([tx+8, ty+2, tx+20, ty+14], fill=(255, 220, 100, 180))

    # Basket
    tx, ty = 0, TH
    draw.ellipse([tx+4, ty+8, tx+TW-4, ty+TH-4], fill=(160, 120, 80, 255))

    # Training dummy
    tx, ty = TW, TH
    draw.rectangle([tx+TW//2-3, ty+4, tx+TW//2+3, ty+TH-4], fill=WOOD + (255,))
    draw.ellipse([tx+TW//2-8, ty, tx+TW//2+8, ty+16], fill=(180, 160, 130, 255))

    # Sign post
    tx, ty = TW*2, TH
    draw.rectangle([tx+10, ty+6, tx+TW-2, ty+16], fill=WOOD + (255,))
    draw.rectangle([tx+8, ty+16, tx+12, ty+TH-2], fill=(80, 55, 40, 255))

    # Crate
    tx, ty = TW*3, TH
    draw.rectangle([tx+4, ty+6, tx+TW-4, ty+TH-4], fill=(140, 100, 65, 255))
    draw.line([(tx+4, ty+TH//2), (tx+TW-4, ty+TH//2)], fill=(100, 70, 45, 255), width=1)

    # Well
    tx, ty = TW*4, TH
    draw.ellipse([tx+4, ty+8, tx+TW-4, ty+TH-4], fill=(110, 105, 100, 255))
    draw.ellipse([tx+8, ty+12, tx+TW-8, ty+TH-8], fill=RAIN_TEAL + (255,))

    return atlas

# ---- MAIN ----
def main():
    base_dir = r"C:\Users\liang\Desktop\UW\materials\inbox\visual\world"
    prefix = "VIS-MAP-001_UW-UPGRADE-1.0"

    # Find terrain texture
    terrain_src = None
    for f in os.listdir(base_dir):
        if f.startswith("Top_down_2D_RPG") and f.endswith(".png"):
            terrain_src = os.path.join(base_dir, f)
            break

    print("Generating terrain layer...")
    terrain = gen_terrain(terrain_src)
    terrain.save(os.path.join(base_dir, f"{prefix}_terrain.png"), "PNG")
    print(f"  terrain: {terrain.size}")

    print("Generating water layer...")
    water = gen_water()
    water.save(os.path.join(base_dir, f"{prefix}_water.png"), "PNG")
    print(f"  water: {water.size}")

    print("Generating roads layer...")
    roads = gen_roads()
    roads.save(os.path.join(base_dir, f"{prefix}_roads.png"), "PNG")
    print(f"  roads: {roads.size}")

    print("Generating buildings layer...")
    buildings = gen_buildings()
    buildings.save(os.path.join(base_dir, f"{prefix}_buildings.png"), "PNG")
    print(f"  buildings: {buildings.size}")

    print("Generating vegetation layer...")
    vegetation = gen_vegetation()
    vegetation.save(os.path.join(base_dir, f"{prefix}_vegetation.png"), "PNG")
    print(f"  vegetation: {vegetation.size}")

    print("Generating occlusion layer...")
    occlusion = gen_occlusion()
    occlusion.save(os.path.join(base_dir, f"{prefix}_occlusion.png"), "PNG")
    print(f"  occlusion: {occlusion.size}")

    print("Generating foreground layer...")
    foreground = gen_foreground()
    foreground.save(os.path.join(base_dir, f"{prefix}_foreground.png"), "PNG")
    print(f"  foreground: {foreground.size}")

    print("Generating lighting layer...")
    lighting = gen_lighting()
    lighting.save(os.path.join(base_dir, f"{prefix}_lighting.png"), "PNG")
    print(f"  lighting: {lighting.size}")

    print("Generating weather layer...")
    weather = gen_weather()
    weather.save(os.path.join(base_dir, f"{prefix}_weather.png"), "PNG")
    print(f"  weather: {weather.size}")

    print("Generating collision/walkable/interaction data...")
    collision = gen_collision()
    walkable = gen_walkable(collision)
    interaction = gen_interaction()

    # Composite preview
    print("Generating composite preview...")
    composite = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    composite.paste(terrain.convert("RGBA"), (0, 0))
    composite = Image.alpha_composite(composite, water)
    composite = Image.alpha_composite(composite, roads)
    composite = Image.alpha_composite(composite, buildings)
    composite = Image.alpha_composite(composite, vegetation)
    composite = Image.alpha_composite(composite, foreground)
    composite = Image.alpha_composite(composite, lighting)
    composite = Image.alpha_composite(composite, weather)
    composite_rgb = composite.convert("RGB")
    composite_rgb.thumbnail((1512, 896), Image.LANCZOS)
    composite_rgb.save(os.path.join(base_dir, f"{prefix}_composite_preview.png"), "PNG")
    print(f"  composite preview: {composite_rgb.size}")

    # Collision/walkable visualization
    coll_img = Image.new("RGB", (W, H), MOSS)
    draw = ImageDraw.Draw(coll_img)
    for ty in range(ROWS):
        for tx in range(COLS):
            x, y = tile_to_px(tx, ty)
            if collision[ty][tx]:
                draw.rectangle([x, y, x+TW, y+TH], fill=(200, 80, 80))
            elif not walkable[ty][tx]:
                draw.rectangle([x, y, x+TW, y+TH], fill=(150, 150, 100))
    for inter in interaction:
        x, y = tile_to_px(inter["tile_x"], inter["tile_y"])
        draw.ellipse([x+4, y+4, x+TW-4, y+TH-4], fill=(100, 200, 255))
    coll_img.thumbnail((1512, 896), Image.LANCZOS)
    coll_img.save(os.path.join(base_dir, f"{prefix}_collision_walkable_preview.png"), "PNG")
    print(f"  collision preview: {coll_img.size}")

    # Tile atlas
    print("Generating tile atlas...")
    tile_atlas = gen_tile_atlas()
    tile_atlas.save(os.path.join(base_dir, f"{prefix}_tile_atlas.png"), "PNG")
    print(f"  tile atlas: {tile_atlas.size}")

    # Prop atlas
    print("Generating prop atlas...")
    prop_atlas = gen_prop_atlas()
    prop_atlas.save(os.path.join(base_dir, f"{prefix}_prop_atlas.png"), "PNG")
    print(f"  prop atlas: {prop_atlas.size}")

    # Metadata JSON
    print("Generating metadata JSON...")
    layers_meta = {}
    for layer_name in ["terrain", "water", "roads", "buildings", "vegetation", "occlusion", "foreground", "lighting", "weather"]:
        layers_meta[layer_name] = {
            "source": f"materials/inbox/visual/world/{prefix}_{layer_name}.png",
            "size": [W, H],
            "format": "PNG",
            "alpha": layer_name in ["occlusion", "foreground", "lighting", "weather", "water", "roads", "buildings", "vegetation"]
        }

    meta = {
        "request_id": "VIS-MAP-001",
        "batch": "UW-UPGRADE-1.0",
        "runtime_size": [W, H],
        "tile_size": [TW, TH],
        "grid": [COLS, ROWS],
        "layers": layers_meta,
        "data": {
            "collision": {
                "type": "grid",
                "width": COLS,
                "height": ROWS,
                "values": collision
            },
            "walkable": {
                "type": "grid",
                "width": COLS,
                "height": ROWS,
                "values": walkable
            },
            "interaction": interaction
        },
        "atlases": {
            "tile_atlas": {
                "source": f"materials/inbox/visual/world/{prefix}_tile_atlas.png",
                "tile_size": [TW, TH]
            },
            "prop_atlas": {
                "source": f"materials/inbox/visual/world/{prefix}_prop_atlas.png",
                "tile_size": [TW, TH]
            }
        },
        "composite_preview": f"materials/inbox/visual/world/{prefix}_composite_preview.png",
        "collision_preview": f"materials/inbox/visual/world/{prefix}_collision_walkable_preview.png"
    }

    meta_path = os.path.join(base_dir, f"{prefix}_map.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"  metadata JSON: {meta_path}")

    # Clean up terrain source
    if terrain_src:
        os.remove(terrain_src)
        print(f"  Cleaned up terrain source")

    print("\nVIS-MAP-001 generation complete!")
    print(f"Layers: 9 independent PNG files")
    print(f"Data: collision ({COLS}x{ROWS}), walkable ({COLS}x{ROWS}), {len(interaction)} interactions")
    print(f"Atlases: tile + prop")

if __name__ == "__main__":
    main()

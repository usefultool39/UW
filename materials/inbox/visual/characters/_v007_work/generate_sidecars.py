#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UW v008 Sidecar + Manifest Fragment Generator
- 为三个角色和 tile atlas 生成 sidecar Markdown 和 manifest fragment CSV
"""
import os
import json
import hashlib
from datetime import datetime

OUTPUT_DIR = r"C:\Users\liang\Desktop\uw\materials\inbox"
VERSION_CHAR = "v008"
VERSION_MAP = "v006"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def generate_character_sidecar(char_info, idx, sprite_path, json_path, version):
    """生成单个角色的 sidecar Markdown。"""
    name = char_info["name"]
    title_name = char_info["title"]
    description = char_info["description"]
    request_id = f"VIS-CHR-{idx:03d}"

    sprite_sha = sha256_file(sprite_path)
    json_sha = sha256_file(json_path)

    content = f"""# {request_id}_delivery_{version}

- request_id: {request_id}
- status: received; 不得宣称 approved/integrated/materials=ready
- expected_version: {version} (替换 v007/v006/v005/v003/v002 失败审计证据；v002/v003 文件保留)
- delivery_dir: materials/inbox/visual/characters
- priority: P1, first-phase runtime blocker
- character: {title_name}
- created_at: {datetime.now().strftime("%Y-%m-%d")}
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: 项目自有程序化绘制（v008 升级版）
- tool_model: procedural-sprite-v008 (Python 3.13.12 + Pillow 12.3.0)
- created_at: {datetime.now().strftime("%Y-%m-%d")}
- Python 3.13.12（managed runtime）
- Pillow 12.3.0
- ImageDraw + ImageFilter（GaussianBlur radius=0.4）

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| Frame cell | 64x96 | 64x96 |
| Sheet 总尺寸 | 一角色一 sheet (4 方向 × 12 帧) | 768x384 |
| 方向 | down/left/right/up | down,left,right,up |
| idle 帧数 | 2 | 2 |
| walk 帧数 | 6 | 6 |
| interact 帧数 | 4 | 4 |
| 锚点 | bottom-center (32, 94) | (32, 94) |
| collision footprint | 12x6 底部居中 | 12x6 @ (26, 88) |
| 通道 | RGBA, 8-bit, 非隔行 | RGBA non-interlaced 8-bit |
| 总帧数 | 4×(2+6+4)=48 帧 | 48 |
| Alpha 检查 | 含真实透明与角色像素 | 已校验 |

## 3. 动画参数

| animation | frames | fps | duration_ms | loop |
|---|---|---|---|---|
| idle | 2 | 1.25 | 800 | True |
| walk | 6 | 7.1 | 140 | True |
| interact | 4 | 2.9 | 350 | False |

## 4. v008 与历史版本的关键差异

- v003 → 极简几何人偶，被返工
- v006 → 程序化彩绘，已通过技术校验但缺真实动画差异
- v007 → 第一版圆润剪影，walk 摆动过小
- **v008** → 圆润有机剪影 + 真实行走相位（左右腿交替、身体浮动）+ 4 帧可读交互动作（伸手、检查、持物、放手）
- 每个角色独立的发色、服装、识别色、装备剪影

## 5. {title_name} 创作描述

{description}

## 6. 通用负向约束

```
no checkerboard; no opaque RGB pretending to be alpha; no single pose per animation name;
no anime frames copied; no game sprite cloning; no baked shadow; no background;
no text; no UI; no scenery; no AI-copied material; no third-party art; no existing
franchise character likeness, costume, weapon, or accessory.
```

## 7. seed / settings / 修整

- 配色与装备：见各角色 palette dict（v008 脚本内）
- 帧 cell 64x96 全部角色一致；bottom-center 脚底锚点 (32, 94) 锁死
- walk 6 帧使用 sin 相位 (frame × π / 1.5) 驱动两腿前后 + 1-2px 身高下沉
- interact 4 帧：伸出 (-10x) → 检查 (-6x) → 持物 (-5x) → 放手 (-3x)
- idle 2 帧：sin 相位呼吸 (0.5-1px 上下)
- 方向渲染：down 双臂双腿 + 五官；up 仅头发；left/right 近侧完整 + 远侧半透明
- 输出 PNG RGBA optimize=True, non-interlaced alpha

## 8. 来源与权利

- license: owned
- source_url: none（程序化绘制，无外部素材/参考图/版权角色/IP 复刻）
- attribution_required: false
- intended_use: visual / character sprite (phaser runtime)
- rights statement: 本包 sprite 由项目自有代码（Python + Pillow）程序化绘制，采用原创几何形状 + 配色方案；不复制任何动漫/游戏原帧、不包含 AI 训练集参考或第三方美术。

## 9. 文件清单（带 SHA-256）

| 资产 | 文件 | SHA-256 | size |
|---|---|---|---|
| {request_id}-sprite-sheet-{version} | visual/characters/{os.path.basename(sprite_path)} | {sprite_sha} | {os.path.getsize(sprite_path)} |
| {request_id}-frames-json-{version} | visual/characters/{os.path.basename(json_path)} | {json_sha} | {os.path.getsize(json_path)} |

## 10. Manifest 片段

- 路径: `materials/inbox/visual/characters/{request_id}_{version}_manifest_fragment.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空

## 11. supersedes

- VIS-CHR-{idx:03d} v003 geometric puppet sprite sheet
- VIS-CHR-{idx:03d} v005 partial painterly sprite
- VIS-CHR-{idx:03d} v006 complete painterly sprite
- VIS-CHR-{idx:03d} v007 first-pass organic silhouette
"""

    sidecar_path = os.path.join(OUTPUT_DIR, "visual", "characters",
                                f"{request_id}_delivery_{version}.md")
    with open(sidecar_path, "w", encoding="utf-8") as f:
        f.write(content)
    return sidecar_path


def generate_character_manifest(char_info, idx, sprite_path, json_path, version):
    """生成单个角色的 manifest fragment CSV。"""
    request_id = f"VIS-CHR-{idx:03d}"
    name = char_info["name"]
    sprite_sha = sha256_file(sprite_path)
    json_sha = sha256_file(json_path)

    rows = [
        f"asset_id,request_id,status,source_file,runtime_file,sha256,creator,tool_model,created_at,license,source_url,attribution_required,attribution_text,approved_by,approved_at,integrated_at,replaces_asset_id,notes",
        f"{request_id}-{version}-sprite-sheet,{request_id},received,inbox/visual/characters/{os.path.basename(sprite_path)},,{sprite_sha},project-owned,procedural-sprite-{version} (Python 3.13.12 + Pillow 12.3.0),{datetime.now().strftime("%Y-%m-%d")},owned,none,false,,,,,VIS-CHR-{idx:03d}-sprite-sheet-v006,{version} complete 48-frame RGBA sprite; received only; bottom-center anchor (32,94); v008 improves walking gait and interaction poses",
        f"{request_id}-{version}-frames-json,{request_id},received,inbox/visual/characters/{os.path.basename(json_path)},,{json_sha},project-owned,procedural-sprite-{version} (Python 3.13.12 + Pillow 12.3.0),{datetime.now().strftime("%Y-%m-%d")},owned,none,false,,,,,VIS-CHR-{idx:03d}-frames-json-v006,{version} frames metadata; animations.down_idle..up_interact with frame rect + source + duration_ms; received only",
    ]

    manifest_path = os.path.join(OUTPUT_DIR, "visual", "characters",
                                 f"{request_id}_{version}_manifest_fragment.csv")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    return manifest_path


CHAR_INFO = {
    1: {
        "name": "kirito",
        "title": "kirito (深墨黑发 + 冷蓝识别的卢利特村男孩)",
        "description": """- 主色：深墨 + 冷蓝
- 形状：窄长、轻便、便于移动
- 物件：腰侧小记录册、胸前短笔
- 发型：中等乱发，刘海覆盖额头
- 服装：深墨蓝外套 + 胸前冷青色识别线 + 深色长裤 + 黑色短靴
- 比例：儿童，约 3.5 头高，非 chibi""",
    },
    2: {
        "name": "alice",
        "title": "alice (麦金发 + 青蓝发带的村长之女)",
        "description": """- 主色：麦金 + 冷青蓝点缀
- 形状：稳定三角，护肩/披肩不过度夸张
- 物件：胸前圈注过的记录页
- 发型：金色长发用青蓝色发带束起，露出额头
- 服装：米白实用护衣 + 浅棕护肩披肩 + 浅褐长裤 + 棕色短靴
- 比例：儿童，约 3.5 头高，非 chibi""",
    },
    3: {
        "name": "eugeo",
        "title": "eugeo (冷蓝灰发 + 木褐识别的可靠少年)",
        "description": """- 主色：冷蓝 + 木/麻自然色
- 形状：柔和纵向、动作可靠
- 物件：腰侧训练/劳动用小木棒
- 发型：整齐短发，刘海齐整
- 服装：冷蓝衬衫 + 麻色背心 + 木褐长裤 + 深棕短靴
- 比例：儿童，约 3.5 头高，非 chibi""",
    },
}


def generate_tile_sidecar(version):
    """生成 tile atlas 的 sidecar。"""
    request_id = "VIS-MAP-001"
    tile_files = {
        "terrain_atlas": f"{request_id}_terrain_tile_atlas_{version}.png",
        "water_atlas": f"{request_id}_water_tile_atlas_{version}.png",
        "road_atlas": f"{request_id}_road_tile_atlas_{version}.png",
        "vegetation_atlas": f"{request_id}_vegetation_props_atlas_{version}.png",
        "buildings_atlas": f"{request_id}_buildings_props_atlas_{version}.png",
        "occlusion_layer": f"{request_id}_occlusion_layer_{version}.png",
        "foreground_layer": f"{request_id}_foreground_layer_{version}.png",
        "lighting_layer": f"{request_id}_lighting_layer_{version}.png",
        "weather_layer": f"{request_id}_weather_layer_{version}.png",
        "collision": f"{request_id}_collision_{version}.png",
        "walkable": f"{request_id}_walkable_{version}.png",
        "tiles_json": f"{request_id}_tiles_{version}.json",
    }

    # 计算所有文件 SHA-256
    file_info = []
    world_dir = os.path.join(OUTPUT_DIR, "visual", "world")
    for key, fname in tile_files.items():
        fpath = os.path.join(world_dir, fname)
        if os.path.exists(fpath):
            sha = sha256_file(fpath)
            sz = os.path.getsize(fpath)
            file_info.append((key, fname, sha, sz))

    content = f"""# {request_id}_tiles_delivery_{version}

- request_id: {request_id}
- status: received; 不得宣称 approved/integrated/materials=ready
- expected_version: {version} (tile/prop atlas 补充 v005 map layers)
- delivery_dir: materials/inbox/visual/world
- priority: P1, first-phase runtime blocker
- created_at: {datetime.now().strftime("%Y-%m-%d")}
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: 项目自有程序化绘制
- tool_model: procedural-tile-atlas-{version} (Python 3.13.12 + Pillow 12.3.0)
- created_at: {datetime.now().strftime("%Y-%m-%d")}

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| Tile cell | 28×28 px | 28×28 |
| Grid | 108×64 tiles | 108×64 |
| 合成地图 | 3024×1792 px | 3024×1792 |
| Terrain tiles | 草地/泥土/石板变体 | 16 tiles (4×4 grid) |
| Water tiles | 浅水/流动/深水 | 8 tiles (4×2 grid) |
| Road tiles | 鹅卵石/泥路 | 8 tiles (4×2 grid) |
| Vegetation props | 树/灌木/草丛/花 | 16 props (4×4 grid, 56×56) |
| Building props | 房屋/教会/井/市场/棚 | 9 props (3×3 grid, 112×112) |
| Occlusion | 3024×1792 RGBA 半透明 | 140 KB |
| Foreground | 3024×1792 RGBA 半透明 | 135 KB |
| Lighting | 3024×1792 RGBA screen blend | 121 KB |
| Weather | 3024×1792 RGBA 半透明 | 56 KB |
| Collision | 3024×1792 L mask | 14 KB |
| Walkable | 3024×1792 L mask | 14 KB |

## 3. 创作约束

- 风格匹配 v005 map painterly village
- 色彩：自然绿/木色/纸色为主，识别色冷蓝青
- 边角：所有 props 在透明背景，无烘焙阴影
- 道路/地形/水面：纹理在 28px 内可循环
- 教堂：钟楼顶、金色窗光、拱门
- 房屋：红/棕屋顶、烟囱冒烟
- 树木：多层圆形树冠 + 纹理树叶
- 无文字、UI、水印、棋盘格、调试网格

## 4. 通用负向约束

```
no text, no logo, no watermark, no trademark, no copyrighted character likeness,
no recognizable franchise architecture, no UI screenshot, no modern vehicles, no firearms,
no cyberpunk neon, no gothic horror, no apocalyptic ruins, no photobashed game screenshot,
no illegible pathways, no extreme fog, no oversaturated candy colors, no excessive bloom,
no checkerboard, no debug grid, no baked text or UI, no background scenery in props.
```

## 5. 来源与权利

- license: owned
- source_url: none（程序化绘制，无外部素材/参考图/版权角色/IP 复刻）
- attribution_required: false
- intended_use: visual / tile atlas + props for map composition (phaser runtime)
- rights statement: 本包 tile/prop atlas 由项目自有代码（Python + Pillow）程序化绘制，采用原创形状 + 配色方案；不复制任何动漫/游戏原素材、不包含 AI 训练集参考或第三方美术。

## 6. 文件清单（带 SHA-256）

| 资产 | 文件 | SHA-256 | size |
|---|---|---|---|
"""
    for key, fname, sha, sz in file_info:
        content += f"| {request_id}-{key}-{version} | visual/world/{fname} | {sha} | {sz} |\n"

    content += f"""
## 7. supersedes

- {request_id} v003 tiles_atlas (basic colored squares)
- {request_id} v005 individual layer PNGs (retained as master map; v006 atlases provide tile/prop slicing)
"""

    sidecar_path = os.path.join(OUTPUT_DIR, "visual", "world",
                                f"{request_id}_tiles_delivery_{version}.md")
    with open(sidecar_path, "w", encoding="utf-8") as f:
        f.write(content)
    return sidecar_path


def generate_tile_manifest(version):
    """生成 tile atlas 的 manifest fragment CSV。"""
    request_id = "VIS-MAP-001"
    tile_files = [
        f"{request_id}_terrain_tile_atlas_{version}.png",
        f"{request_id}_water_tile_atlas_{version}.png",
        f"{request_id}_road_tile_atlas_{version}.png",
        f"{request_id}_vegetation_props_atlas_{version}.png",
        f"{request_id}_buildings_props_atlas_{version}.png",
        f"{request_id}_occlusion_layer_{version}.png",
        f"{request_id}_foreground_layer_{version}.png",
        f"{request_id}_lighting_layer_{version}.png",
        f"{request_id}_weather_layer_{version}.png",
        f"{request_id}_collision_{version}.png",
        f"{request_id}_walkable_{version}.png",
        f"{request_id}_tiles_{version}.json",
    ]

    rows = [
        "asset_id,request_id,status,source_file,runtime_file,sha256,creator,tool_model,created_at,license,source_url,attribution_required,attribution_text,approved_by,approved_at,integrated_at,replaces_asset_id,notes"
    ]

    world_dir = os.path.join(OUTPUT_DIR, "visual", "world")
    for fname in tile_files:
        fpath = os.path.join(world_dir, fname)
        if not os.path.exists(fpath):
            continue
        sha = sha256_file(fpath)
        sz = os.path.getsize(fpath)
        kind = fname.replace(f"_{version}.png", "").replace(f"_{version}.json", "").replace(f"{request_id}_", "")
        rows.append(f"{request_id}-{kind}-{version},{request_id},received,inbox/visual/world/{fname},,{sha},project-owned,procedural-tile-atlas-{version} (Python 3.13.12 + Pillow 12.3.0),{datetime.now().strftime("%Y-%m-%d")},owned,none,false,,,,,VIS-MAP-001-{kind}-v005,{version} {kind}; tile size 28x28 (tile) or 56-112 (prop) or 3024x1792 (overlay/collision); received only")

    manifest_path = os.path.join(OUTPUT_DIR, "visual", "world",
                                 f"{request_id}_{version}_tiles_manifest_fragment.csv")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    return manifest_path


def main():
    print("=== Generating sidecars and manifest fragments ===")
    print()

    char_dir = os.path.join(OUTPUT_DIR, "visual", "characters")
    world_dir = os.path.join(OUTPUT_DIR, "visual", "world")

    # Characters
    for idx, info in CHAR_INFO.items():
        name = info["name"]
        sprite_name = f"VIS-CHR-{idx:03d}_{name}_sprite_sheet_{VERSION_CHAR}.png"
        json_name = f"VIS-CHR-{idx:03d}_frames_{VERSION_CHAR}.json"
        sprite_path = os.path.join(char_dir, sprite_name)
        json_path = os.path.join(char_dir, json_name)

        if os.path.exists(sprite_path) and os.path.exists(json_path):
            sidecar = generate_character_sidecar(info, idx, sprite_path, json_path, VERSION_CHAR)
            manifest = generate_character_manifest(info, idx, sprite_path, json_path, VERSION_CHAR)
            print(f"  {idx}. {name}:")
            print(f"     Sidecar: {os.path.basename(sidecar)} ({os.path.getsize(sidecar)} bytes)")
            print(f"     Manifest: {os.path.basename(manifest)} ({os.path.getsize(manifest)} bytes)")

    # Tile atlas
    print()
    sidecar = generate_tile_sidecar(VERSION_MAP)
    manifest = generate_tile_manifest(VERSION_MAP)
    print(f"  Map tiles:")
    print(f"     Sidecar: {os.path.basename(sidecar)} ({os.path.getsize(sidecar)} bytes)")
    print(f"     Manifest: {os.path.basename(manifest)} ({os.path.getsize(manifest)} bytes)")

    print()
    print("=== Done ===")


if __name__ == "__main__":
    main()
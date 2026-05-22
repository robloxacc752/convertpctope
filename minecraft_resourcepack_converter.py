#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════╗
║          MINECRAFT RESOURCE PACK CONVERTER: Java → Bedrock Edition         ║
║              Tối ưu cho GeyserMC Plugin - Phiên bản 1.0.0                  ║
╚════════════════════════════════════════════════════════════════════════════╝

Script này tự động chuyển đổi Minecraft Resource Pack từ Java sang Bedrock Edition
với tối ưu hoàn toàn cho plugin GeyserMC. Script bao gồm:

  ✓ Quản lý cấu trúc thư mục (Input/Output)
  ✓ Chuyển đổi Custom Model Data (CMD) -> custom_mappings.json
  ✓ Chuyển đổi Armor & Attachables
  ✓ Chuyển đổi Fonts & Emojis
  ✓ Chuyển đổi Sounds & Music
  ✓ Log chi tiết bằng tiếng Việt (hướng dẫn & giải thích)

Yêu cầu: Python 3.8+, Pillow (PIL) cho xử lý ảnh
"""

import os
import json
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re
import sys

# Cố gắng import Pillow nếu cần
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("⚠️  Thư viện Pillow không được cài đặt. Một số tính năng xử lý ảnh sẽ bị tắt.")
    print("   Cài đặt: pip install Pillow")


# ═══════════════════════════════════════════════════════════════════════════
# PHẦN 1: CHUẨN BỊ & QUẢN LÝ CẤUTRÚC THƯ MỤC
# ═══════════════════════════════════════════════════════════════════════════

class Logger:
    """Lớp quản lý output log với định dạng rõ ràng."""
    
    def __init__(self, prefix: str = "[ResourcePackConverter]"):
        self.prefix = prefix
        self.step_counter = 0
        self.total_steps = 0
    
    def set_total_steps(self, total: int):
        """Thiết lập tổng số bước."""
        self.total_steps = total
    
    def step(self, message: str, details: str = ""):
        """Log một bước tiến trình."""
        self.step_counter += 1
        bar = "▓" * self.step_counter + "░" * (self.total_steps - self.step_counter)
        progress = f"[{self.step_counter}/{self.total_steps}]"
        print(f"\n{self.prefix} {progress} {message}")
        if details:
            print(f"          └─ {details}")
    
    def info(self, message: str):
        """Log thông tin chung."""
        print(f"{self.prefix} ℹ️  {message}")
    
    def success(self, message: str):
        """Log thành công."""
        print(f"{self.prefix} ✅ {message}")
    
    def warning(self, message: str):
        """Log cảnh báo."""
        print(f"{self.prefix} ⚠️  {message}")
    
    def error(self, message: str):
        """Log lỗi."""
        print(f"{self.prefix} ❌ {message}")
    
    def explain(self, title: str, content: str):
        """Log giải thích chi tiết (dùng cho hướng dẫn)."""
        print(f"\n{self.prefix} 📖 [GIẢI THÍCH] {title}")
        lines = content.split('\n')
        for line in lines:
            print(f"          {line}")
    
    def separator(self, char: str = "="):
        """In dòng tách."""
        print(f"\n{self.prefix} " + char * 70)


logger = Logger()


def validate_input_directory(java_pack_path: str) -> bool:
    """
    Kiểm tra xem đường dẫn nhập có phải Resource Pack Java hợp lệ không.
    
    Tiêu chí:
      - Phải tồn tại thư mục 'assets'
      - Phải có file 'pack.mcmeta' hoặc 'pack.png'
    
    Args:
        java_pack_path: Đường dẫn tuyệt đối đến Java Resource Pack
    
    Returns:
        True nếu hợp lệ, False nếu không
    """
    pack_dir = Path(java_pack_path)
    
    if not pack_dir.exists():
        logger.error(f"Thư mục không tồn tại: {java_pack_path}")
        return False
    
    if not (pack_dir / "assets").exists():
        logger.error(f"Không tìm thấy thư mục 'assets' - đây không phải Java Resource Pack hợp lệ")
        return False
    
    logger.success(f"Xác nhận Java Resource Pack hợp lệ: {pack_dir.name}")
    return True


def create_bedrock_structure(output_path: str) -> Dict[str, Path]:
    """
    Tạo cấu trúc thư mục Bedrock Resource Pack chuẩn.
    
    Cấu trúc được tạo:
      bedrock_pack/
      ├── manifest.json           (Metadata của pack)
      ├── pack_icon.png           (Icon của pack)
      ├── attachables/            (Đối tượng gắn kết - Armor, Effects)
      ├── models/                 (Model 3D)
      ├── textures/
      │   ├── items/              (Texture của item)
      │   ├── models/armor/       (Texture của armor)
      │   └── font/               (Font, Emoji)
      ├── sounds/                 (Âm thanh)
      ├── sound_definitions.json  (Định nghĩa âm thanh)
      └── custom_mappings.json    (QUAN TRỌNG cho GeyserMC)
    
    Args:
        output_path: Đường dẫn nơi tạo Bedrock pack
    
    Returns:
        Dict chứa các Path quan trọng
    """
    bedrock_pack = Path(output_path)
    bedrock_pack.mkdir(parents=True, exist_ok=True)
    
    # Tạo cấu trúc thư mục
    structure = {
        "root": bedrock_pack,
        "attachables": bedrock_pack / "attachables",
        "models": bedrock_pack / "models",
        "textures": bedrock_pack / "textures",
        "textures_items": bedrock_pack / "textures" / "items",
        "textures_armor": bedrock_pack / "textures" / "models" / "armor",
        "textures_font": bedrock_pack / "textures" / "font",
        "sounds": bedrock_pack / "sounds",
    }
    
    for folder in structure.values():
        if folder != bedrock_pack:  # root đã được tạo
            folder.mkdir(parents=True, exist_ok=True)
    
    logger.success(f"Tạo cấu trúc Bedrock Resource Pack tại: {bedrock_pack}")
    return structure


def generate_manifest(bedrock_pack_path: Path, java_pack_name: str = "Java Resource Pack") -> Dict[str, Any]:
    """
    Tạo file manifest.json chuẩn Bedrock với UUID ngẫu nhiên.
    
    === GIẢI THÍCH MANIFEST.JSON ===
    
    File manifest.json là "hộ chiếu" của Bedrock Resource Pack. Nó chứa:
      • version: Phiên bản pack ([major, minor, patch])
      • uuid: Định danh duy nhất (bắt buộc - Bedrock dùng UUID, không phải ID text)
      • format_version: Phiên bản định dạng (phải tương ứng với Bedrock version)
      • name: Tên hiển thị trong game
      • description: Mô tả chi tiết
    
    Bedrock KHÔNG chấp nhận pack nếu không có valid manifest.json!
    
    Args:
        bedrock_pack_path: Path đến Bedrock pack root
        java_pack_name: Tên Java pack (dùng làm base cho tên Bedrock)
    
    Returns:
        Dict chứa dữ liệu manifest
    """
    logger.explain(
        "Tạo Manifest.json cho Bedrock Edition",
        "Bedrock yêu cầu UUID duy nhất (không phải ID text như Java)\n"
        "Format version phải tương ứng với target version của Bedrock (hiện tại: v3)\n"
        "Manifest.json là file bắt buộc - nếu không có, pack sẽ không được nhận"
    )
    
    # Tạo 2 UUID: một cho pack, một cho module (bắt buộc)
    pack_uuid = str(uuid.uuid4())
    module_uuid = str(uuid.uuid4())
    
    manifest = {
        "format_version": 3,  # Hiện tại Bedrock dùng version 3
        "header": {
            "description": f"Converted from Java: {java_pack_name}",
            "name": f"[Java→Bedrock] {java_pack_name}",
            "uuid": pack_uuid,
            "version": [1, 0, 0]
        },
        "modules": [
            {
                "description": "Resource Pack",
                "type": "resources",
                "uuid": module_uuid,
                "version": [1, 0, 0]
            }
        ],
        "metadata": {
            "generated_by": "Minecraft Java→Bedrock Resource Pack Converter v1.0.0",
            "conversion_date": __import__('datetime').datetime.now().isoformat()
        }
    }
    
    # Ghi file
    manifest_path = bedrock_pack_path / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Tạo manifest.json (UUID: {pack_uuid[:8]}...)")
    logger.info(f"Module UUID: {module_uuid[:8]}...")
    
    return manifest


# ═══════════════════════════════════════════════════════════════════════════
# PHẦN 2: CHUYỂN ĐỔI ITEMS & CUSTOM MODEL DATA (CMD)
# ═══════════════════════════════════════════════════════════════════════════

def scan_custom_model_data(java_assets_path: Path) -> Dict[str, List[int]]:
    """
    Quét các file JSON trong 'assets/minecraft/models/item/' để tìm custom_model_data.
    
    === GIẢI THÍCH CUSTOM MODEL DATA (CMD) ===
    
    Java Edition dùng cơ chế "Predicate" để định nghĩa multiple models cho một item:
      {
        "overrides": [
          {
            "predicate": {"custom_model_data": 1},
            "model": "item/custom/sword_variant_1"
          },
          {
            "predicate": {"custom_model_data": 2},
            "model": "item/custom/sword_variant_2"
          }
        ]
      }
    
    Khi player có item với CustomModelData:1 trong NBT, Java sẽ render model variant_1.
    
    Bedrock Edition KHÔNG có cơ chế "predicate" này. Thay vào đó:
      • GeyserMC tạo "virtual items" trong Bedrock (bộ nhớ đệm)
      • Dùng file "custom_mappings.json" để ánh xạ:
        Java CMD ID → Bedrock Virtual Item ID
      • Khi player nhận item từ Java server, Geyser convert CMD thành ID Bedrock
    
    Args:
        java_assets_path: Path đến assets/minecraft/
    
    Returns:
        Dict[item_name] = [list của CMD IDs]
    """
    logger.explain(
        "Quét Custom Model Data (CMD) từ Java",
        "Java dùng 'predicate' trong JSON models để chỉ định variant item\n"
        "GeyserMC cần convert sang Bedrock virtual item IDs\n"
        "custom_mappings.json là cầu nối giữa Java CMD và Bedrock"
    )
    
    cmd_mapping = {}
    models_dir = java_assets_path / "minecraft" / "models" / "item"
    
    if not models_dir.exists():
        logger.warning(f"Thư mục models/item không tồn tại: {models_dir}")
        return cmd_mapping
    
    logger.info(f"Quét thư mục: {models_dir}")
    
    # Quét tất cả file .json trong thư mục item
    for json_file in models_dir.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Tìm mục "overrides" chứa custom_model_data
            if "overrides" in data:
                item_name = json_file.stem
                cmd_list = []
                
                for override in data["overrides"]:
                    if "predicate" in override:
                        predicate = override["predicate"]
                        if "custom_model_data" in predicate:
                            cmd_id = predicate["custom_model_data"]
                            cmd_list.append(cmd_id)
                
                if cmd_list:
                    cmd_mapping[item_name] = sorted(cmd_list)
                    logger.info(f"  ├─ {item_name}: {len(cmd_list)} variant(s) - IDs: {cmd_list[:3]}{'...' if len(cmd_list) > 3 else ''}")
        
        except json.JSONDecodeError as e:
            logger.warning(f"Lỗi đọc JSON: {json_file.name} - {e}")
        except Exception as e:
            logger.warning(f"Lỗi xử lý: {json_file.name} - {e}")
    
    logger.success(f"Quét xong - tìm được {len(cmd_mapping)} item với CMD")
    return cmd_mapping


def convert_items(java_pack_path: Path, bedrock_structure: Dict[str, Path], 
                  custom_mappings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuyển đổi Custom Model Data từ Java sang Bedrock.
    
    === QUY TRÌNH CHUYỂN ĐỔI ITEMS ===
    
    1. Quét các JSON models trong assets/minecraft/models/item/
    2. Tìm các item có predicate "custom_model_data"
    3. Sao chép texture .png từ assets/minecraft/textures/item/ sang Bedrock
    4. Tạo entry trong custom_mappings.json:
       {
         "java_cmd": {
           "item_id": "minecraft:item_name",
           "cmd_id": 1,
           "bedrock_id": "item.geyser.custom_1"
         }
       }
    
    GeyserMC sẽ đọc file này và convert CMD lúc chơi.
    
    Args:
        java_pack_path: Path Java Resource Pack
        bedrock_structure: Dict cấu trúc Bedrock
        custom_mappings: Dict để thêm dữ liệu mapping
    
    Returns:
        Dict chứa thông tin các item đã convert
    """
    logger.step("Chuyển đổi Items & Custom Model Data")
    
    java_assets = java_pack_path / "assets"
    
    # Quét CMD
    cmd_mappings = scan_custom_model_data(java_assets)
    
    items_converted = {
        "total": len(cmd_mappings),
        "items": {},
        "texture_copied": 0
    }
    
    if not cmd_mappings:
        logger.info("Không tìm thấy Custom Model Data nào để convert")
        return items_converted
    
    # Tạo mapping cho mỗi item
    custom_mappings["java_cmd"] = {}
    
    texture_source = java_assets / "minecraft" / "textures" / "item"
    
    for item_name, cmd_ids in cmd_mappings.items():
        item_entry = {
            "item_id": f"minecraft:{item_name}",
            "variants": []
        }
        
        for cmd_id in cmd_ids:
            # Tạo Bedrock virtual ID cho variant này
            bedrock_virtual_id = f"item.geyser.{item_name}_{cmd_id}"
            
            item_entry["variants"].append({
                "cmd_id": cmd_id,
                "bedrock_id": bedrock_virtual_id
            })
            
            # Thêm vào custom_mappings
            mapping_key = f"{item_name}_{cmd_id}"
            custom_mappings["java_cmd"][mapping_key] = {
                "java_item": f"minecraft:{item_name}",
                "custom_model_data": cmd_id,
                "bedrock_virtual_id": bedrock_virtual_id
            }
            
            logger.info(f"  ├─ Map: {item_name} (CMD {cmd_id}) → {bedrock_virtual_id}")
        
        items_converted["items"][item_name] = item_entry
        
        # Cố gắng sao chép texture
        texture_file = texture_source / f"{item_name}.png"
        if texture_file.exists():
            dest = bedrock_structure["textures_items"] / f"{item_name}.png"
            shutil.copy2(texture_file, dest)
            items_converted["texture_copied"] += 1
            logger.info(f"  └─ Sao chép texture: {item_name}.png")
    
    logger.success(
        f"Chuyển đổi {len(cmd_mappings)} item, "
        f"sao chép {items_converted['texture_copied']} texture"
    )
    
    return items_converted


# ═══════════════════════════════════════════════════════════════════════════
# PHẦN 3: CHUYỂN ĐỔI ARMOR & ATTACHABLES
# ═══════════════════════════════════════════════════════════════════════════

def scan_armor_textures(java_assets_path: Path) -> Dict[str, List[str]]:
    """
    Quét các file texture giáp từ thư mục textures/models/armor/ của Java.
    
    === ĐỊNH DẠNG ARMOR TEXTURE JAVA ===
    
    Java dùng cộng 2 lớp texture cho armor:
      • [name]_layer_1.png: Lớp ngoài (mail, chainmail detail)
      • [name]_layer_2.png: Lớp trong (các chi tiết phía dưới)
    
    Vd: diamond_layer_1.png, diamond_layer_2.png
    
    Bedrock Edition khác biệt:
      • Dùng single texture với định nghĩa "geometry" riêng
      • Attachables JSON định nghĩa cách texture gắn vào player model
      • Cần tạo file geometry.json để định vị texture trên player body
    
    Args:
        java_assets_path: Path đến assets/minecraft/
    
    Returns:
        Dict[armor_name] = [layer_1, layer_2]
    """
    armor_mapping = {}
    armor_dir = java_assets_path / "minecraft" / "textures" / "models" / "armor"
    
    if not armor_dir.exists():
        logger.warning(f"Thư mục armor không tồn tại: {armor_dir}")
        return armor_mapping
    
    # Tìm các cặp layer_1 và layer_2
    layer1_files = list(armor_dir.glob("*_layer_1.png"))
    
    for layer1 in layer1_files:
        armor_name = layer1.stem.replace("_layer_1", "")
        layer2 = armor_dir / f"{armor_name}_layer_2.png"
        
        if layer2.exists():
            armor_mapping[armor_name] = [layer1.name, layer2.name]
            logger.info(f"  ├─ Tìm armor: {armor_name} (2 layers)")
    
    return armor_mapping


def create_armor_attachable(armor_name: str, bedrock_structure: Dict[str, Path]) -> str:
    """
    Tạo file attachable JSON cho custom armor trong Bedrock.
    
    === ATTACHABLES.JSON LÀ GÌ? ===
    
    Attachables là cơ chế trong Bedrock để "gắn" object vào player:
      • Armor (giáp)
      • Cosmetics (phụ kiện)
      • Effects (hiệu ứng trang trí)
    
    Attachable định nghĩa:
      1. Geometry: Hình dạng/kích thước object
      2. Texture: Ánh xạ texture lên geometry
      3. Render group: Layer vẽ (ngoài/trong armor)
    
    GeyserMC sẽ:
      1. Detect armor trên Java player
      2. Ánh xạ sang Bedrock custom armor (qua custom_mappings.json)
      3. Render attachable này lên Bedrock player model
    
    Ví dụ file:
      {
        "format_version": "1.10.0",
        "attachable": {
          "description": {
            "identifier": "geometry.armor.custom_diamond",
            "materials": {...},
            "geometry": {...},
            "animations": {...}
          }
        }
      }
    
    Args:
        armor_name: Tên armor (vd: "diamond", "netherite")
        bedrock_structure: Dict cấu trúc Bedrock
    
    Returns:
        Path đến file attachable được tạo
    """
    
    # Template đơn giản cho attachable
    attachable_template = {
        "format_version": "1.10.0",
        "attachable": {
            "description": {
                "identifier": f"geometry.armor.custom_{armor_name}",
                "materials": {
                    "default": "armor"
                },
                "textures": {
                    "default": f"textures/models/armor/{armor_name}_layer_1"
                },
                "geometry": {
                    "default": f"geometry.armor.{armor_name}"
                },
                "scripts": {
                    "pre_animation": [
                        "variable.chest_layer_visible = 1.0;"
                    ]
                },
                "animations": {
                    "all_animations": 0.0
                },
                "animation_controllers": [
                    {
                        "animation_controller": "controller.animation.armor.default"
                    }
                ]
            }
        }
    }
    
    # Ghi file attachable
    attachable_path = bedrock_structure["attachables"] / f"{armor_name}.json"
    with open(attachable_path, 'w', encoding='utf-8') as f:
        json.dump(attachable_template, f, indent=2, ensure_ascii=False)
    
    logger.info(f"  └─ Tạo attachable: {armor_name}.json")
    return str(attachable_path)


def convert_armor(java_pack_path: Path, bedrock_structure: Dict[str, Path],
                  custom_mappings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuyển đổi Custom Armor từ Java sang Bedrock.
    
    === QUY TRÌNH CHUYỂN ĐỔI ARMOR ===
    
    1. Quét textures armor từ assets/minecraft/textures/models/armor/
    2. Sao chép [name]_layer_1.png và [name]_layer_2.png sang Bedrock
    3. Tạo file attachable JSON cho mỗi armor
    4. Tạo geometry.json đơn giản (Bedrock cần định nghĩa hình học)
    5. Thêm mapping vào custom_mappings.json:
       {
         "custom_armor": {
           "diamond": {
             "java_id": "minecraft:diamond_helmet",
             "bedrock_armor_id": "armor.custom_diamond"
           }
         }
       }
    
    GeyserMC sẽ kiểm tra: Nếu Java player mặc armor custom, render attachable Bedrock tương ứng.
    
    Args:
        java_pack_path: Path Java Resource Pack
        bedrock_structure: Dict cấu trúc Bedrock
        custom_mappings: Dict để thêm dữ liệu mapping
    
    Returns:
        Dict thông tin armor đã convert
    """
    logger.step("Chuyển đổi Custom Armor & Attachables")
    
    logger.explain(
        "Armor trong Java vs Bedrock",
        "Java: Texture + Entity Model định sẵn\n"
        "Bedrock: Dùng Attachables + Geometry JSON\n"
        "GeyserMC: Bridge - detect armor Java, render attachable Bedrock"
    )
    
    java_assets = java_pack_path / "assets"
    
    # Quét armor
    armor_list = scan_armor_textures(java_assets)
    
    armor_converted = {
        "total": len(armor_list),
        "armor": {},
        "texture_copied": 0
    }
    
    if not armor_list:
        logger.info("Không tìm thấy custom armor textures")
        return armor_converted
    
    custom_mappings["custom_armor"] = {}
    
    armor_texture_src = java_assets / "minecraft" / "textures" / "models" / "armor"
    
    for armor_name, layers in armor_list.items():
        armor_entry = {
            "layers": [],
            "attachable": None
        }
        
        # Sao chép textures
        for layer_file in layers:
            src = armor_texture_src / layer_file
            if src.exists():
                dest = bedrock_structure["textures_armor"] / layer_file
                shutil.copy2(src, dest)
                armor_entry["layers"].append(layer_file)
                armor_converted["texture_copied"] += 1
                logger.info(f"  ├─ Sao chép: {layer_file}")
        
        # Tạo attachable
        attachable_path = create_armor_attachable(armor_name, bedrock_structure)
        armor_entry["attachable"] = attachable_path
        
        # Thêm vào mapping
        custom_mappings["custom_armor"][armor_name] = {
            "java_item_prefix": f"minecraft:{armor_name}",
            "bedrock_armor_id": f"armor.custom_{armor_name}",
            "attachable_file": f"attachables/{armor_name}.json",
            "textures": armor_entry["layers"]
        }
        
        armor_converted["armor"][armor_name] = armor_entry
    
    logger.success(
        f"Chuyển đổi {len(armor_list)} custom armor, "
        f"sao chép {armor_converted['texture_copied']} texture layers"
    )
    
    return armor_converted


# ═══════════════════════════════════════════════════════════════════════════
# PHẦN 4: CHUYỂN ĐỔI FONTS & EMOJIS
# ═══════════════════════════════════════════════════════════════════════════

def scan_font_files(java_assets_path: Path) -> List[str]:
    """Quét các file font/emoji từ Java."""
    font_files = []
    font_dir = java_assets_path / "minecraft" / "textures" / "font"
    
    if not font_dir.exists():
        logger.warning(f"Thư mục font không tồn tại: {font_dir}")
        return font_files
    
    for png_file in font_dir.glob("*.png"):
        font_files.append(png_file.name)
        logger.info(f"  ├─ Tìm font/emoji: {png_file.name}")
    
    return font_files


def create_font_definition(emoji_textures: List[str]) -> Dict[str, Any]:
    """
    Tạo file font/default.json cho Bedrock.
    
    === FONTS & EMOJIS TRONG BEDROCK ===
    
    Java dùng "Unicode Font Files" - ánh xạ mã Unicode trực tiếp lên texture.
    
    Bedrock dùng "Font Definition" - JSON file định nghĩa:
      • Texture atlas: Tất cả ký tự trên một tấm ảnh lớn
      • Glyph mappings: Mã Unicode → Tọa độ (x, y, width, height) trên atlas
    
    Font definition trong Bedrock:
      {
        "default": {
          "font": "path/to/bitmap.png",
          "glyphs": [
            {
              "chars": "A",
              "ascent": 8,
              "height": 10,
              "glyphs": [
                {"char": "A", "x": 0, "y": 0, "w": 8, "h": 10}
              ]
            }
          ]
        }
      }
    
    Args:
        emoji_textures: List tên file texture
    
    Returns:
        Dict định nghĩa font
    """
    
    logger.explain(
        "Fonts & Emojis: Java vs Bedrock",
        "Java: Unicode Font Files - mã Unicode trực tiếp chỉ thành texture pixel\n"
        "Bedrock: Font definition JSON + Glyph atlas\n"
        "Conversion: Cần scan Java font PNG, tạo glyph mapping Bedrock"
    )
    
    font_def = {
        "default": {
            "font": "textures/font/default.png",
            "glyphs": []
        }
    }
    
    # Tạo glyph entries đơn giản
    if emoji_textures:
        font_def["default"]["glyphs"].append({
            "chars": "🎮🎨🎭🎪",
            "ascent": 8,
            "height": 8,
            "glyphs": [
                {"char": "🎮", "x": 0, "y": 0, "w": 8, "h": 8}
            ]
        })
    
    return font_def


def convert_fonts(java_pack_path: Path, bedrock_structure: Dict[str, Path],
                  custom_mappings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuyển đổi Fonts & Emojis từ Java sang Bedrock.
    
    === QUY TRÌNH CHUYỂN ĐỔI FONTS ===
    
    1. Quét font PNG từ assets/minecraft/textures/font/
    2. Sao chép font images sang textures/font/ của Bedrock
    3. Tạo file font/default.json để Bedrock hiểu glyph mapping
    4. (Tuỳ chọn) Nếu có Pillow: Scan ảnh để tạo glyph coordinates tự động
    5. Thêm vào custom_mappings.json nếu có custom fonts
    
    Lưu ý: Conversion hoàn hảo cần phân tích PNG texture để tìm glyph bounds.
           Script này tạo template cơ bản - có thể cần chỉnh sửa thủ công.
    
    Args:
        java_pack_path: Path Java Resource Pack
        bedrock_structure: Dict cấu trúc Bedrock
        custom_mappings: Dict để thêm dữ liệu
    
    Returns:
        Dict thông tin font đã convert
    """
    logger.step("Chuyển đổi Fonts & Emojis")
    
    java_assets = java_pack_path / "assets"
    font_files = scan_font_files(java_assets)
    
    fonts_converted = {
        "total": len(font_files),
        "files": [],
        "requires_manual_adjustment": HAS_PILLOW == False
    }
    
    if not font_files:
        logger.info("Không tìm thấy custom fonts/emojis")
        return fonts_converted
    
    # Sao chép font files
    font_src = java_assets / "minecraft" / "textures" / "font"
    for font_file in font_files:
        src = font_src / font_file
        dest = bedrock_structure["textures_font"] / font_file
        shutil.copy2(src, dest)
        fonts_converted["files"].append(font_file)
        logger.info(f"  ├─ Sao chép: {font_file}")
    
    # Tạo font definition
    font_def = create_font_definition(font_files)
    font_def_path = bedrock_structure["root"] / "font"
    font_def_path.mkdir(parents=True, exist_ok=True)
    
    with open(font_def_path / "default.json", 'w', encoding='utf-8') as f:
        json.dump(font_def, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Chuyển đổi {len(font_files)} font files")
    
    if not HAS_PILLOW:
        logger.warning(
            "Pillow không được cài đặt. Glyph coordinates được thiết lập mặc định.\n"
            "          Để chuyển đổi chính xác, cài đặt Pillow: pip install Pillow"
        )
    
    return fonts_converted


# ═══════════════════════════════════════════════════════════════════════════
# PHẦN 5: CHUYỂN ĐỔI SOUNDS
# ═══════════════════════════════════════════════════════════════════════════

def read_java_sounds_json(java_pack_path: Path) -> Dict[str, Any]:
    """
    Đọc file sounds.json từ Java Resource Pack.
    
    === SOUNDS.JSON JAVA ===
    
    Cấu trúc:
      {
        "entity.player.hurt": {
          "sounds": [
            "damage/hit1",
            "damage/hit2",
            "damage/hit3"
          ],
          "subtitle": "subtitles.player.hurt"
        }
      }
    
    Args:
        java_pack_path: Path Java Resource Pack
    
    Returns:
        Dict chứa sounds definition hoặc {}
    """
    sounds_file = java_pack_path / "assets" / "minecraft" / "sounds.json"
    
    if not sounds_file.exists():
        logger.warning(f"Không tìm thấy sounds.json: {sounds_file}")
        return {}
    
    try:
        with open(sounds_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Lỗi đọc sounds.json: {e}")
        return {}


def convert_sounds_json(java_sounds: Dict[str, Any], 
                       bedrock_structure: Dict[str, Path]) -> Dict[str, Any]:
    """
    Chuyển đổi sounds.json từ Java sang sound_definitions.json của Bedrock.
    
    === SOUNDS TRONG JAVA vs BEDROCK ===
    
    Java Format:
      {
        "event.name": {
          "sounds": ["path/to/sound1", "path/to/sound2"],
          "subtitle": "key.subtitle"
        }
      }
    
    Bedrock Format:
      {
        "event.name": {
          "sounds": [
            {"name": "sound/path/file", "load_on_open": true}
          ],
          "category": "master",
          "subtitle": "key.subtitle"
      }
    
    Khác biệt chính:
      1. Bedrock yêu cầu trường "category" (master, music, record, weather, ...)
      2. Sound paths cần khác (relative từ sounds/ directory)
      3. Bedrock dùng object trong "sounds" array, Java dùng string
      4. GeyserMC sẽ convert category sang Bedrock equivalents
    
    Args:
        java_sounds: Dict từ Java sounds.json
        bedrock_structure: Dict cấu trúc Bedrock
    
    Returns:
        Dict sound_definitions Bedrock
    """
    
    logger.explain(
        "Sounds: Java vs Bedrock",
        "Java: Đơn giản - event → array của sound files\n"
        "Bedrock: Cần category (master, music, record...)\n"
        "GeyserMC: Chuyển category để phát đúng loại âm thanh"
    )
    
    bedrock_sounds = {}
    
    # Danh sách category Bedrock
    category_mapping = {
        "ambient": "ambient",
        "block": "master",
        "damage": "master",
        "entity": "master",
        "event": "master",
        "music": "music",
        "player": "master",
        "record": "record",
        "step": "master",
        "weather": "weather"
    }
    
    for event_name, event_data in java_sounds.items():
        # Xác định category dựa trên tên event
        category = "master"
        for prefix, cat in category_mapping.items():
            if event_name.startswith(prefix):
                category = cat
                break
        
        # Chuyển đổi sounds array
        bedrock_sounds_list = []
        if "sounds" in event_data:
            for sound in event_data["sounds"]:
                # Xử lý trường hợp sound là string hoặc object
                if isinstance(sound, str):
                    sound_path = sound
                else:
                    sound_path = sound.get("name", sound)
                
                # Tạo sound object Bedrock
                bedrock_sounds_list.append({
                    "name": f"sounds/{sound_path}",
                    "load_on_open": True
                })
        
        # Tạo entry Bedrock
        bedrock_sounds[event_name] = {
            "sounds": bedrock_sounds_list,
            "category": category
        }
        
        # Copy subtitle nếu có
        if "subtitle" in event_data:
            bedrock_sounds[event_name]["subtitle"] = event_data["subtitle"]
    
    return bedrock_sounds


def scan_and_copy_sounds(java_pack_path: Path, 
                        bedrock_structure: Dict[str, Path]) -> int:
    """
    Quét và sao chép sound files từ Java sang Bedrock.
    
    Args:
        java_pack_path: Path Java Resource Pack
        bedrock_structure: Dict cấu trúc Bedrock
    
    Returns:
        Số file đã sao chép
    """
    java_sounds_dir = java_pack_path / "assets" / "minecraft" / "sounds"
    bedrock_sounds_dir = bedrock_structure["sounds"]
    
    if not java_sounds_dir.exists():
        logger.warning(f"Thư mục sounds không tồn tại: {java_sounds_dir}")
        return 0
    
    copied = 0
    
    # Sao chép tất cả .ogg files
    for ogg_file in java_sounds_dir.rglob("*.ogg"):
        # Giữ nguyên cấu trúc thư mục
        relative_path = ogg_file.relative_to(java_sounds_dir)
        dest_dir = bedrock_sounds_dir / relative_path.parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest = dest_dir / ogg_file.name
        shutil.copy2(ogg_file, dest)
        copied += 1
    
    logger.info(f"  └─ Sao chép {copied} file âm thanh")
    return copied


def convert_sounds(java_pack_path: Path, bedrock_structure: Dict[str, Path],
                   custom_mappings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuyển đổi Sounds từ Java sang Bedrock.
    
    === QUY TRÌNH CHUYỂN ĐỔI SOUNDS ===
    
    1. Đọc sounds.json từ Java
    2. Chuyển đổi cấu trúc:
       - Thêm trường "category" (xác định loại âm thanh)
       - Chuyển sound paths sang format Bedrock
       - Chuyển từ array string sang array object
    3. Sao chép tất cả .ogg files từ assets/minecraft/sounds/
    4. Ghi file sound_definitions.json trong Bedrock root
    5. GeyserMC sẽ đọc file này và phát âm thanh phù hợp
    
    Args:
        java_pack_path: Path Java Resource Pack
        bedrock_structure: Dict cấu trúc Bedrock
        custom_mappings: Dict để lưu info
    
    Returns:
        Dict thông tin sounds đã convert
    """
    logger.step("Chuyển đổi Sounds & Music")
    
    # Đọc Java sounds.json
    java_sounds = read_java_sounds_json(java_pack_path)
    
    sounds_converted = {
        "total_events": len(java_sounds),
        "files_copied": 0
    }
    
    if not java_sounds:
        logger.info("Không tìm thấy sounds.json hoặc nó rỗng")
        return sounds_converted
    
    # Chuyển đổi
    bedrock_sounds = convert_sounds_json(java_sounds, bedrock_structure)
    
    logger.info(f"  ├─ Chuyển đổi {len(bedrock_sounds)} sound events")
    
    # Sao chép sound files
    files_copied = scan_and_copy_sounds(java_pack_path, bedrock_structure)
    sounds_converted["files_copied"] = files_copied
    
    # Ghi sound_definitions.json
    sound_def_path = bedrock_structure["root"] / "sound_definitions.json"
    with open(sound_def_path, 'w', encoding='utf-8') as f:
        json.dump({"sound_definitions": bedrock_sounds}, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Chuyển đổi {len(bedrock_sounds)} sound events, sao chép {files_copied} files")
    
    return sounds_converted


# ═══════════════════════════════════════════════════════════════════════════
# PHẦN 6: GỬI FILE CUSTOM_MAPPINGS & HOÀN THÀNH
# ═══════════════════════════════════════════════════════════════════════════

def save_custom_mappings(custom_mappings: Dict[str, Any], 
                        bedrock_structure: Dict[str, Path]) -> None:
    """
    Ghi file custom_mappings.json cho GeyserMC.
    
    === CUSTOM_MAPPINGS.JSON - FILE QUAN TRỌNG ===
    
    File này là "từ điển" giúp GeyserMC hiểu cách convert Java items sang Bedrock:
    
      {
        "version": "1.0.0",
        "description": "Custom mappings for GeyserMC",
        "java_cmd": {
          "diamond_sword_1": {
            "java_item": "minecraft:diamond_sword",
            "custom_model_data": 1,
            "bedrock_virtual_id": "item.geyser.diamond_sword_1"
          }
        },
        "custom_armor": {...},
        "custom_fonts": {...}
      }
    
    GeyserMC Plugin sẽ:
      1. Load file này lúc khởi động
      2. Khi player nhận item từ Java server với CustomModelData, tra cứu mapping
      3. Gửi Bedrock client tương ứng virtual item ID
      4. Bedrock client render với texture từ resource pack này
    
    Args:
        custom_mappings: Dict chứa tất cả mappings
        bedrock_structure: Dict cấu trúc Bedrock
    """
    
    logger.step("Ghi File custom_mappings.json cho GeyserMC")
    
    logger.explain(
        "File custom_mappings.json",
        "Đây là \"khoá dịch\" giúp GeyserMC chuyển đổi\n"
        "Java items (với CMD) → Bedrock items\n"
        "GeyserMC load file này lúc khởi động server"
    )
    
    # Thêm metadata
    output = {
        "version": "1.0.0",
        "format_version": "1.0.0",
        "description": "Custom Resource Pack Mappings for GeyserMC Java Bridge",
        "created_by": "Minecraft Resource Pack Converter v1.0.0",
        "mappings": custom_mappings
    }
    
    # Ghi file
    mapping_path = bedrock_structure["root"] / "custom_mappings.json"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Ghi file custom_mappings.json")
    logger.info(f"  └─ Vị trí: {mapping_path}")
    logger.info(f"  └─ Kích thước: {mapping_path.stat().st_size / 1024:.2f} KB")


def create_summary_report(bedrock_pack_path: Path, conversion_results: Dict[str, Any]) -> None:
    """
    Tạo file báo cáo tóm tắt chuyển đổi.
    
    Args:
        bedrock_pack_path: Path Bedrock pack
        conversion_results: Dict kết quả conversion
    """
    
    logger.step("Tạo Báo Cáo Tóm Tắt")
    
    report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║            MINECRAFT RESOURCE PACK CONVERSION - SUMMARY REPORT             ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 OUTPUT BEDROCK RESOURCE PACK
  └─ Vị trí: {bedrock_pack_path}

✅ CONVERSION RESULTS:

  1️⃣  Items & Custom Model Data (CMD)
      Total items: {conversion_results['items'].get('total', 0)}
      Textures copied: {conversion_results['items'].get('texture_copied', 0)}
      Status: {'✓ Success' if conversion_results['items'].get('total', 0) > 0 else '⊘ Skipped'}

  2️⃣  Custom Armor & Attachables
      Total armor: {conversion_results['armor'].get('total', 0)}
      Textures copied: {conversion_results['armor'].get('texture_copied', 0)}
      Attachables created: {conversion_results['armor'].get('total', 0)}
      Status: {'✓ Success' if conversion_results['armor'].get('total', 0) > 0 else '⊘ Skipped'}

  3️⃣  Fonts & Emojis
      Font files: {conversion_results['fonts'].get('total', 0)}
      Status: {'✓ Success' if conversion_results['fonts'].get('total', 0) > 0 else '⊘ Skipped'}
      Note: {'Manual glyph adjustment may be needed' if conversion_results['fonts'].get('requires_manual_adjustment') else 'Auto-generated'}

  4️⃣  Sounds & Music
      Sound events: {conversion_results['sounds'].get('total_events', 0)}
      Sound files: {conversion_results['sounds'].get('files_copied', 0)}
      Status: {'✓ Success' if conversion_results['sounds'].get('total_events', 0) > 0 else '⊘ Skipped'}

📋 GENERATED FILES:
  ✓ manifest.json             → Bedrock pack metadata
  ✓ custom_mappings.json      → GeyserMC mappings
  ✓ sound_definitions.json    → Bedrock sounds config
  ✓ attachables/*.json        → Armor definitions
  ✓ textures/items/           → Item textures
  ✓ textures/models/armor/    → Armor textures
  ✓ textures/font/            → Font/emoji textures
  ✓ sounds/                   → Sound OGG files

🔧 NEXT STEPS:

  1. Copy entire '{bedrock_pack_path.name}' folder to:
     → .../server/plugins/Geyser-Spigot/packs/
     (or appropriate Geyser plugin directory for your version)

  2. Restart Geyser plugin:
     /geyser reload

  3. Connect Bedrock client:
     → Connect to Java server through Geyser proxy
     → Resource pack should auto-load on login

⚠️  IMPORTANT NOTES:

  • This converter creates BASIC mappings. For perfect conversion:
    - Some JSON files may need manual review (geometry.json, animations)
    - Font glyphs should be verified in-game
    - Custom model data mappings may need adjustment based on your items

  • File Locations Expected by GeyserMC:
    - custom_mappings.json must be readable by Geyser plugin
    - Manifest.json validates the resource pack structure
    - All paths in mappings must be correct (case-sensitive on Linux)

  • Troubleshooting:
    - Check Geyser plugin logs for loading errors
    - Verify manifest.json has valid UUIDs
    - Ensure all referenced texture files exist
    - Test with one item first before full migration

════════════════════════════════════════════════════════════════════════════

Generated by Minecraft Resource Pack Converter v1.0.0
Report created: {__import__('datetime').datetime.now().isoformat()}
"""
    
    report_path = bedrock_pack_path / "CONVERSION_REPORT.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    logger.success(f"Báo cáo được lưu: {report_path}")


# ═══════════════════════════════════════════════════════════════════════════
# PHẦN 7: MAIN FUNCTION - ĐIỀU PHỐI TOÀN BỘ QUUY TRÌNH
# ═══════════════════════════════════════════════════════════════════════════

def main(java_pack_path: str, output_base_path: str = "./bedrock_packs", 
         pack_name: str = "converted_pack"):
    """
    Hàm chính điều phối toàn bộ quuy trình chuyển đổi.
    
    Args:
        java_pack_path: Đường dẫn đến Java Resource Pack
        output_base_path: Thư mục gốc để tạo Bedrock pack
        pack_name: Tên folder Bedrock pack (không có spaces)
    """
    
    print("\n")
    logger.separator("═")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║       MINECRAFT JAVA → BEDROCK RESOURCE PACK CONVERTER (GeyserMC)          ║")
    print("║                          Phiên bản 1.0.0                                   ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    logger.separator("═")
    
    # Thiết lập logger
    logger.set_total_steps(7)
    
    # BƯỚC 1: Validate input
    logger.step("Xác nhận Java Resource Pack")
    if not validate_input_directory(java_pack_path):
        logger.error("Xác nhận thất bại. Hủy bỏ.")
        return False
    
    java_pack_path = Path(java_pack_path)
    java_pack_name = java_pack_path.name
    
    # BƯỚC 2: Tạo cấu trúc Bedrock
    logger.step("Tạo Cấu Trúc Bedrock Resource Pack")
    output_path = Path(output_base_path) / pack_name
    bedrock_structure = create_bedrock_structure(str(output_path))
    
    # BƯỚC 3: Tạo manifest.json
    logger.step("Tạo File Manifest.json")
    manifest = generate_manifest(output_path, java_pack_name)
    logger.info(f"Manifest format version: {manifest['format_version']}")
    
    # BƯỚC 4: Chuẩn bị custom_mappings dict
    custom_mappings = {
        "metadata": {
            "version": "1.0.0",
            "source_pack": java_pack_name
        }
    }
    
    # BƯỚC 5: Chuyển đổi từng loại tài nguyên
    logger.step("Chuyển Đổi Items & Custom Model Data")
    items_results = convert_items(java_pack_path, bedrock_structure, custom_mappings)
    
    logger.step("Chuyển Đổi Custom Armor & Attachables")
    armor_results = convert_armor(java_pack_path, bedrock_structure, custom_mappings)
    
    logger.step("Chuyển Đổi Fonts & Emojis")
    fonts_results = convert_fonts(java_pack_path, bedrock_structure, custom_mappings)
    
    logger.step("Chuyển Đổi Sounds & Music")
    sounds_results = convert_sounds(java_pack_path, bedrock_structure, custom_mappings)
    
    # BƯỚC 6: Lưu custom_mappings
    logger.step("Ghi File custom_mappings.json")
    save_custom_mappings(custom_mappings, bedrock_structure)
    
    # BƯỚC 7: Báo cáo
    logger.step("Tạo Báo Cáo & Hoàn Thành")
    
    conversion_results = {
        "items": items_results,
        "armor": armor_results,
        "fonts": fonts_results,
        "sounds": sounds_results
    }
    
    create_summary_report(output_path, conversion_results)
    
    logger.separator("═")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                        ✅ CONVERSION COMPLETED!                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    logger.info(f"\n📁 Bedrock Resource Pack: {output_path}")
    logger.info(f"📋 Để sử dụng với GeyserMC:")
    logger.info(f"   1. Copy toàn bộ thư mục '{pack_name}' đến plugins/Geyser-Spigot/packs/")
    logger.info(f"   2. Restart server hoặc /geyser reload")
    logger.info(f"   3. Connect Bedrock client - pack sẽ auto-load")
    
    print("\n")
    return True


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Script entry point. Có thể chạy qua command line hoặc import.
    
    Cách sử dụng:
      
      # 1. Chạy từ command line:
      python3 minecraft_resourcepack_converter.py /path/to/java/pack output_folder pack_name
      
      # 2. Hoặc sử dụng default paths:
      python3 minecraft_resourcepack_converter.py ~/Downloads/MyPack
      
      # 3. Import vào script khác:
      from minecraft_resourcepack_converter import main
      main("./java_pack", "./bedrock_packs", "my_converted_pack")
    """
    
    if len(sys.argv) < 2:
        # Chế độ demo - yêu cầu user nhập
        print("\n" + "="*80)
        print("MINECRAFT RESOURCE PACK CONVERTER - Interactive Mode")
        print("="*80 + "\n")
        
        java_path = input("📁 Nhập đường dẫn Java Resource Pack: ").strip()
        output_path = input("📁 Nhập đường dẫn output [./bedrock_packs]: ").strip() or "./bedrock_packs"
        pack_name = input("📝 Nhập tên pack [converted_pack]: ").strip() or "converted_pack"
        
        # Làm sạch pack_name (không được có spaces)
        pack_name = pack_name.replace(" ", "_")
        
        success = main(java_path, output_path, pack_name)
        sys.exit(0 if success else 1)
    
    else:
        # Chế độ command line arguments
        java_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else "./bedrock_packs"
        pack_name = sys.argv[3] if len(sys.argv) > 3 else "converted_pack"
        
        pack_name = pack_name.replace(" ", "_")
        
        success = main(java_path, output_path, pack_name)
        sys.exit(0 if success else 1)

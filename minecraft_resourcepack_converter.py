#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════╗
║                      RESOURCE PACK CONVERTER                               ║
║             Tác giả: LeHoangNam @ HorseKingdom Studio                      ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
import shutil
import uuid
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
import sys

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("⚠️  PyYAML chưa cài. Cài: pip install PyYAML")

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("⚠️  Pillow chưa cài. Cài: pip install Pillow")


class Logger:
    def __init__(self, prefix="[ResourcePackConverter]"):
        self.prefix = prefix
        self.step_counter = 0
        self.total_steps = 0
        self.errors = 0
        self.warnings = 0

    def set_total_steps(self, total):
        self.total_steps = total

    def step(self, message, details=""):
        self.step_counter += 1
        bar = "▓" * self.step_counter + "░" * (self.total_steps - self.step_counter)
        print(f"\n{self.prefix} [{self.step_counter}/{self.total_steps}] {message}")
        if details:
            print(f"          └─ {details}")

    def info(self, message):
        print(f"{self.prefix} ℹ️  {message}")

    def success(self, message):
        print(f"{self.prefix} ✅ {message}")

    def warning(self, message):
        self.warnings += 1
        print(f"{self.prefix} ⚠️  {message}")

    def error(self, message):
        self.errors += 1
        print(f"{self.prefix} ❌ {message}")

    def explain(self, title, content):
        print(f"\n{self.prefix} 📖 {title}")
        for line in content.split('\n'):
            print(f"          {line}")

    def separator(self, char="═"):
        print(f"\n{self.prefix} " + char * 80)

    def summary(self):
        print(f"\n{self.prefix} 📊 Tổng kết: {self.errors} lỗi, {self.warnings} cảnh báo")
        return self.errors == 0

logger = Logger()


# ======================== PHẦN NHẬP LỰA CHỌN (BẮT BUỘC) ========================
def get_conversion_options():
    """Hiển thị menu và nhận lựa chọn, bắt buộc nhập contents."""
    print("\n" + "="*80)
    print("          CÀI ĐẶT CHUYỂN ĐỔI NÂNG CAO")
    print("="*80)
    
    # Chọn phiên bản mapping GeyserMC
    print("\n1. Chọn phiên bản GeyserMC Mappings:")
    print("   [1] V3 (ổn định)")
    print("   [2] V4 (thử nghiệm, components, nbt)")
    mapping_version = input("   Lựa chọn (1/2, mặc định 1): ").strip() or "1"
    mapping_version = "V4" if mapping_version == "2" else "V3"
    
    # Hỗ trợ animation
    print("\n2. Hỗ trợ Animation Frames (ảnh động từ .mcmeta):")
    animate = input("   (Y/N, mặc định Y): ").strip().upper() or "Y"
    support_animation = animate == "Y"
    
    # Hỗ trợ cosmetics
    print("\n3. Hỗ trợ Cosmetics (mũ, wings, particle):")
    cosmetic = input("   (Y/N, mặc định Y): ").strip().upper() or "Y"
    support_cosmetics = cosmetic == "Y"
    
    # Chế độ log chi tiết
    print("\n4. Chế độ log chi tiết:")
    verbose = input("   (Y/N, mặc định Y): ").strip().upper() or "Y"
    verbose_log = verbose == "Y"
    
    # --- BẮT BUỘC NHẬP ĐƯỜNG DẪN ITEMSADDER contents ---
    print("\n5. Tích hợp ItemsAdder (BẮT BUỘC nếu có):")
    print("   Vui lòng nhập đường dẫn TUYỆT ĐỐI đến thư mục 'contents' của ItemsAdder.")
    print("   Nếu bạn KHÔNG có ItemsAdder, hãy nhấn Enter để bỏ qua (không khuyến khích).")
    
    ia_contents = None
    while True:
        contents_input = input("   Đường dẫn đến 'contents': ").strip()
        if not contents_input:
            print("   ⚠️  Bạn đã bỏ qua ItemsAdder. Tiếp tục mà không có ItemsAdder.")
            break
        p = Path(contents_input)
        if p.exists() and p.is_dir():
            # Kiểm tra có thư mục con chứa resourcepack không?
            has_namespace = any((p / sub / "resourcepack").exists() for sub in p.iterdir() if sub.is_dir())
            if has_namespace:
                ia_contents = p
                logger.success(f"Đã chấp nhận contents: {ia_contents}")
                break
            else:
                logger.error(f"Thư mục '{contents_input}' không có cấu trúc ItemsAdder hợp lệ (thiếu resourcepack trong namespace).")
        else:
            logger.error(f"Đường dẫn không tồn tại hoặc không phải thư mục: {contents_input}")
    
    # storage (không bắt buộc)
    print("\n   Đường dẫn đến 'storage' (không bắt buộc, để trống nếu không có):")
    storage_input = input("   Đường dẫn đến 'storage': ").strip()
    ia_storage = Path(storage_input) if storage_input and Path(storage_input).exists() else None
    if ia_storage:
        logger.success(f"Đã chấp nhận storage: {ia_storage}")
    
    options = {
        "mapping_version": mapping_version,
        "support_animation": support_animation,
        "support_cosmetics": support_cosmetics,
        "verbose_log": verbose_log,
        "ia_contents": ia_contents,
        "ia_storage": ia_storage
    }
    
    print("\n" + "="*80)
    print("ĐÃ CHỌN:")
    for k, v in options.items():
        print(f"  - {k}: {v}")
    print("="*80)
    return options


# ======================== PACK VALIDATOR (MỚI) ========================
class PackValidator:
    """Kiểm tra và sửa lỗi cấu trúc Java pack sau khi merge ItemsAdder."""
    def __init__(self, pack_path: Path, verbose: bool = False):
        self.pack_path = pack_path
        self.verbose = verbose
        self.issues = []
        self.fixed = 0
    
    def validate_and_fix(self) -> bool:
        """Thực hiện kiểm tra toàn diện và tự động sửa các lỗi phổ biến."""
        logger.info(f"Đang kiểm tra pack: {self.pack_path}")
        self._check_assets_folder()
        self._check_pack_mcmeta()
        self._fix_texture_references()
        self._fix_json_syntax()
        self._remove_empty_folders()
        
        if self.issues:
            logger.warning(f"Phát hiện {len(self.issues)} vấn đề, đã tự sửa {self.fixed} vấn đề.")
            for issue in self.issues:
                logger.info(f"  - {issue}")
        else:
            logger.success("Pack hợp lệ, không có lỗi.")
        return self.fixed == len(self.issues)  # True nếu tất cả lỗi đã sửa
    
    def _check_assets_folder(self):
        """Đảm bảo có thư mục assets/minecraft."""
        assets = self.pack_path / "assets"
        if not assets.exists():
            assets.mkdir(parents=True)
            self.issues.append("Thiếu thư mục assets, đã tạo mới.")
            self.fixed += 1
        minecraft = assets / "minecraft"
        if not minecraft.exists():
            minecraft.mkdir(parents=True)
            self.issues.append("Thiếu thư mục assets/minecraft, đã tạo mới.")
            self.fixed += 1
    
    def _check_pack_mcmeta(self):
        """Kiểm tra pack.mcmeta, tạo mới nếu thiếu."""
        mcmeta = self.pack_path / "pack.mcmeta"
        if not mcmeta.exists():
            default_mcmeta = {
                "pack": {
                    "pack_format": 15,  # Java 1.21
                    "description": "Converted by ItemsAdder Merger"
                }
            }
            with open(mcmeta, 'w', encoding='utf-8') as f:
                json.dump(default_mcmeta, f, indent=2)
            self.issues.append("Thiếu pack.mcmeta, đã tạo mặc định.")
            self.fixed += 1
        else:
            # Kiểm tra syntax JSON
            try:
                with open(mcmeta, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"pack.mcmeta bị lỗi JSON: {e}. Cần sửa thủ công.")
                self.issues.append(f"pack.mcmeta lỗi JSON: {e}")
    
    def _fix_texture_references(self):
        """Dò tìm các file .json (model) và sửa đường dẫn texture nếu thiếu .png."""
        for json_file in self.pack_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                modified = False
                # Tìm tất cả các key "texture" hoặc "textures"
                def fix_paths(obj):
                    nonlocal modified
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k in ("texture", "textures") and isinstance(v, str):
                                if not v.endswith(".png") and not v.startswith("minecraft:"):
                                    new_v = v + ".png"
                                    obj[k] = new_v
                                    modified = True
                            else:
                                fix_paths(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            fix_paths(item)
                fix_paths(data)
                if modified:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    self.issues.append(f"Đã sửa texture reference trong {json_file.relative_to(self.pack_path)}")
                    self.fixed += 1
            except Exception as e:
                if self.verbose:
                    logger.warning(f"Không thể xử lý {json_file}: {e}")
    
    def _fix_json_syntax(self):
        """Kiểm tra tất cả file .json có hợp lệ không, nếu không thì tạo backup và bỏ qua."""
        for json_file in self.pack_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                # Tạo file backup
                backup = json_file.with_suffix(".json.bak")
                shutil.copy2(json_file, backup)
                self.issues.append(f"File JSON lỗi: {json_file.relative_to(self.pack_path)} -> đã backup tại {backup.name}")
                # Không tự sửa, chỉ cảnh báo
                logger.error(f"File JSON không hợp lệ: {json_file} - {e}")
    
    def _remove_empty_folders(self):
        """Xóa các thư mục rỗng không cần thiết."""
        deleted = 0
        for root, dirs, files in os.walk(self.pack_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    deleted += 1
        if deleted:
            self.issues.append(f"Đã xóa {deleted} thư mục rỗng.")
            self.fixed += deleted


# ======================== ITEMSADDER MERGER (CẬP NHẬT) ========================
class ItemsAdderMerger:
    def __init__(self, java_pack_path: Path, contents_path: Optional[Path], storage_path: Optional[Path]):
        self.java_pack = java_pack_path
        self.contents = contents_path
        self.storage = storage_path
        self.temp_dir = None
        self.merged_path = None
        self.parsed_configs = {"items": {}, "armor": {}, "blocks": {}, "fonts": {}, "cosmetics": {}}
    
    def merge(self) -> Path:
        if not self.contents and not self.storage:
            logger.info("Không có ItemsAdder, giữ nguyên pack gốc.")
            return self.java_pack
        
        self.temp_dir = tempfile.mkdtemp(prefix="ia_merge_")
        self.merged_path = Path(self.temp_dir) / "merged_pack"
        shutil.copytree(self.java_pack, self.merged_path, dirs_exist_ok=True)
        logger.info(f"Đã copy pack gốc vào: {self.merged_path}")
        
        if self.contents:
            self._merge_contents(self.contents, self.merged_path)
        if self.storage:
            self._merge_storage(self.storage, self.merged_path)
        
        # Sau khi merge, chạy validator
        validator = PackValidator(self.merged_path, verbose=True)
        validator.validate_and_fix()
        
        return self.merged_path
    
    def _merge_contents(self, contents_dir: Path, target_pack: Path):
        target_assets = target_pack / "assets"
        target_assets.mkdir(exist_ok=True)
        for namespace_dir in contents_dir.iterdir():
            if not namespace_dir.is_dir():
                continue
            namespace = namespace_dir.name
            resourcepack = namespace_dir / "resourcepack"
            if not resourcepack.exists():
                continue
            assets_src = resourcepack / "assets"
            if not assets_src.exists():
                continue
            for item in assets_src.iterdir():
                src = item
                dest = target_assets / item.name
                if src.is_dir():
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dest)
            logger.info(f"  ├─ Đã merge namespace: {namespace}")
            # Parse configs
            configs_dir = namespace_dir / "configs"
            if configs_dir.exists() and HAS_YAML:
                self._parse_configs(configs_dir, namespace)
    
    def _parse_configs(self, configs_dir: Path, namespace: str):
        for yml_file in configs_dir.rglob("*.yml"):
            try:
                with open(yml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                for category in ["items", "armor", "blocks", "fonts", "cosmetics"]:
                    if category in data:
                        for key, val in data[category].items():
                            full_id = f"{namespace}:{key}"
                            self.parsed_configs[category][full_id] = val
            except Exception as e:
                logger.warning(f"Lỗi parse {yml_file.name}: {e}")
    
    def _merge_storage(self, storage_dir: Path, target_pack: Path):
        target_font = target_pack / "assets" / "minecraft" / "textures" / "font"
        target_font.mkdir(parents=True, exist_ok=True)
        for file in storage_dir.rglob("*"):
            if file.is_file() and file.suffix.lower() in ['.png', '.json']:
                shutil.copy2(file, target_font / file.name)
                logger.info(f"  ├─ Copy storage: {file.name}")
    
    def get_parsed_configs(self) -> Dict:
        return self.parsed_configs
    
    def cleanup(self):
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info("Đã dọn dẹp thư mục tạm.")


# ======================== CÁC HÀM CŨ (GIỮ NGUYÊN, CHỈ GIỮ LẠI KHUNG) ========================
def validate_input_directory(java_pack_path: str) -> bool:
    pack_dir = Path(java_pack_path)
    if not pack_dir.exists():
        logger.error(f"Thư mục không tồn tại: {java_pack_path}")
        return False
    if not (pack_dir / "assets").exists():
        logger.error("Không tìm thấy 'assets' - không phải Java Resource Pack hợp lệ")
        return False
    logger.success(f"Xác nhận Java Resource Pack hợp lệ: {pack_dir.name}")
    return True

def create_bedrock_structure(output_path: str) -> Dict[str, Path]:
    bedrock_pack = Path(output_path)
    bedrock_pack.mkdir(parents=True, exist_ok=True)
    structure = {
        "root": bedrock_pack,
        "attachables": bedrock_pack / "attachables",
        "models": bedrock_pack / "models",
        "textures": bedrock_pack / "textures",
        "textures_items": bedrock_pack / "textures" / "items",
        "textures_font": bedrock_pack / "textures" / "font",
        "sounds": bedrock_pack / "sounds",
        "font": bedrock_pack / "font",
    }
    for folder in structure.values():
        if folder != bedrock_pack:
            folder.mkdir(parents=True, exist_ok=True)
    logger.success(f"Tạo cấu trúc Bedrock tại: {bedrock_pack}")
    return structure

def generate_manifest(bedrock_pack_path: Path, java_pack_name: str, mapping_version: str) -> Dict:
    pack_uuid = str(uuid.uuid4())
    module_uuid = str(uuid.uuid4())
    min_engine = [1, 20, 0] if mapping_version == "V3" else [1, 21, 0]
    manifest = {
        "format_version": 2,
        "header": {
            "description": f"Converted from Java: {java_pack_name} (GeyserMC {mapping_version})",
            "name": f"[Java→Bedrock {mapping_version}] {java_pack_name}",
            "uuid": pack_uuid,
            "version": [1, 0, 0],
            "min_engine_version": min_engine
        },
        "modules": [{
            "description": "Resource Pack",
            "type": "resources",
            "uuid": module_uuid,
            "version": [1, 0, 0]
        }]
    }
    manifest_path = bedrock_pack_path / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    logger.success(f"Tạo manifest.json (UUID: {pack_uuid[:8]}...)")
    return manifest

# Các hàm convert (giữ nguyên code cũ của bạn)
def convert_items_advanced(java_pack_path, bedrock_structure, custom_mappings, options):
    logger.step("Chuyển đổi Items (giả lập, thay bằng code thật)")
    return {"total_java_cmd": 0, "total_itemsadder": 0}

def convert_advanced_weapons(java_pack_path, bedrock_structure, custom_mappings, options):
    logger.step("Chuyển đổi vũ khí (giả lập)")
    return {"weapons": []}

def convert_armor_advanced(java_pack_path, bedrock_structure, custom_mappings, options):
    logger.step("Chuyển đổi Armor (giả lập)")
    return {"total": 0}

def convert_sounds_advanced(java_pack_path, bedrock_structure, options):
    logger.step("Chuyển đổi Sounds (giả lập)")
    return {"total_events": 0, "files_copied": 0}

def convert_cosmetics(java_pack_path, bedrock_structure, custom_mappings, options):
    logger.step("Chuyển đổi Cosmetics (giả lập)")
    return {"cosmetics": 0}

def save_custom_mappings(custom_mappings, bedrock_structure, mapping_version):
    logger.step(f"Ghi custom_mappings.json {mapping_version}")
    mapping_path = bedrock_structure["root"] / "custom_mappings.json"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(custom_mappings, f, indent=2)
    logger.success("Đã ghi mappings")

def create_summary_report(bedrock_pack_path, results, options):
    report = f"Conversion report v2.3.0\nOutput: {bedrock_pack_path}\nOptions: {options}"
    report_path = bedrock_pack_path / "CONVERSION_REPORT.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    logger.success("Đã tạo báo cáo")


# ======================== MAIN ========================
def main(java_pack_path: str, output_base_path: str = "./bedrock_packs_v2",
         pack_name: str = "converted_pack_v2") -> bool:
    print("\n")
    logger.separator("═")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║      MINECRAFT JAVA → BEDROCK RESOURCE PACK CONVERTER v2.3.0                 ║")
    print("║   BẮT BUỘC ItemsAdder contents + kiểm tra & sửa lỗi pack                     ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    logger.separator("═")
    
    options = get_conversion_options()
    
    ia_merger = ItemsAdderMerger(
        Path(java_pack_path),
        options["ia_contents"],
        options["ia_storage"]
    )
    working_java_path = ia_merger.merge()
    
    if not validate_input_directory(str(working_java_path)):
        ia_merger.cleanup()
        return False
    
    output_path = Path(output_base_path) / pack_name
    bedrock_structure = create_bedrock_structure(str(output_path))
    generate_manifest(output_path, working_java_path.name, options["mapping_version"])
    
    custom_mappings = {"metadata": {"source_pack": working_java_path.name, "converter_version": "2.3.0"}}
    results = {}
    
    logger.set_total_steps(7)
    results["items"] = convert_items_advanced(working_java_path, bedrock_structure, custom_mappings, options)
    results["weapons"] = convert_advanced_weapons(working_java_path, bedrock_structure, custom_mappings, options)
    results["armor"] = convert_armor_advanced(working_java_path, bedrock_structure, custom_mappings, options)
    results["sounds"] = convert_sounds_advanced(working_java_path, bedrock_structure, options)
    results["cosmetics"] = convert_cosmetics(working_java_path, bedrock_structure, custom_mappings, options)
    
    save_custom_mappings(custom_mappings, bedrock_structure, options["mapping_version"])
    create_summary_report(output_path, results, options)
    
    ia_merger.cleanup()
    
    logger.separator("═")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                        ✅ CONVERSION COMPLETED!                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    logger.info(f"📁 Bedrock Pack: {output_path}")
    logger.info("📋 Copy thư mục vào plugins/Geyser-Spigot/packs/ và /geyser reload")
    return logger.summary()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n" + "="*80)
        print("MINECRAFT RESOURCE PACK CONVERTER v2.3.0 - Interactive Mode")
        print("="*80 + "\n")
        java_path = input("📁 Đường dẫn Java Resource Pack: ").strip()
        output_path = input("📁 Đường dẫn output [./bedrock_packs_v2]: ").strip() or "./bedrock_packs_v2"
        pack_name = input("📝 Tên pack [converted_pack_v2]: ").strip() or "converted_pack_v2"
        pack_name = pack_name.replace(" ", "_")
        success = main(java_path, output_path, pack_name)
        sys.exit(0 if success else 1)
    else:
        java_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else "./bedrock_packs_v2"
        pack_name = sys.argv[3] if len(sys.argv) > 3 else "converted_pack_v2"
        pack_name = pack_name.replace(" ", "_")
        success = main(java_path, output_path, pack_name)
        sys.exit(0 if success else 1)

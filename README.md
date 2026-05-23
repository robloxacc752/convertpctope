# 🎮 Minecraft Resource Pack Converter v2.4.0

> **Chuyển đổi Java Edition Resource Pack → Bedrock Edition** để sử dụng với **GeyserMC**  
> Hỗ trợ đầy đủ ItemsAdder, Custom Model Data, 3D Inventory Models, Armor Attachables và Sounds.

---

## ✨ Tính năng chính

### 📦 Core Conversion
| Tính năng | Mô tả |
|-----------|-------|
| **Items & Custom Model Data** | Quét và map toàn bộ CMD overrides sang Bedrock virtual ID |
| **Armor Attachables** | Convert custom armor textures sang Bedrock attachable format |
| **Sounds & Music** | Chuyển đổi `sounds.json` + copy file `.ogg` sang Bedrock structure |
| **Cosmetics** | Hỗ trợ mũ, wings, particle (yêu cầu ItemsAdder configs) |
| **Weapons** | Convert vũ khí nâng cao (yêu cầu ItemsAdder configs) |

### 🗂️ Inventory Model Display *(Mới v2.4.0)*
| Tính năng | Mô tả |
|-----------|-------|
| **item_texture.json** | Tự động tạo registry icon cho toàn bộ items trong inventory |
| **Icon copy** | Copy PNG textures từ Java → `textures/items/` theo đúng namespace |
| **Custom CMD Icons** | Mỗi Custom Model Data override → icon texture riêng |
| **3D Geometry** | Convert Java `elements` (cube 3D) → Bedrock `.geo.json` |
| **render_offsets** | Convert Java `display` props → Bedrock hand/inventory transforms |
| **Attachables** | Tạo `minecraft:attachable` đúng format (sửa lỗi key sai v2.3) |
| **Inventory Animations** | Idle, damaged, enchanted animation effects |

### 🔌 ItemsAdder Integration
- Merge `contents/` folder vào Java pack trước khi convert
- Parse YAML configs để detect item class, armor class
- Load `items_ids_cache.yml` để convert armor chính xác

---

## 📋 Yêu cầu hệ thống

```
Python 3.8+
```

### Thư viện tùy chọn
```bash
pip install PyYAML   # Cần cho ItemsAdder YAML configs
pip install Pillow   # Cần cho xử lý texture (resize, format check)
```
> Nếu thiếu, converter vẫn chạy nhưng bỏ qua các tính năng liên quan.

---

## 🚀 Cách chạy nhanh

```bash
# Interactive mode (khuyến nghị)
python minecraft_resourcepack_converter_FIXED.py

# Command line mode
python minecraft_resourcepack_converter_FIXED.py <java_pack_path> [output_path] [pack_name]
```

**Ví dụ:**
```bash
python minecraft_resourcepack_converter_FIXED.py "C:\MyPack" "C:\Output" "my_bedrock_pack"
```

---

## 📁 Cấu trúc Output

Sau khi convert, Bedrock pack được tạo tại `output_path/pack_name/`:

```
converted_pack/
├── manifest.json                        ← GeyserMC pack header
├── custom_mappings.json                 ← GeyserMC item mappings
├── CONVERSION_REPORT.txt                ← Báo cáo chi tiết
├── attachables/
│   └── inventory_swords_diamond_sword.json
├── animations/
│   └── inventory_animations.json
├── models/
│   └── entity/
│       └── item_custom_sword.geo.json   ← 3D geometry (nếu có)
├── textures/
│   ├── item_texture.json                ← Icon registry (MỚI)
│   ├── items/
│   │   ├── sword.png
│   │   ├── bow.png  …
│   │   └── custom/
│   │       └── diamond_sword_cmd1001.png  ← CMD icons (MỚI)
│   └── models/armor/
│       └── custom_armor_layer_1.png
└── sounds/
    └── *.ogg
```

---

## ⚙️ GeyserMC Setup

1. Copy thư mục pack vào:
   ```
   plugins/Geyser-Spigot/packs/
   ```
2. Reload server:
   ```
   /geyser reload
   ```
3. Bedrock client kết nối → pack tự động load.

---

## 📜 Changelog

### v2.4.0
- ✅ **Thêm** toàn bộ pipeline Inventory Model Display (7 hàm mới)
- ✅ **Thêm** `item_texture.json` generation
- ✅ **Thêm** Java 3D elements → Bedrock `.geo.json` converter
- ✅ **Thêm** Custom CMD icon copy (`textures/items/custom/`)
- ✅ **Thêm** `render_offsets` từ Java `display` properties
- ✅ **Sửa** key sai `"attachable"` → `"minecraft:attachable"`
- ✅ **Sửa** `NameError: cache_file_path` trong `ItemsAdderMerger.__init__`
- ✅ **Sửa** input cache path chấp nhận cả thư mục lẫn file

### v2.3.0
- ✅ Thêm ItemsAdderMerger
- ✅ Hoàn thiện PackValidator
- ✅ Thêm logic thật cho convert_items, armor, sounds, cosmetics, weapons

---

## 👥 Credit

| Vai trò | Người |
|---------|-------|
| Tác giả gốc | LeHoangNam @ HorseKingdom Studio |
| Sửa lỗi & tính năng mới | LeHoangNam @ HorseKingdom Studio |

---

## ⚠️ Lưu ý

- Cần kiểm tra Bedrock compatibility thủ công trước khi deploy production.
- Một số custom cosmetics phức tạp vẫn cần chỉnh tay sau convert.
- File `.geo.json` được tạo tự động có thể cần fine-tune UV mapping với model phức tạp.

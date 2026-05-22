# 📚 HƯỚNG DẪN SỬ DỤNG MINECRAFT RESOURCE PACK CONVERTER

**Phiên bản:** 1.0.0  
**Tác giả:** LeHoangNam @ HorseKingdom Studio  
**Mục đích:** Chuyển đổi Resource Pack từ Minecraft Java sang Bedrock Edition với tối ưu cho GeyserMC

---

## 📋 MỤC LỤC

1. [Yêu cầu & Chuẩn bị](#yêu-cầu--chuẩn-bị)
2. [Cách cài đặt](#cách-cài-đặt)
3. [Cách sử dụng](#cách-sử-dụng)
4. [Giải thích chi tiết](#giải-thích-chi-tiết)
5. [Cấu trúc tệp tạo ra](#cấu-trúc-tệp-tạo-ra)
6. [Xử lý sự cố](#xử-lý-sự-cố)

---

## ✅ Yêu cầu & Chuẩn bị

### Yêu cầu Hệ Thống
- **Python:** 3.8 trở lên
- **OS:** Windows, macOS, hoặc Linux
- **Dung lượng đĩa:** Tối thiểu 2-3 lần kích thước Java Resource Pack

### Thư viện Python
```bash
# Thư viện chuẩn (không cần cài thêm):
- os, json, shutil, uuid, pathlib, re, sys, datetime

# Thư viện tùy chọn (nếu cần xử lý ảnh):
pip install Pillow
```

### Chuẩn bị Java Resource Pack
Đảm bảo Java Resource Pack của bạn có cấu trúc tiêu chuẩn:
```
my_resource_pack/
├── assets/
│   └── minecraft/
│       ├── models/
│       │   └── item/
│       ├── textures/
│       │   ├── items/
│       │   ├── models/armor/
│       │   └── font/
│       └── sounds/
├── pack.mcmeta
└── pack.png
```

---

## 🔧 Cách cài đặt

### Windows
```bash
# 1. Mở PowerShell hoặc Command Prompt
# 2. Tải script:
#    (sao chép file minecraft_resourcepack_converter.py)

# 3. Kiểm tra Python
python --version

# 4. (Tuỳ chọn) Cài Pillow để xử lý ảnh
pip install Pillow
```

### macOS / Linux
```bash
# 1. Mở Terminal
# 2. Tải script
# 3. Kiểm tra Python
python3 --version

# 4. (Tuỳ chọn) Cài Pillow
pip install Pillow
```

---

## 🚀 Cách sử dụng

### Phương pháp 1: Interactive Mode (Dễ dùng nhất)
```bash
# Windows:
python minecraft_resourcepack_converter.py

# macOS / Linux:
python3 minecraft_resourcepack_converter.py

# Sau đó nhập:
# 📁 Nhập đường dẫn Java Resource Pack: C:\Users\...\Downloads\MyPack
# 📁 Nhập đường dẫn output: ./bedrock_packs
# 📝 Nhập tên pack: my_awesome_pack
```

### Phương pháp 2: Command Line Arguments
```bash
python3 minecraft_resourcepack_converter.py \
  /path/to/java/pack \
  ./bedrock_packs \
  my_converted_pack
```

### Phương pháp 3: Import vào Script Python khác
```python
from minecraft_resourcepack_converter import main

# Gọi hàm main
main(
    java_pack_path="./my_java_pack",
    output_base_path="./bedrock_packs",
    pack_name="converted_pack"
)
```

### Kết quả sau chạy
Script sẽ tạo:
```
bedrock_packs/
└── my_converted_pack/
    ├── manifest.json              ← Metadata pack
    ├── custom_mappings.json       ← Mappings GeyserMC (QUAN TRỌNG!)
    ├── sound_definitions.json     ← Định nghĩa âm thanh
    ├── CONVERSION_REPORT.txt      ← Báo cáo chi tiết
    ├── attachables/               ← Armor definitions
    │   └── [armor_name].json
    ├── textures/
    │   ├── items/                 ← Item textures
    │   ├── models/armor/          ← Armor textures
    │   └── font/                  ← Font/emoji
    ├── models/                    ← 3D models
    ├── sounds/                    ← Sound files
    └── font/
        └── default.json           ← Font config
```

---

## 📖 Giải thích chi tiết

### 1️⃣ Items & Custom Model Data (CMD)

#### Vấn đề
Java Edition dùng cơ chế "Predicate" để tạo multiple models cho một item:

**Java JSON Model:**
```json
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
```

Bedrock Edition **KHÔNG** hỗ trợ predicate này.

#### Giải pháp
- Script quét các file JSON để tìm tất cả `custom_model_data` IDs
- Tạo "virtual items" trong Bedrock (được quản lý bởi GeyserMC)
- Tạo file `custom_mappings.json`:

```json
{
  "java_cmd": {
    "diamond_sword_1": {
      "java_item": "minecraft:diamond_sword",
      "custom_model_data": 1,
      "bedrock_virtual_id": "item.geyser.diamond_sword_1"
    }
  }
}
```

**Cách hoạt động:**
1. Player Java nhận item với `CustomModelData:1` từ server
2. GeyserMC đọc `custom_mappings.json`, tìm mapping
3. GeyserMC gửi Bedrock client virtual item ID
4. Bedrock render item với texture từ resource pack

---

### 2️⃣ Custom Armor & Attachables

#### Vấn đề
Java dùng Entity Model định sẵn để render armor:
```
assets/minecraft/textures/models/armor/
├── diamond_layer_1.png    ← Lớp ngoài
└── diamond_layer_2.png    ← Lớp trong
```

Bedrock hoàn toàn khác:
- Không có Entity Model cố định
- Dùng **Attachables** - hệ thống gắn object lên player

#### Giải pháp
1. **Copy textures:** `diamond_layer_1.png` → Bedrock `textures/models/armor/`
2. **Tạo attachable JSON:**
   ```json
   {
     "format_version": "1.10.0",
     "attachable": {
       "description": {
         "identifier": "geometry.armor.custom_diamond",
         "materials": {"default": "armor"},
         "textures": {"default": "textures/models/armor/diamond_layer_1"},
         "geometry": {"default": "geometry.armor.diamond"}
       }
     }
   }
   ```

3. **Thêm vào custom_mappings.json:**
   ```json
   {
     "custom_armor": {
       "diamond": {
         "java_item_prefix": "minecraft:diamond",
         "bedrock_armor_id": "armor.custom_diamond",
         "attachable_file": "attachables/diamond.json"
       }
     }
   }
   ```

**Cách hoạt động:**
1. Player Java mặc diamond helmet
2. GeyserMC detect armor type từ `custom_mappings.json`
3. Load attachable JSON từ Bedrock pack
4. Render attachable lên Bedrock player model

---

### 3️⃣ Fonts & Emojis

#### Vấn đề
Java Font System:
- Dùng Unicode Font PNG files
- Mã Unicode trực tiếp → pixel trên texture

Bedrock Font System:
- Dùng Font Definition JSON
- Cần định nghĩa glyph coordinates (x, y, width, height)

#### Giải pháp
1. **Copy font PNG:** `assets/.../font/*.png` → Bedrock `textures/font/`
2. **Tạo font/default.json:**
   ```json
   {
     "default": {
       "font": "textures/font/default.png",
       "glyphs": [
         {
           "chars": "ABC...",
           "ascent": 8,
           "height": 10,
           "glyphs": [
             {"char": "A", "x": 0, "y": 0, "w": 8, "h": 10}
           ]
         }
       ]
     }
   }
   ```

**Lưu ý:** Conversion chính xác cần phân tích PNG để tìm glyph bounds. Script tạo template cơ bản - có thể cần chỉnh sửa thủ công.

---

### 4️⃣ Sounds & Music

#### Vấn đề
Java Format:
```json
{
  "entity.player.hurt": {
    "sounds": [
      "damage/hit1",
      "damage/hit2"
    ],
    "subtitle": "subtitles.player.hurt"
  }
}
```

Bedrock Format:
```json
{
  "entity.player.hurt": {
    "sounds": [
      {"name": "sounds/damage/hit1", "load_on_open": true},
      {"name": "sounds/damage/hit2", "load_on_open": true}
    ],
    "category": "master",
    "subtitle": "subtitles.player.hurt"
  }
}
```

#### Khác biệt chính
1. **Category:** Bedrock cần xác định loại âm thanh (master, music, record, weather...)
2. **Sound object:** Array của string → Array của object
3. **Path format:** Relative paths phải bắt đầu từ `sounds/`

#### Giải pháp
- Script tự động detect category dựa trên tên event
- Convert paths sang format Bedrock
- Sao chép tất cả `.ogg` files
- Tạo `sound_definitions.json`

---

## 📁 Cấu trúc tệp tạo ra

### Bedrock Resource Pack Structure
```
bedrock_pack/
├── manifest.json
│   └─ Metadata pack (UUID, version, format)
│
├── custom_mappings.json ⭐ QUAN TRỌNG
│   └─ Mappings Java → Bedrock cho GeyserMC
│
├── sound_definitions.json
│   └─ Định nghĩa âm thanh Bedrock format
│
├── attachables/
│   ├─ diamond.json
│   ├─ netherite.json
│   └─ ...
│
├── textures/
│   ├─ items/
│   │  ├─ diamond_sword.png
│   │  ├─ custom_item.png
│   │  └─ ...
│   ├─ models/armor/
│   │  ├─ diamond_layer_1.png
│   │  ├─ diamond_layer_2.png
│   │  └─ ...
│   └─ font/
│      ├─ default.png
│      └─ emoji.png
│
├── sounds/
│   ├─ damage/
│   │  ├─ hit1.ogg
│   │  └─ hit2.ogg
│   ├─ ambient/
│   │  └─ cave1.ogg
│   └─ ...
│
├── models/
│   └─ (custom models nếu có)
│
├── font/
│   └─ default.json
│
└─ CONVERSION_REPORT.txt
```

### File Quan Trọng

#### manifest.json
**Mục đích:** Bedrock metadata - bắt buộc phải có
```json
{
  "format_version": 3,
  "header": {
    "name": "[Java→Bedrock] My Pack",
    "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "version": [1, 0, 0]
  },
  "modules": [
    {
      "type": "resources",
      "uuid": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
      "version": [1, 0, 0]
    }
  ]
}
```

#### custom_mappings.json ⭐
**Mục đích:** Mapping Java items → Bedrock cho GeyserMC
```json
{
  "version": "1.0.0",
  "description": "Custom Resource Pack Mappings for GeyserMC",
  "mappings": {
    "java_cmd": {
      "diamond_sword_1": {
        "java_item": "minecraft:diamond_sword",
        "custom_model_data": 1,
        "bedrock_virtual_id": "item.geyser.diamond_sword_1"
      }
    },
    "custom_armor": {
      "diamond": {
        "java_item_prefix": "minecraft:diamond",
        "bedrock_armor_id": "armor.custom_diamond",
        "attachable_file": "attachables/diamond.json"
      }
    }
  }
}
```

---

## 🖥️ Cách sử dụng với GeyserMC

### Bước 1: Chuẩn bị GeyserMC
```bash
# Cài GeyserMC plugin cho Spigot/Bukkit hoặc standalone
# Download từ: https://geysermc.org/download

# Cấu trúc thư mục:
server/
├── plugins/
│   ├── Geyser-Spigot.jar
│   └── Geyser-Spigot/
│       ├── config.yml
│       └── packs/     ← Nơi đặt resource pack
└── ...
```

### Bước 2: Copy Resource Pack
```bash
# Copy toàn bộ thư mục bedrock pack vào:
cp -r my_converted_pack/ server/plugins/Geyser-Spigot/packs/

# Hoặc trên Windows:
# Copy thư mục my_converted_pack vào GeyserMC/packs/
```

### Bước 3: Cấu hình GeyserMC (config.yml)
```yaml
remote:
  address: localhost  # Java server address
  port: 25565

resource-packs:
  # Bedrock packs được tự động load từ packs/ folder
  
  # Nếu cần xác định cụ thể:
  packs:
    - my_converted_pack

  # Bắt buộc load pack (ngăn player bỏ qua)
  force-resources: true
```

### Bước 4: Restart Server
```bash
# Restart GeyserMC
/geyser reload

# Hoặc restart toàn bộ server
```

### Bước 5: Test
- Connect Bedrock client (Phone, Xbox, Windows 10/11 Edition)
- Resource pack sẽ tự động download
- Verify custom items/armor/sounds hoạt động

---

## 🐛 Xử lý sự cố

### ❌ "Thư mục không tồn tại"
```
❌ Lỗi: Thư mục không tồn tại: /path/to/pack
❌ Lỗi: Không tìm thấy thư mục 'assets'
```

**Giải pháp:**
- Kiểm tra đường dẫn có dấu cách hay ký tự đặc biệt không
- Đảm bảo Java pack có thư mục `assets/`
- Thử đường dẫn tuyệt đối thay vì tương đối:
  ```bash
  # Sai:
  python3 converter.py ./my_pack
  
  # Đúng:
  python3 converter.py /Users/username/Downloads/my_pack
  ```

### ❌ "Thư viện Pillow không được cài đặt"
```
⚠️  Thư viện Pillow không được cài đặt. Một số tính năng xử lý ảnh sẽ bị tắt.
```

**Giải pháp:**
```bash
# Cài Pillow
pip install Pillow

# Hoặc trên macOS:
pip3 install Pillow
```

### ❌ Resource pack không load trong GeyserMC
```
[GeyserMC] Resource pack failed to load
```

**Kiểm tra:**
1. File `manifest.json` có valid không?
   ```python
   # Test import JSON
   import json
   with open("manifest.json") as f:
       data = json.load(f)  # Nếu có lỗi SyntaxError, fix JSON
   ```

2. UUID trong manifest.json có hợp lệ không?
   - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - Phải có 2 UUIDs (header uuid + module uuid)

3. Đường dẫn tệp có đúng không?
   - Bedrock case-sensitive trên Linux/macOS
   - Kiểm tra tất cả đường dẫn trong JSON files

4. Đã copy đến thư mục đúng không?
   ```bash
   ls -la /path/to/server/plugins/Geyser-Spigot/packs/my_pack/
   # Phải thấy: manifest.json, textures/, sounds/...
   ```

### ❌ Custom items không hiển thị
```
Custom Model Data không được convert
```

**Kiểm tra:**
1. `custom_mappings.json` có chứa items không?
   ```bash
   grep "java_cmd" custom_mappings.json
   ```

2. GeyserMC có đọc file không?
   - Xem log: `[GeyserMC] Loading custom mappings...`

3. Item texture có tồn tại không?
   - Verify: `textures/items/[item_name].png`

### ⚠️ Font/Emoji không hiển thị
```
Font không được render đúng
```

**Giải pháp:**
- Script tạo template cơ bản - có thể cần chỉnh sửa thủ công
- Glyph coordinates có thể không chính xác
- Cách fix:
  1. Mở `font/default.json`
  2. Điều chỉnh `x`, `y`, `w`, `h` để match vị trí character trên PNG
  3. Test in-game

### ⚠️ Armor không hiển thị
```
Custom armor texture không render
```

**Kiểm tra:**
1. Attachable JSON có tồn tại không?
   - `attachables/[armor_name].json`

2. Geometry ID có đúng không?
   - Format: `geometry.armor.custom_[name]`

3. Texture path có tồn tại không?
   - Verify: `textures/models/armor/[name]_layer_1.png`

---

## 💡 Tips & Tricks

### Optimization
1. **Compress textures:**
   ```bash
   # Sử dụng ImageMagick để compress PNG
   mogrify -quality 95 textures/**/*.png
   ```

2. **Optimize JSON:**
   ```bash
   # Minify custom_mappings.json để giảm dung lượng
   jq -c '.' custom_mappings.json > custom_mappings.min.json
   ```

### Debugging
1. **Enable verbose logging:**
   ```bash
   # Thêm vào script
   export DEBUG=1
   python3 converter.py ...
   ```

2. **Validate JSON:**
   ```bash
   # Kiểm tra syntax JSON
   python3 -m json.tool manifest.json > /dev/null
   ```

### Advanced
- **Batch convert multiple packs:**
  ```bash
  for pack in ~/packs/*; do
    python3 converter.py "$pack" ./bedrock_packs "$(basename $pack)"
  done
  ```

- **Automate deployment:**
  ```bash
  #!/bin/bash
  python3 converter.py "$1"
  cp -r bedrock_packs/* ~/geyser_server/plugins/Geyser-Spigot/packs/
  echo "Done! Resource pack deployed."
  ```

---

## 📞 Support & Links

- **GeyserMC Official:** https://geysermc.org/
- **GeyserMC GitHub:** https://github.com/GeyserMC/Geyser
- **Bedrock Edition Docs:** https://learn.microsoft.com/en-us/minecraft/creator/reference/content/
- **Minecraft Wiki:** https://minecraft.wiki/

---

## 📄 License & Credits

Converter được tạo bởi Claude @ Anthropic  
Tối ưu cho GeyserMC Plugin

---

**Chúc bạn chuyển đổi thành công! 🎮✨**

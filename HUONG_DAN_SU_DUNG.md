# 📖 Hướng Dẫn Sử Dụng — Resource Pack Converter v2.4.0

---

## 🔧 Cài đặt ban đầu

### Bước 1 — Đảm bảo có Python 3.8+
```bash
python --version
# hoặc
python3 --version
```

### Bước 2 — Cài thư viện (khuyến nghị)
```bash
pip install PyYAML Pillow
```

### Bước 3 — Đặt file script ở nơi dễ tìm
```
C:\Tools\
└── minecraft_resourcepack_converter_FIXED.py
```

---

## ▶️ Khởi chạy

Mở **Command Prompt** hoặc **PowerShell**, chạy:

```bash
python "C:\Tools\minecraft_resourcepack_converter_FIXED.py"
```

Script sẽ bước vào **Interactive Mode** và hỏi từng thông tin một.

---

## 📋 Các bước nhập liệu

### Câu hỏi 1 — Đường dẫn Java Resource Pack

```
📁 Đường dẫn Java Resource Pack:
```

Nhập đường dẫn đến **thư mục gốc** của Java pack (nơi có `pack.mcmeta` và `assets/`).

✅ Ví dụ đúng:
```
C:\Users\thedo\Downloads\MyJavaPack
```

❌ Không nhập path đến file zip — phải giải nén trước.

---

### Câu hỏi 2 — Đường dẫn output

```
📁 Đường dẫn output [./bedrock_packs_v2]:
```

Thư mục để lưu Bedrock pack đã convert. Nhấn **Enter** để dùng mặc định `./bedrock_packs_v2`.

✅ Ví dụ:
```
C:\Users\thedo\Desktop\BedrockPacks
```

---

### Câu hỏi 3 — Tên pack

```
📝 Tên pack [converted_pack_v2]:
```

Tên thư mục output. Khoảng trắng tự động thành `_`.

---

## ⚙️ Menu Cài Đặt Nâng Cao

Sau khi nhập đường dẫn, script hiển thị menu 6 lựa chọn:

---

### 1. Phiên bản GeyserMC Mappings

```
[1] V3 (ổn định)       ← Khuyến nghị cho server production
[2] V4 (thử nghiệm)    ← Dùng nếu GeyserMC yêu cầu
```

Chọn `1` nếu không chắc.

---

### 2. Hỗ trợ Animation Frames

```
(Y/N, mặc định Y)
```

`Y` — Convert animation frames của textures (flipbook).  
`N` — Bỏ qua, textures tĩnh.

---

### 3. Hỗ trợ Cosmetics

```
(Y/N, mặc định Y)
```

`Y` — Convert mũ, wings, particle effects (cần ItemsAdder configs).  
`N` — Bỏ qua cosmetics.

---

### 4. Chế độ log chi tiết

```
(Y/N, mặc định Y)
```

`Y` — In từng file đang được xử lý (giúp debug).  
`N` — Chỉ in tổng kết.

---

### 5. ItemsAdder Contents (tùy chọn)

```
Nhập đường dẫn tuyệt đối đến thư mục 'contents' của ItemsAdder.
Để trống nếu không có ItemsAdder.
```

Trỏ đến thư mục `contents` **bên trong plugin ItemsAdder** trên server.  
Cấu trúc bên trong phải có dạng:

```
contents/
├── namespace_A/
│   ├── resourcepack/
│   │   └── assets/
│   └── configs/
└── namespace_B/
    ├── resourcepack/
    └── configs/
```

✅ Ví dụ:
```
C:\Server\plugins\ItemsAdder\contents
```

❌ Nếu thư mục không có cấu trúc namespace/resourcepack → script báo lỗi và hỏi lại.

> Để trống và nhấn **Enter** nếu không dùng ItemsAdder.

---

### 6. File cache ItemsAdder (tùy chọn)

```
Nhập đường dẫn đến 'storage/items_ids_cache.yml' (hoặc thư mục storage):
```

File này giúp detect chính xác armor class và override class.  
**Có thể nhập theo 2 cách:**

**Cách A — Trỏ vào thư mục `storage`** *(script tự tìm file)*:
```
C:\Server\plugins\ItemsAdder\storage
```

**Cách B — Trỏ thẳng vào file**:
```
C:\Server\plugins\ItemsAdder\storage\items_ids_cache.yml
```

Cả hai đều được chấp nhận.

> Để trống nếu không có → armor conversion sẽ bị giới hạn.

---

## 🔄 Quá trình Convert

Sau khi nhập xong, script tự động chạy **10 bước**:

```
[1/10] Merge ItemsAdder contents
[2/10] Validate Java pack
[3/10] Tạo cấu trúc Bedrock
[4/10] Convert Items & Custom Model Data
[5/10] Convert Armor & Attachables
[6/10] Convert Inventory Models (Icon + 3D)    ← Mới v2.4.0
[7/10] Tạo Inventory Attachables
[8/10] Tạo Inventory Animations
[9/10] Convert Sounds & Music
[10/10] Save mappings & báo cáo
```

---

## 📊 Đọc báo cáo kết quả

Sau khi xong, xem file `CONVERSION_REPORT.txt` trong thư mục output:

```
Inventory Models (3D Display + Icons):
  ├─ Items with display props : 24
  ├─ Textures copied          : 156
  ├─ item_texture.json entries: 156   ← Số icon trong inventory
  ├─ 3D geo models            : 8     ← Số model 3D được convert
  ├─ Swords                   : 6
  ├─ Tools                    : 10
  ├─ Armor                    : 4
  ├─ Custom                   : 4
  ├─ Attachables              : 24
  └─ Animations               : ✓
```

---

## 📂 Deploy lên GeyserMC

1. Copy **toàn bộ thư mục** output vào server:
   ```
   plugins/Geyser-Spigot/packs/<tên_pack>/
   ```

2. Trong console server:
   ```
   /geyser reload
   ```

3. Bedrock client kết nối → pack tự động tải xuống và áp dụng.

---

## ❓ Xử lý lỗi thường gặp

### ❌ `NameError: name 'cache_file_path' is not defined`
**Nguyên nhân:** Dùng file cũ v2.3.0 hoặc trước đó.  
**Giải pháp:** Dùng file `minecraft_resourcepack_converter_FIXED.py` v2.4.0 trở lên.

---

### ❌ `Thư mục 'contents' không có cấu trúc ItemsAdder hợp lệ`
**Nguyên nhân:** Trỏ sai thư mục — phải trỏ vào `contents`, không phải thư mục cha.  
**Giải pháp:** Kiểm tra bên trong có subfolder dạng `namespace/resourcepack/` chưa.

---

### ❌ `File không hợp lệ hoặc không phải items_ids_cache.yml`
**Nguyên nhân:** Phiên bản cũ chỉ chấp nhận path đến file, không chấp nhận thư mục.  
**Giải pháp:** Dùng v2.4.0 — nhập path thư mục `storage` cũng được.

---

### ❌ `PyYAML không cài — không thể load cache file`
**Nguyên nhân:** Thiếu thư viện PyYAML.  
**Giải pháp:**
```bash
pip install PyYAML
```

---

### ❌ Pack load nhưng icon item không hiển thị đúng
**Kiểm tra:**
- `textures/item_texture.json` có tồn tại trong pack không?
- Shortname trong `texture_data` có khớp với GeyserMC mappings không?
- Thử `/geyser dump` để xem log chi tiết.

---

### ❌ 3D model không hiện đúng hình dạng
**Nguyên nhân:** UV mapping phức tạp, rotation nhiều chiều.  
**Giải pháp:** Mở file `.geo.json` trong `models/entity/` và kiểm tra bằng [Blockbench](https://www.blockbench.net).

---

## 💡 Tips

- **Backup** Java pack gốc trước khi chạy.
- Chạy với **Verbose = Y** lần đầu để kiểm tra từng bước.
- Nếu pack lớn (> 500 items), quá trình có thể mất vài phút.
- Dùng **V3 mappings** trừ khi GeyserMC của bạn yêu cầu V4.
- Sau khi deploy, test trên Bedrock client thật (không chỉ emulator).

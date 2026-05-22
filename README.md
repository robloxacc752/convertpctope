# Minecraft Resource Pack Converter (Python) – Java → Bedrock

> Chuyển đổi Java Resource Pack sang Bedrock Edition, tối ưu cho GeyserMC, hỗ trợ ItemsAdder (contents + storage)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Tính năng

- ✅ Chuyển đổi Items (Custom Model Data), Armor 2D/3D, Blocks, Fonts, Sounds, Cosmetics
- ✅ Tích hợp **ItemsAdder** – tự động merge `contents` & `storage`, parse YAML config
- ✅ GeyserMC Mappings V3 / V4
- ✅ Xử lý animation (flipbook) từ `.png.mcmeta`
- ✅ Tự động kiểm tra và sửa lỗi pack sau merge
- ✅ Giao diện dòng lệnh (CLI) đẹp, log chi tiết bằng tiếng Việt

---

## 📦 Yêu cầu

- **Python** 3.8 trở lên (tải tại [python.org](https://python.org))
- Các thư viện:

```bash
pip install pyyaml pillow
```

---

## 🔧 Cài đặt

```bash
# Clone hoặc tải script
git clone https://github.com/your-repo/mc-converter-python.git
cd mc-converter-python

# (Không cần cài thêm gì ngoài pip)
```

---

## 🎮 Cách sử dụng

### Chế độ tương tác (khuyến nghị)

```bash
python converter.py
```

Nhập theo hướng dẫn:

1. Đường dẫn tuyệt đối đến Java Resource Pack (thư mục chứa `assets/` và `pack.mcmeta`)
2. Đường dẫn thư mục output (mặc định `./bedrock_packs_v2`)
3. Tên pack (không dấu cách)
4. Đường dẫn đến `contents` của ItemsAdder (bắt buộc nếu có, để trống nếu không)
5. Đường dẫn đến `storage` (tùy chọn)

### Chế độ dòng lệnh (batch)

```bash
python converter.py "C:\JavaPacks\MyPack" "./output" "my_bedrock_pack"
```

---

## 🧩 Tích hợp ItemsAdder

Để converter nhận diện đúng, thư mục `contents` phải có cấu trúc chuẩn:

```
/đường/dẫn/contents/
└── ten_namespace/
    ├── configs/           # file .yml (items, armor, blocks, fonts, cosmetics)
    └── resourcepack/
        └── assets/
            └── ten_namespace/   # textures, models, sounds
```

Script sẽ tự động:

- Merge `resourcepack/assets` vào Java pack tạm thời
- Parse file YAML trong `configs/` để lấy metadata
- Copy `storage` (nếu có) vào thư mục `textures/font`

---

## ⚙️ Các tùy chọn nâng cao

| Tùy chọn | Mô tả |
|---|---|
| GeyserMC Mappings V3 | Ổn định, dùng cho hầu hết server |
| GeyserMC Mappings V4 | Thử nghiệm, hỗ trợ components, NBT, animation phức tạp |
| Animation frames | Bật/tắt xử lý ảnh động từ `.png.mcmeta` |
| Cosmetics | Chuyển đổi mũ, wings, particle từ ItemsAdder |
| Log chi tiết | Hiển thị thông tin xử lý từng file |

---

## ✅ Kiểm tra & sửa lỗi pack tự động

Sau khi merge ItemsAdder, script tự động:

- Tạo `assets/minecraft` nếu thiếu
- Tạo `pack.mcmeta` mặc định (`pack_format: 15`)
- Sửa đường dẫn texture trong các file `.json` (thêm `.png`)
- Xóa thư mục rỗng
- Phát hiện JSON lỗi cú pháp → tạo file `.bak`

---

## 📤 Triển khai lên GeyserMC

Copy toàn bộ thư mục Bedrock pack vào:

```
plugins/Geyser-Spigot/packs/
```

Reload Geyser:

```
/geyser reload
```

Kết nối từ Bedrock client → pack tự động tải.

---

## 🐛 Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách khắc phục |
|---|---|---|
| `pip` không được nhận diện | Python chưa trong PATH | Dùng `python -m pip install ...` hoặc cài lại Python (chọn "Add to PATH") |
| `KeyError: 'items'` | Phiên bản script cũ | Tải phiên bản 2.3.0 trở lên |
| Không tìm thấy contents hợp lệ | Đường dẫn sai hoặc thiếu `resourcepack/assets` | Nhập lại đường dẫn tuyệt đối, kiểm tra cấu trúc |
| Pack không load trong Geyser | `manifest.json` lỗi | Xóa pack cũ, chạy lại converter |
| Font bị lệch | Thiếu config glyph width | Cài `pillow` để tự động quét hoặc sửa thủ công file `font/*.json` |

---

## 📄 Giấy phép

MIT License. Xem file [LICENSE](LICENSE).

---

**Phiên bản:** 2.3.0 &nbsp;|&nbsp; **Cập nhật:** Tháng 5, 2026

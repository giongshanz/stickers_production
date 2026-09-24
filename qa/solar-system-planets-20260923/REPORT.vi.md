# Topic Các hành tinh trong Hệ Mặt Trời — QA ngày 23/09/2026

## Kết quả

Đã tạo và chọn đủ 8 sticker `solar-system-planets`: Sao Thủy, Sao Kim, Trái Đất, Sao Hỏa, Sao Mộc, Sao Thổ, Sao Thiên Vương và Sao Hải Vương. Mỗi ID là một PNG RGBA 1254 × 1254; 512 × 512 chỉ là target trong prompt. Không resize, thêm lề hoặc chỉnh màu RGB bằng script. Mẫu phong cách chỉ lấy từ `references/Stickers/`.

| ID | Nhận xét chọn bản |
|---|---|
| `planet-mercury` | Bản đầu có quá nhiều hố nhỏ và texture dày nên bị loại. Bản chọn có đúng bảy hố rộng, mảng xám ấm và bóng dịu, dễ đọc ở kích thước nhỏ. |
| `planet-venus` | Dải mây vàng đất và kem rõ, không có hố hoặc chi tiết phụ. |
| `planet-earth` | Đại dương xanh, lục địa đơn giản nhưng nhận ra được, mây và băng cực rõ; không có cảnh nền. |
| `planet-mars` | Mảng địa hình đỏ gạch, cam đất và một chỏm cực nhạt; nhận dạng rõ. |
| `planet-jupiter` | Dải khí kem, nâu và cam cùng một bão oval đỏ; khác rõ Sao Kim. |
| `planet-saturn` | Bản đầu sát mép ngang; bản ImageGen edit được chọn có lề rộng hơn. Hai lỗ vòng đai từng có nền trắng giả và đã được làm sạch bằng alpha-only workflow. |
| `planet-uranus` | Bản đầu có vòng đai quá dày và gần mép; bản chọn có vòng mảnh, lề thoáng và hai lỗ alpha thật. |
| `planet-neptune` | Xanh lam sâu, các dải khí xanh sáng và một bão oval xanh đậm; khác rõ Sao Thiên Vương. |

## Alpha và truy vết

- Cả tám master có alpha thật ở bốn góc và bản `delivery` trùng byte với master.
- Sao Thổ đã được làm sạch hai lỗ vòng đai, 86 pixel rời trong lỗ và alpha 1–15/255 ngoài viền; RGB và canvas được kiểm tra không đổi.
- Bảy hình còn lại được làm sạch alpha 1–15/255 sau khi so trên contact sheet nền sáng/tối. Tổng cộng 75.175 pixel alpha cực mờ được đặt về 0; RGB và kích thước giữ nguyên.
- Bản trước sửa, ứng viên, hash cũ/mới và lý do chọn nằm trong `revisions/solar-system-planets-20260923/`.
- Contact sheet: `qa/solar-system-planets-20260923/planets-light.png` và `planets-dark.png`.

## Giới hạn QA

Đã xem từng hình ở độ phân giải nguồn và cả bộ trên nền sáng/tối. Chủ thể, màu nhận dạng, silhouette, viền trắng, lề và các lỗ vòng đai được chấp nhận tạm thời. Vẫn cần xem trong giao diện game ở kích thước sử dụng thật để xác nhận chi tiết nhỏ và độ đồng đều thị giác. 25 rework của các topic cũ vẫn mở riêng.

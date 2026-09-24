# Topic Book — QA ngày 22/09/2026

## Kết quả

Đã tạo và chọn đủ 8 sticker `book-collection`, mỗi ID một PNG RGBA gốc 1254 × 1254. Prompt target là 512 × 512; không resize, thêm lề hay đổi màu RGB bằng script. Cả tám master có alpha thật ở bốn góc và bản `delivery` trùng byte với master sau khi chọn. Mẫu phong cách chỉ lấy từ `references/Stickers/`.

| ID | Nhận xét chọn bản |
|---|---|
| `book-blue-hardcover` | Sách xanh bìa cứng, mép giấy kem, dấu mặt trời và ruy băng rõ; không chữ. |
| `book-open-storybook` | Hai trang minh họa riêng biệt, không chữ. Bản đầu quá sát mép ngang; ImageGen edit được chọn có thêm khoảng trong suốt. Bản cũ, hash và prompt chỉnh sửa lưu trong `revisions/book-collection-20260922/`. |
| `book-three-volume-stack` | Đúng ba cuốn màu san hô, xanh lá và vàng đất; hình khối dễ đọc. |
| `book-pocket-paperback` | Bản đầu quá dày; bản ImageGen edit mỏng hơn được chọn. Bản đầu và prompt chỉnh sửa được lưu để truy vết. |
| `book-accordion-picture-book` | Ba panel liền mạch với tranh chim và hoa, không chữ. |
| `book-pop-up-castle` | Lâu đài giấy nổi lên từ sách mở, đầy đủ các tháp và mép trang. |
| `book-leather-tome` | Sách da nâu dày, bốn góc kim loại và khóa; không chữ. |
| `book-small-diary` | Nhật ký du lịch màu mận với dây thun và trăng nhỏ. Bản hồng đầu giống quá gần hình sách trong mẫu gốc nên bị loại; lưu trong `revisions/book-collection-20260922/`. |

Mỗi master được làm sạch alpha 1–15/255 để bỏ hạt nền rất mờ dọc mép. Bản trước sửa của cả master và delivery, hash cũ/mới và số pixel thay đổi nằm ở `revisions/book-collection-20260922/alpha-selections.json`; RGB và canvas được kiểm tra không đổi. Không dùng script để chỉnh bố cục hoặc tô lại ảnh.

## Giới hạn QA

Đã xem từng hình ở kích thước nguồn trên nền tối, đối chiếu chủ thể, viền và khoảng trống. Các hình được chấp nhận **tạm thời** cho topic Book. Vẫn cần xem trong giao diện game ở kích thước sử dụng thật để xác nhận những chi tiết nhỏ và viền trắng mảnh; alpha ở bốn góc không chứng nhận mọi mép ảnh đã hoàn hảo. 25 rework của các topic cũ vẫn mở riêng.

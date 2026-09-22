# Topic “Mèo” — QA sơ bộ

Đã tạo 8 sticker riêng: mướp xám, đen, tuxedo, tam thể, Xiêm, trắng lông dài, mèo con cam và British Shorthair xanh xám. Từng hình dùng một lời gọi ImageGen tích hợp; prompt và đường dẫn mẫu gốc chính xác nằm trong `state/requests/cat-*.json`. Bốn yêu cầu đầu dùng hai mẫu Cat đầu tiên; bốn yêu cầu sau chuyển sang cặp mẫu mèo mở mắt để tăng đa dạng biểu cảm. Không dùng sticker đã gen làm mẫu.

Đã xem ở độ phân giải gốc và trên hai contact sheet `light-sheet.png`, `dark-sheet.png`. Cả tám có dáng và màu lông dễ phân biệt ở cỡ thumbnail, viền trắng quanh hình, không có chữ hoặc đạo cụ không yêu cầu. `machine-audit.json` xác nhận mỗi PNG RGBA 1254 × 1254 có bốn góc alpha bằng 0, master trùng hash với delivery và `index.html` trỏ đúng file. Lề alpha nhỏ nhất là 39 px; không thấy hình bị cắt cụt.

Đánh giá là **chấp nhận tạm thời**, không phải game-ready cuối cùng. Mèo mướp xám, tuxedo và tam thể dùng biểu cảm nhắm mắt cười khá gần nhau; cần giữ ý này nếu mở rộng bộ mèo. Vẫn cần kiểm tra mép ria, khe giữa chân và viền sáng ở kích thước game thực tế. 25 ghi chú rework của các topic cũ không thay đổi.

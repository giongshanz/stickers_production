# Topic “Các loài cá” — QA sơ bộ

Đã tạo 8 sticker riêng: cá hề, cá đuôi gai xanh, koi, betta, cá nóc, cá sư tử, cá ngựa và cá đuối manta. Mỗi hình được tạo bằng một lời gọi ImageGen riêng, dùng prompt chính xác trong `state/requests/` và hai mẫu phong cách gốc trong `references/Stickers/`. Không resize hoặc sửa RGB/alpha bằng script.

Đã kiểm tra đủ hình, đúng chủ thể, không có chữ, silhouette và viền cắt trên nền sáng/tối ở cả độ phân giải gốc lẫn contact sheet. Xem `light-sheet.png`, `dark-sheet.png` và `machine-audit.json`. Tám file đều là PNG RGBA 1254 × 1254, bốn góc alpha bằng 0; master và delivery trùng hash, catalogue trỏ đúng file.

Đánh giá hiện tại là **chấp nhận tạm thời**, không phải chứng nhận game-ready. Mép vây/gai của cá sư tử, vòng đuôi cá ngựa và các chi tiết đầu cá đuối cần được rà lại ở kích thước sử dụng thật. Koi và cá sư tử có lề alpha sát nhất trong nhóm (lần lượt 13 px và 17 px tính cả các pixel rìa rất mờ); chưa thấy bị cắt cụt trên contact sheet nhưng cần lưu ý nếu engine lấy mẫu sát mép. 25 ghi chú rework trước đó không thay đổi.

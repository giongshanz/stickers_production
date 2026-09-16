Đợt 16/09/2026: 17 sticker mới thuộc freshwater-wetland, mediterranean-mezze và picnic-day.

Dùng built-in ImageGen, mỗi sticker một request. Prompt chính xác trong state/requests; các request trước khi sửa hình nằm trong revisions/generation-20260916. Đã sửa đuôi chuột xạ, số chân bọ nước và lề chiếu picnic bằng ImageGen.

17 master hiện hành là PNG RGBA, 1254 x 1254 thực tế. Target trong prompt là 512 x 512; không resize hoặc pad bằng script. Sửa alpha theo quyền người dùng đã cho phép. RGB và kích thước đối chiếu nguyên vẹn với bản gốc, không mất pixel màu đang hiển thị theo phép kiểm tra trong báo cáo.

Quy trình alpha: tách vùng ngoài viền trắng bằng scripts/alpha_cleanup.py, bỏ thành phần rời, chỉ gọt phần trắng thừa bằng phép mở mask. Mở ba khoảng rỗng đã nhìn thấy: nơ sandwich và hai quai bình giữ nhiệt. Chuột xạ dùng vùng tranh có màu được giãn 11 pixel để bỏ các ô caro trắng bám ngoài. Tất cả đã xem trên nền tối. Thông số, hash và bản gốc nằm trong final-alpha-review.json và các revision được dẫn từ đó.

selected-overview.jpg là ảnh tổng quan để xem, không phải sprite dùng trong game. Các ảnh preview thu nhỏ không thay đổi kích thước PNG master.

75 candidate alpha của đợt 15/09 vẫn chưa chọn; không nhầm chúng với 17 bản alpha đã chọn của đợt này.

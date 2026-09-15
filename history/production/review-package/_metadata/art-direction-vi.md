# Hướng mỹ thuật đã chỉnh theo phản hồi

Nguồn phong cách duy nhất: `C:/Users/sonng/OneDrive/Máy tính/Stickers/`. Bộ trong project không dùng làm chuẩn phong cách.

Yêu cầu ngày 14/09/2026 đã được làm rõ: chỉ đổi target trong prompt từ 1024 × 1024 sang 512 × 512 cho các lần tạo tiếp theo. Không resize ảnh đã tạo hoặc ép kích thước bằng script. Ghi nhận kích thước thực tế của từng file Imagegen trả về.

Mẫu tổ ong đầu tiên `beehive-skep-pilot.png` bị loại: tương phản cao, bóng mạnh, vân dày và khối quá giống render 3D.

- Minh họa 2D vẽ tay, màu ấm trung sáng; phối màu có kiểm soát.
- Nét bao mảnh, dùng nâu hoặc sắc đậm hơn cùng màu vật thể. Nét trong mảnh và nhẹ hơn nét ngoài.
- Hai đến ba mảng bóng gần màu nền, vài vệt cọ sáng nhỏ. Không bóng đen sâu, phản quang trắng gắt hoặc texture dày.
- Tỷ lệ đầy đặn vừa phải; vật thể nhận ra được khi thu nhỏ. Không tự gắn mặt cười vào đồ vật.
- Thú có mắt và biểu cảm đơn giản. Người có mắt nhỏ, biểu cảm nhẹ và dáng dễ đọc.
- Viền trắng vừa phải theo đường cắt, không thêm đường đen bên ngoài viền trắng. Nền alpha thật phải được kiểm tra bằng dữ liệu PNG.

Ảnh đối chiếu: bánh croissant trong `1-Bakery & Coffee Cafe`, bình tưới trong `8-Gardening`, hoodie trong `Shirts`, máy lạnh trong `Houseware`, nồi cơm trong `2. Home appliance`, nhân vật trong `Women`, bò trong `1_Animals`.

Kiểm tra trước bàn giao: đủ ít nhất 8 PNG mỗi chủ đề; nền trong suốt; hình không cắt cụt; đúng chủ thể; độ tương phản phù hợp; không chữ rác. Hình dùng chung giữa hai chủ đề dùng cùng mã và cùng nội dung PNG. Giữ prompt và nguồn tham chiếu để tạo bổ sung.

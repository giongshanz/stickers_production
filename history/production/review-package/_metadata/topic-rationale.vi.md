# Cơ sở thiết kế bộ sticker mới

Kế hoạch gồm **50 chủ đề, mỗi chủ đề đúng 8 vị trí**: tổng cộng 400 vị trí dùng 390 hình độc lập. Có 10 hình được dùng chung, mỗi hình thuộc đúng hai chủ đề. Danh sách hình và quan hệ dùng chung nằm trong `sticker-plan.json`.

## Nguồn tham chiếu

Chỉ thư mục `C:/Users/sonng/OneDrive/Máy tính/Stickers` được dùng để xác định phong cách hình ảnh. Danh sách thư mục sticker trong dự án chỉ đã được đối chiếu để tránh lặp nguyên tên chủ đề, không được dùng làm mẫu phong cách. Mẫu thử `beehive-skep-pilot.png` có tương phản và độ bóng không phù hợp, đã bị loại; hình `beehive-skep` trong kế hoạch phải được tạo lại.

## Chủ đề và khả năng nhận diện

Các chủ đề mở rộng từ những nhóm phổ biến như đồ ăn, động vật và dụng cụ sang những nhóm cụ thể hơn: nghề nuôi ong, làm gốm, đóng sách, in thủ công, khí tượng, khoáng vật, khảo cổ và phục hồi san hô. Nhóm món Việt và Tết Việt bổ sung nét gần gũi với người chơi Việt Nam. Các nhóm thủ công, khoa học, sinh cảnh, du lịch và cổ tích tạo nhịp thay đổi về hình dáng lẫn màu sắc.

Mỗi hình cần có một chủ thể chính với đường bao dễ phân biệt khi thu nhỏ. Các cụm nhỏ như đôi găng tay, ba chiếc bánh hoặc bộ dụng cụ chỉ được gom khi người chơi nhận ra chúng như một vật hoặc một phần ăn. Hạn chế bối cảnh, chữ, biểu trưng và chi tiết trang trí cạnh tranh với chủ thể.

## Hình dùng chung

Mười cặp có giao điểm rõ nghĩa: món Việt/Tết Việt dùng bánh chưng; nuôi ong/bữa sáng mật ong dùng que lấy mật; xưởng gốm/khảo cổ dùng bình amphora; may vá/sân khấu dùng mannequin; nấm rừng/hái lượm dùng giỏ nấm; terrarium/sen đá dùng haworthia; lặn ngắm san hô/vườn ươm san hô dùng san hô sừng hươu; bưu điện/thư pháp dùng dấu sáp; phòng thí nghiệm/khí tượng dùng nhiệt kế; nhạc cụ gõ/đội nhạc diễu hành dùng trống snare.

Mỗi hình dùng chung có một ID duy nhất, một file gốc duy nhất và hai quan hệ chủ đề. Không tạo hai phiên bản hơi khác nhau cho cùng một hình dùng chung.

## Hướng dẫn hình ảnh cho sản xuất

Mô tả tiếng Anh trong JSON chỉ quy định vật thể và đặc điểm nhận diện. Luôn ghép chúng với hướng dẫn phong cách được hiệu chỉnh từ mẫu desktop: giữ độ dịu của màu, độ tương phản thấp vừa phải và bề mặt mềm; tránh chất liệu nhựa bóng, điểm lóe trắng mạnh, khối 3D hoặc tương phản đậm như mẫu thử bị loại. Độ dày đường viền, bóng đổ và cách xử lý mép phải theo đúng mẫu desktop đã được kiểm tra.

Hình đầu ra cần nền trong suốt thật, đủ khoảng đệm, không bị cắt chi tiết và có kích thước nhất quán. Trước khi đóng gói, kiểm tra đọc được ở kích thước chơi thực tế, không thêm chữ vô nghĩa, không thừa vật thể, không lẫn nền màu trắng vào alpha và không có khác biệt phong cách giữa các lượt tạo.

## Kiểm tra cấu trúc

- 50 `topics`, mỗi mục có 8 `asset_ids` khác nhau.
- 390 `assets`, mỗi `id` là duy nhất.
- Tổng số quan hệ chủ đề–hình: 400.
- 10 `shared_assets`, mỗi mục có đúng 2 `topic_slugs`.
- Không sử dụng nhân vật có bản quyền, logo thương hiệu hoặc chữ cần đọc.

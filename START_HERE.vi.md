# stickers_production

Đây là workspace sản xuất chính. Chỉ cần mang toàn bộ folder này sang vị trí hoặc máy mới để giữ đủ dữ liệu và tiếp tục tiến độ. Mở `index.html` để xem catalogue; không cần chạy server hay cài Python để xem ảnh.

## Chuyển máy và tiếp tục

1. Đợi lần ghi file hiện tại hoàn tất, rồi copy nguyên folder, gồm mọi thư mục con. Nếu chuyển qua OneDrive, bảo đảm file đã tải đầy đủ xuống máy mới.
2. Mở chính folder này làm project/workspace trong Codex. Đọc `AGENTS.md` và `state/resume.json`. Không cần mang Unity project, các folder sản xuất cũ hoặc cuộc trò chuyện cũ.
3. Máy mới cần có công cụ tạo ảnh tương ứng trong tài khoản và còn hạn mức. Để chạy script quản lý, dùng Python 3.11 trở lên và Pillow; Codex có thể dùng runtime Python sẵn có trên máy. Nếu thiếu, chạy `python -m pip install -r requirements.txt` từ folder này. Trên macOS/Linux, lệnh có thể là `python3`.
4. Chạy `python scripts/workspace.py verify`. Thành công nghĩa là dữ liệu khớp checksum và các tham chiếu cần thiết đều nằm trong folder.
5. Gửi câu sau vào phiên mới:

> Tiếp tục sản xuất sticker trong workspace này. Đọc AGENTS.md, START_HERE.vi.md, state/resume.json và các ghi chú mỹ thuật; kiểm tra dữ liệu rồi tiếp tục các ID còn thiếu. Chỉ dùng references/Stickers làm mẫu phong cách. Target prompt 512 × 512, không resize bằng script. Lưu tất cả kết quả và tiến độ trong workspace này.

Folder chứa dữ liệu sản xuất, không chứa tài khoản, hạn mức, mô hình tạo ảnh hoặc cài đặt Codex của máy cũ. Có thể giữ cùng tiến độ, mẫu và quy trình; ảnh sinh mới không được bảo đảm giống tuyệt đối từng pixel.

## Cấu trúc

| Vị trí | Nội dung |
|---|---|
| `index.html` | Catalogue các chủ đề hiện có; tìm kiếm, lọc ảnh thiếu/cần sửa, đổi nền xem ảnh |
| `masters/` | Một PNG được chọn cho mỗi ID; nguồn chính để đóng gói |
| `references/Stickers/` | Toàn bộ 1.708 file từ bộ mẫu ngoài project |
| `delivery/stickers/` | Bản sao theo topic của ảnh có alpha ở bốn góc; vẫn cần kiểm tra viền |
| `delivery/_needs-alpha/` | Bản sao theo topic của ảnh còn cần sửa nền |
| `plan/` | Kế hoạch chủ đề hiện hành, chủ thể và 10 ID dùng chung |
| `prompts/` | Hướng mỹ thuật, prompt hiện hành và nhóm ảnh tham chiếu |
| `state/` | Tiến độ, vị trí tiếp tục, hàng đợi, yêu cầu tạo ảnh và checksum |
| `qa/` | Nhận xét mỹ thuật và kiểm tra alpha/lề bằng cách đọc PNG |
| `logs/` | Nhật ký tạo ảnh có đường dẫn tương đối |
| `revisions/` | Các bản sửa đã chọn, bản cũ và bản thử bị loại; xem README trong đó |
| `scripts/` | Công cụ quản lý và script sửa alpha đã được người dùng cho phép |
| `history/` | Nhật ký/metadata/script cũ, đối chiếu chuyển dữ liệu và bản lưu Git cũ; chỉ tra cứu |

## Tiến độ lúc chuyển workspace

173/390 ảnh master, 183/400 vị trí theo topic, 22/50 topic đã có đủ 8 hình. Trong đó 96 ảnh có alpha ở bốn góc, 77 ảnh cần sửa nền, và 25 ID có ghi chú cần chỉnh mỹ thuật/viền. Còn thiếu 217 ảnh. Số mới nhất luôn nằm trong `state/progress.json`.

Cập nhật 16/09/2026: đã tạo thêm 17 sticker, tổng 190/390 master và 200/400 vị trí theo topic; 25/50 topic có đủ 8 hình. Cả 17 hình mới đã chọn bản RGBA sau kiểm tra nền, viền và RGB. Còn 77 master cũ cần sửa nền, 25 ghi chú cần chỉnh và 75 bản alpha cũ chưa được chọn. Xem `state/batch-20260916.json` và `qa/batch-20260916/`.

Cập nhật 22/09/2026: sau khi hoàn tất 50 chủ đề gốc, người dùng yêu cầu thêm chủ đề “Các loài cá” gồm 8 sticker. Mục tiêu hiện tại là 51 chủ đề, 408 vị trí và 398 master duy nhất. Số đã tạo và QA còn mở xem `state/progress.json`; các mốc cũ bên trên chỉ là lịch sử.

Cập nhật sau đó: người dùng yêu cầu thêm chủ đề “Mèo” gồm 8 sticker. Mục tiêu mới là 52 chủ đề, 416 vị trí và 406 master duy nhất. Xem `state/progress.json` để biết số thực tế đã tạo; các mốc trước là lịch sử.

## Các lệnh quản lý

Chạy từ workspace (hoặc gọi script bằng đường dẫn đến folder đã copy):

```text
python scripts/workspace.py status
python scripts/workspace.py verify
python scripts/workspace.py next --count 4 --write
python scripts/workspace.py save --id wetland-heron --source <file-tool-tra-ve.png> --request state/requests/wetland-heron.json
python scripts/workspace.py refresh
```

`next` chỉ chuẩn bị yêu cầu; bước tạo ảnh do Codex gọi công cụ imagegen. `save` sao chép nguyên byte và từ chối ghi đè master. `refresh` cập nhật catalogue, bảng topic, tiến độ, kiểm tra alpha/lề và checksum sau khi thay đổi hợp lệ. `verify` chỉ đọc và báo file thiếu hoặc thay đổi; không tự sửa dữ liệu. Không có script nào gọi API, cần API key, tạo cron hoặc tự phát sinh chi phí tạo ảnh.

Mọi đường dẫn đang sử dụng đều tính từ gốc workspace. Đường dẫn máy cũ chỉ được giữ trong `history/` để truy vết. Các bản cũ ngoài workspace được giữ nguyên làm bản dự phòng, không còn là đầu vào hay đầu ra của quy trình này.

## Quy tắc mỹ thuật cần giữ

Mẫu chuẩn là bộ tham chiếu gốc ngoài Unity project: màu ấm trung sáng, tương phản dịu, viền mảnh có sắc độ theo vật thể, hai hoặc ba mảng bóng nhẹ và ít chi tiết. Tránh khối bóng như đồ chơi 3D, hốc đen sâu và texture dày.

512 × 512 là target trong prompt theo yêu cầu đã làm rõ. Giữ kích thước thật của file công cụ trả về; không resize, thêm lề hoặc chỉnh màu bằng script. Ngày 15/09/2026, người dùng đã cho phép dùng script tách nền và làm sạch alpha, giữ nguyên kích thước và màu RGB; quyền này tiếp tục có hiệu lực ở phiên mới. Ô caro in vào PNG không phải alpha thật. Kiểm tra góc ảnh chưa thay thế duyệt mỹ thuật và kiểm tra các khoảng rỗng bên trong sticker.

Không chạy script trong `history/`, không lấy checkpoint cũ hoặc mẫu thử bị loại làm bản hiện hành. Dùng công cụ tạo ảnh cho việc sửa nét/hình dáng; script được phép sửa alpha theo phạm vi trên. Lưu lại lý do chọn từng phiên bản.

Ưu tiên tiếp theo: hoàn thiện nền/alpha và các ghi chú mỹ thuật còn tồn của 25 chủ đề đã có đủ hình. Xem state/work-order.json. Hàng đợi tạo mới đã tuân theo phạm vi này; hàng đợi rỗng không có nghĩa là đã hoàn tất mục tiêu 50 chủ đề.

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

Cập nhật 22/09/2026: người dùng yêu cầu thêm topic “Book” và đã cho phép tạo đủ 8 sticker sau khi xem mẫu đầu. Mục tiêu hiện tại là 53 chủ đề, 424 vị trí và 414 master duy nhất. Cả 8 Book master đã được tạo và QA tạm thời; xem `qa/book-collection-20260922/REPORT.vi.md`. Vẫn còn 25 rework cũ và QA ở kích thước game.

Cập nhật 23/09/2026: thêm và hoàn tất topic “Các hành tinh trong Hệ Mặt Trời” gồm tám hành tinh. Mục tiêu hiện tại là 54 chủ đề, 432 vị trí và 422 master duy nhất. Cả tám master đã được tạo và QA tạm thời; xem `qa/solar-system-planets-20260923/REPORT.vi.md`. Vẫn còn 25 rework cũ và QA ở kích thước game.

Cập nhật 23/09/2026: người dùng chốt thêm năm topic Dog, Khủng long, Thể thao mùa đông, Găng tay và Tea, mỗi topic tám sticker. Mục tiêu mới là 59 chủ đề, 472 vị trí và 462 master duy nhất; 40 ID mới đang chờ tạo theo thứ tự topic trong plan.

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

Cập nhật 23/09/2026: đã hoàn tất 8 sticker Dog và 8 sticker Khủng long trong năm topic mới. Hiện có 56/59 topic đủ hình, 438/462 master và 448/472 vị trí topic; còn 24 master thuộc Thể thao mùa đông, Găng tay và Tea. Xem `qa/dog-dinosaur-20260923/REPORT.vi.md`.

Cập nhật 23/09/2026: người dùng thêm topic Farm gồm tám sticker: barn, tractor, cow, pig, sheep, hen, hay bale và windmill. Mục tiêu mới là 60 chủ đề, 480 vị trí và 470 master duy nhất; ưu tiên hiện tại là tạo đủ topic Farm trước ba topic đang chờ.

Cập nhật 23/09/2026: đã hoàn tất 8/8 sticker Farm. Hiện có 57/60 topic đủ hình, 446/470 master và 456/480 vị trí topic; còn 24 master thuộc Thể thao mùa đông, Găng tay và Tea. Xem `qa/farm-20260923/REPORT.vi.md`.

Cập nhật 23/09/2026: người dùng thêm topic Crocodile gồm tám sticker cùng một nhân vật cá sấu thân thiện trong các hoạt động đi biển, lướt sóng, xây lâu đài cát, bơi phao, ăn kem, đọc sách, nhảy vui và ngủ. Mục tiêu mới là 61 chủ đề, 488 vị trí và 478 master duy nhất; ưu tiên hiện tại là hoàn tất Crocodile.


## Cập nhật Crocodile hoàn tất — 23/09/2026

- Đã hoàn tất topic Crocodile: 8/8 sticker hoạt động.
- Trạng thái sau batch: 58/61 topic đủ 8 ảnh; 454/478 master duy nhất; 464/488 slot đã có ảnh; còn 24 master.
- QA batch: `qa/crocodile-20260923/REPORT.vi.md`.


## Đã thêm 6 topic nhân vật — 23/09/2026

- Đã thêm Penguin, Frog, Capybara, Rabbit Gardener, Little Bear Camping và Duck Rainy Day; mỗi topic 8 slot.
- Tổng target mới: 67 topic, 536 slot, 526 master duy nhất.


## Hoàn tất 6 topic nhân vật — 23/09/2026

- Hoàn tất Penguin, Frog, Capybara, Rabbit Gardener, Little Bear Camping và Duck Rainy Day: 48/48 sticker.
- Trạng thái sau batch: 64/67 topic đủ 8 ảnh; 502/526 master duy nhất; 512/536 slot đã có ảnh; còn 24 master.
- QA batch: `qa/six-character-topics-20260923/REPORT.vi.md`.


## Hoàn tất Winter Sports, Gloves và Tea — 23/09/2026

- Hoàn tất 24/24 sticker của ba topic cuối.
- Đã có đủ 67/67 topic, 526/526 master duy nhất và 536/536 topic slot.
- 25 visual rework candidate và game-scale QA vẫn còn mở.
- QA batch: `qa/final-three-topics-20260923/REPORT.vi.md`.


## Đã thêm 7 topic mới — 24/09/2026

- Đã thêm Red Panda Daily Life, Fox Autumn Adventures, Hamster Kitchen, Panda Bakery, Koala Bedtime, Little Dragon Magic và Birthday Cake Collection; mỗi topic 8 slot.
- Tổng target mới: 74 topic, 592 slot, 582 master duy nhất.


## Hoàn tất 7 topic mới — 24/09/2026

- Hoàn tất 56/56 sticker của Red Panda, Fox Autumn, Hamster Kitchen, Panda Bakery, Koala Bedtime, Little Dragon Magic và Birthday Cake.
- Đã có đủ 74/74 topic, 582/582 master duy nhất và 592/592 topic slot.
- 25 visual rework candidate và game-scale QA vẫn còn mở.
- QA batch: `qa/seven-topics-20260924/REPORT.vi.md`.


## Hoàn tất 8 topic mới — 24/09/2026

- Hoàn tất 64/64 sticker của Otter River Life, Sloth Cozy Day, Owl Night Study, Little Bee Adventures, Snail Garden Journey, Baby Elephant Playtime, Monkey Jungle Adventures và Little Ghost Halloween.
- Đã có đủ 82/82 topic, 646/646 master duy nhất và 656/656 topic slot.
- 25 visual rework candidate và game-scale QA vẫn còn mở.
- QA batch: `qa/eight-topics-20260924/REPORT.vi.md`.


## Đang triển khai 20 topic theo 10 cặp — 24/09/2026

- Mục tiêu mới: 102 topic, 816 slot, 796 master duy nhất; 20 ID dùng chung.
- Xem checkpoint mới nhất tại `qa/twenty-pairs-20260924/CHECKPOINT.vi.md` và trạng thái trong `state/resume.json`.

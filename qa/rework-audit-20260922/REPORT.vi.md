# QA 25 sticker cần rework — 22/09/2026

## Phạm vi và kết luận

Đã mở trực tiếp cả 25 master trong `qa/visual-qa.json`, xem ở độ phân giải gốc trên nền tối, đồng thời đối chiếu contact sheet nền tối và nền sáng trong folder này. Tất cả 25 vẫn có lỗi nhìn thấy trong khoảng rỗng/viền alpha và **chưa được duyệt cuối**. Chủ thể chính đều nhận ra được; không có căn cứ để tạo lại toàn bộ 25 ảnh theo mặc định. Ưu tiên là xử lý alpha có kiểm soát theo từng hình; ảnh có nhiều thanh/cành/căm nhỏ cần kiểm tra kỹ để không xóa nét vẽ.

Máy kiểm tra: 25/25 file master mở được, là RGBA 1254 × 1254, có alpha thật ở nền ngoài và padding ít nhất 20 px. 25/25 bản `delivery` trùng SHA-256 với master, 25/25 đường dẫn hiện diện trong `index.html`. Góc alpha trong không chứng nhận các khe bên trong đã sạch. Số liệu từng file nằm ở `machine-audit.json`.

## Hai ID người dùng báo thiếu

| ID | Kết quả |
|---|---|
| `access-hearing-aid` | `masters/access-hearing-aid.png` và `delivery/stickers/accessible-everyday/access-hearing-aid.png` đều có, mở được, cùng SHA-256 `2ced182d295a720a83f9189a2728103d91158aeb3fa34f493f282694570d4bca`; `index.html` có link. Ảnh đúng máy trợ thính sau tai. |
| `railway-signal` | `masters/railway-signal.png` và `delivery/stickers/railway-station/railway-signal.png` đều có, mở được, cùng SHA-256 `c03a05cc5da282ad70522d07543c4f13b25c0edc6d216b475228224ab009b317`; `index.html` có link. Ảnh đúng tín hiệu đường sắt cần gạt. |

Không tạo lại hai ID này vì nguồn và bản giao hiện hữu, khớp checksum. Nếu chúng không xuất hiện ở nơi khác ngoài workspace này, cần kiểm tra bước nhập/copy ở nơi đó.

## Nhóm A — nhiều khoảng rỗng hoặc cấu trúc mảnh (14 hình)

| ID | Phát hiện trực quan | Hướng QA tiếp |
|---|---|---|
| `desert-woven-saddlebag` | Khe lớn giữa hai túi còn mảng trắng và đốm đen. | Tách alpha vùng giữa; giữ nguyên cầu vải phía trên. |
| `arctic-research-hut` | Dưới sàn cabin và giữa chân chống/cầu thang còn nền trắng giả. | Sửa từng khe, bảo vệ các chân và bậc thang. |
| `arctic-ice-auger` | Quanh trục và cánh xoắn có đốm trắng/đen. | Tách từng khoảng giữa vòng xoắn, giữ thân trục màu sáng. |
| `arctic-snowmobile` | Khe tay lái, thân xe và giữa hai ván trượt còn mảng nền giả. | Sửa alpha nhiều vùng, giữ kính chắn gió bán trong. |
| `fairy-thimble-bucket` | Khoảng hở dưới quai cành còn mảng trắng/đen lớn; thân xô vẫn có tranh vẽ. | Chỉ sửa phần trên miệng xô, tránh xóa vùng kim loại sáng. |
| `fairy-leaf-boat` | Khe tam giác giữa buồm hoa và mũi lá còn đốm đen/viền trắng dày. | Sửa alpha cục bộ, bảo vệ mép cánh hoa và mũi lá. |
| `fairy-dewdrop-watering-can` | Lỗ quai lá cuộn còn mảng trắng và đốm đen. | Sửa lỗ quai, giữ thân bình trong mờ. |
| `apothecary-drying-rack` | Nhiều khe giữa dây treo, vòng gỗ và ba bó cây còn nền trắng/đen. | Chia vùng nhỏ; không dùng xóa nền toàn ảnh. |
| `apothecary-balance-scale` | Các khoảng giữa xích, đĩa cân và trụ còn mảng nền giả khá rộng. | Sửa nhiều vùng, bảo vệ các mắt xích mảnh. |
| `canal-stone-bridge` | Khe giữa song lan can bị tô trắng thay vì trong suốt. | Tách từng khe giữa các song sắt. |
| `canal-bicycle` | Lỗ hai bánh xe và khe khung còn nền trắng giả; có thêm đốm đen dưới khung. | Xử lý từng ô giữa nan hoa, tránh xóa nan và giỏ hoa. |
| `canal-quayside-lamp` | Khoảng dưới tay đèn cong còn đốm trắng/đen; viền ngoài lốm đốm. | Sửa quai cong và viền; script nền tự động trước đó không nhận ra foreground. |
| `access-manual-wheelchair` | Bánh sau và khoảng giữa các thanh khung còn nền trắng giả; khe dưới có đốm đen. | Sửa các ô giữa nan hoa/khung, giữ tay vịn và trục bánh. |
| `access-walker` | Bản v2 đã giảm lỗi nhưng nhiều ô khung vẫn còn viền trắng và đốm; thử lấp lỗ alpha chỉ xóa 4.024 pixel, chưa đạt. | Ưu tiên xử lý nhiều ô thủ công/định hướng; không chọn bản thử hiện có. |

## Nhóm B — lỗ hoặc khe cục bộ (11 hình)

| ID | Phát hiện trực quan | Hướng QA tiếp |
|---|---|---|
| `desert-water-skin` | Khe giữa bình và dây tết còn viền trắng/đốm. | Sửa khe quai, giữ sợi dây nâu. |
| `desert-navigation-compass` | Lỗ khoen treo còn trắng và vài đốm đen. | Tách alpha bên trong khoen. |
| `arctic-sample-case` | Lỗ dưới tay xách còn trắng và vệt xám chéo. | Sửa riêng lỗ quai, giữ nắp xanh nhạt. |
| `arctic-snow-goggles` | Vòng dây sau kính còn mảng trắng/đen. | Sửa lỗ dây, giữ dây nâu mảnh. |
| `fairy-seed-lantern` | Lỗ vòng treo phía trên còn nền trắng. | Ứng viên alpha-only đã thử trong `revisions/alpha-hole-trial-20260922/`, chưa thay master vì cần duyệt cận cảnh/game-scale. |
| `fairy-winged-snail` | Khe giữa hai cuống mắt còn nền trắng và đốm đen. | Sửa riêng khe, giữ cuống và cánh trong mờ. |
| `apothecary-herb-bundle` | Lỗ vòng dây treo trên cùng còn trắng. | Sửa lỗ dây treo. |
| `access-white-cane` | Lỗ dây cổ tay và khe sát thân gậy còn nền trắng/đốm. | Sửa hai khe hẹp, giữ thân gậy trắng. |
| `access-braille-slate` | Khe giữa bảng và bút chấm còn mảng trắng/đen. Bút vẫn có trong master ở kích thước gốc. | Sửa khe mà không xóa bút rời. |
| `access-forearm-crutch` | Lỗ chữ U của đai ôm cẳng tay còn trắng. | Sửa lỗ đai, giữ ống nạng màu kem. |
| `access-reaching-aid` | Khe cò ở tay cầm xanh còn nêm trắng và đốm đen. | Sửa riêng lỗ cò. |

## Trạng thái chọn bản

Đây là QA, không phải lệnh phê duyệt bản thay thế: **không master hoặc delivery nào bị ghi đè**. Sau mỗi bản sửa, phải so nền tối/sáng và ở kích thước game; nếu chỉ sửa alpha thì kiểm tra RGB và canvas không đổi. Trước khi chọn bản mới, lưu master và mọi bản delivery cũ vào `revisions/` cùng hash cũ/mới và lý do, rồi `refresh` và `verify`.

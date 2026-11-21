# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 20:05 | Nhóm chỉ có 1 người có được chấp nhận không? `check_team.py` yêu cầu 4–6. | Giả định: được làm, một người kiêm mọi vai. `team_size = 1`; cảnh báo của `check_team.py` là sai lệch đã biết, ghi trong verification từng phase. | myblue-ai (PO) |
| 2 | 2026-11-21 20:18 | Nội dung PRD-0 trên lab board không truy cập được bằng công cụ AI của nhóm. Lấy luật từ đâu? | Bám theo `TODO(nhóm)` trong `chonoi/sim/*.py`, `chonoi/scenario.py`, các trường UI đọc trong `chonoi/web/index.html`, smoke test và `game.contract.json`. Chỗ nào không có thì đặt giả định ở các dòng dưới. | myblue-ai (PO) |
| 3 | 20:20 | Tick nào bắt đầu đếm ngạt? | Sau khi trừ oxy ở bước k, nếu oxy = 0 và đang dưới nước thì `zero_oxy_ticks += 1` (kể cả bước oxy vừa về 0). Đủ `choke_interval_ticks` → `choke`, −1 Máu, đếm lại từ 0. Lên mặt nước thì đếm về 0. | myblue-ai |
| 4 | 20:22 | Giỏ không đủ chỗ cho cả sản lượng (cá linh cho 3) thì sao? | Lấy tất cả hoặc không lấy gì: thiếu chỗ → `hold_full`, nút/đàn cá giữ nguyên. Không lấy một phần. | myblue-ai |
| 5 | 20:24 | `catch` hụt (không có cá trong `catch_radius`) có tính hồi chiêu không? | Có: mỗi lần bấm `catch` hợp lệ (dưới nước, hết hồi chiêu) đều đặt `catch_cd_ticks = round(catch_cooldown_s × 60)`, để không spam được. | myblue-ai |
| 6 | 20:25 | Bắt đàn cá xong đàn đó còn không? | Đàn bị bắt hết, bị xóa khỏi `fish`. Cá sinh thêm thuộc phase sau (ghi chú trong khung). | myblue-ai |
| 7 | 20:40 | Khách chọn món thế nào? | Trong các món nấu được bằng (kho − phần đã giữ chỗ), chọn ngẫu nhiên đều bằng luồng RNG `customer_dish` (tất định theo seed). Khách ngồi bàn trống có id nhỏ nhất. Không bàn trống → bỏ lượt, không sự kiện. Có bàn nhưng không món nào → `no_dish`. | myblue-ai |
| 8 | 20:42 | Khi nào trừ kho? | Giữ chỗ (`reserved`) lúc khách tới; trừ khỏi `stock` lúc bắt đầu nấu (`cook_started`), khi đó `reserved` của khách về `{}`. Khách bỏ đi trước khi nấu thì trả phần giữ chỗ. | myblue-ai |
| 9 | 20:44 | Bếp nấu món cho ai? | Interact bếp `idle` → nấu cho khách `waiting` đến sớm nhất (id nhỏ nhất) chưa có món đang nấu/chờ bưng/trên tay. Không có đơn nào → không làm gì. | myblue-ai |
| 10 | 20:46 | Boa và uy tín tính thế nào? | Lúc phục vụ: nếu `patience_ticks_left ≥ tip_min_patience_ratio × patience_s × 60` thì `tip = floor(price × tip_rate)` và uy tín `+tip_reputation`; ngược lại tip = 0. Trả tiền khi ăn xong (`eat_s`): `money` và `earned` cộng `price + tip`. Khách bỏ đi: uy tín `+left_reputation_delta`. Uy tín kẹp `[reputation_min, reputation_max]`. | myblue-ai |
| 11 | 20:48 | Interact quán chọn đối tượng nào? | Chỉ xét bếp/bàn trong `interact_radius`; sắp theo (khoảng cách, bếp trước bàn, id); chỉ thao tác đối tượng đầu tiên. Nếu đối tượng đó không có việc hợp lệ thì bước đó không làm gì. | myblue-ai |

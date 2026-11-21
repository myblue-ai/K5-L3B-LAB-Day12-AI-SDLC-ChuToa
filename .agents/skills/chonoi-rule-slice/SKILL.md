---
name: chonoi-rule-slice
description: Quy trình cho agent viết một lát luật chơi (gather hoặc quan) theo hợp đồng, kèm test hộp đen. Dùng khi nhận một TODO(nhóm) hoặc một mục ticket mới.
---

# chonoi-rule-slice

## Đầu vào agent phải đọc trước
1. Ticket/PRD của đúng phase (dán vào prompt) và `docs/clarify.md`.
2. `docs/contracts/README.md`: tên sự kiện, `data`, trường snapshot. Không đặt tên sự kiện mới khi chưa thêm vào hợp đồng.
3. `game.contract.json`: mọi số liệu lấy ở đây.

## Các bước
1. Chỗ mơ hồ: thêm một dòng giả định vào `docs/clarify.md` **trước** khi code.
2. Viết luật trong `chonoi/sim/<mode>.py`, theo thứ tự một bước ghi ở docstring module.
   - Số liệu: `self.t[...]` / `self.menu[...]`, không hard-code.
   - Ngẫu nhiên: `self.rng.get("<tên luồng>")`; không `random` toàn cục, không đồng hồ hệ thống.
   - Duyệt thực thể bằng `sort_by_id`; id mới bằng `self.ids.new(prefix)`.
   - Đầu vào mâu thuẫn: `raise BadInput(...)` (mã 2) trong `scenario.py` hoặc lúc dựng sim.
3. Viết test hộp đen trong `tests/test_<mode>_rules.py`: tạo scenario + inputs nhỏ, chạy `run_headless`, kiểm sự kiện và snapshot ở đúng tick.
4. Chạy `PYTHONPATH=tests:. python3 -m unittest discover -s tests` → phải OK.
5. Người review đọc diff; ghi vào `docs/ai-usage-log.md` agent đã làm gì và sai ở đâu.
6. Commit nhỏ, message ghi số test đã chạy.

## Không được
- Không sửa test cũ cho xanh khi luật sai; nếu đổi test phải ghi lý do trong commit.
- Không sửa khung (`chonoi/{headless,inputs,runner,...}.py`) nếu không ghi lý do.

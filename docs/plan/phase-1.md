# Kế hoạch Phase 1 (≤ 1 trang)

Lịch giả định của buổi lab: bắt đầu 20:00 (P0: 20:00–20:15), Phase 1 20:15–21:15, tag `phase-1` trước 21:15.

- **Mục tiêu:** gather (lặn, oxy, Máu, hái, bắt cá, giỏ, cập bến, xuất kho) và quan (khách, giữ chỗ, bếp, bưng, phục vụ, tiền, uy tín) chạy đúng Test Contract v1.0; gather → kho → quan nối được.
- **Việc / người / phụ thuộc** (một người, mỗi lát giao cho AI agent một lượt rồi tự review):

| Lát | Việc | Module | Phụ thuộc | Ước lượng |
|---|---|---|---|---|
| 1 | dive/surface, oxy, ngạt, Máu, ngất | `sim/gather` | hợp đồng sự kiện | M |
| 2 | hái nút, mọc lại, bắt cá, hồi chiêu, giỏ đầy | `sim/gather` | lát 1 | M |
| 3 | lịch khách, chọn món, giữ chỗ, kiên nhẫn, bỏ đi, no_dish | `sim/quan` | schema kho | M |
| 4 | interact bếp/bàn, nấu, bưng, phục vụ, ăn, trả tiền, boa, uy tín | `sim/quan` | lát 3 | M |
| QA | test luật cho từng lát + test tích hợp gather → quan, bằng chứng | `qa` | lát 1–4 | S |

- **Rủi ro:**
  - Không có PO trực tiếp cho các chi tiết luật → mọi giả định ghi `docs/clarify.md`, code đọc số từ `game.contract.json` để sửa nhanh khi có đáp án.
  - Một người làm 4 lát trong 60 phút → ưu tiên gather (test ẩn kiểm lại phase trước), quan làm sau.
  - Windows không có `python3` → dùng bản sao `python3.exe` trong PATH (máy chấm Linux giữ nguyên `headless_cmd`).

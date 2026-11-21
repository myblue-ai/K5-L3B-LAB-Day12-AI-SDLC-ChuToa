# Retro nhóm

## Phase 2 (nhanh) — 22:05
- Điều tốt: có `tools/proof.py` nên bằng chứng mỗi phase chỉ mất một lệnh; so sha256 với P1 chứng minh P2 không đổi hành vi headless.
- Điều tệ: không đọc được Ticket-02 nên P2 chỉ làm chắc hệ thống, có nguy cơ thiếu tính năng mà ticket thật yêu cầu; HUD chỉ kiểm bằng mắt.
- 1 hành động cho Phase 3: viết ADR + bảng tác động **trước** khi sửa code, và mọi thay đổi luật phải mặc định tắt (giữ nguyên byte output khi tuning không đổi).

## Phase 4 (cuối) — 23:10
- Rà lại hành động Phase 2: **đã làm**. ADR-0001 + bảng tác động được commit (b690c91) trước commit sửa code (af7e336); `burn_s` mặc định tắt và sha256 output P3 giống hệt P2.
- Điều tốt: hợp đồng sự kiện chốt từ kickoff nên 4 lát luật không phải đổi tên lần nào; `tools/proof.py` cho bằng chứng thật trong một lệnh; hồi quy kiểm bằng sha256 qua 4 tag.
- Điều tệ: không đọc được PRD-0 và các ticket trên lab board bằng công cụ AI. Toàn bộ luật chi tiết là giả định (clarify #2–#13), nên test ẩn có thể trượt. Nhóm 1 người nên không có review chéo thật và không đạt điều kiện 4–6 thành viên.
- Số liệu:
  - Commit theo người (sau starter): myblue-ai 15 commit trước khi gắn tag phase-4 (cộng commit retro này); 1.249 dòng thêm trong `chonoi/`, `tests/`, `tools/`.
  - Test: 32 (starter) → 64 (P1) → 68 (P2) → 72 (P3–P4), tất cả xanh ở mỗi tag.
  - Cách đọc code: agent viết từng lát, tôi đọc diff và chạy test trước mỗi commit (không có PR vì một người).
  - Token theo người (ước tính từ nhật ký AI): myblue-ai ~170k.
- Một lần AI sai và cách phát hiện: ở Phase 3, bản đầu cho nấu lại món cháy chỉ kiểm `stock ≥ công thức`, nên lấy luôn nguyên liệu khách khác đã giữ chỗ. Lỗi lộ ra khi viết cột "Hệ quả" của ADR; thêm test `test_recook_after_burn_uses_free_stock_only` rồi sửa.
- Nếu làm lại, đổi gì: chép tay PRD/ticket từ lab board vào `docs/` ngay khi mở để agent đọc được; viết test cho giả định quan trọng nhất (thứ tự một bước) trước khi viết luật; quay video HUD làm bằng chứng thay cho kiểm bằng mắt.

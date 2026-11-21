# Kế hoạch Phase 2 (≤ 1 trang) — re-planning

Lịch giả định: Phase 2 21:15–22:10, smoke tích hợp ở phút 20 (21:35), tag `phase-2` trước 22:10.

- **Đầu vào:** Ticket-02 trên lab board **không đọc được bằng công cụ AI** (clarify #13). Không bịa yêu cầu của ticket; phase này làm các việc có thật rút ra từ `docs/verification/phase-1.md` và các `TODO(nhóm)` còn lại trong khung. Khi có nội dung Ticket-02, thêm lát mới theo skill `chonoi-rule-slice`.
- **Thay đổi so với Phase 1:** chuyển từ "viết luật" sang "làm chắc": kiểm cấu hình, cửa sổ chơi chế độ quán, bằng chứng tích hợp lặp lại được.

| Lát | Việc | Module | Nguồn yêu cầu | Ước lượng |
|---|---|---|---|---|
| 2.1 | Kiểm dải tuning quán còn để `TODO(nhóm)`: bếp/bàn, carry_limit, uy tín, công thức món | `contracts` (`chonoi/contract.py`) | TODO trong `contract.py` | S |
| 2.2 | Test cửa sổ chơi chế độ quan (đọc kho, khách xuất hiện) | `qa` | verification P1: UI quán chưa có test | S |
| 2.3 | HUD quán: đếm ngược khách đang ăn, trạng thái bếp chín | `client/ui` | verification P1: HUD chưa đủ | S |
| 2.4 | Smoke tích hợp phút 20 + retro nhanh + tag | `qa` | lịch board | S |

- **Rủi ro:** lệch Ticket-02 thật (test ẩn có thể kiểm thứ chưa làm); giữ output headless Phase 1 không đổi (so sha256 với `docs/proof/phase-1/determinism.txt`).

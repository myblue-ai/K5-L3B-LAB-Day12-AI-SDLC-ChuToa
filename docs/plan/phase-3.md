# Kế hoạch Phase 3 (≤ 1 trang) — change request

Lịch giả định: 22:10–22:45, tag `phase-3` trước 22:45.

- **Mục tiêu:** cơ chế món cháy theo `burn_s` (ADR-0001), mặc định tắt để output P1–P2 giữ nguyên byte.
- **Thứ tự:** ADR + bảng tác động + hợp đồng sự kiện (commit riêng, trước code) → `contract.py` → `quan.py` → test → hồi quy (so sha256 với `proof/phase-2`) → bằng chứng → tag.
- **Rủi ro:** Ticket-03 thật có thể là change request khác (clarify #13); nấu lại món cháy có thể lấy nhầm nguyên liệu khách khác đã giữ chỗ → có test riêng.

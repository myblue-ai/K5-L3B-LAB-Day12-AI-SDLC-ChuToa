# Changelog

## 1.0.0 — 2026-11-21

### Phase 4
- `tools/bench.py`: bench một buổi đầy đủ (10800 tick) qua headless và trong tiến trình.
- README: mục chạy, bảng phase, giới hạn, "Sáng tạo của nhóm".

### Phase 3 — change request (ADR-0001)
- `quan.burn_s`: `null` (mặc định, không cháy) hoặc số trong [1, 600]; món chín quá hạn → `dish_burnt`, bếp về `idle`.
- Nấu lại chỉ dùng phần kho không bị khách khác giữ chỗ.

### Phase 2
- `contract.py`: kiểm dải tuning quán (bếp/bàn, `carry_limit`, uy tín, công thức món, hệ số điểm).
- Cửa sổ chơi: HUD quán hiện khách đang ăn, giá + boa, bếp chín; test cửa sổ chế độ quan.

### Phase 1
- Gather: dive/surface, oxy, ngạt (`choke`), Máu, ngất (`faint`), hái nút + mọc lại, bắt cá + hồi chiêu, `hold_full`, kho khi `gather_end`.
- Quan: khách theo lịch, chọn món nấu được (RNG `customer_dish`), giữ chỗ, kiên nhẫn, `customer_left`, `no_dish`, nấu/chín/bưng/phục vụ, trả tiền, boa, uy tín, `quan_end`.
- `scenario.py`: kiểm mâu thuẫn mức luật cho khách/bếp/tay/uy tín (mã 2).
- QA: 72 test (hộp đen + unit), fixture tích hợp sáng → tối, `tools/proof.py`.
- Harness AI: skill `chonoi-rule-slice`, `chonoi-proof`; AGENTS.md cập nhật mỗi phase.

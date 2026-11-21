# ADR-0001: Món chín để lâu bị cháy (`burn_s`)

- Trạng thái: chấp nhận
- Ngày, người quyết: 2026-11-21 22:15, myblue-ai (Integrator)

## Bối cảnh
Phase 3 trên lịch board là change request. Nội dung Ticket-03 không đọc được bằng công cụ AI (clarify #13), nên nhóm lấy change request có căn cứ trong khung: `chonoi/contract.py` chặn `burn_s` với thông báo "burn_s phải là null ở Phase 1", và `game.contract.json` đã có khóa `quan.burn_s: null`. Tức là sẽ có phase cho món chín để trên bếp quá `burn_s` giây thì cháy. Cần làm sao để khi `burn_s = null` mọi output Phase 1–2 giữ nguyên từng byte (test ẩn kiểm lại phase trước).

## Các lựa chọn đã cân nhắc
1. **Bếp `ready` quá `burn_s` → món cháy, bếp về `idle`, nguyên liệu mất; khách vẫn đợi và có thể nấu lại nếu kho còn (phần không bị khách khác giữ chỗ).** Đơn giản, không thêm trạng thái mới vào hợp đồng snapshot.
2. Thêm trạng thái bếp `burnt` phải interact để dọn. Thêm một bước thao tác và một trạng thái mới cho UI/hợp đồng, rủi ro lệch hợp đồng `stoves[].state` lớn hơn.
3. Món cháy vẫn phục vụ được nhưng không có boa. Khó kiểm, đụng vào luật boa đã chốt (clarify #10).

## Quyết định
Chọn phương án 1. `burn_s` nhận `null` (tắt, mặc định, giữ hành vi P1) hoặc số trong `[1, 600]`. Mỗi tick bếp `ready` tăng `ready_ticks`; khi `ready_ticks ≥ round(burn_s × 60)` phát sự kiện `dish_burnt {stove_id, dish_id}`, bếp về `idle`. Nấu lại chỉ dùng phần kho không bị khách **khác** giữ chỗ.

## Hệ quả (bảng tác động)

| Thành phần | File | Thay đổi | Test bị ảnh hưởng |
|---|---|---|---|
| Hợp đồng tuning | `chonoi/contract.py` | `burn_s`: `null` hoặc số trong [1, 600] (trước: bắt buộc `null`) | `test_contract_rules.py` (thêm ca) |
| Hợp đồng sự kiện | `docs/contracts/README.md` | thêm `dish_burnt` | — |
| Luật quán | `chonoi/sim/quan.py` | `_tick_stoves` đốt món; `_use_stove` kiểm kho trừ phần khách khác giữ | `tests/test_burn_cr.py` (mới) |
| Dữ liệu | `game.contract.json` | **không đổi** (`burn_s: null`) → output headless giữ nguyên byte | so sha256 với `proof/phase-2` |
| UI | `chonoi/web/index.html` | không đổi (bếp về `idle` là trạng thái đã có; sự kiện hiện ở log) | — |
| Test cũ | `test_smoke_p1`, `test_quan_rules`, `test_integration_chain` | không sửa | phải xanh nguyên trạng |

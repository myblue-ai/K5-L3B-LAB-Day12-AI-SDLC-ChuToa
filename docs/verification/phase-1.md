# Ma trận truy vết Phase 1

Lịch giả định: Phase 1 20:15–21:15. Bằng chứng tạo bằng `python3 tools/proof.py 1` (skill `chonoi-proof`).
Mã AC: `CON/MOVE/INV` lấy theo tên test smoke của giảng viên; `G-*`, `Q-*` là mã nhóm tự đặt cho luật suy ra từ `TODO(nhóm)` vì PRD-0 không đọc được bằng công cụ AI (clarify #2).

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| CON-01 ticks 0 + dòng end | `test_smoke_p1.Contract.test_con_01_*` | [tests.txt](../proof/phase-1/tests.txt) | đạt |
| CON-02 cùng seed → cùng byte | smoke test + chạy 2 lần gather/quan seed 7, so sha256 | [determinism.txt](../proof/phase-1/determinism.txt) | đạt |
| CON-03 đầu vào sai → mã 2 | smoke test + `test_quan_rules.ScenarioConflicts` (8 kiểu mâu thuẫn) | [tests.txt](../proof/phase-1/tests.txt) | đạt |
| MOVE-01..03 bơi, hướng, chặn mép | smoke test (khung có sẵn, không đổi) | [tests.txt](../proof/phase-1/tests.txt) | đạt |
| INV-01 gather ghi kho, quan đọc kho | smoke test + chuỗi thật sáng → tối | [integration.txt](../proof/phase-1/integration.txt), [kho.json](../proof/phase-1/kho.json) | đạt |
| G-1 dive / surface | `test_gather_rules.Oxygen.test_dive_and_surface_events` | tests.txt | đạt |
| G-2 oxy trừ/hồi/kẹp, oxygen_empty | `test_oxygen_drains_*`, `test_oxygen_empty_then_choke` | tests.txt | đạt |
| G-3 ngạt → choke −1 Máu, nổi lên đếm lại | `test_oxygen_empty_then_choke`, `test_surface_resets_choke_counter` | tests.txt | đạt |
| G-4 Máu 0 → faint, gather_end fainted, kho rỗng | `test_faint_loses_hold_and_writes_empty_inventory` | tests.txt | đạt |
| G-5 hái nút gần nhất ở mặt nước, mọc lại | `Harvest.*` (5 test) | tests.txt | đạt |
| G-6 bắt cá dưới nước, hồi chiêu, hold_full | `Catch.*` (4 test) | tests.txt | đạt |
| Q-1 khách theo lịch, giữ chỗ, no_dish, kín bàn | `Customers.*` (7 test) | tests.txt | đạt |
| Q-2 kiên nhẫn hết → customer_left, uy tín kẹp | `test_customer_leaves_*`, `test_reputation_clamped_at_min` | tests.txt | đạt |
| Q-3 bếp: nấu, chín, bưng; ưu tiên bếp khi hòa | `Kitchen.*` (3 test) | tests.txt | đạt |
| Q-4 phục vụ, ăn, trả tiền, boa, uy tín, quan_end | `Service.*` (4 test) + chuỗi tích hợp (money 144, score 444) | tests.txt, integration.txt | đạt |
| TEAM danh sách thành viên hợp lệ | `python3 tools/check_team.py` | [check_team.txt](../proof/phase-1/check_team.txt) | **chưa đạt**: nhóm 1 người, script yêu cầu 4–6 (clarify #1) |

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt: toàn bộ test (64) xanh, tất định đạt, gather → kho → quan nối được. Chưa đạt: điều kiện 4–6 thành viên. Rủi ro lớn nhất: luật chi tiết là **giả định** (clarify #3–#12), có thể lệch PRD-0 thật nên test ẩn có thể trượt ở các điểm đó.
- Điều cần chỉnh cho phase sau: đối chiếu từng giả định với PRD-0 khi có bản đọc được; HUD trong cửa sổ thử chưa hiện trạng thái khách/tiền đầy đủ.

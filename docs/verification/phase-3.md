# Ma trận truy vết Phase 3 — change request

Lịch giả định: 22:10–22:45. Ticket-03 **chưa đối chiếu được** (clarify #13). Change request nhóm thực hiện: món cháy theo `burn_s` ([ADR-0001](../adr/0001-mon-chin-bi-chay-burn-s.md)); ADR + bảng tác động được commit **trước** commit sửa code (xem `git log`).
Bằng chứng: `python3 tools/proof.py 3`.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| CR-1 `burn_s` nhận `null` hoặc số trong [1, 600], ngoài dải → lỗi | `test_burn_cr.Burn.test_contract_accepts_null_or_range` | [tests.txt](../proof/phase-3/tests.txt) | đạt |
| CR-2 món `ready` đủ `burn_s` giây → `dish_burnt`, bếp `idle` | `test_ready_dish_burns_after_burn_s` (burn 2 s → cháy đúng tick 120) | tests.txt | đạt |
| CR-3 `burn_s = null` không bao giờ cháy | `test_null_never_burns` | tests.txt | đạt |
| CR-4 nấu lại sau khi cháy không lấy nguyên liệu khách khác giữ chỗ | `test_recook_after_burn_uses_free_stock_only` | tests.txt | đạt |
| Hồi quy P1–P2 | 72 test + sha256 tất định so với `proof/phase-2` | tests.txt, [determinism.txt](../proof/phase-3/determinism.txt), [integration.txt](../proof/phase-3/integration.txt) | đạt: sha256 giống hệt P2 |
| TEAM 4–6 người | `tools/check_team.py` | [check_team.txt](../proof/phase-3/check_team.txt) | chưa đạt (đã biết) |

## Đánh giá ngắn
- Đạt: change request có ADR và bảng tác động trước code, mặc định tắt, không đổi byte output cũ.
- Chưa đạt: chưa biết Ticket-03 thật có phải change request này không; UI chưa có hiệu ứng riêng cho món cháy (chỉ hiện trong log sự kiện).

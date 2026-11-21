# Ma trận truy vết Phase 2

Lịch giả định: 21:15–22:10. Ticket-02 **chưa đối chiếu được** (không đọc được bằng công cụ AI, clarify #13); các AC dưới đây là việc nhóm tự đặt trong `docs/plan/phase-2.md`.
Bằng chứng: `python3 tools/proof.py 2`.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| P2-1 tuning quán sai dải → mã 2 (bếp/bàn, carry_limit, uy tín, công thức, hệ số điểm) | `tests/test_contract_rules.py` (3 test) | [tests.txt](../proof/phase-2/tests.txt) | đạt |
| P2-2 cửa sổ chơi chế độ quan đọc kho, có khách, snapshot đủ trường UI | `tests/test_live_quan.py` | tests.txt | đạt |
| P2-3 HUD quán: đếm ngược khách ăn, giá + boa, bếp chín | chơi thử `python3 -m chonoi.live --mode quan --inventory docs/proof/phase-1/kho.json` | (kiểm bằng mắt; không có ảnh chụp) | đạt một phần: đã kiểm bằng mắt, chưa có ảnh làm bằng chứng |
| Smoke tích hợp phút 20 | chuỗi sáng → kho → tối | [integration.txt](../proof/phase-2/integration.txt) | đạt (money 144, score 444) |
| Hồi quy Phase 1 | toàn bộ test P1 + so sha256 tất định với `proof/phase-1` | tests.txt, [determinism.txt](../proof/phase-2/determinism.txt) | đạt: sha256 gather/quan **giống hệt** Phase 1 → Phase 2 không đổi hành vi headless |
| TEAM 4–6 người | `tools/check_team.py` | [check_team.txt](../proof/phase-2/check_team.txt) | chưa đạt (đã biết, clarify #1) |

## Đánh giá ngắn
- Đạt: 68 test xanh, output headless không đổi so với P1.
- Chưa đạt: chưa đối chiếu Ticket-02; HUD chỉ kiểm bằng mắt.
- Cần chỉnh phase sau: change request phải có ADR và bảng tác động trước khi sửa code.

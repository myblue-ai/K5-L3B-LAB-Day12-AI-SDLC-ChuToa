# Ma trận truy vết Phase 4

Lịch giả định: 22:45–23:15. Ticket-04 **chưa đối chiếu được** (clarify #13); AC theo lịch board: bench, đóng gói, release, retro.
Bằng chứng: `python3 tools/proof.py 4`, `python3 tools/bench.py`.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| P4-1 bench một buổi đầy đủ | `tools/bench.py`: 10800 tick, trung vị 3 lần, trong tiến trình và qua `headless_cmd` | [bench.txt](../proof/phase-4/bench.txt) | đạt: headless ~0,2–0,3 s/buổi (≈ 40–60 nghìn tick/s), nhanh hơn thời gian thực hàng trăm lần |
| P4-2 đóng gói: README chạy được, CHANGELOG, CREDITS | đọc lại README; clone sạch tại tag rồi chạy test | [tests.txt](../proof/phase-4/tests.txt); mục "Clone sạch" dưới đây | đạt |
| P4-3 hồi quy toàn bộ | 72 test + sha256 tất định so với phase 3 | tests.txt, [determinism.txt](../proof/phase-4/determinism.txt), [integration.txt](../proof/phase-4/integration.txt) | đạt |
| P4-4 retro cuối có số liệu, phản tư cá nhân | `docs/retro.md`, `docs/members/myblue-ai.md` | — | đạt |
| P4-5 tag `phase-4` + Release `v1.0.0` | `git tag` | — | tag tạo local; **Release trên GitHub chưa tạo** (máy không có `gh`, cần push rồi tạo bằng web) |
| TEAM 4–6 người | `tools/check_team.py` | [check_team.txt](../proof/phase-4/check_team.txt) | chưa đạt (đã biết) |

## Clone sạch
Ghi ở `docs/proof/phase-4/clean-clone.txt` (clone repo local tại commit cuối, chạy toàn bộ test).

## Đánh giá ngắn
- Đạt: mọi tag đều chạy được và xanh test; output headless giữ nguyên byte từ P1 tới P4.
- Chưa đạt: chưa đối chiếu PRD-0/ticket thật; nhóm 1 người; Release GitHub chờ push.

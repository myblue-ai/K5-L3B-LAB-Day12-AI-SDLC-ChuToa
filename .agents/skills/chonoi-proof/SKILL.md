---
name: chonoi-proof
description: Tạo bằng chứng thật cho một phase (test, tất định, chuỗi sáng -> kho -> tối, danh sách nhóm) rồi cập nhật verification. Dùng trước mỗi lần gắn tag phase-n.
---

# chonoi-proof

## Khi nào dùng
- Ngay trước khi gắn tag `phase-n`.
- Sau khi đổi luật trong `chonoi/sim/*` hoặc `game.contract.json` để chắc không phá phase trước.

## Các bước
1. Chạy `python3 tools/proof.py <n>` ở gốc repo. Script ghi vào `docs/proof/phase-<n>/`:
   `tests.txt`, `determinism.txt`, `integration.txt`, `kho.json`, `check_team.txt`, `SUMMARY.txt`.
2. Đọc `SUMMARY.txt`. Điều kiện để tag:
   - `tests: exit 0 … OK`
   - `determinism gather/quan: same bytes`
   - `integration: gather exit 0, quan exit 0`
   - `check_team` chỉ được báo lỗi "số thành viên" (đã biết, clarify #1).
3. Điền `docs/verification/phase-<n>.md`: mỗi AC một dòng, link tới đúng file proof, ghi **đạt / chưa đạt** trung thực.
4. Commit proof + verification, rồi `git tag phase-<n>`.

## Không được
- Không sửa tay file trong `docs/proof/` (bằng chứng phải là đầu ra thật).
- Không gắn tag khi `tests.txt` không OK.

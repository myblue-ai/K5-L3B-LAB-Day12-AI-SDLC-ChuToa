# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| 0 | myblue-ai | Claude Code (Claude Opus) | Đọc repo, chạy smoke test, tìm nguyên nhân 20 test lỗi trên Windows (`python3` không có trong PATH) | ~40k | Lần đầu AI tạo shim `python3` bằng bản sao exe của venv → vẫn lỗi; phát hiện do `PATH` kiểu `C:/...` trong Git Bash bị hiểu sai, sửa sang `/c/...`. |
| 1 | myblue-ai | Claude Code (Claude Opus) | Viết luật gather lát 1+2, test `test_gather_rules.py` | ~30k | Test kịch bản cả buổi sáng do AI tự đặt lộ trình input bị sai (không tới được đàn cá); phát hiện vì test đỏ, sửa bằng cách mô phỏng lộ trình qua `Session` rồi mới chép số vào test. |
| 1 | myblue-ai | Claude Code (Claude Opus) | Viết luật quan lát 3+4, kiểm mâu thuẫn scenario, test `test_quan_rules.py` | ~35k | 3 test đỏ: AI viết kịch bản "món đã trên tay" nhưng quên `reserved: {}` nên luật kiểm giữ chỗ (đúng) báo mã 2. Sửa kịch bản test, giữ luật; ghi clarify #12. |
| 1 | myblue-ai | Claude Code (Claude Opus) | `tools/proof.py`, fixture tích hợp, 2 skill, AGENTS.md | ~20k | `proof.py` lỗi `relpath` khi file tạm ở ổ C còn repo ở ổ E, và lỗi in tiếng Việt trên console cp1252; cả hai lộ ra khi chạy thật. |
| 1 | myblue-ai | (tự làm) | Đọc lại toàn bộ diff, đối chiếu từng giả định với TODO trong khung | — | AI không đọc được PRD-0 trên lab board (artifact ngoài tổ chức) → mọi luật chi tiết là giả định, đã ghi clarify #2–#12. |

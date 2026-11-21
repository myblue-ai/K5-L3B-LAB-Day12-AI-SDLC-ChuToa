# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| 0 | myblue-ai | Claude Code (Claude Opus) | Đọc repo, chạy smoke test, tìm nguyên nhân 20 test lỗi trên Windows (`python3` không có trong PATH) | ~40k | Lần đầu AI tạo shim `python3` bằng bản sao exe của venv → vẫn lỗi; phát hiện do `PATH` kiểu `C:/...` trong Git Bash bị hiểu sai, sửa sang `/c/...`. |
| 1 | myblue-ai | Claude Code (Claude Opus) | Viết luật gather lát 1+2, test `test_gather_rules.py` | ~30k | Test kịch bản cả buổi sáng do AI tự đặt lộ trình input bị sai (không tới được đàn cá); phát hiện vì test đỏ, sửa bằng cách mô phỏng lộ trình qua `Session` rồi mới chép số vào test. |
| 1 | myblue-ai | Claude Code (Claude Opus) | Viết luật quan lát 3+4, kiểm mâu thuẫn scenario, test `test_quan_rules.py` | ~35k | 3 test đỏ: AI viết kịch bản "món đã trên tay" nhưng quên `reserved: {}` nên luật kiểm giữ chỗ (đúng) báo mã 2. Sửa kịch bản test, giữ luật; ghi clarify #12. |
| 1 | myblue-ai | Claude Code (Claude Opus) | `tools/proof.py`, fixture tích hợp, 2 skill, AGENTS.md | ~20k | `proof.py` lỗi `relpath` khi file tạm ở ổ C còn repo ở ổ E, và lỗi in tiếng Việt trên console cp1252; cả hai lộ ra khi chạy thật. |
| 1 | myblue-ai | (tự làm) | Đọc lại toàn bộ diff, đối chiếu từng giả định với TODO trong khung | — | AI không đọc được PRD-0 trên lab board (artifact ngoài tổ chức) → mọi luật chi tiết là giả định, đã ghi clarify #2–#12. |
| 2 | myblue-ai | Claude Code (Claude Opus) | Kiểm dải tuning (`contract.py`), test cửa sổ quan, HUD quán | ~25k | `proof.py` ghi `check_team.txt` vỡ dấu tiếng Việt (tiến trình con in cp1252); phát hiện khi đọc lại file proof, sửa bằng `PYTHONIOENCODING=utf-8` cho tiến trình con. |
| 3 | myblue-ai | Claude Code (Claude Opus) | ADR-0001, cơ chế `burn_s`, test CR | ~20k | Bản đầu của `_use_stove` sau khi cháy kiểm `stock ≥ công thức` nên sẽ lấy cả nguyên liệu khách khác đã giữ chỗ; phát hiện khi viết bảng tác động trong ADR, thêm test `test_recook_after_burn_uses_free_stock_only` rồi sửa. |
| 4 | myblue-ai | Claude Code (Claude Opus) | `tools/bench.py`, README, CHANGELOG, CREDITS, retro, phản tư | ~20k | Bench ghi chú dòng quan là "gather tự kết thúc" (chép nhầm từ dòng gather); phát hiện khi đọc bảng in ra, sửa trước khi lưu bằng chứng. |

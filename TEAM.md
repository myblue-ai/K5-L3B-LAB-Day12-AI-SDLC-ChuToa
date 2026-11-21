# TEAM

**Tên nhóm:** ChuToa  **Số người:** 1  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Đào Hồng Thắng | myblue-ai | `sim/gather`, `sim/quan`, `client/ui`, `qa` | PO · Integrator · QA lead · Scrum/Release | (làm một mình, không có dự phòng) |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Một người kiêm cả bốn vai.

> Nhóm chỉ có 1 người nên `tools/check_team.py` báo "số thành viên phải từ 4 đến 6". Đây là sai lệch đã biết, ghi ở `docs/clarify.md` (#1) và trong bằng chứng từng phase.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: không cần kênh nhóm; câu hỏi cho PO/giảng viên ghi vào `docs/clarify.md`.
- Khi bất đồng về thiết kế: tự quyết trong 2 phút, ghi lý do vào `docs/clarify.md` hoặc ADR.
- Khi vướng quá 10 phút: ghi giả định hợp lý vào `docs/clarify.md`, làm tiếp, quay lại sau.
- Giờ standup giữa phase: giữa mỗi phase, một dòng trong `docs/standup.md`.
- Cách đọc code: AI agent viết một lát → tôi đọc diff và chạy test trước khi commit; ghi lại vào `docs/ai-usage-log.md`.
- Cách làm việc với Git: commit nhỏ thẳng vào `main`, chỉ commit khi test xanh; tôi gắn tag `phase-n` cuối mỗi phase.

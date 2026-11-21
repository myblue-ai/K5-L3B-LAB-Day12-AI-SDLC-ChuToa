# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Headless: `python3 -m chonoi.headless --mode gather|quan --seed 1 --ticks 600 --out out.jsonl`
- Chơi thử trên trình duyệt: `python3 -m chonoi.live --mode gather|quan` (mở địa chỉ in ra; WASD, E, Space, R)
- Bằng chứng một phase: `python3 tools/proof.py <n>` → `docs/proof/phase-<n>/` (xem skill `chonoi-proof`)
- Chuỗi sáng → tối thủ công: `python3 -m chonoi.headless --mode gather --seed 1 --ticks 10800 --inputs tests/fixtures/morning.inputs.json --inventory-out kho.json --out g.jsonl` rồi `--mode quan --inventory kho.json --inputs tests/fixtures/evening.inputs.json`
- Windows: không có `python3` → tạo bản sao `python3.exe` cạnh `python.exe` (không đổi `headless_cmd`, máy chấm chạy Linux); PowerShell dùng `$env:PYTHONPATH = "tests;."`

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py`; thứ tự một bước ghi ở docstring đầu mỗi file. Giả định luật: `docs/clarify.md`. Tên sự kiện/trường: `docs/contracts/README.md`.
- Test luật của nhóm: `tests/test_gather_rules.py`, `tests/test_quan_rules.py`, `tests/test_integration_chain.py` (hộp đen qua `headless_cmd`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- `chonoi-rule-slice` (`.agents/skills/chonoi-rule-slice/SKILL.md`): giao cho agent khi viết một lát luật mới; bắt buộc ghi giả định trước, test hộp đen sau.
- `chonoi-proof` (`.agents/skills/chonoi-proof/SKILL.md`) + script `tools/proof.py`: chạy trước mỗi tag để tạo bằng chứng thật và điền verification.

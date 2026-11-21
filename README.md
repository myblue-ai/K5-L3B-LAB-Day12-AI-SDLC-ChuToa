# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

```bash
git clone <fork-của-nhóm> && cd <fork-của-nhóm>
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v        # smoke test
python3 -m chonoi.live --mode gather                                # chơi thử trên trình duyệt (tùy chọn)
```

Game cần chế độ **headless** theo Test Contract (`python3 -m chonoi.headless --mode gather|quan …`) để được chạy và chấm tự động. **Công nghệ không ràng buộc**: khung Python trong `chonoi/` chỉ là gợi ý, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.

---

# Bản nộp của nhóm ChuToa (v1.0.0)

**Nhóm:** 1 người, Đào Hồng Thắng ([@myblue-ai](https://github.com/myblue-ai)); xem [`TEAM.md`](TEAM.md). Công nghệ: starter Python 3 (chỉ thư viện chuẩn), giữ nguyên Test Contract v1.0.

## Chạy

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v          # 72 test
python3 -m chonoi.headless --mode gather --seed 1 --ticks 10800   --inputs tests/fixtures/morning.inputs.json --inventory-out kho.json --out g.jsonl
python3 -m chonoi.headless --mode quan --seed 1 --ticks 1600 --inventory kho.json   --inputs tests/fixtures/evening.inputs.json --out q.jsonl
python3 -m chonoi.live --mode gather --inventory-out kho.json        # chơi buổi sáng
python3 -m chonoi.live --mode quan --inventory kho.json              # chơi buổi tối
python3 tools/proof.py 4     # bằng chứng: test, tất định, chuỗi sáng → tối
python3 tools/bench.py       # bench một buổi đầy đủ
```

Windows: không có lệnh `python3` thì tạo bản sao `python3.exe` cạnh `python.exe` (không đổi `headless_cmd`); PowerShell đặt `$env:PYTHONPATH = "tests;."`.

## Đã làm theo phase

| Tag | Nội dung | Bằng chứng |
|---|---|---|
| `phase-1` | Luật gather (oxy, ngạt, Máu, ngất, hái, bắt cá, giỏ) + quan (khách, giữ chỗ, bếp, bưng, phục vụ, tiền, boa, uy tín) + kho | [`docs/verification/phase-1.md`](docs/verification/phase-1.md) |
| `phase-2` | Kiểm dải tuning quán, test cửa sổ quan, HUD quán | [`docs/verification/phase-2.md`](docs/verification/phase-2.md) |
| `phase-3` | Change request: món cháy `burn_s` ([ADR-0001](docs/adr/0001-mon-chin-bi-chay-burn-s.md)) | [`docs/verification/phase-3.md`](docs/verification/phase-3.md) |
| `phase-4` / `v1.0.0` | Bench, đóng gói, retro | [`docs/verification/phase-4.md`](docs/verification/phase-4.md) |

**Giới hạn cần biết:** nội dung PRD-0 và Ticket-02/03/04 trên lab board không đọc được bằng công cụ AI của nhóm. Luật chi tiết là giả định ghi ở [`docs/clarify.md`](docs/clarify.md) (#2–#13); hidden test có thể lệch ở các điểm đó.

## Sáng tạo của nhóm

Chưa thêm nhân vật, món hay cơ chế ngoài đề: nhóm 1 người ưu tiên làm lõi đúng trước. Phần thêm duy nhất là HUD quán trong cửa sổ thử (đếm ngược khách đang ăn, giá + boa, nhãn "chín · E để bưng"), chỉ nằm ở `chonoi/web/index.html`, không ảnh hưởng headless.

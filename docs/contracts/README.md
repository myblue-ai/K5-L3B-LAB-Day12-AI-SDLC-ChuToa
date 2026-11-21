# Hợp đồng tích hợp (chốt lúc kickoff Phase 1, 20:15)

Khi đổi hợp đồng sau này: ghi lý do (ADR hoặc `docs/clarify.md`) trước khi sửa code.

## 1. Schema file kho (Contract G, v1.0)

```json
{"items": {"<nguyên liệu>": <số nguyên > 0>}}
```

- Khóa gốc duy nhất `items`. Nguyên liệu hợp lệ: `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`.
- Mục có số lượng 0 bị bỏ khi ghi; khóa sắp theo bảng chữ cái; một dòng, kết thúc `\n`.
- Gather ghi kho **đúng một lần** khi có `gather_end` (`docked` hoặc `time`: giữ giỏ; `fainted`: kho rỗng `{"items":{}}`). Hết `--ticks` trước `gather_end` thì không ghi.
- Quan đọc kho bằng `--inventory` (không được dùng cùng `quan.stock` trong scenario).
- File mẫu hợp lệ: [`inventory.sample.json`](inventory.sample.json).

## 2. Giao diện `sim/*` ↔ `client/ui`

UI (`chonoi/live.py` + `chonoi/web/index.html`) **chỉ đọc snapshot**, không gọi vào sim. UI gửi vào đúng hai thứ: `move` (vector, chuẩn hóa) và nút `interact` / `catch` (cạnh lên).

| Mode | Trường snapshot UI đọc |
|---|---|
| chung | `tick`, `time_left_ticks`, `money`, `earned`, `reputation`, `score`, `state` |
| gather | `player.{pos, vel, heading_deg, oxygen_ticks, oxygen_max_ticks, hp, hp_max, zero_oxy_ticks, invuln_ticks, catch_cd_ticks, at_surface}`, `hold` (mảng theo thứ tự nhặt), `hold_count`, `hold_capacity`, `nodes[].{id, kind, pos, ready, regrow_ticks}`, `fish[].{id, kind, pos, heading_deg}` |
| quan | `player.pos`, `stock`, `hand` (id món hoặc `null`), `stoves[].{id, pos, state: idle/cooking/ready, dish, cook_ticks_left, ready_ticks}`, `tables[].{id, pos, customer_id}`, `customers[].{id, table_id, dish_id, state: waiting/eating, patience_ticks_left, reserved, eat_ticks_left, price, tip}` |

## 3. Danh sách sự kiện

Dòng event: `{"type":"event","tick":k+1,"phase":...,"name":...,"data":{...}}`; trong một bước, sự kiện ghi theo thứ tự xử lý.

### Gather (phát bởi `sim/gather.py`)

| Tên | data | Khi nào |
|---|---|---|
| `node_regrown` | `{node_id}` | nút đếm ngược mọc lại về 0 |
| `dive` | `{pos}` | đầu bước ở mặt nước (`d ≤ surface_depth`), cuối bước dưới nước |
| `surface` | `{pos}` | ngược lại |
| `oxygen_empty` | `{}` | oxy từ dương về 0 |
| `choke` | `{hp}` | đủ `choke_interval_ticks` tick oxy = 0 dưới nước; `hp` là Máu sau khi trừ |
| `faint` | `{pos}` | Máu về 0 (ngay sau đó là `gather_end` reason `fainted`) |
| `gather` | `{node_id, kind, count}` | hái nút thành công |
| `fish_caught` | `{fish_id, kind, count}` | bắt đàn cá thành công |
| `hold_full` | `{source, kind, need, free}` | giỏ không đủ chỗ cho toàn bộ sản lượng; `source` là id nút hoặc id đàn cá |
| `gather_end` | `{reason: docked/time/fainted, inventory: {items}}` | kết thúc buổi sáng |

### Quan (phát bởi `sim/quan.py`)

| Tên | data | Khi nào |
|---|---|---|
| `customer_arrived` | `{customer_id, table_id, dish_id}` | khách tới theo lịch, có bàn trống và có món nấu được |
| `no_dish` | `{table_id}` | tới lượt khách, có bàn trống nhưng kho không đủ cho món nào |
| `customer_left` | `{customer_id, table_id, dish_id, reputation}` | khách hết kiên nhẫn |
| `cook_started` | `{stove_id, dish_id, customer_id}` | interact bếp rảnh khi có đơn chưa nấu |
| `dish_ready` | `{stove_id, dish_id}` | bếp nấu xong |
| `dish_picked` | `{stove_id, dish_id}` | interact bếp `ready`, tay trống |
| `dish_burnt` | `{stove_id, dish_id}` | chỉ khi `burn_s` khác `null`: món chín nằm trên bếp đủ `burn_s` giây; bếp về `idle` (ADR-0001, Phase 3) |
| `served` | `{customer_id, table_id, dish_id}` | interact bàn, món trên tay đúng món khách gọi |
| `paid` | `{customer_id, price, tip, money, reputation}` | khách ăn xong |
| `quan_end` | `{reason: time, money, earned, shift_earned, reputation}` | hết ca |

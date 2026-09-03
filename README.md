# AUTO BTĐ Thần Long v1.0

AUTO BTĐ là một vòng điều phối duy nhất: **Auto Trừng Ác → nhận Bảo Tàng Đồ → tự dùng/xử lý Bảo Tàng Đồ**.

## Nền được giữ
- Nền kỹ thuật v4.9: route, toàn bộ đường tắt, logic lên/xuống ngựa, Travel Fight Guard, revive/Đầu thai và Bridge theo từng PID.
- Quản lý acc theo thiết kế 9.9: tối đa 30 client, CHỌN TẤT CẢ/BỎ TẤT CẢ, PT1..PT30, PID thu gọn mặc định.

## Feature duy nhất
- Tự tới Ngô Giới NPC 698 / Tô Châu M4 bằng runtime `GetNPCPosition` khi có.
- Dynamic dialog cho nhận/trả Trừng Ác; không hardcode selection ID.
- Discover TaskID runtime qua `GetDoingTasks` diff; không hardcode TaskID Trừng Ác.
- Kill/Loot objective dùng semantic monster + AutoFight primitive nội bộ.
- Tự CompleteNPC, trả nhiệm vụ, nhận thưởng và lặp.
- Scan `ItemID 30000000`, dùng đúng live instance bằng `CMD_ITEM_ACTION 100005`, payload `3:instanceID`.
- Sau Use, phân loại runtime theo Task mới / MoveDestination mới / world-object mới, rồi dùng route v4.9 để đi và tương tác.

## Đã loại khỏi scheduler/UI gameplay
Auto Dồn đồ, Auto Train độc lập, Auto PK và Auto Phó Bản không còn được tick trong sản phẩm v1.0. AutoFight chỉ còn là primitive nội bộ khi Trừng Ác hoặc Travel Guard cần.

## Guard quan trọng
- `ItemID 30000000` được bảo vệ khỏi các nhánh Sell/Drop cũ.
- Một mutable action/PID.
- Không coi 23 `AutoPath Item` candidates là tọa BTĐ khi chưa có runtime evidence.
- Request gửi thành công không được coi là success nếu chưa có proof/state mới.

## Runtime boundary
GitData đã khóa identity + exact Use action của Bảo Tàng Đồ, nhưng chưa chứng minh tĩnh `ScriptID 21001` tạo Task, MoveDestination, Dialog hay Object nào trên server live. v1.0 có post-Use classifier; nếu item đã consume mà không thấy state semantic mới, acc dừng fail-closed với `TREASURE_POST_STATE_UNKNOWN` thay vì đoán tọa.

## File build
GitHub Actions sẽ xuất vào `dist/`:
- `AUTO_BTD_v1.0.exe`
- `ThanLongCleanRouteBridge.dll`
- `AUTO_BTD_v1.0_Windows_x64.zip`
- `AUTO_BTD_v1.0_source.zip`
- `SHA256SUMS.txt`

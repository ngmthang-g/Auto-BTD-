from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'work').resolve()

def read(rel):
    return (root / rel).read_text(encoding='utf-8-sig').replace('\r\n','\n')

def write(rel, text):
    (root / rel).write_text(text, encoding='utf-8')

def repl(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 anchor, found {n}')
    return text.replace(old, new, 1)

p = 'src/controller.cpp'
s = read(p)

s = repl(s,
'''constexpr int IDC_BTD_PARTY = 218;\nconstexpr int IDC_BTD_ASSIGN_PARTY = 219;\n''',
'''constexpr int IDC_BTD_PARTY = 218;\nconstexpr int IDC_BTD_ASSIGN_PARTY = 219;\nconstexpr int IDC_BTD_DRAG_CAPTURE_START = 220;\nconstexpr int IDC_BTD_DRAG_CAPTURE_END = 221;\nconstexpr int IDC_BTD_DRAG_TEST = 222;\n''', 'btd drag control ids')

s = repl(s,
'''        if (enableShortcut_) { SetWindowPos(enableShortcut_, nullptr, 331, 480, 135, 27, SWP_NOZORDER); SetText(enableShortcut_, L"BẬT ĐƯỜNG TẮT"); }\n        if (shortcutSettingsButton_) { SetWindowPos(shortcutSettingsButton_, nullptr, 474, 480, 180, 27, SWP_NOZORDER); SetText(shortcutSettingsButton_, L"CẤU HÌNH ĐƯỜNG TẮT"); }\n        if (logCaption_) { SetWindowPos(logCaption_, nullptr, 18, 515, 1005, 22, SWP_NOZORDER); SetText(logCaption_, L"NHẬT KÝ AUTO BTĐ / RUNTIME PROOF"); }\n        if (log_) SetWindowPos(log_, nullptr, 18, 540, 1005, 390, SWP_NOZORDER);\n\n        for (HWND h : {tradeStatus_, clientList_, btdSelectAllButton_, btdClearAllButton_, btdPartyLabel_, btdPartyCombo_,\n                       btdAssignPartyButton_, scanButton_, startCheckedButton_, stopCheckedButton_, selected_, live_,\n                       enableRevive_, enableConfirm_, enableShortcut_, shortcutSettingsButton_, logCaption_, log_}) {\n''',
'''        if (enableShortcut_) { SetWindowPos(enableShortcut_, nullptr, 331, 480, 135, 27, SWP_NOZORDER); SetText(enableShortcut_, L"BẬT ĐƯỜNG TẮT"); }\n        if (shortcutSettingsButton_) { SetWindowPos(shortcutSettingsButton_, nullptr, 474, 480, 180, 27, SWP_NOZORDER); SetText(shortcutSettingsButton_, L"CẤU HÌNH ĐƯỜNG TẮT"); }\n\n        btdDragStartButton_ = Make(L"BUTTON", L"F8 ĐIỂM ĐẦU", BS_PUSHBUTTON, 664, 480, 108, 27, IDC_BTD_DRAG_CAPTURE_START); setFont(btdDragStartButton_);\n        btdDragEndButton_ = Make(L"BUTTON", L"F8 ĐIỂM CUỐI", BS_PUSHBUTTON, 780, 480, 108, 27, IDC_BTD_DRAG_CAPTURE_END); setFont(btdDragEndButton_);\n        btdDragTestButton_ = Make(L"BUTTON", L"TEST VUỐT", BS_PUSHBUTTON, 896, 480, 127, 27, IDC_BTD_DRAG_TEST); setFont(btdDragTestButton_);\n        btdDragTestLabel_ = Make(L"STATIC", L"VUỐT TEST: START chưa lấy → END chưa lấy", SS_LEFT | SS_CENTERIMAGE | WS_BORDER, 18, 515, 1005, 24, 0); setFont(btdDragTestLabel_);\n        UpdateBtdDragTestLabel();\n\n        if (logCaption_) { SetWindowPos(logCaption_, nullptr, 18, 546, 1005, 22, SWP_NOZORDER); SetText(logCaption_, L"NHẬT KÝ AUTO BTĐ / RUNTIME PROOF"); }\n        if (log_) SetWindowPos(log_, nullptr, 18, 571, 1005, 359, SWP_NOZORDER);\n\n        for (HWND h : {tradeStatus_, clientList_, btdSelectAllButton_, btdClearAllButton_, btdPartyLabel_, btdPartyCombo_,\n                       btdAssignPartyButton_, scanButton_, startCheckedButton_, stopCheckedButton_, selected_, live_,\n                       enableRevive_, enableConfirm_, enableShortcut_, shortcutSettingsButton_, btdDragStartButton_,\n                       btdDragEndButton_, btdDragTestButton_, btdDragTestLabel_, logCaption_, log_}) {\n''', 'btd drag test ui')

anchor = '''    void BtdSelectAll(bool checked) {\n        const int count = ListView_GetItemCount(clientList_);\n        for (int i = 0; i < count; ++i) ListView_SetCheckState(clientList_, i, checked ? TRUE : FALSE);\n    }\n\n'''
insert = anchor + r'''    void UpdateBtdDragTestLabel() {
        if (!btdDragTestLabel_) return;
        const std::wstring start = btdDragTestStart_.valid ? PointDescription(btdDragTestStart_) : L"CHƯA LẤY";
        const std::wstring end = btdDragTestEnd_.valid ? PointDescription(btdDragTestEnd_) : L"CHƯA LẤY";
        SetText(btdDragTestLabel_, L"VUỐT TEST • START " + start + L"  →  END " + end +
                                   L" • 12 điểm nội suy • chuột Windows không di chuyển");
    }

    void BeginBtdDragCapture(bool startPoint) {
        Account* a = nullptr;
        if (startPoint) {
            a = SelectedAccount();
            if (!a) { Log(L"TEST VUỐT: chọn acc cần test trước."); return; }
            btdDragTestStart_ = {};
            btdDragTestEnd_ = {};
            btdDragTestPid_ = 0;
        } else {
            if (!btdDragTestStart_.valid || btdDragTestPid_ == 0) {
                Log(L"TEST VUỐT: phải lấy F8 ĐIỂM ĐẦU trước.");
                return;
            }
            a = AccountByPid(btdDragTestPid_);
            if (!a || !IsWindow(a->game.window)) {
                Log(L"TEST VUỐT: client đã lấy điểm đầu không còn tồn tại; lấy lại START.");
                btdDragTestStart_ = {}; btdDragTestEnd_ = {}; btdDragTestPid_ = 0;
                UpdateBtdDragTestLabel();
                return;
            }
        }

        captureSlot_ = ClickSlot::None;
        captureMacroIndex_ = -1;
        captureTradeSequenceIndex_ = -1;
        captureTradeSequenceMode_ = 0;
        captureTradeSequenceMainRef_ = -1;
        capturePkStepIndex_ = -1;
        capturePkClickIndex_ = -1;
        shortcutKunlunCaptureIndex_ = -1;
        btdDragCaptureMode_ = startPoint ? 1 : 2;
        capturePid_ = a->game.pid;
        LogAccount(*a, startPoint
            ? L"TEST VUỐT • đưa chuột vào ĐIỂM BẮT ĐẦU trong tay nải rồi nhấn F8."
            : L"TEST VUỐT • đưa chuột vào ĐIỂM KẾT THÚC rồi nhấn F8.");
        SetText(selected_, startPoint
            ? L"TEST VUỐT • CHỜ F8 ĐIỂM ĐẦU"
            : L"TEST VUỐT • CHỜ F8 ĐIỂM CUỐI");
        UpdateBtdDragTestLabel();
    }

    void TestBtdHiddenDrag() {
        if (!btdDragTestStart_.valid || !btdDragTestEnd_.valid || btdDragTestPid_ == 0) {
            Log(L"TEST VUỐT: chưa đủ START + END. Bấm F8 ĐIỂM ĐẦU, F8 ĐIỂM CUỐI trước.");
            return;
        }
        Account* a = AccountByPid(btdDragTestPid_);
        if (!a || !IsWindow(a->game.window)) {
            Log(L"TEST VUỐT: client dùng để lấy START/END đã mất.");
            return;
        }
        if (a->runtime.running || a->dungeonOwned) {
            LogAccount(*a, L"TEST VUỐT bị chặn: dừng AUTO/Phó bản trên acc này trước để không chồng mutable action.");
            return;
        }
        if (btdDragTestStart_.baseW != btdDragTestEnd_.baseW ||
            btdDragTestStart_.baseH != btdDragTestEnd_.baseH) {
            LogAccount(*a, L"TEST VUỐT bị chặn: START/END lấy ở hai client-size khác nhau; lấy lại cả hai điểm.");
            return;
        }

        std::wstring error;
        if (!EnsureAttach(*a, error)) {
            LogAccount(*a, L"TEST VUỐT ATTACH FAIL • " + error);
            return;
        }
        int sx = 0, sy = 0, ex = 0, ey = 0;
        if (!NormalizeClickPointForBridge(a->game, btdDragTestStart_, sx, sy, error) ||
            !NormalizeClickPointForBridge(a->game, btdDragTestEnd_, ex, ey, error)) {
            LogAccount(*a, L"TEST VUỐT SCALE FAIL • " + error);
            return;
        }
        const int packedEnd = ((ex & 0xffff) << 16) | (ey & 0xffff);
        Response response{};
        if (!a->bridge.Call(Command::DragInternalPoint, sx, sy, packedEnd, response, error, 2600)) {
            LogAccount(*a, L"TEST VUỐT FAIL • " + error);
            return;
        }
        LogAccount(*a, L"TEST VUỐT PASS • " + PointDescription(btdDragTestStart_) + L" → " +
                       PointDescription(btdDragTestEnd_) +
                       L" • TryClickUI → UpdateUIDrag x12 → EndUIDrag • không chiếm chuột Windows");
    }

'''
s = repl(s, anchor, insert, 'btd drag methods')

s = repl(s,
'''        const bool hasMode = shortcutKunlunCaptureIndex_ >= 0 || captureSlot_ != ClickSlot::None || captureMacroIndex_ >= 0 ||\n                             captureTradeSequenceIndex_ >= 0 || capturePkClickIndex_ >= 0;\n''',
'''        const bool hasMode = btdDragCaptureMode_ != 0 || shortcutKunlunCaptureIndex_ >= 0 || captureSlot_ != ClickSlot::None || captureMacroIndex_ >= 0 ||\n                             captureTradeSequenceIndex_ >= 0 || capturePkClickIndex_ >= 0;\n''', 'capture hasMode')

s = repl(s,
'''            capturePkStepIndex_ = -1; capturePkClickIndex_ = -1; shortcutKunlunCaptureIndex_ = -1;\n            return;\n''',
'''            capturePkStepIndex_ = -1; capturePkClickIndex_ = -1; shortcutKunlunCaptureIndex_ = -1; btdDragCaptureMode_ = 0;\n            return;\n''', 'capture invalid reset')

s = repl(s,
'''        const ClickPoint captured{client.x, client.y, width, height, true};\n        if (shortcutKunlunCaptureIndex_ >= 0 && shortcutKunlunCaptureIndex_ < 3) {\n''',
'''        const ClickPoint captured{client.x, client.y, width, height, true};\n        if (btdDragCaptureMode_ == 1) {\n            btdDragTestStart_ = captured;\n            btdDragTestEnd_ = {};\n            btdDragTestPid_ = captureAccount->game.pid;\n            UpdateBtdDragTestLabel();\n            LogAccount(*captureAccount, L"TEST VUỐT F8 START = " + PointDescription(captured));\n            SetText(selected_, L"ĐÃ LẤY START • bấm F8 ĐIỂM CUỐI rồi đưa chuột tới điểm cuối");\n        } else if (btdDragCaptureMode_ == 2) {\n            if (!btdDragTestStart_.valid || btdDragTestPid_ != captureAccount->game.pid) {\n                LogAccount(*captureAccount, L"TEST VUỐT F8 END bị từ chối: START không thuộc client này.");\n                return;\n            }\n            btdDragTestEnd_ = captured;\n            UpdateBtdDragTestLabel();\n            LogAccount(*captureAccount, L"TEST VUỐT F8 END = " + PointDescription(captured));\n            SetText(selected_, L"ĐỦ START + END • bấm TEST VUỐT");\n        } else if (shortcutKunlunCaptureIndex_ >= 0 && shortcutKunlunCaptureIndex_ < 3) {\n''', 'capture drag branch')

s = repl(s,
'''        capturePkStepIndex_ = -1; capturePkClickIndex_ = -1; shortcutKunlunCaptureIndex_ = -1;\n    }\n\n    bool DispatchInternalPointActionDirect''',
'''        capturePkStepIndex_ = -1; capturePkClickIndex_ = -1; shortcutKunlunCaptureIndex_ = -1; btdDragCaptureMode_ = 0;\n    }\n\n    bool DispatchInternalPointActionDirect''', 'capture final reset')

s = repl(s,
'''                    case IDC_BTD_ASSIGN_PARTY:\n                        if (HIWORD(wp) == BN_CLICKED) BtdAssignPartyToChecked();\n                        break;\n                    case IDC_START_CHECKED:\n''',
'''                    case IDC_BTD_ASSIGN_PARTY:\n                        if (HIWORD(wp) == BN_CLICKED) BtdAssignPartyToChecked();\n                        break;\n                    case IDC_BTD_DRAG_CAPTURE_START:\n                        if (HIWORD(wp) == BN_CLICKED) BeginBtdDragCapture(true);\n                        break;\n                    case IDC_BTD_DRAG_CAPTURE_END:\n                        if (HIWORD(wp) == BN_CLICKED) BeginBtdDragCapture(false);\n                        break;\n                    case IDC_BTD_DRAG_TEST:\n                        if (HIWORD(wp) == BN_CLICKED) TestBtdHiddenDrag();\n                        break;\n                    case IDC_START_CHECKED:\n''', 'wm command btd drag')

s = repl(s,
'''    HWND autoPkStatus_ = nullptr;\n''',
'''    HWND btdDragStartButton_ = nullptr;\n    HWND btdDragEndButton_ = nullptr;\n    HWND btdDragTestButton_ = nullptr;\n    HWND btdDragTestLabel_ = nullptr;\n    ClickPoint btdDragTestStart_{};\n    ClickPoint btdDragTestEnd_{};\n    DWORD btdDragTestPid_ = 0;\n    int btdDragCaptureMode_ = 0; // 0=off, 1=START, 2=END\n\n    HWND autoPkStatus_ = nullptr;\n''', 'btd drag members')

s = s.replace('AUTO BTĐ Thần Long v1.2', 'AUTO BTĐ Thần Long v1.2.1')
s = s.replace('AUTO BTĐ v1.1.1 • TRỪNG ÁC → BẢO TÀNG ĐỒ', 'AUTO BTĐ v1.2.1 • TRỪNG ÁC → BẢO TÀNG ĐỒ')
write(p, s)

p = 'VERSION.txt'; write(p, '1.2.1\n')
p = 'CMakeLists.txt'; s = read(p)
s = repl(s, 'project(AutoBTD VERSION 1.2 LANGUAGES CXX RC)', 'project(AutoBTD VERSION 1.2.1 LANGUAGES CXX RC)', 'cmake version')
s = repl(s, 'OUTPUT_NAME "AUTO_BTD_v1.2"', 'OUTPUT_NAME "AUTO_BTD_v1.2.1"', 'cmake output')
write(p, s)
p = 'resources/app.rc'; s = read(p)
s = repl(s, 'FILEVERSION 1,2,0,0', 'FILEVERSION 1,2,1,0', 'fileversion')
s = repl(s, 'PRODUCTVERSION 1,2,0,0', 'PRODUCTVERSION 1,2,1,0', 'productversion')
s = s.replace('VALUE "FileVersion", "1.2\\0"', 'VALUE "FileVersion", "1.2.1\\0"')
s = s.replace('VALUE "ProductVersion", "1.2\\0"', 'VALUE "ProductVersion", "1.2.1\\0"')
s = repl(s, 'AUTO_BTD_v1.2.exe', 'AUTO_BTD_v1.2.1.exe', 'original filename')
write(p, s)

p='CHANGELOG.md'; s=read(p)
write(p, '# v1.2.1 - Hidden drag F8 test\n\n- Thêm F8 ĐIỂM ĐẦU, F8 ĐIỂM CUỐI và TEST VUỐT trực tiếp trên UI AUTO BTĐ.\n- START/END được lưu theo client-coordinate + BaseW/BaseH của đúng PID đã chọn.\n- TEST gọi cùng primitive `DragInternalPoint` mà AUTO Trừng Ác dùng: `TryClickUI -> UpdateUIDrag x12 -> EndUIDrag`; không di chuyển chuột Windows.\n- TEST fail-closed nếu AUTO đang chạy, PID đã mất, thiếu điểm, hoặc hai điểm được lấy ở hai client-size khác nhau.\n\n' + s)

p='README.md'; s=read(p)
write(p, s + '\n\n## v1.2.1 - TEST VUỐT F8\nChọn một acc, bấm **F8 ĐIỂM ĐẦU** rồi đưa chuột tới điểm bắt đầu và nhấn F8; bấm **F8 ĐIỂM CUỐI** rồi đưa chuột tới điểm cuối và nhấn F8; cuối cùng bấm **TEST VUỐT**. Tool scale hai điểm theo client hiện tại và chạy cùng hidden drag InputSync 12 bước dùng trong AUTO Trừng Ác.\n')

p='tools/verify_btd_v1.py'; s=read(p)
s=s.replace("assert version == '1.2', version", "assert version == '1.2.1', version")
s=s.replace("assert 'project(AutoBTD VERSION 1.2' in cmake", "assert 'project(AutoBTD VERSION 1.2.1' in cmake")
s=s.replace("assert 'OUTPUT_NAME \"AUTO_BTD_v1.2\"' in cmake", "assert 'OUTPUT_NAME \"AUTO_BTD_v1.2.1\"' in cmake")
s += "\nassert 'IDC_BTD_DRAG_CAPTURE_START = 220' in controller\nassert 'IDC_BTD_DRAG_CAPTURE_END = 221' in controller\nassert 'IDC_BTD_DRAG_TEST = 222' in controller\nassert 'BeginBtdDragCapture(true)' in controller\nassert 'BeginBtdDragCapture(false)' in controller\nassert 'TestBtdHiddenDrag()' in controller\nassert 'btdDragCaptureMode_ != 0' in controller\nassert 'TEST VUỐT PASS' in controller\nassert 'Command::DragInternalPoint' in controller\nprint('AUTO BTD v1.2.1 F8 hidden drag test contracts PASS')\n"
write(p,s)

print('AUTO BTD v1.2.1 F8 drag test patch applied')

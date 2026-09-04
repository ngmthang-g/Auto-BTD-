from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'work').resolve()

def read(path):
    return path.read_text(encoding='utf-8-sig')

def write(path, text):
    path.write_text(text, encoding='utf-8-sig')

def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly 1 match, found {count}')
    return text.replace(old, new, 1)

# 1) Restore proven startup ownership: a bag item is not enough proof to skip Ngô Giới.
p = root / 'src' / 'controller.cpp'
s = read(p)
old = '''            // Real client flow (Lỗi.docx): Ngô Giới gives a Trừng Ác Lệnh first.\n            // If AUTO starts mid-round, resume from the live order instead of inventing a fixed TaskID.\n            std::vector<InventoryBagRow> orderRows; int orderCount = 0; std::int64_t orderInstance = 0;\n            std::wstring orderError;\n            if (BtdScanTrungAcOrderBag(a, orderRows, orderCount, orderInstance, orderError) && orderCount > 0) {\n                btd.pendingTurnIn = false;\n                BtdSetPhase(a, BtdPhase::UseOrder, now, L"AUTO BTĐ • phát hiện Trừng Ác Lệnh đang có • tiếp tục lượt đang dở");\n                return;\n            }\n            // Fallback only: some server/client variants may also surface a semantic task.\n'''
new = '''            // Startup must preserve the proven v1.0 route: do NOT treat an orphan/stale\n            // Trừng Ác Lệnh in the bag as proof that a live round is resumable. The user flow\n            // is Ngô Giới -> nhận nhiệm vụ -> wait for the fresh order -> use it.\n            // Semantic task state is the only allowed startup-resume proof.\n            // Fallback only: some server/client variants may also surface a semantic task.\n'''
s = replace_once(s, old, new, 'controller startup resume block')
s = s.replace('AUTO BTĐ Thần Long v1.1', 'AUTO BTĐ Thần Long v1.1.1')
s = s.replace('AUTO BTĐ v1.1 • TRỪNG ÁC', 'AUTO BTĐ v1.1.1 • TRỪNG ÁC')
s = s.replace('// AUTO BTĐ v1.1: one independent orchestrator per PID.', '// AUTO BTĐ v1.1.1: one independent orchestrator per PID.')
write(p, s)

# 2) Resolve the exact SendPacket overload by enumeration instead of trusting
#    class_get_method_from_name's first same-argc overload. Preserve fail-closed behavior.
p = root / 'src' / 'bridge.cpp'
s = read(p)
append_anchor = '''void Append(wchar_t* out, std::size_t cap, const wchar_t* text) {\n    if (!out || !text || cap == 0) return;\n    std::size_t n = 0; while (n + 1 < cap && out[n]) ++n;\n    std::size_t i = 0; while (n + 1 < cap && text[i]) out[n++] = text[i++];\n    out[n] = 0;\n}\n'''
append_repl = append_anchor + '''\nvoid AppendAscii(wchar_t* out, std::size_t cap, const char* text) {\n    if (!out || !text || cap == 0) return;\n    std::size_t n = 0; while (n + 1 < cap && out[n]) ++n;\n    while (n + 1 < cap && *text) out[n++] = static_cast<unsigned char>(*text++);\n    out[n] = 0;\n}\n'''
s = replace_once(s, append_anchor, append_repl, 'Append helper')

exact_anchor = '''const MethodInfo* ExactMethod(Il2CppClass* klass, const char* name, int argc, bool isStatic,\n                              const char* p0 = nullptr, const char* p1 = nullptr, const char* p2 = nullptr) {\n    const MethodInfo* m = FindMethod(klass, name, argc);\n    if (!m || StaticMethod(m) != isStatic) return nullptr;\n    if (argc > 0 && p0 && !ParamType(m, 0, p0)) return nullptr;\n    if (argc > 1 && p1 && !ParamType(m, 1, p1)) return nullptr;\n    if (argc > 2 && p2 && !ParamType(m, 2, p2)) return nullptr;\n    return m;\n}\n'''
exact_repl = exact_anchor + '''\n// class_get_method_from_name may return the first overload with a matching arg count.\n// Network.SendPacket has changed/overloaded across client builds, so enumerate every\n// overload and accept only the exact verified static signature.\nconst MethodInfo* ExactMethodEnumerated(Il2CppClass* klass, const char* name, int argc, bool isStatic,\n                                        const char* p0 = nullptr, const char* p1 = nullptr, const char* p2 = nullptr) {\n    if (const MethodInfo* direct = ExactMethod(klass, name, argc, isStatic, p0, p1, p2)) return direct;\n    if (!klass || !name) return nullptr;\n    if (!g_api.class_get_methods) (void)Resolve(g_api.module, "il2cpp_class_get_methods", g_api.class_get_methods);\n    if (!g_api.method_get_name) (void)Resolve(g_api.module, "il2cpp_method_get_name", g_api.method_get_name);\n    if (!g_api.class_get_methods || !g_api.method_get_name) return nullptr;\n    for (Il2CppClass* current = klass; current; current = g_api.class_get_parent(current)) {\n        void* iterator = nullptr;\n        while (const MethodInfo* m = g_api.class_get_methods(current, &iterator)) {\n            const char* actual = g_api.method_get_name(m);\n            if (!Eq(actual, name)) continue;\n            if (static_cast<int>(g_api.method_get_param_count(m)) != argc) continue;\n            if (StaticMethod(m) != isStatic) continue;\n            if (argc > 0 && p0 && !ParamType(m, 0, p0)) continue;\n            if (argc > 1 && p1 && !ParamType(m, 1, p1)) continue;\n            if (argc > 2 && p2 && !ParamType(m, 2, p2)) continue;\n            return m;\n        }\n    }\n    return nullptr;\n}\n\nvoid AppendNetworkSendCandidates(Il2CppClass* klass, wchar_t* detail, std::size_t cap) {\n    SetText(detail, cap, L"Không resolve Network.SendPacket(Int32,String)");\n    if (!klass) return;\n    if (!g_api.class_get_methods) (void)Resolve(g_api.module, "il2cpp_class_get_methods", g_api.class_get_methods);\n    if (!g_api.method_get_name) (void)Resolve(g_api.module, "il2cpp_method_get_name", g_api.method_get_name);\n    if (!g_api.class_get_methods || !g_api.method_get_name) return;\n    int listed = 0;\n    for (Il2CppClass* current = klass; current && listed < 4; current = g_api.class_get_parent(current)) {\n        void* iterator = nullptr;\n        while (const MethodInfo* m = g_api.class_get_methods(current, &iterator)) {\n            const char* actual = g_api.method_get_name(m);\n            if (!Eq(actual, "SendPacket")) continue;\n            Append(detail, cap, listed == 0 ? L" • candidates: " : L" | ");\n            Append(detail, cap, StaticMethod(m) ? L"static(" : L"instance(");\n            const std::uint32_t pc = g_api.method_get_param_count(m);\n            for (std::uint32_t i = 0; i < pc; ++i) {\n                if (i) Append(detail, cap, L",");\n                const Il2CppType* type = g_api.method_get_param(m, i);\n                char* typeName = type ? g_api.type_get_name(type) : nullptr;\n                if (typeName) { AppendAscii(detail, cap, typeName); g_api.free_fn(typeName); }\n                else Append(detail, cap, L"?");\n            }\n            Append(detail, cap, L")");\n            ++listed;\n            if (listed >= 4) break;\n        }\n    }\n}\n'''
s = replace_once(s, exact_anchor, exact_repl, 'ExactMethod block')
old_send = '''    const MethodInfo* send = ExactMethod(c.networkApi, "SendPacket", 2, true, "System.Int32", "System.String");\n    if (!send) { SetText(detail, cap, L"Không resolve Network.SendPacket(Int32,String)"); return false; }\n'''
new_send = '''    const MethodInfo* send = ExactMethodEnumerated(c.networkApi, "SendPacket", 2, true, "System.Int32", "System.String");\n    if (!send) { AppendNetworkSendCandidates(c.networkApi, detail, cap); return false; }\n'''
s = replace_once(s, old_send, new_send, 'SendNetworkPacket resolver')
write(p, s)

# 3) Version the hotfix distinctly so a broken v1.1 cannot be confused with it.
(root / 'VERSION.txt').write_text('1.1.1\n', encoding='utf-8')
p = root / 'CMakeLists.txt'
s = read(p)
s = replace_once(s, 'project(AutoBTD VERSION 1.1 LANGUAGES CXX RC)', 'project(AutoBTD VERSION 1.1.1 LANGUAGES CXX RC)', 'CMake project version')
s = replace_once(s, 'OUTPUT_NAME "AUTO_BTD_v1.1"', 'OUTPUT_NAME "AUTO_BTD_v1.1.1"', 'CMake output name')
write(p, s)

p = root / 'resources' / 'app.rc'
s = read(p)
s = replace_once(s, 'FILEVERSION 1,1,0,0', 'FILEVERSION 1,1,1,0', 'FILEVERSION')
s = replace_once(s, 'PRODUCTVERSION 1,1,0,0', 'PRODUCTVERSION 1,1,1,0', 'PRODUCTVERSION')
s = s.replace('VALUE "FileVersion", "1.1\\0"', 'VALUE "FileVersion", "1.1.1\\0"')
s = s.replace('VALUE "ProductVersion", "1.1\\0"', 'VALUE "ProductVersion", "1.1.1\\0"')
s = replace_once(s, 'AUTO_BTD_v1.1.exe', 'AUTO_BTD_v1.1.1.exe', 'OriginalFilename')
write(p, s)

# 4) Strengthen the existing static verifier with the regression contracts.
p = root / 'tools' / 'verify_btd_v1.py'
s = p.read_text(encoding='utf-8')
s = replace_once(s, "assert version == '1.1', version", "assert version == '1.1.1', version", 'verify version')
s = replace_once(s, "assert 'project(AutoBTD VERSION 1.1' in cmake", "assert 'project(AutoBTD VERSION 1.1.1' in cmake", 'verify CMake version')
s = replace_once(s, "assert 'OUTPUT_NAME \"AUTO_BTD_v1.1\"' in cmake", "assert 'OUTPUT_NAME \"AUTO_BTD_v1.1.1\"' in cmake", 'verify output name')
s = replace_once(s, "print('AUTO BTD v1.1 Trừng Ác Lệnh static contracts PASS')", "assert 'phát hiện Trừng Ác Lệnh đang có • tiếp tục lượt đang dở' not in controller\nassert 'ExactMethodEnumerated(c.networkApi, \\\"SendPacket\\\"' in bridge\nprint('AUTO BTD v1.1.1 Trừng Ác Lệnh runtime-hotfix contracts PASS')", 'verify final print')
p.write_text(s, encoding='utf-8')

print('AUTO BTD v1.1.1 runtime hotfix applied')

from pathlib import Path
import sys

parts_dir = Path(__file__).with_name('v12_patch_parts')
code = ''.join((parts_dir / f'part{i:02d}.pyfrag').read_text(encoding='utf-8') for i in range(6))

# The generated v1.2 patch is intentionally split into fragments because it embeds
# C++ and four binary image resources. One generated verifier-replacement statement
# contains literal newlines inside a Python single-quoted string. Remove only that
# generated statement before compile; write the verifier explicitly after the source
# patch has run. This leaves all production C++/RC/CMake mutations unchanged.
start = code.find("s=repl(s,'bridge = (root/")
end_marker = "write('tools/verify_btd_v1.py',s)\n"
if start < 0:
    raise RuntimeError('v1.2 verifier replacement start marker not found')
end = code.find(end_marker, start)
if end < 0:
    raise RuntimeError('v1.2 verifier replacement end marker not found')
end += len(end_marker)
code = code[:start] + "# v1.2 verifier replacement deferred to wrapper\n" + code[end:]

exec(compile(code, '<v12_visual_trungac_patch>', 'exec'),
     {'__name__': '__main__', '__file__': __file__, 'sys': sys})

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'work').resolve()
verify = r'''from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
def read(rel):
    return (root / rel).read_text(encoding='utf-8-sig')

controller = read('src/controller.cpp')
bridge = read('src/bridge.cpp')
protocol = read('src/protocol.h')
cmake = read('CMakeLists.txt')
rc = read('resources/app.rc')
version = read('VERSION.txt').strip()

assert version == '1.2', version
assert 'project(AutoBTD VERSION 1.2' in cmake
assert 'OUTPUT_NAME "AUTO_BTD_v1.2"' in cmake
assert 'src/trungac_visual.cpp' in cmake
assert 'windowscodecs' in cmake and 'ole32' in cmake
assert 'kProtocolVersion = 0x00010200u' in protocol
assert 'CloseNpcDialog = 36' in protocol
assert 'DragInternalPoint = 37' in protocol

assert 'kBtdMinActionGapMs = 500' in controller
assert 'kBtdStationaryProofMs = 6000' in controller
assert 'kBtdCoord1X = 843' in controller and 'kBtdCoord1Y = 289' in controller
assert 'kBtdCoord2X = 310' in controller and 'kBtdCoord2Y = 286' in controller
assert 'kBtdCoord3X = 752' in controller and 'kBtdCoord3Y = 80' in controller
assert 'kBtdDragStartX = 620' in controller and 'kBtdDragStartY = 332' in controller
assert 'kBtdDragEndX = 619' in controller and 'kBtdDragEndY = 120' in controller
assert 'kBtdRoi1{803, 198, 75, 80' in controller
assert 'kBtdRoi2{439, 87, 321, 298' in controller
assert 'kBtdRoi3{544, 229, 145, 109' in controller
assert 'Nhận [Trừng Ác Lệnh]' in controller
assert 'BtdPhase::CloseAfterOrderGrant' in controller
assert 'BtdPhase::CloseAfterQuestAccept' in controller
assert 'BtdPhase::VisualCheckRoi1' in controller
assert 'BtdPhase::VisualFindOrderFirst' in controller
assert 'BtdPhase::VisualWaitTravel' in controller
assert 'BtdPhase::VisualFindOrderSecond' in controller
assert 'BtdPhase::VisualFight15s' in controller
assert 'visualDragCount < 2' in controller
assert 'TRUNG_AC_ORDER_VISUAL_NOT_FOUND' in controller
assert 'TRUNG_AC_ROUTE_NO_MOVEMENT' in controller
assert 'Elapsed(now, btd.visualStationarySince, kBtdStationaryProofMs)' in controller
assert 'Elapsed(now, fightStart, 15000)' in controller

assert 'UpdateUIDrag' in bridge
assert 'InputSync hidden drag PASS' in bridge
assert 'Command::DragInternalPoint' in bridge
assert 'Command::CloseNpcDialog' in bridge
assert 'ExactMethodEnumerated(c.networkApi, "SendPacket"' in bridge
assert 'phát hiện Trừng Ác Lệnh đang có • tiếp tục lượt đang dở' not in controller

assert '301 RCDATA "trungac_roi1_image1.jpg"' in rc
assert '302 RCDATA "trungac_roi1_image2.jpg"' in rc
assert '303 RCDATA "trungac_roi2_order.jpg"' in rc
assert '304 RCDATA "trungac_roi3_use.jpg"' in rc
for name in ['trungac_roi1_image1.jpg', 'trungac_roi1_image2.jpg',
             'trungac_roi2_order.jpg', 'trungac_roi3_use.jpg']:
    assert (root / 'resources' / name).exists(), name

print('AUTO BTD v1.2 visual Trừng Ác + hidden drag contracts PASS')
'''
(root / 'tools' / 'verify_btd_v1.py').write_text(verify, encoding='utf-8')
print('AUTO BTD v1.2 visual patch applied')

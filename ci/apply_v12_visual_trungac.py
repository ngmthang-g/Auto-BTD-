from pathlib import Path
import sys
parts_dir = Path(__file__).with_name('v12_patch_parts')
code = ''.join((parts_dir / f'part{i:02d}.pyfrag').read_text(encoding='utf-8') for i in range(6))
exec(compile(code, '<v12_visual_trungac_patch>', 'exec'), {'__name__': '__main__', '__file__': __file__, 'sys': sys})

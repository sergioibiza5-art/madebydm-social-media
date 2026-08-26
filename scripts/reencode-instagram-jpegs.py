from pathlib import Path
from PIL import Image, ImageOps
import json

BASE = Path('media/pokemon-chess-2026-08')
FILES = [
    '01-cover.jpg',
    '02-full-set.jpg',
    '03-top-view.jpg',
    '04-side-view.jpg',
    '05-clean-close.jpg',
]
OUT = Path('diagnostics/instagram-jpeg-reencode.json')


def inspect(path: Path):
    with Image.open(path) as im:
        return {
            'filename': path.name,
            'format': im.format,
            'mode': im.mode,
            'size': list(im.size),
            'progressive': bool(im.info.get('progressive') or im.info.get('progression')),
            'icc_profile_present': bool(im.info.get('icc_profile')),
            'exif_present': bool(im.getexif()),
            'jfif_present': 'jfif' in im.info,
            'jfif_version': list(im.info.get('jfif_version', ())) if im.info.get('jfif_version') else None,
            'density': im.info.get('dpi'),
            'bytes': path.stat().st_size,
        }


report = {'files': []}
for name in FILES:
    path = BASE / name
    before = inspect(path)

    with Image.open(path) as src:
        src.load()
        img = ImageOps.exif_transpose(src).convert('RGB')
        tmp = path.with_suffix('.instagram-safe.jpg')
        img.save(
            tmp,
            format='JPEG',
            quality=92,
            subsampling=2,
            progressive=False,
            optimize=False,
            exif=b'',
        )

    tmp.replace(path)
    after = inspect(path)
    report['files'].append({'before': before, 'after': after})

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))

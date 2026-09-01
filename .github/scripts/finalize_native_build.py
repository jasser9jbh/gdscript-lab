from __future__ import annotations
import argparse, base64, io, re
from pathlib import Path
from PIL import Image, ImageDraw

BG=(20,23,28,255)

def extract_logo(project: Path) -> Image.Image:
    text=(project/'src/index.html').read_text(encoding='utf-8', errors='strict')
    matches=re.findall(r'data:image/png;base64,([A-Za-z0-9+/=]+)', text)
    if not matches:
        raise SystemExit('No embedded PNG data URI found in src/index.html')
    for encoded in matches:
        try:
            im=Image.open(io.BytesIO(base64.b64decode(encoded))).convert('RGBA')
            if im.getchannel('A').getbbox():
                return im
        except Exception:
            pass
    raise SystemExit('Embedded PNG logo could not be decoded')

def crop_logo(im: Image.Image) -> Image.Image:
    bbox=im.getchannel('A').getbbox()
    if not bbox:
        raise SystemExit('Logo alpha channel is empty')
    return im.crop(bbox)

def fit_logo(logo: Image.Image, canvas_size: int, fraction: float) -> Image.Image:
    target=int(canvas_size*fraction)
    scale=min(target/logo.width,target/logo.height)
    size=(max(1,round(logo.width*scale)),max(1,round(logo.height*scale)))
    return logo.resize(size, Image.Resampling.LANCZOS)

def canonical_icon(logo: Image.Image, size: int) -> Image.Image:
    out=Image.new('RGBA',(size,size),(0,0,0,0))
    d=ImageDraw.Draw(out)
    m=max(1,round(size*0.02)); r=round(size*0.22)
    d.rounded_rectangle((m,m,size-m,size-m),radius=r,fill=BG)
    lg=fit_logo(logo,size,0.72)
    out.alpha_composite(lg,((size-lg.width)//2,(size-lg.height)//2))
    return out

def adaptive_foreground(logo: Image.Image, size: int) -> Image.Image:
    out=Image.new('RGBA',(size,size),(0,0,0,0))
    lg=fit_logo(logo,size,0.62)
    out.alpha_composite(lg,((size-lg.width)//2,(size-lg.height)//2))
    return out

def prepare(project: Path):
    cargo=project/'src-tauri/Cargo.toml'
    s=cargo.read_text(encoding='utf-8')
    fixes=[('tauri-build','2.5.6','2.6.3'),('tauri-plugin-fs','2.5.1','2.5.2')]
    for name,old,new in fixes:
        if re.search(rf'^\s*{re.escape(name)}\s*=.*?["\']=?{re.escape(new)}["\']',s,re.M):
            print(f'{name} already {new}')
            continue
        pat=rf'(^\s*{re.escape(name)}\s*=\s*(?:\{{[^\n]*?version\s*=\s*)?["\']=?){re.escape(old)}(["\'])'
        s2,n=re.subn(pat,rf'\g<1>{new}\g<2>',s,count=1,flags=re.M)
        if n != 1:
            raise SystemExit(f'Could not patch {name} {old} -> {new}')
        s=s2
        print(f'Patched {name}: {old} -> {new}')
    cargo.write_text(s,encoding='utf-8')
    logo=crop_logo(extract_logo(project))
    (project/'assets').mkdir(exist_ok=True)
    canonical_icon(logo,1024).save(project/'assets/app-icon-1024.png')
    canonical_icon(logo,512).save(project/'assets/app-icon.png')
    adaptive_foreground(logo,432).save(project/'assets/android-foreground-432.png')
    print('Generated canonical app icons from embedded GDScript Lab logo')

def android_icons(project: Path):
    logo=crop_logo(extract_logo(project))
    res=project/'src-tauri/gen/android/app/src/main/res'
    if not res.is_dir():
        raise SystemExit(f'Android res directory not found: {res}')
    densities=[('mdpi',48,108),('hdpi',72,162),('xhdpi',96,216),('xxhdpi',144,324),('xxxhdpi',192,432)]
    for density,launcher_sz,fg_sz in densities:
        candidates=sorted(res.glob(f'mipmap-{density}*'))
        d=candidates[0] if candidates else res/f'mipmap-{density}'
        d.mkdir(parents=True,exist_ok=True)
        icon=canonical_icon(logo,launcher_sz)
        fg=adaptive_foreground(logo,fg_sz)
        icon.save(d/'ic_launcher.png')
        icon.save(d/'ic_launcher_round.png')
        fg.save(d/'ic_launcher_foreground.png')
        print('Patched',d)
    values=res/'values'; values.mkdir(exist_ok=True)
    (values/'gdlab_icon_colors.xml').write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n  <color name="gdlab_icon_bg">#14171C</color>\n</resources>\n',encoding='utf-8')
    anydpi=res/'mipmap-anydpi-v26'; anydpi.mkdir(exist_ok=True)
    xml=('<?xml version="1.0" encoding="utf-8"?>\n'
         '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
         '  <background android:drawable="@color/gdlab_icon_bg" />\n'
         '  <foreground android:drawable="@mipmap/ic_launcher_foreground" />\n'
         '</adaptive-icon>\n')
    (anydpi/'ic_launcher.xml').write_text(xml,encoding='utf-8')
    (anydpi/'ic_launcher_round.xml').write_text(xml,encoding='utf-8')
    print('Android launcher and adaptive icon resources patched')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=['prepare','android-icons'])
    ap.add_argument('--project',default='.')
    a=ap.parse_args(); p=Path(a.project).resolve()
    if a.mode=='prepare': prepare(p)
    else: android_icons(p)
if __name__=='__main__': main()

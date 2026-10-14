#!/usr/bin/env python3
"""Update Packages/Release for the Minis Keyboard AI deb. Usage: python3 publish_version.py 0.4.9"""
import pathlib, hashlib, gzip, bz2, lzma, datetime, sys

ver = sys.argv[1]
r = pathlib.Path(__file__).resolve().parent
name = 'MinisKeyboardAI_%s_iphoneos-arm64.deb' % ver
d = (r / name).read_bytes()

parts = (r / 'Packages').read_text().strip().split('\n\n')
out = []
for part in parts:
    if 'Package: cc.minis.keyboardai\n' in part:
        lines = part.splitlines()
        ch = {'Version': ver, 'Filename': './' + name, 'Size': str(len(d)),
              'MD5sum': hashlib.md5(d).hexdigest(), 'SHA1': hashlib.sha1(d).hexdigest(),
              'SHA256': hashlib.sha256(d).hexdigest()}
        lines = [line.split(':', 1)[0] + ': ' + ch[line.split(':', 1)[0]]
                 if line.split(':', 1)[0] in ch else line for line in lines]
        part = '\n'.join(lines)
    out.append(part)
b = ('\n\n'.join(out) + '\n\n').encode()
(r / 'Packages').write_bytes(b)
gz = gzip.compress(b, 9, mtime=0); bz = bz2.compress(b); xz = lzma.compress(b)

now = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S UTC')
md5 = ''; sha = ''
for n, data in [('Packages', b), ('Packages.gz', gz), ('Packages.bz2', bz), ('Packages.xz', xz)]:
    md5 += ' %s %d %s\n' % (hashlib.md5(data).hexdigest(), len(data), n)
    sha += ' %s %d %s\n' % (hashlib.sha256(data).hexdigest(), len(data), n)
(r / 'Release').write_text(
    'Origin: Longman Plugins Pack\nLabel: Longman Plugins\nSuite: stable\nVersion: 1.0\n'
    'Codename: ios\nDate: ' + now + '\nArchitectures: iphoneos-arm64\nComponents: main\n'
    'Description: Personal rootless tweak repo for Longman Dictionary\nMD5Sum:\n' + md5 +
    'SHA256:\n' + sha)

# refresh page texts (keep the full Release fields intact — learned the hard way)
for p in [r / 'index.html', r / 'keyboard-ai.html']:
    if p.exists():
        t = p.read_text()
        import re
        t = re.sub(r'MinisKeyboardAI_0\.\d+\.\d+_iphoneos-arm64\.deb', name, t)
        t = re.sub(r'(?<![\d.])0\.4\.\d+(?![\d.])', ver, t)
        p.write_text(t)
print('published', ver, len(d), hashlib.sha256(d).hexdigest())

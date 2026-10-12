"""Verify inline JS and guard the legacy report before/after V1 deployment."""
import hashlib
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
def legacy():
    with urllib.request.urlopen('https://reports.livetransparent.com/embed/executive/index.html',timeout=60) as r:
        return r.read()

if __name__ == '__main__':
    html = (ROOT/'reports/embed/executive-v1/index.html').read_text(encoding='utf-8')
    for script in re.findall(r'<script>(.*?)</script>',html,re.S):
        subprocess.run(['node','--check','-'],input=script,text=True,encoding='utf-8',check=True)
    before = legacy()
    local = (ROOT/'reports/embed/executive/index.html').read_bytes()
    if before != local:
        raise RuntimeError('Local legacy report differs from production; deployment stopped')
    print('Inline JavaScript parses; legacy bytes match production.')
    if '--deploy' in sys.argv:
        subprocess.run([sys.executable,str(ROOT/'scripts/deploy/deploy_report_vps_local.py')],check=True)
        after = legacy()
        assert before == after, 'Legacy report changed'
        print('Legacy preserved SHA256: '+hashlib.sha256(after).hexdigest())

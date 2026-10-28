"""Compile and run power regressions; MonkeyDo may exit 1 even when all tests pass."""
from pathlib import Path
import os
import re
import subprocess
import argparse
p=argparse.ArgumentParser();p.add_argument("--english",action="store_true");args=p.parse_args()

ROOT = Path(__file__).resolve().parents[1]
SDK = Path((Path.home() / 'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip())
env = dict(os.environ)
env.setdefault('JAVA_HOME', '/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home')
env['PATH'] = env['JAVA_HOME'] + '/bin:' + env['PATH']

jungle='tests/power/test.jungle'
name='PowerTestsEnglish' if args.english else 'PowerTests'
if args.english:
    jungle='tests/power/english.jungle'
    (ROOT/jungle).write_text((ROOT/'tests/power/test.jungle').read_text().replace('base.resourcePath = ../../resources;../../preview/resources','base.resourcePath = ../../resources;../../preview/resources;../../resources-eng'))
subprocess.run([str(SDK / 'bin/monkeyc'), '-f', jungle,
                '-d', 'instinct3solar45mm', '-o', 'bin/'+name+'.prg',
                '-y', str(Path.home() / '.Garmin/keys/developer_key.der'), '-t', '-w'],
               cwd=ROOT, env=env, check=True)
try:
    result = subprocess.run([str(SDK / 'bin/monkeydo'), str(ROOT / ('bin/'+name+'.prg')),
                             'instinct3solar45mm', '-t'], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=120)
except subprocess.TimeoutExpired as error:
    (ROOT / ('bin/power-tests'+('-english' if args.english else '')+'.log')).write_text('Timed out after 120 seconds.\n' + str(error))
    raise SystemExit('Power tests timed out; no pass recorded.')
output = result.stdout + result.stderr
(ROOT / ('bin/power-tests'+('-english' if args.english else '')+'.log')).write_text(output)
match = re.search(r'PASSED \(passed=(\d+), failed=0, errors=0\)', output)
if result.returncode not in (0, 1) or not match or int(match[1]) == 0 or 'app crash' in output.lower():
    print(output)
    raise SystemExit('Power regression failed; see bin/power-tests.log')
print(f'Passed {match[1]} power regressions; log: {ROOT / "bin/power-tests.log"}')

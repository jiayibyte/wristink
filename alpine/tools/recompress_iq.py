"""Create a smaller transport copy without changing any signed payload bytes."""
from pathlib import Path
import sys; sys.path.append(str(Path(__file__).resolve().parents[2]/'tools')); import ciq_env
import argparse,hashlib,json,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('destination');a=p.parse_args()
src=Path(a.source).resolve();dst=Path(a.destination).resolve()
if src==dst or dst.exists():raise SystemExit('Keep the original archive and choose a new destination.')
def files(root):return {str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in root.rglob('*') if f.is_file()}
with tempfile.TemporaryDirectory(prefix='alpine-iq-compression-') as temp:
 root=Path(temp);original=root/'original';check=root/'check'
 subprocess.run([ciq_env.sevenzip(),'x',str(src),'-o'+str(original),'-y'],check=True,stdout=subprocess.DEVNULL)
 subprocess.run([ciq_env.sevenzip(),'a','-t7z','-mx=7','-md=64m','-ms=on','-mqs=on','-mmt=2',str(dst),'.'],cwd=original,check=True,stdout=subprocess.DEVNULL)
 subprocess.run([ciq_env.sevenzip(),'x',str(dst),'-o'+str(check),'-y'],check=True,stdout=subprocess.DEVNULL)
 expected=files(original);assert expected==files(check),'Payload changed'
 report={'original':str(src),'transportCopy':str(dst),'files':len(expected),'payloadSha256Identical':True,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'signature':'Run Garmin SDK VerifyIq on this copy before submission'}
 dst.with_suffix('.contents.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

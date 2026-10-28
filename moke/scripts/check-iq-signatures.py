"""Verify the complete signed IQ with Garmin's own verifier; never rewrite the archive."""
from pathlib import Path
import argparse,json,subprocess,tempfile,hashlib
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('package');a=p.parse_args();archive=Path(a.package).resolve()
SDK=Path((Path.home()/'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip())
source='''import java.io.File;
import com.garmin.connectiq.common.signing.KeyUtils;
import com.garmin.connectiq.common.signing.VerifyingUtils;
public class VerifyIq {public static void main(String[] args) throws Exception {
boolean ok=VerifyingUtils.verifyIqFile(new File(args[0]),KeyUtils.getPublicKey(new File(args[1])));
System.out.println("GARMIN_SDK_IQ_SIGNATURE_VALID="+ok);if(!ok)System.exit(1);
}}
'''
with tempfile.TemporaryDirectory(prefix='moke-sdk-signature-') as folder:
 f=Path(folder);subprocess.run(['7zz','e','-y','-o'+folder,str(archive),'dev_key.pub'],check=True,capture_output=True);(f/'VerifyIq.java').write_text(source)
 result=subprocess.run(['java','-cp',str(SDK/'bin/monkeybrains.jar'),str(f/'VerifyIq.java'),str(archive),str(f/'dev_key.pub')],capture_output=True,text=True)
 (R/'bin/iq-signature-validation.log').write_text(result.stdout+result.stderr)
 if result.returncode or 'GARMIN_SDK_IQ_SIGNATURE_VALID=true' not in result.stdout:raise SystemExit(result.stdout+result.stderr)
 proof={'status':'passed','garmin_sdk_verifyIqFile':True,'method':'com.garmin.connectiq.common.signing.VerifyingUtils.verifyIqFile(File, embeddedPublicKey)','package_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'scope':'Full signed archive verification using the official SDK; store review remains separate.'}
 (R/'bin/iq-signature-validation.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof)

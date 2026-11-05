import java.io.File;
import com.garmin.connectiq.common.signing.KeyUtils;
import com.garmin.connectiq.common.signing.VerifyingUtils;

// Use the SDK's verifier: PRG signatures cover Garmin's structured payload,
// rather than a plain whole-file OpenSSL digest.
class VerifyIq {
    public static void main(String[] args) throws Exception {
        if (!VerifyingUtils.verifyIqFile(new File(args[0]), KeyUtils.getPublicKey(new File(args[1])))) {
            throw new IllegalStateException("Garmin IQ signature verification failed");
        }
        System.out.println("Garmin SDK verified IQ package and product signatures.");
    }
}

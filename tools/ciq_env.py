"""Connect IQ toolchain locations shared by the project scripts (macOS, Linux, Windows).

Scripts import it with:

    sys.path.insert(0, str(Path(__file__).resolve().parents[N] / 'tools')); import ciq_env

Overrides: CIQ_HOME (SDK Manager data folder), CIQ_SDK (one SDK folder),
CIQ_DEVICES (device packs), CIQ_KEY (developer key), JAVA_HOME.
"""
import os
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

WINDOWS = os.name == 'nt'
MAC_JDK = Path('/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home')


def _home():
    if os.environ.get('CIQ_HOME'):
        return Path(os.environ['CIQ_HOME'])
    if WINDOWS:
        return Path(os.environ.get('APPDATA', '')) / 'Garmin/ConnectIQ'
    if sys.platform == 'darwin':
        return Path.home() / 'Library/Application Support/Garmin/ConnectIQ'
    return Path.home() / '.Garmin/ConnectIQ'


CIQ_HOME = _home()
DEVICES = Path(os.environ.get('CIQ_DEVICES', CIQ_HOME / 'Devices'))
KEY = Path(os.environ.get('CIQ_KEY', Path.home() / '.Garmin/keys/developer_key.der'))


def sdk():
    """The SDK chosen in SDK Manager (or CIQ_SDK)."""
    if os.environ.get('CIQ_SDK'):
        return Path(os.environ['CIQ_SDK'])
    config = CIQ_HOME / 'current-sdk.cfg'
    if not config.is_file():
        raise SystemExit(f'No Connect IQ SDK selected: install one in SDK Manager ({config} is missing).')
    return Path(config.read_text().strip())


def tool(name):
    """Path of an SDK command such as monkeyc or monkeydo."""
    return sdk() / 'bin' / (name + '.bat' if WINDOWS else name)


def sevenzip():
    """7-Zip command for .iq archives: 7zz (Homebrew/official build) or p7zip's 7z/7za on Linux."""
    for name in ('7zz', '7z', '7za'):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit('7-Zip not found: install 7zz (macOS: brew install sevenzip) or 7z (Linux: apt install p7zip-full).')


def java_home():
    """The macOS JDK the project was built with when present, else JAVA_HOME, else None (java on PATH)."""
    if MAC_JDK.is_dir():
        return MAC_JDK
    if os.environ.get('JAVA_HOME'):
        return Path(os.environ['JAVA_HOME'])
    return None


def java():
    home = java_home()
    if home and (home / 'bin/java').exists():
        return str(home / 'bin/java')
    return shutil.which('java') or 'java'


def java_env(base=None):
    """A copy of the environment with JAVA_HOME and its bin directory set when known,
    and a heap cap above Java's quarter-of-RAM default (Alpine needs ~11 GB to compile)."""
    env = dict(os.environ if base is None else base)
    home = java_home()
    if home:
        env['JAVA_HOME'] = str(home)
        env['PATH'] = str(home / 'bin') + os.pathsep + env.get('PATH', '')
    options = env.get('JAVA_TOOL_OPTIONS', '')
    if '-Xmx' not in options and 'MaxRAM' not in options:
        env['JAVA_TOOL_OPTIONS'] = (options + ' -XX:MaxRAMPercentage=70').strip()
    return env


@lru_cache(maxsize=None)
def _cjk_face():
    candidates = [('/System/Library/Fonts/STHeiti Medium.ttc', 1),
                  ('C:/Windows/Fonts/msyh.ttc', 0)]
    for path, index in candidates:
        if Path(path).is_file():
            return path, index
    if shutil.which('fc-match'):
        for pattern in ('Noto Sans CJK SC:medium', 'Noto Sans CJK SC', ':lang=zh-cn'):
            out = subprocess.run(['fc-match', '-f', '%{file}\n%{index}\n%{lang}', pattern],
                                 capture_output=True, text=True).stdout.split('\n')
            if len(out) >= 3 and 'zh-cn' in out[2].split('|'):
                return out[0], int(out[1] or 0)
    raise SystemExit('No Chinese font found for preview text: on Linux install one, e.g. `sudo apt install fonts-noto-cjk`.')


def cjk_font(size):
    """A Chinese UI font for preview sheets: STHeiti Medium on macOS, Noto Sans CJK SC on Linux."""
    from PIL import ImageFont
    path, index = _cjk_face()
    return ImageFont.truetype(path, size, index=index)

import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'scripts/sdk_device_baseline.py'
spec = importlib.util.spec_from_file_location('sdk_device_baseline', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BaselineTests(unittest.TestCase):
    def test_regional_minimum_overrides_newer_device_group(self):
        result = module.summarize({
            'deviceId': 'fixture', 'deviceGroup': 'ConnectIQ 6.0',
            'appTypes': [{'type': 'watchFace', 'memoryLimit': 65536}],
            'partNumbers': [
                {'number': 'international', 'connectIQVersion': '3.4.2', 'firmwareVersion': 1500},
                {'number': 'regional', 'connectIQVersion': '3.2.7', 'firmwareVersion': 1200},
            ],
        })
        self.assertEqual(result['minimumApi'], '3.2.7')
        self.assertTrue(result['mixedApi'])
        self.assertEqual(result['watchFaceMemoryBytes'], 65536)
        self.assertEqual(result['variants'][1]['minimumFirmware'], 1200)

    def test_versions_sort_numerically(self):
        result = module.summarize({'partNumbers': [
            {'connectIQVersion': '3.10.0'}, {'connectIQVersion': '3.9.0'}]})
        self.assertEqual(result['minimumApi'], '3.9.0')

    def test_equivalent_versions_are_normalized(self):
        result = module.summarize({'partNumbers': [
            {'connectIQVersion': '3.3'}, {'connectIQVersion': '3.3.0'}]})
        self.assertFalse(result['mixedApi'])

    def test_missing_variants_do_not_fall_back_to_device_group(self):
        for parts in [None, [], '3.4']:
            with self.assertRaises(ValueError):
                module.summarize({'deviceGroup': 'ConnectIQ 6.0', 'partNumbers': parts})

    def test_malformed_variant_fails_instead_of_being_skipped(self):
        for bad in [None, {}, {'connectIQVersion': '3.x'}, {'connectIQVersion': 3.4}]:
            with self.assertRaises(ValueError):
                module.summarize({'partNumbers': [{'connectIQVersion': '6.0'}, bad]})


if __name__ == '__main__':
    unittest.main()

import unittest
from dropbox_system.common.xor_encryption import xor_data, XOR_KEY

class TestXORData(unittest.TestCase):
    SHORT_DATA_TO_XOR = b"data"

    def _xor_data(self, data):
        # In case the data is longer than the key, we need to extend the key to the same length.
        extended_key = (XOR_KEY * (len(data) // len(XOR_KEY) + 1))[:len(data)]
        return bytes(a ^ b for a, b in zip(data, extended_key))
    
    def test_xor_short_data(self):
        """
        Check the method `xor_data`
        Execute the method with a short data and verify we got the expected output.
        """
        expected = self._xor_data(self.SHORT_DATA_TO_XOR)
        result = xor_data(self.SHORT_DATA_TO_XOR)
        self.assertEqual(result, expected)

    def test_xor_empty_data(self):
        """
        Check the method `xor_data`
        Execute the method with a empty data and verify we got the expected output.
        """
        data = b""
        result = xor_data(data)
        self.assertEqual(result, b"")

    def test_xor_data_longer_than_key(self):
        """
        Check the method `xor_data`
        Execute the method with a long data (longer that the xor key) and verify we got the expected output.
        """
        long_data = b"A" * 4 * len(XOR_KEY)
        expected = self._xor_data(long_data)
        result = xor_data(long_data)
        self.assertEqual(result, expected)

    def test_xor_symmetry(self):
        """
        Check the method `xor_data`
        Execute the method twice and verify the output has the same value with the initial value.
        """
        xor_result = xor_data(self.SHORT_DATA_TO_XOR)
        reversed_data = xor_data(xor_result)
        self.assertEqual(reversed_data, self.SHORT_DATA_TO_XOR)

if __name__ == '__main__':
    unittest.main()
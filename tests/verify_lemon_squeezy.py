import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

# Add current directory to path
sys.path.append(os.getcwd())

# Import after path setup
from core.billing import lemon_squeezy

class TestLemonSqueezy(unittest.TestCase):
    
    @patch('core.billing.lemon_squeezy.LEMON_SQUEEZY_API_KEY', 'test_key')
    @patch('core.billing.lemon_squeezy.LEMON_SQUEEZY_STORE_ID', '12345')
    @patch('core.billing.lemon_squeezy.LEMON_SQUEEZY_VARIANTS', {'SMALL': '100'})
    @patch('urllib.request.urlopen')
    def test_create_checkout_url(self, mock_urlopen):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "data": {
                "attributes": {
                    "url": "https://test.lemonsqueezy.com/checkout/..."
                }
            }
        }).encode("utf-8")
        
        # Configure context manager
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Call function
        url = lemon_squeezy.create_checkout_url("test@example.com", "SMALL")

        # Verify
        self.assertEqual(url, "https://test.lemonsqueezy.com/checkout/...")
        mock_urlopen.assert_called_once()
        args, kwargs = mock_urlopen.call_args
        self.assertIn("https://api.lemonsqueezy.com/v1/checkouts", args[0].full_url)
        self.assertEqual(args[0].method, "POST")
        
        # Check payload
        payload = json.loads(args[0].data.decode("utf-8"))
        self.assertEqual(payload['data']['attributes']['checkout_data']['email'], "test@example.com")
        self.assertEqual(payload['data']['relationships']['variant']['data']['id'], "100")

    @patch('core.billing.lemon_squeezy.LEMON_SQUEEZY_WEBHOOK_SECRET', 'test_secret')
    def test_verify_webhook_signature(self):
        import hmac
        import hashlib
        
        secret = "test_secret"
        payload = b'{"test": "data"}'
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        self.assertTrue(lemon_squeezy.verify_webhook_signature(payload, signature))
        
        # Test invalid signature
        self.assertFalse(lemon_squeezy.verify_webhook_signature(payload, "wrong_signature"))

if __name__ == '__main__':
    unittest.main()

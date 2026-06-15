import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys

# Add root to path so we can import marketplace
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from marketplace import installer

class TestMarketplaceInstaller(unittest.TestCase):
    
    @patch('marketplace.installer.json.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_browse(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "skills": [{"name": "test-skill", "category": "automation", "rating": 5.0, "downloads": 10, "description": "desc"}]
        }
        
        args = MagicMock()
        with patch('sys.stdout', new_callable=MagicMock) as mock_stdout:
            installer.browse(args)
            
        # Verify it loaded the catalog
        mock_file.assert_called_with(installer.CATALOG_PATH, 'r')
    
    @patch('marketplace.installer.json.load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('urllib.request.urlopen')
    def test_install_success(self, mock_urlopen, mock_makedirs, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "skills": [{"name": "test-skill", "category": "automation", "install_url": "http://fake"}]
        }
        
        # Mock network response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"name": "test-skill"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        args = MagicMock()
        args.skill_name = "test-skill"
        
        installer.install(args)
        
        # Should have created dir and written file
        mock_makedirs.assert_called_once()
        # open is called twice: once for read catalog, once for write manifest
        self.assertEqual(mock_file.call_count, 2)
        
    @patch('marketplace.installer.json.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_install_path_traversal_blocked(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "skills": [{"name": "../../evil", "category": "automation", "install_url": "http://fake"}]
        }
        
        args = MagicMock()
        args.skill_name = "../../evil"
        
        with patch('sys.stdout', new_callable=MagicMock) as mock_stdout:
            installer.install(args)
            # Should have printed security block
            output = "".join([call[0][0] for call in mock_stdout.write.call_args_list])
            self.assertIn("SECURITY BLOCKED", output)

if __name__ == "__main__":
    unittest.main()

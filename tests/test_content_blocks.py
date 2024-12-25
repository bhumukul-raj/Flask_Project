import unittest
import json
from app.admin import convert_block_value

class TestContentBlocks(unittest.TestCase):
    def test_convert_text_to_table(self):
        """Test converting a text block to a table block."""
        old_type = 'text'
        new_type = 'table'
        value = 'Header1 | Header2\nData1 | Data2'
        
        result = convert_block_value(old_type, new_type, value)
        self.assertIsInstance(result, dict)
        self.assertIn('headers', result)
        self.assertIn('rows', result)
        self.assertEqual(len(result['headers']), 2)
        self.assertEqual(len(result['rows']), 1)
    
    def test_convert_code_to_text(self):
        """Test converting a code block to a text block."""
        old_type = 'code'
        new_type = 'text'
        value = 'def test():\n    print("Hello")'
        
        result = convert_block_value(old_type, new_type, value)
        self.assertIsInstance(result, str)
        self.assertEqual(result, value)
    
    def test_convert_text_to_image(self):
        """Test converting a text block to an image block."""
        old_type = 'text'
        new_type = 'image'
        value = 'Sample image description'
        
        result = convert_block_value(old_type, new_type, value)
        self.assertIsInstance(result, dict)
        self.assertIn('url', result)
        self.assertIn('caption', result)
        self.assertIn('alt_text', result)
        self.assertEqual(result['caption'][:100], value[:100])
    
    def test_convert_table_to_text(self):
        """Test converting a table block to a text block."""
        old_type = 'table'
        new_type = 'text'
        value = {
            'headers': ['Header1', 'Header2'],
            'rows': [['Data1', 'Data2'], ['Data3', 'Data4']]
        }
        
        result = convert_block_value(old_type, new_type, value)
        self.assertIsInstance(result, str)
        self.assertIn('Header1 | Header2', result)
        self.assertIn('Data1 | Data2', result)
        self.assertIn('Data3 | Data4', result)
    
    def test_convert_image_to_text(self):
        """Test converting an image block to a text block."""
        old_type = 'image'
        new_type = 'text'
        value = {
            'url': 'http://example.com/image.jpg',
            'caption': 'Sample Caption',
            'alt_text': 'Sample Alt Text'
        }
        
        result = convert_block_value(old_type, new_type, value)
        self.assertIsInstance(result, str)
        self.assertIn('Image: Sample Caption', result)
        self.assertIn('URL: http://example.com/image.jpg', result)
    
    def test_invalid_type_conversion(self):
        """Test converting to an invalid type."""
        old_type = 'text'
        new_type = 'invalid'
        value = 'Sample text'
        
        result = convert_block_value(old_type, new_type, value)
        self.assertEqual(result, value)
    
    def test_invalid_value_format(self):
        """Test converting with an invalid value format."""
        old_type = 'table'
        new_type = 'text'
        value = 'Invalid table format'
        
        result = convert_block_value(old_type, new_type, value)
        self.assertEqual(result, value)

if __name__ == '__main__':
    unittest.main() 
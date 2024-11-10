import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from civitai_client import CivitaiClient

class TestCivitaiClient(unittest.TestCase):
    def setUp(self):
        self.client = CivitaiClient()
        self.test_tag = "character"
        self.test_models = [
            {
                "name": "测试模型1",
                "description": "测试描述1",
                "stats": {"downloadCount": 1000},
                "id": 1,
                "modelVersions": [
                    {
                        "images": [{"id": 1, "url": "https://example.com/image1.jpg"}]
                    }
                ]
            },
            {
                "name": "测试模型2", 
                "description": "测试描述2",
                "stats": {"downloadCount": 2000},
                "id": 2,
                "modelVersions": [
                    {
                        "images": [{"id": 1, "url": "https://example.com/image2.jpg"}]
                    }
                ]
            }
        ]

    @patch('requests.get')
    def test_fetch_models_success(self, mock_get):
        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": self.test_models}
        mock_get.return_value = mock_response

        models = self.client.fetch_models(self.test_tag)
        
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]["name"], "测试模型1")
        self.assertEqual(models[0]["download_count"], 1000)
        self.assertEqual(models[0]["url"], "https://civitai.com/models/1")

    @patch('requests.get')
    def test_fetch_models_error(self, mock_get):
        # 模拟请求失败的情况
        mock_get.side_effect = Exception("API错误")
        
        models = self.client.fetch_models(self.test_tag, limit=1)
        self.assertEqual(models, [])

    @patch('builtins.open', create=True)
    @patch('civitai_client.CivitaiClient.fetch_models')
    def test_export_models_success(self, mock_fetch, mock_open):
        # 模拟fetch_models返回测试数据
        mock_fetch.return_value = [
            {
                "name": "测试模型1",
                "description": "测试描述1",
                "download_count": 1000,
                "images": ["https://example.com/image1.jpg", ""],
                "url": "https://civitai.com/models/1"
            }
        ]
        
        # 模拟文件操作
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = self.client.export_models(self.test_tag, output_file="test_output.md")
        
        self.assertIsNotNone(result)
        mock_file.write.assert_called()

    @patch('civitai_client.CivitaiClient.fetch_models')
    def test_export_models_no_results(self, mock_fetch):
        # 模拟没有找到模型的情况
        mock_fetch.return_value = []
        
        result = self.client.export_models(self.test_tag)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()

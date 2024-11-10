import requests
from datetime import datetime, timedelta
from logger import LOG
import os
class CivitaiClient:
    def __init__(self):
        self.base_url = 'https://civitai.com/api/v1'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("CIVITAI_API_TOKEN", "")}',  # 从环境变量获取 Civitai API 授权令牌
        }

    def fetch_models(self, tag, days="Week", limit=10):
        """
        获取指定tag的高评分模型列表
        
        :param tag: 模型标签
        :param days: enum (AllTime, Year, Month, Week, Day)
        :param limit: 返回结果数量限制，默认10个
        :return: 模型列表
        """
        LOG.debug(f"准备获取Civitai上标签为 {tag} 的模型。")
        
        try:
            # 构建API请求参数
            params = {
                'tag': tag,
                'limit': limit,
                'sort': 'Highest Rated',
                'period': f'{days}'
            }
            
            # 发送API请求
            response = requests.get(
                f'{self.base_url}/models',
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # 解析响应数据
            models_data = response.json()
            
            # 过滤并处理模型数据
            filtered_models = []
            for model in models_data.get('items', []):
                r = {
                    'name': model.get('name'),
                    'download_count': model.get('stats', {}).get('downloadCount'),
                    'url': f"https://civitai.com/models/{model.get('id')}",
                    'tags': model.get('tags', []),
                    'description': model.get('description'),
                    }
                model_version = model.get('modelVersions', [])
                if model_version:
                    r['images']= [img.get('url') for img in model_version[0].get('images', [])][:2]
                else:
                    r['images'] = []

                filtered_models.append(r)
            
            LOG.info(f"成功获取 {len(filtered_models)} 个符合条件的模型。")
            return filtered_models
            
        except Exception as e:
            #import traceback
            #LOG.error(f"获取Civitai模型失败，详细错误信息:\n{traceback.format_exc()}")
            LOG.error(f"获取Civitai模型失败：{str(e)}")
            return []

    def export_models(self, tag, days="Week", limit=10, output_file=None):
        """
        导出模型列表到Markdown文件
        
        :param tag: 模型标签
        :param days: enum (AllTime, Year, Month, Week, Day)
        :param output_file: 输出文件路径，默认为None（自动生成）
        :return: 生成的文件路径
        """
        LOG.debug(f"准备导出Civitai {tag} 标签的模型列表。")
        
        models = self.fetch_models(tag, days, limit)
        
        if not models:
            LOG.warning(f"未找到任何符合条件的 {tag} 模型。")
            return None
            
        # 如果未指定输出文件，则自动生成文件名
        if output_file is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_dir = f'daily_progress/civitai'
            os.makedirs(output_dir, exist_ok=True)
            output_file = f'{output_dir}/{tag}_{date_str}.md'
			
        LOG.debug(f"导出模型列表到文件：{output_file}")

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Civitai {tag} Models Report\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for idx, model in enumerate(models, 1):
                    f.write(f"## {idx}. {model['name']}\n")
                    f.write(f"- Downloads: {model['download_count']}\n")
                    f.write(f"- URL: {model['url']}\n\n")
                    f.write(f"- 展示图：\n")
                    for image in model['images']:
                        if image:  # 只处理非空图片URL
                            f.write(f"![{model['name']}]({image}/width=100)")
                    f.write("\n")
                    if model['description']:
                        f.write(f"- Description: \n{model['description']}\n")
                    f.write("\n-------\n")
                    
            LOG.info(f"模型列表已导出到文件：{output_file}")
            return output_file
            
        except Exception as e:
            import traceback
            LOG.error(f"导出模型列表失败，详细错误信息:\n{traceback.format_exc()}")
            LOG.error(f"导出模型列表失败：{str(e)}")
            return None

if __name__ == "__main__":
    client = CivitaiClient()
    client.export_models("character")
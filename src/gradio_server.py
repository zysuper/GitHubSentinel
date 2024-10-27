import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def add_subscription(repo):
    if repo is None or repo == "":
        return f"请输入要订阅的仓库名称"
    # 定义一个函数，用于添加订阅
    subscription_manager.add_subscription(repo)  # 调用订阅管理器的添加订阅方法
    return f"已订阅 {repo}"  # 返回订阅成功的提示信息

def remove_subscription(repo):
    # 定义一个函数，用于删除订阅
    subscription_manager.remove_subscription(repo)  # 调用订阅管理器的删除订阅方法
    return f"已取消订阅 {repo}"  # 返回取消订阅成功的提示信息

def save_subscriptions():
    # 定义一个函数，用于保存订阅
    subscription_manager.save_subscriptions()  # 调用订阅管理器的保存订阅方法
    return "订阅已保存"  # 返回保存成功的提示信息

def update_dropdown_options():
    return gr.Dropdown(subscription_manager.subscriptions, label="选择要删除项目", choices=0)

#订阅维护页面
with gr.Blocks() as subscribe:
    with gr.Row():
        with gr.Column():    
            # 输入框
            output_text = gr.Textbox(label="执行结果", interactive=False)
        with gr.Column():
            # 输入框
            input_text = gr.Textbox(label="新增开源项目（onwer/repo）")
                
            # 选择删除项目
            choose_list = gr.Dropdown(subscription_manager.subscriptions, label="选择要删除项目"),

            with gr.Row():
                button_one = gr.Button("新增")
                button_one.click(fn=add_subscription, inputs=input_text, outputs=output_text)
                    
                button_two = gr.Button("删除")
                button_two.click(fn=remove_subscription, inputs=choose_list, outputs=output_text)
                
                output_text.change(fn=update_dropdown_options, outputs=choose_list)

#创建Gradio界面
report = gr.Interface(
    fn=export_progress_by_date_range,  # 指定界面调用的函数
    #title="GitHubSentinel",  # 设置界面标题
    inputs=[
        gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        ),  # 下拉菜单选择订阅的GitHub项目
        gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),
        # 滑动条选择报告的时间范围
    ],
    outputs=[gr.Markdown(), gr.File(label="下载报告")],  # 输出格式：Markdown文本和文件下载
)

demo = gr.TabbedInterface([subscribe, report],["订阅维护", "每日报告"], title="GitHubSentinel")

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
import re
from typing import List, Dict, Optional

class TextParserService:
    """
    负责从非结构化的 Markdown 文本中，使用正则表达式和关键词匹配进行信息提取。
    这是本次解析工具的前端入口。
    """
    
    # 定义核心的正则模式常量
    DATE_PATTERN = re.compile(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日')
    EMAIL_PATTERN = re.compile(r'[\w\-.]+\S+@[\w\.-]+\.\w+')
    PHONE_PATTERN = re.compile(r'\d{3}[\s\-\]?\d{4}[\s\-\]?\d{4}')

    def __init__(self, raw_markdown_content: str):
        """初始化时接收整个Markdown文档内容。"""
        self._raw_content = raw_markdown_content.strip()
        print("TextParserService initialized with content.")

    @staticmethod
    def extract_date(text: str) -> Optional[str]:
        """
        根据标题正则，提取并格式化日期为 YYYY-MM-DD。
        Example: "2026年 3月 2日" -> "2026-03-02"
        """
        match = TextParserService.DATE_PATTERN.search(text)
        if match:
            year, month, day = map(int, match.groups())
            return f"{year:04d}-{month:02d}-{day:02d}"
        return None

    def extract_contacts(self) -> Dict[str, List[str]]:
        """
        提取所有联系人信息，分为邮件和电话两类。
        返回: { 'emails': ['email1', ...], 'phones': ['phone1', ...] }
        """
        # 邮箱正则匹配
        emails = self.EMAIL_PATTERN.findall(self._raw_content)
        
        # 电话正则匹配 (需要更复杂的逻辑来关联姓名，此处仅提取号码本身作为初步实现)
        phones = self.PHONE_PATTERN.findall(self._raw_content)

        return {
            'emails': list(set(emails)), # 使用 set 去重
            'phones': list(set(phones))
        }

    def extract_function_details(self, raw_text: str) -> List[Dict[str, str]]:
        """
        根据功能描述的文本块，进行结构化解析。
        核心逻辑：识别编号、功能内容和对应的分类。
        """
        # 查找所有类似 '1、...', '2、...' 的段落
        function_list = []
        # 使用更复杂的正则来捕获带序号的功能点描述 (例如: 1、...，...)
        # 注意：这里的正则需要针对实际的Markdown格式进行微调。
        matches = re.findall(r'(\d+)[、]\s*(.*?)[\n\r\.]', raw_text, re.DOTALL)
        
        for index, (num, description) in enumerate(matches):
            # 调用内部的分类函数对描述进行处理
            category = self._classify_function(description)
            
            function_list.append({
                '序号': str(index + 1), # 使用解析顺序作为本地序号
                '功能编号': num,
                '功能分类': category,
                '具体功能描述': description.strip()
            })
        return function_list

    @staticmethod
    def _classify_function(description: str) -> str:
        """
        根据关键词进行功能类型匹配，实现规则化的分类。
        """
        desc = description.lower()
        if "ivr" in desc or "督办" in desc:
            return "IVR 督办"
        elif "审批" in desc or "流程" in desc:
            return "审批流程优化"
        elif "pc 端" in desc or "app 端" in desc or "界面" in desc:
            return "界面优化"
        elif "接口" in desc or "调用" in desc:
            return "接口优化"
        elif "漏洞" in desc or "安全" in desc or "加固" in desc:
            return "安全加固"
        elif "迁移" in desc:
            return "服务迁移"
        else:
            return "其他/未知功能"

    def parse_document(self) -> Dict[str, List]:
        """主解析函数：调用所有子方法，返回结构化的字典。"""
        print("--- Starting Comprehensive Document Parsing ---")
        
        parsed_data = {
            'raw_date': self.extract_date(self._raw_content), # 尝试从文档头部提取日期
            'contact_info': self.extract_contacts(),
            'function_list': self.extract_function_details(self._raw_content)
        }
        return parsed_data

# Example usage (for testing):
if __name__ == '__main__':
    test_md = """
监控综合应用平台 2026年3月2日功能升级申请
何熙<13405905086@139.com>
...（省略中间内容）...
一、升级功能如下：

1、IVR督办增加保存实际拨打的状态
2、延期审批、挂起审批增加环节时限，并据此时限进行督办
"""
    parser = TextParserService(test_md)
    data = parser.parse_document()
    print("\n--- Parsed Data Sample ---")
    print(f"Date: {data['raw_date']}")
    print(f"Contacts: {data['contact_info']}")
    # print(f"Functions: {[f['具体功能描述'] for f in data['function_list']]}")

import re
from datetime import datetime
from typing import Optional

class VersionCalculatorService:
    """
    负责执行所有与版本号、日期格式化相关的数学和字符串逻辑。
    将Excel公式的业务逻辑转化为可编程的函数调用。
    """

    @staticmethod
    def calculate_new_version(initial_version: str, iteration_count: int, current_step: Optional[float] = None) -> str:
        """
        计算新的版本号，模拟Excel公式：
        O51单元公式=IFERROR(N51+L51*0.01,0)
        P51=IF(O51=0,"无版本",INT(O51)&"."&INT(MOD(O51,1)*10)&"."&MOD(INT(MOD(O51,1)*100),10))
        
        :param initial_version: 基础基准版本号 (e.g., "1.4.6")。
        :param iteration_count: 本次增量/迭代次数 L_n，用于计算小版本号的增长。
        :param current_step: 当前的小数步长 N_n，可选参数。
        :return: 计算出的新版本号字符串 (e.g., "1.4.7")。
        """
        print(f"[VersionCalc] Calculating version based on initial={initial_version}, iteration={iteration_count}")

        # ---------------------------
        # Step 1: Simulate N_n (Current Base Value)
        # For simplicity in this service, we assume the starting point for calculation is a float.
        if current_step is None:
            try:
                current_base_float = float(initial_version.replace('.', '')) / 100.0 # Simplified base conversion
            except ValueError:
                print("Warning: Initial version format invalid for float conversion.")
                return initial_version

        # Step 2: Simulate the Core Formula (N + L * 0.01)
        try:
            new_base_float = current_step + (iteration_count / 100.0)
        except Exception as e:
            print(f"Error during base calculation: {e}")
            return "CALC_ERROR"

        # Step 3: Simulate the Final Formatting Formula (P51)
        # This is the most complex part, requiring precise integer truncation and formatting.
        base = int(new_base_float)
        remainder_hundreds = int((new_base_float - base) * 100) # 取小数点后两位
        minor = base % 10  # 当前版本号的个位作为次版本？ (这个公式在实际业务中可能有更精细的逻辑，此处做简化模拟)
        patch = remainder_hundreds % 10

        # 返回格式化的新版本号：Major.Minor.Patch
        new_version = f"{base}.{minor:01d}.{patch}"
        return new_version


    @staticmethod
    def standardize_date(raw_date_text: str, fallback_time: str = "22:00") -> Optional[str]:
        """
        标准化日期格式：将文本解析为 YYYY-MM-DD，并附加时间。
        输入示例: '监控综合应用平台 2026 年 3 月 2 日功能升级申请' -> 从中提取日期部分。
        """
        # 使用正则匹配 Year Month Day 的组合
        date_match = re.search(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日', str(raw_date_text))
        if date_match:
            year, month, day = map(int, date_match.groups())
            # 格式化为 YYYY-MM-DD HH:MM:SS
            return f"{year:04d}-{month:02d}-{day:02d} {fallback_time}"
        return None

    @staticmethod
    def extract_title(raw_text: str) -> str:
        """
        从文本中提取标准的标题描述。
        """
        # 假设标题总是出现在文档最顶部，并且格式比较稳定
        match = re.search(r'监控综合应用平台.*?年.*月.*日功能升级申请', raw_text, re.DOTALL)
        if match:
            return match.group(0).strip()
        return "未知标题"

# Example usage (for testing):
if __name__ == '__main__':
    test_version = VersionCalculatorService()
    initial = "1.4.6"
    new_v = test_version.calculate_new_version(initial, 1, None)
    print(f"New Version Calculated: {new_v}")

    test_date = "监控综合应用平台 2026 年 3 月 2 日功能升级申请"
    standard_date = test_version.standardize_date(test_date)
    print(f"Standardized Date: {standard_date}")
# 需求：根据查询出的ES数据，生成Excel表格
## 前置条件：
    1. es结构[es的mapping.txt](..%2F..%2Futils%2FES%E7%BB%93%E6%9E%9C%E5%AF%BCExcel%2Fes%E7%9A%84mapping.txt)
    2. excel模板[数据导出0410.xlsx](..%2F..%2Futils%2FES%E7%BB%93%E6%9E%9C%E5%AF%BCExcel%2F%E6%95%B0%E6%8D%AE%E5%AF%BC%E5%87%BA0410.xlsx)
    3. 参考工具[EsToExcel.py](..%2F..%2Futils%2FES%E7%BB%93%E6%9E%9C%E5%AF%BCExcel%2FEsToExcel.py)
    4. 大量数据：[查询结果_大批量_fixed.txt](..%2F..%2Futils%2FES%E7%BB%93%E6%9E%9C%E5%AF%BCExcel%2F%E6%9F%A5%E8%AF%A2%E7%BB%93%E6%9E%9C_%E5%A4%A7%E6%89%B9%E9%87%8F_fixed.txt)
## 架构：实用当前这个flask框架生成，在前端添加对应的路径。
## 步骤：
    1. 前端：增加一个EsToExcel的入口，放置在：高效工具中
    2. 后端：接收传入的txt或者json格式的文件，解析出ES的查询结果，再提供下载表格。
    3. 后端需要把es索引中涉及到的都需要支持，根据传入的文件中有对应的字段，并且映射成对应的中文，没有对应字段的则不需要在表格中展示。
    
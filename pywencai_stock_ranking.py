import pywencai
import os
import pandas as pd
import re
from datetime import datetime, timedelta

# 只查询 "人气排名" 的数据
start_date = "20200630"  # 起始日期
end_date = datetime.today().strftime('%Y%m%d')  # 当前日期
directory = "data"  # 指定保存目录

# 创建保存目录
if not os.path.exists(directory):
    os.makedirs(directory)

# 获取日期范围
def get_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    delta = timedelta(days=1)
    
    while start <= end:
        yield start.strftime("%Y%m%d")
        start += delta

# 定义市场代码映射
market_code_map = {
    '33': '0',  # 如果市场代码是 33，设置为 0
    '17': '1',  # 如果市场代码是 17，设置为 1
    '151': '2', # 如果市场代码是 151，设置为 2
}

# 遍历日期范围，获取每个日期的数据
for date in get_date_range(start_date, end_date):
    print(f"Fetching data for {date}...")

    # 获取 "人气排名" 数据
    keyword = f"{date}人气"
    res = pywencai.get(question=keyword, loop=True)

    # 将 res 转换为 DataFrame 对象
    if isinstance(res, dict):
        res = pd.DataFrame(res)

    # 确保 res 现在是 DataFrame
    if not isinstance(res, pd.DataFrame):
        print(f"Error: Expected DataFrame, got {type(res)}")
    else:
        # 遍历 DataFrame 中的每一行，将每只股票数据单独保存
        for index, row in res.iterrows():
            # 获取股票代码，尝试使用 'code' 或 '股票代码' 字段
            stock_code = row.get('code', None)  # 使用 'code' 字段
            if stock_code is None:
                stock_code = row.get('股票代码', None)  # 如果 'code' 没有，则尝试使用 '股票代码'

            # 如果没有找到股票代码，跳过当前行
            if stock_code is None:
                print(f"Warning: No stock code found for row {index}. Row data:\n{row}")
                continue

            # 获取市场代码
            market_code = row.get('market_code', None)

            # 如果市场代码在映射中，使用映射值，否则默认设置为 '未知'
            mapped_market_code = market_code_map.get(str(market_code), '未知')

            # 获取个股热度排名
            stock_heat_rank = row.get(f'个股热度排名[{date}]', None)  # 获取个股热度排名，日期动态填充

            # 使用股票代码生成文件名
            filename = f'{directory}/{stock_code}.txt'

            # 构建文件内容（市场代码|股票代码|日期|个股热度排名）
            content = f"{mapped_market_code}|{stock_code}|{date}|{stock_heat_rank}\n"

            # 保存文件，追加内容而不是覆盖
            with open(filename, 'a', encoding='utf-8-sig') as f:  # 使用 'a' 模式追加内容
                f.write(content)
            
            # print(f"Saved: {filename}")

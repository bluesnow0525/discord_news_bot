def craw():
    from bs4 import BeautifulSoup
    import pandas as pd
    import requests

    try:
        response = requests.get(url="https://www.forexfactory.com/calendar",headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"})
        if response.status_code == 200:
            page_source = response.content
            soup = BeautifulSoup(page_source, 'html.parser')
            # 現在你可以使用soup對象來進行你所需要的資料提取
            # 初始化一个列表来存储事件数据
            events = []
            table = soup.find('table', class_='calendar__table')
            # 我们假设日期是按顺序列出的
            current_date = None  # 初始化当前日期变量

            # Helper function to get text safely
            def get_text_safe(element):
                return element.get_text(strip=True) if element else ""

            # Helper function to find elements and handle None safely
            def find_safe(parent, tag, class_=None):
                if class_:
                    element = parent.find(tag, class_=class_)
                else:
                    element = parent.find(tag)
                return element if element else None

            # 找到表格中的所有行
            for row in table.find_all('tr'):
                # 检查这行是否是日期分隔符
                if 'calendar__row--day-breaker' in row.get('class', []):
                    current_date = row.get_text(strip=True)  # 更新当前日期
                    continue  # 跳过日期行，继续下一行
                # 接下来找到此日期下的所有事件
                elif row.find('td',class_="calendar__cell calendar__event"):              
                    impact_td = find_safe(row, 'td', 'calendar__cell calendar__impact')
                    impact_span = find_safe(impact_td, 'span')
                    impact_class = impact_span.get('class')[1] if impact_span else "Unknown"
                    time_cell = find_safe(row, 'td', 'calendar__cell calendar__time')
                    time_date = get_text_safe(time_cell) if time_cell else "All Day"
                    currency = get_text_safe(find_safe(row, 'td', 'calendar__cell calendar__currency'))
                    event_title = get_text_safe(find_safe(row, 'td', 'calendar__cell calendar__event'))
                    forecast = get_text_safe(find_safe(row, 'td', 'calendar__cell calendar__forecast'))
                    previous = get_text_safe(find_safe(row, 'td', 'calendar__cell calendar__previous'))                   
                    # 将事件数据添加到列表中
                    events.append({
                            'Date': current_date,
                            'Time': time_date,
                            'Currency': currency,
                            'Event': event_title,
                            'Forecast': forecast,
                            'Previous': previous,
                            'Impact':impact_class
                        })
                else:
                    pass
            # 打印提取的事件信息
            df = pd.DataFrame(events)
            df = df.replace('',None)
            df['Time'] = df['Time'].ffill()
            # 定义转换函数
            def convert_date(date_str, time_str):
                """将日期字符串转换为 datetime 对象"""
                from datetime import datetime,timedelta
                # 假设年份为当前年份
                year = str(datetime.now().year)
                # 合并日期和时间字符串，并尝试将字符串转换为 datetime 对象
                try:
                    date_time_str = f"{date_str} {time_str} {year}"
                    date_obj = datetime.strptime(date_time_str, "%a%b %d %I:%M%p %Y")
                    date_obj_taiwan = date_obj + timedelta(hours=12)  # 调整12小时
                    return pd.Series([date_obj_taiwan.date(), date_obj_taiwan.time()])  # 返回日期部分
                except ValueError as e:
                    # 如果转换失败，打印错误并返回 None
                    # print(f"Error converting '{date_str} {time_str}': {e}")
                    return None
            # 应用转换函数
            df[['Date',"Time"]] = df.apply(lambda x: convert_date(x['Date'], x['Time']), axis=1)
            allow_impact = ['gra','red']
            df_filtered = df[df["Impact"].apply(lambda x: x[-3:] in allow_impact)]
            return df_filtered
    except Exception as e:
        print(e)
    finally:
        pass
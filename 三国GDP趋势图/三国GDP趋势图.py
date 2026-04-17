import pandas as pd

df = pd.read_csv('1960-2019全球GDP数据.csv', encoding='gbk')

china_gdp = df[df.country=='中国']
china_gdp.head(10)
china_gdp = df[df.country=='中国']
china_gdp.head(10)

china_gdp = china_gdp.set_index('year') #将年份设置成索引
china_gdp.head()

china_gdp.GDP.plot()

jp_gdp = df[df.country=='日本'].set_index('year')
jp_gdp.GDP.plot()
china_gdp.GDP.plot()
china_gdp = df[df.country=='中国'].set_index('year')
us_gdp = df[df.country=='美国'].set_index('year')
jp_gdp = df[df.country=='日本'].set_index('year')
jp_gdp.GDP.plot()
china_gdp.GDP.plot()
us_gdp.GDP.plot()

china_gdp = df[df.country=='中国'].set_index('year')
us_gdp = df[df.country=='美国'].set_index('year')
jp_gdp = df[df.country=='日本'].set_index('year')
jp_gdp.GDP.plot(legend=True)
china_gdp.GDP.plot(legend=True)
us_gdp.GDP.plot(legend=True)

china_gdp = df[df.country=='中国'].set_index('year')
us_gdp = df[df.country=='美国'].set_index('year')
jp_gdp = df[df.country=='日本'].set_index('year')

jp_gdp.rename(columns={'GDP':'japan'}, inplace=True)
china_gdp.rename(columns={'GDP':'china'}, inplace=True)
us_gdp.rename(columns={'GDP':'usa'}, inplace=True)

jp_gdp.japan.plot(legend=True)
china_gdp.china.plot(legend=True)
us_gdp.usa.plot(legend=True)

# 按条件选取数据
china_gdp = df[df.country=='中国'].set_index('year')
us_gdp = df[df.country=='美国'].set_index('year')
jp_gdp = df[df.country=='日本'].set_index('year')
# 对指定的列修改列名
jp_gdp.rename(columns={'GDP':'日本'}, inplace=True)
china_gdp.rename(columns={'GDP':'中国'}, inplace=True)
us_gdp.rename(columns={'GDP':'美国'}, inplace=True)
# 画图
jp_gdp['日本'].plot(legend=True)
china_gdp['中国'].plot(legend=True)
us_gdp['美国'].plot(legend=True)

# 解决中文显示问题，下面的代码只需运行一次即可
import matplotlib as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from pyecharts.charts import Bar3D
from pyecharts.commons.utils import JsCode
import pyecharts.options as opts

import os
os.chdir(r'D:\dev\PyProject\PandasProject')

#1. 加载数据
#定义列表，记录Excel表名，读取数据，获取到字典
sheet_name = ['2015', '2016', '2017', '2018', '会员等级']
sheet_dict = pd.read_excel('./RFM模型/sales.xlsx', sheet_name=sheet_name)
rows = 0
for i in sheet_name:
    rows += len(sheet_dict[i])
print(f"五张表共{rows}行")
#2.数据预处理，处理异常值
# 遍历每张表
for i in sheet_name[:-1]: #除去最后一张表
    sheet_dict[i] = sheet_dict[i].dropna()  #删除缺少值
    sheet_dict[i] = sheet_dict[i][sheet_dict[i]['订单金额']>1]  #过滤金额>1
    sheet_dict[i]['max_year_data'] = sheet_dict[i]['提交日期'].max()  #固定时间节点

#把四张表对应的df，合并成一个df   list类型：[df1,df2,df3,df4]
df_merge = pd.concat(list(sheet_dict.values())[:-1])
df_merge['year'] = df_merge['提交日期'].dt.year
#计算购买时间差
df_merge['data_interval'] = df_merge['max_year_data'] - df_merge['提交日期']
df_merge['data_interval'] = df_merge['data_interval'].dt.days
df_merge

#按会员ID汇总
rfm_gb = df_merge.groupby(['year','会员ID'],as_index=False).agg(
    {   'data_interval':'min',
        '提交日期':'count',
       '订单金额':'sum'
    })
#重命名
rfm_gb.columns = ['year','会员ID','r','f','m']

#划分区间
rfm_gb.iloc[:,2:].describe().T  #第一个冒号所有行，第二个2：第3列开始后面的所有列，把‘r’给拿出来
#手动划分区间
r_bins = [-1,79,255,365]
f_bins = [0,2,5,130]
m_bins = [1,69,1199,206252]
pd.cut(rfm_gb['r'],bins=r_bins).unique()
# 基于区间给出每个范围的评分（三分法，高中低）
rfm_gb['r_label'] =pd.cut(rfm_gb['r'],bins=r_bins,labels=[3,2,1])
rfm_gb['f_label'] =pd.cut(rfm_gb['f'],bins=f_bins,labels=[1,2,3])
rfm_gb['m_label'] =pd.cut(rfm_gb['m'],bins=m_bins,labels=[1,2,3])  # labels = [i for i in rang(1,len(m_bins)]

#拼接，将分数（整形）转换成字符串
rfm_gb['r_label'] = rfm_gb['r_label'].astype(str)
rfm_gb['f_label'] = rfm_gb['f_label'].astype(str)
rfm_gb['m_label'] = rfm_gb['m_label'].astype(str)
rfm_gb['rfm_group'] = rfm_gb['r_label'].str.cat(rfm_gb['f_label']).str.cat(rfm_gb['m_label'])
rfm_gb
# #导出结果
# #保存到MySQL
# engine = create_engine('mysql+pymysql://root:123456@localhost:3306/rfm?charset=utf8')
# #参1：存储结果的表名  参2：引擎对象  参3：忽略引擎  参4：如果存在则替换 （append 追加）
# try:
#     rfm_gb.to_sql('rfm_table',engine,index=False,if_exists='replace')
#     display_data=pd.read_sql('select * from rfm_table',engine)
# except Exception as e:
#     print("wrong")
# finally:
#     engine.dispose()

display_data = rfm_gb.groupby(['rfm_group','year'],as_index=False)['会员ID'].count()
    # 5.2 修改列名.
display_data.columns = ['rfm_group', 'year', 'number']
# 细节: 把number列的类型 -> int类型.
display_data['rfm_group'] = display_data['rfm_group'].astype(int)

# 5.3 绘制图形
# 颜色池
range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
               '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']

range_max = int(display_data['number'].max())
c = (
    Bar3D()#设置了一个3D柱形图对象
    .add(
        "",#图例
        [d.tolist() for d in display_data.values],#数据
        xaxis3d_opts=opts.Axis3DOpts(type_="category", name='分组名称'),#x轴数据类型，名称，rfm_group
        yaxis3d_opts=opts.Axis3DOpts(type_="category", name='年份'),#y轴数据类型，名称，year
        zaxis3d_opts=opts.Axis3DOpts(type_="value", name='会员数量'),#z轴数据类型，名称，number
    )
    .set_global_opts( # 全局设置
        visualmap_opts=opts.VisualMapOpts(max_=range_max, range_color=range_color), #设置颜色，及不同取值对应的颜色
        title_opts=opts.TitleOpts(title="RFM分组结果"),#设置标题
    )
)
c.render() 		      # 数据保存到本地的网页中.
# c.render_notebook() #在notebook中显示
import pandas as pd
from sqlalchemy import create_engine

# 1. 模拟生成RFM数据（替代你的rfm_gb）
data = {
    'user_id': [1001, 1002, 1003, 1004],
    'R': [5, 3, 1, 4],  # 最近一次消费时间评分
    'F': [4, 5, 2, 3],  # 消费频率评分
    'M': [5, 4, 3, 5]   # 消费金额评分
}
rfm_gb = pd.DataFrame(data)

# 2. 配置MySQL连接（替换成你的实际配置）
engine = create_engine(
    'mysql+pymysql://root:123456@localhost/rfm?charset=utf8',
    # 新增超时配置，避免连接卡死
    connect_args={'connect_timeout': 10}
)

# 3. 写入MySQL表
try:
    rfm_gb.to_sql('rfm_table', engine, index=False, if_exists='replace')
    print("✅ 数据写入MySQL成功！")

    # 4. 读取验证
    df = pd.read_sql('select * from rfm_table', engine)
    print("📊 读取的表数据：")

except Exception as e:
    print(f"❌ 执行失败：{str(e)}")
finally:
    # 关闭引擎连接
    engine.dispose()

#测试 pycharts
from pyecharts.charts import Line
from pyecharts import options as opts

line = (
    Line()
    .add_xaxis(["周一", "周二", "周三"])
    .add_yaxis("销量", [100, 200, 150])
    .set_global_opts(title_opts=opts.TitleOpts(title="测试图表"))
)
line.render("test_chart.html")  # 生成html文件，能打开且显示图表即成功
exit()

sheet_dict
sheet_dict['2015']
sheet_dict['2015'].info()

for i in sheet_name:
    print(i)
    print(sheet_dict[i].info)
    print(sheet_dict[i].describe())

for i in sheet_name[:-1]: #除去最后一张表
    sheet_dict[i] = sheet_dict[i].dropna()  #删除缺少值
    sheet_dict[i] = sheet_dict[i][sheet_dict[i]['订单金额']>1]  #过滤金额>1
    sheet_dict[i]['max_year_data'] = sheet_dict[i]['提交日期'].max()  #固定时间节点

    #把四张表对应的df，合并成一个df   list类型：[df1,df2,df3,df4]
    df_merge = pd.concat(list(sheet_dict.values())[:-1])
    df_merge['year'] = df_merge['提交日期'].dt.year
    #计算购买时间差
    df_merge['data_interval'] = df_merge['max_year_data'] - df_merge['提交日期']
    df_merge['data_interval'] = df_merge['data_interval'].dt.days

rfm_gb = df_merge.groupby(['year','会员ID'],as_index=False).agg(
    {   'data_interval':'min',
        '提交日期':'count',
       '订单金额':'sum'
    })
#重命名
rfm_gb.columns = ['year','会员ID','r','f','m']


rfm_gb.iloc[:,2:].describe().T  #第一个冒号所有行，第二个2：第3列开始后面的所有列，把‘r’给拿出来
pd.cut(rfm_gb['r'],bins=3).unique()

#划分区间
#思路1：我们给定区间数，系统划分区间
rfm_gb.iloc[:,2:].describe().T  #第一个冒号所有行，第二个2：第3列开始后面的所有列，把‘r’给拿出来
pd.cut(rfm_gb['r'],bins=3).unique()
# 思路2：手动划分区间
r_bins = [-1,79,255,365]
f_bins = [0,2,5,130]
m_bins = [1,69,1199,206252]
pd.cut(rfm_gb['r'],bins=r_bins).unique()
# 基于区间给出每个范围的评分（三分法，高中低）
rfm_gb['r_lable'] =pd.cut(rfm_gb['r'],bins=r_bins,lables=[3,2,1])
rfm_gb['f_lable'] =pd.cut(rfm_gb['f'],bins=f_bins,lables=[1,2,3])
rfm_gb['m_lable'] =pd.cut(rfm_gb['m'],bins=m_bins,lables=[1,2,3])

#获取评分结果
# 1.拼接-> 营销   2.求和 -> 训练模型
#拼接，将分数（整形）转换成字符串
rfm_gb['r_label'] = rfm_gb['r_label'].astype(np.str)
rfm_gb['f_label'] = rfm_gb['f_label'].astype(np.str)
rfm_gb['f_label'] = rfm_gb['f_label'].astype(np.str)
rfm_gb['rfm_group'] = rfm_gb['r_label'].str.cat(rfm_gb['f_label']).str.cat(rfm_gb['m_label'])

#导出结果
#导出到excel
rfm_gb.to_excel('./   ',index=False) #忽略索引

#保存到MySQL
engine = create_engine('mysql+pymysql://root:123456@192.168.127.12:3306/test')
#参1：存储结果的表名  参2：引擎对象  参3：忽略引擎  参4：如果存在则替换 （append 追加）
rfm_gb.to_sql('rfm_table',engine,index=False,if_exists='replace')

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:123456@192.168.133.1:3306/rfm?charset=utf8')
#参1：存储结果的表名  参2：引擎对象  参3：忽略引擎  参4：如果存在则替换 （append 追加）
rfm_gb.to_sql('rfm_table',engine,index=False,if_exists='replace')
pd.read_sql('select * from rfm_table',engine)

# 5.2 修改列名.
display_data.columns = ['rfm_group', 'year', 'number']
# 细节: 把number列的类型 -> int类型.
display_data['number'] = display_data['number'].astype(int)
display_data
# 5.3 绘制图形
# 颜色池
range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
               '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']

range_max = int(display_data['number'].max())
c = (
    Bar3D()#设置了一个3D柱形图对象
    .add(
        "",#图例
        [d.tolist() for d in display_data.values],#数据
        xaxis3d_opts=opts.Axis3DOpts(type_="category", name='分组名称'),#x轴数据类型，名称，rfm_group
        yaxis3d_opts=opts.Axis3DOpts(type_="category", name='年份'),#y轴数据类型，名称，year
        zaxis3d_opts=opts.Axis3DOpts(type_="value", name='会员数量'),#z轴数据类型，名称，number
    )
    .set_global_opts( # 全局设置
        visualmap_opts=opts.VisualMapOpts(max_=range_max, range_color=range_color), #设置颜色，及不同取值对应的颜色
        title_opts=opts.TitleOpts(title="RFM分组结果"),#设置标题
    )
)
c.render() 		      # 数据保存到本地的网页中.
# c.render_notebook() #在notebook中显示
import pandas as pd
from MSG.models import platform, Contest
import pymysql
from config import mydb

def platform_list():
    list = [i for i in platform.platform_name]
    return list

def contest_list():
    list = [i for i in Contest.contest_name]
    return list

def db_connect(query):
    host = '127.0.0.1'
    port = 3306
    database = 'MSG'
    username = 'root'
    password = 'root'
    conn = pymysql.connect(host=host, user=username, passwd=password, port=port,
                           db=database, charset='utf8')
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def db_to_df(id):
    query = "select A.contest_type, A.end_date from contest A inner join user_record B on A.contest_name = B.contest_name where B.user_id='{}';".format(id)
    print(query)
    records = list(db_connect(query))
    print(records)
    user_df = pd.DataFrame(columns=['id','type','end_date'])
    for i in records:
        user_df=user_df.append({'id':id,'type':i[0],'end_date':1}, ignore_index='True')
    return user_df

def recommend(df, id):
    df_id = df[df['id']==id].sort_values(by='end_date', ascending=False)
    for i in range(1, len(df_id)+1):
        df_id['score'] = (0.9)**i
    sum_df = df_id.groupby('type').sum().sort_values(by='score', ascending=False)
    sum_df.reset_index(inplace=True)
    recommend_type = sum_df['type'][0]
    return recommend_type


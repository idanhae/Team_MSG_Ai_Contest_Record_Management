from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import pandas as pd
from MSG import db
from MSG.models import Contest

def crawling_dacon():
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    import time
    import pandas as pd
    driver = webdriver.Chrome('c:/chromedriver/chromedriver.exe')
    url = "https://dacon.io/competitions"
    driver.get(url)
    scroll_pause_time = 1
    while True:
        # 스크롤 이동
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(scroll_pause_time)
        # 더보기 클릭 + 종료 조건
        try:
            driver.find_element_by_xpath(
                "//button[@class='bgBtn px-10 v-btn v-btn--outlined theme--light v-size--default primary--text']").click()
            time.sleep(scroll_pause_time)
        except:
            break
    total_html = driver.page_source
    total_soup = BeautifulSoup(total_html, 'lxml')
    contest_crawling = total_soup.select('p.name.ellipsis')
    contest_list = [contest_crawling[a].text.replace(' ','_') for a in range(len(contest_crawling))]
    condition_list = [total_soup.select('div.dday')[i].text.strip() for i in range(len(contest_crawling))]
    deadline_list = [total_soup.select('div.joinTeam > span')[i].text for i in range(len(contest_crawling))]
    test = [total_soup.select('p.info2 span')[i].text for i in range(len(contest_crawling))]
    contest = {'contest': contest_list, 'condition': condition_list, 'type': '',
               'deadline': deadline_list, 'start_date': '', 'end_date': '', 'test': test, 'test1': ''}
    df_contest = pd.DataFrame(contest)
    type_test = ['시각화', '자연어', '텍스트', '정형데이터', '이미지', '객체', 'Vision',
                 '회귀', 'vision', '영상', '정형']
    # df_contest['test'] 내 문자열을 명사로 추출
    for i in range(len(contest_crawling)):
        f = df_contest.test[i].split()
        g = list(set(f).intersection(type_test))
        df_contest['test1'][i] = g
        if df_contest.test1[i] == []:
            df_contest.test1[i] = '기타'
        else:
            df_contest.test1[i] = df_contest.test1[i][0]
    # df_contest['test1'] 내 명사를 경진대회 카테고리로 통합
    for i in range(len(contest_crawling)):
        if df_contest.test1[i] in ['시각화', '이미지', '객체', 'vision', 'Vision', '영상']:
            df_contest.type[i] = '이미지'
        elif df_contest.test1[i] in ['NLP', '자연어', '텍스트']:
            df_contest.type[i] = '텍스트'
        elif df_contest.test1[i] in ['정형데이터', '회귀', '예측', '분류', '측정', '강우예측', '물성예측', '정형', '암호화폐']:
            df_contest.type[i] = '회귀/예측/분류'
        else:
            df_contest.type[i] = '기타'
    driver.find_element_by_tag_name('body').send_keys(Keys.HOME)
    driver.find_element_by_xpath("//*[@id='main']/div[3]/div/div/div/div[1]/a/div[3]/div[1]").click()
    for i in range(98):
        time.sleep(1)
        new_url = url + total_soup.select('a.clearfix')[i].get('href')[13:]
        driver.get(new_url)
        new_html = driver.page_source
        new_soup = BeautifulSoup(new_html, 'lxml')
        date_crawling = new_soup.select(
            'div.col-md-9.col-12 > ul.d-flex.flex-column.justify-center > li.text-body-2.date')
        try:
            start_date = date_crawling[0].text.strip().replace(' ', '')[:10]
            end_date = date_crawling[0].text.strip().replace(' ', '')[12:22]
            df_contest['start_date'][i] = start_date
            df_contest['end_date'][i] = end_date
        except:
            pass
    df_contest['start_date'][75] = '2020.04.01'
    df_contest['end_date'][75] = '2020.05.25'
    return df_contest


'''
df_contest = crawling_dacon()

for i in range(len(df_contest)):
    c = Contest(contest_name=df_contest['contest'][i], contest_type = df_contest['type'][i], end_date=df_contest['end_date'][i], platform='DACON')
    db.session.add(c)
    db.session.commit()'''

def crawling_aihub():
    # 웹브라우저 실행
    driver = webdriver.Chrome('c:/chromedriver/chromedriver.exe')
    url = "https://aihub.or.kr/problem_contest/promotions"
    driver.get(url)
    # ------------------------------------------------------------------------------------------------------------------------------#
    vision_list = []
    deadline_list = []
    vision_type_list = []
    start_date = []
    end_date = []
    # 비전 경진대회 명칭
    for i in range(4):
        url = 'https://aihub.or.kr/problem_contest/promotions/1174?page={}'.format(i)
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        vision_select = soup.select(
            '#totalboard-basic-list > div > table > tbody > tr > td.views-field.views-field-title > a')
        vision_type = soup.select('a.nav-link.mr-2')[0]
        for info in vision_select:
            vision_list.append(info.text.strip())
        # 비전 경진대회 마감일
        deadline = soup.select('td.views-field.views-field-title > span')
        for t in deadline:
            deadline_list.append(t.text)
        # 비전 경진대회 타입
        for i in range(len(vision_select)):
            vision_type_list.append(vision_type.text.replace('비전', '이미지'))
        # 비전 경진대회 기간
        date = soup.select('td.views-field.views-field-field-period')
        for i in range(len(vision_select)):
            if date[i].text.strip()[14:] != '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[14:])
            elif date[i].text.strip()[14:] == '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[:10])
            else:
                pass
    vision = {'contest': vision_list, 'deadline': deadline_list, 'type': vision_type_list, 'start_date': start_date,
              'end_date': end_date}
    # ------------------------------------------------------------------------------------------------------------------------------#
    text_list = []
    deadline_list = []
    text_type_list = []
    start_date = []
    end_date = []
    # 음성/자연어 경진대회 명칭
    for i in range(6):
        url = 'https://aihub.or.kr/problem_contest/promotions/1175?page={}'.format(i)
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        text_select = soup.select(
            '#totalboard-basic-list > div > table > tbody > tr > td.views-field.views-field-title > a')
        text_type = soup.select('a.nav-link.mr-2')[1]
        for info in text_select:
            text_list.append(info.text.strip())
        # 음성/자연어 경진대회 마감일
        deadline = soup.select('td.views-field.views-field-title > span')
        for t in deadline:
            deadline_list.append(t.text)
        # 음성/자연어 경진대회 타입
        for i in range(len(text_select)):
            text_type_list.append(text_type.text.replace('음성/자연어', '텍스트'))
        # 음성/자연어 경진대회 기간
        date = soup.select('td.views-field.views-field-field-period')
        for i in range(len(text_select)):
            if date[i].text.strip()[14:] != '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[14:])
            elif date[i].text.strip()[14:] == '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[:10])
            else:
                pass
    text = {'contest': text_list, 'deadline': deadline_list, 'type': text_type_list, 'start_date': start_date,
            'end_date': end_date}
    # ------------------------------------------------------------------------------------------------------------------------------#
    url = 'https://aihub.or.kr/problem_contest/promotions/1177'
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    # 국토환경 경진대회 명칭
    env_select = soup.select('#totalboard-basic-list > div > table > tbody > tr > td.views-field.views-field-title > a')
    env_list = []
    for info in env_select:
        env_list.append(info.text.strip())
    # 국토환경 경진대회 마감일
    deadline = soup.select('td.views-field.views-field-title > span')
    deadline_list = []
    for t in deadline:
        deadline_list.append(t.text)
    # 국토환경 경진대회 타입
    env_type_list = []
    env_type = soup.select('a.nav-link.mr-2')[2]
    for i in range(len(env_list)):
        env_type_list.append(env_type.text.replace('국토환경', '이미지'))
    # 국토환경 경진대회 기간
    start_date = []
    end_date = []
    date = soup.select('td.views-field.views-field-field-period')
    for i in range(len(date)):
        if date[i].text.strip()[14:] != '':
            start_date.append(date[i].text.strip()[:10])
            end_date.append(date[i].text.strip()[14:])
        elif date[i].text.strip()[14:] == '':
            start_date.append(date[i].text.strip()[:10])
            end_date.append(date[i].text.strip()[:10])
        else:
            pass
    env = {'contest': env_list, 'deadline': deadline_list, 'type': env_type_list, 'start_date': start_date,
           'end_date': end_date}
    # ------------------------------------------------------------------------------------------------------------------------------#
    lf_list = []
    deadline_list = []
    lf_type_list = []
    start_date = []
    end_date = []
    # 농축수산 경진대회 명칭
    for i in range(3):
        url = 'https://aihub.or.kr/problem_contest/promotions/1178?page={}'.format(i)
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        lf_select = soup.select(
            '#totalboard-basic-list > div > table > tbody > tr > td.views-field.views-field-title > a')
        lf_type = soup.select('a.nav-link.mr-2')[3]
        for info in lf_select:
            lf_list.append(info.text.strip().replace(' ', '_'))
        # 농축수산 경진대회 마감일
        deadline = soup.select('td.views-field.views-field-title > span')
        for t in deadline:
            deadline_list.append(t.text)
        # 농축수산 경진대회 타입
        for i in range(len(lf_select)):
            lf_type_list.append(lf_type.text.replace('농축수산', '이미지'))
        # 농축수산 경진대회 기간
        date = soup.select('td.views-field.views-field-field-period')
        for i in range(len(lf_select)):
            if date[i].text.strip()[14:] != '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[14:])
            elif date[i].text.strip()[14:] == '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[:10])
            else:
                pass
    lf = {'contest': lf_list, 'deadline': deadline_list, 'type': lf_type_list, 'start_date': start_date,
          'end_date': end_date}
    # ------------------------------------------------------------------------------------------------------------------------------#
    safety_list = []
    deadline_list = []
    safety_type_list = []
    start_date = []
    end_date = []
    # 안전 경진대회 명칭
    for i in range(2):
        url = 'https://aihub.or.kr/problem_contest/promotions/1179?page={}'.format(i)
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        safety_select = soup.select(
            '#totalboard-basic-list > div > table > tbody > tr > td.views-field.views-field-title > a')
        safety_type = soup.select('a.nav-link.mr-2')[4]
        for info in safety_select:
            safety_list.append(info.text.strip())
        # 안전 경진대회 마감일
        deadline = soup.select('td.views-field.views-field-title > span')
        for t in deadline:
            deadline_list.append(t.text)
        # 안전 경진대회 타입
        for i in range(len(safety_select)):
            safety_type_list.append(safety_type.text.replace('안전', '이미지'))
        # 안전 경진대회 기간
        date = soup.select('td.views-field.views-field-field-period')
        for i in range(len(safety_select)):
            if date[i].text.strip()[14:] != '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[14:])
            elif date[i].text.strip()[14:] == '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[:10])
            else:
                pass
    safety = {'contest': safety_list, 'deadline': deadline_list, 'type': safety_type_list, 'start_date': start_date,
              'end_date': end_date}
    # ------------------------------------------------------------------------------------------------------------------------------#
    ad_list = []
    deadline_list = []
    ad_type_list = []
    start_date = []
    end_date = []
    # 자율주행 경진대회 명칭
    for i in range(2):
        url = 'https://aihub.or.kr/problem_contest/promotions/1180?page={}'.format(i)
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        ad_select = soup.select(
            '#totalboard-basic-list > div > table > tbody > tr > td.views-field.views-field-title > a')
        ad_type = soup.select('a.nav-link.mr-2')[5]
        for info in ad_select:
            ad_list.append(info.text.strip())
        # 자율주행 경진대회 마감일
        deadline = soup.select('td.views-field.views-field-title > span')
        for t in deadline:
            deadline_list.append(t.text)
        # 자율주행 경진대회 타입
        for i in range(len(ad_select)):
            ad_type_list.append(ad_type.text.replace('자율주행', '이미지'))
        # 자율주행 경진대회 기간
        date = soup.select('td.views-field.views-field-field-period')
        for i in range(len(ad_select)):
            if date[i].text.strip()[14:] != '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[14:])
            elif date[i].text.strip()[14:] == '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[:10])
            else:
                pass
    ad = {'contest': ad_list, 'deadline': deadline_list, 'type': ad_type_list, 'start_date': start_date,
          'end_date': end_date}
    # ------------------------------------------------------------------------------------------------------------------------------#
    hc_list = []
    deadline_list = []
    hc_type_list = []
    start_date = []
    end_date = []
    # 헬스케어 경진대회 명칭
    for i in range(3):
        url = 'https://aihub.or.kr/problem_contest/promotions/1181?page={}'.format(i)
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        hc_select = soup.select(
            '#totalboard-basic-list > div > table > tbody > tr > td.views-field.views-field-title > a')
        hc_type = soup.select('a.nav-link.mr-2')[5]
        for info in hc_select:
            hc_list.append(info.text.strip())
        # 자율주행 경진대회 마감일
        deadline = soup.select('td.views-field.views-field-title > span')
        for t in deadline:
            deadline_list.append(t.text)
        # 자율주행 경진대회 타입
        for i in range(len(hc_select)):
            hc_type_list.append(hc_type.text.replace('자율주행', '이미지'))
        # 자율주행 경진대회 기간
        date = soup.select('td.views-field.views-field-field-period')
        for i in range(len(hc_select)):
            if date[i].text.strip()[14:] != '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[14:])
            elif date[i].text.strip()[14:] == '':
                start_date.append(date[i].text.strip()[:10])
                end_date.append(date[i].text.strip()[:10])
            else:
                pass
    hc = {'contest': hc_list, 'deadline': deadline_list, 'type': hc_type_list, 'start_date': start_date,
          'end_date': end_date}
    # ------------------------------------------------------------------------------------------------------------------------------#
    # AI_Hub 데이터프레임
    df_vision = pd.DataFrame(vision)
    df_text = pd.DataFrame(text)
    df_env = pd.DataFrame(env)
    df_lf = pd.DataFrame(lf)
    df_safety = pd.DataFrame(safety)
    df_ad = pd.DataFrame(ad)
    df_hc = pd.DataFrame(hc)
    df_aihub = pd.concat([df_vision, df_text, df_env, df_lf, df_safety, df_ad, df_hc])
    df_aihub = df_aihub.drop_duplicates(['contest'], keep='first')
    df_aihub = df_aihub.reset_index(drop=True)

    return df_aihub
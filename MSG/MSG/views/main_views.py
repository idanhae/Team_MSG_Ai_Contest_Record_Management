import pandas as pd
from flask import Blueprint, render_template, redirect, request, url_for, flash
from MSG import db
from MSG.models import User, User_record, Contest, Contact_us
from MSG.dataframe import db_connect, db_to_df, recommend
from MSG.crawling import crawling_dacon,crawling_aihub

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def index():
    return render_template('/index.html')

@bp.route('/hi')
def hi():
    return render_template('/login.html')

@bp.route('/log_in',methods=['POST'])
def log_in():
    id = request.form['user_id']
    print(id)
    password = request.form['password']
    print(password)
    user = User.query.get(id)
    if user.password == password:
        return redirect(url_for('main.mypage', id=id))
    else:
        flash("log in failed")
        return redirect(url_for('main.hi'))

@bp.route('/sign_up')
def sign_up():
    return render_template('/sign_up.html')

@bp.route('/welcome', methods=['POST'])
def welcome():
    id = request.form['userid']
    password = request.form['password']
    name = request.form['username']
    user_info = User(user_id=id, password=password, user_name=name)
    db.session.add(user_info)
    db.session.commit()
    flash('Welcome!')
    return redirect(url_for('main.hi'))

@bp.route('/mypage/<id>')
def mypage(id):
    query = 'select distinct A.platform, A.contest_name, A.contest_type,A.start_date,A.end_date from contest A inner join user_record B on A.contest_name = B.contest_name where B.user_id="{}";'.format(id)
    my_list = list(db_connect(query))
    my_df = pd.DataFrame(columns=['platform', 'contest_name', 'contest_type','start_date','end_date','platform_link'])
    query2 = 'select A.platform_link from platform A right outer join contest B on A.platform_name=B.platform inner join user_record C on B.contest_name=C.contest_name where C.user_id = "{}";'.format(id)
    link_list = list(db_connect(query2))
    for i in range(len(my_list)):
       my_df = my_df.append({'platform': my_list[i][0], 'contest_name': my_list[i][1], 'contest_type': my_list[i][2],'start_date': my_list[i][3],'end_date': my_list[i][4], 'platform_link':link_list[i][0]}, ignore_index=True)
    my_df=my_df.sort_values(by='end_date',ascending=False)
    data = my_df.to_dict('records')

    return render_template('/mypage.html', data=data, id=id)


@bp.route('/add_info/<id>')
def add_info(id):
    '''  query = 'select contest_name from contest;'
    contest_list = list(db_connect(query))
    contest_names = [i[0] for i in contest_list]'''
    contest_lists = Contest.query.all()
    contest_names=[i.contest_name for i in contest_lists]
    print(contest_names)
    return render_template('/add_new.html', id=id, data = contest_names)

@bp.route('/append/<id>', methods=['POST'])
def append(id):
    contest_name = request.form['contest_name']
    print(contest_name)
    user_id = id
    new = User_record(user_id=user_id, contest_name=contest_name)
    db.session.add(new)
    db.session.commit()
    return redirect(url_for('main.mypage', id=id))

@bp.route('/recommend/<id>')
def recommend_me(id):
    user_df = db_to_df(id)
    recommend_type = recommend(user_df,id)
    query = 'select distinct A.platform, A.contest_name, A.contest_type,A.start_date,A.end_date from contest A left outer join user_record B on A.contest_name = B.contest_name where B.contest_name is null and A.end_date > now() and A.contest_type="{}";'.format(recommend_type)
    contest_list = list(db_connect(query))
    query2 = 'select A.platform_link from platform A right outer join contest B on A.platform_name=B.platform left outer join user_record C on B.contest_name = C.contest_name where C.contest_name is null and B.end_date > now() and B.contest_type= "{}";'.format(recommend_type)
    link_list = list(db_connect(query2))
    show_df = pd.DataFrame(columns=['platform', 'contest_name', 'contest_type','start_date','end_date','link'])
    for i in range(len(contest_list)):
        show_df=show_df.append({'platform': contest_list[i][0], 'contest_name': contest_list[i][1], 'contest_type': contest_list[i][2],'start_date': contest_list[i][3],'end_date': contest_list[i][4],'link':link_list[i][0]}, ignore_index=True)
    show_df = show_df.sort_values(by='end_date',ascending=False)
    data = show_df.to_dict('records')
    return render_template('/recommend.html', data=data, id=id)

@bp.route('/all_contest/<id>')
def show_all(id):
    query = 'select platform, contest_name, contest_type,start_date,end_date from contest where end_date > now();'
    contest_all = list(db_connect(query))
    query2 = 'select A.platform_link from platform A inner join contest B on A.platform_name=B.platform where B.end_date > now();'
    link = list(db_connect(query2))
    all_df = pd.DataFrame(columns=['platform', 'contest_name', 'contest_type','start_date','end_date','link'])
    for i in range(len(contest_all)):
        all_df = all_df.append({'platform': contest_all[i][0], 'contest_name': contest_all[i][1], 'contest_type': contest_all[i][2],'start_date': contest_all[i][3],'end_date': contest_all[i][4],'link':link[i][0]}, ignore_index=True)
    all_df = all_df.sort_values(by='end_date',ascending=False)
    data = all_df.to_dict('records')
    return render_template('/show_all.html', data=data, id=id)

@bp.route('/all_contest_past/<id>')
def show_all_past(id):
    query = 'select platform, contest_name, contest_type,start_date,end_date from contest where end_date <= now();'
    contest_all = list(db_connect(query))
    query2='select A.platform_link from platform A inner join contest B on A.platform_name=B.platform where B.end_date <= now();'
    link_list = list(db_connect(query2))
    all_df = pd.DataFrame(columns=['platform', 'contest_name', 'contest_type','start_date','end_date','link'])
    for i in range(len(contest_all)):
        all_df = all_df.append({'platform': contest_all[i][0], 'contest_name': contest_all[i][1], 'contest_type': contest_all[i][2],'start_date': contest_all[i][3],'end_date': contest_all[i][4],'link':link_list[i][0]}, ignore_index=True)
    all_df = all_df.sort_values(by='end_date',ascending=False)
    data = all_df.to_dict('records')
    return render_template('/show_all_past.html', data=data, id=id)


@bp.route('/contact_us/<id>')
def contact(id):
    return render_template('/contact_us.html', id=id)

@bp.route('/contact_us/submit', methods=['POST'])
def contact_post():
    user_name = request.form['user_id']
    p_name = request.form['p_name']
    p_link = request.form['p_link']
    if user_name == '':
        flash("please input User id")
    elif p_name == '':
        flash("please input Platform name")
    elif p_link == '':
        flash("please input Platform link")
    else:
        flash('제출 완료!!!')
        suggestion = Contact_us(user_id=user_name, platform_name=p_name, platform_link=p_link)
        db.session.add(suggestion)
        db.session.commit()

    return redirect(url_for("main.contact"))

@bp.route('/test_db')
def test_db():
    df_contest = crawling_dacon()
    df_ai = crawling_aihub()

    for i in range(len(df_contest)):
        c = Contest(contest_name=df_contest['contest'][i], contest_type=df_contest['type'][i],
                    start_date=df_contest['start_date'][i], end_date=df_contest['end_date'][i], platform='DACON')
        try:
            db.session.add(c)
            db.session.commit()
        except:
            pass

    for i in range(len(df_ai)):
        a = Contest(contest_name=df_ai['contest'][i], contest_type = df_ai['type'][i], start_date=df_ai['start_date'][i],end_date=df_ai['end_date'][i], platform='AiHub')
        try:
            db.session.add(a)
            db.session.commit()
        except:
            pass
    return


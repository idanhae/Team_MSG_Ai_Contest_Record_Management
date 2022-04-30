from MSG import db

class platform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(200), unique=True, nullable=False)
    platform_link = db.Column(db.String(200), nullable=False)

class Contest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contest_name = db.Column(db.String(200), nullable=False, unique=True)
    contest_type = db.Column(db.String(150))
    start_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())
    platform = db.Column(db.String(200),db.ForeignKey('platform.platform_name'))

class User(db.Model):
    user_id = db.Column(db.String(150), primary_key=True)
    password = db.Column(db.String(150), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)

class User_record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(150),db.ForeignKey('user.user_id'))
    contest_name = db.Column(db.String(150), db.ForeignKey('contest.contest_name'))

class Contact_us(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(150),db.ForeignKey('user.user_id'))
    platform_name = db.Column(db.String(200), nullable=False)
    platform_link = db.Column(db.String(200), nullable=False)



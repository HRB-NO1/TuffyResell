from datetime import datetime

from twittor import db


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(20))
    body = db.Column(db.String(5000))
    price = db.Column(db.String(10))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sell_status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "id={}, body={}, create_time={}, user_id={}".format(
            self.id, self.body, self.create_time, self.user_id
        )
    # 测试程序懒得写了
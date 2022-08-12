from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_minify import minify, decorators
import uuid

app = Flask(__name__)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secratedb.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
minify(app=app, html=True, js=True, cssless=True, passive=True)


def generate_uuid_short_del():
    delete_key = str(uuid.uuid4())[:13]
    short_key = delete_key[:8]
    return short_key, delete_key


class SecrateMsg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sec_msg = db.Column(db.String(), nullable=False)
    typeofmsg = db.Column(db.Integer(), nullable=False)
    times_clicked = db.Column(db.Integer(), nullable=False)
    short_url_id = db.Column(db.String(), nullable=False)
    delete_url_id = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'SecrateMsg {self.short_url_id}'


@app.route('/')
@decorators.minify(html=True, js=True, cssless=True)
def index():
    return render_template('index.html')


@app.route('/secretmsg', methods=['POST'])
def shorturl():
    sec_msg = request.form.get('sec_msg')
    typeofmsg = request.form.get('message_type')
    short_url_id, delete_url_id = generate_uuid_short_del()
    times_clicked = 0
    sec_record = SecrateMsg(sec_msg=sec_msg, typeofmsg=typeofmsg, times_clicked=times_clicked,
                            short_url_id=short_url_id, delete_url_id=delete_url_id)
    db.session.add(sec_record)
    db.session.commit()
    short_url_id = "https://urscrt.herokuapp.com/" + short_url_id
    delete_url_id = "https://urscrt.herokuapp.com/" + delete_url_id
    return render_template('result.html', short_url=short_url_id, delete_url=delete_url_id)


@app.route('/<string:short_url_key>')
@decorators.minify(html=True, js=True, cssless=True)
def short_minify(short_url_key):
    sec_msg_var = SecrateMsg.query.filter_by(
        short_url_id=short_url_key).first()
    if sec_msg_var != None:
        times_clicked = int(sec_msg_var.times_clicked)
        if times_clicked < 1:
            times_clicked += 1
            sec_msg_var.times_clicked = times_clicked
            db.session.add(sec_msg_var)
            db.session.commit()
            type_of_sec_msg = int(sec_msg_var.typeofmsg)
            if type_of_sec_msg == 1:
                sec_msg = str(sec_msg_var.sec_msg)
                return render_template('secrettext.html', sec_msg=sec_msg)
            elif type_of_sec_msg == 2:
                redirect_link = str(sec_msg_var.sec_msg)
                return redirect(redirect_link)
            elif type_of_sec_msg == 3:
                sec_msg = str(sec_msg_var.sec_msg)
                return render_template('neogram.html', sec_msg=sec_msg)
        else:
            db.session.delete(sec_msg_var)
            db.session.commit()
            return render_template("clickedmulti.html")
    else:
        return render_template("secretnevercreaterd.html")


@app.route('/delete/<string:delete_url_key>', methods=['GET'])
def deleteuser(delete_url_key):
    shortner = SecrateMsg.query.filter_by(
        delete_url_id=delete_url_key).first()
    db.session.delete(shortner)
    db.session.commit()
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=False)

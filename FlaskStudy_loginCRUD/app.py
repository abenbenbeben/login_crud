from flask import Flask, render_template, session, request, redirect, url_for,flash
import os
from pref_question import pref_location
from wiki import wiki
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#インスタンスの作成
app = Flask(__name__)

key = os.urandom(21)
app.secret_key = key

#DBの準備(SQLiteを使う)
URI = 'sqlite:///note.db'#SQLIteを使ってnote.dbという名前のファイルを管理する。
app.config['SQLALCHEMY_DATABASE_URI'] = URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)#SQLAlchemyはインスタンスを作成し、変数DBに割り当てている。

#ORMでDBを操作するためにクラスを継承
class Note(db.Model):
    __tablename__ = 'notes'
    userid = db.Column(db.String(30),primary_key=True)
    userpw = db.Column(db.String(300))
    nicname = db.Column(db.String(300))
    secretq1 = db.Column(db.String(300))
    secretq1_answer = db.Column(db.String(300))
    secretq2 = db.Column(db.String(300))
    secretq2_answer = db.Column(db.String(300))
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    
    
#DBの生成
@app.cli.command('initialize_DB')
def initialize_DB():
    db.create_all()
 
    

#メイン
@app.route('/')
def index():
    if not session.get('login'):
        
        return redirect(url_for('login'))
    else:
        return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logincheck', methods=['POST'])
def logincheck():
    user_id_pre = request.form['user_id']
    user_pw_pre= request.form['password']
    #DBから登録情報をチェック
    
    org_data = Note.query.get(user_id_pre)
    
    if not org_data:
        session['login'] = False
        flash('登録がありませんでした。。新規会員登録してください。')
    else:
        org_data_id = org_data.userid
        org_data_pw = org_data.userpw
        
        if user_pw_pre == org_data_pw:
            session['login'] = True
        else:
            session['login'] = False
            flash('パスワードが違います。')
        

    if session['login']:
        return render_template('index.html',user_nicname = org_data.nicname)
    else:
        return redirect(url_for('login'))
    
@app.route('/registration', methods=['POST'])
def registration():
    return render_template('new_registration.html')

@app.route('/registration_action',methods=['POST'])
def registration_action():
    user_id_new = request.form['user_id_new']
    user_pw_new = request.form['user_pw_new']
    org_data = Note.query.get(user_id_new)
    
    if not org_data:
        if user_id_new:
            if user_pw_new:
                register_data=Note(userid=user_id_new,userpw=user_pw_new)
                db.session.add(register_data)
                db.session.commit()
                return render_template('regist_nicname.html',user_id=user_id_new)
            else:
                flash('登録できませんでした。パスワードを入力してください')
                return render_template('new_registration.html')
        else:
            flash('登録できませんでした。入力項目を確認してください。')
            return render_template('new_registration.html')
    else:
        flash('このIDは登録されています')
        return render_template('new_registration.html')
    
@app.route('/regist_nicname', methods=['POST'])
def regist_nicname():
    org_userid = request.form['user_id']
    org_data = Note.query.get(org_userid)
    org_data.nicname = request.form['nicname']
    if org_data.nicname:
        db.session.merge(org_data)
        db.session.commit()
        flash('ニックネーム登録完了!（あと２ステップです）')
        return render_template('regist_secretquestion1.html', user_id = org_userid)
    else:
        flash('ニックネームを入力してください')
        return render_template('regist_nicname.html')
    
@app.route('/regist_secretq1', methods=['POST'])
def regist_secretq1():
    org_userid = request.form['user_id']
    org_data = Note.query.get(org_userid)
    org_data.secretq1 = request.form['secretq1']
    org_data.secretq1_answer = request.form['secretq1_answer']
    if org_data.secretq1_answer:
        db.session.merge(org_data)
        db.session.commit()
        flash('秘密１登録完了')
        return render_template('regist_secretquestion2.html', user_id=org_userid)
    else:
        flash('秘密の答えを入力して下さい')
        return render_template('regist_secretquestion1.html')

@app.route('/regist_secretq2', methods=['POST'])
def regist_secretq2():
    org_userid = request.form['user_id']
    org_data = Note.query.get(org_userid)
    org_data.secretq2 = request.form['secretq2']
    org_data.secretq2_answer = request.form['secretq2_answer']
    if org_data.secretq2_answer:
        db.session.merge(org_data)
        db.session.commit()
        flash('新規登録完了です！')
        return render_template('login.html', user_id=org_userid)
    else:
        flash('秘密の答えを入力して下さい')
        return render_template('regist_secretquestion2.html')



@app.route('/logout')
def logout():
    session.pop('login',None)
    return redirect(url_for('index'))
    

@app.route('/pref_quiz', methods=['POST'])
def pref_quiz():
    random_pref, city_name, pref_url= pref_location()
    session['prefecture'] = random_pref
    session['city'] = city_name
    session['url'] = pref_url
    return render_template('quiz.html', prefecture=random_pref)

@app.route('/answercheck', methods=['POST'])
def answercheck():
    user_answer = request.form['city']
    quiz = session['prefecture']
    answer = session.get('city')
    url = session.get('url')
    if answer == user_answer:
        correct="正解"
    else:
        correct = "不正解"
        
    return render_template('result.html', correct=correct, answer=answer,user_answer=user_answer,url=url,quiz=quiz)

@app.route('/wikipedia',methods=['POST'])
def wikipedia():
    return render_template('wiki_result.html', result="")

@app.route('/wiki_answer', methods=['POST'])
def wiki_answer():
    word = request.form['word']
    if word == '':
        result = '入力がないため、該当する結果がありませんでした。'
    else:
        result = wiki(word)
        
    return render_template('wiki_result.html', result=result)
    

#アプリケーションの起動
if __name__ == '__main__':
    app.run(debug=True)
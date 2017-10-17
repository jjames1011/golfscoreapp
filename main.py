from flask import request, redirect, render_template, session, flash
from app import app, db
from models import User, Tournament, Player, Round, Round_Player_Table, Course, Hole, Score


@app.route("/")
def index():
   encoded_error = request.args.get("error")
   return redirect('/courses')

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if user.password == password:
                session['user'] = user.email
                flash('welcome back, ' + user.email)
                return redirect("/")
        flash('bad username or password')
        '''have it redirect to courses page until other controllers are implemented'''
        return redirect("/courses")

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    print(session.keys())
    return redirect('/')


@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! ' + email + ' is already taken')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect("/")
    else:
        return render_template('signup.html', title='Sign up!')


@app.route("/courses")
def list_courses():
    courses = Course.query.all()
    return render_template("list_courses.html", courses=courses)


@app.route("/initiate_tournament", methods=['GET', 'POST'])
def initiate_tournament():
    if request.method == 'GET':
        return render_template('tournament_initiation.html', title='Start A Tournament')
    elif request.method == 'POST':
        tournament_course = request.form['course']

        return render_template('tournament_initiation.html', title='Starting Tournament', course=tournament_course)

@app.route('/process_players', methods=['POST', 'GET'])
def process_players():
    if request.method == 'POST':
        player_1_Name = request.form['player1']
        db.session.add(Player(player_1_Name))
        player_2_Name = request.form['player2']
        db.session.add(Player(player_2_Name))
        player_3_Name = request.form['player3']
        db.session.add(Player(player_3_Name))
        player_4_Name = request.form['player4']
        db.session.add(Player(player_4_Name))
        db.session.commit()
        session['player_1_Name'] = player_1_Name
        session['player_2_Name'] = player_2_Name
        session['player_3_Name'] = player_3_Name
        session['player_4_Name'] = player_4_Name
        return redirect('/score_input')




@app.route('/score_input', methods=['POST', 'GET'])
def score_input():
    this_Rounds_Players = []
    this_Rounds_Players += Player.query.filter_by(name = session['player_1_Name'])
    this_Rounds_Players += Player.query.filter_by(name = session['player_2_Name'])
    this_Rounds_Players += Player.query.filter_by(name = session['player_3_Name'])
    this_Rounds_Players += Player.query.filter_by(name = session['player_4_Name'])

    if 'hole_num' not in session:
        session['hole_num'] = 1
    if 'round_num' not in session:
        session['round_num'] = 1
    return render_template('score_input.html', players=this_Rounds_Players, hole_num=session['hole_num'], round_num=session['round_num'])



@app.route('/process_score', methods=['POST', 'GET'])
def process_score():
    tournament_id = 1
    if session['hole_num'] > 18:
        session['round_num'] += 1
        session['hole_num'] = 1
        db.session.add(Round(session['round_num'],tournament_id))
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=1))
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=2))
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=3))
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=4))

    player_1_Score = int(request.form['player_1_score'])
    player_2_Score = int(request.form['player_2_score'])
    player_3_Score = int(request.form['player_3_score'])
    player_4_Score = int(request.form['player_4_score'])
    db.session.add(Score(round_id=session['round_num'], hole_id=session['hole_num'], player_id=1, score=player_1_Score))
    db.session.add(Score(round_id=session['round_num'], hole_id=session['hole_num'], player_id=2, score=player_2_Score))
    db.session.add(Score(round_id=session['round_num'], hole_id=session['hole_num'], player_id=3, score=player_3_Score))
    db.session.add(Score(round_id=session['round_num'], hole_id=session['hole_num'], player_id=4, score=player_4_Score))
    session['hole_num'] += 1
    db.session.commit()
    return redirect('/score_input')




def logged_in_user():
    owner = User.query.filter_by(email=session['user']).first()
    return owner

endpoints_without_login = ['signup' ,'leaderboard', 'signin']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/signin")



app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()

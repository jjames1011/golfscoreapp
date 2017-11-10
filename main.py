from flask import request, redirect, render_template, session, flash, json
from app import app, db
from models import User, Tournament, Player, Round, Round_Player_Table, Course, Hole, Score
import requests
from sqlalchemy import desc
from helper import create_holes_for_course

def logged_in_user_id():#creates a logged in user
    return User.query.filter_by(email=session['user']).first().id

@app.route("/")
def index():
   encoded_error = request.args.get("error")
   return redirect('/courses')

@app.route("/signin", methods=['GET', 'POST'])
def signin():#Accessible without logging in.
    if request.method == 'GET':#During a get request, display the blank signin template
        return render_template('signin.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:#Validate if user exsists in the database
            user = users.first()
            if user.password == password:
                session['user'] = user.email#Put user email into Session variable
                return redirect("/")
        flash('bad username or password')
        '''have it redirect to courses page until other controllers are implemented'''
        return redirect("/courses")

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    print(session.keys())
    return redirect('/')

@app.route("/signup", methods=['GET'])
def display_signup():#show signup blank signup template on from get request
    return render_template('signup.html', title='Sign Up!')

@app.route("/signup", methods=['POST'])
def validate_user():#Validate signup inputs and record errors if there are any.
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    verify = request.form['verify']
    email_db_count = User.query.filter_by(email=email).count()
    username_db_count = User.query.filter_by(username=username).count()
    user_error = ''
    password_error1 = ''
    password_error2 = ''
    email_error = ''

    if not " " in username:
        if username_db_count == 0:
            if len(username) < 3 or len(username) > 20:
                user_error = "Sliced it! User name must be between 3 and 20 characters with no spaces. Please try again."
        else:
            user_error = "Sliced it! User name is already taken. Please try again."
    else:
        user_error = "Sliced it! User name must be between 3 and 20 characters with no spaces. Please try again."

    if not " " in password:
        if len(password) < 3 or len(password) > 20:
            password_error1 = "Chunked it! Password must be between 3 and 20 characters with no spaces. Please try again."
    else:
        password_error1 = "Chunked it! Password must be between 3 and 20 characters with no spaces. Please try again."

    if password != verify:
        password_error2 = "Double Bogey! Passwords do not match."

    if not " " in email:
        if email_db_count == 0:
            if len(email) >= 3 and len(email) <= 30:
                if "@" in email and "." in email:
                    email_error = ''
                else:
                    email_error = "Shanked it! Email can be blank or must contain '@' and '.' to be valid. Please try again."
            else:
                email_error = "Shanked it! Email can be blank or must contain '@' and '.' to be valid. Please try again."
        else:
            email_error = "Shanked it! Email is already taken. Please try again."
    else:
        email_error = "Shanked it! Email can\'t be blank or must contain '@' and '.' to be valid. Please try again."

    if not user_error and not password_error1 and not password_error2 and not email_error:
        user = User(username=username, email=email, password=password)
        #When there is no error's present, log the user into the database and create a session variable with email
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect('/')
    else:#When there are errors, display signup template with errors passed through using Jinja
        return render_template("signup.html", username=username, email=email,
    username_error=user_error, password_error1=password_error1,
    password_error2=password_error2, email_error=email_error)

@app.route("/api_courses")
def find_courses():
    r = requests.get("http://api.sportradar.us/golf-t2/schedule/pga/2017/tournaments/schedule.json?api_key=cruz8v8npxp9zd2s3wzk9uwr")
    json_string = r.text
    all_tourney = json.loads(json_string)
    all_Courses = all_tourney['tournaments']
    a = 0
    list_courses = []
    for course in all_Courses:
        print(course['venue']['courses'][0]['name'])
        list_courses.append(course['venue']['courses'][0]['name'])
    for course in list_courses:
        if not Course.query.filter_by(name=course).all():
            db.session.add(Course(course))
            db.session.commit()
    return render_template("list_api_courses.html", courses=all_Courses)


@app.route("/courses")
def list_courses():#Queries the database for all Course names and passes them to template. Template loops and displays names.
    if not Course.query.filter_by(id=4).first():
        find_courses()
    courses = Course.query.all()
    return render_template("list_courses.html", courses=courses)

@app.route("/initiate_tournament", methods=['GET', 'POST'])#This route is accessed through the post request from list_courses template and GET from initiate_tournament.html template
def initiate_tournament():
    if request.method == 'GET':#The template is rendered user query parameters when a player name input is blank
        player_1_Name = request.args.get('p1')
        player_2_Name = request.args.get('p2')
        player_3_Name = request.args.get('p3')
        player_4_Name = request.args.get('p4')
        tournament_Name = request.args.get('tname')
        name_Error = 'No blank names allowed, please input 4 player names.'
        return render_template('tournament_initiation.html', title='Start A Tournament', course=session['course'],
    p1_Name=player_1_Name, p2_Name=player_2_Name, p3_Name=player_3_Name, p4_Name=player_4_Name, t_Name=tournament_Name, name_Error=name_Error)
    elif request.method == 'POST':
        tournament_course = request.form['course']#pulls name of course from list_courses template
        session['course'] = tournament_course#puts that course name in session variable with key 'course'
        course = Course.query.filter_by(name = tournament_course).first()#assigns course database object to variable via the course name
        course_id = course.id#assigns course ID from db to variable
        session['course_id'] = course_id #puts course ID varible into session with key 'course_id'

        if not Hole.query.filter_by(owner_id=course.id).first():#Check to see if this course has holes
            create_holes_for_course(course.name)#If no holes exsist, create them with helper

        return render_template('tournament_initiation.html', title='Starting Tournament', course=tournament_course)#sends course name to template using Jinja

@app.route('/process_players', methods=['POST', 'GET'])
def process_players():#This method sets up players in the database so that their scores can be tracked
    if request.method == 'POST':
        player_1_Name = request.form['player1']
        player_2_Name = request.form['player2']
        player_3_Name = request.form['player3']
        player_4_Name = request.form['player4']
        tournament_Name = request.form['tournament_name']

        if (player_1_Name and player_2_Name and player_3_Name and player_4_Name) == None or (player_1_Name and player_2_Name and player_3_Name and player_4_Name) == "" or (player_1_Name and player_2_Name and player_3_Name and player_4_Name) == False:
            flash('No blank names allowed, please input 4 player names.')
            return redirect('/initiate_tournament?p1='+player_1_Name+'&p2='+player_2_Name+'&p3='+player_3_Name+'&p4='+player_4_Name+'&tname='+tournament_Name)
        else:#This adds a tournament and players to the database
            logged_in_user_id = User.query.filter_by(email=session['user']).first().id
            db.session.add(Tournament(logged_in_user_id, tournament_Name))
            db.session.commit()
            session['tournament_Id'] = Tournament.query.filter_by(name=tournament_Name).first().id

            db.session.add(Player(player_1_Name,session['tournament_Id'],logged_in_user_id))#Players are instatiated using player name from template POST request and tournament_ID session variable
            db.session.add(Player(player_2_Name,session['tournament_Id'],logged_in_user_id))
            db.session.add(Player(player_3_Name,session['tournament_Id'],logged_in_user_id))
            db.session.add(Player(player_4_Name,session['tournament_Id'],logged_in_user_id))
            db.session.commit()
            #After players have been confirmed in the DB, their name is assigned into Session variables
            player_1_Id = Player.query.filter_by(name = player_1_Name , owner_id = logged_in_user_id).first().id
            player_2_Id = Player.query.filter_by(name = player_2_Name , owner_id = logged_in_user_id).first().id
            player_3_Id = Player.query.filter_by(name = player_3_Name , owner_id = logged_in_user_id).first().id
            player_4_Id = Player.query.filter_by(name = player_4_Name , owner_id = logged_in_user_id).first().id

            session['player_1_Id'] = player_1_Id
            session['player_2_Id'] = player_2_Id
            session['player_3_Id'] = player_3_Id
            session['player_4_Id'] = player_4_Id
            return redirect('/score_input')




@app.route('/score_input')#This route handles score input
def score_input():#this fills in a blank template with player,round,and par information for use in score inputs.
    if 'error' not in session:
        session['error'] = ""
    if 'error1' not in session:
        session['error1'] = ""
    if 'error2' not in session:
        session['error2'] = ""
    if 'error3' not in session:
        session['error3'] = ""
    if 'error4' not in session:
        session['error4'] = ""

    this_Rounds_Players = []#create an empty list then add player names from session into the list
    this_Rounds_Players += Player.query.filter_by(id = session['player_1_Id'])
    this_Rounds_Players += Player.query.filter_by(id = session['player_2_Id'])
    this_Rounds_Players += Player.query.filter_by(id = session['player_3_Id'])
    this_Rounds_Players += Player.query.filter_by(id = session['player_4_Id'])
    if 'hole_num' not in session:#This tracks the current hole number being scored
        session['hole_num'] = 1
    if 'round_num' not in session:#This tracks the current round number being scored
        session['round_num'] = 1
        db.session.add(Round(session['round_num'],session['tournament_Id']))#Instantiate a round with the given round number.
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=1))#Connect each player to this new round
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=2))
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=3))
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=4))
        db.session.commit()
    #get the hole from the db for the par property
    hole = Hole.query.filter_by(id = session['hole_num']).first()
    return render_template('score_input.html', players=this_Rounds_Players, hole_num=session['hole_num'], round_num=session['round_num'],par_num=hole.par, errors=session['error'], error1=session['error1'], error2=session['error2'], error3=session['error3'], error4=session['error4'])

    #grab scores from form POST request
@app.route('/process_score', methods=['POST', 'GET'])
def process_score():
    # if request.method=='POST':

    tournament_id = session['tournament_Id']
    tournament_id_str = str(tournament_id)
    session['error'] = ""
    session['error1'] = ""
    session['error2'] = ""
    session['error3'] = ""
    session['error4'] = ""

    #grab scores from form POST request
    score1 = request.form['player_1_score']
    if (score1 == None) or (score1 == "") or (score1 == False):
        session['error1'] = "You must input a score for every player"
    score2 = request.form['player_2_score']
    if (score2 == None) or (score2 == "") or (score2 == False):
        session['error1'] = "You must input a score for every player"
    score3 = request.form['player_3_score']
    if (score3 == None) or (score3 == "") or (score3 == False):
        session['error1'] = "You must input a score for every player"
    score4 = request.form['player_4_score']
    if (score4 == None) or (score4 == "") or (score4 == False):
        session['error1'] = "You must input a score for every player"

    if session['error1'] != "":
        session['error'] += session['error1']
        return redirect ('/score_input')

    else:
        player_1_Score_val = score1.strip()
        for c in player_1_Score_val:
            if not c in '0123456789':
                session['error2'] = "Input must be a number"
                # return redirect('/score_input')
        if session['error2'] == "":
            player_1_Score = int(player_1_Score_val)
            if player_1_Score <= 0:
                session['error3'] = "Score must be greater than 0"
            if player_1_Score > 99:
                session['error4'] = "Score must be no greater than 99"

        player_2_Score_val = score2.strip()
        for c in player_2_Score_val:
            if not c in '0123456789':
                session['error2'] = "Input must be a number"
                # return redirect('/score_input')
        if session['error2'] == "":
            player_2_Score = int(player_2_Score_val)
            if player_2_Score <= 0:
                session['error3'] = "Score must be greater than 0"
            if player_2_Score > 99:
                session['error4'] = "Score must be no greater than 99"

        player_3_Score_val = score3.strip()
        for c in player_3_Score_val:
            if not c in '0123456789':
                session['error2'] = "Input must be a number"
                # return redirect('/score_input')
        if session['error2'] == "":
            player_3_Score = int(player_3_Score_val)
            if player_3_Score <= 0:
                session['error3'] = "Score must be greater than 0"
            if player_3_Score > 99:
                session['error4'] = "Score must be no greater than 99"

        player_4_Score_val = score4.strip()
        for c in player_4_Score_val:
            if not c in '0123456789':
                session['error2'] = "Input must be a number"
                # return redirect('/score_input')
        if session['error2'] == "":
            player_4_Score = int(player_4_Score_val)
            if player_4_Score <= 0:
                session['error3'] = "Score must be greater than 0"
            if player_4_Score > 99:
                session['error4'] = "Score must be no greater than 99"
    session['error'] += session['error1'] + session['error2'] + session['error3'] + session['error4']
    if session['error'] > "":
        return redirect('/score_input')


    #get the player ids using Session variable
    hole_id = Hole.query.filter_by(hole_num = session['hole_num'], owner_id = session['course_id']).first().id
    print(hole_id)
    #create new score object using player ID, Round ID, Hole ID, Course ID, Tournament ID all from session and Score from the POST request
    db.session.add(Score(round_id=session['round_num'], hole_id=hole_id, course_id=session['course_id'], player_id=session['player_1_Id'], tournament_id=session['tournament_Id'],score=player_1_Score))
    db.session.add(Score(round_id=session['round_num'], hole_id=hole_id, course_id=session['course_id'], player_id=session['player_2_Id'], tournament_id=session['tournament_Id'],score=player_2_Score))
    db.session.add(Score(round_id=session['round_num'], hole_id=hole_id, course_id=session['course_id'], player_id=session['player_3_Id'], tournament_id=session['tournament_Id'],score=player_3_Score))
    db.session.add(Score(round_id=session['round_num'], hole_id=hole_id, course_id=session['course_id'], player_id=session['player_4_Id'], tournament_id=session['tournament_Id'],score=player_4_Score))
    db.session.commit()
    #update the current hole number in the session variable
    session['hole_num'] += 1
    if session['hole_num'] > 18:#this logic will determine if all 18 holes have been played.
        session['hole_num'] = 1#After 18 holes, hole is reset to 1
        session['round_num'] += 1#Round is increased by 1
        db.session.add(Round(session['round_num'],tournament_id))#New round is created in preparation for new scores
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=1))#Player connected to new round
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=2))
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=3))
        db.session.add(Round_Player_Table(round_id=session['round_num'],player_id=4))
        db.session.commit()
        return redirect('/leaderboard?tournament_id='+ tournament_id_str)#After last 18 holes, user sent to leaderboard
    return redirect('/score_input')#when there are more scores to report, user goes to next score_input template

@app.route('/list_tournaments')
def list_tournaments():#Used to display tournaments that a user can select to see their leaderboard
    tournaments = Tournament.query.all()
    if not tournaments:
        flash('There are currently no tournaments, sign-in and start one!')
        return redirect('/sign-in')
    return render_template('list_tournaments.html',tournaments=tournaments)


@app.route("/leaderboard", methods=['GET'])
def leaderboard():#populating score data assuming a for loop will be used in the template to list every players score'''
    if not Score.query.all():
        flash('Leaderboard is currently empty')
        return redirect('/score_input')

    else:
        tournament_id = request.args.get('tournament_id')

        some_Score = Score.query.filter_by(tournament_id = tournament_id).first()
        round_num = some_Score.round_id
        course_id = some_Score.course_id
        course = Course.query.filter_by(id = course_id).first().name
        player_scores = Score.query.filter_by(tournament_id = tournament_id).all()
        players = Player.query.filter_by(tournament_id = tournament_id).all()

        #get player id's for score query
        player_ids = {}
        j=1
        for player in players:
            player_ids['player_{0}_Id'.format(j)] = player.id
            j+=1
        
        #Create empty lists to be used for sorting later
        ordered_names = []
        ordered_scores = []

        #Set scores to zero
        player1total = 0
        player2total = 0
        player3total = 0
        player4total = 0

        #Query score database using player_ID and accumulate total scores
        player_1_Scores = Score.query.filter_by(player_id=player_ids['player_1_Id']).all()
        for score in player_1_Scores:
            player1total += score.score

        #add the score and name to the sorting list
        ordered_names.append(players[0].name)
        ordered_scores.append(player1total)


        player_2_Scores = Score.query.filter_by(player_id=player_ids['player_2_Id']).all()
        for score in player_2_Scores:
            player2total += score.score

        #Logic to determine if where score/name goes in the list
        if player2total <= ordered_scores[0]:
            ordered_names.insert(0,players[1].name)
            ordered_scores.insert(0,player2total)
        else:
            ordered_names.append(players[1].name)
            ordered_scores.append(player2total)


        player_3_Scores = Score.query.filter_by(player_id=player_ids['player_3_Id']).all()
        for score in player_3_Scores:
            player3total += score.score
        
        #Logic to determine if where score/name goes in the list
        if player3total <= ordered_scores[0]:
            ordered_names.insert(0,players[2].name)
            ordered_scores.insert(0,player3total)
        elif player3total <= ordered_scores[1]:
            ordered_names.insert(1,players[2].name)
            ordered_scores.insert(1,player3total)
        else:
            ordered_names.append(players[2].name)
            ordered_scores.append(player3total)


        player_4_Scores = Score.query.filter_by(player_id=player_ids['player_4_Id']).all()
        for score in player_4_Scores:
            player4total += score.score
        
        #Logic to determine if where score/name goes in the list
        if player4total <= ordered_scores[0]:
            ordered_names.insert(0,players[3].name)
            ordered_scores.insert(0,player4total)
        elif player4total <= ordered_scores[1]:
            ordered_names.insert(1,players[3].name)
            ordered_scores.insert(1,player4total)
        elif player4total <= ordered_scores[2]:
            ordered_names.insert(2,players[3].name)
            ordered_scores.insert(2,player4total)
        else:
            ordered_names.append(players[3].name)
            ordered_scores.append(player4total)

        #determine the last hole played on this tournament
        last_hole_id = Score.query.filter_by(tournament_id=tournament_id).order_by(desc(Score.hole_id)).first().hole_id
        last_hole_played = Hole.query.filter_by(id=last_hole_id).first().hole_num

        return render_template("leaderboard.html", player_scores=ordered_scores,round_num=round_num, player_Names_List=ordered_names,course=course,last_hole_played=last_hole_played)
    


endpoints_without_login = ['display_signup' , 'validate_user','list_tournaments', 'leaderboard', 'signin', 'static']

@app.before_request
def require_login():#Control for endpoint access for a non logged in user
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/signin")



# Our app secret key should be kept secret (i.e. not on github) upon app launch. (Not placed on github)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()

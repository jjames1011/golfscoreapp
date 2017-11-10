from app import db

'''In java, classes usually go in their own file but for some reason the norm in python is to throw them
all into one file called models so here they are...'''

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    tournaments = db.relationship('Tournament', backref='owner')
    players = db.relationship('Player', backref='owner')


    def __init__(self, username, email, password):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return '<User %r' % self.username

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rounds = db.relationship('Round', backref='owner')
    scores = db.relationship('Score', backref='tournament')
    players = db.relationship('Player', backref='tournament')

    def __init__(self, owner_id, name):
        self.owner_id = owner_id
        self.name = name

    def __repr__(self):
        return '<Tournament %r' % self.name

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    scores = db.relationship('Score', backref='player')
    rounds = db.relationship('Round_Player_Table', backref='player')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, name,tournament_id, owner_id):
        self.name = name
        self.tournament_id = tournament_id
        self.owner_id = owner_id

    def __repr__(self):
        return '<Player %r>' % self.name

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    scores = db.relationship('Score', backref='round')
    players = db.relationship('Round_Player_Table', backref='round')


    def __init__(self, round_number, tournament_id):
        self.round_number = round_number
        self.tournament_id = tournament_id

    def __repr__(self):
        return '<Round %d>' % self.roundNum


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    holes = db.relationship('Hole', backref = 'owner')
    scores = db.relationship('Score', backref='course')


    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Course %r' % self.name


class Hole(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    hole_num = db.Column(db.Integer)
    par = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    scores = db.relationship('Score', backref='hole')


    def __init__(self, owner_id, par,hole_num):
        self.owner_id = owner_id
        self.par = par
        self.hole_num = hole_num

    def __repr__(self):
        return '<Hole %d>' % self.id

class Round_Player_Table(db.Model):
    '''this is a table specifically for associating a round with a player. This is a many-to-many relationship
    as a round can have many players and a player can have many rounds(hence having a unique table for this relationship)'''
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    def __init__(self, round_id, player_id):
        self.round_id=round_id
        self.player_id=player_id

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer,db.ForeignKey('round.id'))
    hole_id = db.Column(db.Integer, db.ForeignKey('hole.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    score = db.Column(db.Integer)


    def __init__(self, round_id, hole_id, course_id, player_id, tournament_id, score):
        self.round_id = round_id
        self.hole_id = hole_id
        self.course_id = course_id
        self.player_id = player_id
        self.tournament_id = tournament_id
        self.score = score

    def __repr__(self):
        return '<Score %d' % self.score

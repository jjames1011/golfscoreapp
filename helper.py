from flask import flash, redirect,json
from app import app, db
from models import User, Tournament, Player, Round, Round_Player_Table, Course, Hole, Score
import requests

def validation(score):
    while True:
        try:
            num_str1 = score.strip()
            for c in num_str1:
                if c in '0123456789':
                    continue
        except NameError:
            vError = "Input must be a number"
            return vError
            break
            num_str2 = int(num_str1)
            if not num_str2 <= 0:
                continue
        except NameError:
            vError = "Score must be a number 1 or greater"
            return vError
            break
            if score != None:
                continue
        except NameError:
            vError="You must input a score for every player"
            return vError
            break
            if num_str2 < 99:
                break
        except NameError:
            vError = "Score must be no greater than 99"
            return vError
            break
        vError = ""
        return vError
        break


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
    return None

def create_holes_for_course(course_Setup):
    r = requests.get("http://api.sportradar.us/golf-t2/schedule/pga/2017/tournaments/schedule.json?api_key=cruz8v8npxp9zd2s3wzk9uwr")
    json_string = r.text
    all_tourney = json.loads(json_string)
    all_Courses = all_tourney['tournaments']
    list_Holes = []
    for course in all_Courses:
        if course['venue']['courses'][0]['name'] == course_Setup:
            list_Holes = course['venue']['courses'][0]['holes']
            for hole in list_Holes:
                db.session.add(Hole(Course.query.filter_by(name = course_Setup).first().id,hole['par'], hole['number']))
            db.session.commit()
            return None
    return None

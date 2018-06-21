from __future__ import division
from sympy.solvers import solve
from sympy import Symbol, Eq, solveset
import requests
from sqlalchemy import and_
from scraper.database import init_db, db_session
from scraper.models import Lecture, Practical
from scraper.captcha import captcha_solver

def bunk_lecture(n, tot_lec, chatID, stype, index):
    '''Bunk calculator'''
    init_db()
    if(stype == "Lectures"):
        subject_data = Lecture.query.filter(Lecture.chatID == chatID).all()
    else:
        subject_data = Practical.query.filter(Practical.chatID == chatID).all()
    index -= 1 # DB Tables are Zero-Index 
    attended = subject_data[index].attended
    conducted = subject_data[index].conducted

    result = (((int(attended) + int(tot_lec)) -  int(n))/(int(conducted) + tot_lec)) * 100
    return round(result, 2) #Round up to 2 decimals.

def until80(chatID):
    '''Calculates the no. of lectures user must attend in order to get attendance to 80%'''
    init_db()
    subject_data = Lecture.query.filter(and_(Lecture.chatID == chatID, Lecture.name == "Total")).first()
    attended = subject_data.attended
    conducted = subject_data.conducted
    x = Symbol('x')
    expr = Eq((((int(attended) + x)/(int(conducted) + x))*100), 80)
    soln = solveset(expr, x)
    return next(iter(soln)) # Extracting the integer from singleton set soln.

def check_login(username, password):
    '''Checks if user input for their credentials is correct.'''
    base_url = 'http://report.aldel.org/student_page.php'
    with requests.session() as s:
        r = s.get(base_url)
        sessionID = str(r.cookies.get('PHPSESSID')) #Get SessionID
        captcha_answer = captcha_solver(sessionID) #Solve the CAPTCHA
        payload = {
        'studentid':username,
        'studentpwd':password,
        'captcha_code':captcha_answer,
        'student_submit':''
        }
        s.post(base_url, data=payload)
        r = s.get('http://report.aldel.org/student/attendance_report.php')
        return username in r.text


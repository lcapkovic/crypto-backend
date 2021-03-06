from flask import Flask
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3 as sql

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1 per second"],
)

answers = []
hints = []

def load_answers():
    global answers

    print("Loading answers...")
    with open('answers.txt', encoding='utf-8') as f:
        answers = [line.rstrip('\n') for line in f]
    print("Loaded answers:")
    print(answers)

def load_hints():
    global hints
    print("Loading hints...")
    with open('hints.txt', encoding='utf-8') as f:
        data = f.read()
        hints = [hint.strip() for hint in data.split('----')]
    print("Loaded hints:")
    print(hints)

@app.after_request
def treat_as_plain_text(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers["content-type"] = "text/plain"
    return response

load_answers()
load_hints()

def add_submission(problem, answer, correctInt):
    con = sql.connect("db/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO submissions (problemId, answer, correct) VALUES (?,?,?)", (problem, answer, correctInt))
    con.commit()
    con.close()

def count_all_submissions(problem):
	con = sql.connect("db/database.db")
	cur = con.cursor()
	cur.execute("SELECT COUNT(*) FROM submissions WHERE problemId=?", (str(problem),))
	count = cur.fetchall()
	con.close()
	return count[0][0]

def count_correct_submissions(problem):
	con = sql.connect("db/database.db")
	cur = con.cursor()
	cur.execute("SELECT COUNT(*) FROM submissions WHERE problemId=? AND correct=1", (str(problem),))
	count = cur.fetchall()
	con.close()
	return count[0][0]

@app.route("/check_answer", methods=['GET'])
@limiter.limit("2 per minute")
def check_answer():
    problem = int(request.args.get('problem'))
    answer = request.args.get('answer')

    if len(answers) > problem and len(hints) > problem and answer.lower() == answers[problem].lower():
        correct = 1
    else:
        correct = 0
    
    if len(answer) < 100:
        print("Adding submission to database")
        add_submission(problem, answer, correct)

    if len(answers) > problem and len(hints) > problem and answer.lower() == answers[problem].lower():
        return hints[problem]
    else:
        return "INCORRECT"

@app.route("/get_submissions", methods=['GET'])
def get_submissions():
    problem = int(request.args.get('problem'))

    if problem < len(answers):
        total = count_all_submissions(problem)
        correct = count_correct_submissions(problem)
        print(total)
        print(correct)
        return str(total) + " " + str(correct)
    return "0 0"

if __name__ == "__main__":
    app.run(host='0.0.0.0')

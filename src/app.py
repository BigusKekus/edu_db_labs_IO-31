from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Lomalomiha82',
    database='expertsurveysystemdb',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route('/')
def index():
    return "REST API для опитувань працює. Використовуйте /users, /surveys тощо"

# --- Users ---
@app.route('/users', methods=['GET'])
def get_users():
    with conn.cursor() as cur:
        cur.execute("SELECT id, login, email FROM Users")
        return jsonify(cur.fetchall())

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO Users (login, email, password) VALUES (%s, %s, %s)",
                    (data['login'], data['email'], data['password']))
        conn.commit()
        return jsonify({'message': 'User created'}), 201

# --- Surveys ---
@app.route('/surveys', methods=['GET'])
def get_surveys():
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, description, author_id FROM Surveys WHERE is_active = TRUE")
        return jsonify(cur.fetchall())

@app.route('/surveys', methods=['POST'])
def create_survey():
    data = request.get_json()
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO Surveys (title, description, author_id) 
                       VALUES (%s, %s, %s)""",
                    (data['title'], data['description'], data['author_id']))
        conn.commit()
        return jsonify({'message': 'Survey created'}), 201

# --- Questions ---
@app.route('/questions/<int:survey_id>', methods=['GET'])
def get_questions_for_survey(survey_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Questions WHERE survey_id = %s ORDER BY question_order", (survey_id,))
        return jsonify(cur.fetchall())

# --- Options ---
@app.route('/options/<int:question_id>', methods=['GET'])
def get_options(question_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Options WHERE question_id = %s", (question_id,))
        return jsonify(cur.fetchall())

# --- Submitting response ---
@app.route('/responses', methods=['POST'])
def submit_response():
    data = request.get_json()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO Responses (survey_id, user_id) VALUES (%s, %s)",
                    (data['survey_id'], data['user_id']))
        response_id = cur.lastrowid
        for ans in data['answers']:
            cur.execute("""INSERT INTO Answers (response_id, question_id, answer_text, selected_option_ids)
                           VALUES (%s, %s, %s, %s)""",
                        (response_id, ans['question_id'], ans.get('answer_text'), ans.get('selected_option_ids')))
        conn.commit()
    return jsonify({'message': 'Response submitted'}), 201
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM Users WHERE id = %s", (user_id,))
        conn.commit()
    return jsonify({'message': f'User {user_id} deleted'})

if __name__ == '__main__':
    app.run(debug=True)

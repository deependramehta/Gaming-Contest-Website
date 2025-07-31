from flask import Flask, request, render_template, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",  # or your MySQL root password
    database="gamearena"
)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    try:
        # Insert into teams table
        cursor.execute("""
            INSERT INTO teams (team_name, leader_name, leader_email, leader_phone, experience, special_requirements)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['teamName'],
            data['leaderName'],
            data['leaderEmail'],
            data['leaderPhone'],
            data['experience'],
            data['specialRequirements']
        ))
        db.commit()
        team_id = cursor.lastrowid

        # Insert members
        for member in data['members']:
            cursor.execute("""
                INSERT INTO team_members (team_id, member_name, member_email)
                VALUES (%s, %s, %s)
            """, (team_id, member['name'], member['email']))
        db.commit()

        return jsonify({"message": "Team registered successfully"}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Registration failed"}), 500

@app.route('/teams')
def show_teams():
    cursor.execute("SELECT * FROM teams")
    teams = cursor.fetchall()

    team_list = []
    for team in teams:
        team_id = team[0]
        cursor.execute("SELECT member_name FROM team_members WHERE team_id = %s", (team_id,))
        members = [row[0] for row in cursor.fetchall()]
        team_data = {
            'team_name': team[1],
            'leader': team[2],
            'experience': team[5],
            'special': team[6],
            'members': members
        }
        team_list.append(team_data)

    return render_template('teams.html', teams=team_list)

if __name__ == '__main__':
    app.run(debug=True)



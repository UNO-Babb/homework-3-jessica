#ChatGPT Game
#Logic is in this python file

from flask import Flask, render_template, jsonify
import csv
import os
import random 

app = Flask(__name__)

# Copy game code here
CSV_FILE = 'score.csv'
BOARD_SIZE = 100

def load_scores():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_scores(scores):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['player', 'turn', 'position'])
        writer.writeheader()
        writer.writerows(scores)

def create_new_game(player_names):
    scores = [{'player': name, 'turn': '0', 'position': '0'} for name in player_names]
    save_scores(scores)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'continue' in request.form:
            return redirect(url_for('game'))
        elif 'new' in request.form:
            return redirect(url_for('new_game'))
    players_exist = os.path.exists(CSV_FILE)
    return render_template_string("""
        <html><body>
        <h1>Welcome to the Dice Board Game</h1>
        <form method="post">
            {% if players_exist %}
                <button name="continue" type="submit">Continue Game</button>
            {% endif %}
            <button name="new" type="submit">New Game</button>
        </form>
        </body></html>
    """, players_exist=players_exist)

@app.route('/new', methods=['GET', 'POST'])
def new_game():
    if request.method == 'POST':
        player_names = request.form.get('players').split(',')
        player_names = [p.strip() for p in player_names if p.strip()]
        if len(player_names) >= 2:
            create_new_game(player_names)
            return redirect(url_for('game'))
    return render_template_string("""
        <html><body>
        <h1>Start a New Game</h1>
        <form method="post">
            <label>Enter player names (comma separated):</label><br>
            <input type="text" name="players" required><br><br>
            <button type="submit">Start</button>
        </form>
        </body></html>
    """)

@app.route('/game', methods=['GET', 'POST'])
def game():
    scores = load_scores()
    if not scores:
        return redirect(url_for('index'))

    current_player_index = min(range(len(scores)), key=lambda i: int(scores[i]['turn']))
    player = scores[current_player_index]

    roll1 = roll2 = guess = correct = winner = None

    if request.method == 'POST':
        guess = request.form.get('guess')
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        total = roll1 + roll2
        correct = (guess == 'even' and total % 2 == 0) or (guess == 'odd' and total % 2 == 1)

        if correct:
            new_position = int(player['position']) + total
            player['position'] = str(min(new_position, BOARD_SIZE))
        player['turn'] = str(int(player['turn']) + 1)

        save_scores(scores)

        if int(player['position']) >= BOARD_SIZE:
            winner = player['player']

    return render_template_string("""
        <html><head>
        <title>Play Game</title>
        <style>
            .board {
                display: grid;
                grid-template-columns: repeat(10, 50px);
                gap: 2px;
            }
            .cell {
                width: 50px; height: 50px;
                text-align: center;
                vertical-align: middle;
                line-height: 50px;
                border: 1px solid black;
            }
            .player { font-size: 0.7em; background: white; border-radius: 50%; padding: 2px; display: inline-block; }
            {% for i in range(100) %}
            .cell:nth-child({{ i + 1 }}) { background-color: hsl({{ i * 3.6 }}, 100%, 75%); }
            {% endfor %}
        </style>
        </head><body>

        <h1>Current Player: {{ current_player }}</h1>

        {% if winner %}
            <h2>{{ winner }} wins!</h2>
            <a href="{{ url_for('index') }}">Back to main menu</a>
        {% else %}
        <form method="post">
            <label>Guess:</label><br>
            <input type="radio" name="guess" value="odd" required>Odd
            <input type="radio" name="guess" value="even">Even<br><br>
            <button type="submit">Roll Dice</button>
        </form>
        {% endif %}

        {% if roll1 %}
            <p>You rolled: {{ roll1 }} and {{ roll2 }} (Total: {{ roll1 + roll2 }})</p>
            <p>Your guess was: {{ guess }}. You were {{ "correct" if correct else "incorrect" }}.</p>
        {% endif %}

        <h2>Board</h2>
        <div class="board">
            {% for i in range(1, 101) %}
                <div class="cell">
                {% for s in scores %}
                    {% if i == s.position|int %}
                        <div class="player">{{ s.player[0] }}</div>
                    {% endif %}
                {% endfor %}
                </div>
            {% endfor %}
        </div>

        </body></html>
    """, scores=scores, current_player=player['player'],
           roll1=roll1, roll2=roll2, guess=guess, correct=correct, winner=winner)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

COLORS = ['green', 'orange', 'purple', 'red']
PLAYERS = ['Player 1', 'Player 2', 'Player 3', 'Player 4']

# Initialize game board
def generate_board():
    board = ['start']
    for i in range(80):
        board.append(COLORS[i % len(COLORS)])
    board.append('end')
    return board

# Initialize player positions with shapes
def init_players():
    return {
        'Player 1': {'position': 0, 'shape': 'X'},
        'Player 2': {'position': 0, 'shape': 'O'},
        'Player 3': {'position': 0, 'shape': '▲'},
        'Player 4': {'position': 0, 'shape': '■'}
    }

@app.route('/')
def index():
    if 'board' not in session:
        session['board'] = generate_board()
        session['players'] = init_players()
        session['turn'] = 0
        session['winner'] = None
        session['events'] = []

    current_player = PLAYERS[session['turn'] % len(PLAYERS)]
    current_player_shape = session['players'][current_player]['shape']  # Get the current player's shape

    return render_template('index.html',
                           board=session['board'],
                           players=session['players'],
                           turn=session['turn'],
                           current_player=current_player,
                           current_player_shape=current_player_shape,
                           winner=session['winner'],
                           events=session['events'])

@app.route('/draw')
def draw_card():
    if session.get('winner'):
        return redirect(url_for('index'))

    card_color = random.choice(COLORS)
    current_player = PLAYERS[session['turn'] % len(PLAYERS)]
    players = session.get('players', init_players())
    position = players[current_player]['position']
    board = session['board']
    event_log = session.get('events', [])

    moved = False
    for i in range(position + 1, len(board)):
        if board[i] == card_color:
            session['players'][current_player]['position'] = i
            moved = True
            log_message = f"{current_player} drew {card_color.upper()} and moved to tile {i}."
            break

    if not moved:
        session['players'][current_player]['position'] = len(board) - 1
        session['winner'] = current_player
        log_message = f"{current_player} drew {card_color.upper()}, but no {card_color} tile ahead — moved to END and won!"

    if session['players'][current_player]['position'] == len(board) - 1 and not session.get('winner'):
        session['winner'] = current_player
        log_message = f"{current_player} landed on the END and won!"

    event_log.append(log_message)
    session['events'] = event_log
    session['turn'] += 1

    with open('game_log.txt', 'a') as f:
        f.write(log_message + '\n')

    return redirect(url_for('index'))

@app.route('/reset')
def reset_game():
    session.clear()
    with open('game_log.txt', 'w') as f:
        f.write('--- Game Reset ---\n')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
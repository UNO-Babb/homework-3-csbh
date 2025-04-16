#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template, redirect, url_for, flash, session
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

COLORS = ['green', 'orange', 'purple', 'red']
PLAYERS = ['player1', 'player2', 'player3', 'player4']

# Initialize game board
def generate_board():
    board = ['start']
    for i in range(80):
        board.append(COLORS[i % len(COLORS)])
    board.append('end')
    return board

# Initialize player positions
def init_players():
    return {player: 0 for player in PLAYERS}

@app.route('/')
def index():
    if 'board' not in session:
        session['board'] = generate_board()
        session['players'] = init_players()
        session['turn'] = 0
        session['winner'] = None
    return render_template('index.html',
                           board=session['board'],
                           players=session['players'],
                           turn=session['turn'],
                           current_player=PLAYERS[session['turn'] % 4],
                           winner=session['winner'])
    if 'events' not in session:
        session['events'] = []
    return render_template('index.html',
                       board=session['board'],
                       players=session['players'],
                       turn=session['turn'],
                       current_player=PLAYERS[session['turn'] % 4],
                       winner=session['winner'],
                       events=session['events'])

@app.route('/draw')
def draw_card():
    if session.get('winner'):
        return redirect(url_for('index'))

    card_color = random.choice(COLORS)
    current_player = PLAYERS[session['turn'] % 4]
    position = session['players'][current_player]
    board = session['board']

    event_log = session.get('events', [])
    log_message = ""

    # Try to find the next tile of the drawn color
    moved = False
    for i in range(position + 1, len(board)):
        if board[i] == card_color:
            session['players'][current_player] = i
            moved = True
            log_message = f"{current_player} drew {card_color.upper()} and moved to tile {i}."
            break

    if not moved:
        session['players'][current_player] = len(board) - 1
        session['winner'] = current_player
        log_message = f"{current_player} drew {card_color.upper()}, but no {card_color} tile ahead — moved to END and won!"

    if session['players'][current_player] == len(board) - 1 and not session.get('winner'):
        session['winner'] = current_player
        log_message = f"{current_player} landed on the END and won!"

    event_log.append(log_message)
    session['events'] = event_log
    session['turn'] += 1

    # Save log entry to file
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

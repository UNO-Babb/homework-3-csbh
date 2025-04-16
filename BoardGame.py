#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template, redirect, url_for, session
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

@app.route('/draw')
def draw_card():
    if session.get('winner'):
        return redirect(url_for('index'))

    card_color = random.choice(COLORS)
    current_player = PLAYERS[session['turn'] % 4]
    position = session['players'][current_player]
    board = session['board']

    # Try to find the next tile of the drawn color
    moved = False
    for i in range(position + 1, len(board)):
        if board[i] == card_color:
            session['players'][current_player] = i
            moved = True
            break

    # If no tile found, move to 'end' and win
    if not moved:
        session['players'][current_player] = len(board) - 1  # index of 'end'
        session['winner'] = current_player

    # If landed on end tile by matching color, mark as winner too
    if session['players'][current_player] == len(board) - 1:
        session['winner'] = current_player

    session['turn'] += 1
    return redirect(url_for('index'))


@app.route('/reset')
def reset_game():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

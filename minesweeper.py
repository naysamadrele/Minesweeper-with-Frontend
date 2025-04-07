from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

class Minesweeper:
    def __init__(self, width=10, height=10, num_mines=10):
        self.width = width
        self.height = height
        self.num_mines = min(num_mines, width * height - 1)
        self.board = [[' ' for _ in range(width)] for _ in range(height)]
        self.mines = [[False for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flagged = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.win = False
        self.first_move = True
        self.start_time = None
        self.end_time = None

    def place_mines(self, first_x, first_y):
        positions = [(x, y) for x in range(self.width) for y in range(self.height) 
                    if not (x == first_x and y == first_y)]
        mine_positions = random.sample(positions, self.num_mines)
        
        for x, y in mine_positions:
            self.mines[y][x] = True
            
        self.calculate_numbers()

    def calculate_numbers(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.mines[y][x]:
                    count = self.count_adjacent_mines(x, y)
                    if count > 0:
                        self.board[y][x] = str(count)
                    else:
                        self.board[y][x] = ' '
                else:
                    self.board[y][x] = '*'

    def count_adjacent_mines(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.mines[ny][nx]:
                    count += 1
        return count

    def reveal(self, x, y):
        if self.first_move:
            self.start_time = time.time()
            self.place_mines(x, y)
            self.first_move = False
            
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
            
        if self.revealed[y][x] or self.flagged[y][x]:
            return False
            
        self.revealed[y][x] = True
        
        if self.mines[y][x]:
            self.game_over = True
            self.end_time = time.time()
            return False
            
        if self.board[y][x] == ' ':
            self.flood_fill(x, y)
            
        self.check_win()
        return True

    def flood_fill(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not self.revealed[ny][nx] and not self.flagged[ny][nx]:
                    self.revealed[ny][nx] = True
                    if self.board[ny][nx] == ' ':
                        self.flood_fill(nx, ny)

    def toggle_flag(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
            
        if self.revealed[y][x]:
            return False
            
        self.flagged[y][x] = not self.flagged[y][x]
        self.check_win()
        return True

    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.mines[y][x] and not self.revealed[y][x]:
                    return False
                    
        self.win = True
        self.game_over = True
        self.end_time = time.time()
        return True

    def to_dict(self):
        return {
            'width': self.width,
            'height': self.height,
            'board': self.board,
            'mines': self.mines,
            'revealed': self.revealed,
            'flagged': self.flagged,
            'game_over': self.game_over,
            'win': self.win,
            'remaining_mines': self.num_mines - sum(row.count(True) for row in self.flagged),
            'elapsed_time': int(time.time() - self.start_time) if self.start_time and not self.end_time else 0
        }

game = None

@app.route('/start', methods=['POST'])
def start_game():
    global game
    data = request.json
    width = data.get('width', 10)
    height = data.get('height', 10)
    difficulty = data.get('difficulty', 'medium')
    if difficulty == 'easy':
        num_mines = int(width * height * 0.1)
    elif difficulty == 'medium':
        num_mines = int(width * height * 0.15)
    elif difficulty == 'hard':
        num_mines = int(width * height * 0.2)
    else:  # expert
        num_mines = int(width * height * 0.25)
    game = Minesweeper(width, height, num_mines)
    return jsonify(game.to_dict()), 200

@app.route('/reveal', methods=['POST'])
def reveal():
    global game
    if not game:
        return jsonify({'error': 'Game not started'}), 400
    data = request.json
    x = data['x']
    y = data['y']
    result = game.reveal(x, y)
    return jsonify({'result': result, 'game': game.to_dict()}), 200

@app.route('/flag', methods=['POST'])
def flag():
    global game
    if not game:
        return jsonify({'error': 'Game not started'}), 400
    data = request.json
    x = data['x']
    y = data['y']
    result = game.toggle_flag(x, y)
    return jsonify({'result': result, 'game': game.to_dict()}), 200

if __name__ == '__main__':
    app.run(debug=True)
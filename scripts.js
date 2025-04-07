// Helper functions to interact with the backend API
async function startGame(width, height, difficulty) {
    const response = await fetch('http://127.0.0.1:5000/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ width, height, difficulty })
    });
    return response.json();
}

async function revealCell(x, y) {
    const response = await fetch('http://127.0.0.1:5000/reveal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ x, y })
    });
    return response.json();
}

async function flagCell(x, y) {
    const response = await fetch('http://127.0.0.1:5000/flag', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ x, y })
    });
    return response.json();
}

document.getElementById('start-game').addEventListener('click', async () => {
    const difficulty = document.getElementById('difficulty').value;
    let width, height;
    const boardSize = document.getElementById('board-size').value;
    if (boardSize === 'small') {
        width = 8;
        height = 8;
    } else if (boardSize === 'medium') {
        width = 12;
        height = 12;
    } else if (boardSize === 'large') {
        width = 16;
        height = 16;
    } else {
        width = parseInt(document.getElementById('custom-width').value, 10);
        height = parseInt(document.getElementById('custom-height').value, 10);
        width = Math.max(5, Math.min(30, width));
        height = Math.max(5, Math.min(30, height));
    }
    const gameData = await startGame(width, height, difficulty);
    renderBoard(gameData);
    startGameLoop(gameData);
});

document.getElementById('board-size').addEventListener('change', (event) => {
    if (event.target.value === 'custom') {
        document.getElementById('custom-size').style.display = 'block';
    } else {
        document.getElementById('custom-size').style.display = 'none';
    }
});

function renderBoard(game) {
    const boardElement = document.getElementById('board');
    boardElement.innerHTML = '';
    boardElement.style.gridTemplateColumns = `repeat(${game.width}, 30px)`;
    for (let y = 0; y < game.height; y++) {
        for (let x = 0; x < game.width; x++) {
            const cellElement = document.createElement('div');
            cellElement.classList.add('cell');
            cellElement.dataset.x = x;
            cellElement.dataset.y = y;
            cellElement.addEventListener('click', async () => {
                const gameData = await revealCell(x, y);
                renderBoard(gameData.game);
                updateStatus(gameData.game);
            });
            cellElement.addEventListener('contextmenu', async (event) => {
                event.preventDefault();
                const gameData = await flagCell(x, y);
                renderBoard(gameData.game);
                updateStatus(gameData.game);
            });
            if (game.revealed[y][x]) {
                cellElement.classList.add('revealed');
                if (game.mines[y][x]) {
                    cellElement.classList.add('mine');
                } else {
                    cellElement.textContent = game.board[y][x];
                }
            } else if (game.flagged[y][x]) {
                cellElement.textContent = 'F';
            }
            boardElement.appendChild(cellElement);
        }
    }
}

function updateStatus(game) {
    document.getElementById('remaining-mines').textContent = `Remaining mines: ${game.remaining_mines}`;
    document.getElementById('timer').textContent = `Time: ${game.elapsed_time}`;
}

function startGameLoop(game) {
    const intervalId = setInterval(async () => {
        if (game.game_over) {
            clearInterval(intervalId);
            if (game.win) {
                alert(`Congratulations! You won in ${game.elapsed_time}!`);
            } else {
                alert('Game Over! You hit a mine.');
                renderBoard(game);
            }
        } else {
            const gameData = await revealCell(-1, -1); // Dummy call to update the timer
            updateStatus(gameData.game);
        }
    }, 1000);
}
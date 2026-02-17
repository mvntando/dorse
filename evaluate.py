# material
# PST
# pawn structure
# king safety
# mobility

from dorse import Position

PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000
}

def evaluate(position: Position) -> int:
    score = 0
    for rows in position.board:
        for piece in rows:
            if piece != '.':
                score += PIECE_VALUES[piece]

    return score if position.sd == 'w' else -score

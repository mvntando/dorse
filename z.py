import dorse, utils
import numpy as np
from collections import namedtuple

BOARD = np.array([
    ['.', '.', '.', '.', 'k', '.', '.', 'r'],
    ['.', '.', '.', '.', '.', 'q', '.', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', 'P'],
    ['.', '.', '.', '.', 'K', '.', '.', 'R']
], dtype='U1')
BOARD = np.flipud(BOARD)

Move = namedtuple('Move', ('src', 'dst', 'promo'))

position = dorse.Position(BOARD, 0, (0, 1), (0, 1), None, None, 'w')
moves = position.gen_moves()

i = 0
for move in moves:
    if not position.is_legal(move):
        continue
    i += 1
    promo = f" promo: {move.promo}" if move.promo else ""
    print(f"{i}: {utils.notation(move.src)} -> {utils.notation(move.dst)}{promo}")

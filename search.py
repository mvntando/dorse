# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table (later)

# search.py

from dorse import Position, Move
from utils import checkmate
from eval import evaluate
import helpers # <-- DEBUG

INF = 10**9
MATE = INF - 1

def search(position: 'Position', depth: int = 4) -> 'Move | None':
    """
    Iterative deepening search to find the best move.  
    """
    best_move = None
    alpha = -INF
    beta = INF

    for move in position.gen_moves():
        position.push(move)
        score = -alphabeta(position, depth - 1, -beta, -alpha)
        position.pop()

        if score > alpha:
            alpha = score
            best_move = move

    return best_move

def alphabeta(position: 'Position', depth: int, alpha: int, beta: int) -> int:
    """
    Alpha-beta pruning search algorithm.
    """
    if depth == 0:
        return evaluate(position)

    moves = position.gen_moves()
    if not moves:
        if checkmate(position):
            return -MATE + depth  # Checkmate
        else:
            return 0  # stalemate

    for move in moves:
        position.push(move)
        score = -alphabeta(position, depth - 1, -beta, -alpha)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table (later)

# search.py

from dorse import Position, Move
from eval import evaluate
from constants import INF


def search(position: 'Position', depth: int = 4) -> 'Move | None':
    """
    Top-level search. Returns the best move for the current side to move.
    """
    best_move = None
    alpha = -INF
    beta = INF

    for move in position.gen_moves():
        new_pos = position.copy()
        new_pos.move(move)

        score = -alphabeta(new_pos, depth - 1, -beta, -alpha)

        if score > alpha:
            alpha = score
            best_move = move

    return best_move


def alphabeta(position: 'Position', depth: int, alpha: int, beta: int) -> int:
    """
    Negamax Alpha-Beta search.
    Returns the score for the side to move in `position`.
    """
    # Leaf node or depth 0
    if depth == 0:
        val = evaluate(position)
        # Adjust for side to move: + for white, - for black
        val = val if position.sd == 'w' else -val
        return val

    moves = position.gen_moves()
    if not moves:
        val = evaluate(position)
        val = val if position.sd == 'w' else -val
        return val

    for move in moves:
        new_pos = position.copy()
        new_pos.move(move)

        score = -alphabeta(new_pos, depth - 1, -beta, -alpha)

        if score >= beta:
            return score
        if score > alpha:
            alpha = score

    return alpha
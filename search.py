# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table (later)

# search.py

from dorse import Position, Move
from utils import check
from eval import evaluate

INF = 10**9
MATE = INF - 1

def search(position: 'Position', depth: int | None = None) -> Move | None: # TODO: Test
    """
    Search to find the best move.
    """
    MAX_DEPTH = 3
    if depth is None:
        depth = MAX_DEPTH # Default depth

    best_move = None
    alpha = -INF
    beta = INF

    moves = position.gen_moves()

    for move in moves:
        position.push(move)
        score = -alphabeta(position, -beta, -alpha, depth-1)
        position.pop()

        if score > alpha:
            alpha = score
            best_move = move

    return best_move

def alphabeta(position: 'Position', alpha: int, beta: int, depth: int) -> int: # TODO: Test
    """
    Alpha-beta pruning search algorithm.
    """
    if depth == 0:
        return quiescence(position, alpha, beta)

    moves = position.gen_moves() # TODO: Order moves

    if not moves:
        if check(position):
            return -MATE + depth # Checkmate
        else:
            return 0 # stalemate

    for move in moves:
        position.push(move)
        score = -alphabeta(position, -beta, -alpha, depth-1)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

def quiescence(position: Position, alpha: int, beta: int, qs_depth: int = 0) -> int: # TODO: Test 
    MAX_QS_DEPTH = 3

    static_eval = evaluate(position)
    if static_eval >= beta:
        return beta
    if static_eval > alpha:
        alpha = static_eval
    if qs_depth >= MAX_QS_DEPTH:
        return alpha
    
    moves = position.gen_captures()

    for move in moves:
        position.push(move)
        score = -quiescence(position, -beta, -alpha, qs_depth+1)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
                
    return alpha

def order(position: Position, moves: list[Move]) -> list[Move]:
    return [] # TODO: Implement move ordering
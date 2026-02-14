# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table (later)

# search.py

from dorse import Position, Move
from evaluate import evaluate
import helpers

INF = 1000000
MATE = 20000

def search(position: 'Position', depth: int | None = None) -> Move | None: # TODO: Test
    """
    Search to find the best move.
    """
    MAX_DEPTH = 6
    if depth is None:
        depth = MAX_DEPTH # Default depth

    best_move = None
    alpha = -INF
    beta = INF

    moves = position.gen_moves()

    for move in moves:
        mover = position.sd
        position.push(move)
        if position.in_check(mover): # Illegal move, skip
            position.pop()
            continue
        score = -alphabeta(position, -beta, -alpha, depth-1)
        position.pop()

        if best_move is None or score > alpha:
            alpha = score
            best_move = move
            
    return best_move

def alphabeta(position: 'Position', alpha: int, beta: int, depth: int) -> int: # TODO: Test
    """
    Alpha-beta pruning search algorithm.
    """
    if depth == 0:
        return quiescence(position, alpha, beta)

    legal_found = False
    moves = position.gen_captures() # TODO: Order moves

    for move in moves:
        mover = position.sd
        position.push(move)
        if position.in_check(mover): # Illegal move, skip
            position.pop()
            continue

        legal_found = True
        score = -alphabeta(position, -beta, -alpha, depth-1)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    moves = position.gen_quiets() # TODO: Order moves
    for move in moves:
        mover = position.sd
        position.push(move)
        if position.in_check(mover): # Illegal move, skip
            position.pop()
            continue

        legal_found = True
        score = -alphabeta(position, -beta, -alpha, depth-1)
        position.pop()

        if score >= beta:
            return score
        if score > alpha:
            alpha = score

    # Mate / stalemate detection AFTER all moves
    if not legal_found:
        if position.in_check(position.sd):
            return -MATE-depth # mate TODO: change depth to ply
        else:
            return 0 # stalemate

    return alpha

def quiescence(position: Position, alpha: int, beta: int, qs_depth: int = 0) -> int: # TODO: Test
    MAX_QSDEPTH = 4

    score = evaluate(position)
    if score >= beta:
        return beta
    if score > alpha:
        alpha = score
    if qs_depth >= MAX_QSDEPTH:
        return alpha
    
    moves = position.gen_captures()

    for move in moves:
        mover = position.sd
        position.push(move)
        if position.in_check(mover): # Illegal move, skip
            position.pop()
            continue

        score = -quiescence(position, -beta, -alpha, qs_depth+1)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
                
    return alpha

# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table (later)

# search.py

from dorse import Position, Move
from evaluate import evaluate

INF = 10**9

def search(position: 'Position', depth: int | None = None) -> Move | None: # TODO: Test
    """
    Search to find the best move.
    """
    MAX_DEPTH = 4
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

    for move in moves:
        mover = position.sd
        position.push(move)
        if position.in_check(mover): # Illegal move, skip
            position.pop()
            continue
        score = -alphabeta(position, -beta, -alpha, depth-1)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

def quiescence(position: Position, alpha: int, beta: int, qs_depth: int = 0) -> int: # TODO: Test 
    MAX_QSDEPTH = 3

    static_eval = evaluate(position)
    if static_eval >= beta:
        return beta
    if static_eval > alpha:
        alpha = static_eval
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

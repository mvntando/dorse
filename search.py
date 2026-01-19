# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table (later)

# search.py

from dorse import Position, Move
from utils import check, capture
from eval import evaluate, PIECE_ABS_VALUES

INF = 10**9
MATE = INF - 1

def search(position: 'Position', depth: int | None = None) -> Move | None: # TODO: Test
    """
    Iterative deepening search to find the best move.
    """
    MAX_DEPTH = 4
    if depth is None:
        depth = MAX_DEPTH  # Default depth

    best_move = None
    alpha = -INF
    beta = INF

    moves = position.gen_moves()

    for move in moves:
        position.push(move)
        score = -alphabeta(position, depth - 1, -beta, -alpha)
        position.pop()

        if score > alpha:
            alpha = score
            best_move = move

    return best_move

def alphabeta(position: 'Position', depth: int, alpha: int, beta: int) -> int: # TODO: Test
    """
    Alpha-beta pruning search algorithm.
    """
    if depth == 0:
        return quiescence(position, alpha, beta)

    moves = position.gen_moves()
    moves = order(position, moves)

    if not moves:
        if check(position):
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

def quiescence(position: Position, alpha: int, beta: int, qs_depth: int = 0) -> int: # TODO: Test
    MAX_QS_DEPTH = 4

    static_eval = evaluate(position)
    if static_eval >= beta:
        return beta
    if static_eval > alpha:
        alpha = static_eval

    if qs_depth >= MAX_QS_DEPTH:
        return alpha

    for move in position.gen_captures():
        position.push(move)
        score = -quiescence(position, -beta, -alpha, qs_depth+1)
        position.pop()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

def order(position: 'Position', moves: list[Move]) -> list[Move]: # TODO: Test
    scored_moves: list[tuple[Move, int]] = []
    for move in moves:
        score = 0  # Default for non-captures
        if capture(position, move):
            victim = position.board[move.dst[0]][move.dst[1]]
            attacker = position.board[move.src[0]][move.src[1]]

            victim_value = PIECE_ABS_VALUES.get(victim, 100)  # Default to pawn for en passant
            score = victim_value - PIECE_ABS_VALUES[attacker]
        
        scored_moves.append((move, score))
    
    scored_moves.sort(reverse=True, key=lambda x: x[1])
    return [move for move, score in scored_moves]

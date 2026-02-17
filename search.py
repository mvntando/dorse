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

def search(position: Position, depth: int | None = None) -> Move | None: # TODO: Test
    """
    Search to find the best move.
    """
    MAX_DEPTH = 6
    if depth is None:
        depth = MAX_DEPTH  # Default depth

    best_move = None
    alpha = -INF
    beta = INF

    moves = position.gen_moves()
    order(position, moves)  # Score moves
    for i in range(len(moves)):
        index = i  # best move index
        for j in range(i + 1, len(moves)):
            if moves[j].score > moves[index].score:
                index = j

        moves[i], moves[index] = moves[index], moves[i]

        move = moves[i]
        mover = position.sd
        position.push(move)
        if position.in_check(mover):  # Illegal move, skip
            position.pop()
            continue

        score = -alphabeta(position, -beta, -alpha, depth-1)
        position.pop()

        if best_move is None or score > alpha:
            alpha = score
            best_move = move
    
    return best_move

def alphabeta(position: Position, alpha: int, beta: int, depth: int) -> int: # TODO: Test
    """
    Alpha-beta pruning search algorithm.
    """
    if depth == 0:
        return quiescence(position, alpha, beta)

    found = False
    moves = position.gen_moves()
    order(position, moves)
    for i in range(len(moves)):
        index = i  # best move index
        for j in range(i + 1, len(moves)):
            if moves[j].score > moves[index].score:
                index = j

        moves[i], moves[index] = moves[index], moves[i]

        move = moves[i]
        mover = position.sd
        position.push(move)
        if position.in_check(mover):  # Illegal move, skip
            position.pop()
            continue

        found = True
        score = -alphabeta(position, -beta, -alpha, depth-1)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    # Mate / stalemate detection after all moves
    if not found:
        if position.in_check(position.sd):
            return -MATE-depth  # mate TODO: change depth to ply
        else:
            return 0  # stalemate

    return alpha

MAX_QSDEPTH = 4
def quiescence(position: Position, alpha: int, beta: int, qs_depth: int = 0) -> int: # TODO: Test
    """
    Quiescence search to evaluate "quiet" positions and avoid horizon effect.
    """    

    score = evaluate(position)
    if score >= beta:
        return beta
    if score > alpha:
        alpha = score
    if qs_depth >= MAX_QSDEPTH:
        return alpha
    
    moves = position.gen_captures()
    order(position, moves)
    for i in range(len(moves)):
        index = i  # best move index
        for j in range(i + 1, len(moves)):
            if moves[j].score > moves[index].score:
                index = j

        moves[i], moves[index] = moves[index], moves[i]

        move = moves[i]
        mover = position.sd
        position.push(move)
        if position.in_check(mover):  # Illegal move, skip
            position.pop()
            continue

        score = -quiescence(position, -beta, -alpha, qs_depth+1)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
                
    return alpha

# Score moves using MVV-LVA and store in move.score
PIECE_VALUE = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
}
def order(position: Position, moves: list[Move]):

    def mvv_lva(move: Move):
        """
        MVV-LVA (Most Valuable Victim - Least Valuable Attacker) move ordering
        """
        victim = position.board[move.dst[0]][move.dst[1]]
        if victim == '.':
            return 0
        attacker = position.board[move.src[0]][move.src[1]]
        return 10000 + PIECE_VALUE[victim] - PIECE_VALUE[attacker]

    for move in moves:
        move.score = mvv_lva(move)

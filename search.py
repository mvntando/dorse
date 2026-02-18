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

global Nodes

MAX_DEPTH = 6
MAX_PLY = 64
KILLERS: list[list[Move | None]] = [[None, None] for _ in range(MAX_PLY)]  # killer moves for each depth

def search(position: Position, depth: int | None = None) -> Move | None: # TODO: Test
    """
    Search to find the best move.
    """

    global Nodes
    Nodes = 0
    if depth is None:
        depth = MAX_DEPTH

    for i in range(MAX_DEPTH):  # Clear killer moves for new search
        KILLERS[i][0] = None
        KILLERS[i][1] = None

    best_move = None
    alpha = -INF
    beta = INF

    moves = position.gen_moves()
    order(moves, 0)
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

        score = -alphabeta(position, -beta, -alpha, depth-1, 1)
        position.pop()

        if best_move is None or score > alpha:
            alpha = score
            best_move = move

    print(f"Nodes: {Nodes}")
    return best_move

def alphabeta(position: Position, alpha: int, beta: int, depth: int, ply: int) -> int: # TODO: Test
    """
    Alpha-beta pruning search algorithm.
    """

    global Nodes
    Nodes += 1
    if depth == 0:
        return quiescence(position, alpha, beta, ply)

    found = False
    moves = position.gen_moves()
    order(moves, ply)
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
        score = -alphabeta(position, -beta, -alpha, depth-1, ply+1)
        position.pop()

        if score >= beta:
            if move.captured is None:
                if KILLERS[ply][0] != move:  #  killer moves
                    KILLERS[ply][1] = KILLERS[ply][0]
                    KILLERS[ply][0] = move
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

def quiescence(position: Position, alpha: int, beta: int, ply: int = 0) -> int: # TODO: Test
    """
    Quiescence search to evaluate "quiet" positions and avoid horizon effect.
    """

    global Nodes
    Nodes += 1
    score = evaluate(position)
    if score >= beta:
        return beta
    if score > alpha:
        alpha = score
    
    moves = position.gen_captures()
    order(moves, ply)
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

        score = -quiescence(position, -beta, -alpha, ply+1)
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
def order(moves: list[Move], depth: int) -> None:
    for move in moves:
        move.score = 0
        if move.captured is not None:
            attacker = move.piece
            victim = move.captured
            move.score = 100000 + PIECE_VALUE[victim] * 10 - PIECE_VALUE[attacker]

        else:
            if KILLERS[depth][0] is not None and move == KILLERS[depth][0]:
                move.score = 90000
            elif KILLERS[depth][1] is not None and move == KILLERS[depth][1]:
                move.score = 80000

# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table

from dorse import Position, Move
from evaluate import evaluate, PIECE_VALUES
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

    for i in range(depth):  # Clear killer moves for new search
        KILLERS[i][0] = None
        KILLERS[i][1] = None

    best_move: Move | None = None

    for c_depth in range(1, depth + 1):  # Iterative deepening
        s_nodes = Nodes  # nodes at start of this iteration
        alpha = -INF
        beta = INF

        l_best = None  # local best move for this iteration
        moves = position.gen_moves()
        score_moves(moves, 0)

        if best_move is not None:  # try best_move first from previous iteration
            for m in moves:
                if m == best_move:
                    m.score = 10_000_000  # force first
                    break

        moves.sort(key=lambda m: m.score, reverse=True)

        for move in moves:
            mover = position.sd
            position.push(move)
            if position.in_check(mover):
                position.pop()
                continue

            score = -alphabeta(position, -beta, -alpha, c_depth - 1, 1)
            position.pop()

            if l_best is None or score > alpha:
                alpha = score
                l_best = move

        if l_best is not None:
            best_move = l_best

        print(f"info depth {c_depth} nodes {Nodes - s_nodes} score {alpha}")


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

    score_moves(moves, ply)
    moves.sort(key=lambda m: m.score, reverse=True)
    for move in moves:
        mover = position.sd
        position.push(move)
        if position.in_check(mover):  # Illegal move, skip
            position.pop()
            continue

        found = True
        score = -alphabeta(position, -beta, -alpha, depth - 1, ply + 1)
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
            return -MATE + ply  # mate
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
    score_moves(moves, ply)
    moves.sort(key=lambda m: m.score, reverse=True)
    for move in moves:
        mover = position.sd
        position.push(move)
        if position.in_check(mover):  # Illegal move, skip
            position.pop()
            continue

        score = -quiescence(position, -beta, -alpha, ply + 1)
        position.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
                
    return alpha

# Score moves using MVV-LVA and store in move.score
PIECE_VALUE = {p: abs(v) for p, v in PIECE_VALUES.items()}
def score_moves(moves: list[Move], depth: int) -> None:
    for move in moves:
        move.score = 0
        if move.captured is not None:
            attacker = move.piece
            victim = move.captured
            move.score = 100_000 + PIECE_VALUE[victim] * 10 - PIECE_VALUE[attacker]

        else:
            if KILLERS[depth][0] is not None and move == KILLERS[depth][0]:
                move.score = 90_000
            elif KILLERS[depth][1] is not None and move == KILLERS[depth][1]:
                move.score = 80_000

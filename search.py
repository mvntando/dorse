# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table

from dorse import Position, Move
from evaluate import evaluate, PIECE_VALUES

INF = 1_000_000
MATE = 20_000

global Nodes

TT = {}  # Transposition Table

# Flags
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

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

    TT.clear()  # Clear transposition table for new search
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
        moves.sort(key=lambda m: m.score, reverse=True)

        if best_move is not None:  # try best_move first from previous iteration
            if best_move in moves:
                moves.remove(best_move)
                moves.insert(0, best_move)

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

def alphabeta(position: Position, alpha: int, beta: int, depth: int, ply: int) -> int:
    """
    Alpha-beta pruning search algorithm.
    """

    global Nodes, TT
    Nodes += 1

    og_alpha = alpha
    key = position.hash
    entry = TT.get(key)

    # TT probe
    if entry:
        entry_depth, entry_score, entry_flag, entry_move = TT[key]

        if entry_depth >= depth:
            if entry_flag == EXACT:
                return entry_score
            elif entry_flag == LOWERBOUND and entry_score >= beta:
                return entry_score
            elif entry_flag == UPPERBOUND and entry_score <= alpha:
                return entry_score

    if depth == 0:
        return qsearch(position, alpha, beta, ply)

    best_move = None
    best_score = -INF
    found = False

    moves = position.gen_moves()
    score_moves(moves, ply)
    moves.sort(key=lambda m: m.score, reverse=True)

    # TT move ordering
    if entry:
        tt_move = TT[key][3]
        if tt_move in moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)

    for move in moves:
        mover = position.sd
        position.push(move)

        if position.in_check(mover):
            position.pop()
            continue

        found = True

        score = -alphabeta(position, -beta, -alpha, depth - 1, ply + 1)
        position.pop()

        if score > best_score:
            best_score = score
            best_move = move

        if score >= beta:
            TT[key] = (depth, score, LOWERBOUND, best_move)

            if move.captured is None:
                if KILLERS[ply][0] != move:
                    KILLERS[ply][1] = KILLERS[ply][0]
                    KILLERS[ply][0] = move

            return score

        if score > alpha:
            alpha = score

    if not found:
        if position.in_check(position.sd):
            return -MATE + ply  # mate
        else:
            return 0  # stalemate

    # TT store
    if best_score <= og_alpha:
        flag = UPPERBOUND
    else:
        flag = EXACT

    TT[key] = (depth, best_score, flag, best_move)

    return best_score

def qsearch(position: Position, alpha: int, beta: int, ply: int = 0) -> int: # TODO: Test
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

        score = -qsearch(position, -beta, -alpha, ply + 1)
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

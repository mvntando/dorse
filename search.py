# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table

import time
from dorse import Position, Move
from evaluation import Evaluator, PIECE_VALUE

INF = 1_000_000
MATE = 20_000

MAX_DEPTH = 64
MAX_PLY = 64

# TT entry flags
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

class Searcher:
    TT: dict
    KILLERS: list[list[Move | None]]

    __slots__ = ("position", "TT", "KILLERS", "Nodes", "stop", "start_time", "time_limit")

    def __init__(self, position: Position):
        self.position = position

        self.TT = {}  # Transposition Table
        self.KILLERS = [[None, None] for _ in range(MAX_PLY)]
        self.Nodes = 0

        self.stop = False
        self.start_time = time.perf_counter()
        self.time_limit = 0

    def search(self, depth: int | None = None, movetime: float | None = None) -> Move | None:
        """
        Search to find the best move.
        """

        position = self.position
        TT = self.TT
        KILLERS = self.KILLERS
        self.Nodes = 0

        if depth is None:
            depth = MAX_DEPTH

        if movetime is not None:
            self.time_limit = movetime
        else:
            self.time_limit = None

        TT.clear()  # Clear transposition table for new search
        for i in range(depth):  # Clear killer moves for new search
            KILLERS[i][0] = None
            KILLERS[i][1] = None

        best_move: Move | None = None

        for c_depth in range(1, depth + 1):  # Iterative deepening
            if self.time_up():
                break

            s_nodes = self.Nodes  # nodes at start of this iteration
            alpha = -INF
            beta = INF

            l_best = None  # local best move for this iteration
            moves = position.gen_moves()
            self.score_moves(moves, 0)
            moves.sort(key=lambda m: m.score, reverse=True)

            if best_move is not None:  # try best_move first from previous iteration
                if best_move in moves:
                    moves.remove(best_move)
                    moves.insert(0, best_move)

            for move in moves:
                if self.time_up():
                    break

                mover = position.sd
                position.push(move)
                if position.in_check(mover):
                    position.pop()
                    continue

                score = -self.alphabeta(-beta, -alpha, c_depth - 1, 1)
                position.pop()

                if l_best is None or score > alpha:
                    alpha = score
                    l_best = move

            if self.stop:
                break

            if l_best is not None:
                best_move = l_best

            print(f"info depth {c_depth} nodes {self.Nodes - s_nodes} score {alpha}")

        print(f"Nodes: {self.Nodes}")
        return best_move

    def alphabeta(self, alpha: int, beta: int, depth: int, ply: int) -> int:
        """
        Alpha-beta pruning search algorithm.
        """

        if self.stop:
            return 0

        if self.time_up():
            return 0

        position = self.position
        TT = self.TT
        KILLERS = self.KILLERS
        self.Nodes += 1

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
            return self.qsearch(alpha, beta, ply)

        best_move = None
        best_score = -INF
        found = False

        moves = position.gen_moves()
        self.score_moves(moves, ply)
        moves.sort(key=lambda m: m.score, reverse=True)

        # TT move ordering
        if entry:
            tt_move = TT[key][3]
            if tt_move in moves:
                moves.remove(tt_move)
                moves.insert(0, tt_move)

        for move in moves:
            if self.stop:
                return 0

            mover = position.sd
            position.push(move)

            if position.in_check(mover):
                position.pop()
                continue

            found = True

            score = -self.alphabeta(-beta, -alpha, depth - 1, ply + 1)
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

    def qsearch(self, alpha: int, beta: int, ply: int = 0) -> int:
        """
        Quiescence search to evaluate "quiet" positions and avoid horizon effect.
        """

        if self.stop:
            return 0

        if self.time_up():
            return 0

        position = self.position
        self.Nodes += 1

        score = Evaluator(position).evaluate()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
        
        moves = position.gen_captures()
        self.score_moves(moves, ply)
        moves.sort(key=lambda m: m.score, reverse=True)
        for move in moves:
            mover = position.sd
            position.push(move)
            if position.in_check(mover):  # Illegal move, skip
                position.pop()
                continue

            score = -self.qsearch(-beta, -alpha, ply + 1)
            position.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    
        return alpha

    # Score moves using MVV-LVA and store in move.score
    def score_moves(self, moves: list[Move], depth: int) -> None:
        KILLERS = self.KILLERS
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

    def time_up(self):
        if self.time_limit is None:
            return False
        if time.perf_counter() - self.start_time >= self.time_limit * 0.98:
            self.stop = True
            return True
        return False

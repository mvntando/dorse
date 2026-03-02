# minimax / alpha-beta
# iterative deepening
# quiescence
# move ordering
# transposition table

import time
from dorse import Position, Move
from evaluation import Evaluator, PIECE_VALUE
from utils import PIECE_INDEX

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
    HH: list[list[int]]
    KILLERS: list[list[Move | None]]

    __slots__ = ('TT', 'HH', 'KILLERS', 'Nodes', 'stop', 'start_time', 'time_limit')

    def __init__(self):
        self.TT = {}  # Transposition Table
        self.HH = [[0] * 64 for _ in range(12)]
        self.KILLERS = [[None, None] for _ in range(MAX_PLY)]
        self.Nodes = 0

    def search(self, position: Position, depth: int | None = None, movetime: float | None = None) -> Move | None:
        """
        Search to find the best move.
        """

        self.Nodes = 0
        self.stop = False
        self.start_time = time.perf_counter()

        if depth is None:
            depth = MAX_DEPTH

        if movetime is not None:
            self.time_limit = movetime
        else:
            self.time_limit = None

        best_move: Move | None = None

        for c_depth in range(1, depth + 1):  # Iterative deepening
            if self.time_up():
                break

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

                score = -self.alphabeta(position, -beta, -alpha, c_depth - 1, 1)
                position.pop()

                if l_best is None or score > alpha:
                    alpha = score
                    l_best = move

            if self.stop:
                break

            if l_best is not None:
                best_move = l_best

            elapsed = int((time.perf_counter() - self.start_time) * 1000)
            nps = int(self.Nodes * 1000 / elapsed) if elapsed > 0 else 0
            print(f"info depth {c_depth} score cp {alpha} nodes {self.Nodes} time {elapsed} nps {nps} localbest {l_best.uci() if l_best else '0000'}")

        return best_move

    def alphabeta(self, position: Position, alpha: int, beta: int, depth: int, ply: int) -> int:
        """
        Alpha-beta pruning search algorithm.
        """

        if self.stop:
            return 0
        if self.time_up():
            return 0
        
        if depth == 0:
            return self.qsearch(position, alpha, beta, ply)
        
        TT = self.TT
        HH = self.HH
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
                
        # Null Move Pruning
        if depth >= 3 and not position.in_check(position.sd):
            R = 2
            position.push_null()
            score = -self.alphabeta(position, -beta, -beta + 1, depth - 1 - R, ply + 1)
            position.pop_null()
            if score >= beta:
                return beta

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

            score = -self.alphabeta(position, -beta, -alpha, depth - 1, ply + 1)
            position.pop()

            if score > best_score:
                best_score = score
                best_move = move

            if score >= beta:
                TT[key] = (depth, score, LOWERBOUND, best_move)

                if move.captured is None:
                    # Update heuristics
                    piece_index = PIECE_INDEX[move.piece]
                    to_sq = move.dst[0] * 8 + move.dst[1]
                    HH[piece_index][to_sq] += depth * depth

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

    def qsearch(self, position: Position, alpha: int, beta: int, ply: int = 0) -> int:
        """
        Quiescence search to evaluate "quiet" positions and avoid horizon effect.
        """

        if self.stop:
            return 0

        if self.time_up():
            return 0

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

            score = -self.qsearch(position, -beta, -alpha, ply + 1)
            position.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    
        return alpha

    # Score moves using MVV-LVA and store in move.score
    def score_moves(self, moves: list[Move], ply: int) -> None:
        KILLERS = self.KILLERS
        for move in moves:
            move.score = 0
            # captures: mvv-lva
            if move.captured is not None:
                attacker = move.piece
                victim = move.captured
                move.score = 100_000 + PIECE_VALUE[victim] * 10 - PIECE_VALUE[attacker]

            # killer moves
            else:
                if KILLERS[ply][0] is not None and move == KILLERS[ply][0]:
                    move.score = 90_000
                elif KILLERS[ply][1] is not None and move == KILLERS[ply][1]:
                    move.score = 80_000

                else:
                    piece_index = PIECE_INDEX[move.piece]
                    to_sq = move.dst[0] * 8 + move.dst[1]
                    move.score += self.HH[piece_index][to_sq]

    def time_up(self):
        if self.time_limit is None:
            return False
        if time.perf_counter() - self.start_time >= self.time_limit:
            self.stop = True
            return True
        return False

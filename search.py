# Basic alpha-beta search with iterative deepening
import math
import time
from dorse import Position, Move
from evaluation import PIECE_VALUE
from utils import PIECE_INDEX

INF = 1_000_000
MATE = 20_000

MAX_DEPTH = 64
MAX_PLY = 64

# tt entry flags
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

class Searcher:
    tt: list[tuple[int, int, int, Move | None, int] | None]
    hh: list[list[int]]
    killers: list[list[Move | None]]
    pv: list[list[Move | None]]

    __slots__ = ('tt_size', 'tt_mask', 'tt', 'hh', 'killers', 'nodes', 'pv', 'pv_len', 'stop', 'start_time', 'time_limit')

    def __init__(self):
        self.tt_size = 1 << 19  # 512K entries
        self.tt_mask = self.tt_size - 1
        self.tt = [None] * self.tt_size
        self.hh = [[0] * 64 for _ in range(12)]
        self.killers = [[None, None] for _ in range(MAX_PLY)]
        self.nodes = 0
        self.pv = [[None] * MAX_PLY for _ in range(MAX_PLY)]
        self.pv_len = [0] * MAX_PLY

    def search(self, position: Position, depth: int | None = None, movetime: float | None = None) -> Move | None:
        """
        Search to find the best move.
        """

        self.nodes = 0
        self.stop = False
        self.start_time = time.perf_counter()

        if depth is None:
            depth = MAX_DEPTH

        if movetime is not None:
            self.time_limit = movetime
        else:
            self.time_limit = None

        best_move: Move | None = None

        for c_depth in range(1, depth + 1):  # ID
            if self.time_up():
                break

            alpha = -INF
            beta = INF

            l_best = None
            moves = position.gen_moves()
            self.score_moves(moves, 0)
            if best_move is not None and best_move in moves:
                best_move.score = 10_000_000
            moves.sort(key=lambda m: m.score, reverse=True)

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

                if score > alpha:
                    alpha = score
                    l_best = move

                    self.pv[0][0] = move  # update PV
                    for i in range(1, self.pv_len[1]):
                        self.pv[0][i] = self.pv[1][i]
                    self.pv_len[0] = self.pv_len[1]

            if self.stop:
                break

            if l_best is not None:
                best_move = l_best

            elapsed = int((time.perf_counter() - self.start_time) * 1000)
            nps = int(self.nodes * 1000 / elapsed) if elapsed > 0 else 0
            pv_moves = self.pv[0][:self.pv_len[0]]
            pv_str = " ".join(m.uci() for m in pv_moves if m)

            print(f"info depth {c_depth} score cp {alpha} nodes {self.nodes} time {elapsed} nps {nps} pv {pv_str}")

        return best_move

    def alphabeta(self, position: Position, alpha: int, beta: int, depth: int, ply: int) -> int:
        """
        Alpha-beta pruning search algorithm.
        """

        if self.stop:
            return 0
        if self.time_up():
            return 0
        
        if depth <= 0:
            return self.qsearch(position, alpha, beta, ply)
        
        hh = self.hh
        killers = self.killers
        self.nodes += 1
        self.pv_len[ply] = ply

        og_alpha = alpha
        key = position.hash
        entry = self.tt_lookup(key)

        # tt probe
        if entry:
            entry_depth, entry_score, entry_flag, entry_move, _ = entry

            if entry_depth >= depth:
                if entry_flag == EXACT:
                    return entry_score
                elif entry_flag == LOWERBOUND and entry_score >= beta:
                    return entry_score
                elif entry_flag == UPPERBOUND and entry_score <= alpha:
                    return entry_score
                
        # NMP
        if depth >= 3 and not position.in_check(position.sd):
            R = 2
            position.push_null()
            score = -self.alphabeta(position, -beta, -beta + 1, depth - 1 - R, ply + 1)
            position.pop_null()
            if score >= beta:
                return beta

        best_move = None
        best_score = -INF
        found = 0

        moves = position.gen_moves()
        self.score_moves(moves, ply)
        # tt move ordering
        if entry:
            tt_move = entry[3]  # index 3 is best_move
            for m in moves:
                if m == tt_move:
                    m.score = 10_000_000
                    break
        moves.sort(key=lambda m: m.score, reverse=True)

        for move in moves:
            if self.stop:
                return 0
            
            mover = position.sd
            position.push(move)
            if position.in_check(mover):
                position.pop()
                continue

            found += 1

            # LMR
            lmr = (depth >= 3 and found > 4 and not move.captured and not move.promo and not position.in_check(position.sd))
            if lmr:
                reduction = max(1, int(math.log(depth) * math.log(found) / 2))
                score = -self.alphabeta(position, -alpha - 1, -alpha, depth - 1 - reduction, ply + 1)
                if score > alpha:  # re-search full depth
                    score = -self.alphabeta(position, -beta, -alpha, depth - 1, ply + 1)
            else:
                score = -self.alphabeta(position, -beta, -alpha, depth - 1, ply + 1)

            position.pop()

            if score > best_score:
                best_score = score
                best_move = move

            if score >= beta:
                self.tt_store(depth, score, LOWERBOUND, best_move, key)

                if move.captured is None:
                    # Update heuristics
                    piece_index = PIECE_INDEX[move.piece]
                    to_sq = move.dst[0] * 8 + move.dst[1]
                    hh[piece_index][to_sq] += depth * depth

                    if killers[ply][0] != move:
                        killers[ply][1] = killers[ply][0]
                        killers[ply][0] = move

                return score

            if score > alpha:
                alpha = score

                self.pv[ply][ply] = move  # update PV
                for i in range(ply + 1, self.pv_len[ply + 1]):
                    self.pv[ply][i] = self.pv[ply + 1][i]
                self.pv_len[ply] = self.pv_len[ply + 1]

        if not found:
            if position.in_check(position.sd):
                return -MATE + ply  # mate
            else:
                return 0  # stalemate

        # tt store
        if best_score <= og_alpha:
            flag = UPPERBOUND
        elif best_score >= beta:
            flag = LOWERBOUND
        else:
            flag = EXACT

        self.tt_store(depth, best_score, flag, best_move, key)

        return best_score

    def qsearch(self, position: Position, alpha: int, beta: int, ply: int) -> int:
        """
        Quiescence search to evaluate "quiet" positions and avoid horizon effect.
        """

        if self.stop:
            return 0
        if self.time_up():
            return 0

        self.nodes += 1
        self.pv_len[ply] = ply

        score = position.eval if position.sd == 'w' else -position.eval
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

        if position.in_check(position.sd):
            moves = position.gen_moves()
        else:
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
    
    def tt_store(self, depth: int, score: int, flag: int, move: Move | None, key: int) -> None:
        idx = key & self.tt_mask
        existing = self.tt[idx]
        if existing is None or depth >= existing[0]:
            self.tt[idx] = (depth, score, flag, move, key)

    def tt_lookup(self, key: int) -> tuple[int, int, int, Move | None, int] | None:
        idx = key & self.tt_mask
        entry = self.tt[idx]
        if entry and entry[4] == key:  # verify not a collision
            return entry  # (depth, score, flag, move, key)
        return None

    # Score moves using MVV-LVA and store in move.score
    def score_moves(self, moves: list[Move], ply: int) -> None:
        killers = self.killers
        for move in moves:
            move.score = 0
            # captures: mvv-lva
            if move.captured is not None:
                attacker = move.piece
                victim = move.captured
                move.score = 100_000 + PIECE_VALUE[victim] * 10 - PIECE_VALUE[attacker]

            else:  # killer moves
                if killers[ply][0] is not None and move == killers[ply][0]:
                    move.score = 90_000
                elif killers[ply][1] is not None and move == killers[ply][1]:
                    move.score = 80_000

                else:  # history heuristic
                    piece_index = PIECE_INDEX[move.piece]
                    to_sq = move.dst[0] * 8 + move.dst[1]
                    move.score += self.hh[piece_index][to_sq]

    def time_up(self) -> bool:
        if self.time_limit is None:
            return False
        if time.perf_counter() - self.start_time >= self.time_limit:
            self.stop = True
            return True
        return False

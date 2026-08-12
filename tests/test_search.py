from dorse import Position, Move
from utils import *
from search import Searcher
from evaluate import PIECE_VALUES

# TESTS FOR SEARCH MODULE

# SEARCH TESTS
def test_search_pv_correctness():
    position = Position(*parse_fen("8/kP1K4/P1P5/3N4/6P1/8/6P1/8 b - - 2 58"))  # other fens do fail, e.g "8/kP1K4/P1P5/3N4/6P1/8/6P1/8 b - - 2 58" at depth > 5
    searcher = Searcher()
    searcher.search(position, depth=3)

    pv = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv) == 3, f"pv={pv}, len={len(pv)}, expected depth={3}"

def test_search_pv_correctness_multisearch():
    position = Position(*parse_fen(STARTPOS))
    searcher = Searcher()

    searcher.search(position, depth=3)
    pv3 = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv3) == 3, f"pv={pv3}, len={len(pv3)}, expected depth=3"

    searcher.search(position, depth=3)
    pv3 = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv3) == 3, f"pv={pv3}, len={len(pv3)}, expected depth=3"

def test_search_pv_correctness_deepsearch():
    position = Position(*parse_fen(STARTPOS))
    searcher = Searcher()

    searcher.search(position, depth=3)
    pv3 = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv3) == 3, f"pv={pv3}, len={len(pv3)}, expected depth=3"

    searcher.search(position, depth=5)
    pv5 = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv5) == 5, f"pv={pv5}, len={len(pv5)}, expected depth=5"

# SEE TESTS
def test_see():
    position = Position(*parse_fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1"))
    searcher = Searcher()

    move = Move((4, 7), (6, 7), 0, 0, -1)
    assert searcher.see(position, move) == PIECE_VALUES[PAWN] - PIECE_VALUES[QUEEN]

    move = Move((4, 7), (6, 5), 0, 0, -1)
    assert searcher.see(position, move) == PIECE_VALUES[PAWN]

def test_see_value():
    position = Position(*parse_fen("q7/1n6/r7/P7/Q7/8/R7/R7 b - - 0 1"))
    searcher = Searcher()

    move = Move((6, 1), (4, 0), 0, -2, 1)
    assert searcher.see(position, move) == PIECE_VALUES[PAWN]

def test_see_xray():
    position = Position(*parse_fen("q7/r7/r7/P7/R7/8/R7/Q7 b - - 0 1"))
    searcher = Searcher()

    move = Move((5, 0), (4, 0), 0, -4, 1)
    assert searcher.see(position, move) == -PIECE_VALUES[ROOK] + PIECE_VALUES[PAWN]

def test_see_illegal_king():
    position = Position(*parse_fen("8/r7/k7/p7/R7/R7/8/8 w - - 0 1"))
    searcher = Searcher()

    move = Move((3, 0), (4, 0), 0, -4, 1)
    assert searcher.see(position, move) == PIECE_VALUES[PAWN]

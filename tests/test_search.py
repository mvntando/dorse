from dorse import Position
from utils import parse_fen, START_POS 
from search import Searcher

# TESTS FOR SEARCH MODULE

def test_search_pv_correctness():
    position = Position(*parse_fen("8/kP1K4/P1P5/3N4/6P1/8/6P1/8 b - - 2 58"))  # other fens do fail, e.g "8/kP1K4/P1P5/3N4/6P1/8/6P1/8 b - - 2 58" at depth > 5
    searcher = Searcher()
    searcher.search(position, depth=3)

    pv = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv) == 3, f"pv={pv}, len={len(pv)}, expected depth={3}"

def test_search_pv_correctness_multisearch():
    position = Position(*parse_fen(START_POS))
    searcher = Searcher()

    searcher.search(position, depth=3)
    pv3 = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv3) == 3, f"pv={pv3}, len={len(pv3)}, expected depth=3"

    searcher.search(position, depth=3)
    pv3 = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv3) == 3, f"pv={pv3}, len={len(pv3)}, expected depth=3"

def test_search_pv_correctness_deepsearch():
    position = Position(*parse_fen(START_POS))
    searcher = Searcher()

    searcher.search(position, depth=3)
    pv3 = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv3) == 3, f"pv={pv3}, len={len(pv3)}, expected depth=3"

    searcher.search(position, depth=5)
    pv5 = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv5) == 5, f"pv={pv5}, len={len(pv5)}, expected depth=5"

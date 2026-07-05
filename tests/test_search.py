from dorse import Position
from utils import parse_fen, START_POS 
from search import Searcher

# TESTS FOR SEARCH MODULE

def test_search_pv_correctness():
    position = Position(*parse_fen(START_POS))
    searcher = Searcher()
    depth = 3
    searcher.search(position, depth=depth)

    pv = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv) == depth, f"pv={pv}, len={len(pv)}, expected depth={depth}"

def test_search_pv_correctness_multisearch():
    position = Position(*parse_fen(START_POS))
    searcher = Searcher()
    depth = 3
    searcher.search(position, depth=depth)

    depth = 3
    searcher.search(position, depth=depth)

    pv = searcher.pv[0][:searcher.pv_len[0]]
    assert len(pv) == depth, f"pv={pv}, len={len(pv)}, expected depth={depth}"

import dorse
from utils import parse_fen, attacked
from helpers import coord

# TESTS FOR UTILS MODULE

# PARSE FEN TESTS
INIT_BOARD = [
    ['R','N','B','Q','K','B','N','R'],  # y = 0 (rank 1)
    ['P','P','P','P','P','P','P','P'],  # y = 1
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['p','p','p','p','p','p','p','p'],  # y = 6
    ['r','n','b','q','k','b','n','r'],  # y = 7 (rank 8)
]

def test_parse_fen_white():
    board, wc, bc, ep, sd = parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    assert board == INIT_BOARD
    assert wc == (1, 1)
    assert bc == (1, 1)
    assert ep is None
    assert sd == 'w'

def test_parse_fen_black():
    board, wc, bc, ep, sd = parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1")

    assert board == INIT_BOARD
    assert wc == (1, 1)
    assert bc == (1, 1)
    assert ep is None
    assert sd == 'b'

def test_parse_fen_ep_white():
    *_, ep, _ = parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    assert ep == coord('d6')

def test_parse_fen_ep_black():
    *_, ep, _ = parse_fen("rnbqkbnr/ppp1pppp/8/8/3pP3/P4N2/1PPP1PPP/RNBQKB1R b KQkq e3 0 1")
    assert ep == coord('e3')

def test_parse_fen_castle_rights():
    _, wc, bc, ep, sd = parse_fen("r1bq1rk1/ppppbppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQ1RK1 w - - 0 1")

    assert wc == (0, 0)
    assert bc == (0, 0)
    assert ep is None
    assert sd == 'w'

def test_parse_fen_castle_rights_kingside_only():
    _, wc, bc, ep, sd = parse_fen("1rbqkbnr/pppppppp/2n5/8/8/2N5/PPPPPPPP/1RBQKBNR w Kk - 0 1")

    assert wc == (0, 1)
    assert bc == (0, 1)
    assert ep is None
    assert sd == 'w'

def test_parse_fen_castle_rights_queenside_only():
    _, wc, bc, ep, sd = parse_fen("rnbqkbr1/pppppppp/5n2/8/8/5N2/PPPPPPPP/RNBQKBR1 w Qq - 0 1")

    assert wc == (1, 0)
    assert bc == (1, 0)
    assert ep is None
    assert sd == 'w'


# ATTACKED TESTS
def test_attacked_white():
    board, wc, bc, ep, sd = parse_fen("bn1qk2r/6bp/8/8/8/8/6BP/BN1QK2R w - - 0 1")
    pos = dorse.Position(board, wc, bc, ep, sd)

    assert attacked(pos, coord('a3'), 'w') is True  # knight
    assert attacked(pos, coord('b2'), 'w') is True
    assert attacked(pos, coord('d3'), 'w') is True
    assert attacked(pos, coord('f2'), 'w') is True
    assert attacked(pos, coord('e4'), 'w') is True
    assert attacked(pos, coord('g3'), 'w') is True
    assert attacked(pos, coord('g1'), 'w') is True

def test_attacked_black():
    board, wc, bc, ep, sd = parse_fen("bn1qk2r/6bp/8/8/8/8/6BP/BN1QK2R w - - 0 1")
    pos = dorse.Position(board, wc, bc, ep, sd)

    assert attacked(pos, coord('a6'), 'b') is True
    assert attacked(pos, coord('b7'), 'b') is True
    assert attacked(pos, coord('d6'), 'b') is True
    assert attacked(pos, coord('f7'), 'b') is True
    assert attacked(pos, coord('e5'), 'b') is True
    assert attacked(pos, coord('g6'), 'b') is True
    assert attacked(pos, coord('g8'), 'b') is True
    
def test_attacked_false_white():
    board, wc, bc, ep, sd = parse_fen("1n2k2r/1b1q2bp/8/8/8/8/1B1Q2BP/1N2K2R w - - 0 1")
    pos = dorse.Position(board, wc, bc, ep, sd)

    assert attacked(pos, coord('a2'), 'w') is False
    assert attacked(pos, coord('h8'), 'w') is False
    assert attacked(pos, coord('d8'), 'w') is False
    assert attacked(pos, coord('a8'), 'w') is False
    assert attacked(pos, coord('h4'), 'w') is False

def test_attacked_false_black():
    board, wc, bc, ep, sd = parse_fen("1n2k2r/1b1q2bp/8/8/8/8/1B1Q2BP/1N2K2R w - - 0 1")
    pos = dorse.Position(board, wc, bc, ep, sd)

    assert attacked(pos, coord('a7'), 'b') is False
    assert attacked(pos, coord('h1'), 'b') is False
    assert attacked(pos, coord('d1'), 'b') is False
    assert attacked(pos, coord('a1'), 'b') is False
    assert attacked(pos, coord('h5'), 'b') is False

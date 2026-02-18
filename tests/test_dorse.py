import pytest
from dorse import Position, Move
import utils
from helpers import coord, move_str

# TESTS FOR DORSE MODULE

STARTPOS = utils.START_POS
INIT_BOARD, WC, BC, EP, SD = utils.parse_fen(STARTPOS)

# Position initialization tests
def test_initial_position():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    expected = [
        ['R','N','B','Q','K','B','N','R'],  # y = 0 (rank 1)
        ['P','P','P','P','P','P','P','P'],  # y = 1
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['p','p','p','p','p','p','p','p'],  # y = 6
        ['r','n','b','q','k','b','n','r'],  # y = 7 (rank 8)
    ]

    assert pos.board == expected
    assert pos.wc == (1, 1)
    assert pos.bc == (1, 1)
    assert pos.ep is None
    assert pos.sd == 'w'


# GEN_MOVE TESTS
def test_gen_moves_start():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "a2a3", "a2a4",
        "b2b3", "b2b4",
        "c2c3", "c2c4",
        "d2d3", "d2d4",
        "e2e3", "e2e4",
        "f2f3", "f2f4",
        "g2g3", "g2g4",
        "h2h3", "h2h4",
        "b1a3", "b1c3",
        "g1f3", "g1h3",
    }

    assert move_strs == expected_moves
    
def test_gen_moves_after_e4():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "a7a6", "a7a5",
        "b7b6", "b7b5",
        "c7c6", "c7c5",
        "d7d6", "d7d5",
        "e7e6", "e7e5",
        "f7f6", "f7f5",
        "g7g6", "g7g5",
        "h7h6", "h7h5",
        "b8a6", "b8c6",
        "g8f6", "g8h6",
    }

    assert move_strs == expected_moves

def test_gen_moves_pawn_promotion():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "a7a8q", "a7a8r", "a7a8b", "a7a8n",
    }

    assert move_strs == expected_moves

def test_gen_moves_castling():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQk - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "e1c1", "e1g1",
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_en_passant():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "e5d6"
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_no_legal():
    board, wc, bc, ep, sd = utils.parse_fen("4k2r/8/6N1/8/8/8/8/4K3 b k - 0 1") # black to move, knight attacks king
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    # Black cannot castle because the king is in check
    unexpected_moves = {
        "e8g8", "e8c8"
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_captures_and_gen_quiets():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppqpppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    pos = Position(board, wc, bc, ep, sd)

    assert set(pos.gen_moves()) == set(pos.gen_captures() + pos.gen_quiets())


# PUSH TESTS
# Test playing a move
def test_push():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e2'), coord('e4'), None, 'P')  # e2 to e4
    pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")

    assert pos.board == expected_board
    assert pos.ep == expected_ep
    assert pos.sd == 'b'

def test_push_capture():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e4'), coord('d5'), None, 'P', 'p')  # e4 captures e5
    pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")

    assert pos.board == expected_board
    assert pos.ep == expected_ep
    assert pos.sd == 'b'

def test_push_en_passant():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e5'), coord('d6'), None, 'P', 'p')  # e5 captures d5 en passant
    pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/1pp1pppp/p2P4/8/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2")

    assert pos.board == expected_board
    assert pos.ep == expected_ep
    assert pos.sd == 'b'

def test_push_castling():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e1'), coord('g1'), None, 'K')  # White kingside castling
    pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("r3k2r/8/8/8/8/8/8/R4RK1 b kq - 0 1")

    assert pos.board == expected_board
    assert pos.ep == expected_ep
    assert pos.sd == 'b'

def test_push_promotion():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('a7'), coord('a8'), 'q', 'P')  # a7 to a8 promoting to Queen
    pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("Q7/8/8/8/8/8/7p/8 b - - 0 1")

    assert pos.board == expected_board
    assert pos.ep == expected_ep
    assert pos.sd == 'b'

def test_push_promotion_capture():
    board, wc, bc, ep, sd = utils.parse_fen("8/8/8/8/8/8/7p/6R1 b - - 0 1 ")
    pos = Position(board, wc, bc, ep, sd)
    move = Move(coord('h2'), coord('g1'), 'q', 'p', 'R')  # h2 to g1 promoting to queen capturing black rook

    pos = pos.push(move)

    assert pos.board[0][6] == 'q'  # g1 should now have the promoted queen

def test_push_update_castling_rights():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('h1'), coord('h2'), None, 'R')  # Move white rook from h1 to h2
    pos = pos.push(move)

    expected_wc = (1, 0)  # White can no longer castle kingside
    expected_bc = bc

    assert pos.wc == expected_wc
    assert pos.bc == expected_bc

def test_pust_many_moves():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    moves = [
        Move(coord('e2'), coord('e4'), None, 'P'),  # e2 to e4
        Move(coord('e7'), coord('e5'), None, 'p'),
        Move(coord('g1'), coord('f3'), None, 'N'),
        Move(coord('b8'), coord('c6'), None, 'n'),
        Move(coord('f1'), coord('c4'), None, 'B'),
    ]

    for move in moves:
        pos = pos.push(move)
        pos = pos.pop()
    
    assert pos.board == INIT_BOARD


# POP TESTS
def test_pop():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('e2'), coord('e4'), None, 'P')  # e2 to e4
    pos = pos.push(move)
    assert not orig_pos.board == pos.board
    
    pos = pos.pop()

    assert orig_pos == pos

def test_pop_full():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    moves = pos.gen_moves()
    assert moves, "No moves generated"

    for move in moves:
        pos.push(move)
        pos.pop()
        after = pos.copy()
        assert after == orig_pos, f"Position corrupted by move: {move_str(move)}"

def test_pop_en_passant():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('e5'), coord('d6'), None, 'P', 'p')  # e5 captures d5 en passant
    pos = pos.push(move)
    assert not orig_pos.board == pos.board
    
    pos = pos.pop()

    assert orig_pos == pos

def test_pop_castling():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('e1'), coord('g1'), None, 'K')  # White kingside castling
    pos = pos.push(move)
    assert not orig_pos.board == pos.board
    
    pos = pos.pop()

    assert orig_pos == pos


# IN_CHECK TESTS
def test_in_check_start():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    assert not pos.in_check('w')
    assert not pos.in_check('b')

def test_in_check_white_true():
    board, wc, bc, ep, sd = utils.parse_fen("rnb1k1nr/pppp1ppp/5q2/4p3/4P3/P6N/1PPPQbPP/RNB1KB1R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    assert pos.in_check('w')
    assert not pos.in_check('b')

def test_in_check_black_true():
    board, wc, bc, ep, sd = utils.parse_fen("r1b1kbnr/ppppqBpp/2n5/4p3/4P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    assert pos.in_check('b')
    assert not pos.in_check('w')

def test_in_check_both():
    board, wc, bc, ep, sd = utils.parse_fen("4k3/8/5N2/8/8/3n4/8/4K3 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    assert pos.in_check('w')
    assert pos.in_check('b')


# UCI_MOVE TESTS
def test_make_uci_move_e2e4():
    pos = Position(INIT_BOARD.copy(), WC, BC, EP, SD)
    pos.make_uci_move("e2e4")

    # Check pawn moved
    assert pos.board[1][4] == '.'   # e2 empty
    assert pos.board[3][4] == 'P'   # e4 pawn

def test_make_uci_move_e7e5():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)
    pos.make_uci_move("e2e4")
    pos.make_uci_move("e7e5")

    # Check pawn moved
    assert pos.board[6][4] == '.'   # e7 empty
    assert pos.board[4][4] == 'p'   # e5 pawn

def test_make_uci_move_sequence():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    moves = ["e2e4", "e7e5", "g1f3", "b8c6"]
    for uci in moves:
        pos.make_uci_move(uci)

    # Check white knight moved
    assert pos.board[0][6] == '.'   # g1
    assert pos.board[2][5] == 'N'   # f3
    # Check black knight moved
    assert pos.board[7][1] == '.'   # b8
    assert pos.board[5][2] == 'n'   # c6

def test_make_uci_move_promotion():
    # Simplified board with white pawn on 7th rank
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/8/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    pos.make_uci_move("a7a8Q")  # promote to queen

    assert pos.board[6][0] == '.'   # a7 empty
    assert pos.board[7][0] == 'Q'   # a8 queen

def test_make_uci_move_pseudo_illegal():
    pos = Position(INIT_BOARD.copy(), WC, BC, EP, SD)

    with pytest.raises(ValueError):
        pos.make_uci_move("e2e5")  # illegal

def test_make_uci_move_chess960():
    # Example Chess960 start, assume utils provides fen
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board, wc, bc, ep, sd = utils.parse_fen(fen)
    pos = Position(board, wc, bc, ep, sd)

    # Try a simple move
    pos.make_uci_move("e2e4")
    assert pos.board[1][4] == '.'
    assert pos.board[3][4] == 'P'

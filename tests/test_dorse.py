import numpy as np
from dorse import Position, Move, INITIAL
import utils

# TESTS FOR DORSE MODULE
def test_initial_position():
    pos = INITIAL

    expected = np.array([
        ['R','N','B','Q','K','B','N','R'],  # y = 0 (rank 1)
        ['P','P','P','P','P','P','P','P'],  # y = 1
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['p','p','p','p','p','p','p','p'],  # y = 6
        ['r','n','b','q','k','b','n','r'],  # y = 7 (rank 8)
    ], dtype='U1')

    assert np.array_equal(pos[0], expected)
    assert pos[1] == (1, 1)
    assert pos[2] == (1, 1)
    assert pos[3] is None
    assert pos[4] == 'w'

# Generate moves tests
def test_gen_moves_start():
    pos = Position(INITIAL[0], 0, INITIAL[1], INITIAL[2], INITIAL[3], 'w')
    moves = pos.gen_moves()
    move_strs = {utils.move_str(m) for m in moves}

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
    board, *_ = utils.parse_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    pos = Position(board, 0, *_)
    moves = pos.gen_moves()
    move_strs = {utils.move_str(m) for m in moves}

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
    board, *_ = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, 0, *_)
    moves = pos.gen_moves()
    move_strs = {utils.move_str(m) for m in moves}

    expected_moves = {
        "a7a8Q", "a7a8R", "a7a8B", "a7a8N",
    }

    assert move_strs == expected_moves

def test_gen_moves_castling():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {utils.move_str(m) for m in moves}

    expected_moves = {
        "e1g1", "e1c1"
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_en_passant():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {utils.move_str(m) for m in moves}

    expected_moves = {
        "e5d6"
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_king_in_check():
    board, *_ = utils.parse_fen("4k2r/8/5N2/8/8/8/8/4K3 b k - 0 1") # black to move, knight attacks king
    pos = Position(board, 0, *_)
    moves = pos.gen_moves()
    move_strs = {utils.move_str(m) for m in moves}

    # Black king must move out of check
    expected_moves = {
        "e8d8", "e8e7", "e8f8", "e8f7",
    }

    assert move_strs == expected_moves

def test_gen_moves_no_legal():
    board, *_ = utils.parse_fen("4k2r/8/6N1/8/8/8/8/4K3 b k - 0 1") # black to move, knight attacks king
    pos = Position(board, 0, *_)
    moves = pos.gen_moves()
    move_strs = {utils.move_str(m) for m in moves}

    # Black cannot castle because the king is in check
    unexpected_moves = {
        "e8g8", "e8c8"
    }

    assert not unexpected_moves.intersection(move_strs)

# Test playing a move
def test_make_move():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)

    move = Move(utils.coord('e2'), utils.coord('e4'))  # e2 to e4
    new_pos = pos.move(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_make_move_capture():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)

    move = Move(utils.coord('e4'), utils.coord('d5'))  # e4 captures e5
    new_pos = pos.move(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_make_move_en_passant():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)

    move = Move(utils.coord('e5'), utils.coord('d6'))  # e5 captures d5 en passant
    new_pos = pos.move(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/1pp1pppp/p2P4/8/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_make_move_castling():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)

    move = Move(utils.coord('e1'), utils.coord('g1'))  # White kingside castling
    new_pos = pos.move(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("r3k2r/8/8/8/8/8/8/R4RK1 b kq - 0 1")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_make_move_promotion():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)

    move = Move(utils.coord('a7'), utils.coord('a8'), 'Q')  # a7 to a8 promoting to Queen
    new_pos = pos.move(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("Q7/8/8/8/8/8/7p/8 b - - 0 1")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_make_move_update_castling_rights():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)

    move = Move(utils.coord('h1'), utils.coord('h2'))  # Move white rook from h1 to h2
    new_pos = pos.move(move)

    expected_wc = (1, 0)  # White can no longer castle kingside
    expected_bc = bc

    assert new_pos.wc == expected_wc
    assert new_pos.bc == expected_bc

def test_search():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)

    move = pos.search()
    assert move is not None

def test_search_no_moves():
    board, *_ = utils.parse_fen("8/8/8/8/8/8/8/K7 b - - 0 1")  # Black to move, no pieces
    pos = Position(board, 0, *_)

    move = pos.search()
    assert move is None

def test_play():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, 0, wc, bc, ep, sd)

    move = pos.play()
    assert move is not None

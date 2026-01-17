from shutil import move
import numpy as np
import pytest
from dorse import Position, Move
import utils
import helpers

# TESTS FOR DORSE MODULE

STARTPOS = utils.START_POS
INIT_BOARD, WC, BC, EP, SD = utils.parse_fen(STARTPOS)

def test_initial_position():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

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

    assert np.array_equal(board, expected)
    assert wc == (1, 1)
    assert bc == (1, 1)
    assert ep is None
    assert sd == 'w'

# Generate moves tests
def test_gen_moves_start():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {helpers.move_str(m) for m in moves}

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
    move_strs = {helpers.move_str(m) for m in moves}

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
    move_strs = {helpers.move_str(m) for m in moves}

    expected_moves = {
        "a7a8Q", "a7a8R", "a7a8B", "a7a8N",
    }

    assert move_strs == expected_moves

def test_gen_moves_castling():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {helpers.move_str(m) for m in moves}

    expected_moves = {
        "e1g1", "e1c1"
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_en_passant():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {helpers.move_str(m) for m in moves}

    expected_moves = {
        "e5d6"
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_king_in_check():
    board, wc, bc, ep, sd = utils.parse_fen("4k2r/8/5N2/8/8/8/8/4K3 b k - 0 1") # black to move, knight attacks king
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {helpers.move_str(m) for m in moves}

    # Black king must move out of check
    expected_moves = {
        "e8d8", "e8e7", "e8f8", "e8f7",
    }

    assert move_strs == expected_moves

def test_gen_moves_no_legal():
    board, wc, bc, ep, sd = utils.parse_fen("4k2r/8/6N1/8/8/8/8/4K3 b k - 0 1") # black to move, knight attacks king
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {helpers.move_str(m) for m in moves}

    # Black cannot castle because the king is in check
    unexpected_moves = {
        "e8g8", "e8c8"
    }

    assert not unexpected_moves.intersection(move_strs)

# Test playing a move (push)
def test_push():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(helpers.coord('e2'), helpers.coord('e4'))  # e2 to e4
    new_pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_push_capture():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(helpers.coord('e4'), helpers.coord('d5'))  # e4 captures e5
    new_pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_push_en_passant():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(helpers.coord('e5'), helpers.coord('d6'))  # e5 captures d5 en passant
    new_pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("rnbqkbnr/1pp1pppp/p2P4/8/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_push_castling():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(helpers.coord('e1'), helpers.coord('g1'))  # White kingside castling
    new_pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("r3k2r/8/8/8/8/8/8/R4RK1 b kq - 0 1")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_push_promotion():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(helpers.coord('a7'), helpers.coord('a8'), 'Q')  # a7 to a8 promoting to Queen
    new_pos = pos.push(move)

    expected_board, _, _, expected_ep, _ = utils.parse_fen("Q7/8/8/8/8/8/7p/8 b - - 0 1")

    assert np.array_equal(new_pos.board, expected_board)
    assert new_pos.ep == expected_ep
    assert new_pos.sd == 'b'

def test_push_update_castling_rights():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(helpers.coord('h1'), helpers.coord('h2'))  # Move white rook from h1 to h2
    new_pos = pos.push(move)

    expected_wc = (1, 0)  # White can no longer castle kingside
    expected_bc = bc

    assert new_pos.wc == expected_wc
    assert new_pos.bc == expected_bc

# Test pop
def test_pop():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(helpers.coord('e2'), helpers.coord('e4'))  # e2 to e4
    pos = pos.push(move)
    assert not np.array_equal(orig_pos.board, pos.board)
    
    pos = pos.pop()

    assert np.array_equal(orig_pos.board, pos.board)
    assert orig_pos.wc == pos.wc
    assert orig_pos.bc == pos.bc
    assert orig_pos.ep == pos.ep
    assert orig_pos.sd == pos.sd
    assert orig_pos.history == pos.history

def test_pop_full():
    def snapshot(pos):
        return (
            tuple(pos.board.tolist()),
            pos.wc,
            pos.bc,
            pos.ep,
            pos.sd,
        )

    board, wc, bc, ep, sd = utils.parse_fen(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    )
    pos = Position(board, wc, bc, ep, sd)

    before = snapshot(pos)

    moves = pos.gen_moves()
    assert moves, "No moves generated"

    for move in moves:
        pos.push(move)
        pos.pop()

        after = snapshot(pos)
        assert after == before, f"Position corrupted by move {move}"

# Test making UCI moves
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

def test_make_uci_move_illegal():
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



import pytest
import random
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
    assert pos.sd == 1


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

def test_gen_moves_after_move_white():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppp1ppp/8/4p3/8/7P/PPPPPPP1/RNBQKBNR w KQkq - 0 1")
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
        "h3h4", "g1f3",
        "b1a3", "b1c3",
        "h1h2",
    }

    assert move_strs == expected_moves

def test_gen_moves_after_move_black():
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

def test_gen_moves_promotion_white():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "a7a8q", "a7a8r", "a7a8b", "a7a8n",
    }

    assert move_strs == expected_moves

def test_gen_moves_promotion_black():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 b - - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "h2h1q", "h2h1r", "h2h1b", "h2h1n",
    }

    assert move_strs == expected_moves

def test_gen_moves_castling_white():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQk - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "e1c1", "e1g1",
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_castling_black():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "e8c8", "e8g8",
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_en_passant_white():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "e5d6"
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_en_passant_black():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/ppp1pppp/8/8/3pP3/P4N2/1PPP1PPP/RNBQKB1R b KQkq e3 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    expected_moves = {
        "d4e3"
    }

    assert expected_moves.issubset(move_strs)

def test_gen_moves_en_passant_ilegal_white():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    unexpected_moves = {
        "e5d6"
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_moves_en_passant_ilegal_black():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/P7/1PPP1PPP/RNBQKBNR b KQkq e3 0 1")
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    unexpected_moves = {
        "d4e3"
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_moves_castle_ilegal_white():
    board, wc, bc, ep, sd = utils.parse_fen("4k2r/8/6N1/8/8/6n1/8/4K2R w Kk - 0 1")  # king passes thru check
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    unexpected_moves = {
        "e1g1",
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_moves_castle_ilegal_black():
    board, wc, bc, ep, sd = utils.parse_fen("4k2r/8/6N1/8/8/6n1/8/4K2R b Kk - 0 1")  # king passes thru check
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    unexpected_moves = {
        "e8g8",
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_moves_castle_rights_kingside_white():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w Kk - 0 1")  # white can castle only kingside
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    unexpected_moves = {
        "e1c1",
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_moves_castle_rights_kingside_black():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R b Kk - 0 1")  # black can castle only kingside
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    unexpected_moves = {
        "e8c8",
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_moves_castle_rights_queenside_white():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w Qq - 0 1")  # white can castle only queenside
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    unexpected_moves = {
        "e1g1",
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_moves_castle_rights_queenside_black():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R b Qq - 0 1")  # black can castle only queenside
    pos = Position(board, wc, bc, ep, sd)
    moves = pos.gen_moves()
    move_strs = {move_str(m) for m in moves}

    unexpected_moves = {
        "e8g8",
    }

    assert not unexpected_moves.intersection(move_strs)

def test_gen_captures_white():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    moves = pos.gen_moves()
    captures = pos.gen_captures()

    assert set(captures).issubset(set(moves))

def test_gen_captures_black():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppqpppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    pos = Position(board, wc, bc, ep, sd)

    moves = pos.gen_moves()
    captures = pos.gen_captures()

    assert set(captures).issubset(set(moves))


# PUSH TESTS
def test_push_white():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e2'), coord('e4'), None, 'P')  # e2 to e4
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")

    assert pos.board == expected_board
    assert pos.wc == (1, 1)
    assert pos.bc == (1, 1)
    assert pos.ep == None
    assert pos.sd == -1

def test_push_black():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e7'), coord('e5'), None, 'P')  # e7 to e5
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("rnbqkbnr/pppp1ppp/8/4p3/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    assert pos.board == expected_board
    assert pos.wc == (1, 1)
    assert pos.bc == (1, 1)
    assert pos.ep == None
    assert pos.sd == 1

def test_push_capture_white():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e4'), coord('d5'), None, 'P', 'p')  # e4 captures e5
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")

    assert pos.board == expected_board

def test_push_capture_black():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('d5'), coord('e4'), None, 'p', 'P')  # e5 captures d4
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("rnbqkbnr/ppp1pppp/8/8/4p3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")

    assert pos.board == expected_board

def test_push_en_passant_white():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e5'), coord('d6'), None, 'P', 'p')  # e5 captures d5 en passant
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("rnbqkbnr/1pp1pppp/p2P4/8/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")

    assert pos.board == expected_board
    assert pos.ep == None
    assert pos.sd == -1

def test_push_en_passant_black():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/8/3pP3/P4N2/1PPP1PPP/RNBQKB1R b KQkq e3 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('d4'), coord('e3'), None, 'p', 'P')
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/8/8/P3pN2/1PPP1PPP/RNBQKB1R w KQkq - 0 1")

    assert pos.board == expected_board
    assert pos.ep == None
    assert pos.sd == 1

def test_push_castling_kingside_white():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e1'), coord('g1'), None, 'K')  # White kingside castling
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("r3k2r/8/8/8/8/8/8/R4RK1 b kq - 0 1")

    assert pos.board == expected_board
    assert pos.wc == (0, 0)
    assert pos.sd == -1

def test_push_castling_kingside_black():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e8'), coord('g8'), None, 'k')  # Black kingside castling
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("r4rk1/8/8/8/8/8/8/R3K2R w KQ - 0 1")

    assert pos.board == expected_board
    assert pos.bc == (0, 0)
    assert pos.sd == 1

def test_push_castling_queenside_white():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e1'), coord('c1'), None, 'K')
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("r3k2r/8/8/8/8/8/8/2KR3R b kq - 0 1")

    assert pos.board == expected_board
    assert pos.wc == (0, 0)
    assert pos.sd == -1

def test_push_castling_queenside_black():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('e8'), coord('g8'), None, 'k')
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("r4rk1/8/8/8/8/8/8/R3K2R w KQ - 0 1")

    assert pos.board == expected_board
    assert pos.bc == (0, 0)
    assert pos.sd == 1

def test_push_promotion_white():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('a7'), coord('a8'), 'q', 'P')
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("Q7/8/8/8/8/8/7p/8 b - - 0 1")

    assert pos.board == expected_board
    assert pos.sd == -1

def test_push_promotion_black():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 b - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('h2'), coord('h1'), 'r', 'p')
    pos = pos.push(move)

    expected_board, *_ = utils.parse_fen("8/P7/8/8/8/8/8/7r w - - 0 1")

    assert pos.board == expected_board
    assert pos.sd == 1

def test_push_promotion_capture_white():
    board, wc, bc, ep, sd = utils.parse_fen("r7/1P6/8/8/8/8/6p1/7R w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    move = Move(coord('b7'), coord('a8'), 'q', 'P', 'r')

    pos = pos.push(move)

    assert pos.board[7][0] == 'Q'
    assert pos.board[6][1] == '.'

def test_push_promotion_capture_black():
    board, wc, bc, ep, sd = utils.parse_fen("r7/1P6/8/8/8/8/6p1/7R b - - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    move = Move(coord('g2'), coord('h1'), 'q', 'p', 'R')

    pos = pos.push(move)

    assert pos.board[0][7] == 'q'
    assert pos.board[1][7] == '.'

def test_push_update_castling_rights_white():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('h1'), coord('g1'), None, 'R')
    pos = pos.push(move)

    assert pos.wc == (1, 0)
    assert pos.bc == bc

def test_push_update_castling_rights_black():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    move = Move(coord('h8'), coord('g8'), None, 'r')
    pos = pos.push(move)

    assert pos.wc == wc
    assert pos.bc == (1, 0)

def test_push_pop():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    moves = [
        Move(coord('e2'), coord('e4'), None, 'P'),
        Move(coord('e7'), coord('e5'), None, 'p'),
        Move(coord('g1'), coord('f3'), None, 'N'),
        Move(coord('b8'), coord('c6'), None, 'n'),
        Move(coord('f1'), coord('c4'), None, 'B'),
    ]

    for move in moves:
        pos = pos.push(move)
        pos = pos.pop()

    assert pos.board == INIT_BOARD

# Test hash consistency
def test_push_hash():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    for _ in range(1000):
        moves = pos.gen_moves()
        if not moves:
            break
        pos.push(random.choice(moves))

    assert pos.hash == pos.gen_hash()

def test_push_pop_hash():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)
    original_hash = pos.hash

    stack = []
    for _ in range(50):
        moves = pos.gen_moves()
        if not moves:
            break
        move = random.choice(moves)
        stack.append(move)
        pos.push(move)

    while stack:
        pos.pop()
        stack.pop()

    assert pos.hash == original_hash

from evaluation import evaluate

# Test incremental evaluation consistency
def test_push_eval():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    for move in pos.gen_moves():
        pos.push(move)
        full = evaluate(pos)
        assert pos.eval == full, f"move={move.uci()} incremental={pos.eval} full={full}"
        pos.pop()

def test_push_eval_deeper():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    for move in pos.gen_moves():
        pos.push(move)
        for move2 in pos.gen_moves():
            pos.push(move2)
            full = evaluate(pos)
            assert pos.eval == full, f"move={move.uci()} move2={move2.uci()} incremental={pos.eval} full={full}"
            pos.pop()
        pos.pop()


# POP TESTS
def test_pop_white():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('e2'), coord('e4'), None, 'P')
    pos = pos.push(move)
    assert not pos == orig_pos

    pos = pos.pop()
    assert pos == orig_pos

def test_pop_black():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('e7'), coord('e5'), None, 'p')
    pos = pos.push(move)
    assert not pos == orig_pos

    pos = pos.pop()
    assert pos == orig_pos

def test_pop_en_passant_white():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('e5'), coord('d6'), None, 'P', 'p')
    pos = pos.push(move)
    assert not pos == orig_pos

    pos = pos.pop()
    assert pos == orig_pos

def test_pop_en_passant_black():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/ppp1pppp/8/8/3pP3/P4N2/1PPP1PPP/RNBQKB1R b KQkq e3 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('d4'), coord('e3'), None, 'p', 'P')
    pos = pos.push(move)
    assert not pos == orig_pos

    pos = pos.pop()
    assert pos == orig_pos

def test_pop_castling_white():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('e1'), coord('c1'), None, 'K')
    pos = pos.push(move)
    assert not pos == orig_pos

    pos = pos.pop()
    assert pos == orig_pos

def test_pop_castling_black():
    board, wc, bc, ep, sd = utils.parse_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('e8'), coord('c8'), None, 'k')
    pos = pos.push(move)
    assert not pos == orig_pos

    pos = pos.pop()
    assert pos.bc == orig_pos.bc

def test_pop_promotion_white():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('a7'), coord('a8'), 'q', 'P')
    pos = pos.push(move)
    assert not pos == orig_pos

    pos = pos.pop()
    assert pos == orig_pos

def test_pop_promotion_black():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 b - - 0 1")
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    move = Move(coord('h2'), coord('h1'), 'r', 'p')
    pos = pos.push(move)
    assert not pos == orig_pos

    pos = pos.pop()
    assert pos == orig_pos

def test_pop_full():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    moves = pos.gen_moves()
    assert moves, "No moves generated"

    for move in moves:
        pos.push(move)
        pos.pop()
        after = pos.copy()
        assert after == orig_pos, f"Position corrupted by move: {move_str(move)}"

def test_pop_many():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)
    orig_pos = pos.copy()

    moves = pos.gen_moves()
    pos.push(moves[0])
    moves = pos.gen_moves()
    pos.push(moves[0])
    pos.pop()
    pos.pop()

    assert pos == orig_pos


# IN_CHECK TESTS
def test_in_check_start():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    assert not pos.in_check(1)
    assert not pos.in_check(-1)

def test_in_check_white_true():
    board, wc, bc, ep, sd = utils.parse_fen("rnb1k1nr/pppp1ppp/5q2/4p3/4P3/P6N/1PPPQbPP/RNB1KB1R w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    assert pos.in_check(1)
    assert not pos.in_check(-1)

def test_in_check_black_true():
    board, wc, bc, ep, sd = utils.parse_fen("r1b1kbnr/ppppqBpp/2n5/4p3/4P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    assert pos.in_check(-1)
    assert not pos.in_check(1)

def test_in_check_both():
    board, wc, bc, ep, sd = utils.parse_fen("4k3/8/5N2/8/8/3n4/8/4K3 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    assert pos.in_check(1)
    assert pos.in_check(-1)


# UCI_MOVE TESTS
def test_make_uci_move_e2e4():
    pos = Position(INIT_BOARD.copy(), WC, BC, EP, SD)
    pos.make_uci_move("e2e4")

    # Check pawn moved
    assert pos.board[1][4] == '.'  # e2 empty
    assert pos.board[3][4] == 'P'  # e4 pawn

def test_make_uci_move_e7e5():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)
    pos.make_uci_move("e2e4")
    pos.make_uci_move("e7e5")

    assert pos.board[6][4] == '.'  # e7 empty
    assert pos.board[4][4] == 'p'  # e5 pawn

def test_make_uci_move_sequence():
    board, wc, bc, ep, sd = utils.parse_fen(utils.START_POS)
    pos = Position(board, wc, bc, ep, sd)

    moves = ["e2e4", "e7e5", "g1f3", "b8c6"]
    for uci in moves:
        pos.make_uci_move(uci)

    assert pos.board[0][6] == '.'  # g1
    assert pos.board[2][5] == 'N'  # f3

    assert pos.board[7][1] == '.'  # b8
    assert pos.board[5][2] == 'n'  # c6

def test_make_uci_move_promotion_white():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    pos.make_uci_move("a7a8Q")

    assert pos.board[6][0] == '.'  # a7
    assert pos.board[7][0] == 'Q'  # a8

def test_make_uci_move_promotion_black():
    board, wc, bc, ep, sd = utils.parse_fen("8/P7/8/8/8/8/7p/8 b - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    pos.make_uci_move("h2h1Q")

    assert pos.board[1][7] == '.'  # h2
    assert pos.board[0][7] == 'q'  # h1

def test_make_uci_move_pseudo_illegal():
    pos = Position(INIT_BOARD.copy(), WC, BC, EP, SD)

    with pytest.raises(ValueError):
        pos.make_uci_move("e2e5")  # illegal

def test_make_uci_move_chess960():
    fen = utils.START_POS
    board, wc, bc, ep, sd = utils.parse_fen(fen)
    pos = Position(board, wc, bc, ep, sd)

    pos.make_uci_move("e2e4")
    assert pos.board[1][4] == '.'
    assert pos.board[3][4] == 'P'

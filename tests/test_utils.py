import numpy as np
import dorse
from utils import parse_fen, attacked
from helpers import coord, square, move_str

# Tests for notation conversion
def test_notation():
    assert square((0, 0)) == 'a1'
    assert square((7, 7)) == 'h8'
    assert square((3, 4)) == 'e4'
    assert square((6, 2)) == 'c7'
    assert coord('a1') == (0, 0)
    assert coord('h8') == (7, 7)
    assert coord('e4') == (3, 4)
    assert coord('c7') == (6, 2)


# Tests for FEN parsing
def test_parse_fen():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

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

    board, w_castling, b_castling, en_passant, turn = parse_fen(fen)

    assert np.array_equal(board, expected)
    assert w_castling == (1, 1)
    assert b_castling == (1, 1)
    assert en_passant is None
    assert turn == 'w'
    assert board[0][0] == 'R'   # a1
    assert board[0][4] == 'K'   # e1
    assert board[7][0] == 'r'   # a8
    assert board[7][4] == 'k'   # e8

def test_parse_fen_ep():
    fen = "rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1"
    board, w_castling, b_castling, en_passant, turn = parse_fen(fen)
    assert en_passant == coord('d6')  # d6 corresponds to (5, 3)


# Tests for attacked squares
def test_attacked():
    board, wc, bc, ep, sd = parse_fen("8/8/8/8/4q3/8/8/8 w - - 0 1") # queen on d5
    pos = dorse.Position(board, wc, bc, ep, sd)

    assert attacked(pos, coord('d5'), 'b') is True
    assert attacked(pos, coord('c6'), 'b') is True
    assert attacked(pos, coord('a1'), 'b') is False

def test_attacked_white():
    board, wc, bc, ep, sd = parse_fen("8/8/8/8/4Q3/8/8/8 b - - 0 1") # queen on d5
    pos = dorse.Position(board, wc, bc, ep, sd)

    assert attacked(pos, coord('d5'), 'w') is True
    assert attacked(pos, coord('a1'), 'w') is False

def test_attacked_black():
    board, wc, bc, ep, sd = parse_fen("8/8/8/8/4q3/8/8/8 w - - 0 1") # queen on e4
    pos = dorse.Position(board, wc, bc, ep, sd)

    assert attacked(pos, coord('h7'), 'b') is True
    assert attacked(pos, coord('a1'), 'b') is False

def test_attacked_other():
    board, wc, bc, ep, sd = parse_fen("R2q1bn1/8/8/8/8/8/8/8 w - - 0 1") # queen on e4
    pos = dorse.Position(board, wc, bc, ep, sd)

    assert attacked(pos, coord('b6'), 'b') is True
    assert attacked(pos, coord('a3'), 'b') is True
    assert attacked(pos, coord('h6'), 'b') is True
    assert attacked(pos, coord('e6'), 'b') is False
    assert attacked(pos, coord('a7'), 'b') is False

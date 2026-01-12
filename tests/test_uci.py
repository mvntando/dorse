import io
import sys
import numpy as np
import pytest
from dorse import Position
import utils
from uci import parse_position, uci_loop, print_id, print_options

# TESTS FOR UCI MODULE
# UCI handshake tests
def test_uci_loop_startpos(monkeypatch, capsys):
    # Commands we want to simulate
    commands = "\n".join([
        "uci",
        "isready",
        "position startpos",
        "quit"
    ]) + "\n"

    # Mock input() to read from our commands
    input_stream = io.StringIO(commands)
    monkeypatch.setattr('builtins.input', lambda: input_stream.readline().rstrip('\n'))

    # Run the UCI loop
    uci_loop()

    # Capture stdout
    captured = capsys.readouterr()
    output = captured.out.splitlines()

    # Check key responses
    assert "id name Dorse" in output
    assert "id author MV" in output
    assert "uciok" in output
    assert "readyok" in output

def test_uci_loop_go(monkeypatch, capsys):
    commands = "\n".join([
        "uci",
        "isready",
        "position startpos",
        "go",
        "quit"
    ]) + "\n"

    input_stream = io.StringIO(commands)
    monkeypatch.setattr('builtins.input', lambda: input_stream.readline().rstrip('\n'))

    uci_loop()

    captured = capsys.readouterr()
    output = captured.out.splitlines()

    # Check that bestmove line exists
    assert any(line.startswith("bestmove") for line in output)

# Position parsing tests
def test_position_startpos_initial():
    pos = parse_position("position startpos")

    board, *_ = utils.parse_fen(utils.START_POS)

    assert pos is not None
    assert np.array_equal(pos.board, board)

def test_position_startpos_single_move():
    pos = parse_position("position startpos moves e2e4")

    # Pawn moved from e2 to e4
    assert pos is not None
    assert pos.board[1][4] == '.'   # e2 empty
    assert pos.board[3][4] == 'P'   # e4 pawn

def test_position_multiple_moves():
    pos = parse_position(
        "position startpos moves e2e4 e7e5 g1f3"
    )

    assert pos is not None
    assert pos.board[1][4] == '.'   # e2
    assert pos.board[3][4] == 'P'   # e4

    assert pos.board[6][4] == '.'   # e7
    assert pos.board[4][4] == 'p'   # e5

    assert pos.board[0][6] == '.'   # g1
    assert pos.board[2][5] == 'N'   # f3

def test_position_side_multiple_moves():
    pos = parse_position(
        "position startpos moves e2e4 e7e5 g1f3"
    )

    assert pos is not None
    assert pos.sd == 'b'  # Black to move after 3 moves

def test_position_fen_with_moves():
    fen = "8/8/8/8/8/8/4P3/4K3 w - - 0 1"
    pos = parse_position(f"position fen {fen} moves e2e4")

    assert pos is not None
    assert pos.board[1][4] == '.'
    assert pos.board[3][4] == 'P'
    
def test_illegal_uci_move_raises():
    with pytest.raises(ValueError):
        parse_position("position startpos moves e2e5")

def test_something(capsys):
    pos = parse_position("position startpos")
    captured = capsys.readouterr()

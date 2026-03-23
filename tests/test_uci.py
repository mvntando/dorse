import io
import numpy as np
import pytest
from utils import parse_fen, START_POS, WHITE, BLACK, EMPTY, PAWN, KNIGHT
from uci import parse_position, uci_loop

# TESTS FOR UCI MODULE

# UCI HANDSHAKE TESTS
# UCI LOOP TESTS
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
        "go movetime 1000",
        "quit"
    ]) + "\n"

    input_stream = io.StringIO(commands)
    monkeypatch.setattr('builtins.input', lambda: input_stream.readline().rstrip('\n'))

    uci_loop()

    captured = capsys.readouterr()
    output = captured.out.splitlines()

    # Check that bestmove line exists
    assert any(line.startswith("bestmove") for line in output)

def test_uci_loop_quit(monkeypatch, capsys):
    commands = "\n".join([
        "uci",
        "isready",
        "position startpos",
        "quit"
    ]) + "\n"

    input_stream = io.StringIO(commands)
    monkeypatch.setattr('builtins.input', lambda: input_stream.readline().rstrip('\n'))

    uci_loop()

    captured = capsys.readouterr()
    output = captured.out.splitlines()

    # Check that we got the expected responses before quitting
    assert "id name Dorse" in output
    assert "id author MV" in output
    assert "uciok" in output
    assert "readyok" in output

# PARSE POSITION TESTS
def test_parse_position_startpos():
    pos = parse_position("position startpos")

    board, *_ = parse_fen(START_POS)

    assert pos is not None
    assert pos.board == board

def test_parse_position_startpos_single_move():
    pos = parse_position("position startpos moves e2e4")

    # Pawn moved from e2 to e4
    assert pos is not None
    assert pos.board[1][4] == EMPTY  # e2 empty
    assert pos.board[3][4] == PAWN  # e4 pawn
    assert pos.sd == BLACK

def test_parse_position_multiple_moves():
    pos = parse_position("position startpos moves e2e4 e7e5 g1f3 b8c6")

    assert pos is not None
    assert pos.board[1][4] == EMPTY  # e2
    assert pos.board[3][4] == PAWN  # e4

    assert pos.board[6][4] == EMPTY  # e7
    assert pos.board[4][4] == -PAWN  # e5

    assert pos.board[0][6] == EMPTY  # g1
    assert pos.board[2][5] == KNIGHT  # f3

    assert pos.board[7][1] == EMPTY  # b8
    assert pos.board[5][2] == -KNIGHT  # c6
    assert pos.sd == 1

def test_illegal_uci_move_raises():
    with pytest.raises(ValueError):
        parse_position("position startpos moves e2e5")

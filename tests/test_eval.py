from dorse import Position
import utils
from evaluation import evaluate

# TESTS FOR EVALUATE MODULE

def test_evaluate_start():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 0, f"Expected 0, got {score}"

def test_evaluate_no_piece():
    board, wc, bc, ep, sd = utils.parse_fen("8/8/8/8/8/8/8/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 0, f"Expected 0, got {score}"

def test_evaluate_white_piece_up_white():
    board, wc, bc, ep, sd = utils.parse_fen("8/8/8/8/4P3/8/8/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 106, f"Expected 106, got {score}"

def test_evaluate_white_piece_up_black():
    board, wc, bc, ep, sd = utils.parse_fen("8/8/8/8/4P3/8/8/8 b - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 106, f"Expected 106, got {score}"

def test_evaluate_black_piece_up_white():
    board, wc, bc, ep, sd = utils.parse_fen("8/8/8/8/4p3/8/8/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == -114, f"Expected -114, got {score}"

def test_evaluate_black_piece_up_black():
    board, wc, bc, ep, sd = utils.parse_fen("8/8/8/8/4p3/8/8/8 b - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == -114, f"Expected -114, got {score}"

def test_evaluate_piece_difference_white():
    board, wc, bc, ep, sd = utils.parse_fen("1kr4r/pp5p/1q3bp1/2b5/P7/1B5P/2PQNPP1/R4RK1 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 62, f"Expected 62, got {score}"

def test_evaluate_piece_difference_black():
    board, wc, bc, ep, sd = utils.parse_fen("1kr4r/pp5p/1q3bp1/2b5/P7/1B5P/2PQNPP1/R4RK1 b - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 62, f"Expected 62, got {score}"

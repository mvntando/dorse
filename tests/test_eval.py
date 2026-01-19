from dorse import Position
import utils
from eval import evaluate

def test_evaluate_0():
    board, wc, bc, ep, sd = utils.parse_fen("8/8/8/8/8/8/8/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 0, f"Expected 0, got {score}"

def test_evaluate_1():
    board, wc, bc, ep, sd = utils.parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 0, f"Expected 0, got {score}"

def test_evaluate_2():
    board, wc, bc, ep, sd = utils.parse_fen("1kr4r/pp5p/1q3np1/2b5/P7/1B5P/2PQNPP1/R4RK1 w Qk - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == 100, f"Expected 100, got {score}"

def test_evaluate_3():
    board, wc, bc, ep, sd = utils.parse_fen("8/8/8/8/4p3/8/8/8 w - - 0 1")
    pos = Position(board, wc, bc, ep, sd)

    score = evaluate(pos)
    assert score == -100, f"Expected 100, got {score}"


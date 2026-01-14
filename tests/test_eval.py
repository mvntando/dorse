from dorse import Position
import utils
from eval import evaluate

def test_evaluate():
    # Create empty positions or startpos
    board, *_ = utils.parse_fen("8/8/8/8/8/8/8/8 w - - 0 1")
    pos1 = Position(board, 0, *_)

    board2, *_ = utils.parse_fen("8/8/8/8/4p3/8/8/8 w - - 0 1")
    pos2 = Position(board2, 0, *_)

    score1 = evaluate(pos1)
    score2 = evaluate(pos2)

    assert score1 == 0, f"Expected 0, got {score1}"
    assert score2 == -100, f"Expected 100, got {score2}"



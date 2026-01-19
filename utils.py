import numpy as np
from numpy.typing import NDArray

# Initial chess board setup
START_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Lists of possible moves for each piece type
DIRECTIONS = {
    "N":  [(2, 1), (2, -1), (-2, 1), (-2, -1),
           (1, 2), (1, -2), (-1, 2), (-1, -2)],  # Knight
    "B":  [(1, 1), (1, -1), (-1, 1), (-1, -1)],  # Bishop
    "R":  [(1, 0), (-1, 0), (0, 1), (0, -1)],    # Rook
    "Q":  [(1, 0), (-1, 0), (0, 1), (0, -1),
           (1, 1), (1, -1), (-1, 1), (-1, -1)],  # Queen
    "K":  [(1, 0), (-1, 0), (0, 1), (0, -1),
           (1, 1), (1, -1), (-1, 1), (-1, -1)],  # King
    "P":  [(1, 0)],  # White pawn (moves up the board)
    "p":  [(-1, 0)], # Black pawn (moves down the board)

    "P_capture":  [(1, 1), (1, -1)],    # White pawn captures diagonally up
    "p_capture":  [(-1, 1), (-1, -1)],  # Black pawn captures diagonally down
}

# Sliding vs non-sliding
SLIDING = {"B", "R", "Q"}


# Parse FEN string into board representation and game state
def parse_fen(fen: str) -> tuple[NDArray[np.str_], tuple[int, int], tuple[int, int], tuple[int, int] | None, str]:
    """
    Docstring for parse_fen
    
    :param fen: Description
    :type fen: str
    :return: Description
    :rtype: tuple[NDArray[str_], tuple[int, int], tuple[int, int], tuple[int, int] | None, str]
    """
    parts = fen.split()
    if len(parts) < 4:
        raise ValueError("Invalid FEN")

    board_part, side, castling, ep = parts[:4]

    board: NDArray[np.str_] = np.full((8, 8), '.', dtype='U1')

    # FEN ranks: 8 → 1
    for fen_rank, row in enumerate(board_part.split('/')):
        file = 0
        for ch in row:
            if ch.isdigit():
                file += int(ch)
            else:
                board[fen_rank, file] = ch
                file += 1
        # optional safety check (can remove if you want zero overhead)
        if file != 8:
            raise ValueError("Invalid FEN rank")

    # Flip so board[0][0] == a1 (white side) (cartesian coordinates)
    board = np.flipud(board)

    # Side to move: keep as 'w' / 'b'
    sd = side

    # Castling rights
    wc = (1 if 'Q' in castling else 0, 1 if 'K' in castling else 0)
    bc = (1 if 'q' in castling else 0, 1 if 'k' in castling else 0)

    # En passant
    if ep == '-':
        ep = None
    else:
        file = ord(ep[0]) - ord('a')
        rank = int(ep[1]) - 1   # rank 1 → index 0
        ep = (rank, file)

    return board, wc, bc, ep, sd

# Check for legal moves
def legal(pos, move) -> bool:
    """
    Is the given move legal?
    
    :param pos: Position: dorse.Position
    :type pos: Position
    :param move: Move: dorse.Move
    :type move: Move
    :return: is the move legal
    :rtype: bool
    """
    src, dst, promo = move.src, move.dst, move.promo
    r0, c0 = src
    r1, c1 = dst

    is_white = pos.sd == 'w'
    opponent = 'b' if is_white else 'w'

    # --- Make a backup copy of state ---
    piece = pos.board[r0][c0]
    captured = pos.board[r1][c1]

    # --- Handle castling moves ---
    if piece.upper() == 'K' and abs(c1 - c0) == 2:
        if c1 == 6:  # King-side castle
            rook_src, rook_dst = (r0, 7), (r0, 5)
        else:  # Queen-side castle
            rook_src, rook_dst = (r0, 0), (r0, 3)

        # Temporary move
        pos.board[r0][c0] = '.'
        pos.board[r1][c1] = 'K' if is_white else 'k'
        pos.board[rook_dst[0]][rook_dst[1]] = pos.board[rook_src[0]][rook_src[1]]
        pos.board[rook_src[0]][rook_src[1]] = '.'

        # Check if king passes through or ends up in check
        king_sqs = [(r0, c0), (r0, (c0 + c1) // 2), (r1, c1)]
        legal = all(not attacked(pos, sq, opponent) for sq in king_sqs)

        # Restore state
        pos.board[r0][c0] = 'K' if is_white else 'k'
        pos.board[r1][c1] = '.'
        pos.board[rook_src[0]][rook_src[1]] = pos.board[rook_dst[0]][rook_dst[1]]
        pos.board[rook_dst[0]][rook_dst[1]] = '.'

        return legal

    # --- Handle en passant moves ---
    was_ep = piece.upper() == 'P' and pos.ep and dst == pos.ep
    if was_ep:
        pawn_row = r1 + (1 if is_white else -1)
        ep_sq = pos.board[pawn_row][c1]
        pos.board[pawn_row][c1] = '.'

    # --- Normal move ---
    pos.board[r0][c0] = '.'
    pos.board[r1][c1] = piece if not promo else (promo if is_white else promo.lower())

    # Find king position
    king_sq = None
    for r in range(8):
        for c in range(8):
            if pos.board[r][c] == ('K' if is_white else 'k'):
                king_sq = (r, c)
                break
        if king_sq:
            break

    # Check if own king is attacked
    legal = not attacked(pos, king_sq, opponent) if king_sq else True

    # --- Undo move ---
    pos.board[r0][c0] = piece
    pos.board[r1][c1] = captured
    if was_ep:
        pos.board[pawn_row][c1] = ep_sq

    return legal

def attacked(pos, sq, sd) -> bool:
        """
        Is the given square attacked?
        
        :param pos: Description
        :param sq: Description
        :param sd: Description
        :return: Description
        :rtype: bool
        """
        # sd = side to check for attacks from ('w' or 'b')
        r, c = sq
        board = pos.board
        in_bounds = lambda r, c: 0 <= r < 8 and 0 <= c < 8

        DIRS = DIRECTIONS  # local alias

        # --- Pawn attacks ---
        pawn_dirs = DIRS['p_capture'] if sd == 'w' else DIRS['P_capture']
        pawn = 'P' if sd == 'w' else 'p'
        for dr, dc in pawn_dirs:
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc) and board[rr][cc] == pawn:
                return True

        # --- Knight attacks ---
        for dr, dc in DIRS['N']:
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc) and board[rr][cc] == ('N' if sd == 'w' else 'n'):
                return True

        # --- King attacks ---
        for dr, dc in DIRS['K']:
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc) and board[rr][cc] == ('K' if sd == 'w' else 'k'):
                return True

        # --- Sliding attacks ---
        sliders = SLIDING # local alias
        for piece in sliders:
            p = piece if sd == 'w' else piece.lower()
            for dr, dc in DIRS[piece]:
                rr, cc = r, c
                while True:
                    rr += dr
                    cc += dc
                    if not in_bounds(rr, cc):
                        break
                    sq_piece = board[rr][cc]
                    if sq_piece == '.':
                        continue
                    if sq_piece == p:
                        return True
                    break  # blocked by another piece

        return False

def check(pos) -> bool: # TODO: Test
    """
    Is the side to move in check?
    
    :param pos: Description
    :return: Description
    :rtype: bool
    """
    is_white = pos.sd == 'w'
    opponent = 'b' if is_white else 'w'

    # Find king position
    king_sq = None
    for r in range(8):
        for c in range(8):
            if pos.board[r][c] == ('K' if is_white else 'k'):
                king_sq = (r, c)
                break
        if king_sq:
            break

    if king_sq and attacked(pos, king_sq, opponent):
        return True
    return False

def capture(pos, move) -> bool: # TODO: Test
    """
    Docstring for capture
    
    :param pos: Description
    :param move: Description
    :return: Description
    :rtype: bool
    """
    target_square = pos.board[move.dst[0]][move.dst[1]]
    if target_square != '.':
        return True
    
    # En passant: pawn moves diagonally to empty square
    piece = pos.board[move.src[0]][move.src[1]]
    if piece.lower() == 'p':  # Is it a pawn?
        # Diagonal move (x changes)
        if move.src[1] != move.dst[1]:
            return True  # Pawn diagonal to empty = en passant
    
    return False


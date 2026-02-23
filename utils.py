import random

# Zobrist hashing
random.seed(0)  # deterministic

PIECE_INDEX = {
    "P": 0, "N": 1, "B": 2, "R": 3, "Q": 4, "K": 5,
    "p": 6, "n": 7, "b": 8, "r": 9, "q": 10, "k": 11
}

# 12 pieces × 64 squares
# 1 side-to-move key
# 4 castling keys
# 8 ep file keys

PIECE_KEYS = [[random.getrandbits(64) for _ in range(64)] for _ in range(12)]
SIDE_KEY = random.getrandbits(64)  # if is white
CASTLE_KEYS = [random.getrandbits(64) for _ in range(4)]  # KQkq
EP_KEYS = [random.getrandbits(64) for _ in range(8)]  # ep file a-h


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

# Sliding pieces
SLIDING = {"B", "R", "Q"}

# Parse FEN string into board representation and game state
def parse_fen(fen: str) -> tuple[list[list[str]], tuple[int, int], tuple[int, int], tuple[int, int] | None, str]:
    parts = fen.split()
    if len(parts) < 4:
        raise ValueError("Invalid FEN")
    board_part, side, castling, ep = parts[:4]
    board: list[list[str]] = []
    # FEN ranks: 8 → 1
    for fen_rank, row in enumerate(board_part.split('/')):
        board.append(['.'] * 8)  # <-- Create the row first
        file = 0
        for ch in row:
            if ch.isdigit():
                file += int(ch)
            else:
                board[fen_rank][file] = ch
                file += 1
        # optional safety check (can remove if you want zero overhead)
        if file != 8:
            raise ValueError("Invalid FEN rank")
    # Flip so board[0][0] == a1 (white side) (cartesian coordinates)
    board = board[::-1]
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
        rank = int(ep[1]) - 1  # rank 1 → index 0
        ep = (rank, file)
    return board, wc, bc, ep, sd

# Check if square is attacked by opponent's pieces
def attacked(pos, sq: tuple[int, int], opponent: str) -> bool:
    r, c = sq
    board = pos.board
    
    # --- Precompute piece symbols and directions ---
    if opponent == 'w':
        pawn_dirs = DIRECTIONS['p_capture']
        pawn, knight, king = 'P', 'N', 'K'
        sliders = {p: DIRECTIONS[p] for p in SLIDING}
    else:
        pawn_dirs = DIRECTIONS['P_capture']
        pawn, knight, king = 'p', 'n', 'k'
        sliders = {p.lower(): DIRECTIONS[p] for p in SLIDING}
    
    # --- Sliding attacks ---
    for piece, dirs in sliders.items():
        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            while 0 <= rr < 8 and 0 <= cc < 8:
                sq_piece = board[rr][cc]
                if sq_piece == '.':
                    rr += dr
                    cc += dc
                    continue
                if sq_piece == piece:
                    return True
                break  # blocked by another piece

    # --- Pawn attacks ---
    for dr, dc in pawn_dirs:
        rr, cc = r + dr, c + dc
        if 0 <= rr < 8 and 0 <= cc < 8 and board[rr][cc] == pawn:
            return True
    
    # --- Knight attacks ---
    for dr, dc in DIRECTIONS['N']:
        rr, cc = r + dr, c + dc
        if 0 <= rr < 8 and 0 <= cc < 8 and board[rr][cc] == knight:
            return True
    
    # --- King attacks ---
    for dr, dc in DIRECTIONS['K']:
        rr, cc = r + dr, c + dc
        if 0 <= rr < 8 and 0 <= cc < 8 and board[rr][cc] == king:
            return True
    
    return False

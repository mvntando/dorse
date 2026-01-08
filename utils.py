import numpy as np

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
def parse_fen(fen: str):
    parts = fen.split()
    if len(parts) < 4:
        raise ValueError("Invalid FEN")

    board_part, side, castling, ep = parts[:4]

    board = np.full((8, 8), '.', dtype='U1')

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

    # Flip so board[0][0] == a1 (white side)
    board = np.flipud(board)

    # Side to move: keep as 'w' / 'b'
    sd = side

    # Castling rights
    wc = (1 if 'Q' in castling else 0, 1 if 'K' in castling else 0)
    bc = (1 if 'q' in castling else 0, 1 if 'k' in castling else 0)

    # En passant
    if ep == '-':
        ep_sq = None
    else:
        file = ord(ep[0]) - ord('a')
        rank = int(ep[1]) - 1   # rank 1 → index 0
        ep_sq = (rank, file)

    return board, wc, bc, ep_sq, sd

# Check for legal moves
def legal(self, move):
    src, dst, promo = move.src, move.dst, move.promo
    r0, c0 = src
    r1, c1 = dst

    is_white = self.sd == 'w'
    opponent = 'b' if is_white else 'w'

    # --- Make a backup copy of state ---
    piece = self.board[r0][c0]
    captured = self.board[r1][c1]

    # --- Handle castling moves ---
    if piece.upper() == 'K' and abs(c1 - c0) == 2:
        if c1 == 6:  # King-side castle
            rook_src, rook_dst = (r0, 7), (r0, 5)
        else:  # Queen-side castle
            rook_src, rook_dst = (r0, 0), (r0, 3)

        # Temporary move
        self.board[r0][c0] = '.'
        self.board[r1][c1] = 'K' if is_white else 'k'
        self.board[rook_dst[0]][rook_dst[1]] = self.board[rook_src[0]][rook_src[1]]
        self.board[rook_src[0]][rook_src[1]] = '.'

        # Check if king passes through or ends up in check
        king_sqs = [(r0, c0), (r0, (c0 + c1) // 2), (r1, c1)]
        legal = all(not attacked(self, sq, opponent) for sq in king_sqs)

        # Restore state
        self.board[r0][c0] = 'K' if is_white else 'k'
        self.board[r1][c1] = '.'
        self.board[rook_src[0]][rook_src[1]] = self.board[rook_dst[0]][rook_dst[1]]
        self.board[rook_dst[0]][rook_dst[1]] = '.'

        return legal

    # --- Handle en passant moves ---
    was_ep = piece.upper() == 'P' and self.ep and dst == self.ep
    if was_ep:
        pawn_row = r1 + (1 if is_white else -1)
        ep_captured = self.board[pawn_row][c1]
        self.board[pawn_row][c1] = '.'

    # --- Normal move ---
    self.board[r0][c0] = '.'
    self.board[r1][c1] = piece if not promo else (promo if is_white else promo.lower())

    # Find king position
    king_sq = None
    for r in range(8):
        for c in range(8):
            if self.board[r][c] == ('K' if is_white else 'k'):
                king_sq = (r, c)
                break
        if king_sq:
            break

    # Check if own king is attacked
    legal = not attacked(self, king_sq, opponent)

    # --- Undo move ---
    self.board[r0][c0] = piece
    self.board[r1][c1] = captured
    if was_ep:
        self.board[pawn_row][c1] = ep_captured

    return legal

def attacked(self, sq, sd):
        r, c = sq
        board = self.board
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

# HELPERS
# Convert a position to algebraic notation
def notation(sq):
    files = "abcdefgh"  # columns
    ranks = "12345678"  # rows from White's perspective
    if 0 <= sq[0] < 8 and 0 <= sq[1] < 8:
        return files[sq[1]] + ranks[sq[0]]
    raise ValueError("Coordinates out of range")


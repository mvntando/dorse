from typing import cast
from utils import DIRECTIONS, SLIDING, attacked, PIECE_INDEX, PIECE_KEYS, SIDE_KEY, CASTLE_KEYS, EP_KEYS

# GAME LOGIC
# Move representation
class Move:
    __slots__ = ('src', 'dst', 'promo', 'piece', 'captured', 'score')

    def __init__(self, src: tuple[int, int], dst: tuple[int, int], promo: str | None, piece: str, captured: str | None = None):
        self.src = src
        self.dst = dst
        self.promo = promo

        self.piece = piece
        self.captured = captured

        self.score: int = 0

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.src == other.src and self.dst == other.dst and self.promo == other.promo)

    def __hash__(self):
        return hash((self.src, self.dst, self.promo))


class Undo:
    __slots__ = ('move', 'wc', 'bc', 'ep', 'sd', 'ep_sq', 'castle', 'wk', 'bk', 'hash')

    # This class represents the information needed to undo a move.
    # move      -- the move being undone
    # piece     -- the piece that was moved (for undoing promotion)
    # wc, bc    -- castling rights before the move
    # ep        -- en passant square before the move
    # sd        -- side to move before the move
    # ep_sq     -- the square of the captured pawn for en passant captures (for restoring captured pawn)
    # castle    -- if the move was a castling move, this indicates the rook move
    # wk, bk    -- the king squares before the move
    # hash      -- the Zobrist hash of the position before the move

    def __init__(self, move: Move, wc: tuple[int, int], bc: tuple[int, int], ep: tuple[int, int] | None, sd: str, wk: tuple[int, int] | None, bk: tuple[int, int] | None):
        self.move = move
        self.wc = wc
        self.bc = bc
        self.ep = ep
        self.sd = sd

        self.wk = wk
        self.bk = bk
        
        self.ep_sq: tuple[int, int] | None = None
        self.castle: int | None = None  # queenside: 0, kingside: 1 or None
        self.hash: int = 0


class UndoNull:
    __slots__ = ('ep', 'sd', 'hash')

    def __init__(self, ep: tuple[int, int] | None, sd: str, hash: int):
        self.ep = ep
        self.sd = sd
        self.hash = hash


class Position:
    __slots__ = ('board', 'wc', 'bc', 'ep', 'sd', 'wk', 'bk', 'score', 'stack', 'hash')

    # A state of a chess game
    # board   -- the current board state as a numpy array. !IMPOTANT - board is a cartesian grid
    # wc      -- white castling rights, [left/queen side, right/king side]
    # bc      -- black castling rights, [left/queen side, right/king side]
    # ep      -- the en passant square
    # sd      -- the player to move
    # wk      -- white king square (for quick in_check checks)
    # bk      -- black king square (for quick in_check checks)

    # score   -- the board evaluation (none unless incremental evaluation is enabled)
    # stack -- stack of Undo objects for undoing moves
    # hash    -- zobrist hash of the position

    def __init__(self, board: list[list[str]], wc: tuple[int, int], bc: tuple[int, int], ep: tuple[int, int] | None, sd: str):
        self.board = board
        self.wc = wc
        self.bc = bc
        self.ep = ep
        self.sd = sd
        
        self.wk: tuple[int, int] | None = None
        self.bk: tuple[int, int] | None = None
        
        self.score: int | None = None  # Reserved for future incremental evaluation
        self.stack: list[Undo | UndoNull] = []
        self.hash = self.gen_hash()  # Zobrist hash

        # Initialize king squares
        for r in range(8):
            for c in range(8):
                if board[r][c] == 'K':
                    self.wk = (r, c)
                elif board[r][c] == 'k':
                    self.bk = (r, c)


    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        return (all(r1 == r2 for r1, r2 in zip(self.board, other.board)) and self.wc == other.wc and self.bc == other.bc and self.ep == other.ep and self.sd == other.sd)

    # DEBUG: remove later
    def copy(self) -> 'Position':
        return Position(
            [row[:] for row in self.board],  # Deep copy of board
            self.wc,
            self.bc,
            None if self.ep is None else self.ep,
            self.sd,
        )
    
    def gen_hash(self) -> int:
        # Initialize hash
        h = 0
        # pieces
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]

                if piece != ".":
                    piece_index = PIECE_INDEX[piece]
                    sq = row * 8 + col
                    h ^= PIECE_KEYS[piece_index][sq]

        # side to move
        if self.sd == "w":
            h ^= SIDE_KEY

        # castling rights
        if self.wc[0] == 1:
            h ^= CASTLE_KEYS[0]
        if self.wc[1] == 1:
            h ^= CASTLE_KEYS[1]
        if self.bc[0] == 1:
            h ^= CASTLE_KEYS[2]
        if self.bc[1] == 1:
            h ^= CASTLE_KEYS[3]

        # en passant
        if self.ep is not None:
            file = self.ep[1]
            h ^= EP_KEYS[file]

        return h

    # Return legal moves for at a given position.
    def gen_moves(self) -> list[Move]:
        DIRS = DIRECTIONS # local alias

        moves: list[Move] = []

        for r0 in range(8):
            row = self.board[r0] # local row ref
            for c0 in range(8):
                piece = row[c0]
                if piece == '.':
                    continue
                # skip opponent pieces
                if self.sd == 'w':
                    if not piece.isupper():
                        continue
                else:  # player == 'b'
                    if not piece.islower():
                        continue

                is_white = piece.isupper()
                pu = piece.upper()

                # --- Pawn logic ---
                if pu == 'P':
                    if is_white:
                        fwd_dirs = DIRS["P"]
                        cap_dirs = DIRS["P_capture"]
                        start_row = 1
                        promo_row = 7
                    else:
                        fwd_dirs = DIRS["p"]
                        cap_dirs = DIRS["p_capture"]
                        start_row = 6
                        promo_row = 0
                    # forward moves
                    for dr, dc in fwd_dirs:
                        r = r0 + dr; c = c0 + dc
                        if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == '.':  # in bounds and empty
                            if r == promo_row:
                                for promo in ("q","r","b","n"):
                                    moves.append(Move((r0, c0), (r, c), promo, piece, None))
                            else:
                                moves.append(Move((r0, c0), (r, c), None, piece, None))
                            # double step
                            if r0 == start_row:
                                rr = r + dr; cc = c + dc
                                if 0 <= rr < 8 and 0 <= cc < 8 and self.board[rr][cc] == '.':
                                    moves.append(Move((r0, c0), (rr, cc), None, piece, None))
                    # captures
                    for dr, dc in cap_dirs:
                        r = r0 + dr; c = c0 + dc
                        if 0 <= r < 8 and 0 <= c < 8:
                            target = self.board[r][c]
                            # normal capture
                            if target != '.' and (target.isupper() != is_white):
                                if r == promo_row:
                                    for promo in ("q","r","b","n"):
                                        moves.append(Move((r0, c0), (r, c), promo, piece, target))
                                else:
                                    moves.append(Move((r0, c0), (r, c), None, piece, target))
                            # en passant capture
                            elif self.ep is not None and (r, c) == self.ep:
                                moves.append(Move((r0, c0), (r, c), None, piece, self.board[r0][c]))
                    # done with this pawn
                    continue

                # --- Non-pawns ---
                dirs = DIRS[pu]
                sliding = pu in SLIDING

                for dr, dc in dirs:
                    r = r0; c = c0
                    while True:
                        r += dr; c += dc
                        if not (0 <= r < 8 and 0 <= c < 8):
                            break
                        target = self.board[r][c]
                        if target == '.':
                            moves.append(Move((r0, c0), (r, c), None, piece, None))
                            if not sliding:
                                break
                        else:
                            # enemy?
                            if target.isupper() != is_white:
                                moves.append(Move((r0, c0), (r, c), None, piece, target))
                            break

                # --- Castling ---
                if pu == 'K':
                    back_row = 0 if is_white else 7
                    rights = self.wc if is_white else self.bc
                    opponent = 'b' if is_white else 'w'

                    # King-side castling
                    if rights[1]:  # king-side right available
                        if self.board[back_row][5] == '.' and self.board[back_row][6] == '.':
                            # King can't pass through check
                            if not attacked(self, (back_row, c0), opponent) and not attacked(self, (back_row, 5), opponent):
                                moves.append(Move((r0, c0), (back_row, 6), None, piece, None))

                    # Queen-side castling
                    if rights[0]:  # queen-side right available
                        if (self.board[back_row][1] == '.' and self.board[back_row][2] == '.' and self.board[back_row][3] == '.'):
                            # King can't pass through check
                            if not attacked(self, (back_row, c0), opponent) and not attacked(self, (back_row, 3), opponent):
                                moves.append(Move((r0, c0), (back_row, 2), None, piece, None))

        return moves
    
    # Return pseudo-legal capture moves at a given position.
    def gen_captures(self) -> list[Move]:
        DIRS = DIRECTIONS

        moves: list[Move] = []

        for r0 in range(8):
            row = self.board[r0]
            for c0 in range(8):
                piece = row[c0]
                if piece == '.':
                    continue

                if self.sd == 'w':
                    # Skip opponent pieces
                    if not piece.isupper():
                        continue
                else:
                    if not piece.islower():
                        continue

                is_white = piece.isupper()
                pu = piece.upper()

                # --- Pawn logic ---
                if pu == 'P':
                    cap_dirs = DIRS["P_capture"] if is_white else DIRS["p_capture"]
                    promo_row = 7 if is_white else 0
                    for dr, dc in cap_dirs:
                        r = r0 + dr; c = c0 + dc
                        if not (0 <= r < 8 and 0 <= c < 8):  # not in bounds
                            continue
                        target = self.board[r][c]
                        # normal capture
                        if target != '.' and target.isupper() != is_white:
                            if r == promo_row:
                                for promo in ("q","r","b","n"):
                                    moves.append(Move((r0,c0), (r,c), promo, piece, target))
                            else:
                                moves.append(Move((r0,c0), (r,c), None, piece, target))
                        # en passant capture
                        elif self.ep is not None and (r, c) == self.ep:
                            moves.append(Move((r0, c0), (r, c), None, piece, self.board[r0][c]))
                    continue

                # --- Non-pawns ---
                dirs = DIRS[pu]
                sliding = pu in SLIDING

                for dr, dc in dirs:
                    r = r0; c = c0
                    while True:
                        r += dr; c += dc
                        if not (0 <= r < 8 and 0 <= c < 8):
                            break

                        target = self.board[r][c]
                        if target == '.':
                            if not sliding:
                                break
                            continue
                        if target.isupper() != is_white:
                            moves.append(Move((r0,c0), (r,c), None, piece, target))
                        break
        
        return moves    

    def push(self, move: Move):
        # --- Push undo ---
        undo = Undo(move, self.wc, self.bc, self.ep, self.sd, self.wk, self.bk,)
        undo.hash = self.hash
        self.stack.append(undo)

        src, dst, promo = move.src, move.dst, move.promo
        r0, c0 = src
        r1, c1 = dst
        piece = self.board[r0][c0]

        is_white = self.sd == 'w'

        # Remove en passant hash if exists
        if self.ep is not None:
            self.hash ^= EP_KEYS[self.ep[1]]

        captured = move.captured
        # --- Handle en passant capture ---
        if piece.upper() == 'P' and self.ep and dst == self.ep:
            # --- Add captured piece for en passant undo ---
            undo.ep_sq = (r0, c1)

            # Remove captured pawn from board and hash
            sq_ep = r0 * 8 + c1
            captured_pawn = 'p' if is_white else 'P'
            self.hash ^= PIECE_KEYS[PIECE_INDEX[captured_pawn]][sq_ep]

            self.board[r0][c1] = '.'
        
        # Remove captured piece hash
        elif captured:
            sq_to = r1 * 8 + c1
            self.hash ^= PIECE_KEYS[PIECE_INDEX[captured]][sq_to]

        # --- Update castling rights if rook was captured ---
        if captured and captured.upper() == 'R':
            if is_white:  # Captured black rook
                if dst == (7, 0) and self.bc[0] != 0:  # a8 rook
                    self.hash ^= CASTLE_KEYS[2]  # remove black queenside hash
                    self.bc = (0, self.bc[1])
                elif dst == (7, 7) and self.bc[1] != 0:  # h8 rook
                    self.hash ^= CASTLE_KEYS[3]  # remove black kingside hash
                    self.bc = (self.bc[0], 0)
            else:  # Captured white rook
                if dst == (0, 0) and self.wc[0] != 0:  # a1 rook
                    self.hash ^= CASTLE_KEYS[0]  # remove white queenside hash
                    self.wc = (0, self.wc[1])
                elif dst == (0, 7) and self.wc[1] != 0:  # h1 rook
                    self.hash ^= CASTLE_KEYS[1]  # remove white kingside hash
                    self.wc = (self.wc[0], 0)

        # Update hash for moved piece
        sq_from = r0 * 8 + c0
        self.hash ^= PIECE_KEYS[PIECE_INDEX[piece]][sq_from]
        sq_to = r1 * 8 + c1
        self.hash ^= PIECE_KEYS[PIECE_INDEX[piece]][sq_to]

        # --- Move piece ---
        self.board[r1][c1] = piece
        self.board[r0][c0] = '.'

        # --- Handle promotion ---
        if promo is not None:
            self.hash ^= PIECE_KEYS[PIECE_INDEX[piece]][sq_to]  # remove pawn hash added before
            promo = promo.upper() if is_white else promo
            self.hash ^= PIECE_KEYS[PIECE_INDEX[promo]][sq_to]  # add promoted piece hash

            self.board[r1][c1] = promo

        # --- Handle castling (moving rook as well) ---
        if piece.upper() == 'K' and abs(c1 - c0) == 2:
            rook = 'R' if is_white else 'r'
            
            if c1 == 2:  # Queenside castling
                undo.castle = 0  # Update undo castle flag

                rook_from = r1 * 8 + 0
                rook_to   = r1 * 8 + 3
                # Update hash for rook move
                self.hash ^= PIECE_KEYS[PIECE_INDEX[rook]][rook_from]
                self.hash ^= PIECE_KEYS[PIECE_INDEX[rook]][rook_to]

                # Update board
                self.board[r1][3] = rook
                self.board[r1][0] = '.'

            else:  # Kingside castling
                undo.castle = 1  # Update undo castle flag

                rook_from = r1 * 8 + 7
                rook_to   = r1 * 8 + 5
                # Update hash for rook move
                self.hash ^= PIECE_KEYS[PIECE_INDEX[rook]][rook_from]
                self.hash ^= PIECE_KEYS[PIECE_INDEX[rook]][rook_to]

                # Update board
                self.board[r1][5] = rook
                self.board[r1][7] = '.'

        # --- Update castling rights and king squares ---
        if piece.upper() == 'K':  # King moved -> lose both rights
            if is_white:
                if self.wc != (0, 0):
                    if self.wc[0] != 0:
                        self.hash ^= CASTLE_KEYS[0]  # remove white queenside hash
                    if self.wc[1] != 0:
                        self.hash ^= CASTLE_KEYS[1]  # remove white kingside hash

                    self.wc = (0, 0)
                self.wk = (r1, c1)
            else:
                if self.bc != (0, 0):
                    if self.bc[0] != 0:
                        self.hash ^= CASTLE_KEYS[2]  # remove black queenside hash
                    if self.bc[1] != 0:
                        self.hash ^= CASTLE_KEYS[3]  # remove black kingside hash

                    self.bc = (0, 0)
                self.bk = (r1, c1)

        elif piece.upper() == 'R':  # Rook moved
            if is_white:  # White rook moved
                if src == (0, 0):  # a1 rook
                    if self.wc[0] != 0:
                        self.hash ^= CASTLE_KEYS[0]  # remove white queenside hash
                        self.wc = (0, self.wc[1])
                elif src == (0, 7):  # h1 rook
                    if self.wc[1] != 0:
                        self.hash ^= CASTLE_KEYS[1]  # remove white kingside hash
                        self.wc = (self.wc[0], 0)
            else:  # Black rook moved
                if src == (7, 0):  # a8 rook
                    if self.bc[0] != 0:
                        self.hash ^= CASTLE_KEYS[2]  # remove black queenside hash
                        self.bc = (0, self.bc[1])
                elif src == (7, 7):  # h8 rook
                    if self.bc[1] != 0:
                        self.hash ^= CASTLE_KEYS[3]  # remove black kingside hash
                        self.bc = (self.bc[0], 0)

        # --- Update en passant target ---
        if piece.upper() == 'P' and abs(r1 - r0) == 2:
            ep_row = (r0 + r1) // 2
            enemy = 'p' if is_white else 'P'
            if any(0 <= nc < 8 and self.board[r1][nc] == enemy for nc in (c0 - 1, c0 + 1)):
                self.ep = (ep_row, c0)
                self.hash ^= EP_KEYS[c0]  # add new ep hash
            else:
                self.ep = None
        
        else:
            self.ep = None

        # --- Switch side ---
        self.hash ^= SIDE_KEY  # switch side hash
        self.sd = 'b' if is_white else 'w'

        return self
    
    def pop(self):
        undo = cast(Undo, self.stack.pop())

        move = undo.move
        r0, c0 = move.src
        r1, c1 = move.dst

        # Restore state FIRST
        self.sd = undo.sd
        self.wc = undo.wc
        self.bc = undo.bc
        self.ep = undo.ep
        self.wk = undo.wk
        self.bk = undo.bk
        self.hash = undo.hash

        # --- Undo move ---
        self.board[r1][c1] = '.'
        self.board[r0][c0] = undo.move.piece
            
        # --- Undo castling rook move ---
        if undo.castle is not None:
            if undo.castle == 1:  # kingside
                rook = self.board[r1][5]
                self.board[r1][5] = '.'
                self.board[r1][7] = rook
            else:  # queenside
                rook = self.board[r1][3]
                self.board[r1][3] = '.'
                self.board[r1][0] = rook

        # --- Restore captured piece ---
        if undo.move.captured:
            if undo.ep_sq:
                er, ec = undo.ep_sq
                self.board[er][ec] = undo.move.captured
            else:
                self.board[r1][c1] = undo.move.captured
        
        return self

    def push_null(self):
        undo = UndoNull(self.ep, self.sd, self.hash)
        self.stack.append(undo)

        if self.ep is not None:
            self.hash ^= EP_KEYS[self.ep[1]]
            self.ep = None

        self.hash ^= SIDE_KEY
        self.sd = 'b' if self.sd == 'w' else 'w'

        return self
    
    def pop_null(self):
        undo = cast(UndoNull, self.stack.pop())
        self.ep = undo.ep
        self.sd = undo.sd
        self.hash = undo.hash

        return self
    
    def in_check(self, sd: str) -> bool:
        """
        Check if the king of side `sd` is attacked by opponent.
        """
        # This must NOT depend on position.sd, because legality checks in search occur AFTER push(), when position.sd has already flipped.
        
        king = self.wk if sd == 'w' else self.bk
        if king is None:
            raise ValueError(f"King square for {sd} is not set")

        opponent = 'b' if sd == 'w' else 'w'
        return attacked(self, king, opponent)

    def make_uci_move(self, uci_move: str):
        file_from = ord(uci_move[0]) - ord('a')
        rank_from = int(uci_move[1]) - 1
        file_to   = ord(uci_move[2]) - ord('a')
        rank_to   = int(uci_move[3]) - 1

        src = (rank_from, file_from)
        dst = (rank_to, file_to)

        promo = (p.upper() if self.sd == 'w' else p) if (p := uci_move[4:5]) else None

        for m in self.gen_moves():
            if m.src == src and m.dst == dst:
                if promo is None or (m.promo and m.promo.upper() == promo.upper()):
                    self.push(m)
                    return

        raise ValueError(f"Illegal UCI move: {uci_move}")

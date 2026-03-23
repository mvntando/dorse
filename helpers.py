from dorse import Position, Move

# Convert a position to algebraic notation
def square(sq: tuple[int, int]) -> str:
    y, x = sq

    if not (0 <= x < 8 and 0 <= y < 8):
        raise ValueError("Coordinates out of range")

    file = chr(ord('a') + x)
    rank = str(y + 1)

    return file + rank

# Convert algebraic notation to position
def coord(s: str) -> tuple[int, int]:
    if len(s) != 2:
        raise ValueError("Invalid square notation")

    file, rank = s[0], s[1]

    if not ('a' <= file <= 'h') or not ('1' <= rank <= '8'):
        raise ValueError("Invalid square notation")

    x = ord(file) - ord('a')
    y = int(rank) - 1

    return y, x

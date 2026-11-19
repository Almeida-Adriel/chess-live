import time
import chess

CASTLE_ROOK = {
        (chess.WHITE, True):  ("h1", "f1"),   # roque pequeno das brancas
        (chess.WHITE, False): ("a1", "d1"),   # roque grande das brancas
        (chess.BLACK, True):  ("h8", "f8"),   # roque pequeno das pretas
        (chess.BLACK, False): ("a8", "d8"),   # roque grande das pretas
    }
    
def build_move_event(game_id: str, fen_before: str, uci: str,
                     fen_after: str, wc: int, bc: int) -> dict:
    board = chess.Board(fen_before)
    move = chess.Move.from_uci(uci)

    # TODO 1: peça que se moveu e cor
    piece = board.piece_at(move.from_square)
    if piece is None:
        raise ValueError(
            f"nenhuma peça em {chess.square_name(move.from_square)} — fen_before e uci não batem"
        )
    color = "white" if piece.color == chess.WHITE else "black"

    # TODO 2: captura (cuidado com en passant)
    captured = None
    capture_square = None
    if board.is_capture(move):
        if board.is_en_passant(move):
            offset = -8 if piece.color == chess.WHITE else 8
            sq = move.to_square + offset
        else:
            sq = move.to_square
        captured = board.piece_at(sq).symbol()
        capture_square = chess.square_name(sq)

    # TODO 3: roque → de onde para onde foi a torre
    
    # TODO 4: san ANTES do push; check/mate DEPOIS do push

    # TODO 5: conferir se board.fen() depois do push == fen_after

    return {...}
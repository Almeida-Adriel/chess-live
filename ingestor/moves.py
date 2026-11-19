import time
import chess

# TODO 3: de onde para onde a torre vai em cada roque
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

    # TODO 3: roque → movimento da torre
    castle_rook = None
    if board.is_castling(move):
        rook_from, rook_to = CASTLE_ROOK[(piece.color, board.is_kingside_castling(move))]
        castle_rook = {"from": rook_from, "to": rook_to}

    # promoção
    promotion = chess.piece_symbol(move.promotion) if move.promotion else None

    # TODO 4: o que precisa do tabuleiro ANTES do lance...
    if not board.is_legal(move):
        raise ValueError(f"lance ilegal {uci} na posição {fen_before}")
    san = board.san(move)
    ply = board.ply()

    board.push(move)  # ← a partir daqui, o tabuleiro está DEPOIS do lance

    # ...e o que só existe DEPOIS do lance
    is_check = board.is_check()
    is_mate = board.is_checkmate()

    # TODO 5: checagem de qualidade — a posição calculada bate com a do Lichess?
    fen_ok = board.fen().split()[:3] == fen_after.split()[:3]
    if not fen_ok:
        print(f"[AVISO] {game_id} ply {ply}: posição divergente\n"
              f"  calculada: {board.fen()}\n  lichess:   {fen_after}")

    return {
        "game_id": game_id,
        "source": "tv",
        "ply": ply,
        "uci": uci,
        "san": san,
        "color": color,
        "piece": piece.symbol(),
        "from": chess.square_name(move.from_square),
        "to": chess.square_name(move.to_square),
        "captured": captured,
        "capture_square": capture_square,
        "castle_rook": castle_rook,
        "promotion": promotion,
        "check": is_check,
        "mate": is_mate,
        "fen_before": fen_before,
        "fen_after": fen_after,
        "fen_ok": fen_ok,
        "clock": {"white": wc, "black": bc},
        "ingested_at": time.time(),
    }


if __name__ == "__main__":
    casos = [
        ("lance normal (seus dados)",
         "r2q1rk1/p5bp/1p1Pbnp1/2p1n3/Q4B2/2N3P1/PP3PBP/R2R2K1 b - - 1 19", "e5g4",
         "r2q1rk1/p5bp/1p1Pbnp1/2p5/Q4Bn1/2N3P1/PP3PBP/R2R2K1 w - - 2 20"),
        ("captura (seus dados)",
         "r2q1rk1/p5bp/1p1PN1p1/2p5/Q4nn1/6P1/PP3PBP/R2R2K1 b - - 0 22", "f4e6",
         "r2q1rk1/p5bp/1p1Pn1p1/2p5/Q5n1/6P1/PP3PBP/R2R2K1 w - - 0 23"),
        ("roque pequeno",
         "r3k2r/pppqbppp/2np1n2/4p3/4P3/2NP1N2/PPPQBPPP/R3K2R w KQkq - 0 1", "e1g1",
         "r3k2r/pppqbppp/2np1n2/4p3/4P3/2NP1N2/PPPQBPPP/R4RK1 b kq - 1 1"),
        ("roque grande",
         "r3k2r/pppqbppp/2np1n2/4p3/4P3/2NP1N2/PPPQBPPP/R3K2R w KQkq - 0 1", "e1c1",
         "r3k2r/pppqbppp/2np1n2/4p3/4P3/2NP1N2/PPPQBPPP/2KR3R b kq - 1 1"),
        ("promoção com xeque",
         "8/P7/8/8/8/8/8/k6K w - - 0 1", "a7a8q",
         "Q7/8/8/8/8/8/8/k6K b - - 0 1"),
        ("xeque-mate (mate do louco)",
         "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2", "d8h4",
         "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"),
        ("posição divergente (fen_after errado de propósito)",
         "r2q1rk1/p5bp/1p1Pbnp1/2p1n3/Q4B2/2N3P1/PP3PBP/R2R2K1 b - - 1 19", "e5g4",
         "8/8/8/8/8/8/8/k6K w - - 0 1"),
    ]
    for nome, fb, uci, fa in casos:
        ev = build_move_event("teste", fb, uci, fa, 30, 30)
        resumo = {k: ev[k] for k in ("ply", "san", "piece", "captured",
                                     "castle_rook", "promotion", "check", "mate", "fen_ok")}
        print(f"{nome}:\n  {resumo}")
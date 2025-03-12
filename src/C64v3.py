import chess


inf = float("inf")
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}


def evaluate(board: chess.Board):
    evaluation = 0

    for piece_type in range(1, 6):
        white_pieces = board.pieces_mask(piece_type, chess.WHITE).bit_count()
        black_pieces = board.pieces_mask(piece_type, chess.BLACK).bit_count()
        
        evaluation += (white_pieces - black_pieces) * piece_values[piece_type]
    
    perspective = (1 if board.turn == chess.WHITE else -1)
    return evaluation * perspective

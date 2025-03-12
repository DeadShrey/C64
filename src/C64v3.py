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


def search(board: chess.Board, depth: int, alpha: int, beta: int):
    if board.outcome() is not None:
        if board.is_checkmate():
            return -inf
        
        return 0
    
    if depth == 0:
        return evaluate(board)

    for move in board.legal_moves:
        board.push(move)
        evaluation = -search(board, depth - 1, -beta, -alpha)
        board.pop()

        alpha = max(alpha, evaluation)
        if alpha >= beta:
            return alpha  # *Snip*
    
    return alpha


def lookup(board: chess.Board, depth: int):
    best_move = None
    best_eval = -inf

    for move in board.legal_moves:
        board.push(move)
        evaluation = -search(board, depth - 1, -inf, inf)
        board.pop()

        if best_eval < evaluation:
            best_eval = evaluation
            best_move = move
        
        elif best_eval == -inf and evaluation == -inf: # The situation is helpless :(
            best_eval = evaluation
            best_move = move
    
    return best_move

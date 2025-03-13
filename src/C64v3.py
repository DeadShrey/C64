import chess


inf = float("inf")
piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 325,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

psqts = {
    chess.PAWN: [
         0,   0,   0,   0,   0,   0,   0,   0,
        50,  50,  50,  50,  50,  50,  50,  50,
        10,  10,  20,  30,  30,  20,  10,  10,
         5,   5,  10,  25,  25,  10,   5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,  -5, -10,   0,   0, -10,  -5,   5,
         5,  10,  10, -20, -20,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    chess.KNIGHT: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20,   0,   5,   5,   0, -20, -40,
        -30,   5,  10,  15,  15,  10,   5, -30,
        -30,   0,  15,  20,  20,  15,   0, -30,
        -30,   5,  15,  20,  20,  15,   5, -30,
        -30,   0,  10,  15,  15,  10,   0, -30,
        -40, -20,   0,   0,   0,   0, -20, -40,
        -50, -20, -30, -30, -30, -30, -20, -50
    ],
    chess.BISHOP: [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10,   5,   0,   0,   0,   0,   5, -10,
        -10,  10,  10,  10,  10,  10,  10, -10,
        -10,   0,  10,  10,  10,  10,   0, -10,
        -10,   5,   5,  10,  10,   5,   5, -10,
        -10,   0,   5,  10,  10,   5,   0, -10,
        -10,   0,   0,   0,   0,   0,   0, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
    ],
    chess.ROOK: [
         0,   0,   0,   5,   5,   0,   0,   0,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         5,  10,  10,  10,  10,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    chess.QUEEN: [
        -20, -10, -10,  -5,  -5, -10, -10, -20,
        -10,   0,   0,   0,   0,   0,   0, -10,
        -10,   0,   5,   5,   5,   5,   0, -10,
         -5,   0,   5,   5,   5,   5,   0,  -5,
          0,   0,   5,   5,   5,   5,   0,  -5,
        -10,   5,   5,   5,   5,   5,   0, -10,
        -10,   0,   5,   0,   0,   0,   0, -10,
        -20, -10, -10,  -5,  -5, -10, -10, -20
    ],
    chess.KING: [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
         20,  20,   0,   0,   0,   0,  20,  20,
         20,  30,  10,   0,   0,  10,  30,  20
    ]
}


def evaluate(board: chess.Board):
    evaluation = 0

    white_material = 0
    white_psqt_score = 0
    black_material = 0
    black_psqt_score = 0

    for sq in range(64):
        piece = board.piece_at(sq)
        if piece is None: continue

        # Conting material value and applying psqts
        psqt = psqts[piece.piece_type]

        if piece.color == chess.WHITE:
            white_material += piece_values[piece.piece_type]
            white_psqt_score += psqt[chess.square_mirror(sq)]
        
        else:
            black_material += piece_values[piece.piece_type]
            black_psqt_score += psqt[sq]

    evaluation += white_material - black_material
    evaluation += white_psqt_score - black_psqt_score
    
    perspective = (1 if board.turn == chess.WHITE else -1)
    return evaluation * perspective


def order_moves(move: chess.Move, board: chess.Board):
    guess_score = 0
    moved_piece = board.piece_type_at(move.from_square)
    captured_piece = board.piece_type_at(move.to_square)
    
    if captured_piece is not None:
        guess_score += 10 * piece_values[captured_piece] - piece_values[moved_piece]  # MVV-LVA
    
    elif board.is_en_passant(move):
        guess_score += 10 - piece_values[moved_piece]  # The captured piece is a pawn
    
    else:
        # The move is not a capture
        if move.promotion is not None:
            guess_score += 50
        
        elif board.is_attacked_by(not board.turn, move.to_square):
            guess_score -= piece_values[moved_piece]
    
    return guess_score


def search(board: chess.Board, depth: int, alpha: int, beta: int):
    if board.outcome() is not None:
        if board.is_checkmate():
            return -inf
        
        return 0
    
    if depth == 0:
        return evaluate(board)
    
    ordered_moves = sorted(board.legal_moves, key=lambda move: order_moves(move, board), reverse=True)

    for move in ordered_moves:
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

        if best_eval <= evaluation:
            best_eval = evaluation
            best_move = move
    
    return best_move

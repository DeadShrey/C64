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

killer_moves = [[None, None] for _ in range(100)]  # Storing 2 killer moves for each position

mirrored_sq = tuple(chess.square_mirror(sq) for sq in range(64))  # Precomputing mirrored squares
psqts = {
    chess.PAWN: (
         0,   0,   0,   0,   0,   0,   0,   0,
        50,  50,  50,  50,  50,  50,  50,  50,
        10,  10,  20,  30,  30,  20,  10,  10,
         5,   5,  10,  25,  25,  10,   5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,  -5, -10,   0,   0, -10,  -5,   5,
         5,  10,  10, -20, -20,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ),
    chess.KNIGHT: (
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20,   0,   5,   5,   0, -20, -40,
        -30,   5,  10,  15,  15,  10,   5, -30,
        -30,   0,  15,  20,  20,  15,   0, -30,
        -30,   5,  15,  20,  20,  15,   5, -30,
        -30,   0,  10,  15,  15,  10,   0, -30,
        -40, -20,   0,   0,   0,   0, -20, -40,
        -50, -20, -30, -30, -30, -30, -20, -50
    ),
    chess.BISHOP: (
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10,   5,   0,   0,   0,   0,   5, -10,
        -10,  10,  10,  10,  10,  10,  10, -10,
        -10,   0,  10,  10,  10,  10,   0, -10,
        -10,   5,   5,  10,  10,   5,   5, -10,
        -10,   0,   5,  10,  10,   5,   0, -10,
        -10,   0,   0,   0,   0,   0,   0, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
    ),
    chess.ROOK: (
         0,   0,   0,   5,   5,   0,   0,   0,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         5,  10,  10,  10,  10,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ),
    chess.QUEEN: (
        -20, -10, -10,  -5,  -5, -10, -10, -20,
        -10,   0,   0,   0,   0,   0,   0, -10,
        -10,   0,   5,   5,   5,   5,   0, -10,
         -5,   0,   5,   5,   5,   5,   0,  -5,
          0,   0,   5,   5,   5,   5,   0,  -5,
        -10,   5,   5,   5,   5,   5,   0, -10,
        -10,   0,   5,   0,   0,   0,   0, -10,
        -20, -10, -10,  -5,  -5, -10, -10, -20
    ),
    chess.KING: (
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
         20,  20,   0,   0,   0,   0,  20,  20,
         20,  30,  10,   0,   0,  10,  30,  20
    )
}


def evaluate(board: chess.Board):
    evaluation = 0

    white_material = 0
    black_material = 0
    white_psqt_score = 0
    black_psqt_score = 0

    for piece_type in range(1, 7):
        white_bb = board.pieces_mask(piece_type, chess.WHITE)
        black_bb = board.pieces_mask(piece_type, chess.BLACK)
        piece_value = piece_values[piece_type]

        # Counting material
        white_material += white_bb.bit_count() * piece_value
        black_material += black_bb.bit_count() * piece_value

        # Applying PSQTs
        psqt = psqts[piece_type]
        for sq in chess.scan_reversed(white_bb):
            white_psqt_score += psqt[mirrored_sq[sq]]
        
        for sq in chess.scan_reversed(black_bb):
            black_psqt_score += psqt[sq]

    evaluation += white_material - black_material
    evaluation += white_psqt_score - black_psqt_score
    
    return evaluation if board.turn == chess.WHITE else -evaluation  # Taking perspective into account


def order_moves(move: chess.Move, board: chess.Board, depth: int):
    guess_score = 0
    moved_piece = board.piece_type_at(move.from_square)
    captured_piece = board.piece_type_at(move.to_square)
    
    if captured_piece is not None:
        guess_score += 10 * piece_values[captured_piece] - piece_values[moved_piece]  # MVV-LVA
    
    else:
        # The move is not a capture
        if move in killer_moves[depth - 1]:
            return 100000

        if move.promotion:
            guess_score += 50
        
        elif board.is_attacked_by(not board.turn, move.to_square):
            guess_score -= piece_values[moved_piece]
    
    return guess_score


def order_captures(move: chess.Move, board: chess.Board):
    moved_piece = board.piece_type_at(move.from_square)
    captured_piece = board.piece_type_at(move.to_square)
    
    if captured_piece is not None:
        return 10 * piece_values[captured_piece] - piece_values[moved_piece]  # MVV-LVA

    return 10 - piece_values[moved_piece]  # En passant


def quiescence_search(board: chess.Board, alpha: int, beta: int):
    if board.outcome() is not None:
        if board.is_checkmate():
            return -inf
        
        return 0
    
    stand_pat = evaluate(board)
    if stand_pat >= beta: return stand_pat
    alpha = max(alpha, stand_pat)

    ordered_captures = sorted(board.generate_legal_captures(), key=lambda move: order_captures(move, board), reverse=True)

    for move in ordered_captures:
        board.push(move)
        evaluation = -quiescence_search(board, -beta, -alpha)
        board.pop()

        if evaluation >= beta: return beta
        alpha = max(alpha, evaluation)

    return alpha


def search(board: chess.Board, depth: int, alpha: int, beta: int):
    if board.outcome() is not None:
        if board.is_checkmate():
            return -inf
        
        return 0
    
    if depth == 0:
        return quiescence_search(board, alpha, beta)
    
    ordered_moves = sorted(board.legal_moves, key=lambda move: order_moves(move, board, depth), reverse=True)

    for move in ordered_moves:
        board.push(move)
        evaluation = -search(board, depth - 1, -beta, -alpha)
        board.pop()

        if evaluation >= beta:
            if not board.is_capture(move):  # The move is not a capture and can be used as a killer move
                killer_moves[depth - 1] = [killer_moves[depth - 1][1], move]

            return beta  # *Snip*
        
        alpha = max(alpha, evaluation)

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

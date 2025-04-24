import random

# Giá trị các quân cờ
piece_values = {
    'P': 100,   # Tốt
    'N': 320,   # Mã
    'B': 330,   # Tượng
    'R': 500,   # Xe
    'Q': 900,   # Hậu
    'K': 20000  # Vua
}

# Bảng giá trị vị trí cho từng quân cờ
pawn_scores = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

knight_scores = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

bishop_scores = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5,  5,  5,  5,  5,-10],
    [-10,  0,  5,  0,  0,  5,  0,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

rook_scores = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

queen_scores = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

king_scores_middle_game = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
]

king_scores_end_game = [
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,  0,  0,-10,-20,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-30,  0,  0,  0,  0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50]
]

piece_position_scores = {
    'P': pawn_scores,
    'N': knight_scores,
    'B': bishop_scores,
    'R': rook_scores,
    'Q': queen_scores,
    'K': king_scores_middle_game
}

# Hằng số để kiểm tra giai đoạn cuối game
ENDGAME_MATERIAL_THRESHOLD = 3000  # Ngưỡng vật liệu tổng cộng để xác định giai đoạn cuối game

CHECKMATE_SCORE = 10000
STALEMATE_SCORE = 0
DEPTH = 3
QUIESCENCE_DEPTH = 2  # Độ sâu cho tìm kiếm yên tĩnh

def find_best_move(game_state, valid_moves, return_queue=None):
    """
    Tìm nước đi tốt nhất sử dụng thuật toán alpha-beta với quiescence search và move ordering.
    """
    global next_move
    next_move = None

    # Dùng alpha-beta để tìm nước đi tốt nhất
    find_move_alpha_beta(game_state, valid_moves, DEPTH, -float('inf'), float('inf'),
                        1 if game_state.white_to_move else -1)

    if return_queue is not None:
        return_queue.put(next_move)
    # Nếu không tìm thấy nước đi nào (rất hiếm), chọn ngẫu nhiên
    if next_move is None and valid_moves:
        next_move = random.choice(valid_moves)
        if return_queue is not None:
             return_queue.put(next_move)  # Đảm bảo luôn trả về gì đó
    elif next_move is None and not valid_moves:
         if return_queue is not None:
             return_queue.put(None)  # Không có nước đi hợp lệ

    return next_move

def order_moves(game_state, moves):
    """
    Sắp xếp các nước đi để cải thiện hiệu quả alpha-beta.
    Ưu tiên: Bắt quân giá trị cao, Phong cấp, Chiếu, Nước đi khác.
    """
    move_scores = {}
    for move in moves:
        score = 0
        # Ưu tiên bắt quân
        if move.piece_captured != "--":
            # Lấy giá trị quân bị bắt trừ đi giá trị quân tấn công (ước tính đơn giản)
            score += 10 * piece_values[move.piece_captured[1]] - piece_values[move.piece_moved[1]]

        # Ưu tiên phong cấp
        if move.is_pawn_promotion:
            score += piece_values['Q']  # Thưởng bằng giá trị Hậu

        move_scores[move] = score

    # Sắp xếp giảm dần theo điểm số
    return sorted(moves, key=lambda m: move_scores[m], reverse=True)

def find_move_alpha_beta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    """
    Thuật toán minimax với alpha-beta pruning và quiescence search.
    """
    global next_move

    if depth == 0:
        return quiescence_search(game_state, QUIESCENCE_DEPTH, alpha, beta, turn_multiplier)

    # Move ordering
    ordered_moves = order_moves(game_state, valid_moves)

    max_score = -float('inf')
    for move in ordered_moves:  # Sử dụng danh sách đã sắp xếp
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_move_alpha_beta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        game_state.undo_move()

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break  # Cắt tỉa Beta

    return max_score

def quiescence_search(game_state, depth, alpha, beta, turn_multiplier):
    """
    Tìm kiếm sâu hơn cho các nước đi bắt quân để tránh horizon effect.
    """
    stand_pat_score = turn_multiplier * score_board(game_state)

    if depth == 0:
        return stand_pat_score

    if stand_pat_score >= beta:
        return beta  # Cắt tỉa Beta (fail-hard)
    if stand_pat_score > alpha:
        alpha = stand_pat_score  # Cập nhật Alpha

    # Chỉ xem xét các nước đi bắt quân (và có thể là phong cấp/chiếu)
    capture_moves = [move for move in game_state.get_valid_moves() if move.piece_captured != "--" or move.is_pawn_promotion]
    ordered_captures = order_moves(game_state, capture_moves)  # Sắp xếp các nước bắt quân

    for move in ordered_captures:
        game_state.make_move(move)
        score = -quiescence_search(game_state, depth - 1, -beta, -alpha, -turn_multiplier)
        game_state.undo_move()

        if score >= beta:
            return beta  # Cắt tỉa Beta
        if score > alpha:
            alpha = score  # Cập nhật Alpha

    return alpha  # Trả về điểm tốt nhất tìm được hoặc điểm stand-pat ban đầu

def score_board(game_state):
    """
    Đánh giá trạng thái bàn cờ. Cải thiện với Xe cột mở, Tốt thông.
    Điểm số dương có lợi cho bên trắng, điểm số âm có lợi cho bên đen.
    """
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE_SCORE  # Đen chiếu bí
        else:
            return CHECKMATE_SCORE  # Trắng chiếu bí
    elif game_state.stalemate:
        return STALEMATE_SCORE  # Hòa

    score = 0
    total_material = 0
    white_pawns = []
    black_pawns = []
    white_rooks = []
    black_rooks = []

    # Tính tổng vật liệu và thu thập vị trí quân
    for row in range(8):
        for col in range(8):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_type = piece[1]
                if piece_type != 'K':
                    total_material += piece_values[piece_type]
                if piece == "wP": white_pawns.append((row, col))
                elif piece == "bP": black_pawns.append((row, col))
                elif piece == "wR": white_rooks.append((row, col))
                elif piece == "bR": black_rooks.append((row, col))

    is_endgame = total_material < ENDGAME_MATERIAL_THRESHOLD

    for row in range(8):
        for col in range(8):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_type = piece[1]
                piece_color = piece[0]
                piece_score = piece_values[piece_type]

                # Điểm vị trí
                if piece_type == 'K':
                    position_score = (king_scores_end_game if is_endgame else king_scores_middle_game)[row][col]
                else:
                    # Đảo ngược bảng điểm cho quân đen
                    pos_row = 7 - row if piece_color == 'b' else row
                    position_score = piece_position_scores[piece_type][pos_row][col]

                if piece_color == 'w':
                    score += piece_score + position_score
                else:
                    score -= piece_score + position_score

    # Đánh giá cấu trúc tốt
    pawn_structure_score = evaluate_pawn_structure(game_state, white_pawns, black_pawns)
    score += pawn_structure_score

    # Đánh giá an toàn của vua
    king_safety_score = evaluate_king_safety(game_state, is_endgame)
    score += king_safety_score

    # Đánh giá Xe trên cột mở/nửa mở
    rook_placement_score = evaluate_rook_placement(game_state, white_rooks, black_rooks, white_pawns, black_pawns)
    score += rook_placement_score

    # Đánh giá Tốt thông
    passed_pawn_score = evaluate_passed_pawns(game_state, white_pawns, black_pawns)
    score += passed_pawn_score

    return score

def evaluate_pawn_structure(game_state, white_pawns, black_pawns):
    """
    Đánh giá cấu trúc tốt: tốt cô lập, tốt đôi, tốt bảo vệ...
    """
    score = 0
    # Đánh giá tốt cô lập
    white_isolated = count_isolated_pawns(white_pawns)
    black_isolated = count_isolated_pawns(black_pawns)
    score -= white_isolated * 15  # Phạt tốt trắng cô lập
    score += black_isolated * 15  # Thưởng nếu tốt đen cô lập (bất lợi cho đen)

    # Đánh giá tốt đôi
    white_doubled = count_doubled_pawns(white_pawns)
    black_doubled = count_doubled_pawns(black_pawns)
    score -= white_doubled * 20  # Phạt tốt trắng đôi
    score += black_doubled * 20  # Thưởng nếu tốt đen đôi

    return score

def count_isolated_pawns(pawns):
    """
    Đếm số lượng tốt cô lập (không có tốt đồng minh ở cột liền kề)
    """
    isolated_count = 0
    pawn_columns = [col for _, col in pawns]

    for _, col in pawns:
        is_isolated = True
        for adjacent_col in [col-1, col+1]:
            if 0 <= adjacent_col < 8 and adjacent_col in pawn_columns:
                is_isolated = False
                break
        if is_isolated:
            isolated_count += 1

    return isolated_count

def count_doubled_pawns(pawns):
    """
    Đếm số lượng tốt đôi (nhiều tốt trên cùng một cột)
    """
    columns = [col for _, col in pawns]
    doubled_count = 0

    for col in range(8):
        pawns_in_col = columns.count(col)
        if pawns_in_col > 1:
            doubled_count += pawns_in_col - 1

    return doubled_count

def evaluate_king_safety(game_state, is_endgame):
    """
    Đánh giá an toàn của vua, thêm phạt cột mở gần vua.
    """
    score = 0
    if is_endgame: return 0  # Vua nên tích cực ở cuối game

    # An toàn Vua Trắng
    w_king_row, w_king_col = game_state.white_king_location
    w_king_safety = calculate_king_safety_score(game_state, w_king_row, w_king_col, 'w')
    score += w_king_safety

    # An toàn Vua Đen
    b_king_row, b_king_col = game_state.black_king_location
    b_king_safety = calculate_king_safety_score(game_state, b_king_row, b_king_col, 'b')
    score -= b_king_safety

    return score

def calculate_king_safety_score(game_state, king_row, king_col, king_color):
    """Tính điểm an toàn cho một vua cụ thể."""
    safety_score = 0
    ally_color = king_color
    enemy_color = 'b' if king_color == 'w' else 'w'

    # 1. Quân đồng minh bảo vệ xung quanh
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for d_row, d_col in directions:
        r, c = king_row + d_row, king_col + d_col
        if 0 <= r < 8 and 0 <= c < 8 and game_state.board[r][c][0] == ally_color:
            safety_score += 3

    # 2. Cấu trúc tốt bảo vệ (Pawn Shield)
    pawn_shield_bonus = 0
    shield_row = king_row + (1 if king_color == 'b' else -1)  # Hàng tốt bảo vệ lý tưởng
    if 0 <= shield_row < 8:
        for dc in [-1, 0, 1]:
            shield_col = king_col + dc
            if 0 <= shield_col < 8:
                piece = game_state.board[shield_row][shield_col]
                if piece == ally_color + 'P':
                    pawn_shield_bonus += 10  # Tốt ở vị trí che chắn tốt

    # Thưởng nếu vua đã nhập thành và có lá chắn tốt
    castled = False
    if king_color == 'w' and king_row == 7 and king_col in [1, 2, 6]: castled = True
    if king_color == 'b' and king_row == 0 and king_col in [1, 2, 6]: castled = True
    if castled:
        safety_score += 15 + pawn_shield_bonus
    else:
        safety_score += pawn_shield_bonus // 2

    # 3. Phạt cột mở/nửa mở gần vua
    open_file_penalty = 0
    for dc in [-1, 0, 1]:  # Kiểm tra 3 cột: cột vua và 2 cột bên cạnh
        check_col = king_col + dc
        if 0 <= check_col < 8:
            is_open = True
            is_semi_open_ally = True
            is_semi_open_enemy = True
            for r in range(8):
                piece = game_state.board[r][check_col]
                if piece == ally_color + 'P':
                    is_open = False
                    is_semi_open_enemy = False
                elif piece == enemy_color + 'P':
                    is_open = False
                    is_semi_open_ally = False

            if is_open:
                open_file_penalty += 15
            elif is_semi_open_enemy:
                open_file_penalty += 8

    safety_score -= open_file_penalty

    return safety_score

def evaluate_rook_placement(game_state, white_rooks, black_rooks, white_pawns, black_pawns):
    """Đánh giá vị trí của quân Xe (cột mở, nửa mở, hàng 7)."""
    score = 0
    all_pawns = white_pawns + black_pawns

    # Xe trắng
    for r_row, r_col in white_rooks:
        col_pawns = [p_row for p_row, p_col in all_pawns if p_col == r_col]
        col_white_pawns = [p_row for p_row, p_col in white_pawns if p_col == r_col]
        if not col_pawns:  # Cột mở
            score += 15
        elif not col_white_pawns:  # Cột nửa mở (chỉ có tốt đen)
            score += 8
        if r_row == 1:  # Hàng 7
            score += 20

    # Xe đen
    for r_row, r_col in black_rooks:
        col_pawns = [p_row for p_row, p_col in all_pawns if p_col == r_col]
        col_black_pawns = [p_row for p_row, p_col in black_pawns if p_col == r_col]
        if not col_pawns:  # Cột mở
            score -= 15
        elif not col_black_pawns:  # Cột nửa mở (chỉ có tốt trắng)
            score -= 8
        if r_row == 6:  # Hàng 2
            score -= 20

    return score

def evaluate_passed_pawns(game_state, white_pawns, black_pawns):
    """Đánh giá Tốt thông."""
    score = 0
    # Tốt trắng
    for p_row, p_col in white_pawns:
        is_passed = True
        for b_row, b_col in black_pawns:
            if b_col >= p_col - 1 and b_col <= p_col + 1 and b_row < p_row:
                is_passed = False
                break
        if is_passed:
            passed_pawn_bonus = (7 - p_row) * 10
            score += passed_pawn_bonus

    # Tốt đen
    for p_row, p_col in black_pawns:
        is_passed = True
        for w_row, w_col in white_pawns:
            if w_col >= p_col - 1 and w_col <= p_col + 1 and w_row > p_row:
                is_passed = False
                break
        if is_passed:
            passed_pawn_bonus = p_row * 10
            score -= passed_pawn_bonus

    return score
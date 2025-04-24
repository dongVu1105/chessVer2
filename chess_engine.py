class GameState():
    def __init__(self):
        # Bàn cờ là ma trận 8x8, mỗi ô là một chuỗi gồm 2 ký tự
        # Ký tự đầu tiên biểu thị màu của quân cờ ('b' cho đen, 'w' cho trắng)
        # Ký tự thứ hai biểu thị loại quân cờ ('R' cho xe, 'N' cho mã, 'B' cho tượng, 'Q' cho hậu, 'K' cho vua, 'P' cho tốt)
        # "--" biểu thị ô trống
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.move_log = []
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 
                               'N': self.get_knight_moves, 'B': self.get_bishop_moves, 
                               'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = () # Tọa độ của ô có thể bắt tốt qua đường
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                              self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    def make_move(self, move):
        """
        Thực hiện nước đi (không xử lý trường hợp nhập thành, phong cấp, bắt tốt qua đường)
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move) # Ghi lại nước đi để có thể hoàn tác
        self.white_to_move = not self.white_to_move # Chuyển lượt đi
        # Cập nhật vị trí vua nếu đã di chuyển
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # Phong cấp cho tốt
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"  # Mặc định phong cấp thành hậu

        # Bắt tốt qua đường
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"  # Xóa quân tốt bị bắt

        # Cập nhật biến enpassant_possible
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:  # Chỉ áp dụng nếu tốt di chuyển 2 ô
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()
        
        self.enpassant_possible_log.append(self.enpassant_possible)

        # Di chuyển nhập thành
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # Nhập thành bên vua
                # Di chuyển xe từ góc đến bên cạnh vua
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            else:  # Nhập thành bên hậu
                # Di chuyển xe từ góc đến bên cạnh vua
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

        # Cập nhật quyền nhập thành
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                 self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    def undo_move(self):
        """
        Hoàn tác nước đi cuối cùng
        """
        if len(self.move_log) != 0:  # Đảm bảo có nước đi để hoàn tác
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # Chuyển lượt chơi
            # Cập nhật vị trí vua nếu hoàn tác di chuyển vua
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            
            # Hoàn tác bắt tốt qua đường
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"  # Xóa tốt từ ô đích
                self.board[move.start_row][move.end_col] = move.piece_captured  # Đặt lại tốt bị bắt

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # Hoàn tác các quyền nhập thành
            self.castle_rights_log.pop()  # Bỏ quyền nhập thành hiện tại
            new_rights = self.castle_rights_log[-1]  # Lấy quyền nhập thành trước đó
            self.current_castling_rights = CastleRights(new_rights.wks, new_rights.bks, 
                                                       new_rights.wqs, new_rights.bqs)

            # Hoàn tác nhập thành
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # Nhập thành bên vua
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:  # Nhập thành bên hậu
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"
            
            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move):
        """
        Cập nhật quyền nhập thành dựa trên nước đi
        """
        if move.piece_moved == 'wK':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # Xe trắng bên trái
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # Xe trắng bên phải
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # Xe đen bên trái
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # Xe đen bên phải
                    self.current_castling_rights.bks = False

        # Nếu xe bị bắt
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.bks = False

    def get_valid_moves(self):
        """
        Tất cả các nước đi hợp lệ có xét đến chiếu
        """
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                         self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        # 1. Tạo tất cả các nước đi có thể
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]

        if self.in_check:
            if len(self.checks) == 1:  # Chỉ có một quân đang chiếu
                moves = self.get_all_possible_moves()
                # Để chặn chiếu, ta có thể di chuyển quân khác để chặn hoặc bắt quân đang chiếu
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # Các ô mà quân di chuyển đến có thể chặn chiếu
                # Nếu là mã thì phải bắt mã hoặc di chuyển vua
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                
                # Loại bỏ các nước đi không chặn được chiếu hoặc không di chuyển vua
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':  # Không phải di chuyển vua
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:  # Không chặn được chiếu
                            moves.remove(moves[i])
            else:  # Chiếu kép, vua phải di chuyển
                self.get_king_moves(king_row, king_col, moves)
        else:  # Không bị chiếu
            moves = self.get_all_possible_moves()
            if self.white_to_move:
                self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassant_possible = temp_enpassant_possible
        self.current_castling_rights = temp_castle_rights
        return moves

    def check_for_pins_and_checks(self):
        pins = []  # Quân bị ghim
        checks = []  # Các quân đang chiếu
        in_check = False
        
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        
        # Kiểm tra tất cả 8 hướng từ vua
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j, direction in enumerate(directions):
            d_row, d_col = direction
            possible_pin = ()  # Quân đồng minh có thể bị ghim
            for i in range(1, 8):
                end_row = start_row + d_row * i
                end_col = start_col + d_col * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():  # Mới tìm thấy quân đồng minh đầu tiên
                            possible_pin = (end_row, end_col, d_row, d_col)
                        else:  # Tìm thấy quân đồng minh thứ hai, không có ghim
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        # 5 trường hợp:
                        # 1. Theo hướng thẳng và gặp xe hoặc hậu
                        # 2. Theo hướng chéo và gặp tượng hoặc hậu
                        # 3. Đi 1 ô theo đường chéo và gặp tốt (chỉ kiểm tra với hai hướng)
                        # 4. Đi theo bất kỳ hướng nào và gặp vua (để phòng trường hợp di chuyển sẽ mở ra đường chiếu)
                        # 5. Bất kỳ hướng nào và gặp mã (kiểm tra riêng)
                        if (0 <= j <= 3 and piece_type == 'R') or \
                           (4 <= j <= 7 and piece_type == 'B') or \
                           (i == 1 and piece_type == 'P' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                           (piece_type == 'Q') or (i == 1 and piece_type == 'K'):
                            if possible_pin == ():  # Không có quân chặn, đang bị chiếu
                                in_check = True
                                checks.append((end_row, end_col, d_row, d_col))
                                break
                            else:  # Có quân chặn, bị ghim
                                pins.append(possible_pin)
                                break
                        else:  # Quân địch không chiếu được
                            break
                else:  # Ngoài bàn cờ
                    break
        
        # Kiểm tra chiếu bởi mã
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':  # Mã địch đang chiếu
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        
        return in_check, pins, checks

    def is_square_under_attack(self, row, col, attacking_color):
        """
        Xác định xem ô (row, col) có đang bị tấn công bởi quân màu attacking_color hay không
        """
        # Kiểm tra tất cả các quân địch, xem chúng có thể tấn công ô này không
        opponent_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece[0] == attacking_color:  # Quân địch
                    piece_type = piece[1]
                    if piece_type == 'P':
                        self.get_pawn_moves(r, c, opponent_moves, just_captures=True, target=(row, col))
                    else:
                        self.move_functions[piece_type](r, c, opponent_moves, just_captures=True, target=(row, col))
        
        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def get_all_possible_moves(self):
        """
        Tất cả các nước đi có thể mà không xét đến chiếu
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece[0] == 'w' and self.white_to_move) or (piece[0] == 'b' and not self.white_to_move):
                    piece_type = piece[1]
                    self.move_functions[piece_type](row, col, moves)
        return moves

    def get_pawn_moves(self, row, col, moves, just_captures=False, target=None):
        """
        Lấy tất cả các nước đi của quân tốt ở vị trí (row, col)
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = 'b'
            king_row, king_col = self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            enemy_color = 'w'
            king_row, king_col = self.black_king_location

        if not just_captures:
            # Tốt đi tới 1 ô
            if self.board[row + move_amount][col] == "--":
                if not piece_pinned or pin_direction == (move_amount, 0):
                    moves.append(Move((row, col), (row + move_amount, col), self.board))
                    # Tốt đi tới 2 ô từ vị trí khởi đầu
                    if row == start_row and self.board[row + 2 * move_amount][col] == "--":
                        moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))

        # Tốt bắt chéo
        directions = [(move_amount, -1), (move_amount, 1)]  # Bắt chéo trái, phải
        for direction in directions:
            end_row = row + direction[0]
            end_col = col + direction[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if target is None or (end_row == target[0] and end_col == target[1]):
                    if not piece_pinned or pin_direction == direction:
                        end_piece = self.board[end_row][end_col]
                        if end_piece[0] == enemy_color:  # Bắt quân địch
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif (end_row, end_col) == self.enpassant_possible:
                            attacking_piece = blocking_piece = False
                            if king_row == row:
                                if king_col < col:  # Vua ở bên trái tốt
                                    # Trong khoảng giữa vua và tốt
                                    inside_range = range(king_col + 1, col)
                                    # Ngoài khoảng, giữa tốt và rìa bàn cờ
                                    outside_range = range(col + 1, 8)
                                else:  # Vua ở bên phải tốt
                                    inside_range = range(col + 1, king_col)
                                    outside_range = range(0, col)
                                for i in inside_range:
                                    if self.board[row][i] != "--":  # Có quân chặn đường
                                        blocking_piece = True
                                for i in outside_range:
                                    square = self.board[row][i]
                                    if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                        attacking_piece = True
                                    elif square != "--":
                                        blocking_piece = True
                            if not attacking_piece or blocking_piece:
                                moves.append(Move((row, col), (end_row, end_col), self.board, is_enpassant_move=True))

    def get_rook_moves(self, row, col, moves, just_captures=False, target=None):
        """
        Lấy tất cả các nước đi của quân xe ở vị trí (row, col)
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':  # Không xóa ghim nếu là hậu
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # Lên, trái, xuống, phải
        enemy_color = 'b' if self.white_to_move else 'w'
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if target is None or (end_row == target[0] and end_col == target[1]):
                        if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                            end_piece = self.board[end_row][end_col]
                            if end_piece == "--":  # Ô trống
                                if not just_captures:
                                    moves.append(Move((row, col), (end_row, end_col), self.board))
                            elif end_piece[0] == enemy_color:  # Bắt quân địch
                                moves.append(Move((row, col), (end_row, end_col), self.board))
                                break
                            else:  # Quân đồng minh
                                break
                        else:  # Nếu bị ghim và đi không đúng hướng
                            break
                else:  # Ngoài bàn cờ
                    break

    def get_knight_moves(self, row, col, moves, just_captures=False, target=None):
        """
        Lấy tất cả các nước đi của quân mã ở vị trí (row, col)
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        ally_color = 'w' if self.white_to_move else 'b'
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if target is None or (end_row == target[0] and end_col == target[1]):
                    if not piece_pinned:
                        end_piece = self.board[end_row][end_col]
                        if end_piece[0] != ally_color:  # Ô trống hoặc quân địch
                            if not just_captures or end_piece != "--":
                                moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves, just_captures=False, target=None):
        """
        Lấy tất cả các nước đi của quân tượng ở vị trí (row, col)
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':  # Không xóa ghim nếu là hậu
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Đường chéo: tây bắc, đông bắc, tây nam, đông nam
        enemy_color = 'b' if self.white_to_move else 'w'
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if target is None or (end_row == target[0] and end_col == target[1]):
                        if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                            end_piece = self.board[end_row][end_col]
                            if end_piece == "--":  # Ô trống
                                if not just_captures:
                                    moves.append(Move((row, col), (end_row, end_col), self.board))
                            elif end_piece[0] == enemy_color:  # Bắt quân địch
                                moves.append(Move((row, col), (end_row, end_col), self.board))
                                break
                            else:  # Quân đồng minh
                                break
                        else:  # Nếu bị ghim và đi không đúng hướng
                            break
                else:  # Ngoài bàn cờ
                    break

    def get_queen_moves(self, row, col, moves, just_captures=False, target=None):
        """
        Lấy tất cả các nước đi của quân hậu ở vị trí (row, col)
        """
        self.get_rook_moves(row, col, moves, just_captures, target)
        self.get_bishop_moves(row, col, moves, just_captures, target)

    def get_king_moves(self, row, col, moves, just_captures=False, target=None):
        """
        Lấy tất cả các nước đi của quân vua ở vị trí (row, col)
        """
        row_moves = [-1, -1, -1, 0, 0, 1, 1, 1]
        col_moves = [-1, 0, 1, -1, 1, -1, 0, 1]
        ally_color = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if target is None or (end_row == target[0] and end_col == target[1]):
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # Ô trống hoặc quân địch
                        # Tạm thời di chuyển vua để kiểm tra xem có bị chiếu không
                        if ally_color == 'w':
                            self.white_king_location = (end_row, end_col)
                        else:
                            self.black_king_location = (end_row, end_col)
                        in_check, _, _ = self.check_for_pins_and_checks()
                        if not in_check:
                            if not just_captures or end_piece != "--":
                                moves.append(Move((row, col), (end_row, end_col), self.board))
                        # Đặt vua trở lại vị trí ban đầu
                        if ally_color == 'w':
                            self.white_king_location = (row, col)
                        else:
                            self.black_king_location = (row, col)

    def get_castle_moves(self, row, col, moves):
        """
        Tạo tất cả các nước nhập thành hợp lệ cho vua ở (row, col) và thêm vào danh sách moves
        """
        if self.in_check:  # Không thể nhập thành khi bị chiếu
            return
        
        if (self.white_to_move and self.current_castling_rights.wks) or \
           (not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(row, col, moves)
            
        if (self.white_to_move and self.current_castling_rights.wqs) or \
           (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(row, col, moves)

    def get_kingside_castle_moves(self, row, col, moves):
        """
        Tạo nước nhập thành bên vua nếu hợp lệ
        """
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.is_square_under_attack(row, col + 1, 'b' if self.white_to_move else 'w') and \
               not self.is_square_under_attack(row, col + 2, 'b' if self.white_to_move else 'w'):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, row, col, moves):
        """
        Tạo nước nhập thành bên hậu nếu hợp lệ
        """
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.is_square_under_attack(row, col - 1, 'b' if self.white_to_move else 'w') and \
               not self.is_square_under_attack(row, col - 2, 'b' if self.white_to_move else 'w'):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # White king-side
        self.bks = bks  # Black king-side
        self.wqs = wqs  # White queen-side
        self.bqs = bqs  # Black queen-side

class Move:
    # Ánh xạ các tọa độ của bàn cờ sang ký hiệu đại số (algebraic notation)
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}
    
    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # Xác định xem nước đi có phong cấp cho tốt không
        self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7)
        # Xác định xem nước đi có phải là bắt tốt qua đường không
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'
        # Xác định xem nước đi có phải là nhập thành không
        self.is_castle_move = is_castle_move
        # Tạo ID duy nhất cho mỗi nước đi
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    '''
    Override the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    '''
    Override the hash method
    '''
    def __hash__(self):
        # Return the hash of the unique move_id (which is an integer)
        return hash(self.move_id)

    def get_chess_notation(self):
        """
        Chuyển đổi nước đi sang ký hiệu đại số
        """
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        """
        Chuyển đổi tọa độ (row, col) sang ký hiệu đại số (ví dụ: "e4")
        """
        return self.cols_to_files[col] + self.rows_to_ranks[row]
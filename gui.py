import pygame as p
import chess_engine
import chess_ai
import sys
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 400
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Colors
WHITE = p.Color("white")
BLACK = p.Color("black")
GRAY = p.Color("gray")
BLUE = p.Color("blue")
GREEN = p.Color(162, 209, 73)
LIGHT = p.Color(232, 235, 239)
DARK = p.Color(125, 135, 150)

def load_images():
    """
    Tải hình ảnh các quân cờ. Chỉ thực hiện một lần.
    """
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("assets/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)
        )

def main():
    """
    Hàm chính xử lý đầu vào của người dùng và cập nhật đồ họa
    """
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    p.display.set_caption('Chess - Người chơi vs. AI')
    clock = p.time.Clock()
    screen.fill(WHITE)
    
    game_state = chess_engine.GameState()
    valid_moves = game_state.get_valid_moves()
    
    move_made = False  # Cờ để theo dõi khi nước đi được thực hiện
    animate = False  # Cờ để theo dõi khi cần hoạt ảnh
    
    load_images()  # Chỉ thực hiện một lần
    
    running = True
    sq_selected = ()  # Lần chọn cuối cùng của người dùng (tuple: (row, col))
    player_clicks = []  # Theo dõi các lần click của người chơi (hai tuples: [(6,4), (4,4)])
    game_over = False
    player_one = True  # Nếu người chơi điều khiển quân trắng thì True, nếu AI thì False
    player_two = False  # Nếu người chơi điều khiển quân đen thì True, nếu AI thì False
    ai_thinking = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    
    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # Xử lý sự kiện chuột
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) vị trí của chuột
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    
                    if sq_selected == (row, col) or col >= 8:  # Người dùng click cùng một ô hoặc click vào log
                        sq_selected = ()  # Bỏ chọn
                        player_clicks = []  # Xóa các lần click
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)  # Thêm cả lần click thứ nhất và thứ hai
                    
                    if len(player_clicks) == 2 and human_turn:  # Sau lần click thứ hai
                        move = chess_engine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()  # Reset lựa chọn
                                player_clicks = []
                        
                        if not move_made:
                            player_clicks = [sq_selected]
            
            # Xử lý sự kiện bàn phím
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo khi nhấn 'z'
                    game_state.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                
                if e.key == p.K_r:  # Reset khi nhấn 'r'
                    game_state = chess_engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                
                if e.key == p.K_1:  # Người chơi vs. AI
                    player_one = True
                    player_two = False
                    game_state = chess_engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                
                if e.key == p.K_2:  # AI vs. Người chơi
                    player_one = False
                    player_two = True
                    game_state = chess_engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                        
                if e.key == p.K_3:  # AI vs. AI
                    player_one = False
                    player_two = False
                    game_state = chess_engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                        
                if e.key == p.K_4:  # Người chơi vs. Người chơi
                    player_one = True
                    player_two = True
                    game_state = chess_engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
        
        # AI Move Finder
        if not game_over and not human_turn and not ai_thinking:
            ai_thinking = True
            return_queue = Queue()  # Dùng để truyền dữ liệu giữa các threads
            move_finder_process = Process(target=chess_ai.find_best_move, args=(game_state, valid_moves, return_queue))
            move_finder_process.start()
        
        if ai_thinking and not move_finder_process.is_alive():
            ai_move = return_queue.get()
            if ai_move is not None:
                game_state.make_move(ai_move)
                move_made = True
                animate = True
            ai_thinking = False
        
        if move_made:
            if animate:
                animate_move(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False
        
        draw_game_state(screen, game_state, valid_moves, sq_selected, move_log_font)
        
        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                draw_text(screen, "Đen chiếu bí")
            else:
                draw_text(screen, "Trắng chiếu bí")
        elif game_state.stalemate:
            game_over = True
            draw_text(screen, "Hòa cờ do bế tắc")
        
        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen, game_state, valid_moves, sq_selected, move_log_font):
    """
    Chịu trách nhiệm vẽ toàn bộ giao diện
    """
    draw_board(screen)  # Vẽ các ô của bàn cờ
    highlight_squares(screen, game_state, valid_moves, sq_selected)
    draw_pieces(screen, game_state.board)  # Vẽ các quân cờ lên các ô
    draw_move_log(screen, game_state, move_log_font)

def draw_board(screen):
    """
    Vẽ các ô của bàn cờ
    """
    global colors
    colors = [LIGHT, DARK]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(screen, game_state, valid_moves, sq_selected):
    """
    Highlight ô đã chọn và các nước đi hợp lệ
    """
    if sq_selected != ():
        r, c = sq_selected
        if r < 8 and c < 8:  # Đảm bảo ô đã chọn nằm trong bàn cờ
            # Highlight ô đã chọn
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Độ trong suốt 0-255
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            
            # Highlight các nước đi từ ô đó
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))

def draw_pieces(screen, board):
    """
    Vẽ các quân cờ lên bàn cờ sử dụng trạng thái hiện tại của board
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animate_move(move, screen, board, clock):
    """
    Tạo hoạt ảnh cho nước đi
    """
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 5  # Số khung hình để di chuyển 1 ô
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    
    for frame in range(frame_count + 1):
        r, c = (move.start_row + d_row * frame / frame_count, 
                move.start_col + d_col * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        
        # Xóa quân cờ ở ô đích để tránh vẽ hai quân
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        
        # Vẽ quân bị bắt
        if move.piece_captured != "--":
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        
        # Vẽ quân đang di chuyển
        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_move_log(screen, game_state, font):
    """
    Vẽ nhật ký các nước đi
    """
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, GRAY, move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + ". " + move_log[i].get_chess_notation() + " "
        if i + 1 < len(move_log):
            move_string += move_log[i + 1].get_chess_notation()
        move_texts.append(move_string)
    
    padding = 5
    text_y = padding
    line_spacing = 18
    
    for i in range(len(move_texts)):
        text = font.render(move_texts[i], True, BLACK)
        text_rect = text.get_rect()
        text_rect.topleft = (BOARD_WIDTH + padding, text_y)
        screen.blit(text, text_rect)
        text_y += line_spacing

def draw_text(screen, text):
    """
    Vẽ text ở giữa màn hình
    """
    font = p.font.SysFont("Arial", 32, True, False)
    text_object = font.render(text, False, p.Color("Black"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2
    )
    screen.blit(text_object, text_location)

if __name__ == "__main__":
    main()
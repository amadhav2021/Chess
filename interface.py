"""App to play chess. Claude 3.5 Sonnet was used to help with development"""


import pygame
from copy import deepcopy


class ChessBoard:
    def __init__(self):
        pygame.init()
        self.SQUARE_SIZE = 80
        self.BOARD_SIZE = self.SQUARE_SIZE * 8
        self.screen = pygame.display.set_mode((self.BOARD_SIZE, self.BOARD_SIZE + 40))  # Extra height for status
        pygame.display.set_caption("Chess Game")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BROWN = (139, 69, 19)
        self.YELLOW = (255, 255, 0, 50)
        self.RED = (255, 0, 0, 50)
        
        # Game state
        self.selected_piece = None
        self.piece_count = 32
        self.pieces_left = {
            'wP': 8,
            'wR': 2,
            'wN': 2,
            'wB': 2,
            'wQ': 1,
            'wK': 1,
            'bP': 8,
            'bR': 2,
            'bN': 2,
            'bB': 2,
            'bQ': 1,
            'bK': 1,
        }
        self.white_to_move = True
        self.in_check = False
        self.checkmate = False
        self.stalemate = False
        self.insufficient = False
        
        # Initialize piece positions
        self.board_state = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        
        # Load piece images
        self.pieces = {}
        for piece in ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 
                     'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']:
            self.pieces[piece] = pygame.transform.scale(
                pygame.image.load(f'images/{piece}.png'),
                (self.SQUARE_SIZE, self.SQUARE_SIZE)
            )
        
        self.valid_moves = []

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = self.WHITE if (row + col) % 2 == 0 else self.BROWN
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    pygame.Rect(
                        col * self.SQUARE_SIZE,
                        row * self.SQUARE_SIZE,
                        self.SQUARE_SIZE,
                        self.SQUARE_SIZE
                    )
                )
        
        # Highlight selected piece and valid moves
        if self.selected_piece:
            row, col = self.selected_piece
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(self.YELLOW)
            self.screen.blit(s, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE))
            
            for move in self.valid_moves:
                end_row, end_col = move
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                s.set_alpha(100)
                s.fill(self.YELLOW)
                self.screen.blit(s, (end_col * self.SQUARE_SIZE, end_row * self.SQUARE_SIZE))
        
        # Highlight king in check
        if self.in_check:
            king_pos = self.find_king(self.white_to_move)
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(self.RED)
            self.screen.blit(s, (king_pos[1] * self.SQUARE_SIZE, king_pos[0] * self.SQUARE_SIZE))

        # Draw status bar
        status_rect = pygame.Rect(0, self.BOARD_SIZE, self.BOARD_SIZE, 40)
        pygame.draw.rect(self.screen, (200, 200, 200), status_rect)
        font = pygame.font.Font(None, 36)
        
        # Status text
        status = "White to move" if self.white_to_move else "Black to move"
        if self.checkmate:
            status = "Checkmate! " + ("Black" if self.white_to_move else "White") + " wins!"
        elif self.stalemate:
            status = "Stalemate! Draw."
        elif self.insufficient:
            status = "Insufficient material! Draw."
        elif self.in_check:
            status = "Check! " + status
        
        text = font.render(status, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.BOARD_SIZE/2, self.BOARD_SIZE + 20))
        self.screen.blit(text, text_rect)

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board_state[row][col]
                if piece != '--':
                    self.screen.blit(
                        self.pieces[piece],
                        pygame.Rect(
                            col * self.SQUARE_SIZE,
                            row * self.SQUARE_SIZE,
                            self.SQUARE_SIZE,
                            self.SQUARE_SIZE
                        )
                    )

    def find_king(self, is_white_king):
        """Find the position of the king"""
        king = 'wK' if is_white_king else 'bK'
        for row in range(8):
            for col in range(8):
                if self.board_state[row][col] == king:
                    return (row, col)
        return None

    def is_under_attack(self, row, col, is_white):
        """Check if a square is under attack by opponent pieces"""
        opponent_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board_state[r][c]
                if piece != '--' and (piece[0] == 'b' if is_white else piece[0] == 'w'):
                    opponent_moves.extend(self.get_valid_moves_for_piece(r, c, check_check=False))
        return (row, col) in opponent_moves

    def is_insufficient(self):
        """Check if the current board state has insufficient material"""
        
        if self.piece_count == 2: return True
        if self.piece_count >= 4: return False
        
        if (self.pieces_left['wP'] > 0) or (self.pieces_left['bP'] > 0): return False
        if (self.pieces_left['wQ'] > 0) or (self.pieces_left['bQ'] > 0): return False
        if (self.pieces_left['wR'] > 0) or (self.pieces_left['bR'] > 0): return False

        return True


    def make_move(self, start_row, start_col, end_row, end_col):
        """Make a move and update game state"""
        # Store current state
        old_board = deepcopy(self.board_state)

        # Check if the move is a capture
        destination = self.board_state[end_row][end_col]
        if destination != '--':
            self.pieces_left[destination]-=1
            self.piece_count-=1
        
        # Make the move
        self.board_state[end_row][end_col] = self.board_state[start_row][start_col]
        self.board_state[start_row][start_col] = '--'
        
        # Switch turns
        self.white_to_move = not self.white_to_move
        
        # Check if the move puts the opponent in check
        king_pos = self.find_king(self.white_to_move)
        self.in_check = self.is_under_attack(king_pos[0], king_pos[1], self.white_to_move)
        
        # Check for checkmate and stalemate
        has_valid_moves = False
        for r in range(8):
            for c in range(8):
                piece = self.board_state[r][c]
                if piece != '--' and piece[0] == ('w' if self.white_to_move else 'b'):
                    moves = self.get_valid_moves_for_piece(r, c)
                    if moves:
                        has_valid_moves = True
                        break
            if has_valid_moves:
                break
        
        if not has_valid_moves:
            self.checkmate = self.in_check
            self.stalemate = not self.in_check

        # Check for draw by insufficient material
        self.insufficient = self.is_insufficient()

    def get_valid_moves_for_piece(self, start_row, start_col, check_check=True):
        """Get all valid moves for a piece"""
        piece = self.board_state[start_row][start_col]
        moves = []
        
        if piece == '--':
            return moves
            
        piece_type = piece[1]
        piece_color = piece[0]
        
        # Pawn moves
        if piece_type == 'P':
            direction = 1 if piece_color == 'b' else -1
            
            # Forward move
            if 0 <= start_row + direction < 8 and self.board_state[start_row + direction][start_col] == '--':
                moves.append((start_row + direction, start_col))
                # Initial two-square move
                if (piece_color == 'w' and start_row == 6) or (piece_color == 'b' and start_row == 1):
                    if self.board_state[start_row + 2*direction][start_col] == '--':
                        moves.append((start_row + 2*direction, start_col))
            
            # Captures
            for col_offset in [-1, 1]:
                if 0 <= start_col + col_offset < 8 and 0 <= start_row + direction < 8:
                    target_piece = self.board_state[start_row + direction][start_col + col_offset]
                    if target_piece != '--' and target_piece[0] != piece_color:
                        moves.append((start_row + direction, start_col + col_offset))
        
        # Rook moves
        elif piece_type == 'R':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in directions:
                for i in range(1, 8):
                    end_row = start_row + dr * i
                    end_col = start_col + dc * i
                    if 0 <= end_row < 8 and 0 <= end_col < 8:
                        target_piece = self.board_state[end_row][end_col]
                        if target_piece == '--':
                            moves.append((end_row, end_col))
                        elif target_piece[0] != piece_color:
                            moves.append((end_row, end_col))
                            break
                        else:
                            break
                    else:
                        break
        
        # Knight moves
        elif piece_type == 'N':
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_moves:
                end_row = start_row + dr
                end_col = start_col + dc
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    target_piece = self.board_state[end_row][end_col]
                    if target_piece == '--' or target_piece[0] != piece_color:
                        moves.append((end_row, end_col))
        
        # Bishop moves
        elif piece_type == 'B':
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    end_row = start_row + dr * i
                    end_col = start_col + dc * i
                    if 0 <= end_row < 8 and 0 <= end_col < 8:
                        target_piece = self.board_state[end_row][end_col]
                        if target_piece == '--':
                            moves.append((end_row, end_col))
                        elif target_piece[0] != piece_color:
                            moves.append((end_row, end_col))
                            break
                        else:
                            break
                    else:
                        break
        
        # Queen moves (combination of Rook and Bishop)
        elif piece_type == 'Q':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                         (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    end_row = start_row + dr * i
                    end_col = start_col + dc * i
                    if 0 <= end_row < 8 and 0 <= end_col < 8:
                        target_piece = self.board_state[end_row][end_col]
                        if target_piece == '--':
                            moves.append((end_row, end_col))
                        elif target_piece[0] != piece_color:
                            moves.append((end_row, end_col))
                            break
                        else:
                            break
                    else:
                        break
        
        # King moves
        elif piece_type == 'K':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                         (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                end_row = start_row + dr
                end_col = start_col + dc
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    target_piece = self.board_state[end_row][end_col]
                    if target_piece == '--' or target_piece[0] != piece_color:
                        moves.append((end_row, end_col))
        
        # Filter moves that would leave/put the king in check
        if check_check:
            valid_moves = []
            for move in moves:
                # Make temporary move
                temp_board = deepcopy(self.board_state)
                end_row, end_col = move
                self.board_state[end_row][end_col] = self.board_state[start_row][start_col]
                self.board_state[start_row][start_col] = '--'
                
                # Check if king is in check after move
                king_pos = self.find_king(piece_color == 'w')
                if not self.is_under_attack(king_pos[0], king_pos[1], piece_color == 'w'):
                    valid_moves.append(move)
                
                # Restore board
                self.board_state = temp_board
            
            return valid_moves
        
        return moves

    def handle_click(self, row, col):
        if self.checkmate or self.stalemate or self.insufficient:
            return
            
        if self.selected_piece is None:
            piece = self.board_state[row][col]
            if piece != '--' and ((piece[0] == 'w' and self.white_to_move) or 
                                (piece[0] == 'b' and not self.white_to_move)):
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves_for_piece(row, col)
        else:
            start_row, start_col = self.selected_piece
            if (row, col) in self.valid_moves:
                self.make_move(start_row, start_col, row, col)
            self.selected_piece = None
            self.valid_moves = []

    def run_game(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        pos = pygame.mouse.get_pos()
                        col = pos[0] // self.SQUARE_SIZE
                        row = pos[1] // self.SQUARE_SIZE
                        self.handle_click(row, col)

            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = ChessBoard()
    game.run_game()
"""App to play chess. Claude 3.5 Sonnet was used to help with development"""


import pygame


class ChessBoard:
    def __init__(self):
        pygame.init()
        self.SQUARE_SIZE = 80
        self.BOARD_SIZE = self.SQUARE_SIZE * 8
        self.screen = pygame.display.set_mode((self.BOARD_SIZE, self.BOARD_SIZE))
        pygame.display.set_caption("Chess Game")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BROWN = (139, 69, 19)
        self.YELLOW = (255, 255, 0, 50)  # Highlighting color
        
        # Game state
        self.selected_piece = None
        self.white_to_move = True
        self.move_log = []
        
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
            
        # Valid moves for the selected piece
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
            
            # Highlight valid moves
            for move in self.valid_moves:
                end_row, end_col = move
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                s.set_alpha(100)
                s.fill(self.YELLOW)
                self.screen.blit(s, (end_col * self.SQUARE_SIZE, end_row * self.SQUARE_SIZE))

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

    def get_valid_moves(self, start_row, start_col):
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
        
        return moves

    def handle_click(self, row, col):
        if self.selected_piece is None:
            piece = self.board_state[row][col]
            if piece != '--' and ((piece[0] == 'w' and self.white_to_move) or 
                                (piece[0] == 'b' and not self.white_to_move)):
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
        else:
            start_row, start_col = self.selected_piece
            if (row, col) in self.valid_moves:
                # Make the move
                self.board_state[row][col] = self.board_state[start_row][start_col]
                self.board_state[start_row][start_col] = '--'
                self.white_to_move = not self.white_to_move
                self.move_log.append((start_row, start_col, row, col))
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
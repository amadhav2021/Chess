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

    def run_game(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = ChessBoard()
    game.run_game()
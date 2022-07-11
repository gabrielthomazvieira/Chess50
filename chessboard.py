'''This file handles most functions related to drawings and animations.
Source: https://www.pygame.org/docs/ and https://www.geeksforgeeks.org
'''

import pyperclip
import pygame as p
from gamestate import *

gs = GameState()
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images():
    '''Scales and loads the images from file to the game.
    '''

    pieces = ["wP", "wR", "wN", "wB", "wQ",
              "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(
            "assets/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        


def draw_game_state(screen, gs, valid_moves, sq_selected):
    '''Draws the current gamestate.
    '''

    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    check(screen, gs)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs)


def draw_board(screen):
    '''Draws the board by creating a for loop in the specified dimension
    and drawing rectangles with alternating colors.
    '''

    global colors
    colors = [p.Color("light gray"), p.Color("dark gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight_squares(screen, gs, valid_moves, sq_selected):
    '''Highlights the squares which a piece can move to.
    '''

    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.w_to_move else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color("light blue"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.target_col * SQ_SIZE,
                                move.target_row * SQ_SIZE))
                    
def check(screen, gs):
    if gs.w_to_move and gs.in_check():
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("red"))
        screen.blit(s, (gs.w_king_coord[1] * SQ_SIZE,
                    gs.w_king_coord[0] * SQ_SIZE))
    elif not gs.w_to_move and gs.in_check():
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("red"))
        screen.blit(s, (gs.b_king_coord[1] * SQ_SIZE,
                    gs.b_king_coord[0] * SQ_SIZE))

def draw_move_log(screen, gs):
    '''Draws the move log on the right side of the board.
    '''

    # Sets font and rectangle.
    move_log_font = p.font.SysFont("Helvitca", 18, False, False)
    move_log_rect = p.Rect(
        BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("gray90"), move_log_rect)

    # Iterates through the move log and creates a list with all the moves
    # converted to proper chess notation.
    tmp = gs.move_log
    moves_list = []
    for i in range(0, len(tmp), 2):
        fullmove_notation = str(i // 2 + 1) + ". " + \
            str(tmp[i].chess_notation()) + " "
        if i + 1 < len(tmp):
            fullmove_notation += str(tmp[i + 1].chess_notation()) + "  "
        moves_list.append(fullmove_notation)

    # Renders the moves on the screen.
    moves_row = 3
    padding = 5
    text_y = padding
    line_spacing = 2
    for i in range(0, len(moves_list), moves_row):
        text = ""
        for j in range(moves_row):
            if i + j < len(moves_list):
                text += moves_list[i + j]
        text_object = move_log_font.render(text, True, p.Color("Black"))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def draw_pieces(screen, board):
    '''Draws the pieces on the screen. One on each rectangle.
    '''

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animate_move(move, screen, board, clock):
    '''Animates the moves.
    '''

    global colors
    dr = move.target_row - move.start_row
    dc = move.target_col - move.start_col
    fps = 5
    frame_count = (abs(dr) + abs(dc)) * fps
    for frame in range(frame_count + 1):
        r, c = (move.start_row + dr * frame/frame_count,
                move.start_col + dc * frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.target_row + move.target_col) % 2]
        target_square = p.Rect(move.target_col * SQ_SIZE,
                               move.target_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, target_square)
        if move.piece_captured != "--":
            if move.is_ep:
                ep_row = move.target_row + \
                    1 if move.piece_captured[0] == "b" else move.target_row - 1
                target_square = p.Rect(
                    move.target_col * SQ_SIZE, ep_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], target_square)
        if move.piece_moved != "--":
            screen.blit(IMAGES[move.piece_moved], p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_text(screen, text):
    '''Draws text on the scren
    '''

    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color("Black"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH/2 - text_object.get_width()/2, BOARD_HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location.move(2, 2))


class Input():
    '''Handles user input.
    '''

    def __init__(self, x, y, w, h, text=""):
        # Used to draw input boxes.
        self.rect = p.Rect(x, y, w, h)

        # Color when input box is inactive.
        self.color_inactive = p.Color("#e6ffff")

        # Color when it's active.
        self.color_active = p.Color("#ccf5ff")

        # Sets input boxes' font.
        self.input_font = p.font.SysFont("Helvitca", 26, True, False)

        # Sets color to inactive initially.
        self.color = self.color_inactive
        
        # Renders surface
        self.txt_surface = self.input_font.render(text, True, self.color)
        
        self.text = text
        self.active = False
        self.input_list = []

    def click_input_box(self, e):
        '''Handles the player's clicks on the input boxes.
        '''
        
        if self.rect.collidepoint(e.pos):
            self.active = not self.active
        else:
            self.active = False
        self.color = self.color_active if self.active else self.color_inactive

    def type_input_box(self, e):
        '''Handles player's typing on the input boxes.
        '''
        
        if self.active:
            if e.key == p.K_RETURN:
                self.input_list.append(self.text)
                self.text = ''
            elif e.key == p.K_BACKSPACE:
                self.text = self.text[:-1]
            elif e.key == p.K_v:
                self.text = pyperclip.paste()
            else:
                self.text += e.unicode
            self.txt_surface = self.input_font.render(self.text, True, "black")

    def update(self):
        '''Updates input boxes.
        '''
        
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        '''Draws input boxes.
        '''
        
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        p.draw.rect(screen, self.color, self.rect, 2)

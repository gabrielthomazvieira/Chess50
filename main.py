'''This is the main file. It initialises pygame and runs the code.
'''

import pygame as p
from cs50 import SQL
from gamestate import *
from chessboard import *
from fen_parser import *
from fen_writer import fen_generator
from engine import *
from chessboard import *
from pgnparser import *
import random
import sys


def main():
    # Initialises pygame
    p.init()

    # Initialises database containing chess games.
    db = SQL("sqlite:///games.db")

    # Initialises a screen for display.
    screen = p.display.set_mode(
        (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))

    # Starts a clock object to help control framerate.
    clock = p.time.Clock()

    # Fills the screen with white
    screen.fill(p.Color("white"))

    # Assigns GameState() to gs and gets all valid moves.
    gs = GameState()
    valid_moves = gs.get_valid_moves()

    # Checks if a move was made.
    move_made = False

    # Looks for animations.
    animate = False

    # Loads any images.
    load_images()

    # Tuple containing squares selected by the player.
    sq_selected = ()

    # List containing the player's clicks.
    player_clicks = []

    # Used for checkmate and stalemate later.
    game_over = False

    # Used to draw engine evaluation.
    eng_eval = False

    # Keep track of important information for writing FEN.
    captures, halfmove_clock, pgn_index, castle_counter, fullmove_number = 0, 0, 0, 1, 1

    # Input boxes. The first is used for SQL queries, the second, for FEN.
    input_box1 = Input(535, 400, 140, 32)
    input_box2 = Input(535, 450, 140, 32)
    input_boxes = [input_box1, input_box2]

    # Stores PGN moves
    pgn_moves = []

    # Error messages
    search_error, eng_error, eval_error, fen_error = False, False, False, False

    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    '''Looks for player clicks and makes the move, if valid.
                    '''

                    # Checks if the user clicked on the input boxes.
                    for box in input_boxes:
                        box.click_input_box(e)

                    # Get mouse location
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    # Check for any player clicks.
                    if sq_selected == (row, col) or col >= 8:
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)

                    # If player clicks twice
                    if len(player_clicks) == 2:

                        # Passes these clicks to Move class
                        move = Move(player_clicks[0], player_clicks[1], gs.board)

                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:  # If move is valid:

                                # Makes the move.
                                gs.make_move(valid_moves[i])

                                # Gets en passant target square for FEN record.
                                fen_ep = move.convert(
                                    move.start_row, move.start_col)

                                # Counts the number of empty squares on the board.
                                empty = sum(row.count('--') for row in gs.board)

                                # Looks for captures and resets the halfmove clock.
                                if empty > 32 + captures:
                                    captures += 1
                                    halfmove_clock = 0

                                # Resets halfmove clock if the piece moved was a pawn.
                                if move.piece_moved[1] == "P":
                                    halfmove_clock = 0

                                # Increments 1 to fullmove number.
                                if gs.w_to_move:
                                    fullmove_number += 1

                                # Generates a FEN from the current position.
                                fen = fen_generator(gs.board, gs.w_to_move, gs.castling_rights_log[castle_counter].wks, gs.castling_rights_log[castle_counter].wqs,
                                                    gs.castling_rights_log[castle_counter].bks, gs.castling_rights_log[
                                                        castle_counter].bqs, move.piece_moved,
                                                    move.start_row, move.target_row, fen_ep[0], halfmove_clock, fullmove_number)

                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []

                        if not move_made:
                            player_clicks = [sq_selected]

                    # Closes engine evaluation when player clicks on the screen.
                    eng_eval = False

            elif e.type == p.KEYDOWN:

                # Checks if the player typed in the input boxes.
                for box in input_boxes:
                    box.type_input_box(e)

                if e.key == p.K_RETURN and p.key.get_mods() & p.KMOD_SHIFT:  # SHIFT + RETURN
                    '''Reads FEN string and sets up the board.
                    '''

                    # Gets the last input on the 2nd input box.
                    last_input = input_box2.input_list[-1]

                    try:
                        # Reads last input.
                        fp = FenParser(last_input)

                    except:
                        fen_error = True

                    else:
                        # Gets values in FEN's fields and assigns them to variables.
                        castle_counter, halfmove_clock, fullmove_number, turn, fen_castle = 1, fp.halfmove_clock(
                        ), fp.fullmove_number(), fp.turn(), fp.castle()

                        # Sets up the board.
                        gs.board = fp.parse()

                        # Sums up empty squares on the board and looks for captures.
                        empty = sum(row.count('--') for row in gs.board)
                        captures = empty - 32

                        # Handles castling rights and appends them to the castling rights log.
                        gs.w_to_move = True if turn == "w" else False
                        wks = True if "K" in fen_castle else False
                        bks = True if "k" in fen_castle else False
                        wqs = True if "Q" in fen_castle else False
                        bqs = True if "q" in fen_castle else False
                        gs.current_castling_rights = CastleRights(
                            wks, bks, wqs, bqs)
                        gs.castling_rights_log.append(CastleRights(gs.current_castling_rights.wks, gs.current_castling_rights.bks,
                                                                   gs.current_castling_rights.wqs, gs.current_castling_rights.bqs))

                        # Sets FEN in the clipboard to the current FEN.
                        fen = pyperclip.paste()

                        move_made = True

                elif e.key == p.K_RETURN:
                    '''Reads PGN notation from SQL database.
                    Player only needs to type the value he's looking for.
                    (E. g. opening = "Sicilian" or round = 6)
                    '''

                    # Gets the last input on the 1st input box.
                    last_input = input_box1.input_list[-1]

                    try:
                        # Runs SQL SELECT query from player's input and selects the game's PGN.
                        query = db.execute(
                            "SELECT pgn FROM games WHERE " + last_input + ";")[0]["pgn"]
                    except RuntimeError:
                        search_error = True
                    else:
                        # Reads query's PGN, gets all valid moves, and resets variables.
                        pgn_moves = pgn_parser(query)
                        gs = GameState()
                        valid_moves = gs.get_valid_moves()
                        sq_selected = ()
                        player_clicks = []
                        move_made = False
                        animate = False
                        captures, halfmove_clock, pgn_index, castle_counter, fullmove_number = 0, 0, 0, 1, 1
                elif e.key == p.K_r:
                    '''Resets all variables.
                    '''
                    
                    gs = GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    captures, halfmove_clock, pgn_index, castle_counter, fullmove_number = 0, 0, 0, 1, 1
                    game_over = False
                    search_error, eng_error, eval_error, eng_eval = False, False, False, False
                    query = None
                elif e.key == p.K_1 and p.key.get_mods() & p.KMOD_SHIFT:  # SHIFT + 1
                    '''Looks for best moves in the position with a low-depth engine.
                    '''
                    try:
                        # Analyzes the position in low depth and time limit.
                        eng_evaluation = analyze_position(
                            fen, num_moves_to_return=3, depth_limit=3, time_limit=1)
                    except UnboundLocalError:
                        eng_error = True
                    else:
                        # To avoid playing the same moves all the time, checks if the best moves are
                        # similar in evaluation and picks one randomly. Also plays any moves that
                        # lead to mate instantly.
                        if eng_evaluation[0]["mate_score"] != None:
                            eng_line = eng_evaluation[0]
                        elif abs(eng_evaluation[2]["centipawn_score"] - eng_evaluation[0]["centipawn_score"]) < 25:
                            eng_line = eng_evaluation[random.randint(0, 2)]
                        elif abs(eng_evaluation[1]["centipawn_score"] - eng_evaluation[0]["centipawn_score"]) < 25:
                            eng_line = eng_evaluation[random.randint(0, 1)]
                        else:
                            eng_line = eng_evaluation[0]
                        eng_interpret = eng_interpreter(eng_line)

                        # Makes the engine's move.
                        move = Move(eng_interpret[0],eng_interpret[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                fen_ep = move.convert(
                                    move.start_row, move.start_col)
                                empty = sum(row.count('--')
                                            for row in gs.board)
                                if empty > 32 + captures:
                                    captures += 1
                                    halfmove_clock = 0
                                if move.piece_moved[1] == "P":
                                    halfmove_clock = 0
                                if gs.w_to_move:
                                    fullmove_number += 1
                                if len(gs.move_log) != 0:
                                    fen = fen_generator(gs.board, gs.w_to_move, gs.castling_rights_log[castle_counter].wks, gs.castling_rights_log[castle_counter].wqs,
                                                        gs.castling_rights_log[castle_counter].bks, gs.castling_rights_log[
                                                            castle_counter].bqs, move.piece_moved,
                                                        move.start_row, move.target_row, fen_ep[0], halfmove_clock, fullmove_number)
                                move_made = True
                                animate = True
                elif e.key == p.K_2 and p.key.get_mods() & p.KMOD_SHIFT:
                    '''Looks for best moves in the position with a mid-depth engine.
                    '''
                    try:
                        # Analyzes the position in mid depth and time limit.
                        eng_evaluation = analyze_position(
                            fen, num_moves_to_return=3, depth_limit=10, time_limit=3)
                    except UnboundLocalError:
                        eng_error = True
                    else:
                        # To avoid playing the same moves all the time, checks if the best moves are
                        # similar in evaluation and picks one randomly. Also plays any moves that
                        # lead to mate instantly.
                        if eng_evaluation[0]["mate_score"] != None:
                            eng_line = eng_evaluation[0]
                        elif abs(eng_evaluation[2]["centipawn_score"] - eng_evaluation[0]["centipawn_score"]) < 25:
                            eng_line = eng_evaluation[random.randint(0, 2)]
                        elif abs(eng_evaluation[1]["centipawn_score"] - eng_evaluation[0]["centipawn_score"]) < 25:
                            eng_line = eng_evaluation[random.randint(0, 1)]
                        else:
                            eng_line = eng_evaluation[0]

                        # Makes the engine's move.
                        move = Move(eng_interpret[0], eng_interpret[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                fen_ep = move.convert(
                                    move.start_row, move.start_col)
                                empty = sum(row.count('--')
                                            for row in gs.board)
                                if empty > 32 + captures:
                                    captures += 1
                                    halfmove_clock = 0
                                if move.piece_moved[1] == "P":
                                    halfmove_clock = 0
                                if gs.w_to_move:
                                    fullmove_number += 1
                                if len(gs.move_log) != 0:
                                    fen = fen_generator(gs.board, gs.w_to_move, gs.castling_rights_log[castle_counter].wks, gs.castling_rights_log[castle_counter].wqs,
                                                        gs.castling_rights_log[castle_counter].bks, gs.castling_rights_log[
                                                            castle_counter].bqs, move.piece_moved,
                                                        move.start_row, move.target_row, fen_ep[0], halfmove_clock, fullmove_number)
                                move_made = True
                                animate = True
                elif e.key == p.K_3 and p.key.get_mods() & p.KMOD_SHIFT:
                    '''Looks for best moves in the position with a high-depth engine.
                    '''
                    try:
                        # Analyzes the position in low depth and time limit.
                        eng_evaluation = analyze_position(
                            fen, num_moves_to_return=3, depth_limit=22, time_limit=10)
                    except UnboundLocalError:
                        eng_error = True
                    else:
                        # To avoid playing the same moves all the time, checks if the best moves are
                        # similar in evaluation and picks one randomly. Also plays any moves that
                        # lead to mate instantly.
                        if eng_evaluation[0]["mate_score"] != None:
                            eng_line = eng_evaluation[0]
                        elif abs(eng_evaluation[2]["centipawn_score"] - eng_evaluation[0]["centipawn_score"]) < 25:
                            eng_line = eng_evaluation[random.randint(0, 2)]
                        elif abs(eng_evaluation[1]["centipawn_score"] - eng_evaluation[0]["centipawn_score"]) < 25:
                            eng_line = eng_evaluation[random.randint(0, 1)]
                        else:
                            eng_line = eng_evaluation[0]
                        eng_interpret = eng_interpreter(eng_line)

                        # Makes the engine's move.
                        move = Move(eng_interpret[0], eng_interpret[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                fen_ep = move.convert(
                                    move.start_row, move.start_col)
                                empty = sum(row.count('--')
                                            for row in gs.board)
                                if empty > 32 + captures:
                                    captures += 1
                                    halfmove_clock = 0
                                if move.piece_moved[1] == "P":
                                    halfmove_clock = 0
                                if gs.w_to_move:
                                    fullmove_number += 1
                                if len(gs.move_log) != 0:
                                    fen = fen_generator(gs.board, gs.w_to_move, gs.castling_rights_log[castle_counter].wks, gs.castling_rights_log[castle_counter].wqs,
                                                        gs.castling_rights_log[castle_counter].bks, gs.castling_rights_log[
                                                            castle_counter].bqs, move.piece_moved,
                                                        move.start_row, move.target_row, fen_ep[0], halfmove_clock, fullmove_number)
                                move_made = True
                                animate = True
                elif e.key == p.K_4 and p.key.get_mods() & p.KMOD_SHIFT:
                    '''Evaluates the position on the board with a mid depth engine.
                    '''
                    try:
                        eng_evaluation = analyze_position(
                            fen, num_moves_to_return=1, depth_limit=22, time_limit=5)
                    except UnboundLocalError:
                        eval_error = True
                    else:
                        if eng_evaluation[0]["mate_score"] != None and gs.w_to_move:
                            score = "White has mate in " + \
                                str(eng_evaluation[0]["mate_score"] +
                                    " (" + str(eng_evaluation[0]["pv"][0]) + ")")
                        elif eng_evaluation[0]["mate_score"] != None and not gs.w_to_move:
                            score = "Black has mate in " + \
                                str(eng_evaluation[0]["mate_score"]) + \
                                " (" + str(eng_evaluation[0]["pv"][0]) + ")"
                        else:
                            score = str(eng_evaluation[0]["centipawn_score"]) + \
                                " centipawns (" + \
                                str(eng_evaluation[0]["pv"][0]) + ")"
                        eng_eval = True
                elif e.key == p.K_5 and p.key.get_mods() & p.KMOD_SHIFT:
                    '''Evaluates the position on the board with a high depth engine.
                    '''
                    try:
                        eng_evaluation = analyze_position(
                            fen, num_moves_to_return=1, depth_limit=22, time_limit=10)
                    except UnboundLocalError:
                        eval_error = True
                    else:
                        if eng_evaluation[0]["mate_score"] != None and gs.w_to_move:
                            score = "White has mate in " + \
                                str(eng_evaluation[0]["mate_score"] +
                                    " (" + str(eng_evaluation[0]["pv"][0]) + ")")
                        elif eng_evaluation[0]["mate_score"] != None and not gs.w_to_move:
                            score = "Black has mate in " + \
                                str(eng_evaluation[0]["mate_score"]) + \
                                " (" + str(eng_evaluation[0]["pv"][0]) + ")"
                        else:
                            score = str(eng_evaluation[0]["centipawn_score"]) + \
                                " centipawns (" + \
                                str(eng_evaluation[0]["pv"][0]) + ")"
                        eng_eval = True
                elif e.key == p.K_RIGHT:
                    '''Iterates through PGN string and makes the moves.
                    '''
                    if len(input_box1.input_list) != 0:
                        pgn_move = pgn_interpreter(pgn_moves, pgn_index)
                        pgn_index += 1
                        move = Move(pgn_move[0], pgn_move[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                fen_ep = move.convert(
                                    move.start_row, move.start_col)
                                empty = sum(row.count('--')
                                            for row in gs.board)
                                if empty > 32 + captures:
                                    captures += 1
                                    halfmove_clock = 0
                                if move.piece_moved[1] == "P":
                                    halfmove_clock = 0
                                if gs.w_to_move:
                                    fullmove_number += 1
                                if len(gs.move_log) != 0:
                                    fen = fen_generator(gs.board, gs.w_to_move, gs.castling_rights_log[castle_counter].wks, gs.castling_rights_log[castle_counter].wqs,
                                                        gs.castling_rights_log[castle_counter].bks, gs.castling_rights_log[
                                                            castle_counter].bqs, move.piece_moved,
                                                        move.start_row, move.target_row, fen_ep[0], halfmove_clock, fullmove_number)
                                move_made = True
                                animate = True
                                eng_eval = False
        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            castle_counter += 1
            halfmove_clock += 1
        for box in input_boxes:
            box.update()
        draw_game_state(screen, gs, valid_moves, sq_selected)
        for box in input_boxes:
            box.draw(screen)

        # Draws checkmate, stalemate and error functions on the screen.
        if gs.checkmate or gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate (press r)" if gs.stalemate else "Black wins by checkmate (press r)" if gs.w_to_move else "White wins by checkmate (press r)")
        elif search_error:
            draw_text(screen, "Sorry, can't find your search :(  (press r)")
        elif eng_error:
            draw_text(screen, "Please, play a move (press r)")
        elif eval_error:
            draw_text(screen, "Please, play a move (press r)")
        elif fen_error:
            draw_text(screen, "Please, provide a valid fen")
        elif eng_eval:
            draw_text(screen, score)

        # Sets FPS
        clock.tick(MAX_FPS)

        p.display.flip()


if __name__ == "__main__":
    main()

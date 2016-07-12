import chess
import random
import tweepy
import pickle
import logging
from logging.handlers import RotatingFileHandler
from local_settings import cKey, cKeySecret, aToken, aTokenSecret

logging.basicConfig(filename='metrics.log',
                    level=logging.INFO,
                    format='%(levelname)s %(asctime)s - %(message)s')

def get_random_move(board):
    legal_moves = [move for move in board.legal_moves]
    return random.choice(legal_moves)


def game_alive(board):
    return not any([board.is_stalemate(),
                    board.is_game_over(),
                    board.is_fivefold_repetition(),
                    board.is_seventyfive_moves(),
                    board.is_checkmate()])


def checkmate_gen():
    generated_games = 0
    while True:
        generated_games += 1
        board = chess.Board()
        while game_alive(board):
            board.push(get_random_move(board))

        if board.is_checkmate():
            if add_to_history(board):
                logging.info("{} games generated".format(generated_games))
                return board


def add_to_history(board):
    """
    Returns False if board has already been posted
    Otherwise adds to history and returns True
    """
    fen = board.fen().split()[0]
    try:
        with open('previous_boards.p', 'rb') as record:
            board_history = pickle.load(record)
    except IOError:  # file does not exist, create new list
        board_history = []

    if fen not in board_history:
        board_history.append(fen)
        with open('previous_boards.p', 'wb') as record:
            pickle.dump(board_history, record)

        return True
    else:
        logging.warn("collision for {}".format())
        return False


def convert_board_to_utf(board):
    WHITE_TILE = u'+'
    BLACK_TILE = u'_'
    unicode_chess_translate_table = str.maketrans(
            u"KQRBNPkqrbnp",
            u"\u2654\u2655\u2656\u2657\u2658\u2659\u265A\u265B\u265C\u265D\u265E\u265F",
            )

    checkmate_utf_list = str(board).translate(unicode_chess_translate_table).split()

    checkmate_utf_list_with_tiles = []

    def _get_tile_for_count(count):
        """
        even tile on even row: white
        even tile on odd row: black
        odd tile on even row: black
        odd tile on odd row: white
        """

        even_tile = count % 2 == 0
        even_row  = int(count / 8) % 2 == 0
        if (even_tile and even_row) or not (even_tile or even_row):
            return WHITE_TILE
        else:
            return BLACK_TILE

    for count, character in enumerate(checkmate_utf_list):
        if character == '.':
            checkmate_utf_list_with_tiles.append(_get_tile_for_count(count))

        else:
            checkmate_utf_list_with_tiles.append(character)

        end_of_line = ((count + 1) % 8) == 0
        if end_of_line:
            checkmate_utf_list_with_tiles.append('\n')

    if checkmate_utf_list_with_tiles[-1] == '\n':
        checkmate_utf_list_with_tiles.pop()


    return "".join(checkmate_utf_list_with_tiles)


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(cKey, cKeySecret)
    auth.set_access_token(aToken, aTokenSecret)
    api = tweepy.API(auth)

    checkmateObj = checkmate_gen()
    tweet_body = convert_board_to_utf(checkmateObj)
    print(tweet_body)
    #api.update_status(tweet_body)

import chess
import random
import tweepy
import pickle
from local_settings import cKey, cKeySecret, aToken, aTokenSecret


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
    while True:
        board = chess.Board()
        while game_alive(board):
            board.push(get_random_move(board))

        if board.is_checkmate():
            if add_to_history(board):
                return board


def add_to_history(board):
    """
    Returns False if board has already been posted
    Otherwise adds to history and returns True
    """
    try:
        with open('previous_boards.p', 'rb') as record:
            board_history = pickle.load(record)
    except IOError:  # file does not exist, create new list
        board_history = []

    if board not in board_history:
        board_history.append(board)
        with open('previous_boards.p', 'wb') as record:
            pickle.dump(board_history, record)

        return True
    else:
        return False


def convert_board_to_utf(board):
    WHITE_TILE = u'\u2003'
    BLACK_TILE = u'\u274E'
    unicode_chess_translate_table = str.maketrans(
            u"KQRBNPkqrbnp",
            u"\u2654\u2655\u2656\u2657\u2658\u2659\u265A\u265B\u265C\u265D\u265E\u265F",
            )

    checkmate_utf_list = list(str(board).translate(unicode_chess_translate_table))

    for x, y in enumerate(checkmate_utf_list):
        if checkmate_utf_list[x] == '.':
            if x % 2 == 0:
                checkmate_utf_list[x] = WHITE_TILE
            else:
                checkmate_utf_list[x] = BLACK_TILE

    return "".join(checkmate_utf_list)


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(cKey, cKeySecret)
    auth.set_access_token(aToken, aTokenSecret)
    api = tweepy.API(auth)

    checkmateObj = checkmate_gen()
    fen = checkmateObj.fen().split()[0]
    tweet_body = "{board}\n{fen}".format(board=convert_board_to_utf(checkmateObj),
                                         fen=fen)
    api.update_status(tweet_body)

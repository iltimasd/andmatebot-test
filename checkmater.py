import chess
import string
import random
import tweepy
import mmap
from local_settings import cKey, cKeySecret, aToken, aTokenSecret


auth = tweepy.OAuthHandler(cKey, cKeySecret)
auth.set_access_token(aToken, aTokenSecret)

api = tweepy.API(auth)


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
            record = open('records.txt', 'a+')
            oldgoal = str(board.fen())
            goal = oldgoal[:oldgoal.find(' ')]
            s = mmap.mmap(record.fileno(), 0, access=mmap.ACCESS_READ)
            if s.find(goal) != -1:
                checkmate_gen()
            else:
                record.write(goal + '\n')
                record.close()
                return board


if __name__ == '__main__':
    checkmateObj = checkmate_gen()
    fen = str(checkmateObj.fen())
    checkmateUTF = str(checkmateObj).translate(None, ''.join(' ')).encode('utf-8', 'strict')
    checkmateUTF = checkmateUTF.replace(u'K', u'\u2654')
    checkmateUTF = checkmateUTF.replace(u'Q', u'\u2655')
    checkmateUTF = checkmateUTF.replace(u'R', u'\u2656')
    checkmateUTF = checkmateUTF.replace(u'B', u'\u2657')
    checkmateUTF = checkmateUTF.replace(u'N', u'\u2658')
    checkmateUTF = checkmateUTF.replace(u'P', u'\u2659')
    checkmateUTF = checkmateUTF.replace(u'k', u'\u265A')
    checkmateUTF = checkmateUTF.replace(u'q', u'\u265B')
    checkmateUTF = checkmateUTF.replace(u'r', u'\u265C')
    checkmateUTF = checkmateUTF.replace(u'b', u'\u265D')
    checkmateUTF = checkmateUTF.replace(u'n', u'\u265E')
    checkmateUTF = checkmateUTF.replace(u'p', u'\u265F')
    for x, y in enumerate(checkmateUTF):
        if checkmateUTF[x] == '.':
            if x % 2 == 0:
                checkmateUTF = checkmateUTF[:x]+u'\u2003'+checkmateUTF[x+1:]
            else:
                checkmateUTF = checkmateUTF[:x]+u'\u274E'+checkmateUTF[x+1:]
    print checkmateUTF+'\n'+fen[:fen.find(' ')]
    api.update_status(checkmateUTF+'\n'+fen[:fen.find(' ')])

    # unicode_checkmate = string.maketrans(
    #      u"KQRBNPkqrbnp"
    # translated = string.translate(checkmateUTF, unicode_checkmate)
    # print(translated)

from copy import deepcopy
from random import choice
from time import sleep, time

COLOR_MASK = 1 << 3     #색상을 나타내기 위해 사용 -> 비트 연산을 통해 색상을 설정
WHITE = 0 << 3
BLACK = 1 << 3

ENDGAME_PIECE_COUNT = 7

PIECE_MASK = 0b111      #말의 타입을 나타내기 위해 사용
EMPTY  = 0              #각 말의 타입을 상수를 정의
PAWN   = 1
KNIGHT = 2
BISHOP = 3
ROOK   = 4
QUEEN  = 5
KING   = 6
JOKER  = 7

#말의 종류를 리스트로 나열
PIECE_TYPES = [ PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, JOKER ]
#각 말의 가치를 딕셔너리로 정의
PIECE_VALUES = { EMPTY:0, PAWN:100, KNIGHT:300, BISHOP:300, ROOK:500, QUEEN:900, JOKER:1300, KING:42000 }

FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']    #체스 보드의 열을 나타내는 리스트
RANKS = ['1', '2', '3', '4', '5', '6', '7', '8']    #체스 보드의 행을 나태내는 리스트

#백색과 흑색의 킹사이드 및 퀸사이드 캐슬링 권리를 비트로 정의
CASTLE_KINGSIDE_WHITE  = 0b1 << 0
CASTLE_QUEENSIDE_WHITE = 0b1 << 1
CASTLE_KINGSIDE_BLACK  = 0b1 << 2
CASTLE_QUEENSIDE_BLACK = 0b1 << 3
#모든 캐슬링 권리를 하나로 합친 것
FULL_CASTLING_RIGHTS = CASTLE_KINGSIDE_WHITE|CASTLE_QUEENSIDE_WHITE|CASTLE_KINGSIDE_BLACK|CASTLE_QUEENSIDE_BLACK

ALL_SQUARES    = 0xFFFFFFFFFFFFFFFF     #체스 보드의 모든 칸을 비트로 표현한 것
FILE_A         = 0x0101010101010101     #각각의 파일을 비트보드로 표현한 것
FILE_B         = 0x0202020202020202
FILE_C         = 0x0404040404040404
FILE_D         = 0x0808080808080808
FILE_E         = 0x1010101010101010
FILE_F         = 0x2020202020202020
FILE_G         = 0x4040404040404040
FILE_H         = 0x8080808080808080
RANK_1         = 0x00000000000000FF     #각각의 랭크를 비트보드로 표현한 것
RANK_2         = 0x000000000000FF00
RANK_3         = 0x0000000000FF0000
RANK_4         = 0x00000000FF000000
RANK_5         = 0x000000FF00000000
RANK_6         = 0x0000FF0000000000
RANK_7         = 0x00FF000000000000
RANK_8         = 0xFF00000000000000
DIAG_A1H8      = 0x8040201008040201     #A1에서 H8로 가는 대각선을 비트보드로 표현한 것
ANTI_DIAG_H1A8 = 0x0102040810204080     #H1에서 A8로 가는 반대 대각선을 비트보드로 표현한 것
LIGHT_SQUARES  = 0x55AA55AA55AA55AA     #밝은 색 칸들을 비트보드로 표현한 것
DARK_SQUARES   = 0xAA55AA55AA55AA55     #어두운 색 칸들을 비트보드로 표현한 것

FILE_MASKS = [FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H]   #파일을 비트보드로 표현한 리스트
RANK_MASKS = [RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8]   #랭크를 비트보드로 표현한 리스트
#체스 보드의 초기 상태를 나타내는 리스트. 각 요소는 특정 위치에 있는 체스말을 나타냄
INITIAL_BOARD = [ WHITE|ROOK, WHITE|KNIGHT, WHITE|BISHOP, WHITE|QUEEN, WHITE|KING, WHITE|BISHOP, WHITE|KNIGHT, WHITE|ROOK,
                  WHITE|PAWN, WHITE|PAWN,   WHITE|PAWN,   WHITE|PAWN,  WHITE|PAWN, WHITE|PAWN,   WHITE|PAWN,   WHITE|PAWN, 
                  EMPTY,      EMPTY,        EMPTY,        EMPTY,       EMPTY,      EMPTY,        EMPTY,        EMPTY,
                  EMPTY,      EMPTY,        EMPTY,        EMPTY,       EMPTY,      EMPTY,        EMPTY,        EMPTY,
                  EMPTY,      EMPTY,        EMPTY,        EMPTY,       EMPTY,      EMPTY,        EMPTY,        EMPTY,
                  EMPTY,      EMPTY,        EMPTY,        EMPTY,       EMPTY,      EMPTY,        EMPTY,        EMPTY,
                  BLACK|PAWN, BLACK|PAWN,   BLACK|PAWN,   BLACK|PAWN,  BLACK|PAWN, BLACK|PAWN,   BLACK|PAWN,   BLACK|PAWN,
                  BLACK|ROOK, BLACK|KNIGHT, BLACK|BISHOP, BLACK|QUEEN, BLACK|KING, BLACK|BISHOP, BLACK|KNIGHT, BLACK|ROOK ]
#빈 체스 보드를 나타내는 리스트
EMPTY_BOARD = [ EMPTY for _ in range(64) ]
#체스 게임의 초기 상태를 나타내는 FEN 문자열
INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
'''
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR: 각 랭크의 체스말을 나타내며, 소문자는 흑색의 체스말, 대문자는 백색의 체스말을 나타냄
w: 백색이 먼저 두는 것을 나타냅니다.
KQkq: 백색과 흑색의 캐슬링 권리를 나타냄
-: 앙파상 가능 여부를 나타냄
0: 반수(체스 경기에서의 수)를 나타냄
1: 전체 턴 수를 나타냄
'''
#특정 테스 보드 상태를 나타내는 FEN 문자열
STROKES_YOLO = '1k6/2b1p3/Qp4N1/4r2P/2B2q2/1R6/2Pn2K1/8 w - - 0 1'
#각 체스말과 그에 대응하는 기호를 매핑하는 딕셔너리
PIECE_CODES = { WHITE|KING:  'K',
                WHITE|QUEEN: 'Q',
                WHITE|ROOK:  'R',
                WHITE|BISHOP:'B',
                WHITE|KNIGHT:'N',
                WHITE|PAWN:  'P',
                WHITE|JOKER: 'J',
                BLACK|KING:  'k',
                BLACK|QUEEN: 'q',
                BLACK|ROOK:  'r',
                BLACK|BISHOP:'b',
                BLACK|KNIGHT:'n',
                BLACK|PAWN:  'p',
                BLACK|JOKER: 'j',
                EMPTY:       '.' }
#각 체스말 기호와 그에 대응하는 체스말 상수를 매핑하여, 역방향 조회가 가능하도록 함
PIECE_CODES.update({v: k for k, v in PIECE_CODES.items()})

DOUBLED_PAWN_PENALTY      = 10      #이중 폰에 대한 패널티
ISOLATED_PAWN_PENALTY     = 20      #고립된 폰에 대한 패널티
BACKWARDS_PAWN_PENALTY    = 8       #후방 폰에 대한 패널티
PASSED_PAWN_BONUS         = 20      #통과 폰에 대한 보너스
ROOK_SEMI_OPEN_FILE_BONUS = 10      #반열림 파일에 있는 룩에 대한 보너스
ROOK_OPEN_FILE_BONUS      = 15      #열림 파일에 있는 룩에 대한 보너스
ROOK_ON_SEVENTH_BONUS     = 20      #7번째 랭크에 있는 룩에 대한 보너스
#폰이 전진할수록 보너스 점수가 높아짐. 중간 열에 있는 폰은 약간의 패널티
PAWN_BONUS = [0,   0,   0,   0,   0,   0,   0,   0,
              0,   0,   0, -40, -40,   0,   0,   0,
              1,   2,   3, -10, -10,   3,   2,   1,
              2,   4,   6,   8,   8,   6,   4,   2,
              3,   6,   9,  12,  12,   9,   6,   3,
              4,   8,  12,  16,  16,  12,   8,   4,
              5,  10,  15,  20,  20,  15,  10,   5,
              0,   0,   0,   0,   0,   0,   0,   0]
#나이트가 보드 중앙에 있을 때 보너스가 가장 높음, 가장자리에 있을 때 패널티 
KNIGHT_BONUS = [-10, -30, -10, -10, -10, -10, -30, -10,
                -10,   0,   0,   0,   0,   0,   0, -10,
                -10,   0,   5,   5,   5,   5,   0, -10,
                -10,   0,   5,  10,  10,   5,   0, -10,
                -10,   0,   5,  10,  10,   5,   0, -10,
                -10,   0,   5,   5,   5,   5,   0, -10,
                -10,   0,   0,   0,   0,   0,   0, -10,
                -10, -10, -10, -10, -10, -10, -10, -10]
#비숍이 보드 중앙에 있을 경우 보너스 높음, 가장자리에 있을 때 패널티
BISHOP_BONUS = [-10, -10, -20, -10, -10, -20, -10, -10,
                -10,   0,   0,   0,   0,   0,   0, -10,
                -10,   0,   5,   5,   5,   5,   0, -10,
                -10,   0,   5,  10,  10,   5,   0, -10,
                -10,   0,   5,  10,  10,   5,   0, -10,
                -10,   0,   5,   5,   5,   5,   0, -10,
                -10,   0,   0,   0,   0,   0,   0, -10,
                -10, -10, -10, -10, -10, -10, -10, -10]
#킹이 초기 위치 근처에 있을때 가장 보너스 높음, 중앙에 있을 경우 페널티. 게임 초반의 킹 안장성을 반영
KING_BONUS = [  0,  20,  40, -20,   0, -20,  40,  20,
              -20, -20, -20, -20, -20, -20, -20, -20,
              -40, -40, -40, -40, -40, -40, -40, -40,
              -40, -40, -40, -40, -40, -40, -40, -40,
              -40, -40, -40, -40, -40, -40, -40, -40,
              -40, -40, -40, -40, -40, -40, -40, -40,
              -40, -40, -40, -40, -40, -40, -40, -40,
              -40, -40, -40, -40, -40, -40, -40, -40]
#앤드게임에서 킹의 위치에 따라 보너스 적용. 킹이 중앙에 있을 경우 보너스가 높음 이는 킹의 활동성을 반영
KING_ENDGAME_BONUS = [ 0,  10,  20,  30,  30,  20,  10,   0,
                      10,  20,  30,  40,  40,  30,  20,  10,
                      20,  30,  40,  50,  50,  40,  30,  20,
                      30,  40,  50,  60,  60,  50,  40,  30,
                      30,  40,  50,  60,  60,  50,  40,  30,
                      20,  30,  40,  50,  50,  40,  30,  20,
                      10,  20,  30,  40,  40,  30,  20,  10,
                       0,  10,  20,  30,  30,  20,  10,   0]
#디버그 모드 설정 -> True 로 설정하면 추가적인 디버그 정보를 출력 가능
verbose = False

# ========== CHESS GAME ==========

class Game:
    def __init__(self, FEN=''):     #체스 게임 초기 상태 설정
        self.board = INITIAL_BOARD  #체스 보드를 초기 상태로 설정
        self.to_move = WHITE        #다음 수를 둘 플레이어를 백색으로 설정
        self.ep_square = 0          #앙팡상 가능한 위치를 초기화
        self.castling_rights = FULL_CASTLING_RIGHTS     #캐슬링 권리를 초기화
        self.halfmove_clock = 0     #반수 시계를 초기화
        self.fullmove_number = 1    #전체 천 수를 초기화
        
        self.position_history = []  #포지션 히스토리를 초기화하고, FEN 문자열이 제공되면 이를 로드
        if FEN != '':
            self.load_FEN(FEN)
            self.position_history.append(FEN)
        else:
            self.position_history.append(INITIAL_FEN)
            
        self.move_history = []      #이동 히스토리를 초기화
    #게임의 이동 히스토리를 문자열로 반환
    def get_move_list(self):
        return ' '.join(self.move_history)
    #현재 게임 상태를 FEN 문자열로 변환하여 반환
    def to_FEN(self):
        FEN_str = ''
        
        for i in range(len(RANKS)):
            first = len(self.board) - 8*(i+1)
            empty_sqrs = 0
            for fille in range(len(FILES)):
                piece = self.board[first+fille]
                if piece&PIECE_MASK == EMPTY:
                    empty_sqrs += 1
                else:
                    if empty_sqrs > 0:
                        FEN_str += '{}'.format(empty_sqrs)
                    FEN_str += '{}'.format(piece2str(piece))
                    empty_sqrs = 0
            if empty_sqrs > 0:
                FEN_str += '{}'.format(empty_sqrs)
            FEN_str += '/'
        FEN_str = FEN_str[:-1] + ' '
        
        if self.to_move == WHITE:
            FEN_str += 'w '
        if self.to_move == BLACK:
            FEN_str += 'b '
            
        if self.castling_rights & CASTLE_KINGSIDE_WHITE:
            FEN_str += 'K'
        if self.castling_rights & CASTLE_QUEENSIDE_WHITE:
            FEN_str += 'Q'
        if self.castling_rights & CASTLE_KINGSIDE_BLACK:
            FEN_str += 'k'
        if self.castling_rights & CASTLE_QUEENSIDE_BLACK:
            FEN_str += 'q'
        if self.castling_rights == 0:
            FEN_str += '-'
        FEN_str += ' '
            
        if self.ep_square == 0:
            FEN_str += '-'
        else:
            FEN_str += bb2str(self.ep_square)
        
        FEN_str += ' {}'.format(self.halfmove_clock)
        FEN_str += ' {}'.format(self.fullmove_number)
        return FEN_str
    
    def load_FEN(self, FEN_str):
        FEN_list = FEN_str.split(' ')       #FEN 문자열을 공백으로 구분하여 리스트로 만듬
        #보드 상태 설정
        board_str = FEN_list[0]
        rank_list = board_str.split('/')    #/로 구분하여 랭크 리스트로 만듬
        rank_list.reverse()         #리스트를 역순으로 변환하여 체스보드의 하단부터 설정
        self.board = []             #숫자는 빈칸을 의미, 문자는 체스말을 의미
        
        for rank in rank_list:
            rank_pieces = []
            for p in rank:
                if p.isdigit():
                    for _ in range(int(p)):
                        rank_pieces.append(EMPTY)
                else:
                    rank_pieces.append(str2piece(p))
            self.board.extend(rank_pieces)
        #다음 수를 둘 플레이어 설정
        to_move_str = FEN_list[1].lower()
        if to_move_str == 'w':
            self.to_move = WHITE
        if to_move_str == 'b':
            self.to_move = BLACK
        #캐슬링 권리 설정
        castling_rights_str = FEN_list[2]   #확인하여 캐슬링 권리를 설정
        self.castling_rights = 0
        if castling_rights_str.find('K') >= 0:
            self.castling_rights |= CASTLE_KINGSIDE_WHITE
        if castling_rights_str.find('Q') >= 0:
            self.castling_rights |= CASTLE_QUEENSIDE_WHITE
        if castling_rights_str.find('k') >= 0:
            self.castling_rights |= CASTLE_KINGSIDE_BLACK
        if castling_rights_str.find('q') >= 0:
            self.castling_rights |= CASTLE_QUEENSIDE_BLACK 
        #앙파상 가능한 위치 설정
        ep_str = FEN_list[3]
        if ep_str == '-':
            self.ep_square = 0
        else:
            self.ep_square = str2bb(ep_str)
        #반수 시계와 전체 턴 수 설정
        self.halfmove_clock = int(FEN_list[4])
        self.fullmove_number = int(FEN_list[5])

# ================================

#주어진 비토보드 위치에 있는 체스말을 반환
def get_piece(board, bitboard):
    return board[bb2index(bitboard)]
#주어진 비트보드의 1인 비트의 인덱스를 반환        
def bb2index(bitboard):
    for i in range(64):
        if bitboard & (0b1 << i):
            return i
#체스 보드 위치 문자열을 인덱스로 변환
def str2index(position_str):
    fille = FILES.index(position_str[0].lower())
    rank = RANKS.index(position_str[1])
    return 8*rank + fille
#비트보드 위치를 체스 보드 위치 문자열로 변환
def bb2str(bitboard):
    for i in range(64):
        if bitboard & (0b1 << i):
            fille = i%8
            rank = int(i/8)
            return '{}{}'.format(FILES[fille], RANKS[rank])
#체스 보드 위치 문자열을 비트보드로 변환
def str2bb(position_str):
    return 0b1 << str2index(position_str)
#이동을 문자열로 변환
def move2str(move):
    return bb2str(move[0]) + bb2str(move[1])
#비트보드에서 1인 비트 위치를 생성
def single_gen(bitboard):
    for i in range(64):
        bit = 0b1 << i
        if bitboard & bit:
            yield bit
#보드에서 특정 체스말의 위치를 생성
def piece_gen(board, piece_code):
    for i in range(64):
        if board[i]&PIECE_MASK == piece_code:
            yield 0b1 << i
#보드에서 특정 색상의 체스말 위치를 생성
def colored_piece_gen(board, piece_code, color):
    for i in range(64):
        if board[i] == piece_code|color:
            yield 0b1 << i
#상대방의 색상을 반환            
def opposing_color(color):
    if color == WHITE:
        return BLACK
    if color == BLACK:
        return WHITE
#체스말 코드를 문자열로 변환
def piece2str(piece):
    return PIECE_CODES[piece]
#체스말 문자열을 코드로 변환
def str2piece(string):
    return PIECE_CODES[string]
#체스 보드를 콘솔에 출력함    
def print_board(board):
    print('')
    for i in range(len(RANKS)):
        rank_str = str(8-i) + ' '
        first = len(board) - 8*(i+1)
        for fille in range(len(FILES)):
            rank_str += '{} '.format(piece2str(board[first+fille]))
        print(rank_str)
    print('  a b c d e f g h')
#회전된 체스보드를 콘솔에 출력
def print_rotated_board(board):
    r_board = rotate_board(board)
    print('')
    for i in range(len(RANKS)):
        rank_str = str(i+1) + ' '
        first = len(r_board) - 8*(i+1)
        for fille in range(len(FILES)):
            rank_str += '{} '.format(piece2str(r_board[first+fille]))
        print(rank_str)
    print('  h g f e d c b a')
#비트보드를 콘솔에 출력    
def print_bitboard(bitboard):
    print('')
    for rank in range(len(RANKS)):
        rank_str = str(8-rank) + ' '
        for fille in range(len(FILES)):
            if (bitboard >> (fille + (7-rank)*8)) & 0b1:
                rank_str += '# '
            else:
                rank_str += '. '
        print(rank_str)
    print('  a b c d e f g h')
#비트보드의 최하위 1인 비트를 반환함    
def lsb(bitboard):
    for i in range(64):
        bit = (0b1 << i) 
        if bit & bitboard:
            return bit
#비트보드의 최상위 1인 비트를 반환
def msb(bitboard):
    for i in range(64):
        bit = (0b1 << (63-i)) 
        if bit & bitboard:
            return bit
#주어진 색상의 체스말이 있는 위치를 비트보드로 반환
def get_colored_pieces(board, color):
    return list2int([ (i != EMPTY and i&COLOR_MASK == color) for i in board ])
#빈 칸의 위치를 비트보드로 반환
def empty_squares(board):
    return list2int([ i == EMPTY for i in board ])
#체스말이 있는 칸의 위치를 비트보드로 반환
def occupied_squares(board):
    return nnot(empty_squares(board))
#주어진 리스트를 비트보드로 변환
def list2int(lst):
    rev_list = lst[:]
    rev_list.reverse()
    return int('0b' + ''.join(['1' if i else '0' for i in rev_list]), 2)
#비트보드를 반전시켜 반환함
def nnot(bitboard):
    return ~bitboard & ALL_SQUARES
#체스 보드를 회전시킴
def rotate_board(board):
    rotated_board = deepcopy(board)
    rotated_board.reverse()
    return rotated_board
#체스 보드를 수직으로 뒤집음
def flip_board_v(board):
    flip = [56,  57,  58,  59,  60,  61,  62,  63,
            48,  49,  50,  51,  52,  53,  54,  55,
            40,  41,  42,  43,  44,  45,  46,  47,
            32,  33,  34,  35,  36,  37,  38,  39,
            24,  25,  26,  27,  28,  29,  30,  31,
            16,  17,  18,  19,  20,  21,  22,  23,
             8,   9,  10,  11,  12,  13,  14,  15,
             0,   1,   2,   3,   4,   5,   6,   7]
    
    return deepcopy([board[flip[i]] for i in range(64)])
#비트보드를 동쪽으로 한 칸 이동
def east_one(bitboard):
    return (bitboard << 1) & nnot(FILE_A)
#비트보드를 서쪽으로 한 칸 이동
def west_one(bitboard):
    return (bitboard >> 1) & nnot(FILE_H)
#비트보드를 북쪽으로 한 칸 이동
def north_one(bitboard):
    return (bitboard << 8) & nnot(RANK_1)
#비트보드를 남쪽으로 한 칸 이동
def south_one(bitboard):
    return (bitboard >> 8) & nnot(RANK_8)
#비트보드를 북동쪽으로 한 칸 이동
def NE_one(bitboard):
    return north_one(east_one(bitboard))
#비트보드를 북서쪽으로 한 칸 이동
def NW_one(bitboard):
    return north_one(west_one(bitboard))
#비트보드를 남동쪽으로 한 칸 이동
def SE_one(bitboard):
    return south_one(east_one(bitboard))
#비트보드를 남서쪽으로 한 칸 이동
def SW_one(bitboard):
    return south_one(west_one(bitboard))
#체스말을 이동시킴
def move_piece(board, move):
    new_board = deepcopy(board)
    new_board[bb2index(move[1])] = new_board[bb2index(move[0])] 
    new_board[bb2index(move[0])] = EMPTY
    return new_board

def make_move(game, move):
    #초기설정
    new_game = deepcopy(game)
    leaving_position = move[0]
    arriving_position = move[1]
    
    #클락 업데이트
    new_game.halfmove_clock += 1
    if new_game.to_move == BLACK:
        new_game.fullmove_number += 1
    
    #캡처 시 클락 리셋
    if get_piece(new_game.board, arriving_position) != EMPTY:
        new_game.halfmove_clock = 0
    
    #폰의 이동 처리
    if get_piece(new_game.board, leaving_position)&PIECE_MASK == PAWN:
        new_game.halfmove_clock = 0
        
        if arriving_position == game.ep_square:
            new_game.board = remove_captured_ep(new_game)
    
        if is_double_push(leaving_position, arriving_position):
            new_game.ep_square = new_ep_square(leaving_position)
            
        if arriving_position&(RANK_1|RANK_8):
            new_game.board[bb2index(leaving_position)] = new_game.to_move|QUEEN
    
    #앙파상 위치 리셋
    if new_game.ep_square == game.ep_square:
        new_game.ep_square = 0
        
    #루크 이동 시 캐슬링 권리 업데이트
    if leaving_position == str2bb('a1'):
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_QUEENSIDE_WHITE)
    if leaving_position == str2bb('h1'):
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_KINGSIDE_WHITE)
    if leaving_position == str2bb('a8'):
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_QUEENSIDE_BLACK)
    if leaving_position == str2bb('h8'):
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_KINGSIDE_BLACK)
    
    #캐슬링 처리
    if get_piece(new_game.board, leaving_position) == WHITE|KING:
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_KINGSIDE_WHITE|CASTLE_QUEENSIDE_WHITE)
        if leaving_position == str2bb('e1'):
            if arriving_position == str2bb('g1'):
                new_game.board = move_piece(new_game.board, [str2bb('h1'), str2bb('f1')])
            if arriving_position == str2bb('c1'):
                new_game.board = move_piece(new_game.board, [str2bb('a1'), str2bb('d1')])
        
    if get_piece(new_game.board, leaving_position) == BLACK|KING:
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_KINGSIDE_BLACK|CASTLE_QUEENSIDE_BLACK)
        if leaving_position == str2bb('e8'):
            if arriving_position == str2bb('g8'):
                new_game.board = move_piece(new_game.board, [str2bb('h8'), str2bb('f8')])
            if arriving_position == str2bb('c8'):
                new_game.board = move_piece(new_game.board, [str2bb('a8'), str2bb('d8')])
    
    #위치 및 다음 수 업데이트
    new_game.board = move_piece(new_game.board, (leaving_position, arriving_position))
    new_game.to_move = opposing_color(new_game.to_move)
    
    #히스토리 업데이트
    new_game.move_history.append(move2str(move))
    new_game.position_history.append(new_game.to_FEN())
    #새로운 게임 상태 반환
    return new_game
#이전 이동을 되돌려 게임 상태를 업데이트
def unmake_move(game):
    if len(game.position_history) < 2:
        return deepcopy(game)
    
    new_game = Game(game.position_history[-2])
    new_game.move_history = deepcopy(game.move_history)[:-1]
    new_game.position_history = deepcopy(game.position_history)[:-1]
    return new_game
#주어진 랭크 번호에 해당하는 비트보드를 반환
def get_rank(rank_num):
    rank_num = int(rank_num)
    return RANK_MASKS[rank_num]
#주어진 파일 문자열에 해당하는 비트보드를 반환     
def get_file(file_str):
    file_str = file_str.lower()
    file_num = FILES.index(file_str)
    return FILE_MASKS[file_num]
#주어진 문자열이 파일인지 랭크인지 판단하여 해당하는 비트보드를 반환    
def get_filter(filter_str):
    if filter_str in FILES:
        return get_file(filter_str)
    if filter_str in RANKS:
        return get_rank(filter_str)

# ========== PAWN ==========
#보드에 있는 모든 폰의 위치를 비트보드로 반환
def get_all_pawns(board):
    return list2int([ i&PIECE_MASK == PAWN for i in board ])
#주어진 색상의 폰의 위치를 비트보드로 반환
def get_pawns(board, color):
    return list2int([ i == color|PAWN for i in board ])
#폰의 가능한 이동을 계산
def pawn_moves(moving_piece, game, color):
    return pawn_pushes(moving_piece, game.board, color) | pawn_captures(moving_piece, game, color)
#폰의 가능한 캡처 이동을 계산
def pawn_captures(moving_piece, game, color):
    return pawn_simple_captures(moving_piece, game, color) | pawn_ep_captures(moving_piece, game, color)
#폰의 가능한 푸시 이동을 계산
def pawn_pushes(moving_piece, board, color):
    return pawn_simple_pushes(moving_piece, board, color) | pawn_double_pushes(moving_piece, board, color)
#폰의 가능한 단순 캡처를 계산
def pawn_simple_captures(attacking_piece, game, color):
    return pawn_attacks(attacking_piece, game.board, color) & get_colored_pieces(game.board, opposing_color(color))
#폰의 가능한 앙파상 캡처를 계산
def pawn_ep_captures(attacking_piece, game, color):
    if color == WHITE:
        ep_squares = game.ep_square & RANK_6
    if color == BLACK:
        ep_squares = game.ep_square & RANK_3
    return pawn_attacks(attacking_piece, game.board, color) & ep_squares
#폰의 가능한 모든 공격 위치를 계산
def pawn_attacks(attacking_piece, board, color):
    return pawn_east_attacks(attacking_piece, board, color) | pawn_west_attacks(attacking_piece, board, color)
#폰의 가능한 단순 푸시를 계산
def pawn_simple_pushes(moving_piece, board, color):
    if color == WHITE:
        return north_one(moving_piece) & empty_squares(board)
    if color == BLACK:
        return south_one(moving_piece) & empty_squares(board)
#폰의 가능한 더블 푸시를 계산    
def pawn_double_pushes(moving_piece, board, color):
    if color == WHITE:
        return north_one(pawn_simple_pushes(moving_piece, board, color)) & (empty_squares(board) & RANK_4)
    if color == BLACK:
        return south_one(pawn_simple_pushes(moving_piece, board, color)) & (empty_squares(board) & RANK_5)
#폰의 동쪽 공격 위치를 계산
def pawn_east_attacks(attacking_piece, board, color):
    if color == WHITE:
        return NE_one(attacking_piece & get_colored_pieces(board, color))
    if color == BLACK:
        return SE_one(attacking_piece & get_colored_pieces(board, color))
#폰의 서쪽 공격 위치를 계산
def pawn_west_attacks(attacking_piece, board, color):
    if color == WHITE:
        return NW_one(attacking_piece & get_colored_pieces(board, color))
    if color == BLACK:
        return SW_one(attacking_piece & get_colored_pieces(board, color))
#주어진 폰의 동쪽과 서쪽 공격 위치가 모두 가능한 경우를 반환
def pawn_double_attacks(attacking_piece, board, color):
    return pawn_east_attacks(attacking_piece, board, color) & pawn_west_attacks(attacking_piece, board, color)
#주어진 이동이 더블 푸시인지 확인
def is_double_push(leaving_square, target_square):
    return (leaving_square&RANK_2 and target_square&RANK_4) or \
           (leaving_square&RANK_7 and target_square&RANK_5)
#더블 푸시 후 새로운 앙파상 위치를 반환    
def new_ep_square(leaving_square):
    if leaving_square&RANK_2:
        return north_one(leaving_square)
    if leaving_square&RANK_7:
        return south_one(leaving_square)
#앙파상 캡처로 제거된 폰을 보드에서 제거
def remove_captured_ep(game):
    new_board = deepcopy(game.board)
    if game.ep_square & RANK_3:
        new_board[bb2index(north_one(game.ep_square))] = EMPTY
    if game.ep_square & RANK_6:
        new_board[bb2index(south_one(game.ep_square))] = EMPTY
    return new_board

# ========== KNIGHT ==========
#주어진 색상의 나이트 위치를 비트보드로 반환
def get_knights(board, color):
    return list2int([ i == color|KNIGHT for i in board ])
#주어진 나이트의 모든 가능한 이동을 반환
def knight_moves(moving_piece, board, color):
    return knight_attacks(moving_piece) & nnot(get_colored_pieces(board, color))
#주어진 나이트의 모든 공격 위치를 반환
def knight_attacks(moving_piece):
    return knight_NNE(moving_piece) | \
           knight_ENE(moving_piece) | \
           knight_NNW(moving_piece) | \
           knight_WNW(moving_piece) | \
           knight_SSE(moving_piece) | \
           knight_ESE(moving_piece) | \
           knight_SSW(moving_piece) | \
           knight_WSW(moving_piece)
#왼쪽 위 2칸, 위쪽 1칸
def knight_WNW(moving_piece):
    return moving_piece << 6 & nnot(FILE_G | FILE_H)
#오른쪽 위 2칸, 오른쪽 1칸
def knight_ENE(moving_piece):
    return moving_piece << 10 & nnot(FILE_A | FILE_B)
#왼쪽 위 2칸, 왼쪽 1칸
def knight_NNW(moving_piece):
    return moving_piece << 15 & nnot(FILE_H)
#오른쪽 위 2칸, 오른쪽 1칸
def knight_NNE(moving_piece):
    return moving_piece << 17 & nnot(FILE_A)
#오른쪽 아래 2칸, 오른쪽 1칸
def knight_ESE(moving_piece):
    return moving_piece >> 6 & nnot(FILE_A | FILE_B)
#왼쪽 아래 2칸, 왼쪽 1칸
def knight_WSW(moving_piece):
    return moving_piece >> 10 & nnot(FILE_G | FILE_H)
#오른쪽 아래 2칸, 오른쪽 1칸
def knight_SSE(moving_piece):
    return moving_piece >> 15 & nnot(FILE_A)
#왼쪽 아래 2칸, 왼쪽 1칸
def knight_SSW(moving_piece):
    return moving_piece >> 17 & nnot(FILE_H)
#주어진 나이트 위치에서 n단계까지의 모든 공격 위치를 반환
def knight_fill(moving_piece, n):
    fill = moving_piece
    for _ in range(n):
        fill |= knight_attacks(fill)
    return fill
#나이트가 주어진 두 위치 사이를 이동하는 데 필요한 최소 이동 횟수를 계산
def knight_distance(pos1, pos2):
    init_bitboard = str2bb(pos1)
    end_bitboard = str2bb(pos2)
    fill = init_bitboard
    dist = 0
    while fill & end_bitboard == 0:
        dist += 1
        fill = knight_fill(init_bitboard, dist)
    return dist
    
# ========== KING ==========
#주어진 색상의 킹의 위치를 비트보드로 반환
def get_king(board, color):
    return list2int([ i == color|KING for i in board ])
#주어진 킹의 모든 가능한 이동을 반환
def king_moves(moving_piece, board, color):
    return king_attacks(moving_piece) & nnot(get_colored_pieces(board, color))
#주어진 킹의 모든 공격 위치를 반환
def king_attacks(moving_piece):
    king_atks = moving_piece | east_one(moving_piece) | west_one(moving_piece)
    king_atks |= north_one(king_atks) | south_one(king_atks)
    return king_atks & nnot(moving_piece)
#주어진 색상의 킹사이드 캐슬링을 할 수 있는지 확인
def can_castle_kingside(game, color):
    if color == WHITE:
        return (game.castling_rights & CASTLE_KINGSIDE_WHITE) and \
                game.board[str2index('f1')] == EMPTY and \
                game.board[str2index('g1')] == EMPTY and \
                (not is_attacked(str2bb('e1'), game.board, opposing_color(color))) and \
                (not is_attacked(str2bb('f1'), game.board, opposing_color(color))) and \
                (not is_attacked(str2bb('g1'), game.board, opposing_color(color)))
    if color == BLACK:
        return (game.castling_rights & CASTLE_KINGSIDE_BLACK) and \
                game.board[str2index('f8')] == EMPTY and \
                game.board[str2index('g8')] == EMPTY and \
                (not is_attacked(str2bb('e8'), game.board, opposing_color(color))) and \
                (not is_attacked(str2bb('f8'), game.board, opposing_color(color))) and \
                (not is_attacked(str2bb('g8'), game.board, opposing_color(color)))
#주어진 색상이 퀸사이드 캐슬링을 할 수 있는지 확인
def can_castle_queenside(game, color):
    if color == WHITE:
        return (game.castling_rights & CASTLE_QUEENSIDE_WHITE) and \
                game.board[str2index('b1')] == EMPTY and \
                game.board[str2index('c1')] == EMPTY and \
                game.board[str2index('d1')] == EMPTY and \
                (not is_attacked(str2bb('c1'), game.board, opposing_color(color))) and \
                (not is_attacked(str2bb('d1'), game.board, opposing_color(color))) and \
                (not is_attacked(str2bb('e1'), game.board, opposing_color(color)))
    if color == BLACK:
        return (game.castling_rights & CASTLE_QUEENSIDE_BLACK) and \
                game.board[str2index('b8')] == EMPTY and \
                game.board[str2index('c8')] == EMPTY and \
                game.board[str2index('d8')] == EMPTY and \
                (not is_attacked(str2bb('c8'), game.board, opposing_color(color))) and \
                (not is_attacked(str2bb('d8'), game.board, opposing_color(color))) and \
                (not is_attacked(str2bb('e8'), game.board, opposing_color(color)))
#주어진 게임 상태에서 킹사이드 캐슬링 이동을 반환
def castle_kingside_move(game):
    if game.to_move == WHITE:
        return (str2bb('e1'), str2bb('g1'))
    if game.to_move == BLACK:
        return (str2bb('e8'), str2bb('g8'))
#주어진 게임 상태에서 퀸사이드 캐슬링 이동을 반환
def castle_queenside_move(game):
    if game.to_move == WHITE:
        return (str2bb('e1'), str2bb('c1'))
    if game.to_move == BLACK:
        return (str2bb('e8'), str2bb('c8'))
#주어진 게임 상태에서 특정 캐슬링 권리를 제거
def remove_castling_rights(game, removed_rights):
    return game.castling_rights & ~removed_rights

# ========== BISHOP ==========
#주어진 색상의 비숍의 위치를 비트보드로 반환
def get_bishops(board, color):
    return list2int([ i == color|BISHOP for i in board ])
#주어진 비숍의 대각선 방향 모든 공격 위치를 반환
def bishop_rays(moving_piece):
    return diagonal_rays(moving_piece) | anti_diagonal_rays(moving_piece)
#주어진 비숍의 대각선 방향 공격 위치를 반환           
def diagonal_rays(moving_piece):
    return NE_ray(moving_piece) | SW_ray(moving_piece)
#주어진 비숍의 반대각선 방향 공격 위치를 반환
def anti_diagonal_rays(moving_piece):
    return NW_ray(moving_piece) | SE_ray(moving_piece)
#주어진 방향으로 비숍을 이동 -> 북동쪽 방향 이동
def NE_ray(moving_piece):
    ray_atks = NE_one(moving_piece)
    for _ in range(6):
        ray_atks |= NE_one(ray_atks)
    return ray_atks & ALL_SQUARES
#남동쪽 방향 이동
def SE_ray(moving_piece):
    ray_atks = SE_one(moving_piece)
    for _ in range(6):
        ray_atks |= SE_one(ray_atks)
    return ray_atks & ALL_SQUARES
#북서쪽 방향 이동
def NW_ray(moving_piece):
    ray_atks = NW_one(moving_piece)
    for _ in range(6):
        ray_atks |= NW_one(ray_atks)
    return ray_atks & ALL_SQUARES
#남서쪽 방향 이동
def SW_ray(moving_piece):
    ray_atks = SW_one(moving_piece)
    for _ in range(6):
        ray_atks |= SW_one(ray_atks)
    return ray_atks & ALL_SQUARES
#주어진 방향으로 비숍의 공격 위치를 계산 -> 북동
def NE_attacks(single_piece, board, color):
    blocker = lsb(NE_ray(single_piece) & occupied_squares(board))
    if blocker:
        return NE_ray(single_piece) ^ NE_ray(blocker)
    else:
        return NE_ray(single_piece)
#북서    
def NW_attacks(single_piece, board, color):
    blocker = lsb(NW_ray(single_piece) & occupied_squares(board))
    if blocker:
        return NW_ray(single_piece) ^ NW_ray(blocker)
    else:
        return NW_ray(single_piece)
#남동
def SE_attacks(single_piece, board, color):
    blocker = msb(SE_ray(single_piece) & occupied_squares(board))
    if blocker:
        return SE_ray(single_piece) ^ SE_ray(blocker)
    else:
        return SE_ray(single_piece)
#남서
def SW_attacks(single_piece, board, color):
    blocker = msb(SW_ray(single_piece) & occupied_squares(board))
    if blocker:
        return SW_ray(single_piece) ^ SW_ray(blocker)
    else:
        return SW_ray(single_piece)
#주어진 비숍의 대각선 및 반대각선 방향 모든 공격 위치를 계산 -> 대각선 방향 공격
def diagonal_attacks(single_piece, board, color):
    return NE_attacks(single_piece, board, color) | SW_attacks(single_piece, board, color)
#반대각선 방향 공격
def anti_diagonal_attacks(single_piece, board, color):
    return NW_attacks(single_piece, board, color) | SE_attacks(single_piece, board, color)
#주어진 비숍의 모든 공격 위치를 계산
def bishop_attacks(moving_piece, board, color):
    atks = 0
    for piece in single_gen(moving_piece):
        atks |= diagonal_attacks(piece, board, color) | anti_diagonal_attacks(piece, board, color)
    return atks
#주어진 비숍의 모든 가능한 이동을 게산
def bishop_moves(moving_piece, board, color):
    return bishop_attacks(moving_piece, board, color) & nnot(get_colored_pieces(board, color))

# ========== ROOK ==========
#주어진 색상의 룩의 위치를 비트보드로 반환
def get_rooks(board, color):
    return list2int([ i == color|ROOK for i in board ])
#주어진 룩의 모든 랭크 및 파일 방향 공격 위치를 반환
def rook_rays(moving_piece):
    return rank_rays(moving_piece) | file_rays(moving_piece)
#주어진 룩의 랭크(가로)방향 공격 위치를 반환
def rank_rays(moving_piece):
    return east_ray(moving_piece) | west_ray(moving_piece)
#주어진 룩의 파일(세로)방향 공격 위치를 반환
def file_rays(moving_piece):
    return north_ray(moving_piece) | south_ray(moving_piece)
#주어진 방향으로 룩을 이동시킴 -> 동쪽
def east_ray(moving_piece):
    ray_atks = east_one(moving_piece)
    for _ in range(6):
        ray_atks |= east_one(ray_atks)
    return ray_atks & ALL_SQUARES
#서쪽
def west_ray(moving_piece):
    ray_atks = west_one(moving_piece)
    for _ in range(6):
        ray_atks |= west_one(ray_atks)
    return ray_atks & ALL_SQUARES
#북쪽
def north_ray(moving_piece):
    ray_atks = north_one(moving_piece)
    for _ in range(6):
        ray_atks |= north_one(ray_atks)
    return ray_atks & ALL_SQUARES
#남쪽
def south_ray(moving_piece):
    ray_atks = south_one(moving_piece)
    for _ in range(6):
        ray_atks |= south_one(ray_atks)
    return ray_atks & ALL_SQUARES
#주어진 방향으로 룩의 공격 위치를 계산 -> 동쪽
def east_attacks(single_piece, board, color):
    blocker = lsb(east_ray(single_piece) & occupied_squares(board))
    if blocker:
        return east_ray(single_piece) ^ east_ray(blocker)
    else:
        return east_ray(single_piece)
#서쪽    
def west_attacks(single_piece, board, color):
    blocker = msb(west_ray(single_piece) & occupied_squares(board))
    if blocker:
        return west_ray(single_piece) ^ west_ray(blocker)
    else:
        return west_ray(single_piece)
#랭크(가로)    
def rank_attacks(single_piece, board, color):
    return east_attacks(single_piece, board, color) | west_attacks(single_piece, board, color)
#북쪽
def north_attacks(single_piece, board, color):
    blocker = lsb(north_ray(single_piece) & occupied_squares(board))
    if blocker:
        return north_ray(single_piece) ^ north_ray(blocker)
    else:
        return north_ray(single_piece)
#남쪽    
def south_attacks(single_piece, board, color):
    blocker = msb(south_ray(single_piece) & occupied_squares(board))
    if blocker:
        return south_ray(single_piece) ^ south_ray(blocker)
    else:
        return south_ray(single_piece)
#파일(세로) 방향 공격    
def file_attacks(single_piece, board, color):
    return north_attacks(single_piece, board, color) | south_attacks(single_piece, board, color)
#주어진 룩의 모든 공격 위치를 계산
def rook_attacks(moving_piece, board, color):
    atks = 0
    for single_piece in single_gen(moving_piece):
        atks |= rank_attacks(single_piece, board, color) | file_attacks(single_piece, board, color)
    return atks
#주어진 룩의 모든 가능한 이동을 계산
def rook_moves(moving_piece, board, color):
    return rook_attacks(moving_piece, board, color) & nnot(get_colored_pieces(board, color))

# ========== QUEEN ==========
#주어진 색상의 퀸의 위치를 비트보드로 반환
def get_queen(board, color):
    return list2int([ i == color|QUEEN for i in board ])
#주어진 퀸의 모든 랭크, 파일, 대각선 및 반대각선 방향 공격 위치를 반환
def queen_rays(moving_piece):
    return rook_rays(moving_piece) | bishop_rays(moving_piece)
#주어진 퀸의 모든 공격 위치를 반환
def queen_attacks(moving_piece, board, color):
    return bishop_attacks(moving_piece, board, color) | rook_attacks(moving_piece, board, color)
#주어진 퀸의 모든 가능한 이동을 반환
def queen_moves(moving_piece, board, color):
    return bishop_moves(moving_piece, board, color) | rook_moves(moving_piece, board, color)

# ========== JOKER ==========
#주어진 조커의 모든 랭크, 파일, 대각선 및 반대각선 방향 공격 위치를 반환
def joker_rays(moving_piece):
    return queen_rays(moving_piece)
#주어진 조커의 모든 공격 위치를 반환
def joker_attacks(moving_piece, board, color):
    return queen_attacks(moving_piece, board, color) | knight_attacks(moving_piece)
#주어진 조커의 모든 가능한 이동을 반환
def joker_moves(moving_piece, board, color):
    return queen_moves(moving_piece, board, color) | knight_moves(moving_piece, board, color)

# ===========================
#주어진 위치가 공격받고 있는지 확인
def is_attacked(target, board, attacking_color):
    return count_attacks(target, board, attacking_color) > 0
#주어진 색상의 킹이 체크 상태인지 확인
def is_check(board, color):
    return is_attacked(get_king(board, color), board, opposing_color(color))
#주어진 체스말의 모든 공격 위치를 반환
def get_attacks(moving_piece, board, color):
    piece = board[bb2index(moving_piece)]
    
    if piece&PIECE_MASK == PAWN:
        return pawn_attacks(moving_piece, board, color)
    elif piece&PIECE_MASK == KNIGHT:
        return knight_attacks(moving_piece)
    elif piece&PIECE_MASK == BISHOP:
        return bishop_attacks(moving_piece, board, color)
    elif piece&PIECE_MASK == ROOK:
        return rook_attacks(moving_piece, board, color)
    elif piece&PIECE_MASK == QUEEN:
        return queen_attacks(moving_piece, board, color)
    elif piece&PIECE_MASK == KING:
        return king_attacks(moving_piece)
    elif piece&PIECE_MASK == JOKER:
        return joker_attacks(moving_piece, board, color)
#주어진 체스말의 모든 가능한 이동 위치를 반환
def get_moves(moving_piece, game, color):
    piece = game.board[bb2index(moving_piece)]
    
    if piece&PIECE_MASK == PAWN:
        return pawn_moves(moving_piece, game, color)
    elif piece&PIECE_MASK == KNIGHT:
        return knight_moves(moving_piece, game.board, color)
    elif piece&PIECE_MASK == BISHOP:
        return bishop_moves(moving_piece, game.board, color)
    elif piece&PIECE_MASK == ROOK:
        return rook_moves(moving_piece, game.board, color)
    elif piece&PIECE_MASK == QUEEN:
        return queen_moves(moving_piece, game.board, color)
    elif piece&PIECE_MASK == KING:
        return king_moves(moving_piece, game.board, color)
    elif piece&PIECE_MASK == JOKER:
        return joker_moves(moving_piece, game.board, color)
#특정 위치가 공격받는 횟수를 계산
def count_attacks(target, board, attacking_color):
    attack_count = 0
      
    for index in range(64):
        piece = board[index]
        if piece != EMPTY and piece&COLOR_MASK == attacking_color:
            pos = 0b1 << index
            
            if get_attacks(pos, board, attacking_color) & target:
                attack_count += 1
                      
    return attack_count
#주어진 색상의 체스말의 물질 점수를 계산
def material_sum(board, color):
    material = 0
    for piece in board:
        if piece&COLOR_MASK == color:
            material += PIECE_VALUES[piece&PIECE_MASK]
    return material
#체스판에서 백과 흑 체스말의 물질 점수 차이를 계산
def material_balance(board):
    return material_sum(board, WHITE) - material_sum(board, BLACK)
#백과 흑 체스말의 이동 가능성 차이를 계산
def mobility_balance(game):
    return count_legal_moves(game, WHITE) - count_legal_moves(game, BLACK)
#게임 상태를 평가
def evaluate_game(game):
    if game_ended(game):
        return evaluate_end_node(game)
    else:
        return material_balance(game.board) + positional_balance(game)# + 10*mobility_balance(game)
#게임의 종료 상태를 평가
def evaluate_end_node(game):
    if is_checkmate(game, game.to_move):
        return win_score(game.to_move)
    elif is_stalemate(game) or \
         has_insufficient_material(game) or \
         is_under_75_move_rule(game):
        return 0
#백과 흑 체스말의 위치적 균형을 계산
def positional_balance(game):
    return positional_bonus(game, WHITE) - positional_bonus(game, BLACK) 
#주어진 색상의 체스말의 위치 보너스를 계산
def positional_bonus(game, color):
    bonus = 0
    
    if color == WHITE:
        board = game.board
    elif color == BLACK:
        board = flip_board_v(game.board)
        
    for index in range(64):
        piece = board[index]
        
        if piece != EMPTY and piece&COLOR_MASK == color:
            piece_type = piece&PIECE_MASK
            
            if piece_type == PAWN:
                bonus += PAWN_BONUS[index]
            elif piece_type == KNIGHT:
                bonus += KNIGHT_BONUS[index]
            elif piece_type == BISHOP:
                bonus += BISHOP_BONUS[index]
             
            elif piece_type == ROOK:
                position = 0b1 << index
                 
                if is_open_file(position, board):
                    bonus += ROOK_OPEN_FILE_BONUS
                elif is_semi_open_file(position, board):
                    bonus += ROOK_SEMI_OPEN_FILE_BONUS
                     
                if position & RANK_7:
                    bonus += ROOK_ON_SEVENTH_BONUS
                 
            elif piece_type == KING:
                if is_endgame(board):
                    bonus += KING_ENDGAME_BONUS[index]
                else:
                    bonus += KING_BONUS[index]
    
    return bonus
#현재 보드가 엔드게임 상태인지 확인
def is_endgame(board):
    return count_pieces(occupied_squares(board)) <= ENDGAME_PIECE_COUNT
#주어진 비트보드 위치가 오픈 파일에 있는지 확인
def is_open_file(bitboard, board):
    for f in FILES:
        rank_filter = get_file(f)
        if bitboard & rank_filter:
            return count_pieces(get_all_pawns(board)&rank_filter) == 0
#주어진 비트보드 위치가 세미 오픈 파일에 있는지 확인
def is_semi_open_file(bitboard, board):
    for f in FILES:
        rank_filter = get_file(f)
        if bitboard & rank_filter:
            return count_pieces(get_all_pawns(board)&rank_filter) == 1
#주어진 비트보드에 있는 체스말의 수를 계산
def count_pieces(bitboard):
    return bin(bitboard).count("1")
#주어진 색상의 승리했을 때의 점수를 반환
def win_score(color):
    if color == WHITE:
        return -10*PIECE_VALUES[KING]
    if color == BLACK:
        return 10*PIECE_VALUES[KING]
#주어진 색상의 모든 가능한 이동을 생성(캐슬링 포함)
def pseudo_legal_moves(game, color):
    for index in range(64):
        piece = game.board[index]
        
        if piece != EMPTY and piece&COLOR_MASK == color:
            piece_pos = 0b1 << index
            
            for target in single_gen(get_moves(piece_pos, game, color)):
                yield (piece_pos, target)
                
    if can_castle_kingside(game, color):
        yield (get_king(game.board, color), east_one(east_one(get_king(game.board, color))))
    if can_castle_queenside(game, color):
        yield (get_king(game.board, color), west_one(west_one(get_king(game.board, color))))
#주어진 색상의 모든 합법적인 이동을 생성
def legal_moves(game, color):
    for move in pseudo_legal_moves(game, color):
        if is_legal_move(game, move):
            yield move
#주어진 이동이 합법적인지 확인
def is_legal_move(game, move):
    new_game = make_move(game, move)
    return not is_check(new_game.board, game.to_move)
#주어진 색상의 합법적인 이동 수를 계산    
def count_legal_moves(game, color):
    move_count = 0
    for _ in legal_moves(game, color):
        move_count += 1
    return move_count
#현재 게임 상태가 스테일메이트인지 확인
def is_stalemate(game):
    for _ in legal_moves(game, game.to_move):
        return False
    return not is_check(game.board, game.to_move)
#주어진 색상이 체크메이트 상태인지 확인  
def is_checkmate(game, color):
    for _ in legal_moves(game, game.to_move):
        return False
    return is_check(game.board, color)  
#두 개의 FEN문자열이 같은 위치를 나타내는지 확인
def is_same_position(FEN_a, FEN_b):
    FEN_a_list = FEN_a.split(' ')
    FEN_b_list = FEN_b.split(' ')
    return FEN_a_list[0] == FEN_b_list[0] and \
           FEN_a_list[1] == FEN_b_list[1] and \
           FEN_a_list[2] == FEN_b_list[2] and \
           FEN_a_list[3] == FEN_b_list[3]
#현재 위치가 세 번 반복되었는지 확인
def has_threefold_repetition(game):
    current_pos = game.position_history[-1]
    position_count = 0
    for position in game.position_history:
        if is_same_position(current_pos, position):
            position_count += 1
    return position_count >= 3
#50수 규칙에 따라 게임이 종료될 수 있는지 확인
def is_under_50_move_rule(game):
    return game.halfmove_clock >= 100
#75수 규칙에 따라 게임이 종료될 수 있는지 확인
def is_under_75_move_rule(game):
    return game.halfmove_clock >= 150
#현재 체스판에 남은 체스말로 승부를 낼 수 없는지 확인
def has_insufficient_material(game): # TODO: other insufficient positions
    if material_sum(game.board, WHITE) + material_sum(game.board, BLACK) == 2*PIECE_VALUES[KING]:
        return True
    if material_sum(game.board, WHITE) == PIECE_VALUES[KING]:
        if material_sum(game.board, BLACK) == PIECE_VALUES[KING] + PIECE_VALUES[KNIGHT] and \
        (get_knights(game.board, BLACK) != 0 or get_bishops(game.board, BLACK) != 0):
            return True
    if material_sum(game.board, BLACK) == PIECE_VALUES[KING]:
        if material_sum(game.board, WHITE) == PIECE_VALUES[KING] + PIECE_VALUES[KNIGHT] and \
        (get_knights(game.board, WHITE) != 0 or get_bishops(game.board, WHITE) != 0):
            return True
    return False
#게임이 종료되었는지 확인
def game_ended(game):
    return is_checkmate(game, WHITE) or \
           is_checkmate(game, BLACK) or \
           is_stalemate(game) or \
           has_insufficient_material(game) or \
           is_under_75_move_rule(game)
#주어진 색상의 체스말의 합법적인 이동 중 하나를 무작위로 선택
def random_move(game, color):
    return choice(legal_moves(game, color))
#주어진 색상의 체스말의 이동을 평가하고 최적의 이동을 결정
def evaluated_move(game, color):
    best_score = win_score(color)
    best_moves = []
    
    for move in legal_moves(game, color):
        evaluation = evaluate_game(make_move(game, move))
        
        if is_checkmate(make_move(game, move), opposing_color(game.to_move)):
            return [move, evaluation]
        
        if (color == WHITE and evaluation > best_score) or \
           (color == BLACK and evaluation < best_score):
            best_score = evaluation
            best_moves = [move]
        elif evaluation == best_score:
            best_moves.append(move)
                
    return [choice(best_moves), best_score]
#미니맥스 알고리즘을 사용하여 주어진 깊이까지 최적의 이동을 결정
def minimax(game, color, depth=1):
    if game_ended(game):
        return [None, evaluate_game(game)]
    
    [simple_move, simple_evaluation] = evaluated_move(game, color)
    
    if depth == 1 or \
       simple_evaluation == win_score(opposing_color(color)):
        return [simple_move, simple_evaluation]
    
    best_score = win_score(color)
    best_moves = []
    
    for move in legal_moves(game, color):
        his_game = make_move(game, move)
        
        if is_checkmate(his_game, his_game.to_move):
            return [move, win_score(his_game.to_move)]
            
        [_, evaluation] = minimax(his_game, opposing_color(color), depth-1)
        
        if evaluation == win_score(opposing_color(color)):
            return [move, evaluation]
        
        if (color == WHITE and evaluation > best_score) or \
           (color == BLACK and evaluation < best_score):
            best_score = evaluation
            best_moves = [move]
        elif evaluation == best_score:
            best_moves.append(move)
        
    return [choice(best_moves), best_score]
'''
알파-베타 가지치기 알고리즘을 사용하여 최적의 이동을 결정
게임이 종료되었는지 확인, 종료된 경우 게임 상태를 평가하여 반환
가능한 모든 합법적인 이동을 생성, 각 이동 후 게임 상태를 재귀적으로 평가
알파-베타 가지치기를 적용하여 불필요한 탐색을 줄임
최적의 평가 점수를 가진 이동을 찾고, 해당 이동을 반환. 동일한 평가 점수를 가진 이동이 여러 개 있는 경우 무작위로 선택
'''
def alpha_beta(game, color, depth, alpha=-float('inf'), beta=float('inf')):
    if game_ended(game):
        return [None, evaluate_game(game)]
    
    [simple_move, simple_evaluation] = evaluated_move(game, color)
    
    if depth == 1 or \
       simple_evaluation == win_score(opposing_color(color)):
        return [simple_move, simple_evaluation]

    best_moves = []
        
    if color == WHITE:
        for move in legal_moves(game, color):
            if verbose:
                print('\t'*depth + str(depth) + '. evaluating ' + PIECE_CODES[get_piece(game.board, move[0])] + move2str(move))
                
            new_game = make_move(game, move)
            [_, score] = alpha_beta(new_game, opposing_color(color), depth-1, alpha, beta)
            
            if verbose:
                print('\t'*depth + str(depth) + '. ' + str(score) + ' [{},{}]'.format(alpha, beta))
            
            if score == win_score(opposing_color(color)):
                return [move, score]
            
            if score == alpha:
                best_moves.append(move)
            if score > alpha: # white maximizes her score
                alpha = score
                best_moves = [move]
                if alpha > beta: # alpha-beta cutoff
                    if verbose:
                        print('\t'*depth + 'cutoff')
                    break
        if best_moves:
            return [choice(best_moves), alpha]
        else:
            return [None, alpha]
    
    if color == BLACK:
        for move in legal_moves(game, color):
            if verbose:
                print('\t'*depth + str(depth) + '. evaluating ' + PIECE_CODES[get_piece(game.board, move[0])] + move2str(move))
                
            new_game = make_move(game, move)
            [_, score] = alpha_beta(new_game, opposing_color(color), depth-1, alpha, beta)
            
            if verbose:
                print('\t'*depth + str(depth) + '. ' + str(score) + ' [{},{}]'.format(alpha, beta))
            
            if score == win_score(opposing_color(color)):
                return [move, score]
            
            if score == beta:
                best_moves.append(move)
            if score < beta: # black minimizes his score
                beta = score
                best_moves = [move]
                if alpha > beta: # alpha-beta cutoff
                    if verbose:
                        print('\t'*depth + 'cutoff')
                    break
        if best_moves:
            return [choice(best_moves), beta]
        else:
            return [None, beta]
#체스 게임의 이동 코드를 파싱하여 해당 이동을 해석, 이를 실행 가능한 이동으로 변환
def parse_move_code(game, move_code):
    move_code = move_code.replace(" ","")
    move_code = move_code.replace("x","")
    
    if move_code.upper() == 'O-O' or move_code == '0-0':
        if can_castle_kingside(game, game.to_move):
            return castle_kingside_move(game)
        
    if move_code.upper() == 'O-O-O' or move_code == '0-0-0':
        if can_castle_queenside(game, game.to_move):
            return castle_queenside_move(game)
    
    if len(move_code) < 2 or len(move_code) > 4:
        return False
    
    if len(move_code) == 4:
        filter_squares = get_filter(move_code[1])
    else:
        filter_squares = ALL_SQUARES

    destination_str = move_code[-2:]
    if destination_str[0] in FILES and destination_str[1] in RANKS:
        target_square = str2bb(destination_str)
    else:
        return False

    if len(move_code) == 2:
        piece = PAWN
    else:
        piece_code = move_code[0]
        if piece_code in FILES:
            piece = PAWN
            filter_squares = get_filter(piece_code)
        elif piece_code in PIECE_CODES:
            piece = PIECE_CODES[piece_code]&PIECE_MASK
        else:
            return False
    
    valid_moves = []
    for move in legal_moves(game, game.to_move):
        if move[1] & target_square and \
           move[0] & filter_squares and \
           get_piece(game.board, move[0])&PIECE_MASK == piece:
            valid_moves.append(move)                     
    
    if len(valid_moves) == 1:
        return valid_moves[0]
    else:
        return False
    
def move2str(move):
    return bb2str(move[0]) + bb2str(move[1])

def str2bb(position_str):
    return 0b1 << str2index(position_str)
#사용자의 이동 입력을 처리하고, 유요한 이동을 반환
def get_player_move(game):
    move = None
    while not move:
        move = parse_move_code(game, input())
        if not move:
            print('Invalid move!')
    return move
#AI 플레이어 최적 이동을 계산하고 반환
def get_AI_move(game, depth=2):
    if verbose:
        print('Searching best move for white...' if game.to_move == WHITE else 'Searching best move for black...')
    start_time = time()

    if find_in_book(game):
        move = get_book_move(game)
    else:
#         move = minimax(game, game.to_move, depth)[0]
        move = alpha_beta(game, game.to_move, depth)[0]

    end_time = time()
    if verbose:
        print('Found move ' + PIECE_CODES[get_piece(game.board, move[0])] + ' from ' + str(bb2str(move[0])) + ' to ' + str(bb2str(move[1])) + ' in {:.3f} seconds'.format(end_time-start_time) + ' ({},{})'.format(evaluate_game(game), evaluate_game(make_move(game, move))))
    return move
#현재 게임의 결과를 출력
def print_outcome(game):
    print(get_outcome(game))
#현재 게임의 결과를 확인하고 반환    
def get_outcome(game):
    if is_stalemate(game):
        return 'Draw by stalemate'
    if is_checkmate(game, WHITE):
        return 'BLACK wins!'
    if is_checkmate(game, BLACK):
        return 'WHITE wins!'
    if has_insufficient_material(game):
        return 'Draw by insufficient material!'
    if is_under_75_move_rule(game):
        return 'Draw by 75-move rule!'
#백색 플레이어로 게임을 플레이
def play_as_white(game=Game()):
    print('Playing as white!')
    while True:
        print_board(game.board)
        if game_ended(game):
            break
        
        game = make_move(game, get_player_move(game))
        
        print_board(game.board)
        if game_ended(game):
            break
        
        game = make_move(game, get_AI_move(game))
    print_outcome(game)

#흑색 플레이어로 게임을 플레이
def play_as_black(game=Game()):
    print('Playing as black!')
    while True:
        print_rotated_board(game.board)
        if game_ended(game):
            break
        
        game = make_move(game, get_AI_move(game))
        
        print_rotated_board(game.board)
        if game_ended(game):
            break
        
        game = make_move(game, get_player_move(game))
    print_outcome(game)
#AI 대 AI 게임을 관전
def watch_AI_game(game=Game(), sleep_seconds=0):
    print('Watching AI-vs-AI game!')
    while True:
        print_board(game.board)
        if game_ended(game):
            break
                
        game = make_move(game, get_AI_move(game))
        sleep(sleep_seconds)
    print_outcome(game)
    
#주어진 색상으로 게임을 시작        
def play_as(color):
    if color == WHITE:
        play_as_white()
    if color == BLACK:
        play_as_black()
#무작위로 생상을 선택하여 게임을 시작
def play_random_color():
    color = choice([WHITE, BLACK])
    play_as(color)
#오프닝 북에서 현재 게임 상태와 일치하는 오프닝을 찾음
def find_in_book(game):
    if game.position_history[0] != INITIAL_FEN:
        return False
    
    openings = []
    book_file = open("book.txt")
    for line in book_file:
        if line.startswith(game.get_move_list()) and line.rstrip() > game.get_move_list():
            openings.append(line.rstrip())
    book_file.close()
    return openings
#오프닝 북에서 현재 게임 상태와 일치하는 오프닝을 찾아 다음 이동을 반환
def get_book_move(game):
    openings = find_in_book(game)
    chosen_opening = choice(openings)
    next_moves = chosen_opening.replace(game.get_move_list(), '').lstrip()
    move_str = next_moves.split(' ')[0]
    move = [str2bb(move_str[:2]), str2bb(move_str[-2:])]
    return move

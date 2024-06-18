import pygame, chess #그래픽 인터페이스 / 게임 로직
from random import choice #렌덤 선택
from traceback import format_exc #에러처리
from sys import stderr #시스템 연산
from time import strftime #시간 포맷팅
from copy import deepcopy #복사
import socket
import threading
from chess import Game, parse_move_code, print_board, print_rotated_board, game_ended, print_outcome, make_move, move2str, str2bb

HOST = '127.0.0.1'  # 서버의 IP 주소
PORT = 65432
pygame.init()

SQUARE_SIDE = 50 #체스 보드 각 칸의 한 변의 길이를 설정
AI_SEARCH_DEPTH = 2 #AI 의사 결정 과정에서 탐색 깊이를 설정

'''
보드 테마에 사용할 RGB 색상 튜플을 정의
여러 가지 보드 색상 테마를 튜플로 묶어 리스트화
보드 색상 테마를 랜덤으로 선택
'''

RED_CHECK          = (240, 150, 150)
WHITE              = (255, 255, 255)
BLUE_LIGHT         = (140, 184, 219)
BLUE_DARK          = (91,  131, 159)
GRAY_LIGHT         = (240, 240, 240)
GRAY_DARK          = (200, 200, 200)
CHESSWEBSITE_LIGHT = (212, 202, 190)
CHESSWEBSITE_DARK  = (100,  92,  89)
LICHESS_LIGHT      = (240, 217, 181)
LICHESS_DARK       = (181, 136,  99)
LICHESS_GRAY_LIGHT = (164, 164, 164)
LICHESS_GRAY_DARK  = (136, 136, 136)

BOARD_COLORS = [(GRAY_LIGHT, GRAY_DARK),
                (BLUE_LIGHT, BLUE_DARK),
                (WHITE, BLUE_LIGHT),
                (CHESSWEBSITE_LIGHT, CHESSWEBSITE_DARK),
                (LICHESS_LIGHT, LICHESS_DARK),
                (LICHESS_GRAY_LIGHT, LICHESS_GRAY_DARK)]
BOARD_COLOR = choice(BOARD_COLORS)

BLACK_KING   = pygame.image.load('images/black_king.png')
BLACK_QUEEN  = pygame.image.load('images/black_queen.png')
BLACK_ROOK   = pygame.image.load('images/black_rook.png')
BLACK_BISHOP = pygame.image.load('images/black_bishop.png')
BLACK_KNIGHT = pygame.image.load('images/black_knight.png')
BLACK_PAWN   = pygame.image.load('images/black_pawn.png')
BLACK_JOKER  = pygame.image.load('images/black_joker.png')

WHITE_KING   = pygame.image.load('images/white_king.png')
WHITE_QUEEN  = pygame.image.load('images/white_queen.png')
WHITE_ROOK   = pygame.image.load('images/white_rook.png')
WHITE_BISHOP = pygame.image.load('images/white_bishop.png')
WHITE_KNIGHT = pygame.image.load('images/white_knight.png')
WHITE_PAWN   = pygame.image.load('images/white_pawn.png')
WHITE_JOKER  = pygame.image.load('images/white_joker.png')

CLOCK = pygame.time.Clock() # 게임의 프레임 속도를 제어하기 위한 시계 객체를 초기화함.
CLOCK_TICK = 15 #프레임 속도 설정

#체스 보드의 크기를 기준으로 화면을 설정하고 크기 조정 가능.
SCREEN = pygame.display.set_mode((8*SQUARE_SIDE, 8*SQUARE_SIDE), pygame.RESIZABLE)
SCREEN_TITLE = 'Chess Game'

pygame.display.set_icon(pygame.image.load('images/chess_icon.ico'))
pygame.display.set_caption(SCREEN_TITLE)

#체스 보드의 각 크기를 변경하게, 이에 맞춰 화면 크기를 조정
def resize_screen(square_side_len):
    global SQUARE_SIDE #전역 변수를 수정할 수 있게함
    global SCREEN
    SCREEN = pygame.display.set_mode((8*square_side_len, 8*square_side_len), pygame.RESIZABLE)
    SQUARE_SIDE = square_side_len

#빈 체스 보드를 화면에 그림
def print_empty_board():
    SCREEN.fill(BOARD_COLOR[0])
    paint_dark_squares(BOARD_COLOR[1])

#특정 위치의 체스 칸을 지정된 색으로 그림
def paint_square(square, square_color):
    col = chess.FILES.index(square[0])
    row = 7-chess.RANKS.index(square[1])
    pygame.draw.rect(SCREEN, square_color, (SQUARE_SIDE*col,SQUARE_SIDE*row,SQUARE_SIDE,SQUARE_SIDE), 0)

# 보드의 어두운 칸들을 지정된 색으로 그림
def paint_dark_squares(square_color):
    for position in chess.single_gen(chess.DARK_SQUARES):
        paint_square(chess.bb2str(position), square_color)

#주어진 체스 칸의 위치를 기반으로 Pygame 사각형 객체를 생성       
def get_square_rect(square):
    col = chess.FILES.index(square[0])
    row = 7-chess.RANKS.index(square[1])
    return pygame.Rect((col*SQUARE_SIDE, row*SQUARE_SIDE), (SQUARE_SIDE,SQUARE_SIDE))

#화면 좌표를 체스 칸 위치 문자열로 변환 -> 사용자 입력을 보드 칸으로 매핑
def coord2str(position, color=chess.WHITE):
    if color == chess.WHITE:
        file_index = int(position[0]/SQUARE_SIDE)
        rank_index = 7 - int(position[1]/SQUARE_SIDE)
        return chess.FILES[file_index] + chess.RANKS[rank_index]
    if color == chess.BLACK:
        file_index = 7 - int(position[0]/SQUARE_SIDE)
        rank_index = int(position[1]/SQUARE_SIDE)
        return chess.FILES[file_index] + chess.RANKS[rank_index]
    
def print_board(board, color=chess.WHITE):
    if color == chess.WHITE:
        printed_board = board
    if color == chess.BLACK:
        printed_board = chess.rotate_board(board)
    
    print_empty_board()
    
    if chess.is_check(board, chess.WHITE):
        paint_square(chess.bb2str(chess.get_king(printed_board, chess.WHITE)), RED_CHECK)
    if chess.is_check(board, chess.BLACK):
        paint_square(chess.bb2str(chess.get_king(printed_board, chess.BLACK)), RED_CHECK)
    
    #각 체스말을 나타내기 위한 반복문 -> 체스말 이미지를 보드의 해당 위치에 나타냄
    for position in chess.colored_piece_gen(printed_board, chess.KING, chess.BLACK):
        SCREEN.blit(pygame.transform.scale(BLACK_KING,   (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.QUEEN, chess.BLACK):
        SCREEN.blit(pygame.transform.scale(BLACK_QUEEN,  (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.ROOK, chess.BLACK):
        SCREEN.blit(pygame.transform.scale(BLACK_ROOK,   (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.BISHOP, chess.BLACK):
        SCREEN.blit(pygame.transform.scale(BLACK_BISHOP, (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.KNIGHT, chess.BLACK):
        SCREEN.blit(pygame.transform.scale(BLACK_KNIGHT, (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.PAWN, chess.BLACK):
        SCREEN.blit(pygame.transform.scale(BLACK_PAWN,   (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.JOKER, chess.BLACK):
        SCREEN.blit(pygame.transform.scale(BLACK_JOKER,  (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
        
    for position in chess.colored_piece_gen(printed_board, chess.KING, chess.WHITE):
        SCREEN.blit(pygame.transform.scale(WHITE_KING,   (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.QUEEN, chess.WHITE):
        SCREEN.blit(pygame.transform.scale(WHITE_QUEEN,  (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.ROOK, chess.WHITE):
        SCREEN.blit(pygame.transform.scale(WHITE_ROOK,   (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.BISHOP, chess.WHITE):
        SCREEN.blit(pygame.transform.scale(WHITE_BISHOP, (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.KNIGHT, chess.WHITE):
        SCREEN.blit(pygame.transform.scale(WHITE_KNIGHT, (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.PAWN, chess.WHITE):
        SCREEN.blit(pygame.transform.scale(WHITE_PAWN,   (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
    for position in chess.colored_piece_gen(printed_board, chess.JOKER, chess.WHITE):
        SCREEN.blit(pygame.transform.scale(WHITE_JOKER,  (SQUARE_SIDE,SQUARE_SIDE)), get_square_rect(chess.bb2str(position)))
        
    pygame.display.flip()
    
#게임 창의 제목을 설정하고 화면을 업데이트
def set_title(title):
    pygame.display.set_caption(title)
    pygame.display.flip()
    
#AI 수를 계산하여 실행하고, 보드를 업데이트, 새로운 게임 상태를 반환
def make_AI_move(game, color):
    set_title(SCREEN_TITLE + ' - Calculating move...')
    new_game = chess.make_move(game, chess.get_AI_move(game, AI_SEARCH_DEPTH))
    set_title(SCREEN_TITLE)
    print_board(new_game.board, color)
    return new_game


#플레이어가 시도한 수를 확인하여 규칙에 맞는 수인지 검토, 규칙에 맞다면 게임 상태를 업데이트
def try_move(game, attempted_move):
    for move in chess.legal_moves(game, game.to_move):
        if move == attempted_move:
            game = chess.make_move(game, move)
    return game

def play_as(game, color):
    run = True  #게임 루프를 계속 실행할지 여부 결정
    ongoing = True  # 게임이 진행 중인지 여부를 나타냄
    joker = 0   #조커 사용 횟수를 추적
    
    #게임 루프 
    try:
        while run:
            CLOCK.tick(CLOCK_TICK)  #프레임 속도 유지
            print_board(game.board, color)  #현재 보드 상태를 화면에 출력
            
            #게임 종료 확인 -> 종료되면 제목에 결과를 표시
            if chess.game_ended(game):
                set_title(SCREEN_TITLE + ' - ' + chess.get_outcome(game))
                ongoing = False
            
            #AI 차례 처리
            if ongoing and game.to_move == chess.opposing_color(color):
                game = make_AI_move(game, color)
            
            if chess.game_ended(game):
                set_title(SCREEN_TITLE + ' - ' + chess.get_outcome(game))
                ongoing = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   #종료 이벤트
                    run = False
                
                #마우스 이벤트
                if event.type == pygame.MOUSEBUTTONDOWN:
                    leaving_square = coord2str(event.pos, color)
                    
                if event.type == pygame.MOUSEBUTTONUP:
                    arriving_square = coord2str(event.pos, color)
                    
                    if ongoing and game.to_move == color:
                        move = (chess.str2bb(leaving_square), chess.str2bb(arriving_square))
                        game = try_move(game, move)
                        print_board(game.board, color)
                
                #키보드 이벤트
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == 113:
                        run = False
                    if event.key == 104 and ongoing: # H key
                        game = make_AI_move(game, color)
                    if event.key == 117: # U key
                        game = chess.unmake_move(game)
                        game = chess.unmake_move(game)
                        set_title(SCREEN_TITLE)
                        print_board(game.board, color)
                        ongoing = True
                    if event.key == 99: # C key
                        global BOARD_COLOR
                        new_colors = deepcopy(BOARD_COLORS)
                        new_colors.remove(BOARD_COLOR)
                        BOARD_COLOR = choice(new_colors)
                        print_board(game.board, color)
                    if event.key == 112 or event.key == 100: # P or D key
                        print(game.get_move_list() + '\n')
                        print('\n'.join(game.position_history))
                    if event.key == 101: # E key
                        print('eval = ' + str(chess.evaluate_game(game)/100))
                    if event.key == 106: # J key
                        joker += 1
                        if joker == 13 and chess.get_queen(game.board, color):
                            queen_index = chess.bb2index(chess.get_queen(game.board, color))
                            game.board[queen_index] = color|chess.JOKER
                            print_board(game.board, color)
                
                #화면 크기 조정 이벤트
                if event.type == pygame.VIDEORESIZE:
                    if SCREEN.get_height() != event.h:
                        resize_screen(int(event.h/8.0))
                    elif SCREEN.get_width() != event.w:
                        resize_screen(int(event.w/8.0))
                    print_board(game.board, color)
                    
    #예외 처리
    except:
        print(format_exc(), file=stderr)
        bug_file = open('bug_report.txt', 'a')
        bug_file.write('----- ' + strftime('%x %X') + ' -----\n')
        bug_file.write(format_exc())
        bug_file.write('\nPlaying as WHITE:\n\t' if color == chess.WHITE else '\nPlaying as BLACK:\n\t')
        bug_file.write(game.get_move_list() + '\n\t')
        bug_file.write('\n\t'.join(game.position_history))
        bug_file.write('\n-----------------------------\n\n')
        bug_file.close()

#백색 플레이어로 체스 게임을 시작
def play_as_white(game=chess.Game()):
    print('Playing as white!')
    while True:
        print_board(game.board)
        if game_ended(game):
            break
        
        move_str = input('Enter your move: ')
        move = parse_move_code(game, move_str)
        
        if move:
            game = make_move(game, move)
            ai_move_str = send_move_to_server(move_str)
            if ai_move_str == 'GAME_OVER':
                print_outcome(game)
                break
            ai_move = [str2bb(ai_move_str[:2]), str2bb(ai_move_str[2:])]
            game = make_move(game, ai_move)
        else:
            print('Invalid move!')
        
        print_board(game.board)
        if game_ended(game):
            break
    print_outcome(game)

#흑색 플레이어로 체스 게임을 시작
def play_as_black(game=chess.Game()):
    print('Playing as black!')
    while True:
        print_rotated_board(game.board)
        if game_ended(game):
            break
        
        ai_move_str = send_move_to_server('AI_MOVE')
        if ai_move_str == 'GAME_OVER':
            print_outcome(game)
            break
        ai_move = [str2bb(ai_move_str[:2]), str2bb(ai_move_str[2:])]
        game = make_move(game, ai_move)
        
        print_rotated_board(game.board)
        if game_ended(game):
            break
        
        move_str = input('Enter your move: ')
        move = parse_move_code(game, move_str)
        
        if move:
            game = make_move(game, move)
        else:
            print('Invalid move!')
            continue

    print_outcome(game)

#랜덤한 색상으로 체스 게임을 시작
def play_random_color(game=chess.Game()):
    color = choice([chess.WHITE, chess.BLACK])
    play_as(game, color)

# chess.verbose = True
play_random_color() #게임시작 -> 호출 시 랜덤한 색상으로 게임을 시작

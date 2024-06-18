import socket
import threading
import pygame
from chess import Game, parse_move_code, game_ended, print_outcome, make_move, move2str, str2bb
from gui import print_board, print_rotated_board, resize_screen
# 서버의 IP 주소와 포트 설정
HOST = '192.168.0.16'  # 서버의 로컬 IP 주소
PORT = 65432

game = Game()  # 전역 변수로 선언
#서버로 이동 문자열을 전송하고 서버로부터 AI의 이동을 수신하는 함수
def send_move_to_server(move_str):
    global s
    s.sendall(move_str.encode('utf-8'))
    data = s.recv(1024) # 서버로부터 응답 수신
    return data.decode('utf-8')
#Pygame을 사용하여 GUI를 표시하고 사용자 입력을 처리하는 함수
def handle_gui():
    pygame.init()   #Pygame 초기화
    resize_screen(60)  # 각 체스 칸의 크기를 60 픽셀로 설정
    clock = pygame.time.Clock() # FPS 설정을 위한 시계 객체 생성

    while True:
        clock.tick(30)  # 30 FPS로 설정
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()    #마우스 클릭 위치 얻기
                square = coord2str(pos)         #클릭 위치를 체스 보드 위치로 변환
                global leaving_square           
                leaving_square = square         #출발 위치 저장
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()        #마우스 버튼을 놓은 위치 얻기
                square = coord2str(pos)             #놓은 위치 체스 보드 위치로 변환
                arriving_square = square        #도착 위치 저장
                move_str = leaving_square + arriving_square
                move = parse_move_code(game, move_str)
                if move:
                    game = make_move(game, move)    #이동이 유효하면 게임 상태 업데이트
                    ai_move_str = send_move_to_server(move_str) #이동을 서버로 전송하고 AI의 이동 수신
                    if ai_move_str == 'GAME_OVER':
                        print_outcome(game)
                        break
                    ai_move = [str2bb(ai_move_str[:2]), str2bb(ai_move_str[2:])]    #AI 이동 파싱
                    game = make_move(game, ai_move) #게임 상태 업데이트
                else:
                    print('Invalid move!')

        print_board(game.board) #체스 보드 출력
        pygame.display.flip()   #디스플레이 업데이트
#서버에 연결하고 GUI를 실행하는 함수
def start_client():
    global s
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT)) #서버에 연결 시도
            print('Connected to the server.')

            gui_thread = threading.Thread(target=handle_gui)    #GUI를 처리할 스레드 생성
            gui_thread.start()  #스레드 시작
            gui_thread.join()   #스레드가 종료될 때까지 대기
    except ConnectionRefusedError:
        print("Could not connect to the server. Please ensure the server is running and try again.")
        
if __name__ == "__main__":
    start_client()

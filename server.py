import socket
import threading
#라브러리를 가져옴 TCP Socket 통신 및 스레딩을 처리
from chess import Game, make_move, get_AI_move, game_ended, print_outcome
#chess 모듈에서 여러 함수와 클래스를 가져옴
HOST = '0.0.0.0'    #모든 네트워크 인터페이스에서 연결을 수락하도록 설정
PORT = 65432        #사용할 포트 설정
# 전역 변수로 게임 상태를 저장할 Game 객체 생성
game = Game()       

"""
클라이언트와의 통신을 처리하는 함수.
클라이언트로부터 체스 이동을 수신하고 AI의 응답을 전송함.
"""
def handle_client(conn, addr):          #conn : 클라이언트와의 연결 소켓    addr: 클라이언트의 주소
    global game
    print(f'Connected by {addr}')
    
    while True:
        data = conn.recv(1024)   # 클라이언트로부터 데이터를 수신
        if not data:
            break   # 데이터가 없으면 연결 종료
        
        move_str = data.decode('utf-8')
        move = parse_move_code(game, move_str)  # 체스 이동 문자열을 이동 객체로 파싱
        
        if move:        # 이동이 유효하면 게임 상태 업데이트
            game = make_move(game, move)
            print(f'Player move: {move_str}')    # 플레이어의 이동 출력
        # 게임 종료 여부 확인
        if game_ended(game):
            print_outcome(game)
            conn.sendall(b'GAME_OVER')
            break
        # AI의 이동 계산
        ai_move = get_AI_move(game)
        game = make_move(game, ai_move) # 게임 상태 업데이트
        ai_move_str = move2str(ai_move) # AI 이동을 문자열로 변환
        print(f'AI move: {ai_move_str}')    # AI의 이동 출력
         # AI의 이동을 클라이언트에 전송
        conn.sendall(ai_move_str.encode('utf-8'))
        
        if game_ended(game):
            print_outcome(game)
            conn.sendall(b'GAME_OVER')
            break

    conn.close()    # 클라이언트와의 연결 종료
    
"""
서버 소켓을 설정하고 클라이언트 연결을 대기하는 함수.
클라이언트 연결이 수락되면 handle_client 함수에서 처리.
"""
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print('Server started, waiting for connection...')
        
        while True:
            # 클라이언트의 연결 요청을 수락
            conn, addr = s.accept()
            # 새 스레드를 생성하여 클라이언트와의 통신을 처리
            client_handler = threading.Thread(target=handle_client, args=(conn, addr))
            client_handler.start()

if __name__ == "__main__":
    start_server()

import socket
from email.parser import Parser
from functools import lru_cache


def parse_request(request):
    """Парсинг HTTP запроса"""
    lines = request.split('\r\n')
    method, path, version = lines[0].split(' ')
    headers = {}

    for line in lines[1:]:
        if not line:
            break
        key, value = line.split(': ', 1)
        headers[key] = value

    return method, path, version, headers


@lru_cache
def read_html_file(filename):
    """Чтение HTML файла с кэшированием"""
    try:
        with open(f'templates/{filename}', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def handle_request(client_socket):
    """Обработка входящего запроса"""
    request_data = client_socket.recv(1024).decode('utf-8')

    if not request_data:
        return

    method, path, version, headers = parse_request(request_data)

    print(f"Received {method} request for {path}")

    # Для любого GET запроса возвращаем contacts.html
    if method == 'GET':
        content = read_html_file('contacts.html')
        if content:
            response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: {len(content)}
Connection: close

{content}"""
        else:
            response = "HTTP/1.1 404 Not Found\n\nFile not found"

    # Обработка POST запроса (дополнительное задание)
    elif method == 'POST':
        # Извлекаем тело запроса
        body = request_data.split('\r\n\r\n')[1] if '\r\n\r\n' in request_data else ''
        print(f"POST данные от пользователя: {body}")

        content = read_html_file('contacts.html')
        response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: {len(content)}
Connection: close

{content}"""

    else:
        response = "HTTP/1.1 405 Method Not Allowed\n\nMethod not allowed"

    client_socket.send(response.encode('utf-8'))
    client_socket.close()


def start_server(host='localhost', port=8000):
    """Запуск сервера"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Сервер запущен на http://{host}:{port}")
    print("Для остановки сервера нажмите Ctrl+C")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Подключение от {addr}")
            handle_request(client_socket)
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()
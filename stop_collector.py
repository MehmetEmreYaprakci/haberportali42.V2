"""Stops the current news collection loop, leaving the Streamlit UI running."""
import socket
try:
    with socket.create_connection(('127.0.0.1',48542),timeout=2) as sock:
        sock.sendall(b'STOP\n')
    print('Otomatik toplayiciya dur komutu gonderildi.')
except OSError:
    print('Calisan bir otomatik toplayici bulunamadi.')

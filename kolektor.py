"""RSS worker: one local instance, checks sources every 300 seconds."""
import socket
import time
import traceback
from datetime import datetime
from haber_radari import init_db, collect_news, APP_DIR

LOG_DIR=APP_DIR/'logs'
LOG_DIR.mkdir(exist_ok=True)

def log(message):
    line=f'{datetime.now():%Y-%m-%d %H:%M:%S} | {message}'
    print(line,flush=True)
    with (LOG_DIR/'collector.log').open('a',encoding='utf-8') as f:
        f.write(line+'\n')


def main():
    guard=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        guard.bind(('127.0.0.1',48542))
        guard.listen(1)
    except OSError:
        log('Toplayici zaten calisiyor. Ikinci kopya baslatilmadi.')
        return
    init_db()
    log('Otomatik toplayici basladi. Kontrol: 300 saniyede bir.')
    try:
        while True:
            started=time.monotonic()
            try:
                added,errors=collect_news(force=False)
                log(f'Kontrol: yeni haber={added}, sorunlu kaynak={len(errors)}')
                for msg in errors[:40]:
                    log('UYARI: '+msg)
            except Exception:
                log('HATA: '+traceback.format_exc())
            delay=max(5,300-(time.monotonic()-started))
            deadline=time.monotonic()+delay
            while time.monotonic()<deadline:
                guard.settimeout(min(5,max(0.1,deadline-time.monotonic())))
                try:
                    conn,_=guard.accept()
                except socket.timeout:
                    continue
                with conn:
                    if conn.recv(64).strip()==b'STOP':
                        log('Otomatik toplayici kullanici istegiyle durduruldu.')
                        return
    finally:
        guard.close()

if __name__=='__main__':
    main()

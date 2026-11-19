import json
import time
import httpx

TV_URL = "https://lichess.org/api/tv/feed"
HEADERS = {"User-Agent": "chess-live-estudo/0.1 (github.com/Almeida-Adriel)"}
TIMEOUT = httpx.Timeout(10.0, read=60.0)   # 10s pra conectar, 60s sem dados = morto
MAX_BACKOFF = 60


def stream_tv():
    """Gera os eventos da TV para sempre, reconectando se cair."""
    backoff = 1
    while True:
        try:
            with httpx.stream("GET", TV_URL, headers=HEADERS, timeout=TIMEOUT) as resp:
                if resp.status_code == 429:
                    print("429 — esperando 60s (regra do Lichess)")
                    time.sleep(60)
                    continue

                resp.raise_for_status()
                backoff = 1

                for line in resp.iter_lines():

                    if not line.strip():       # keep-alive
                        continue

                    try:
                        yield json.loads(line)

                    except json.JSONDecodeError:
                        print(f"linha inválida ignorada: {line[:80]!r}")

        except httpx.HTTPError as e:
            print(f"conexão caiu ({e!r}), reconectando em {backoff}s")
            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)


if __name__ == "__main__":
    for event in stream_tv():
        print(event, flush=True)
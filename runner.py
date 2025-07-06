import os

import uvicorn

if __name__ == "__main__":
    host = "127.0.0.1" if os.getenv("GRAHAWS") else "0.0.0.0"  # noqa: S104 # acceptable
    conf = uvicorn.Config("src:app", host=host, port=8032, workers=5, proxy_headers=True, forwarded_allow_ips="*")
    server = uvicorn.Server(conf)

    server.run()

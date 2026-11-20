"""main.py — entrypoint for news-image-20261120 (v3 blind rebuild).

Runs the deterministic renderer and writes entry.png (1024x1024).
No network access. Run: python3 main.py
"""
import hashlib

from render import compose


def main():
    compose("entry.png")
    data = open("entry.png", "rb").read()
    print(len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()

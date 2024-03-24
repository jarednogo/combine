import sgf
import sys

if __name__ == "__main__":
    if not sys.argv[1:]:
        sys.exit(f"Usage: {sys.argv[0]} [file]")

    with open(sys.argv[1]) as f:
        data = f.read()

    p = sgf.Parser(data)
    e = p.parse()
    if e.type == "error":
        sys.exit(e.value)

    print(e.create_sgf())

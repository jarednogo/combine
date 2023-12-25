import sys
import sgf

# steps
# 1. reduce games to main branch <-- done
# 2. combine games into one tree <-- done, i think?
# 3. note players (and date) at the earliest unique branch

class Node:
    def __init__(self, move, comment=""):
        self.move = move
        self.children = []
        self.parent = None
        self.comment = comment

    def __str__(self):
        return self.move + self.comment

def create_sgf(root):
    sgf_text = '''
(;GM[1]FF[4]CA[UTF-8]AP[CGoban:3]ST[2]
RU[Japanese]SZ[19]KM[6.50]TM[1800]OT[3x30 byo-yomi]
PW[White]PB[Black]'''

    stack = [root]
    while stack:
        cur = stack.pop()
        if cur in {"(", ")"}:
            sgf_text += cur
            continue

        sgf_text += cur.move
        if cur.comment:
            sgf_text += f"C[{cur.comment}]"
        if len(cur.children) == 1:
            stack += cur.children
        else:
            for ch in cur.children:
                stack.append(")")
                stack.append(ch)
                stack.append("(")
    sgf_text += ")"
    return sgf_text

def parse_sgf(data):
    l = 50
    p = sgf.Parser(data)
    result = p.parse()
    if result.type == "error":
        return
    root = result.value
    pw = root.fields["PW"][0]
    pb = root.fields["PB"][0]

    moves = []
    cur = root
    while len(moves) < 50:
        if cur.value == None and cur.down:
            cur = cur.down[0]
        elif not cur.down:
            break
        c = "B"
        if cur.color == 2:
            c = "W"
        moves.append(";" + c + "[" + sgf.coord2letters(cur.value) + "]")
        if cur.down:
            cur = cur.down[0]
        else:
            break
    return moves, pb, pw

def fix_comments(root, truncate=False):
    stack = [root]
    while stack:
        cur = stack.pop()
        stack += cur.children
        if cur.comment:
            comment = cur.comment
            cur.comment = ""
            while cur.parent and len(cur.parent.children) < 2:
                cur = cur.parent
            cur.comment = comment
            
            # choose to truncate everything below comments
            if truncate:
                cur.children = []

def ingest(games, filename):
    root = Node("")
    cur = root
    for moves, pb, pw, base in games:
        for move in moves:
            for ch in cur.children:
                if ch.move == move:
                    cur = ch
                    break
            else:
                node = Node(move)
                node.parent = cur
                cur.children.append(node)
                cur = node
        cur.comment = f"Black: {pb}, White: {pw}, {base}"
        cur = root

    fix_comments(root)

    sgf_text = create_sgf(root)
    with open(filename, "w") as f:
        f.write(sgf_text)

if __name__ == "__main__":
    b_games = []
    w_games = []
    games = []
    for fname in sys.argv[1:]:
        with open(fname) as f:
            data = f.read()
        base = fname.split("/")[-1]
        moves, pb, pw = parse_sgf(data)
        # truncate to 50 moves
        moves = moves[:50]
        game = (moves, pb, pw, base)
        if pb.lower() == "jarstar":
            b_games.append(game)
        else:
            w_games.append(game)
        games.append(game)


    ingest(games, "output.sgf")
    ingest(b_games, "black.sgf")
    ingest(w_games, "white.sgf")



class Node:
    def __init__(self, value, captured, color, up, labels, triangles, fields):
        self.value = value
        self.captured = captured
        self.color = color
        self.down = []
        self.up = up
        self.labels = labels
        self.triangles = triangles
        self.fields = fields

    def __str__(self):
        return f"(value={self.value}, captured={self.captured}, color={self.color}, down={self.down}, up={self.up}, labels={self.labels}, triangles={self.triangles}, fields={self.fields})"

    def __repr__(self):
        return self.__str__()

class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()


class Expr:
    def __init__(self, typ, value):
        self.type = typ
        self.value = value

def iswhitespace(c):
    return c == "\n" or c == " " or c == "\t" or c == "\r"

def letters2coord(s):
    if len(s) != 2:
        return None
    a = s[0].lower()
    b = s[1].lower()
    x = ord(a) - 97;
    y = ord(b) - 97;
    return Coord(x,y);

def coord2letters(c):
    a = chr(c.x + 97).lower()
    b = chr(c.y + 97).lower()
    return a+b

class Parser:
    def __init__(self, text):
        self.text = text
        self.index = 0

    def parse(self):
        self.skip_whitespace()
        c = self.read()
        if c == "(":
            return self.parse_branch()
        else:
            return Expr("error", "unexpected " + c)

    def skip_whitespace(self):
        while 1:
            if iswhitespace(self.peek(0)):
                self.read()
            else:
                break
        return Expr("whitespace", "")

    def parse_key(self):
        s = ""
        while 1:
            c = self.peek(0)
            if c == "\0":
                return Expr("error", "bad key")
            elif c < "A" or c > "Z":
                break
            s += self.read()
        return Expr("key", s)

    def parse_field(self):
        s = ""
        while 1:
            t = self.read()
            if t == "\0":
                return Expr("error", "bad field")
            elif t == "]":
                break
            elif t == "\\" and self.peek(0) == "]":
                t = self.read()
            s += t
        return Expr("field", s)

    def parse_nodes(self):
        n = self.parse_node()
        if n.type == "error":
            return n
        root = n.value
        cur = root
        while 1:
            c = self.peek(0)
            if c == ";":
                self.read()
                m = self.parse_node()
                if m.type == "error":
                    return m
                nxt = m.value
                cur.down.append(nxt)
                cur = nxt
            else:
                break
        return Expr("nodes", [root, cur])

    def parse_node(self):
        fields = {}
        labels = {}
        triangles = []
        color = 0
        move = ""
        while 1:
            self.skip_whitespace()
            c = self.peek(0)
            if c == "(" or c == ";" or c == ")":
                break
            if c < "A" or c > "Z":
                return Expr("error", "bad node (expected key)" + c)
            result = self.parse_key()
            if result.type == "error":
                return result
            key = result.value

            multifield = []
            self.skip_whitespace()
            if self.read() != "[":
                return Expr("error", "bad node (expected field) " + self.read())
            result = self.parse_field()
            if result.type == "error":
                return result
            multifield.append(result.value)

            while 1:
                self.skip_whitespace()
                if self.peek(0) == "[":
                    self.read()
                    result = self.parse_field()
                    if result.type == "error":
                        return result
                    multifield.append(result.value)
                else:
                    break

            self.skip_whitespace()
            if key == "TR":
                for f in multifield:
                    triangles.append(f)
            elif key == "LB":
                for f in multifield:
                    spl = f.split(":")
                    if len(spl) != 2:
                        print("label error: " + f)
                    labels[spl[0]] = spl[1]
            elif key == "B":
                color = 1
                move = multifield[0]
            elif key == "W":
                color = 2
                move = multifield[0]
            else:
                fields[key] = multifield
        v = letters2coord(move)
        n = Node(v, [], color, None, labels, triangles, fields)
        return Expr("node", n)

    def parse_branch(self):
        root = None
        current = None
        while 1:
            c = self.read()
            if c == "\0":
                return Expr("error", "unfinished branch, expected ')'")
            elif c == ";":
                result = self.parse_nodes()
                if result.type == "error":
                    return result
                node = result.value[0]
                cur = result.value[1]
                if root == None:
                    root = node
                    current = cur
                else:
                    current.down.append(node)
                    current = cur
            elif c == "(":
                result = self.parse_branch()
                if result.type == "error":
                    return result
                new_branch = result.value
                if root == None:
                    root = new_branch
                    current = new_branch
                else:
                    current.down.append(new_branch)
            elif c == ")":
                break
        return Expr("branch", root)

    def read(self):
        if self.index >= len(self.text):
            return "\0"
        result = self.text[self.index]
        self.index+=1
        return result

    def unread(self):
        if self.index == 0:
            return
        self.index-=1

    def peek(self, n):
        if self.index+n >= len(self.text):
            return "\0"
        return self.text[self.index+n]


def test():
    data = '''(;GM[1]FF[4]CA[UTF-8]AP[CGoban:3]ST[2]
RU[Japanese]SZ[19]KM[6.50]
PW[ tony ]PB[jared ]
(;B[pd]
(;W[qf]
;B[nc]
(;W[qc]
;B[qd]C[comment [some comment\\]])
(;W[qd]
;B[qc]
;W[rc]TR[qd]
;B[qe]
;
;W[rd]
;B[pe]))
(;W[qc]
;B[qd]
;W[pc]TR[qc][pd][qd]
;B[od]LB[pc:D][qc:B][pd:A][qd:C])
(;W[oc]
;B[pc]
;W[mc]))
(;B[qg]))'''

    p = Parser(data)
    result = p.parse()
    if result.type == "error":
        print(result)
        return
    print(result.value)
    return result.value

if __name__ == '__main__':
    test()

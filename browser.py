
import tkinter

from url import URL

WIDTH, HEIGHT = 800, 600
DEFAULT_URL = "file:///home/retcherj/simplebrowser/localFileTest.txt"
ENTITIES = {
    "&gt;": ">",
    "&lt;": "<"
}
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)

    def load(self, url):
        if url.scheme in ["http", "https"]:
            body = url.request()
        elif url.scheme == "file":
            body = url.openFile()
        elif url.scheme == "data":
            body = url.inlineHtml
        else:
            raise Exception(f"Unsupported scheme: {url.scheme}")
        

        text = body if url.viewing_source else lex(body)
        self.display_list = layout(text)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        if c == "\n":
            cursor_x = HSTEP
            cursor_y += VSTEP * 1.2
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list

def lex(body):
    in_tag = False
    i = 0
    text = ""
    while i < len(body):
        c = body[i]
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif c == "&":
            entity = ""
            while c != ";":
                entity += c
                i += 1
                c = body[i]
            entity += c
            
            if(entity in ENTITIES):
                text += ENTITIES[entity]
            else:
                text += entity
                
        elif not in_tag:
            text += c

        i += 1
    return text

if __name__ == "__main__":
    import sys

    url = DEFAULT_URL if len(sys.argv) == 1 else sys.argv[1]
    Browser().load(URL(url))
    tkinter.mainloop()
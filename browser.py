
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
        self.canvas.pack(fill="both", expand=1)

        self.scroll = 0

        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<MouseWheel>", self.mousescroll)
        self.window.bind("<Configure>", self.resizewindow)

    def load(self, url):
        if url.scheme in ["http", "https"]:
            body = url.request()
        elif url.scheme == "file":
            body = url.openFile()
        elif url.scheme == "data":
            body = url.inlineHtml
        else:
            raise Exception(f"Unsupported scheme: {url.scheme}")
        

        self.text = body if url.viewing_source else lex(body)
        self.display_list = layout(self.text)
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)
            last_item_drawn_height = y

        x, y, c = self.display_list[-1]
        max_page_height = (y + VSTEP)

        if max_page_height > HEIGHT:
            y2 = HEIGHT * last_item_drawn_height / max_page_height
            scrollbar_scale = HEIGHT / max_page_height
            scrollbar_height = HEIGHT * scrollbar_scale
            y1 = y2 - scrollbar_height
            self.canvas.create_rectangle(WIDTH-10, y1, WIDTH, y2, fill="lightblue")

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        last_scroll_item = self.display_list[-1]
        x, y, c = last_scroll_item
        if y + VSTEP - self.scroll < HEIGHT:
            self.scroll = y + VSTEP - HEIGHT
        
        self.draw()

    def scrollup(self, e):
        self.scroll = self.scroll - SCROLL_STEP
        if self.scroll - SCROLL_STEP < 0:
            self.scroll = 0
        self.draw()

    def mousescroll(self, e):
        self.scroll += -1 * e.delta
        if(self.scroll < 0):
            self.scroll = 0
        last_scroll_item = self.display_list[-1]
        x, y, c = last_scroll_item
        if y + VSTEP - self.scroll <= HEIGHT:
            self.scroll = y + VSTEP - HEIGHT
        self.draw()

    def resizewindow(self, e):
        global WIDTH, HEIGHT
        if e.width != WIDTH or e.height != HEIGHT:
            WIDTH, HEIGHT = e.width, e.height
            self.display_list = layout(self.text)
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
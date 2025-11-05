import socket
import ssl

DEFAULT_URL = "file:///home/retcherj/simplebrowser/localFileTest.txt"
SCHEMES = ["http", "https", "file", "data", "view-source"]
ENTITIES = {
    "&gt;": ">",
    "&lt;": "<"
}

class URL:
    def __init__(self, url):
        self.viewing_source = False

        self.scheme, url = url.split(":", 1)
        assert self.scheme in SCHEMES

        if self.scheme in ["data"]:
            self.contentType, self.inlineHtml = url.split(",", 1)

        else:
            if self.scheme == "view-source":
                self.viewing_source = True
                self.scheme, url = url.split("://", 1)
            else:
                url = url[2:] # file path would have :// originally

            if "/" not in url:
                url = url + "/"

            if self.scheme in ["http", "https"]:
                if self.scheme == "http":
                    self.port = 80
                elif self.scheme == "https":
                    self.port = 443

                self.host, url = url.split("/", 1)

                if ":" in self.host:
                    self.host, port = self.host.split(":", 1)
                    self.port = int(port)

                self.path = "/" + url # adding back cause lost in split

            elif self.scheme == "file":
                self.path = url

    def request(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        # connect takes a single arg - diff fams have diff params
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        headers = [
            f"GET {self.path} HTTP/1.1",
            f"Host: {self.host}",
            f"Connection: close",
            f"User-Agent: python script",
            "\r\n"
        ]

        request = "\r\n".join(headers)

        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close()

        return content
    
    def openFile(self):
        with open(self.path) as f:
            return f.read()

def show(body):
    in_tag = False
    i = 0
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
                print(ENTITIES[entity], end="")
            else:
                print(entity, end="")
                
        elif not in_tag:
            print(c, end="")

        i += 1

def load(url):
    if url.scheme in ["http", "https"]:
        body = url.request()
    elif url.scheme == "file":
        body = url.openFile()
    elif url.scheme == "data":
        body = url.inlineHtml
    else:
        raise Exception(f"Unsupported scheme: {url.scheme}")
    
    if(url.viewing_source):
        print(body)
    else:
        show(body)

if __name__ == "__main__":
    import sys

    url = DEFAULT_URL if len(sys.argv) == 1 else sys.argv[1]
    load(URL(url))
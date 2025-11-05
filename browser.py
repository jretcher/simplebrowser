import socket
import ssl

DEFAULT_URL = "file:///home/retcherj/simplebrowser/localFileTest.txt"
SCHEMES = ["http", "https", "file"]

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in SCHEMES

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

            self.path = "/" + url

        elif self.scheme == "file":
            self.path = url

    def webRequest(self):
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
    
    def fileRequest(self):
        with open(self.path) as f:
            return f.read()
    
    def request(self):
        if self.scheme in ["http", "https"]:
            return self.webRequest()
        elif self.scheme == 'file':
            return self.fileRequest()
        else:
            raise Exception(f"Unsupported scheme: {self.scheme}")

def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
    import sys

    url = DEFAULT_URL if len(sys.argv) == 1 else sys.argv[1]
    load(URL(url))
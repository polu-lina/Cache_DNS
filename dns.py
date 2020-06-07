import sys, requests, dnslib, socket, pickle, time

class DNS():

    def __init__(self):
        self.cache = {}
        self.request_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.request_socket.bind(('localhost', 53))
        self.request_socket.settimeout(1)
        self.receive_socket.settimeout(1)

    def make_request(self):
        try:
            data, address = self.request_socket.recvfrom(1024)
            if data:
                parse_data = dnslib.DNSRecord.parse(data)
                question = parse_data.questions[0]
                if question.qname in self.cache and question.qtype in cache[question.qname]:
                    info, ttl = self.cache[question.qname]
                    print('Info from cache:\t' + info)
                    parse_data.questions.remove(question)
                else:
                    server = ("8.8.8.8", 53)
                    self.receive_socket.sendto(parse_data.pack(), server)
        except OSError:
            pass

    def take_request(self):
        try:
            data, address = self.receive_socket.recvfrom(1024)
            current_time = int(time.time())
            if data:
                parse_data = dnslib.DNSRecord.parse(data)
                print(parse_data)
                for question in parse_data.rr:
                    self.cache[question.rname]= (parse_data, current_time + question.ttl)
        except OSError:
            pass

    def process(self):
        self.make_request()
        time.sleep(0.25)
        self.take_request()
        time.sleep(0.25)
        self.check_TTL()

    def check_TTL(self):
        for i in self.cache:
            _, ttl = self.cache[i]
            if ttl < int(time.time()):
                del self.cache[i]

    def upload_cache(self):
        with open('cache.txt', 'rb') as f:
            try:
                self.cache = pickle.load(f)
                self.check_TTL()
            except Exception:
                pass

    def test_send(self, address):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(dnslib.DNSRecord.question(address).pack(), ("localhost", 53))
        s.close()


if __name__ == '__main__':
    server = DNS()
    t = input("Выберите режим:\nclient - в режиме клиента, server - в режиме сервера\n")
    print("Server is running")
    server.upload_cache()
    try:
        if t == "test":
            while True:
                address = input("Введите адрес")
                server.test_send(str(address))
                server.process
        elif t == "server":
            while True:
                server.process
        else:
            print("Что-то пошло не так, попробуйте заново")
    except Exception as e:
        print(e)
    finally:
        server.request_socket.close()
        server.receive_socket.close()
        with open('cache.txt', 'wb') as f:
            pickle.dump(server.cache, f)
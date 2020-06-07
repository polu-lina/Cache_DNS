import sys, requests, dnslib, socket, pickle, time

class DNS():

    def __init__(self):
        self.cache = {}
        self.request = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.response = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.request.bind(('localhost', 53))
        self.request.settimeout(1)
        self.response.settimeout(1)


    def process(self):
        while True:
            try:
                data, address = self.request.recvfrom(512)
                if data:
                    parse_data = dnslib.DNSRecord.parse(data)
                    question = parse_data.questions[0]
                    if question.qname in self.cache and question.qtype in cache[question.qname]:
                        info, ttl = self.cache[question.qname]
                        print('Info from cache:\t' + info)
                        parse_data.questions.remove(question)
                    else:
                        server = ("8.8.4.4", 53)
                        self.response.sendto(parse_data.pack(), server)

                time.sleep(0.25)

                data, address = self.response.recvfrom(512)
                current_time = int(time.time())
                if data:
                    parse_data = dnslib.DNSRecord.parse(data)
                    print(parse_data)
                    for question in parse_data.rr:
                        self.cache[question.rname]= (parse_data, current_time + question.ttl)
            except OSError:
                pass
            time.sleep(0.25)
            self.update_cache()

    def update_cache(self):
        current_time = int(time.time())
        for i in self.cache:
            _, ttl = self.cache[i]
            if ttl < current_time:
                del self.cache[i]
                  


if __name__ == '__main__':
    server = DNS()
    server.run()
    try:
        with open('cache.txt', 'rb') as f:
                server.cache = pickle.load(f)
                server.update_cache()
    except Exception:
        pass
    print("Server is running")
    command = input("Введите 'stop', если хотите остановить сервер, введите 'check', если хотите протестировать его")
    try:
        while True:
            if command == "client":
                while True:
                    address = input("Введите адрес")
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(dnslib.DNSRecord.question(str(address)).pack(), ("localhost", 53))
                    s.close()
            elif command == "stop":
                break
            else:
                print("Вы ввели неправильную команду")
    except Exception as e:
        print(e)
    finally:
        server.request.close()
        server.response.close()
        with open('cache.txt', 'wb') as f:
            pickle.dump(server.cache, f)
            time.sleep(1)
        sys.exit(0)

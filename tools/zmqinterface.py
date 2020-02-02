import threading
import zmq

running = True
publisher = None
subscriber = None


def run():
    global subscriber
    global publisher

    print("connecting to zmq server")
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.connect("tcp://127.0.0.1:5557")
    publisher = context.socket(zmq.PUSH)
    publisher.connect("tcp://127.0.0.1:5558")
    print("connected to zmq server")

    t = threading.Thread(target=start_receiving_thread)
    t.setDaemon(True)
    t.start();

    while running:
        msg = input()
        publisher.send(msg.encode("utf-8"))


def start_receiving_thread():
    while running:
        msg = subscriber.recv()
        string = msg.decode("utf-8")
        print(string)


if __name__ == "__main__":
    run()

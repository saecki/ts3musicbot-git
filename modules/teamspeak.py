import json
import subprocess
import sys
import time
import ts3

import ts3musicbot as bot

from common.classes import FileSystem, JSONData
from common.constants import Commands, JSONFields, Prefixes
from modules import cli

api_key = ""
nickname = ""
server_address = ""
host = "localhost"
team_speak_path = ""

client_query = None
disconnected = True
last_description = None


def run():
    global client_query
    global disconnected

    print("starting teamspeak module")
    read_data()
    start_teamspeak_thread(team_speak_path)
    client_query = ClientQuery(host, api_key)

    if not disconnected:
        if client_query.is_connected():
            update_bot()
            bot.add_thread(target=start_checking_for_teamspeak_command, daemon=True)
            bot.add_thread(target=start_keeping_alive_client_query, daemon=True)
        elif len(server_address) > 0:
            if client_query.try_connecting(server_address):
                update_bot()
                bot.add_thread(target=start_checking_for_teamspeak_command, daemon=True)
                bot.add_thread(target=start_keeping_alive_client_query, daemon=True)
        else:
            print("connect to a teamspeak server first or set a server address in the config.json file")
            print("running without teamspeak interface")
    print("started teamspeak module")


def update():
    if not disconnected:
        update_description()


def report(string):
    if not disconnected:
        send_to_channel(string)


def read_data():
    global api_key
    global nickname
    global server_address
    global team_speak_path

    try:
        json_file = open(FileSystem.get_config_file_path())
        data = json.load(json_file)

        with JSONData.read(data, JSONFields.ApiKey) as json_field:
            api_key = json_field

        with JSONData.read(data, JSONFields.Nickname) as json_field:
            nickname = json_field

        with JSONData.read(data, JSONFields.ServerAddress) as json_field:
            server_address = json_field

        with JSONData.read(data, JSONFields.TeamSpeakPath) as json_field:
            team_speak_path = json_field

        return True

    except:
        print("couldn't read config file")
        print("trying to create a ts3 clientquery config file")
        try:
            json_file = open(FileSystem.get_config_file_path(), "w")
            data = {
                JSONFields.ApiKey: "<YOURAPIKEY>",
                JSONFields.Nickname: "Musicbot",
                JSONFields.ServerAddress: "",
                JSONFields.TeamSpeakPath: ""
            }

            json.dump(data, json_file, indent=4)

            print(
                "created a config.json file in " + FileSystem.get_data_folder_path() +
                "you'll have to enter a ts3clientquery api key which can be found in your teamspeak client at: "
                "tools - options - addons - clientquery - settings. optionally you can change the nickname and "
                "specify a default server address and a teamspeak path to automatically start teamspeak.")
        except FileExistsError:
            print("couldn't create config file")
    return False


def start_teamspeak_thread(team_speak_path):
    if len(team_speak_path) > 0:
        print("starting teamspeak in: " + team_speak_path)
        bot.start_new_thread(target=start_teamspeak, args=(team_speak_path,), daemon=True)
        for i in range(100):
            time.sleep(0.2)
            try:
                time.sleep(10)
            except:
                print("starting...")
            else:
                print("started teamspeak")
                return True
        print("starting teamspeak failed")
        return False


def start_teamspeak(team_speak_path):
    out = sys.stdout
    if bot.silent:
        out = open(FileSystem.get_log_file_path(), "a")

    subprocess.call(team_speak_path, shell=True, stdout=out, stderr=out)


def start_checking_for_teamspeak_command():
    if bot.silent:
        sys.stdout = open(FileSystem.get_log_file_path(), "a")
        sys.stderr = open(FileSystem.get_log_file_path(), "a")

    client_query.registerForTextEvents()

    while bot.running:
        string = client_query.listenForTextEvents()
        if string is not None:
            command = cli.parse_command(string)
            with bot.lock:
                cli.handle_command(command, prefix=Prefixes.TeamSpeak)


def start_keeping_alive_client_query():
    if bot.silent:
        sys.stdout = open(FileSystem.get_log_file_path(), "a")
        sys.stderr = open(FileSystem.get_log_file_path(), "a")

    while bot.running:
        time.sleep(200)
        with bot.clientQueryLock:
            client_query.sendKeepAlive()


def handle_teamspeak_command(event):
    try:
        msg = event[0]["msg"]
        startswithprefix = None
        for p in Prefixes.TeamSpeak:
            if msg.startswith(p):
                startswithprefix = p
                break

        if startswithprefix is not None:
            command = msg[len(startswithprefix):]
            if command in Commands.ComeOver:
                come_over(event)
            else:
                return False
            return True
    except Exception as e:
        print(e)
        return False


def update_bot():
    try:
        with bot.clientQueryLock:
            client_query.setNickname(nickname)
    except:
        pass


def update_description():
    global last_description

    msg = cli.get_playback_info()

    if not msg == last_description:
        with bot.clientQueryLock:
            client_query.set_description(msg)
        last_description = msg


def send_to_channel(string):
    with bot.clientQueryLock:
        client_query.send_message_to_current_channel(string)


def come_over(event):
    try:
        client_id = event[0]["invokerid"]
        with bot.clientQueryLock:
            channel_id = client_query.getChannelID(client_id)
            client_query.move_to_channel(channel_id)
    except Exception as e:
        print("couldn't come over")
        print(e)


class ClientQuery:

    def __init__(self, host, api_key):
        global disconnected

        self.host = host
        self.main_connection = ClientQuery.create_query(host, api_key)
        self.listening_connection = ClientQuery.create_query(host, api_key)

        if self.main_connection is None or self.listening_connection is None:
            print("most likely the teamspeak client isn't running or the clientquery apikey is wrong")
            print("running without teamspeak interface")
        else:
            disconnected = False

    @staticmethod
    def create_query(host, api_key):
        try:
            ts3conn = ts3.query.TS3ClientConnection(host)
            ts3conn.auth(apikey=api_key)
            ts3conn.use()
            return ts3conn
        except Exception as e:
            print("couldn't connect to teamspeak")
            print(e)
        return None

    #
    # connection
    #

    def try_connecting(self, address):
        print("connecting to " + address)
        self.connect(address)
        for i in range(50):
            time.sleep(0.2)
            if self.is_connected():
                print("connected to " + address)
                time.sleep(0.5)
                return True
            else:
                print("connecting...")
        print("connection failed")
        return False

    def connect(self, address):
        if len(address) > 0:
            try:
                server_info = None
                try:
                    server_info = self.main_connection.serverconnectinfo()
                except:
                    self.main_connection.send("connect", {"address": address})
                else:
                    if server_info[0]["ip"] != address:
                        self.main_connection.send("connect", {"address": address})
            except Exception as e:
                print("couldn't connect to " + address)
                raise e

    def is_connected(self):
        try:
            server_info = self.main_connection.serverconnectinfo()
            return True
        except:
            return False

    def move_to_channel(self, channel_id):
        try:
            client_id = self.get_client_id()
            self.main_connection.clientmove(cid=channel_id, clid=client_id)
        except Exception as e:
            print("couldn't move to channel with id " + channel_id)
            raise e

    def send_message_to_current_channel(self, message):
        try:
            channel_id = self.get_current_channel_id()
            self.main_connection.sendtextmessage(targetmode=2, target=channel_id, msg=message)
        except Exception as e:
            print("couldn't get channel id")
            raise e

    def send_keep_alive(self):
        self.main_connection.send_keepalive()

    def set_nickname(self, nickname):
        try:
            client_id = self.get_client_id()
            client_variables = self.main_connection.clientvariable(client_id, "client_nickname")
            client_nickname = client_variables[0]["client_nickname"]
            if nickname != client_nickname:
                self.main_connection.clientupdate(client_nickname=nickname)
        except Exception as e:
            print("couldn't update teamspeak nickname")
            raise e

    def set_description(self, description):
        try:
            client_database_id = self.get_database_client_id()
            self.main_connection.clientdbedit(cldbid=client_database_id, client_description=description)
        except Exception as e:
            print("couldn't update teamspeak description")
            raise e

    def get_client_id(self):
        try:
            client_info = self.main_connection.whoami()
            client_id = client_info[0]["clid"]
            return client_id
        except Exception as e:
            print("couldn't get client id")
            raise e

    def get_current_channel_id(self):
        try:
            client_info = self.main_connection.whoami()
            channel_id = client_info[0]["cid"]
            return channel_id
        except Exception as e:
            print("couldn't get current channel id")
            raise e

    def get_channel_id(self, client_id):
        try:
            clients = self.main_connection.clientlist()
            for c in clients:
                if c["clid"] == client_id:
                    return c["cid"]
        except Exception as e:
            print("couldn't get channel id")
            raise e
        return None

    def get_database_client_id(self):
        try:
            client_id = self.get_client_id()

            client_variables = self.main_connection.clientvariable(client_id, "client_database_id")
            client_database_id = client_variables[0]["client_database_id"]

            return client_database_id
        except Exception as e:
            print("couldn't get client database id")
            raise e
        return None

    #
    # eventlistening
    #

    def register_for_text_events(self):
        try:
            self.listening_connection.clientnotifyregister(event="notifytextmessage", schandlerid=1)
        except Exception as e:
            print("couldn't register for text events from the teamspeak client")
            raise e

    def listen_for_text_events(self, timeout=200):
        try:
            event = self.listening_connection.wait_for_event(timeout=timeout)
        except:
            self.listening_connection.send_keepalive()
        else:
            client_info = self.listening_connection.whoami()
            client_id = client_info[0]["clid"]
            invoker_id = event[0]["invokerid"]
            msg = event[0]["msg"]
            if bot.debug:
                print("received teamspeak message invokerid: " + invoker_id + " msg: " + msg)
                if not handle_teamspeak_command(event):
                    return msg
            elif invoker_id != client_id:
                if not handle_teamspeak_command(event):
                    return msg

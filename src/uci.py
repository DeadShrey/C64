import chess
import sys
from random import choice


class UCIEngine:
    def __init__(self):
        self.board = chess.Board()
        self.name = "C64v3"
        self.author = "Shrey"
        self.options = {
            "depth": {
                "type": "spin",
                "value": 1,     # Default value
                "min": 1,
                "max": 100
            }
        }
    
    def send(self, msg: str):
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()
    
    def read(self):
        return sys.stdin.readline()

    def run(self):
        while True:
            cmd = self.read().strip()
            if cmd: self.handle_cmd(cmd)
    
    def handle_cmd(self, cmd: str):
        parts = cmd.split(" ")

        if parts[0] == "uci":
            self.handle_uci()
        
        elif parts[0] == "isready":
            self.handle_ready()
        
        elif parts[0] == "ucinewgame":
            self.board.reset()
        
        elif parts[0] == "quit":
            sys.exit(0)
        
        elif parts[0] == "position":
            self.handle_pos(parts)
        
        elif parts[0] == "go":
            self.handle_go()
        
        elif parts[0] == "setoption":
            self.handle_options(parts)
    
    def handle_uci(self):
        self.send(f"id name {self.name}")
        self.send(f"id author {self.author}")

        # Sending options
        for option in self.options:
            _option = self.options[option]
            self.send(f"option name {option} type {_option['type']} default {_option['value']} min {_option['min']} max {_option['max']}")
        
        self.send("uciok")
    
    def handle_ready(self):
        self.send("readyok")
    
    def handle_pos(self, cmd: list):
        if "startpos" in cmd:
            fen = chess.STARTING_FEN
        
        elif "fen" in cmd:
            fen = " ".join(cmd[cmd.index("fen") + 1 : cmd.index("fen") + 7])
        
        self.board.set_fen(fen)
        if "moves" in cmd:
            for move in cmd[cmd.index("moves") + 1 : ]:
                self.board.push_uci(move)
        
    def handle_go(self):
        # Returning a random move as a placeholder
        if self.board.legal_moves.count() > 0:
            self.send(f"bestmove {choice(tuple(self.board.legal_moves))}")
        
        else:
            self.send("bestmove (none)")
    
    def handle_options(self, cmd: list):
        name = cmd[cmd.index("name") + 1]
        value = cmd[cmd.index("value") + 1]
        self.options[name]["value"] = (int(value) if value.isdigit() else value)


# Running the engine
UCIEngine().run()

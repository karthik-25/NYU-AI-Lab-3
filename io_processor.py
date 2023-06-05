import sys

class IO_Processor:
    def __init__(self):
        self.df = 1.0
        self.is_max = True
        self.tol = 0.001
        self.iter = 100
        self.input_file = None
        self.input_parse_fail_str = "Error: Input parsing failed."

    def parse_input(self, args):
        if len(args) < 1:
            print(self.input_parse_fail_str, "Invalid arguments. Sample command: python mdp.py -df .9 -tol 0.0001 some-input.txt")
            sys.exit()

        if "-df" in args:
            self.df = float(args[args.index("-df") + 1])

        if "-tol" in args:
            self.tolerance = float(args[args.index("-tol") + 1])

        if "-iter" in args:
            self.iter = int(args[args.index("-iter") + 1])

        if "-min" in args:
            self.is_max = False
        
        self.input_file = [arg for arg in args if ".txt" in arg][0]
        if not self.input_file:
            print(self.input_parse_fail_str, "Invalid input: input txt file not specified.")
            sys.exit()
import sys

from io_processor import IO_Processor
from graph import Graph

def main():
    iop = IO_Processor()
    iop.parse_input(sys.argv[1:])

    g = Graph(iop.df, iop.tol, iop.iter, iop.is_max)
    g.build_graph(iop.input_file)

    g.mdp_sovler()

if __name__ == "__main__":
    main()
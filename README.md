SCRIPTS
1. graph.py contains the code for Graph and GraphNode classes. It contains the logic for building a graph and and solving MDP (value iteration and greedy policy computation).

2. io_processor.py contains the code for IO_Processor class. It contains the logic for parsing
the user input via CLI.

3. mdp.py contains the main function and it is the script to run via CLI.

RUN SCRIPTS
Please run mdp.py as follows:
python3 mdp.py [-df] [df_value] [-min] [-tol] [tol_value] [-iter] [iter_value] input_filename

-df: Specify discount factor. Optional argument (Default = 1.0). Add flag followed by desired df_value.
-min: Toggle min. Optional argument (Default - solve for max value (rewards)). Add this flag to solve for min value (costs).
-tol: Tolerance for exiting value iteration. Optional argument (Default = 0.001). Add flag followed by desired tol_value.
-iter: Cutoff for value iteration. Optional argument (Default = 100). Add flag followed by desired iter_value.
input_filename: Input graph file. Must be a text file with ".txt" extension. Required argument.

SAMPLE COMMANDS
python3 mdp.py inputs/maze.txt
python3 mdp.py inputs/publisher.txt
python3 mdp.py -min inputs/restaurant.txt
python3 mdp.py inputs/student.txt
python3 mdp.py inputs/student2.txt
python3 mdp.py -df 0.9 inputs/cmu.txt

REFERENCES
- Lecture and class notes

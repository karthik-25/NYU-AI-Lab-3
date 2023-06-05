import sys

class GraphNode:
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.is_decision_node = False
        self.success_rate = None
        self.edges_dict = {}
        self.edges_list = None
        self.edges_prob_list = None

class Graph:
    def __init__(self, df, tol, iter, is_max):
        self.df = df
        self.tol = tol
        self.iter = iter
        self.is_max = is_max
        self.nodes = {}
        self.graph_build_fail_str = "Error: Graph build failed."
    
    def build_graph(self, input_file):
        with open(input_file, "r") as f:
            for line in f:
                if line == "\n" or "#" in line:
                    continue

                elif "=" in line:
                    self.process_value_line(line)

                elif "%" in line:
                    self.process_probability_line(line)

                elif ":" in line:
                    self.process_edge_line(line)

                else:
                    print(self.graph_build_fail_str, "Input line does not follow expected format: {0}".format(line))
                    sys.exit()

        self.process_edges_probabilities()

    def process_value_line(self, line):
        node_name = line.split("=")[0].strip()
        if node_name not in self.nodes:
            self.nodes[node_name] = GraphNode(node_name)
        self.nodes[node_name].value = int(line.split("=")[1].strip())

    def process_probability_line(self, line):
        node_name = line.split("%")[0].strip()
        prob_list = [float(p) for p in line.split("%")[1].strip().split()]

        if node_name not in self.nodes:
            self.nodes[node_name] = GraphNode(node_name)

        if len(prob_list) == 1:
            self.nodes[node_name].is_decision_node = True
            self.nodes[node_name].success_rate = prob_list[0]
        else:
            self.nodes[node_name].edges_prob_list = prob_list

    def process_edge_line(self, line):
        node_name = line.split(":")[0].strip()

        if node_name not in self.nodes:
            self.nodes[node_name] = GraphNode(node_name)

        self.nodes[node_name].edges_list = [e.strip() for e in line.split(":")[1].strip()[1:-1].split(",")]

        for edge in self.nodes[node_name].edges_list:
            if edge not in self.nodes:
                self.nodes[edge] = GraphNode(edge)

    def process_edges_probabilities(self):
        for node_name, node in self.nodes.items():
            # If a node has no edges it is terminal. A probability entry for such a node is an error.
            if not node.edges_list and (node.edges_prob_list or node.success_rate):
                print(self.graph_build_fail_str, "{0} has no edges (terminal node) but probability given".format(node_name))
                sys.exit()

            # If a node has edges but no probability entry, it is assumed to be a decision node with p=1
            if node.edges_list and not (node.edges_prob_list or node.success_rate):
                node.is_decision_node = True
                node.success_rate = 1.0

            # store edges in dict for decision nodes
            if node.is_decision_node:
                for edge in node.edges_list:
                    node.edges_dict[edge] = 0 # populated later when policy is set

            # store edges in dict with probabilities for non-decision nodes
            if not node.is_decision_node and node.edges_list and node.edges_prob_list:
                if len(node.edges_list) != len(node.edges_prob_list):
                    print(self.graph_build_fail_str, "Number of edges does not match number of probabilities for {0} | edge list: {1} | prob list: {2}".format(node_name, node.edge_list, node.prob_list))
                    sys.exit()

                if sum(node.edges_prob_list) != 1.0:
                    print(self.graph_build_fail_str, "Sum of probabilities for {0} is not 1.0 | edge list: {1} | prob list: {2}".format(node_name, node.edge_list, node.prob_list))
                    sys.exit()

                for i, edge in enumerate(node.edges_list):
                    node.edges_dict[edge] = node.edges_prob_list[i]

    def mdp_sovler(self):
        # set initial policy
        new_policy = {}
        for node_name, node in self.nodes.items():
            if node.is_decision_node:
                new_policy[node_name] = node.edges_list[0]

        # generate initial value function (dict)
        V = {}
        for node_name, node in self.nodes.items():
            V[node_name] = node.value

        cur_policy = None
        while new_policy != cur_policy:
            cur_policy = new_policy

            # update probabilities for edges in decision nodes based on policy
            self.update_decision_node_edges_probabilities(cur_policy)
            
            # value iteration
            V = self.value_iteration(V)

            # greedy policy computation
            new_policy = self.greedy_policy_computation(V)

        self.print_results(V, new_policy)
        
    def update_decision_node_edges_probabilities(self, policy):
        for node_src, node_dest in policy.items():
            self.nodes[node_src].edges_dict[node_dest] = self.nodes[node_src].success_rate
            num_remaining_edges = len(self.nodes[node_src].edges_dict) - 1
            if num_remaining_edges > 0:
                remaining_prob = (1 - self.nodes[node_src].success_rate) / num_remaining_edges
                for edge in self.nodes[node_src].edges_dict:
                    if edge != node_dest:
                        self.nodes[node_src].edges_dict[edge] = remaining_prob

    def greedy_policy_computation(self, V):
        policy = {}
        for node_name, node in self.nodes.items():
            if node.is_decision_node:
                possible_utilities = {}
                for edge in node.edges_list:
                    exp_edge_value = node.success_rate * V[edge]
                    remaining_edge_list = [e for e in node.edges_list if e != edge]
                    if remaining_edge_list:
                        fail_rate = (1 - node.success_rate)/len(remaining_edge_list)
                        for remaining_edge in remaining_edge_list:
                            exp_edge_value += fail_rate * V[remaining_edge]

                    possible_utilities[edge] = exp_edge_value

                if self.is_max:
                    policy[node_name] = max(possible_utilities, key=possible_utilities.get)
                else:
                    policy[node_name] = min(possible_utilities, key=possible_utilities.get)

        return policy

    def value_iteration(self, V):
        Vcur = V
        for i in range(self.iter):
            delta = 0
            Vnew = {}
            for node_name, node in self.nodes.items():
                R = node.value
                exp_edge_utility = 0
                for edge, prob in node.edges_dict.items():
                    exp_edge_utility += prob * Vcur[edge]

                Vnew[node_name] = R + (self.df * exp_edge_utility)

                delta = max(delta, abs(Vnew[node_name] - Vcur[node_name]))

            if delta < self.tol:
                break

            Vcur = Vnew

        return Vnew
    
    def print_results(self, V, policy):
        node_print_list = []
        for node_src, node_dest in policy.items():
            if len(self.nodes[node_src].edges_list) > 1:
                node_print_list.append("{0} -> {1}".format(node_src, node_dest))

        for line in sorted(node_print_list):
            print(line)

        print_list = []
        for node, value in V.items():
            print_list.append("{0}={1:.3f}".format(node, value))
        
        print("\n")
        print(*sorted(print_list))
            
    def print_graph(self):
        for node_name, node in self.nodes.items():
            print("{0} - {1} - {2} - {3} - {4}".format(node_name, node.value, node.edges_dict, "DN" if node.is_decision_node else "N", node.success_rate if node.is_decision_node else ""))



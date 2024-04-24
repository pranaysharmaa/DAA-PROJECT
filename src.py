import tkinter as tk
from tkinter import messagebox
import heapq
import math

class NetworkSimulator:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=600, height=400, bg="white")
        self.canvas.pack()

        # Nodes (computers)
        self.nodes = []

        # Switches
        self.switches = []

        # Connections
        self.connections = {}

        # Entry fields for node numbers
        self.node1_entry = tk.Entry(master)
        self.node1_entry.pack()
        self.node2_entry = tk.Entry(master)
        self.node2_entry.pack()

        self.canvas.bind("<Button-1>", self.create_node)
        self.create_switch_button = tk.Button(master, text="Create Switch", command=self.create_switch)
        self.create_switch_button.pack()
        self.connect_button = tk.Button(master, text="Connect", command=self.connect_components)
        self.connect_button.pack()
        self.shortest_path_button = tk.Button(master, text="Find Shortest Path", command=self.find_shortest_path)
        self.shortest_path_button.pack()

        # Initialize graph for Dijkstra's algorithm
        self.graph = {}
        self.node_counter = 0
        self.switch_counter = 0

        # Conversion factor for cost calculation (1 unit = 10k pixels)
        self.conversion_factor = 10

    def create_node(self, event):
        self.node_counter += 1
        node = self.canvas.create_oval(event.x - 10, event.y - 10, event.x + 10, event.y + 10, fill="blue")
        self.nodes.append(node)
        self.graph[node] = {}
        self.canvas.create_text(event.x, event.y, text=str(self.node_counter))

    def create_switch(self):
        self.switch_counter += 1
        switch = self.canvas.create_rectangle(100 + (self.switch_counter - 1) * 150, 150,
                                              150 + (self.switch_counter - 1) * 150, 200, fill="green")
        self.switches.append(switch)
        self.graph[switch] = {}
        self.canvas.create_text(125 + (self.switch_counter - 1) * 150, 175, text="Switch " + str(self.switch_counter))

    def connect_components(self):
        num_nodes = len(self.nodes)
        num_switches = len(self.switches)
        if num_nodes < 1 or num_switches < 1:
            messagebox.showwarning("Warning", "Insufficient components to connect.")
            return
        for i in range(len(self.switches) - 1):
            switch1 = self.switches[i]
            switch2 = self.switches[i + 1]
            connection = self.canvas.create_line(
                self.canvas.coords(switch1)[0] + 25, self.canvas.coords(switch1)[1] + 25,
                self.canvas.coords(switch2)[0] + 25, self.canvas.coords(switch2)[1] + 25,
                fill="black"
            )
            self.connections[connection] = (switch1, switch2)
            # Add edges to graph for Dijkstra's algorithm
            self.graph[switch1][switch2] = 1
            self.graph[switch2][switch1] = 1
        # Connect nodes to the nearest switch based on Euclidean distance
        for node in self.nodes:
            node_x, node_y = self.canvas.coords(node)[0] + 10, self.canvas.coords(node)[1] + 10
            min_distance = float('inf')
            nearest_switch = None
            for switch in self.switches:
                switch_x, switch_y = self.canvas.coords(switch)[0] + 25, self.canvas.coords(switch)[1] + 25
                distance = math.sqrt((node_x - switch_x) ** 2 + (node_y - switch_y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_switch = switch
            if nearest_switch:
                connection = self.canvas.create_line(node_x, node_y, self.canvas.coords(nearest_switch)[0] + 25,
                                                     self.canvas.coords(nearest_switch)[1] + 25,
                                                     fill="black")
                self.connections[connection] = (node, nearest_switch)
                # Add edges to graph for Dijkstra's algorithm
                self.graph[node][nearest_switch] = min_distance * self.conversion_factor
                self.graph[nearest_switch][node] = min_distance * self.conversion_factor

    def find_shortest_path(self):
        # Clear previous highlights
        for connection in self.connections.keys():
            self.canvas.itemconfig(connection, fill="black", dash=())

        node1_number = int(self.node1_entry.get())
        node2_number = int(self.node2_entry.get())

        if node1_number < 1 or node2_number < 1 or node1_number > len(self.nodes) or node2_number > len(self.nodes):
            messagebox.showwarning("Warning", "Invalid node numbers.")
            return

        start = self.nodes[node1_number - 1]  # Nodes are 1-indexed
        end = self.nodes[node2_number - 1]  # Nodes are 1-indexed

        self.show_shortest_path(start, end)

    def show_shortest_path(self, start, end):
        # Initialize Dijkstra's algorithm
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        previous = {}

        priority_queue = [(0, start)]

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_node == end:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = previous.get(current_node)
                path.reverse()

                # Highlight the shortest path as a red dotted line
                for i in range(len(path) - 1):
                    connection = self.find_connection(path[i], path[i + 1])
                    self.canvas.itemconfig(connection, fill="red")
                return

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.graph[current_node].items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))

    def find_connection(self, node1, node2):
        # Find the connection between two nodes
        for connection, (n1, n2) in self.connections.items():
            if (node1 == n1 and node2 == n2) or (node1 == n2 and node2 == n1):
                return connection
        return None


def main():
    root = tk.Tk()
    root.title("Network Simulator")
    app = NetworkSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import networkx as nx
from pyvis.network import Network
from typing import Dict, Any, List

class GraphBuilder:
    def __init__(self):
        self.graph = nx.Graph()

    def add_entity(self, entity_id: str, entity_type: str, attributes: Dict[str, Any] = None):
        """
        Adds a node to the graph representing an entity (e.g., User, Email, IP, Domain).
        """
        if attributes is None:
            attributes = {}

        # Color coding based on entity type
        colors = {
            "Username": "#3498db",  # Blue
            "Email": "#e74c3c",     # Red
            "Domain": "#2ecc71",    # Green
            "IP": "#f1c40f",        # Yellow
            "Tracker": "#9b59b6",   # Purple
            "Bucket": "#e67e22"     # Orange
        }

        color = colors.get(entity_type, "#95a5a6") # Default Grey

        self.graph.add_node(
            entity_id,
            label=entity_id,
            title=f"Type: {entity_type}",
            group=entity_type,
            color=color,
            **attributes
        )

    def add_relationship(self, source_id: str, target_id: str, relationship_type: str):
        """
        Adds an edge between two entities representing a relationship.
        """
        # Ensure both nodes exist before adding an edge, or add them with generic types if they don't
        if not self.graph.has_node(source_id):
            self.add_entity(source_id, "Unknown")
        if not self.graph.has_node(target_id):
            self.add_entity(target_id, "Unknown")

        self.graph.add_edge(source_id, target_id, title=relationship_type, label=relationship_type)

    def generate_html(self, output_filepath: str = "sherlock_graph.html"):
        """
        Generates an interactive HTML dashboard using Pyvis.
        """
        # Set up Pyvis network
        net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')

        # Inherit the NetworkX graph
        net.from_nx(self.graph)

        # Add physics options for better layout stabilization
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
          }
        }
        """)

        # Write out the HTML file
        net.save_graph(output_filepath)

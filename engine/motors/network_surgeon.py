import networkx as nx


class NetworkSurgeon:
    def find_hidden_connections(self, nodes, edges):
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        centrality = nx.betweenness_centrality(G)
        hidden_brokers = [n for n, c in centrality.items() if c > 0.5]
        communities = list(nx.community.greedy_modularity_communities(G))
        return {
            "motor": "NetworkX",
            "hidden_brokers": hidden_brokers,
            "communities_count": len(communities),
            "negative_finding": "Bu ağda gizli aracılar var" if hidden_brokers else "Ağ temiz"
        }

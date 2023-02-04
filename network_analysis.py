#### FUNCTION
from networkx.algorithms.community import modularity, louvain_communities
import numpy as np
import networkx as nx


def estimate_modularity(adoption_dict: dict):
    """
    Estimates the modularity of the pattern.
     1. Builds undirected graph with edges for (land) borders between EU countries.
     2. Computes and adds weights to edges based on euclidian similarity of green energy adoption.
     3. Compartmentalises graph according to similarity into communities.
     4. Calculates modularity score.
     :param:dict energy_adoption: dictionary of {country_name:green_energy_adoption_val) pairs.
     :return:float modularity of the network
     """
    eu_graph = similarity_weighting(import_eu_graph(), adoption_dict)
    communities = louvain_communities(eu_graph)

    return modularity(eu_graph, communities, weight="weight")


def import_eu_graph():
    """Import and initialise networkx graph object for the EU.
    Edges are not weighted and only exist if countries share a land border."""
    eu_countries = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
                    "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
                    "Spain", "Sweden"]

    eu_borders = [
        ("Austria", "Germany"),
        ("Austria", "Czech Republic"),
        ("Austria", "Slovakia"),
        ("Austria", "Slovenia"),
        ("Austria", "Italy"),
        ("Belgium", "Netherlands"),
        ("Belgium", "Germany"),
        ("Belgium", "Luxembourg"),
        ("Belgium", "France"),
        ("Bulgaria", "Romania"),
        ("Bulgaria", "Greece"),
        ("Croatia", "Slovenia"),
        ("Croatia", "Hungary"),
        ("Czech Republic", "Germany"),
        ("Czech Republic", "Poland"),
        ("Czech Republic", "Slovakia"),
        ("Denmark", "Germany"),
        ("Estonia", "Latvia"),
        ("Finland", "Sweden"),
        ("France", "Belgium"),
        ("France", "Luxembourg"),
        ("France", "Germany"),
        ("France", "Italy"),
        ("Germany", "Denmark"),
        ("Germany", "Poland"),
        ("Germany", "Czech Republic"),
        ("Germany", "Austria"),
        ("Germany", "Netherlands"),
        ("Greece", "Bulgaria"),
        ("Hungary", "Austria"),
        ("Hungary", "Slovakia"),
        ("Hungary", "Romania"),
        ("Italy", "Austria"),
        ("Italy", "Slovenia"),
        ("Latvia", "Lithuania"),
        ("Lithuania", "Poland"),
        ("Luxembourg", "Belgium"),
        ("Luxembourg", "Germany"),
        ("Malta", "Italy"),
        ("Netherlands", "Belgium"),
        ("Netherlands", "Germany"),
        ("Poland", "Germany"),
        ("Poland", "Czech Republic"),
        ("Poland", "Slovakia")]

    eu_borders += [("Sweden", "Denmark")]
    G = nx.Graph()

    # Add the EU countries as nodes to the graph
    G.add_nodes_from(eu_countries)
    G.add_edges_from(eu_borders)
    return G


def similarity_weighting(eu_graph, adoption_dict):
    """Compute similarity and add as weights to graph."""

    def euclidian_similarity(a, b):
        """Symmetric similarity measure based on euclidean distance."""
        return 1 - np.linalg.norm(a - b)

    borders = eu_graph.edges
    for country_a, country_b in borders:
        weight = euclidian_similarity(adoption_dict[country_a], adoption_dict[country_b])
        eu_graph.add_edge(country_a, country_b, weight=weight)
    return eu_graph

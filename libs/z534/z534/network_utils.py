def extract_backbone(G, alpha):
    """
    Network backbone extraction using the multi-scale backbone algorithm
    by Serrano et al., PNAS.

    Source:
    https://gist.github.com/bagrow/11181518#file-extract_backbone-py

    I took this code from that created by Lili Miao.

    Parameterss
    ----------
    G : networkx graph object
        The networkx graph object
    alpha :
        Parameter for edge filtering

    Returns
    -------
    out:
        A new networkx graph containing the backbone structure of the
        parameter graph
    """

    import networkx as nx

    keep_graph = nx.Graph()
    for n in G:
        k_n = len(G[n])
        if k_n > 1:
            sum_w = G.degree(n, weight="weight")
            for nj in G[n]:
                pij = 1.0 * G[n][nj]["weight"] / sum_w
                if (1 - pij) ** (k_n - 1) < alpha:  # edge is significant
                    keep_graph.add_edge(n, nj)
    return keep_graph

def set_business_node_attributes(G, df, attribute_list):
    """
    Adds node-level attributes to the networkx graph

    Parameterss
    ----------
    G : networkx graph object
        The networkx graph object
    df :
        Pandas dataframe contianing information for each business
    attribute_list:
        List of attributes to apply to each node

    Returns
    -------
    out:
        A new networkx graph with the node attributes applied
    """
    import networkx as nx
    # Make a copy of the graph—I like functional style over OO style
    g = G.copy()

    for attr in attribute_list:
        attr_dict = {}
        for index, row in df.iterrows():
            attr_dict[row['business_id']] = row[attr]

        # set attributes on the graph
        nx.set_node_attributes(g, attr_dict, name=attr)

    # return the updated graph
    return(g)

def get_neighbors_of_node(G, target):
    """
    Returns the neighbors of a given node as a list

    Parameterss
    ----------
    G : networkx graph object
        The networkx graph object
    target :
        The business id associated with the node whose neighbors are being queried

    Returns
    -------
    out:
        A list containing the business ids of the neighbors of the target node
    """
    return([neighbor for neighbor in G.neighbors(target)])

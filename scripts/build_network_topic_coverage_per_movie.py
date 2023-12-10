import argparse
from collections import Counter
import pandas as pd
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt


def build_coverage_network(csv_filepath) -> nx.Graph:
    print(f"Building network from '{Path(csv_filepath).relative_to(Path(csv_filepath).parent.parent)}'...")
    df = pd.read_csv(csv_filepath, encoding='utf-8')

    movies = sorted(df['ID'].unique())
    topics = sorted(df['Annotation'].unique())
    topics.remove('duplicate')

    B = nx.Graph()
    B.name = "Topic Coverage by Movie"
    B.add_nodes_from(movies, bipartite=0)
    B.add_nodes_from(topics, bipartite=1)
    
    for index, row in df.iterrows():
        movie = row['ID']
        topic = row['Annotation']
        if topic == 'duplicate':
            continue
        
        if B.has_edge(movie, topic):
            B[movie][topic]['weight'] += 1
        else:
            B.add_edge(movie, topic, weight=1)

    print(f"Network '{B.name}' has been built.")
    return B


def draw_graph(B: nx.Graph, filepath):
    NODE_SIZE_MULTIPLIER = 1100
    EDGE_WIDTH_MULTIPLIER = 60
    MOVIE_COLORS = ['mediumseagreen', 'deepskyblue', 'slateblue', 'hotpink']
    
    print(f"Drawing graph '{B.name}'...")
    # Set up figure and axis (the axis are changed slightly to make sure the nodes and their labels fit in the figure).
    f = plt.figure(figsize=(50, 50), dpi=80)
    plt.axis([-1.3, 0.9, -0.7, 0.7])

    movie_nodes = [node for node, bipartite in B.nodes(data='bipartite') if bipartite == 0]
    pos = nx.bipartite_layout(B, movie_nodes)

    node_weighted_degrees = B.degree(weight='weight')
    edge_weights = nx.get_edge_attributes(B, 'weight')
    max_weight = max(edge_weights.values())

    # Draw updated graph nodes with colour representing the movie (or a default colour for topic nodes)
    # and size representing the coverage of that movie/topic relative to the entire set of articles.
    for node, weighted_deg in node_weighted_degrees:
        size = weighted_deg * NODE_SIZE_MULTIPLIER
        color = MOVIE_COLORS[movie_nodes.index(node)] if node in movie_nodes else 'sandybrown'        
        nx.draw_networkx_nodes(B, pos, nodelist=[node], node_size=size, node_color=color)

    # Draw updated graph edges with colour representing the edge's movie node, and width representing its weight.
    for edge in B.edges(data='weight'):
        movie = edge[0]
        weight = edge[2]
        width = (weight / max_weight) * EDGE_WIDTH_MULTIPLIER
        color = MOVIE_COLORS[movie_nodes.index(movie)]
        nx.draw_networkx_edges(B, pos, edgelist=[edge], width=width, edge_color=color)

    article_total = sum([wdeg for n, wdeg in node_weighted_degrees if n in movie_nodes])
    print(article_total)
    labels = {n: f"{n}\n({round(100 * wdeg / article_total, 1)}%)" for n, wdeg in node_weighted_degrees}
    nx.draw_networkx_labels(B, pos, labels, font_size=50)

    f.savefig(filepath)
    print(f"Graph '{B.name}' has been saved to '{filepath}'.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--articles", required=True,
                        help="The path to the article csv file.")
    parser.add_argument("-o", "--output", required=True, help="The path to the output graph png file.")
    args = parser.parse_args()

    output_file = Path(args.output)
    output_file.parent.mkdir(exist_ok=True, parents=True)

    B = build_coverage_network(args.articles)
    draw_graph(B, output_file)


if __name__ == '__main__':
    main()

from botdet.data.dataset_botnet import BotnetDataset
from botdet.data.dataloader import GraphDataLoader
from tqdm import tqdm
import os
import torch as ch
import numpy as np


LOCAL_DATA_DIR = "/localtmp/as9rw/datasets/botnet"
SPLIT_INFO_PATH = "/p/adversarialml/as9rw/datasets/botnet"


class BotNetWrapper:
    def __init__(self, dataset_name="chord", split=None,
                 feat_len=1, subsample=1.0):
        self.dataset_name = dataset_name
        self.split = split
        assert subsample >= 0 and subsample <= 1

        # Use local storage (much faster)
        if not os.path.exists(LOCAL_DATA_DIR):
            raise FileNotFoundError("Local data not found")
        data_dir = os.path.join(LOCAL_DATA_DIR, dataset_name)

        # Use adv/victim split
        split_info = [None] * 3
        if split is not None:
            splits = self.get_splits(split)
            for i, spl in enumerate(splits):

                # Further subsample graphs from these splits
                if subsample < 1:
                    print(spl)
                    perm_ = np.random.permutation(len(spl))
                    perm_ = perm_[:int(len(spl) * subsample)]
                    spl = spl[perm_]

                split_info[i] = [str(x) for x in spl]

        self.train_data = BotnetDataset(
            name=dataset_name, root=data_dir,
            add_features_dgl=feat_len, in_memory=True,
            split='train', graph_format='dgl',
            partial_load=split_info[0])

        self.val_data = BotnetDataset(
            name=dataset_name, root=data_dir,
            add_features_dgl=feat_len, in_memory=True,
            split='val', graph_format='dgl',
            partial_load=split_info[1])

        self.test_data = BotnetDataset(
            name=dataset_name, root=data_dir,
            add_features_dgl=feat_len, in_memory=True,
            split='test', graph_format='dgl',
            partial_load=split_info[2])

        # TODO: Combine val and test data

    def get_splits(self, split):
        splitname = "split_70_30.npz"
        splitfile = np.load(os.path.join(
            SPLIT_INFO_PATH, self.dataset_name, splitname),
            allow_pickle=True)
        return splitfile[split]

    def get_loaders(self, batch_size, shuffle=False, num_workers=0):
        # Create loaders
        self.train_loader = GraphDataLoader(
            self.train_data, batch_size, shuffle, num_workers)
        self.test_loader = GraphDataLoader(
            self.test_data, batch_size, False, num_workers)

        return self.train_loader, self.test_loader


def get_pairwise_distances(graph):
    # Complexity O(V*(V+E))
    # Average graph has ~143K nodes, ~1.5M edges
    # Not scalable to compute diamater, certainly not to
    # Manipulate graph to get desired diameter
    import networkx as nx
    from networkx.algorithms.shortest_paths.unweighted import single_source_shortest_path_length
    from networkx.algorithms.components import number_connected_components
    from networkx.algorithms import approximation
    from networkx.algorithms.assortativity.pairs import node_degree_xy
    from networkx.algorithms.distance_measures import diameter
    import time

    print("Creating networkX graph")
    nwg = graph.to_networkx().to_undirected()

    # Create SNAP graph
    print("Creating SNAP graph")
    import snap
    sng = snap.TUNGraph.New()
    for i in nwg.nodes:
        sng.AddNode(int(i))
    for (e, v, _) in nwg.edges:
        sng.AddEdge(int(e), int(v))

    print(sng.GetNodes())
    print(sng.GetEdges())

    # Actual diam
    # start = time.time()
    # efd = diameter(nwg)
    # end = time.time()
    # print(efd, "took", end - start)

    # Diam stats
    start = time.time()
    efd = sng.GetBfsEffDiamAll(10, False)
    end = time.time()
    print(efd, "took", end - start)

    start = time.time()
    efd = sng.GetBfsFullDiam(10, False)
    end = time.time()
    print(efd, "took", end - start)

    # Diameter approx
    start = time.time()
    efd = sng.GetAnfEffDiam(1, -1)
    end = time.time()
    print(efd, "took", end - start)

    # Average clustering coefficient (heuristic)
    start = time.time()
    ca = approximation.clustering_coefficientaverage_clustering(
        nwg, trials=10000)
    end = time.time()
    print(ca, "took", end - start)
    # exit(0)

    # Mixing-rate computation
    start = time.time()
    xy_iter = node_degree_xy(nwg)
    matrix = np.zeros((nwg.number_of_nodes(), nwg.number_of_nodes()))
    for x, y in xy_iter:
        matrix[x][y] += 1
    end = time.time()
    print(ca, "mixmat", end - start)
    exit(0)

    # Get degrees
    print("Calculating degrees")
    degrees = np.array([val for (node, val) in nwg.degree()])

    print("Start with:", number_connected_components(nwg) / nwg.number_of_nodes())
    top_k = 5
    max_degree_nodes = np.argsort(-degrees)
    for i in range(top_k):

        # Remove node (and its edges)
        print("Remove most dense node")
        nwg.remove_node(max_degree_nodes[i])

        # Get number of connected components
        print(number_connected_components(nwg) / nwg.number_of_nodes())

    print("Start")
    import time
    st = time.time()
    length = single_source_shortest_path_length(nwg, 0)
    et = time.time()
    print("BFS took %.2f seconds" % (et - st))


if __name__ == "__main__":
    dataset_name = "chord"

    ds = BotNetWrapper(dataset_name)

    # Create victim/adv splits
    victim_ratio = 0.7
    train_perm = np.random.permutation(len(ds.train_data))
    val_perm = np.random.permutation(len(ds.val_data))
    test_perm = np.random.permutation(len(ds.test_data))

    victim_train = train_perm[:int(victim_ratio * len(ds.train_data))]
    adv_train = train_perm[int(victim_ratio * len(ds.train_data)):]

    victim_val = val_perm[:int(victim_ratio * len(ds.val_data))]
    adv_val = val_perm[int(victim_ratio * len(ds.val_data)):]

    victim_test = test_perm[:int(victim_ratio * len(ds.test_data))]
    adv_test = test_perm[int(victim_ratio * len(ds.test_data)):]

    splits = {
        "victim": np.array(
            [victim_train, victim_val, victim_test], dtype=object),
        "adv": np.array(
            [adv_train, adv_val, adv_test], dtype=object)
    }
    print(len(victim_train), len(victim_val), len(victim_test))
    print(len(adv_train), len(adv_val), len(adv_test))

    # Save split information
    np.savez(os.path.join(SPLIT_INFO_PATH, dataset_name, "split_70_30"),
             adv=splits["adv"], victim=splits["victim"])
    print("Saved split information!")

    # Check time taken to load data
    import time
    start = time.time()
    ds = BotNetWrapper(split="adv")
    end = time.time()
    print("Time taken to load adv", end - start)

    start = time.time()
    ds = BotNetWrapper(split="victim")
    end = time.time()
    print("Time taken to load victim", end - start)

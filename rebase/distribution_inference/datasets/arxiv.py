import os
import torch as ch
from tqdm import tqdm
import torch.nn as nn

import distribution_inference.datasets.base as base
from distribution_inference.models.core import GCN
from distribution_inference.config import DatasetConfig, TrainConfig
from collections import Counter
from distribution_inference.training.utils import load_model
from distribution_inference.utils import get_arxiv_node_params_mapping

import dgl
import numpy as np
from ogb.nodeproppred.dataset_dgl import DglNodePropPredDataset


class DatasetInformation(base.DatasetInformation):
    def __init__(self, epoch_wise: bool = False):
        degrees = [9, 10, 11, 12, 12.5, 13, 13.5, 14, 15, 16, 17]
        super().__init__(name="arXiv",
                         data_path="ogbn_data/",
                        #  models_path="models_arxiv_new",
                         models_path="models_arxiv_nobalancing",
                         properties=["mean"],
                         values={"mean": degrees},
                         supported_models=["gcn"],
                         default_model="gcn",
                         epoch_wise=epoch_wise)
        self.supported_properties = ["mean"]
        # Mapping between distributions and their (n, s) values
        self.param_mapping = get_arxiv_node_params_mapping()

    def get_model(self,
                  cpu: bool = False,
                  model_arch: str = None) -> nn.Module:
        if model_arch is None:
            model_arch = self.default_model

        if model_arch == "gcn":
            model = GCN(n_hidden=256,
                        n_layers=3,
                        dropout=0.5,
                        num_classes=40,
                        num_features=128)
        else:
            raise NotImplementedError("Model architecture not supported")

        if cpu:
            model = model.cpu()
        else:
            model = model.cuda()
        return model
    
    def _best_fit_no_intercept(self, x, y):
        num = np.sum(x * y)
        den = np.sum(x * x)
        return num / den
    
    def get_zipf_params_for_degree(self, split, degree, order=None):
        ds = ArxivNodeDataset(split)

        # Change mean-node degree
        ds.change_mean_degree(degree)

        # Compute degrees
        ds.precompute_degrees()

        # Get degs
        degs = ds.degs

        # Get counts of degrees
        deg_counts_og = Counter(degs)
        deg_counts = deg_counts_og.items()

        # Get sorting order of degrees according to degree
        # deg_counts.sort(key=lambda x: x[0])

        start_point = 2
        # Skip nodes with degree < start_point
        deg_counts = [dc for dc in deg_counts if dc[0] >= start_point]

        # Skip nodes with frequency <= 2
        deg_counts = np.array([dc for dc in deg_counts if dc[1] > 2])

        # Get sorting order of degrees according to frequency
        if order is None:
            order = np.argsort(deg_counts[:, 1])[::-1]
            order = deg_counts[order][:, 0]

        deg_counts = [(k, deg_counts_og.get(k, 0)) for k in order]

        # Sort by this order
        # deg_counts = [deg_counts[o] for o in order]

        # Extract frequencies (to fit Zipf's law)
        freqs = np.array([dc[1] for dc in deg_counts])

        # Normalize frequencies
        x_range = np.arange(1, len(freqs) + 1)
        freqs = freqs / np.sum(freqs)

        # Convert to log-log scale to find parameters
        log_freqs = np.log(freqs)
        log_x_range = np.log(x_range)

        # Get slope for log-log line
        m = - self._best_fit_no_intercept(log_x_range, log_freqs)

        # Print out relevant parameters
        N_max = len(freqs)

        # While at it, also compute mean node degree using curve
        y_calc = np.array([x_range ** (-m)])
        y_calc /= np.sum(y_calc)
        mean_deg = np.sum(y_calc * order)
        # Add scaling (x-axis shift)
        mean_deg += (start_point - 1)

        return m, N_max, order, mean_deg


class NodeLevelDataset:
    def __init__(self, name, normalize=True, on_gpu=True):
        di = DatasetInformation()
        self.data = DglNodePropPredDataset(name=name, root=di.base_data_dir)

        self.g, self.labels = self.data[0]
        self.on_gpu = on_gpu

        # Extract node features
        self.features = self.g.ndata['feat']

        # Degrees of nodes
        self.degs = []

        # Normalize features
        if normalize:
            m, std = ch.mean(self.features, 0), ch.std(self.features, 0)
            self.features = (self.features - m) / std

        self.num_features = self.features.shape[1]
        self.num_classes = self.data.num_classes
        self.num_nodes = self.g.number_of_nodes()

        # Extract any extra data
        self.before_init()

        # Process graph before shifting to GPU
        self.pre_process()

        # Shift data to GPU
        if self.on_gpu:
            self.shift_to_gpu()

    def before_init(self):
        pass

    def pre_process(self):
        # Add self loops
        self.g = dgl.remove_self_loop(self.g)
        self.g = dgl.add_self_loop(self.g)

        # Make bidirectional
        self.g = dgl.to_bidirected(self.g)

    def shift_to_gpu(self):
        # Shift graph, labels to cuda
        self.g = self.g.to('cuda')
        self.labels = self.labels.cuda()
        self.features = self.features.cuda()

    def get_idx_split(self, test_ratio=0.2):
        num_test = int(test_ratio * self.num_nodes)
        train_mask = ch.zeros(self.num_nodes, dtype=ch.bool)
        train_mask[num_test:] = 1
        test_mask = ch.zeros(
            self.num_nodes, dtype=ch.bool)
        test_mask[:num_test] = 1
        return train_mask, test_mask

    def get_features(self):
        return self.features

    def get_labels(self):
        return self.labels

    def precompute_degrees(self):
        X, _ = self.g.edges()
        degs = []
        for i in tqdm(range(self.g.number_of_nodes())):
            degs.append(ch.sum(X == i).item())
        self.degs = np.array(degs)


class ArxivNodeDataset(NodeLevelDataset):
    def __init__(self, split, normalize=True, on_gpu=True):
        super(ArxivNodeDataset, self).__init__(
            'ogbn-arxiv', normalize=normalize, on_gpu=on_gpu)

        # 59:41 victim:adv data split
        # (all original data, including train/val/test)
        # Original data had 54:46 train-nontrain split
        # Get similar splits
        split_year = 2016
        if split == 'adv':
            # 77:23 train:test split
            test_year = 2015
            self.train_idx = self.years < test_year
            self.test_idx = ch.logical_and(
                self.years >= test_year, self.years < split_year)
        elif split == 'victim':
            # 66:34 train:test split
            test_year = 2019
            self.train_idx = ch.logical_and(
                self.years != test_year, self.years >= split_year)
            self.test_idx = (self.years == test_year)
        else:
            raise ValueError("Invalid split requested!")

        self.train_idx = ch.nonzero(self.train_idx, as_tuple=True)[0]
        self.test_idx = ch.nonzero(self.test_idx, as_tuple=True)[0]

        # Sort them now, for easier access later
        self.train_idx = ch.sort(self.train_idx)[0]
        self.test_idx = ch.sort(self.test_idx)[0]

    def before_init(self):
        # Extract years
        self.years = ch.squeeze(self.g.ndata['year'], 1)
        if self.on_gpu:
            self.years = self.years.cuda()

    def get_idx_split(self):
        return self.train_idx, self.test_idx

    def random_split_pick(self, ratio):
        # Randomly sample 'ratio' worth of specified train data
        # Set train mask to those ones
        n_elems = len(self.train_idx)
        perm = ch.randperm(n_elems)[:int(ratio * n_elems)]
        self.train_idx = self.train_idx[perm]

    def not_label_ratio_preserving_pick(self, total_tr, total_te):
        # Take random sample (no replacement) from self.train_idx
        perm_train = ch.randperm(len(self.train_idx))[:total_tr]
        perm_test = ch.randperm(len(self.test_idx))[:total_te]

        self.train_idx = self.train_idx[perm_train]
        self.test_idx = self.test_idx[perm_test]

    def label_ratio_preserving_pick(self, total_tr, total_te):
        # While maintaining relative label ratios for classes
        # Sample a set of size total
        labels = ch.cat(
            (self.labels[self.train_idx, 0], self.labels[self.test_idx, 0]), 0)
        elems, counts = ch.unique(labels, return_counts=True)
        # Get ratios for these elems
        counts = counts.float() / len(labels)
        # Sample according to ratio from existing train, test sets
        train_new, test_new = [], []
        for e, c in zip(elems, counts):
            # for train
            qualify = ch.nonzero(
                self.labels[self.train_idx, 0] == e, as_tuple=True)[0]
            ids = ch.randperm(len(qualify))[:int(c * total_tr)]
            train_new.append(qualify[ids])
            # for test
            qualify = ch.nonzero(
                self.labels[self.test_idx, 0] == e, as_tuple=True)[0]
            ids = ch.randperm(len(qualify))[:int(c * total_te)]
            test_new.append(qualify[ids])

        self.train_idx = ch.cat(train_new, 0)
        self.test_idx = ch.cat(test_new, 0)

    def change_property(self, wanted_degree, change, prune_ratio=0.0):
        '''
        Prune graph nodes such that mean degree of remaining
        graph is the same as requested degree.
        '''
        # If no change requested, perform no change
        if wanted_degree is None:
            return

        # Compute degrees
        self.precompute_degrees()

        # Prune graph, get rid of nodes
        label_ids = ch.cat((self.train_idx, self.test_idx)).cpu().numpy()
        self.g, pruned_nodes = change_graph_property(
            self.g, self.degs, wanted_degree, change,
            label_ids, prune_ratio=prune_ratio)

        # Make mapping between old and new IDs
        not_pruned = ch.ones(self.num_nodes).byte()
        not_pruned[pruned_nodes] = False
        not_pruned = ch.nonzero(not_pruned, as_tuple=True)[0]
        mapping = {x.item(): i for i, x in enumerate(not_pruned)}

        # Function to modify current masks to reflect pruning
        def process(ids):
            # Convert indices to mask
            keep = ch.zeros(self.num_nodes).byte()
            keep[ids] = True

            # Get rid of pruned nodes from this, get back to IDs
            not_pruned = ch.ones(self.num_nodes).byte()
            not_pruned[pruned_nodes] = False
            not_pruned = ch.nonzero(not_pruned, as_tuple=True)[0]
            keep[pruned_nodes] = False
            keep = ch.nonzero(keep, as_tuple=True)[0]

            # Update current mask to point to correct IDs
            for i, x in enumerate(keep):
                keep[i] = mapping[x.item()]

            # Shift mask back to GPU
            if self.on_gpu:
                keep = keep.cuda()
            return keep

        # Update masks to account for pruned nodes,  re-indexing
        self.train_idx = process(self.train_idx)
        self.test_idx = process(self.test_idx)

        # Update features, labels, year-information
        self.years = self.years[not_pruned]
        self.features = self.features[not_pruned]
        self.labels = self.labels[not_pruned]

        # Update number of nodes in graph
        self.num_nodes -= len(pruned_nodes)

    def change_mean_degree(self, wanted_degree, prune_ratio=0.0):
        '''
        Prune graph nodes such that mean degree of remaining
        graph is the same as requested degree.
        '''
        self.change_property(wanted_degree, "mean", prune_ratio)

    def keep_below_degree_threshold(self, threshold_degree, prune_ratio=0.0):
        '''
        Prune graph nodes such that remaining nodes all have
        node degree strictly below threshold
        '''
        self.change_property(threshold_degree, "keep_below", prune_ratio)


class ArxivWrapper(base.CustomDatasetWrapper):
    def __init__(self,
                 data_config: DatasetConfig,
                 skip_data: bool = False,
                 label_noise: float = 0,
                 epoch: bool = False):
        # Call parent constructor
        super().__init__(data_config, skip_data, label_noise, is_graph_data=True)

        # Define how much data (nodes) needed to sample
        self.sample_sizes = {
            "mean": {
                "adv": (30000, 10000),
                "victim": (62000, 35000)
            }
        }
        # TODO: Update above quantity for non-balanced case
        # Define DI object
        self.info_object = DatasetInformation()

    def _filter(self, x):
        return x[self.prop] == 1

    def load_model(self, path: str,
                   on_cpu: bool = False,
                   model_arch: str = None) -> nn.Module:
        model = self.info_object.get_model(cpu=on_cpu, model_arch=model_arch)
        return load_model(model, path, on_cpu=on_cpu)
    
    def get_labels(self):
        return self.ds.get_labels()
    
    def get_features(self):
        return self.ds.get_features()

    def load_data(self):
        self.ds = ArxivNodeDataset(self.split)

        # Modify mean degree
        self.ds.change_mean_degree(self.ratio, self.prune)

        # self.ds.label_ratio_preserving_pick(
        self.ds.not_label_ratio_preserving_pick(
            self.sample_sizes[self.prop][self.split][0],
            self.sample_sizes[self.prop][self.split][1])
        
        # Get train/test ID splits
        train_idx, test_idx = self.ds.get_idx_split()

        return train_idx, test_idx
    
    def get_processed_val_loader(self, batch_size: int,
                                 shuffle: bool = False,
                                 val_factor: float = 1,
                                 num_workers: int = 0,
                                 prefetch_factor: int = 2):
        raise ValueError("Processed variant does not exist for this dataset")

    def get_loaders(self, batch_size,
                    shuffle: bool = False,
                    eval_shuffle: bool = False,
                    num_workers: int = 2,
                    prefetch_factor: int = 2):
        # Prepare data and get splits
        train_idx, test_idx = self.load_data()

        if shuffle:
            train_idx = ch.randperm(train_idx)
        if eval_shuffle:
            test_idx = ch.randperm(test_idx)

        return self.ds, (train_idx, test_idx)

    def get_save_dir(self, train_config: TrainConfig, model_arch: str) -> str:
        info_object = DatasetInformation()
        base_models_dir = info_object.base_models_dir
        if int(self.ratio) == self.ratio:
            deg_name = "deg%d" % self.ratio
        else:
            "deg%.1f" % self.ratio
        subfolder_prefix = os.path.join(self.split, self.prop, deg_name)

        # Standard logic
        if model_arch is None:
            model_arch = self.info_object.default_model
        if model_arch not in info_object.supported_models:
            raise ValueError(f"Model architecture {model_arch} not supported")
        if model_arch is None:
            model_arch = info_object.default_model
        base_models_dir = os.path.join(base_models_dir, model_arch)

        save_path = os.path.join(base_models_dir, subfolder_prefix)

        # Make sure this directory exists
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
        return save_path


def neighbor_removal(g, pick, degs, inf_val):
    L, R = g.edges()
    neighbors = R[L == pick].cpu().numpy()
    neighbors_mask = np.zeros_like(degs, dtype=bool)
    neighbors_mask[neighbors] = True
    neighbors_mask[degs == inf_val] = False
    degs[neighbors_mask] -= 1
    return degs


def find_to_prune_for_mean_degree(g, degs, wanted_deg, pre_prune=[]):
    prune = []
    degs = degs.astype(np.float32)

    # Define logic to process removal of node
    def loop_step(pick):
        nonlocal degs, prune

        # Reduce degree of all nodes that were connected to pruned node
        # And are up for consideration currently
        degs = neighbor_removal(g, pick, degs, np.nan)

        # Removed this node, mark as NAN
        degs[pick] = np.nan

        # Note node to be pruned and keep track of current degree
        cur_deg = np.nanmean(degs)
        prune.append(pick)

        return cur_deg

    # If nodes to be pruned already provided, add them to list
    # and be mindful of their pruning
    for pp in pre_prune:
        cur_deg = loop_step(pp)

    # Take note of mean degree right now
    cur_deg = np.nanmean(degs)

    # If desired degree is more than current, prune low-degree nodes
    if wanted_deg > cur_deg:
        while cur_deg < wanted_deg:
            # Find minimum right now
            pick = np.nanargmin(degs)

            # Process removal of this node
            cur_deg = loop_step(pick)

    # Else, prune high-degree nodes
    else:
        while cur_deg > wanted_deg:
            # Find minimum right now
            pick = np.nanargmax(degs)

            # Process removal of this node
            cur_deg = loop_step(pick)

    # Return list of nodes that should be removed
    return prune


def find_to_prune_for_threshold_degree(
    g, degs, threshold_degree, pre_prune=[]):
    prune = []
    inf_val = -1

    # Define logic to process removal of node
    def loop_step(pick):
        nonlocal degs, prune

        # Note node to be pruned
        prune.append(pick)

        # Reduce degree of all nodes that were connected to pruned node
        # And are up for consideration currently
        degs = neighbor_removal(g, pick, degs, inf_val)

        # Removed this node, mark as -1
        degs[pick] = inf_val

        return degs

    # If nodes to be pruned already provided, add them to list
    # and be mindful of their pruning
    for pp in pre_prune:
        degs = loop_step(pp)

    # Keep going until maximum node degree in graph is below threshold
    pick = np.argmax(degs)
    while degs[pick] >= threshold_degree:

        # Process removal of this node
        degs = loop_step(pick)

        # Find maximum degree node right now
        pick = np.argmax(degs)

    # Make sure other nodes have strictly smaller degree
    assert np.all(degs < threshold_degree)

    return prune


def change_graph_property(
        g, degs, wanted_deg, change,
        label_ids, prune_ratio=0):

    # Randomly pick and prune non-label nodes for graph
    # To introduce some randomness in graph structure
    pre_prune = []

    if prune_ratio > 0:
        # Since distribution according to connectivity is uneven
        # Bin according to degree to avoid pruning only
        # Low degree nodes

        bins = [0, 5, 10, 20, 50, np.inf]
        for i in range(len(bins)-1):
            picked = np.logical_and(degs >= bins[i], degs < bins[i+1])
            picked = picked.nonzero()[0]
            n_wanted = int(prune_ratio * len(picked))

            # Avoid nodes with labels
            picked = np.setdiff1d(picked, label_ids, assume_unique=True)

            perm = np.random.permutation(
                len(picked))[:n_wanted]
            pre_prune += list(perm)

    if change not in DatasetInformation().supported_properties:
        raise NotImplementedError("Not implemented this property")

    if change == "mean":
        to_prune = find_to_prune_for_mean_degree(
            g, degs, wanted_deg, pre_prune)
    else:
        to_prune = find_to_prune_for_threshold_degree(
            g, degs, wanted_deg, pre_prune)

    # Get rid of these nodes from graph
    g = dgl.remove_nodes(g, to_prune)

    return g, to_prune

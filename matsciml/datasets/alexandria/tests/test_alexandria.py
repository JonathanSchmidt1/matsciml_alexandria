from __future__ import annotations

from matsciml.datasets import transforms
from matsciml.datasets.alexandria import AlexandriaDataset
from matsciml.datasets.transforms import PointCloudToGraphTransform


def test_dataset_collate():
    dset = AlexandriaDataset(AlexandriaDataset.__devset__)
    data = [dset.__getitem__(index) for index in range(10)]
    batch = dset.collate_fn(data)
    # check the nuclear coordinates and numbers match what is expected
    assert batch["pos"].shape[-1] == 3
    assert batch["pos"].ndim == 2
    assert len(batch["atomic_numbers"]) == 10


def test_dgl_dataset():
    dset = AlexandriaDataset(
        AlexandriaDataset.__devset__,
        transforms=[transforms.PointCloudToGraphTransform("dgl", cutoff_dist=20.0)],
    )
    for index in range(10):
        data = dset.__getitem__(index)
        assert "graph" in data


def test_dgl_collate():
    dset = AlexandriaDataset(
        AlexandriaDataset.__devset__,
        transforms=[transforms.PointCloudToGraphTransform("dgl", cutoff_dist=20.0)],
    )
    data = [dset.__getitem__(index) for index in range(10)]
    batch = dset.collate_fn(data)
    assert "graph" in batch
    # should be ten graphs
    assert batch["graph"].batch_size == 10
    assert all([key in batch["graph"].ndata for key in ["pos", "atomic_numbers"]])


def test_dataset_target_keys():
    dset = AlexandriaDataset.from_devset()
    assert dset.target_keys == {
        "regression": [
            "energy",
            "e_form",
            "e_above_hull",
            "dos_ef",
            "forces",
            "magmoms",
            "stress",
            "total_magnetization",
            "band_gap",
        ],
        "classification": [],
    }


def test_pairwise_pointcloud():
    dset = AlexandriaDataset.from_devset()
    sample = dset.__getitem__(10)
    assert all(
        [
            key in sample
            for key in ["pos", "pc_features", "sizes", "src_nodes", "dst_nodes"]
        ],
    )
    # for a pairwise point cloud sizes should be equal
    feats = sample["pc_features"]
    assert feats.size(0) == feats.size(1)
    assert sample["pos"].ndim == 2


def test_sampled_pointcloud():
    dset = AlexandriaDataset(AlexandriaDataset.__devset__, full_pairwise=False)
    sample = dset.__getitem__(10)
    assert all(
        [
            key in sample
            for key in ["pos", "pc_features", "sizes", "src_nodes", "dst_nodes"]
        ],
    )
    # for a pairwise point cloud sizes should be equal
    feats = sample["pc_features"]
    assert feats.size(0) >= feats.size(1)
    assert sample["pos"].ndim == 2


def test_graph_transform():
    dset = AlexandriaDataset(
        AlexandriaDataset.__devset__,
        full_pairwise=False,
        transforms=[PointCloudToGraphTransform("dgl", cutoff_dist=20.0)],
    )
    sample = dset.__getitem__(10)
    assert "graph" in sample
    assert all([key in sample["graph"].ndata for key in ["pos", "atomic_numbers"]])

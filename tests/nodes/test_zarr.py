import pytest
import torch
import zarr
from torch_geometric.data import HeteroData

from anemoi.graphs.nodes import builder
from anemoi.graphs.nodes.attributes import AreaWeights
from anemoi.graphs.nodes.attributes import UniformWeights


def test_init(mocker, mock_zarr_dataset):
    """Test ZarrNodes initialization."""
    mocker.patch.object(builder, "open_dataset", return_value=mock_zarr_dataset)
    node_builder = builder.ZarrDatasetNodes("dataset.zarr")
    assert isinstance(node_builder, builder.BaseNodeBuilder)
    assert isinstance(node_builder, builder.ZarrDatasetNodes)


def test_fail_init():
    """Test ZarrNodes initialization with invalid resolution."""
    with pytest.raises(zarr.errors.PathNotFoundError):
        builder.ZarrDatasetNodes("invalid_path.zarr")


def test_register_nodes(mocker, mock_zarr_dataset):
    """Test ZarrNodes register correctly the nodes."""
    mocker.patch.object(builder, "open_dataset", return_value=mock_zarr_dataset)
    node_builder = builder.ZarrDatasetNodes("dataset.zarr")
    graph = HeteroData()

    graph = node_builder.register_nodes(graph, "test_nodes")

    assert graph["test_nodes"].x is not None
    assert isinstance(graph["test_nodes"].x, torch.Tensor)
    assert graph["test_nodes"].x.shape == (node_builder.ds.num_nodes, 2)
    assert graph["test_nodes"].node_type == "ZarrDatasetNodes"


@pytest.mark.parametrize("attr_class", [UniformWeights, AreaWeights])
def test_register_attributes(mocker, graph_with_nodes: HeteroData, attr_class):
    """Test ZarrNodes register correctly the weights."""
    mocker.patch.object(builder, "open_dataset", return_value=None)
    node_builder = builder.ZarrDatasetNodes("dataset.zarr")
    config = {"test_attr": {"_target_": f"anemoi.graphs.nodes.attributes.{attr_class.__name__}"}}

    graph = node_builder.register_attributes(graph_with_nodes, "test_nodes", config)

    assert graph["test_nodes"]["test_attr"] is not None
    assert isinstance(graph["test_nodes"]["test_attr"], torch.Tensor)
    assert graph["test_nodes"]["test_attr"].shape[0] == graph["test_nodes"].x.shape[0]

import itertools

from ..structures.core import StructureFamily
from ..structures.data_source import DataSource, Management
from .base import BaseClient


def sync(
    source: BaseClient,
    dest: BaseClient,
    copy_internal: bool = True,
    copy_external: bool = False,
):
    """

    Parameters
    ----------
    source : tiled node
    dest : tiled node
    """
    source = source.include_data_sources().refresh()
    _DISPATCH[source.structure_family](source, dest, copy_internal, copy_external)


def _sync_array(source, dest, copy_internal, copy_external):
    num_blocks = (range(len(n)) for n in source.chunks)
    # Loop over each block index --- e.g. (0, 0), (0, 1), (0, 2) ....
    for block in itertools.product(*num_blocks):
        array = source.read_block(block)
        dest.write_block(array, block)


def _sync_table(source, dest, copy_internal, copy_external):
    for partition in range(source.structure().npartitions):
        df = source.read_partition(partition)
        dest.write_partition(df, partition)


def _sync_container(source, dest, copy_internal, copy_external):
    for key, child_node in source.items():
        original_data_sources = child_node.data_sources()
        if not original_data_sources:
            if child_node.structure_family == StructureFamily.container:
                data_sources = []
            else:
                raise ValueError(
                    f"Unable to copy {child_node} which has is a "
                    f"{child_node.structure_family} but has no data sources."
                )
        else:
            (original_data_source,) = original_data_sources
            if original_data_source.management == Management.external:
                data_sources = [original_data_source]
                if copy_external:
                    raise NotImplementedError(
                        "Copying externally-managed data is not yet implemented"
                    )
            else:
                if child_node.structure_family == StructureFamily.container:
                    data_sources = []
                else:
                    data_sources = [
                        DataSource(
                            management=original_data_source.management,
                            mimetype=original_data_source.mimetype,
                            structure_family=original_data_source.structure_family,
                            structure=original_data_source.structure,
                        )
                    ]
        node = dest.new(
            key=key,
            structure_family=child_node.structure_family,
            data_sources=data_sources,
            metadata=dict(child_node.metadata),
            specs=child_node.specs,
        )
        if (original_data_source.management != Management.external) and copy_internal:
            _DISPATCH[child_node.structure_family](
                child_node, node, copy_internal, copy_external
            )


_DISPATCH = {
    StructureFamily.array: _sync_array,
    StructureFamily.container: _sync_container,
    StructureFamily.table: _sync_table,
}

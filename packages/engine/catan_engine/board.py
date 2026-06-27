from __future__ import annotations

import math
import random
from dataclasses import dataclass

from catan_engine.resources import HEX_TO_RESOURCE, HexType, Resource


@dataclass
class Port:
    kind: str
    resource: Resource | None
    ratio: int

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "resource": self.resource.name if self.resource else None,
            "ratio": self.ratio,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> Port | None:
        if data is None:
            return None
        resource = Resource[data["resource"]] if data.get("resource") else None
        return cls(kind=data["kind"], resource=resource, ratio=int(data["ratio"]))


@dataclass
class Hex:
    id: int
    hex_type: HexType
    number_token: int | None
    node_ids: tuple[int, ...]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "hex_type": self.hex_type.name,
            "number_token": self.number_token,
            "node_ids": list(self.node_ids),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Hex:
        return cls(
            id=int(data["id"]),
            hex_type=HexType[data["hex_type"]],
            number_token=data.get("number_token"),
            node_ids=tuple(int(node_id) for node_id in data["node_ids"]),
        )


@dataclass
class Node:
    id: int
    hex_ids: tuple[int, ...]
    edge_ids: tuple[int, ...]
    port: Port | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "hex_ids": list(self.hex_ids),
            "edge_ids": list(self.edge_ids),
            "port": self.port.to_dict() if self.port else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Node:
        return cls(
            id=int(data["id"]),
            hex_ids=tuple(int(hex_id) for hex_id in data["hex_ids"]),
            edge_ids=tuple(int(edge_id) for edge_id in data["edge_ids"]),
            port=Port.from_dict(data.get("port")),
        )


@dataclass
class Edge:
    id: int
    node_a: int
    node_b: int
    hex_ids: tuple[int, ...]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "node_a": self.node_a,
            "node_b": self.node_b,
            "hex_ids": list(self.hex_ids),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Edge:
        return cls(
            id=int(data["id"]),
            node_a=int(data["node_a"]),
            node_b=int(data["node_b"]),
            hex_ids=tuple(int(hex_id) for hex_id in data["hex_ids"]),
        )


@dataclass
class Board:
    hexes: dict[int, Hex]
    nodes: dict[int, Node]
    edges: dict[int, Edge]
    robber_hex_id: int

    def get_adjacent_nodes(self, node_id: int) -> tuple[int, ...]:
        return tuple(self.get_opposite_node(edge_id, node_id) for edge_id in self.nodes[node_id].edge_ids)

    def get_adjacent_edges(self, node_id: int) -> tuple[int, ...]:
        return self.nodes[node_id].edge_ids

    def get_edge_between(self, node_a: int, node_b: int) -> int | None:
        wanted = {node_a, node_b}
        for edge_id in self.nodes[node_a].edge_ids:
            edge = self.edges[edge_id]
            if {edge.node_a, edge.node_b} == wanted:
                return edge_id
        return None

    def get_nodes_for_hex(self, hex_id: int) -> tuple[int, ...]:
        return self.hexes[hex_id].node_ids

    def get_hexes_for_node(self, node_id: int) -> tuple[int, ...]:
        return self.nodes[node_id].hex_ids

    def get_edges_for_node(self, node_id: int) -> tuple[int, ...]:
        return self.nodes[node_id].edge_ids

    def get_opposite_node(self, edge_id: int, node_id: int) -> int:
        edge = self.edges[edge_id]
        if edge.node_a == node_id:
            return edge.node_b
        if edge.node_b == node_id:
            return edge.node_a
        raise ValueError(f"node {node_id} is not on edge {edge_id}")

    def validate(self) -> None:
        if self.robber_hex_id not in self.hexes:
            raise ValueError("robber hex does not exist")
        if self.hexes[self.robber_hex_id].hex_type != HexType.DESERT:
            raise ValueError("robber must start on desert")

        for edge in self.edges.values():
            if edge.node_a not in self.nodes or edge.node_b not in self.nodes:
                raise ValueError(f"edge {edge.id} references missing endpoint")
            if edge.id not in self.nodes[edge.node_a].edge_ids or edge.id not in self.nodes[edge.node_b].edge_ids:
                raise ValueError(f"edge {edge.id} missing symmetric node reference")
            for hex_id in edge.hex_ids:
                if hex_id not in self.hexes:
                    raise ValueError(f"edge {edge.id} references missing hex")

        for node in self.nodes.values():
            for edge_id in node.edge_ids:
                if edge_id not in self.edges:
                    raise ValueError(f"node {node.id} references missing edge")
                edge = self.edges[edge_id]
                if node.id not in (edge.node_a, edge.node_b):
                    raise ValueError(f"node {node.id} has asymmetric edge {edge_id}")
            for hex_id in node.hex_ids:
                if hex_id not in self.hexes:
                    raise ValueError(f"node {node.id} references missing hex")
                if node.id not in self.hexes[hex_id].node_ids:
                    raise ValueError(f"node {node.id} has asymmetric hex {hex_id}")

        for hex_tile in self.hexes.values():
            if len(hex_tile.node_ids) != 6:
                raise ValueError(f"hex {hex_tile.id} does not have six nodes")
            for node_id in hex_tile.node_ids:
                if node_id not in self.nodes:
                    raise ValueError(f"hex {hex_tile.id} references missing node")
                if hex_tile.id not in self.nodes[node_id].hex_ids:
                    raise ValueError(f"hex {hex_tile.id} has asymmetric node {node_id}")

    def to_dict(self) -> dict:
        return {
            "hexes": {str(key): hex_tile.to_dict() for key, hex_tile in self.hexes.items()},
            "nodes": {str(key): node.to_dict() for key, node in self.nodes.items()},
            "edges": {str(key): edge.to_dict() for key, edge in self.edges.items()},
            "robber_hex_id": self.robber_hex_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Board:
        return cls(
            hexes={int(key): Hex.from_dict(value) for key, value in data["hexes"].items()},
            nodes={int(key): Node.from_dict(value) for key, value in data["nodes"].items()},
            edges={int(key): Edge.from_dict(value) for key, value in data["edges"].items()},
            robber_hex_id=int(data["robber_hex_id"]),
        )

    @classmethod
    def create_standard_board(cls, seed: int | None = None) -> Board:
        return create_standard_board(seed=seed)


def create_standard_board(seed: int | None = None) -> Board:
    rng = random.Random(seed)
    coords = [
        (q, r)
        for q in range(-2, 3)
        for r in range(-2, 3)
        if max(abs(q), abs(r), abs(-q - r)) <= 2
    ]
    coords.sort(key=lambda item: (item[1], item[0]))

    resource_types = [
        HexType.LUMBER,
        HexType.BRICK,
        HexType.WOOL,
        HexType.GRAIN,
        HexType.ORE,
        HexType.WOOL,
        HexType.GRAIN,
        HexType.LUMBER,
        HexType.BRICK,
        HexType.DESERT,
        HexType.ORE,
        HexType.GRAIN,
        HexType.WOOL,
        HexType.LUMBER,
        HexType.ORE,
        HexType.BRICK,
        HexType.GRAIN,
        HexType.WOOL,
        HexType.LUMBER,
    ]
    numbers = iter([5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11])
    if seed is not None:
        # Keep the desert at the center for a familiar fixed topology; seed only
        # affects non-desert resource ordering for now.
        non_desert = [hex_type for hex_type in resource_types if hex_type != HexType.DESERT]
        rng.shuffle(non_desert)
        iterator = iter(non_desert)
        resource_types = [HexType.DESERT if hex_type == HexType.DESERT else next(iterator) for hex_type in resource_types]

    hex_specs: list[tuple[int, int, HexType, int | None]] = []
    robber_hex_id = 0
    for index, (q, r) in enumerate(coords):
        hex_type = resource_types[index]
        if hex_type == HexType.DESERT:
            robber_hex_id = index
            hex_specs.append((q, r, hex_type, None))
        else:
            hex_specs.append((q, r, hex_type, next(numbers)))

    corner_keys: dict[tuple[float, float], int] = {}
    hex_corner_keys: list[tuple[tuple[float, float], ...]] = []
    for q, r, _hex_type, _number in hex_specs:
        cx, cy = _hex_center(q, r)
        keys: list[tuple[float, float]] = []
        for corner in range(6):
            angle = math.radians(60 * corner - 30)
            key = (round(cx + math.cos(angle), 6), round(cy + math.sin(angle), 6))
            keys.append(key)
            corner_keys.setdefault(key, -1)
        hex_corner_keys.append(tuple(keys))

    sorted_corners = sorted(corner_keys)
    node_id_by_key = {key: index for index, key in enumerate(sorted_corners)}
    hex_node_ids = [tuple(node_id_by_key[key] for key in keys) for keys in hex_corner_keys]

    edge_hexes: dict[tuple[int, int], list[int]] = {}
    for hex_id, node_ids in enumerate(hex_node_ids):
        for index, node_id in enumerate(node_ids):
            other = node_ids[(index + 1) % 6]
            edge_hexes.setdefault(tuple(sorted((node_id, other))), []).append(hex_id)

    sorted_edges = sorted(edge_hexes)
    edge_id_by_nodes = {edge_nodes: edge_id for edge_id, edge_nodes in enumerate(sorted_edges)}
    edges = {
        edge_id: Edge(id=edge_id, node_a=edge_nodes[0], node_b=edge_nodes[1], hex_ids=tuple(sorted(edge_hexes[edge_nodes])))
        for edge_nodes, edge_id in edge_id_by_nodes.items()
    }

    node_hexes: dict[int, list[int]] = {node_id: [] for node_id in node_id_by_key.values()}
    node_edges: dict[int, list[int]] = {node_id: [] for node_id in node_id_by_key.values()}
    for hex_id, node_ids in enumerate(hex_node_ids):
        for node_id in node_ids:
            node_hexes[node_id].append(hex_id)
    for edge_id, edge in edges.items():
        node_edges[edge.node_a].append(edge_id)
        node_edges[edge.node_b].append(edge_id)

    ports = _assign_ports(edges, node_hexes, sorted_corners)
    nodes = {
        node_id: Node(
            id=node_id,
            hex_ids=tuple(sorted(node_hexes[node_id])),
            edge_ids=tuple(sorted(node_edges[node_id])),
            port=ports.get(node_id),
        )
        for node_id in node_hexes
    }
    hexes = {
        hex_id: Hex(id=hex_id, hex_type=hex_type, number_token=number, node_ids=hex_node_ids[hex_id])
        for hex_id, (_q, _r, hex_type, number) in enumerate(hex_specs)
    }
    board = Board(hexes=hexes, nodes=nodes, edges=edges, robber_hex_id=robber_hex_id)
    board.validate()
    return board


def _hex_center(q: int, r: int) -> tuple[float, float]:
    return (math.sqrt(3) * (q + r / 2), 1.5 * r)


def _assign_ports(
    edges: dict[int, Edge],
    node_hexes: dict[int, list[int]],
    sorted_corners: list[tuple[float, float]],
) -> dict[int, Port]:
    boundary_edges = [
        edge_id
        for edge_id, edge in edges.items()
        if len(set(node_hexes[edge.node_a]).intersection(node_hexes[edge.node_b])) == 1
    ]

    def edge_angle(edge_id: int) -> float:
        edge = edges[edge_id]
        ax, ay = sorted_corners[edge.node_a]
        bx, by = sorted_corners[edge.node_b]
        return math.atan2((ay + by) / 2, (ax + bx) / 2)

    boundary_edges.sort(key=edge_angle)
    specs = [
        Port("generic", None, 3),
        Port("resource", Resource.LUMBER, 2),
        Port("generic", None, 3),
        Port("resource", Resource.BRICK, 2),
        Port("resource", Resource.WOOL, 2),
        Port("generic", None, 3),
        Port("resource", Resource.GRAIN, 2),
        Port("resource", Resource.ORE, 2),
        Port("generic", None, 3),
    ]

    ports: dict[int, Port] = {}
    used_nodes: set[int] = set()
    start_indexes = [int(index * len(boundary_edges) / len(specs)) for index in range(len(specs))]
    for spec, start in zip(specs, start_indexes, strict=True):
        for offset in range(len(boundary_edges)):
            edge = edges[boundary_edges[(start + offset) % len(boundary_edges)]]
            if edge.node_a not in used_nodes and edge.node_b not in used_nodes:
                ports[edge.node_a] = spec
                ports[edge.node_b] = spec
                used_nodes.update({edge.node_a, edge.node_b})
                break
    return ports


def hex_resource(hex_type: HexType) -> Resource | None:
    return HEX_TO_RESOURCE.get(hex_type)

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MapState:
    terrain: dict = field(default_factory=dict)
    resources: dict = field(default_factory=dict)
    buildings: dict = field(default_factory=dict)
    cities: tuple = ()
    villages: frozenset = field(default_factory=frozenset)
    monuments: frozenset = field(default_factory=frozenset)
    lighthouses: frozenset = field(default_factory=frozenset)

    def terrain_at(self, pos):
        return self.terrain.get(pos)

    def resource_at(self, pos):
        return self.resources.get(pos)

    def building_at(self, pos):
        return self.buildings.get(pos)

    def defined_positions(self):
        return set(self.terrain.keys())

    def occupied_positions(self):
        return set(self.buildings.keys()) | self.monuments | self.lighthouses

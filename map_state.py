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

    def territory_ownership(self):
        """Map each defined tile to the id of its owning city. First city claims contested tiles."""
        ownership = {}
        for city in self.cities:
            radius = city['border_level']
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    pos = (city['row'] + dr, city['col'] + dc)
                    if pos in self.terrain and pos not in ownership:
                        ownership[pos] = city['id']
        return ownership

    def tiles_owned_by(self, city_id):
        """Return set of positions owned by a specific city."""
        return {pos for pos, cid in self.territory_ownership().items() if cid == city_id}

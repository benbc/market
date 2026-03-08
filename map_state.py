from dataclasses import dataclass, field


@dataclass(frozen=True)
class MapState:
    terrain: dict = field(default_factory=dict)

    def terrain_at(self, pos):
        return self.terrain.get(pos)

    def defined_positions(self):
        return set(self.terrain.keys())

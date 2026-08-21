import random
from dataclasses import dataclass, field


@dataclass
class Soldier:
    team: int
    x: float
    y: float
    alive: bool = True


@dataclass
class Obstacle:
    x: float
    y: float
    r: float


@dataclass
class World:
    width: float
    height: float
    obstacles: list = field(default_factory=list)
    soldiers: list = field(default_factory=list)

    @classmethod
    def from_level(cls, level: dict, seed=None):
        rng = random.Random(seed)
        world = cls(width=level.get("width", 50.0), height=level.get("height", 30.0))
        for o in level.get("obstacles", []):
            world.obstacles.append(Obstacle(o["x"], o["y"], o["r"]))
        for s in level.get("team1", []):
            world.soldiers.append(Soldier(team=1, x=s["x"], y=s["y"]))
        for s in level.get("team2", []):
            world.soldiers.append(Soldier(team=2, x=s["x"], y=s["y"]))
        return world

    def alive(self, team):
        return [s for s in self.soldiers if s.team == team and s.alive]

    def all_alive(self):
        return [s for s in self.soldiers if s.alive]
from dataclasses import dataclass
import random


@dataclass
class Tile:
    sideLeft: dict
    sideUp: dict
    sideRight: dict
    sideDown: dict
    tag: str

    @staticmethod
    def ParseTiles(tilesAsDict: dict) -> list['Tile']:
        tiles = []
        for tile in tilesAsDict.values():
            tiles.append(Tile(sideUp=tile["up"], sideDown=tile["down"], sideLeft=tile["left"], sideRight=tile["right"], tag=list(tilesAsDict.keys())[list(tilesAsDict.values()).index(tile)]))
        return tiles

    @staticmethod
    def Rotate():
        pass

@dataclass
class Cell:
    position: list
    state: Tile
    possibleStates: list[Tile]

class Grid:
    def __init__(self, width: int, height: int, step: int, tiles: list[Tile]) -> None:
        self.width = width
        self.height = height
        self.step = step
        self.grid: list[Cell] = []
        self.tiles = tiles

        for x in range(0, width + 1, step):
             for y in range(0, height + 1, step):
                  self.grid.append(Cell([x,y], Tile({}, {}, {}, {}, "Unknown"), possibleStates=tiles))


class WaveFunctionCollapse:
    @staticmethod
    def ManualCollapse(cell: 'Cell', state: 'Tile') -> 'Cell':
        cell.state = state
        cell.possibleStates = [cell.state]
        return cell

    @staticmethod
    def Collapse(grid: 'Grid', cell: 'Cell' = None) -> Cell | bool:
        if cell == None:
            toCollapse = WaveFunctionCollapse.Select(grid)
        else: toCollapse = cell
        if len(toCollapse.possibleStates) == 0:
            return False
        toCollapse.state = random.choice(toCollapse.possibleStates)
        toCollapse.possibleStates = [toCollapse.state]
        return toCollapse

    @staticmethod
    def __EdgeCheck(grid: 'Grid', side: str, cell: 'Cell') -> bool:
        match side:
            case "up":
                return cell.position[1] - 50 < 0
            case "down":
                return cell.position[1] + 50 > grid.height
            case "left":
                return cell.position[0] - 50 < 0
            case "right":
                return cell.position[0] + 50 > grid.width


    @staticmethod
    def Propagate(grid: 'Grid', cell: 'Cell'):
        upPos = [cell.position[0], cell.position[1] - grid.step]
        downPos = [cell.position[0], cell.position[1] + grid.step]
        leftPos = [cell.position[0] - grid.step, cell.position[1]]
        rightPos = [cell.position[0] + grid.step, cell.position[1]]
        

        if(not WaveFunctionCollapse.__EdgeCheck(grid, "up", cell)):
            upCell = [x for x in grid.grid if x.position == upPos][0]
        if(not WaveFunctionCollapse.__EdgeCheck(grid, "down", cell)):
            downCell = [x for x in grid.grid if x.position == downPos][0]
        if(not WaveFunctionCollapse.__EdgeCheck(grid, "left", cell)):
            leftCell = [x for x in grid.grid if x.position == leftPos][0]
        if(not WaveFunctionCollapse.__EdgeCheck(grid, "right", cell)):
            rightCell = [x for x in grid.grid if x.position == rightPos][0]

        toRemove = []
        if(not WaveFunctionCollapse.__EdgeCheck(grid, "up", cell)):
            for state in upCell.possibleStates:
                if(state.sideDown != cell.state.sideUp[::-1]):
                    toRemove.append(state)
            upCell.possibleStates = [x for x in upCell.possibleStates if x not in toRemove]
            toRemove.clear()
        if(not WaveFunctionCollapse.__EdgeCheck(grid, "down", cell)):
            for state in downCell.possibleStates:
                if(state.sideUp != cell.state.sideDown[::-1]):
                    toRemove.append(state)
            downCell.possibleStates = [x for x in downCell.possibleStates if x not in toRemove]
            toRemove.clear()
        if(not WaveFunctionCollapse.__EdgeCheck(grid, "left", cell)):
            for state in leftCell.possibleStates:
                if(state.sideRight != cell.state.sideLeft[::-1]):
                    toRemove.append(state)
            leftCell.possibleStates = [x for x in leftCell.possibleStates if x not in toRemove]
            toRemove.clear()
        if(not WaveFunctionCollapse.__EdgeCheck(grid, "right", cell)):
            for state in rightCell.possibleStates:
                if(state.sideLeft != cell.state.sideRight[::-1]):
                    toRemove.append(state)
            rightCell.possibleStates = [x for x in rightCell.possibleStates if x not in toRemove]
            toRemove.clear()

    @staticmethod
    def Select(grid: 'Grid') -> 'Cell':
        lowest = min([cell.possibleStates for cell in grid.grid if cell.state.tag == "Unknown"], key=len)
        return random.choice([cell for cell in grid.grid if cell.possibleStates == lowest and cell.state.tag == "Unknown"])

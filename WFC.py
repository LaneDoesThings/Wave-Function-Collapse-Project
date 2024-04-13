from dataclasses import dataclass
import random


@dataclass
class Tile:
    """Class for storing tile side data for the Wave Function Collapse algorithm

    Attributes:
    sideLeft (dict): Stores the key/value for the left side of the tile
    sideUp (dict): Stores the key/value for the top of the tile
    sideRight (dict): Stores the key/value for the right side of the tile
    sideDown (dict): Stores the key/value for the bottom of the tile
    tag (str): Stores the internal tag of the tile for use when drawing to the screen
    """

    sideLeft: dict
    sideUp: dict
    sideRight: dict
    sideDown: dict
    tag: str

    @staticmethod
    def ParseTiles(tilesAsDict: dict) -> list['Tile']:
        """Takes the tile data as a dictionary and turns it into usable tile data

        Returns:
            list[Tile]: The parsed tiles as a list
        """
        tiles = []
        for tile in tilesAsDict.values():
            tiles.append(Tile(sideUp=tile["up"], sideDown=tile["down"], sideLeft=tile["left"], sideRight=tile["right"], tag=list(tilesAsDict.keys())[list(tilesAsDict.values()).index(tile)]))
        return tiles

@dataclass
class Cell:
    """Class that holds the data for a cell on the Wave Function Collapse Grid

    Attributes:
    position (list): The xy position of the cell as a list of [x,y]
    state (Tile): The current tile state of the cell
    possibleStates (list[Tile]): A list of all the possible tiles that this cell can have
    """
    position: list
    state: Tile
    possibleStates: list[Tile]

class Grid:
    """Class that stores the grid information for the Wave Function Collapse Algorithm
    """
    def __init__(self, width: int, height: int, step: int, tiles: list[Tile]) -> None:
        """Creates a new Grid object that can be used in tandum with the Wave Function Collapse algorithm 

        Args:
            width (int): The width of the grid which should match the width of the application
            height (int): The height of the grid which should match the height of the application
            step (int): The step size for the grid i.e the size of each tile
            tiles (list[Tile]): List of all the tiles that the grid can have
        """
        self.width = width
        self.height = height
        self.step = step
        self.grid: list[Cell] = []
        self.tiles = tiles

        for x in range(0, width + 1, step):
             for y in range(0, height + 1, step):
                  self.grid.append(Cell([x,y], Tile({}, {}, {}, {}, "Unknown"), possibleStates=tiles))


class WaveFunctionCollapse:
    """Implementation of Wave Function Collapse Algorithm with known side data
    and requires use of the Grid class
    """
    @staticmethod
    def ManualCollapse(cell: 'Cell', state: 'Tile') -> 'Cell':
        """Manually collapse a cell to a certain state

        Args:
            cell (Cell): The cell to be collapsed
            state (Tile): The state to collapse the cell to

        Returns:
            Cell: The new cell object that has had its state collapsed
        """
        cell.state = state
        cell.possibleStates = [cell.state]
        return cell

    @staticmethod
    def Collapse(grid: 'Grid', cell: 'Cell' = None) -> Cell | bool:
        """Function to collapse a cell on the grid

        Args:
            grid (Grid): The grid to collapse on
            cell (Cell, optional): Allows a ceratin cell to be collapsed instead of letting the algorithm pick. Defaults to None.

        Returns:
            Cell | bool: Returns a cell if the collapse was successful or False otherwise
        """
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
        """Internal Function to check whether a cell is on the edge of the grid

        Args:
            grid (Grid): The grid to check
            side (str): The side to check ("up", "down", "left", or "right")
            cell (Cell): The Cell that is being checked

        Returns:
            bool: True if it is on the edge False otherwise
        """
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
        """Function to propagate the cell to the rest of the grid

        Args:
            grid (Grid): The grid that will be propagated on
            cell (Cell): The cell to propagate
        """
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
        """Function to select the cell with the least "entropy"
        or the cell that contains the least possible states

        Args:
            grid (Grid): The grid to check on

        Returns:
            Cell: The cell that needs to be collapsed
        """
        lowest = min([cell.possibleStates for cell in grid.grid if cell.state.tag == "Unknown"], key=len)
        return random.choice([cell for cell in grid.grid if cell.possibleStates == lowest and cell.state.tag == "Unknown"])

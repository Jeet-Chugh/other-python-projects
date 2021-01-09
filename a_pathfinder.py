import pygame
import math
from queue import PriorityQueue

from colors import get_color as c

DIMENSIONS = 800
ROWS = 50
WIN = pygame.display.set_mode((DIMENSIONS,DIMENSIONS))
pygame.display.set_caption("Pathfinding Algorithm using Python + A*. By: Jeet Chugh")

class Node():
    def __init__(self, row, col, width, total_rows):
        self.row, self.col = row, col
        self.x, self.y = row * width, col * width
        self.width = width
        self.total_rows = total_rows

        self.color = c('WHITE')

    def get_pos(self):
        return self.row,self.col

    def cond(self,type,state):
        states = {
            'CLOSED' : 'RED',
            'OPEN' : 'GREEN',
            'BARRIER' : 'BLACK',
            'START' : 'ORANGE',
            'END' : 'TURQUOISE'
        }
        if type == 'is':
            return self.color == c(states[state.upper()])
        elif type == 'make':
            if state.upper() == 'PATH':
                self.color = c('PURPLE')
            else:
                self.color = c(states[state.upper()])

    def reset(self):
        self.color = c('WHITE')

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].cond('is','barrier'):
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].cond('is','barrier'):
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].cond('is','barrier'):
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].cond('is','barrier'):
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def heuristics(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.cond('make','path')
        draw()

def algo(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float('inf') for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float('inf') for row in grid for node in row}
    f_score[start] = heuristics(start.get_pos(),end.get_pos())

    open_set_hash = {start}
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            return True
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristics(neighbor.get_pos(),end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor],count,neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.cond('make','open')
        draw()

        if current != start:
            current.cond('make','closed')

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, c('GREY'), (0,i*gap), (width,i*gap))
        for j in range(rows):
            pygame.draw.line(win, c('GREY'), (j*gap,0), (j*gap,width))

def draw(win, grid, rows, width):
    win.fill(c('WHITE'))
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y,x = pos
    row,col = y // gap, x // gap
    return row,col

def main(win, width):
    grid = make_grid(ROWS,width)

    start,end = None,None
    run,started = True,False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:  continue
            if pygame.mouse.get_pressed()[0]:
                row,col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.cond("make","start")
                elif not end and node != start:
                    end = node
                    end.cond("make","end")
                elif node != end and node != start:
                    node.cond("make","barrier")
            elif pygame.mouse.get_pressed()[2]:
                row,col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:  start = None
                elif node == end:  end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algo(lambda: draw(win, grid, ROWS, width), grid, start, end)
                if event.key == pygame.K_c:
                    start, end  = None, None
                    grid = make_grid(ROWS, width)
    pygame.quit()

main(WIN,DIMENSIONS)

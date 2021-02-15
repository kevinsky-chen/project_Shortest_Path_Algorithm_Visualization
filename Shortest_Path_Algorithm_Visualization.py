import pygame
from queue import PriorityQueue


WIDTH = 750
pygame.init()  		# initiate pygame
WIN = pygame.display.set_mode((WIDTH, WIDTH))   # 設定畫布大小
pygame.display.set_caption("Shortest Path Algorithm Visualization")

# 各種顏色
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
SAXE_BLUE = (71, 152, 179)
DODGER_BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
MAUVE = (102, 64, 255)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


clock = pygame.time.Clock()
guide = pygame.image.load("guide.png").convert()   # 加上convert使得pygame執行速度較快
height = 750*guide.get_height()/guide.get_width()  # keep aspect ratio
guide = pygame.transform.scale(guide, (750, int(height)))   # 縮放
guide_rect = guide.get_rect(center=(375, 375))

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == DODGER_BLUE

	def is_open(self):
		return self.color == MAUVE

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == GREEN

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = DODGER_BLUE

	def make_open(self):
		self.color = MAUVE

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = GREEN

	def make_path(self):
		self.color = YELLOW

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):   	# 更新current節點周圍的節點並存入其neighbors陣列中
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): 	# UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():   # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):    # 重建shortest path
	while current in came_from:
		current = came_from[current]
		current.make_path()         # 將該節點塗成黃色的路徑
		draw()

class algorithm:
	def __init__(self, grid, start, end):
		self.grid = grid
		self.start = start
		self.end = end

	def dijkstra(self, draw):
		count = 0
		open_set = PriorityQueue()
		open_set.put((0, count, self.start))  # 等同於c++的push，增加element的意思
		# 0是f(n)，count紀錄節點添加的順序，start是目前節點(該節點物件)
		# priority queue 會根據開頭的數字排序，較小的排較前面

		came_from = {}
		g_score = {spot: float("inf") for row in self.grid for spot in row}
		g_score[self.start] = 0            # 一開始由於目前節點==起點，所以g(n)==0，所以f(n)=g(n)=0

		open_set_hash = {self.start}  # Record elements in the open_set(because it is a queue; unable to traverse though; use this to record what is inside the queue)

		while not open_set.empty():
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			current = open_set.get()[2]  # 拿出節點物件(如同queue從"頭"取出)
			open_set_hash.remove(current)  # 取出對應的物件(利用key移除)

			if current == self.end:
				reconstruct_path(came_from, self.end, draw)
				self.end.make_end()
				self.start.make_start()
				return True

			for neighbor in current.neighbors:
				temp_g_score = g_score[current] + 1  # 照理來講，鄰居相較於current node應該g(n)會大1，因為節點之間的權重是1

				if temp_g_score < g_score[neighbor]:  # we found a better path, so update the g_score
					came_from[neighbor] = current  # 要往neighbor走(因為neighbor的g(n)變小)，把目前走過的節點(current)紀錄起來(用以重建路徑)
					g_score[neighbor] = temp_g_score

					if neighbor not in open_set_hash:
						count += 1
						open_set.put((g_score[neighbor], count, neighbor))
						open_set_hash.add(neighbor)
						neighbor.make_open()

			draw()

			if current != self.start:
				current.make_closed()

		return False

	def astar(self, draw):
		count = 0
		open_set = PriorityQueue()
		open_set.put((0, count, self.start))     # 等同於c++的push，增加element的意思
											# 0是f(n)，count紀錄節點添加的順序，start是目前節點(該節點物件)
											# priority queue 會根據開頭的數字排序，較小的排較前面

		came_from = {}
		g_score = {spot: float("inf") for row in self.grid for spot in row}
		g_score[self.start] = 0
		f_score = {spot: float("inf") for row in self.grid for spot in row}
		f_score[self.start] = h(self.start.get_pos(), self.end.get_pos())   # 一開始由於目前節點==起點，所以g(n)==0，所以f(n)=h(n)

		open_set_hash = {self.start}     # Record elements in the open_set(because it is a queue; unable to traverse though; use this to record what is inside the queue)

		while not open_set.empty():
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			current = open_set.get()[2]       # 拿出節點物件(如同queue從"頭"取出)
			open_set_hash.remove(current)     # 取出對應的物件(利用key移除)

			if current == self.end:
				reconstruct_path(came_from, self.end, draw)
				self.end.make_end()
				self.start.make_start()
				return True

			for neighbor in current.neighbors:
				temp_g_score = g_score[current] + 1       # 照理來講，鄰居相較於current spot應該g(n)會大1，因為節點之間的權重是1

				if temp_g_score < g_score[neighbor]:      # we found a better path, so update the g_score
					came_from[neighbor] = current         # 要往neighbor走(因為neighbor的g(n)變小)，把目前走過的節點(current)紀錄起來(用以重建路徑)
					g_score[neighbor] = temp_g_score
					f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), self.end.get_pos())
					if neighbor not in open_set_hash:
						count += 1
						open_set.put((f_score[neighbor], count, neighbor))
						open_set_hash.add(neighbor)
						neighbor.make_open()

			draw()

			if current != self.start:
				current.make_closed()

		return False


def make_grid(rows, width):   	 # 畫網格各節點(spot)
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):   # 畫網格格線
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, SAXE_BLUE, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, SAXE_BLUE, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()
	clock.tick(120)  		# 設定120ms更新一次地圖狀態


def get_clicked_pos(pos, rows, width):   # 得到滑鼠點擊的位置
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	IS_ASTAR = None     # 選擇AStar或Dijkstra演算法
	GAME_ACTIVE = False   # 是否開啟說明圖(game guide or game instruction)

	ROWS = 30    # 30*30的棋盤
	grid = make_grid(ROWS, width)

	start = None   # 起點spot
	end = None	   # 終點spot

	run = True
	while run:
		if GAME_ACTIVE:
			draw(win, grid, ROWS, width)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False

				if pygame.mouse.get_pressed()[0]:    # LEFT: 選擇spot
					pos = pygame.mouse.get_pos()
					row, col = get_clicked_pos(pos, ROWS, width)
					spot = grid[row][col]
					if not start and spot != end:    # 第一個選擇的spot設定為起點
						start = spot
						start.make_start()

					elif not end and spot != start:    # 第二個選擇的spot設定為終點
						end = spot
						end.make_end()

					elif spot != end and spot != start:     # 第三個以後選擇的spot設定為障礙物
						spot.make_barrier()

				elif pygame.mouse.get_pressed()[2]:       # RIGHT: 取消spot
					pos = pygame.mouse.get_pos()
					row, col = get_clicked_pos(pos, ROWS, width)
					spot = grid[row][col]
					spot.reset()
					if spot == start:
						start = None
					elif spot == end:
						end = None

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_KP1:
						IS_ASTAR = False
					if event.key == pygame.K_KP2:
						IS_ASTAR = True

					if event.key == pygame.K_SPACE and start and end and (IS_ASTAR is not None):
						for row in grid:
							for spot in row:
								spot.update_neighbors(grid)

						algo = algorithm(grid, start, end)
						if IS_ASTAR:
							algo.astar(lambda: draw(win, grid, ROWS, width))
						else:
							algo.dijkstra(lambda: draw(win, grid, ROWS, width))

					if event.key == pygame.K_c:    # c:將地圖清空(clear)
						start = None
						end = None
						grid = make_grid(ROWS, width)

					if event.key == pygame.K_TAB:
						GAME_ACTIVE = not GAME_ACTIVE
		else:     # game instruction(guide)界面
			win.blit(guide, guide_rect)  		# display one surface onto another surface(surface, 位置)
			pygame.display.update()
			clock.tick(120)  # 設定fps的上限

			for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_TAB:
							GAME_ACTIVE = not GAME_ACTIVE

	pygame.quit()

main(WIN, WIDTH)
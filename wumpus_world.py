import random
import copy

class WumpusWorld:
    def __init__(self, size=4):
        self.size = size
        self.grid = [[[] for _ in range(size)] for _ in range(size)]
        self.agent_pos = (0, 0)  #시작 위치를 왼쪽 하단 모서리로 변경 (0,0)
        self.agent_direction = 'East'
        self.arrows = 3
        self.initial_grid = None
        self.generate_world()

    def generate_world(self):
        while True:
            #모든 격자에 대한 좌표 리스트 생성
            all_cells = [(x, y) for x in range(self.size) for y in range(self.size)]
            all_cells.remove((0, 0))  #시작 위치는 안전한 격자로 남겨둠

            #골드의 위치를 무작위로 정함
            gold_pos = random.choice(all_cells)
            all_cells.remove(gold_pos)  #이미 골드가 있는 위치는 제거

            #움퍼스의 위치를 무작위로 정함
            wumpus_pos = random.choice(all_cells)
            all_cells.remove(wumpus_pos)  #이미 움퍼스가 있는 위치는 제거

            #웅덩이의 위치를 무작위로 정함
            pit_pos1 = random.choice(all_cells)
            all_cells.remove(pit_pos1)  #이미 웅덩이가 있는 위치는 제거

            #(1,0)와 (0,1)에 동시에 웅덩이가 배치되지 않도록 함
            if pit_pos1 == (1, 0):
                pit_pos2_candidates = [cell for cell in all_cells if cell != (0, 1)]
            elif pit_pos1 == (0, 1):
                pit_pos2_candidates = [cell for cell in all_cells if cell != (1, 0)]
            else:
                pit_pos2_candidates = all_cells

            if not pit_pos2_candidates:
                continue  #조건을 만족하는 위치가 없으면 다시 시도

            #두 번째 웅덩이 위치 선택
            pit_pos2 = random.choice(pit_pos2_candidates) if random.random() < 0.1 else None
            if pit_pos2:
                all_cells.remove(pit_pos2)  #두 번째 웅덩이 위치 제거

            #각 요소의 위치를 그리드에 할당
            self.grid = [[[] for _ in range(self.size)] for _ in range(self.size)]
            self.grid[gold_pos[0]][gold_pos[1]].append('Glitter')
            self.grid[wumpus_pos[0]][wumpus_pos[1]].append('Wumpus')
            self.grid[pit_pos1[0]][pit_pos1[1]].append('Pit')
            if pit_pos2:
                self.grid[pit_pos2[0]][pit_pos2[1]].append('Pit')

            #웅덩이가 (1, 0)와 (0, 1)에 동시에 있는지 확인
            if not ('Pit' in self.grid[1][0] and 'Pit' in self.grid[0][1]):
                break

        #Wumpus와 Pit의 개수를 각 최대 3개로 제한함
        #추가적인 요소들을 무작위로 배치
        additional_wumpus_count = 1  #이미 하나 배치했으므로 2개 더 배치 가능
        additional_pit_count = 2  #이미 두 개 배치했으므로 1개 더 배치 가능

        for row in range(self.size):
            for col in range(self.size):
                if (row, col) == (0, 0) or (row, col) in [gold_pos, wumpus_pos, pit_pos1, pit_pos2]:
                    continue  #시작 위치와 이미 배치된 위치는 건너뜀

                if random.random() < 0.1 and additional_wumpus_count < 3:
                    if 'Wumpus' not in self.grid[row][col]:  #이미 움퍼스가 있는 위치는 건너뜀
                        self.grid[row][col].append('Wumpus')
                        additional_wumpus_count += 1
                elif random.random() < 0.1 and additional_pit_count < 3:
                    if 'Pit' not in self.grid[row][col]:  #이미 웅덩이가 있는 위치는 건너뜀
                        self.grid[row][col].append('Pit')
                        additional_pit_count += 1

        self.initial_grid = copy.deepcopy(self.grid)

    #그리드 내 위치가 유효한지 확인
    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.size and 0 <= y < self.size

    def display_grid(self, agent_position, agent_direction):
        print("-" * (self.size * 4 + 1))
        for row in range(self.size - 1, -1, -1):
            print("|", end="")
            for col in range(self.size):
                cell = self.grid[row][col]
                symbol = ' '
                if 'Glitter' in cell:
                    symbol += 'G'
                if 'Wumpus' in cell:
                    symbol += 'W'
                if 'Pit' in cell:
                    symbol += 'B'
                if (row, col) == agent_position:
                    symbol += 'A'
                    if agent_direction == 'North':
                        symbol += '^'
                    elif agent_direction == 'East':
                        symbol += '>'
                    elif agent_direction == 'South':
                        symbol += 'v'
                    elif agent_direction == 'West':
                        symbol += '<'
                print(symbol.ljust(3) + "|", end=" ")
            print()
            print("-" * (self.size * 4 + 1))
        
        for row in range(self.size):
            for col in range(self.size):
                cell = self.grid[row][col]
                if (row + 1, col) == agent_position or (row - 1, col) == agent_position or \
                   (row, col + 1) == agent_position or (row, col - 1) == agent_position:
                    if 'Wumpus' in cell:
                        print('Wumpus가 근처에 있습니다.')
                    elif 'Pit' in cell:
                        print('웅덩이가 근처에 있습니다.')
                    elif 'Glitter' in cell:
                        print("금이 근처에 있습니다.")
    
    #로드된 그리드 그대로 저장
    def reset_world(self):
        self.grid = copy.deepcopy(self.initial_grid)

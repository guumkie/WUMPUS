import random

class Agent:
    def __init__(self, start_position):
        self.position = start_position
        self.direction = 'East'
        self.arrows = 3
        self.dead = False
        self.has_gold = False
        self.visited = set()
        self.wumpus_killed = False
        self.previous_states = []
        self.escaped = False
        self.recent_moves = []          #최근 움직임 기록
        self.recent_positions = []     #최근 위치 기록
        self.recent_directions = []
        self.dangerous_paths = set()   #위험한 위치 기록

    def save_state(self):
        self.previous_states.append((self.position, self.direction, self.arrows, self.dead, self.has_gold))

    def display_status(self):
        print(f"\n현재 위치: {self.position}, 방향: {self.direction}, 화살: {self.arrows}, 금 획득: {self.has_gold}")

    #주어진 행동 실행하고 결과 확인
    def execute_action(self, action, world):
        if action == 'GoForward':
            next_position = self.get_next_position()
            if world.is_valid_position(next_position):
                if 'Wumpus' in world.grid[next_position[0]][next_position[1]] or 'Pit' in world.grid[next_position[0]][next_position[1]]:
                    self.turn_right()
                    return False
                self.move_forward(world)
            else:
                print("벽과 충돌")
                self.recent_moves.append('TurnRight')  #최근 이동에 'TurnRight' 추가
                self.turn_right()
                return False

        elif action == 'TurnLeft':
            self.turn_left()
        elif action == 'TurnRight':
            self.turn_right()
        elif action == 'Grab':
            self.grab(world)
        elif action == 'Shoot':
            self.shoot(world)
        elif action == 'Climb':
            self.climb()

        if action != 'Shoot':  #액션이 'Shoot'이 아닌 경우에만 체크
            #에이전트가 현재 위치에서 wumpus와 마주치면 죽음
            if 'Wumpus' in world.grid[self.position[0]][self.position[1]]:
                print("Wumpus에게 죽었습니다.")
                self.dead = True
                self.dangerous_paths.add(frozenset(self.visited))  #위험한 경로 추가
                return True
            #에이전트가 현재 위치에서 웅덩이에 빠지면 죽음
            if 'Pit' in world.grid[self.position[0]][self.position[1]]:
                print("Pit에 빠졌습니다.")
                self.dead = True
                self.dangerous_paths.add(frozenset(self.visited))  #위험한 경로 추가
                return True
        return self.dead

    #현재 방향에 따라 한 칸 앞으로 이동
    def move_forward(self, world):
        #다음 위치 계산
        new_position = self.get_next_position()

        #새로운 위치가 유효한 위치인지 확인하고 이동
        if world.is_valid_position(new_position):
            self.position = new_position        #위치 업데이트
            self.visited.add(self.position)     #방문한 위치에 추가
            self.recent_moves.append('GoForward')  #최근 이동 방향 기록
            if not self.has_gold:
                self.previous_states.append((self.position, self.direction))
        else:
            print("벽과 충돌")
            self.recent_moves.append('TurnRight')  #최근 이동에 'TurnRight' 추가
            self.turn_right()

    def turn_left(self):
        directions = ['North', 'East', 'South', 'West']
        current_index = directions.index(self.direction)
        self.direction = directions[(current_index - 1) % 4]
        self.recent_moves.append('TurnLeft')
        self.recent_directions.append(self.direction)  #변경된 방향 저장
        if len(self.recent_moves) > 4: 
            self.recent_moves.pop(0)
        if len(self.recent_directions) > 4:
            self.recent_directions.pop(0)

    def turn_right(self):
        directions = ['North', 'East', 'South', 'West']
        current_index = directions.index(self.direction)
        self.direction = directions[(current_index + 1) % 4]
        self.recent_moves.append('TurnRight')
        self.recent_directions.append(self.direction)  #변경된 방향 저장
        if len(self.recent_moves) > 4:
            self.recent_moves.pop(0)
        if len(self.recent_directions) > 4:
            self.recent_directions.pop(0)

    def grab(self, world):
        if 'Glitter' in world.grid[self.position[0]][self.position[1]]:
            self.has_gold = True
            world.grid[self.position[0]][self.position[1]].remove('Glitter')
            print("금을 획득했습니다!\n")
            #시작 경로로 이동
            self.return_to_start()

    def shoot(self, world):
        #화살이 남아있는지 확인
        if self.arrows > 0:
            self.arrows -= 1
            print("화살 발사!!")
            #현재 방향에 따라 wumpus 위치 계산
            if self.direction == 'North':
                wumpus_position = (self.position[0] + 1, self.position[1])
            elif self.direction == 'East':
                wumpus_position = (self.position[0], self.position[1] + 1)
            elif self.direction == 'South':
                wumpus_position = (self.position[0] - 1, self.position[1])
            elif self.direction == 'West':
                wumpus_position = (self.position[0], self.position[1] - 1)
            
            #계산한 wumpus 위치가 유효한 위치인지, 그 위치에 wumpus가 있는지 확인
            if world.is_valid_position(wumpus_position) and 'Wumpus' in world.grid[wumpus_position[0]][wumpus_position[1]]:
                print("WUMPUS 사냥 성공!!\n")
                world.grid[wumpus_position[0]][wumpus_position[1]].remove('Wumpus')
                self.wumpus_killed = True
        else:
            print("화살 없음 --> 다 썼음\n")

    def climb(self):
        if self.position == (0, 0):
            if self.has_gold:
                print("금과 함께 탈출 성공!")
                self.escaped = True
            else:
                print("금 없이 탈출하셨네요...")
                self.dead = True
        else:
            print("여기서는 탈출이 안됩니다.")

    #다음에 이동할 위치 계산
    def get_next_position(self):
        #현재 방향에 따라 다음 위치 계산
        if self.direction == 'North':
            return (self.position[0] + 1, self.position[1])
        elif self.direction == 'East':
            return (self.position[0], self.position[1] + 1)
        elif self.direction == 'South':
            return (self.position[0] - 1, self.position[1])
        elif self.direction == 'West':
            return (self.position[0], self.position[1] - 1)

    #다음 행동 선택
    def decide_next_action(self, world):
        #현재 위치의 셀 정보 가져오기
        current_cell = world.grid[self.position[0]][self.position[1]]

        #만약 금을 가지고 있다면, 출발 위치로 돌아가 탈출 시도
        if self.has_gold:
            return self.return_to_start()

        #현재 위치에 금이 있다면 금을 잡기
        if 'Glitter' in current_cell:
            return 'Grab'
        
        #에이전트가 바라보는 방향의 다음 셀 계산
        next_position = self.get_next_position()

        #화살이 남아있는 경우, 에이전트가 바라보는 방향의 다음 셀과 인접한 셀에서 wumpus가 있는지 확인
        if self.arrows > 0:
            if next_position and world.is_valid_position(next_position) and 'Wumpus' in world.grid[next_position[0]][next_position[1]]:
                return 'Shoot'
            for direction, cell in self.get_adjacent_cells().items():
                if world.is_valid_position(cell) and 'Wumpus' in world.grid[cell[0]][cell[1]]:
                    self.direction = direction
                    return 'Shoot'

        #인접한 칸에서 금이 있으면 이동
        for direction, cell in self.get_adjacent_cells().items():
            if world.is_valid_position(cell) and 'Glitter' in world.grid[cell[0]][cell[1]]:
                self.direction = direction
                return 'GoForward'

        #에이전트의 네 방향(앞, 뒤, 왼쪽, 오른쪽)에 있는 장애물 검사
        safe_directions = self.get_safe_directions(world)

        #에이전트가 바라보는 방향에 웅덩이가 있다면 회피
        if next_position and world.is_valid_position(next_position) and 'Pit' in world.grid[next_position[0]][next_position[1]]:
            self.turn_right()
            next_position = self.get_next_position()
            #네 방향 중 안전한 위치로 이동
            for direction, position in safe_directions:
                if world.is_valid_position(position) and 'Pit' not in world.grid[position[0]][position[1]] and 'Wumpus' not in world.grid[position[0]][position[1]]:
                    self.direction = direction
                    return 'GoForward'

        #네 방향 중 안전한 위치로 이동
        for direction, position in safe_directions:
            if world.is_valid_position(position) and 'Pit' not in world.grid[position[0]][position[1]] and 'Wumpus' not in world.grid[position[0]][position[1]]:
                self.direction = direction
                return 'GoForward'

        #무한 루프 감지
        if self.detect_loop():
            return 'TurnRight'

        #유효한 이동이 없으면 무작위로 방향을 전환
        valid_moves = [direction for direction, cell in self.get_adjacent_cells().items() if world.is_valid_position(cell)]
        if not valid_moves:
            return random.choice(['TurnLeft', 'TurnRight'])

        #에이전트 마지막 움직임이 'TurnLeft'가 아니면 'TurnLeft' 반환
        return 'TurnLeft' if self.recent_moves[-1] != 'TurnLeft' else 'TurnRight'

    #에이전트의 현재 방향 기준으로 왼쪽 방향
    def get_left_direction(self):
        directions = ['North', 'East', 'South', 'West']
        current_index = directions.index(self.direction)
        return directions[(current_index - 1) % 4]

    #에이전트의 현재 방향 기준으로 오른쪽 방향
    def get_right_direction(self):
        directions = ['North', 'East', 'South', 'West']
        current_index = directions.index(self.direction)
        return directions[(current_index + 1) % 4]

    #에이전트의 현재 방향 기준으로 뒤쪽 방향
    def get_backward_direction(self):
        directions = ['North', 'East', 'South', 'West']
        current_index = directions.index(self.direction)
        return directions[(current_index + 2) % 4]

    # 에이전트의 현재 방향 기준으로 뒤쪽 위치 계산
    def get_backward_position(self):
        if self.direction == 'North':
            return (self.position[0] - 1, self.position[1])
        elif self.direction == 'East':
            return (self.position[0], self.position[1] - 1)
        elif self.direction == 'South':
            return (self.position[0] + 1, self.position[1])
        elif self.direction == 'West':
            return (self.position[0], self.position[1] + 1)

    #에이전트의 인접한 칸의 위치 목록
    def get_adjacent_cells(self):
        return {
            'North': (self.position[0] + 1, self.position[1]),
            'South': (self.position[0] - 1, self.position[1]),
            'East': (self.position[0], self.position[1] + 1),
            'West': (self.position[0], self.position[1] - 1)
        }

    #에이전트의 네 방향(앞, 뒤, 왼쪽, 오른쪽) 중 안전한 방향 반환
    def get_safe_directions(self, world):
        forward_position = self.get_next_position()
        backward_position = self.get_backward_position()
        left_position = self.get_adjacent_cells()[self.get_left_direction()]
        right_position = self.get_adjacent_cells()[self.get_right_direction()]

        return [
            (self.direction, forward_position),
            (self.get_left_direction(), left_position),
            (self.get_right_direction(), right_position),
            (self.get_backward_direction(), backward_position)
        ]

    #시작 지점으로 이동
    def return_to_start(self):
        if self.position == (0, 0):
            return 'Climb'
        else:
            if self.position[0] > 0:
                self.direction = 'South'
            elif self.position[1] > 0:
                self.direction = 'West'
            return 'GoForward'

    #최근 위치와 움직임 패턴을 체크하여 무한 루프 감지
    def detect_loop(self):
        #충분한 데이터가 없으면 무한 루프가 아님을 반환
        if len(self.recent_positions) < 4:
            return False

        #최근 3개의 위치 확인
        last_positions = [self.recent_positions[-i] for i in range(1, 4)]
        last_directions = [self.recent_directions[-i] for i in range(1, 4)]

        #같은 위치, 같은 방향으로 3번 이상 머물면 무한 루프 감지
        if (last_positions[0] == last_positions[1] == last_positions[2]) and \
            (last_directions[0] == last_directions[1] == last_directions[2]):
            self.clear_recent_history()
            print("Debug - 무한 루프 감지: 같은 위치에 같은 방향으로 3번 머물렀습니다!\n")
            return True

        #최근 6번의 움직임 패턴 확인
        last_moves = self.recent_moves[-6:]
        move_patterns = [
            ['North', 'South', 'North', 'South'],
            ['South', 'North', 'South', 'North'],
            ['East', 'West', 'East', 'West'],
            ['West', 'East', 'West', 'East'],
            ['West', 'South', 'West', 'South'],
            ['South', 'West', 'South', 'West'],
            ['East', 'South', 'East', 'Sout'],
            ['South', 'East' , 'South', 'East'],
            ['Norht', 'East', 'North', 'East'],
            ['East', 'North', 'East', 'North'],
            ['Norht', 'West', 'North', 'West'],
            ['West', 'North', 'West', 'North'],
            ['GoForward', 'TurnLeft', 'GoForward', 'TurnRight'],
            ['GoForward', 'TurnRight', 'GoForward', 'TurnLeft'],
            ['TurnLeft', 'TurnRight', 'TurnLeft', 'TurnRight'],
            ['TurnRight', 'TurnLeft', 'TurnRight', 'TurnLeft'],
            ['GoForward', 'GoForward', 'TurnRight', 'GoForward', 'GoForward', 'TurnRight'],
            ['GoForward', 'GoForward', 'TurnLeft', 'GoForward', 'GoForward', 'TurnLeft']
        ]
        if any(last_moves == pattern for pattern in move_patterns):
            self.clear_recent_history()
            print("Debug - 무한 루프 감지: 반복 패턴을 탐지했습니다!\n")
            return True

        return False

    #최근 기록 정리
    def clear_recent_history(self):
        self.recent_moves.clear()
        self.recent_positions.clear()
        self.recent_directions.clear()

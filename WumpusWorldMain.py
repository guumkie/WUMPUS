from wumpus_world import WumpusWorld
from agent import Agent
import copy
import random

def main():
    world = WumpusWorld()
    agent = Agent(start_position=(0, 0))
    agent.world = world

    while True:
        world.display_grid(agent.position, agent.direction)
        agent.display_status()

        agent.recent_positions.append(agent.position)  #현재 위치를 최근 위치 리스트에 추가
        agent.recent_directions.append(agent.direction) #현재 방향을 최근 방향 리스트에 추가
        if len(agent.recent_positions) > 6 and len(agent.recent_directions) > 6:  #최근 위치 리스트가 너무 길어지지 않도록 제한
            agent.recent_positions.pop(0)
            agent.recent_directions.pop(0)

        agent.save_state()
        
        #자동으로 다음 행동 결정
        action = agent.decide_next_action(world)
        print(f"Selected action: {action}\n")

        #무한 루프 감지되면 방향 바꾸기
        if agent.detect_loop():
            turn_action = 'TurnRight'
            agent.execute_action(turn_action, world)
            continue

        #액션을 실행하고 에이전트가 죽었는지 확인
        agent_dead = agent.execute_action(action, world)

        if agent.escaped:
            break
  
        if agent_dead:
            print("에이전트가 죽었습니다. 게임 오버!")
            choice = input("게임을 끝내시겠습니까? (yes/no): ")  
            if choice.lower() == 'yes':
                print("게임을 종료합니다.")
                break
            else:
                print("에이전트가 시작 위치로 돌아갑니다.")
                agent.position = (0, 0)
                agent.direction = 'East'
                agent.dead = False
                agent.visited = set()
                agent.visited.add((0, 0))
                agent.has_gold = False
                agent.arrows = 3
                agent.recent_moves = []
                agent.recent_positions = []
                agent.recent_directions = []
                agent.previous_states = []
                world.reset_world()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
贪吃蛇小游戏 - Python 实现
使用 Pygame 库
"""

import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# 游戏常量
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
GRAY = (40, 40, 40)

# 方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    """贪吃蛇类"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置蛇的状态"""
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.score = 0
        self.grow_pending = 2  # 初始长度
        
    def get_head_position(self):
        """获取蛇头位置"""
        return self.positions[0]
    
    def turn(self, point):
        """改变方向"""
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return  # 不能直接反向
        self.direction = point
    
    def move(self):
        """移动蛇"""
        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_position = (new_x, new_y)
        
        # 检查是否撞到自己
        if new_position in self.positions[1:]:
            return False  # 游戏结束
        
        self.positions.insert(0, new_position)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
            
        return True  # 游戏继续
    
    def grow(self):
        """蛇增长"""
        self.grow_pending += 1
        self.length += 1
        self.score += 10
    
    def draw(self, surface):
        """绘制蛇"""
        for i, p in enumerate(self.positions):
            rect = pygame.Rect(p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            # 蛇头用不同颜色
            if i == 0:
                pygame.draw.rect(surface, BLUE, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)
            else:
                # 身体渐变颜色
                color_intensity = max(50, 255 - i * 10)
                body_color = (0, color_intensity, 0)
                pygame.draw.rect(surface, body_color, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)

class Food:
    """食物类"""
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
    
    def randomize_position(self):
        """随机生成食物位置"""
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                         random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        """绘制食物"""
        rect = pygame.Rect(self.position[0] * GRID_SIZE, 
                          self.position[1] * GRID_SIZE, 
                          GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)
        
        # 添加食物内部的细节
        inner_rect = pygame.Rect(
            self.position[0] * GRID_SIZE + 4,
            self.position[1] * GRID_SIZE + 4,
            GRID_SIZE - 8,
            GRID_SIZE - 8
        )
        pygame.draw.rect(surface, (255, 200, 200), inner_rect)

class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("贪吃蛇小游戏 - Python 实现")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
        self.paused = False
    
    def draw_grid(self):
        """绘制网格"""
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y), 1)
    
    def draw_score(self):
        """绘制分数"""
        score_text = self.font.render(f"分数: {self.snake.score}", True, WHITE)
        length_text = self.font.render(f"长度: {self.snake.length}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(length_text, (WIDTH - 150, 10))
    
    def draw_instructions(self):
        """绘制操作说明"""
        instructions = [
            "方向键: 控制移动",
            "空格键: 暂停/继续",
            "R: 重新开始",
            "ESC: 退出游戏"
        ]
        
        for i, text in enumerate(instructions):
            instruction = self.small_font.render(text, True, WHITE)
            self.screen.blit(instruction, (10, HEIGHT - 100 + i * 25))
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("游戏结束!", True, RED)
        score_text = self.font.render(f"最终分数: {self.snake.score}", True, WHITE)
        restart_text = self.font.render("按 R 重新开始", True, GREEN)
        
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
    
    def check_food_collision(self):
        """检查是否吃到食物"""
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.food.randomize_position()
            
            # 确保食物不出现在蛇身上
            while self.food.position in self.snake.positions:
                self.food.randomize_position()
    
    def run(self):
        """运行游戏主循环"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    
                    if event.key == pygame.K_r:
                        self.snake.reset()
                        self.food.randomize_position()
                        self.game_over = False
                        self.paused = False
                    
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    
                    if not self.paused and not self.game_over:
                        if event.key == pygame.K_UP:
                            self.snake.turn(UP)
                        elif event.key == pygame.K_DOWN:
                            self.snake.turn(DOWN)
                        elif event.key == pygame.K_LEFT:
                            self.snake.turn(LEFT)
                        elif event.key == pygame.K_RIGHT:
                            self.snake.turn(RIGHT)
            
            # 清屏
            self.screen.fill(BLACK)
            
            # 绘制网格
            self.draw_grid()
            
            if not self.paused and not self.game_over:
                # 移动蛇
                if not self.snake.move():
                    self.game_over = True
                
                # 检查食物碰撞
                self.check_food_collision()
            
            # 绘制游戏元素
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # 绘制分数和说明
            self.draw_score()
            self.draw_instructions()
            
            # 绘制暂停或游戏结束画面
            if self.paused:
                pause_text = self.font.render("游戏暂停 - 按空格继续", True, YELLOW)
                self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
            
            if self.game_over:
                self.draw_game_over()
            
            # 更新屏幕
            pygame.display.flip()
            self.clock.tick(FPS)

def main():
    """主函数"""
    print("贪吃蛇游戏启动中...")
    print("操作说明:")
    print("  方向键: 控制蛇的移动")
    print("  空格键: 暂停/继续游戏")
    print("  R键: 重新开始游戏")
    print("  ESC键: 退出游戏")
    print()
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"游戏运行出错: {e}")
        pygame.quit()

if __name__ == "__main__":
    main()

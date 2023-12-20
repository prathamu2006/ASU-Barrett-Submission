import pygame
import sys
import random
import time

pygame.init()

width, height = 640, 480
grid_size = 20
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
brownDark = (139, 69, 19)

snake = [(100, 100), (80, 100)]
snakeDir = (grid_size, 0)

food = (300, 200)

applesEaten = 0
score = 0

clock = pygame.time.Clock()

startTime = time.time()

def drawSnake(snake):
    for i, segment in enumerate(snake):
        pygame.draw.rect(screen, green if i % 2 == 0 else (0, 200, 0), (segment[0], segment[1], grid_size, grid_size))

def drawFood(food, color):
    pygame.draw.rect(screen, color, (food[0], food[1], grid_size, grid_size))

def drawApplesEaten(applesEaten):
    font = pygame.font.Font(None, 24)
    applesText = font.render(f"Apples: {applesEaten}", True, white)
    screen.blit(applesText, (width - 150, 10))

def drawBorder():
    pygame.draw.rect(screen, brownDark, (0, 0, width, grid_size * 2), 0)
    pygame.draw.rect(screen, brownDark, (0, height - grid_size * 2, width, grid_size * 2), 0)
    pygame.draw.rect(screen, brownDark, (0, 0, grid_size * 2, height), 0)
    pygame.draw.rect(screen, brownDark, (width - grid_size * 2, 0, grid_size * 2, height), 0)

def displayGameOver(score, applesEaten):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Game Over! Final Score: {score} (Apples Eaten: {applesEaten})", True, brownDark)
    screen.blit(text, (50, height // 2))
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    sys.exit()

def increaseSpeed():
    global clock
    clock.tick(12)

def spawnObstacle():
    global obstacleActive, obstacle
    if applesEaten >= 10 and not obstacleActive:
        obstacle = (random.randrange(2, (width - grid_size * 2) // grid_size - 1) * grid_size, random.randrange(2, (height - grid_size * 2) // grid_size - 1) * grid_size)
        obstacleActive = True

def drawObstacle(obstacle):
    pygame.draw.rect(screen, red, (obstacle[0], obstacle[1], grid_size, grid_size))

def resetGame():
    global snake, snakeDir, food, score, applesEaten, startTime
    snake = [(100, 100), (80, 100)]
    snakeDir = (grid_size, 0)
    food = (300, 200)
    score = 0
    applesEaten = 0
    startTime = time.time()

def main():
    global snake, snakeDir, food, score, applesEaten, startTime, obstacleActive, obstacle

    obstacleActive = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                displayGameOver(score, applesEaten)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and snakeDir != (0, grid_size):
            snakeDir = (0, -grid_size)
        if keys[pygame.K_DOWN] and snakeDir != (0, -grid_size):
            snakeDir = (0, grid_size)
        if keys[pygame.K_LEFT] and snakeDir != (grid_size, 0):
            snakeDir = (-grid_size, 0)
        if keys[pygame.K_RIGHT] and snakeDir != (-grid_size, 0):
            snakeDir = (grid_size, 0)

        newHead = (snake[0][0] + snakeDir[0], snake[0][1] + snakeDir[1])

        if (newHead[0] < grid_size * 2 or newHead[0] >= width - grid_size * 2 or newHead[1] < grid_size * 2 or newHead[1] >= height - grid_size * 2):
            displayGameOver(score, applesEaten)

        if newHead == food:
            applesEaten += 1
            score += 10

            if applesEaten % 3 == 0:
                increaseSpeed()
            spawnObstacle()

            snake.insert(0, newHead)

            screen.fill(white)
            drawBorder()
            drawFood(food, red)

            if obstacleActive:
                drawObstacle(obstacle)

            drawSnake(snake)
            drawApplesEaten(applesEaten)
            pygame.display.flip()

            food = (random.randrange(2, (width - grid_size * 2) // grid_size - 1) * grid_size, random.randrange(2, (height - grid_size * 2) // grid_size - 1) * grid_size)
        else:
            snake.pop()
            snake.insert(0, newHead)

            screen.fill(white)
            drawBorder()
            drawFood(food, red)

            if obstacleActive:
                drawObstacle(obstacle)

            drawSnake(snake)
            drawApplesEaten(applesEaten)
            pygame.display.flip()

        clock.tick(10)

main()

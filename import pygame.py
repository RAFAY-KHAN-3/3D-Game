import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import time

# Define cube vertices for the player and collectibles
vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
)

edges = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7)
)

# Draw a cube
def draw_cube(position, color):
    glPushMatrix()
    glTranslatef(*position)
    glColor3f(*color)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    glPopMatrix()

# Draw walls
def draw_walls(walls):
    for wall in walls:
        draw_cube(wall, (0, 0, 1))  # Blue walls

# Check collision with walls
def check_collision(player_position, walls):
    for wall in walls:
        dist = sum([(a - b) ** 2 for a, b in zip(player_position, wall)]) ** 0.5
        if dist < 2:
            return True
    return False

# Display text using Pygame (overlaying on OpenGL)
def render_text_overlay(screen, font, text, position, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Show intro screen
def show_intro():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Pygame 2D window
    pygame.display.set_caption("Maze Adventure Intro")
    font = pygame.font.SysFont('Arial', 36)
    clock = pygame.time.Clock()
    intro = True

    # Load and scale logo
    logo = pygame.image.load(r"C:\Users\ABDUL RAFAY ALI KHAN\Downloads\GameCube-Symbol.png")
    logo = pygame.transform.scale(logo, (300, 200))
    angle = 0

    while intro:
        screen.fill((0, 0, 0))

        # Draw rotating logo
        rotated_logo = pygame.transform.rotate(logo, angle)
        rect = rotated_logo.get_rect(center=(400, 300))
        screen.blit(rotated_logo, rect.topleft)

        # Render text
        render_text_overlay(screen, font, "Welcome to Maze Adventure!", (200, 100), (0, 255, 0))
        render_text_overlay(screen, font, "Press ANY key to start", (250, 500), (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                intro = False

        pygame.display.flip()
        angle += 2  # Rotate the logo
        clock.tick(30)

    pygame.display.quit()  # Close intro screen

# Main game loop
def main():
    # Show intro screen
    show_intro()

    # Initialize OpenGL context
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Maze Adventure")
    font = pygame.font.SysFont('Arial', 24)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -20)

    # Initialize variables
    player_position = [0, 0, 0]
    speed = 0.1
    movement = [0, 0, 0]
    level = 1
    score = 0
    timer = 60  # 60 seconds countdown
    collectibles = [(random.randint(-5, 5), 0, random.randint(-15, -5)) for _ in range(5)]
    walls = [(3, 0, -10), (-3, 0, -10), (0, 0, -5), (5, 0, -3), (0, 0, -3)]

    # Game loop
    clock = pygame.time.Clock()
    start_time = time.time()

    while True:
        elapsed_time = time.time() - start_time
        timer = max(0, 60 - int(elapsed_time))  # Update timer
        if timer == 0:
            print("Time's up! Game Over!")
            pygame.quit()
            quit()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            movement[0] = -speed
        elif keys[pygame.K_RIGHT]:
            movement[0] = speed
        else:
            movement[0] = 0

        if keys[pygame.K_UP]:
            movement[2] = -speed
        elif keys[pygame.K_DOWN]:
            movement[2] = speed
        else:
            movement[2] = 0

        # Update player position
        player_position[0] += movement[0]
        player_position[2] += movement[2]

        # Collision with walls
        if check_collision(player_position, walls):
            player_position[0] -= movement[0]
            player_position[2] -= movement[2]

        # Collect collectibles
        collected = False
        for c in collectibles:
            dist = sum([(a - b) ** 2 for a, b in zip(player_position, c)]) ** 0.5
            if dist < 2:
                collectibles.remove(c)
                score += 1
                collected = True
                break

        # Level progression
        if not collectibles and collected:  # Level up when all collectibles are gone
            level += 1
            speed += 0.02  # Increase speed each level
            collectibles = [(random.randint(-5, 5), 0, random.randint(-15, -5)) for _ in range(5 + level)]
            walls = [(random.randint(-5, 5), 0, random.randint(-15, -5)) for _ in range(5 + level)]

        # Render 3D objects
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_cube(player_position, (1, 0, 0))  # Draw player
        draw_walls(walls)  # Draw walls
        for collectible in collectibles:
            draw_cube(collectible, (0, 1, 0))  # Green collectibles

        # Render 2D overlay (timer, score, level)
        screen_2d = pygame.display.get_surface()
        glDisable(GL_DEPTH_TEST)  # Disable depth test for 2D rendering
        render_text_overlay(screen_2d, font, f"Timer: {timer}s", (10, 10), (255, 255, 255))
        render_text_overlay(screen_2d, font, f"Score: {score}", (10, 40), (255, 255, 255))
        render_text_overlay(screen_2d, font, f"Level: {level}", (10, 70), (255, 255, 255))
        pygame.display.flip()
        glEnable(GL_DEPTH_TEST)  # Re-enable depth test for 3D rendering

        clock.tick(60)

# Run the game
if __name__ == "__main__":
    main()

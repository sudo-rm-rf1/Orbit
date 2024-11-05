import pygame, sys
import math
import os
import random
from datetime import datetime 

planets = {}
count = 0
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_width(), screen.get_height()
fps = pygame.time.Clock()
counter = 0
centre = (width // 2, height // 2)
show_axes, show_lines = False, False
tick = 60
lines = []

star_update_interval = 50
stars_counter = 0

stars = [(random.randint(0, width), random.randint(0, height), random.choice([1, 2])) for _ in range(100)]

def draw_background():
    for y in range(height):
        color = (0, 0, int(125 * (y / height)))
        pygame.draw.line(screen, color, (0, y), (width, y))

def update_stars():
    global stars
    stars = [(x, y, random.choice([1, 2])) for x, y, z in stars]

def draw_stars():
    for x, y, z in stars:
        pygame.draw.circle(screen, (255, 255, 255), (x, y), z)

planet_colors = [(100, 149, 237), (255, 69, 0), (34, 139, 34), (238, 130, 238)]
planet_sizes = [8, 12, 10, 6]

def from_centre(x, y):
    return (centre[0] + x, centre[1] - y)

def render_planet(planet, color, radius):
    x, y = from_centre(planet["x"], planet["y"])
    pygame.draw.circle(screen, color, (x, y), radius)
    for i in range(1, 3):
        pygame.draw.circle(screen, color + (100 // i,), (x, y), radius + i * 2)

def render_sun():
    sun_color = (253, 184, 19)
    pygame.draw.circle(screen, sun_color, centre, 30)
    for i in range(1, 4):
        pygame.draw.circle(screen, sun_color + (150 // i,), centre, 30 + i * 15)

def render_instructions():
    font = pygame.font.SysFont("monospace", 20)
    instructions = [
        "Press 'S' to save a screenshot.",
        "Press 'A' to toggle axes.",
        "Press 'L' to toggle orbit lines.",
        "Press '+' or '-' to adjust speed.",
        "Press 'R' to reset planets.",
        "Click to add planets."
    ]
    for i, text in enumerate(instructions):
        screen.blit(font.render(text, True, (255, 255, 255)), (10, 10 + i * 25))

def render():
    draw_background()
    draw_stars()

    for i, (planet_name, planet) in enumerate(planets.items()):
        planet["angle"] += planet["omega"]
        planet["x"], planet["y"] = (
            planet["a"] * math.cos(planet["angle"]),
            planet["a"] * math.sin(planet["angle"]),
        )
        color = planet_colors[i % len(planet_colors)]
        size = planet_sizes[i % len(planet_sizes)]
        render_planet(planet, color, size)

        pygame.draw.circle(screen, (0, 79, 71), centre, int(planet["a"]), 1)

    render_sun()
    render_instructions()

    if count > 1 and show_lines:
        for i in range(1, count):
            pygame.draw.line(
                screen,
                (255, 255, 255),
                from_centre(planets[str(i)]["x"], planets[str(i)]["y"]),
                from_centre(planets[str(i + 1)]["x"], planets[str(i + 1)]["y"]),
            )

        if counter % 6 == 0:
            for k in range(1, count):
                lines.append((
                    from_centre(planets[str(k)]["x"], planets[str(k)]["y"]),
                    from_centre(planets[str(k + 1)]["x"], planets[str(k + 1)]["y"])
                ))

        for line in lines:
            pygame.draw.line(screen, (255, 255, 255), line[0], line[1])

    if show_axes:
        pygame.draw.line(screen, (0, 255, 0), (0, height // 2), (width, height // 2))
        pygame.draw.line(screen, (0, 255, 0), (width // 2, 0), (width // 2, height))

    font = pygame.font.SysFont("monospace", 15)
    radius = round(math.sqrt((centre[0] - pygame.mouse.get_pos()[0]) ** 2 + (centre[1] - pygame.mouse.get_pos()[1]) ** 2))
    ang = math.atan2(centre[1] - pygame.mouse.get_pos()[1], pygame.mouse.get_pos()[0] - centre[0])
    screen.blit(font.render(f"Radius: {radius}", 1, (255, 255, 255)), pygame.mouse.get_pos())
    screen.blit(font.render(f"Angle: {round(math.degrees(ang))}", 1, (255, 255, 255)), (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] + 20))

while True:
    counter += 1
    stars_counter += 1 

    if stars_counter >= star_update_interval:
        update_stars()
        stars_counter = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_q] or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                if not os.path.isdir("images"):
                    os.makedirs("images")
                pygame.image.save(screen, f"images/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png")
            elif event.key == pygame.K_a:
                show_axes = not show_axes
            elif event.key == pygame.K_l:
                show_lines = not show_lines
            elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                tick += 10 if tick < 30 else 30
            elif event.key == pygame.K_MINUS:
                tick = max(10, tick - (10 if tick <= 30 else 30))
            elif event.key == pygame.K_r:
                count, planets, lines = 0, {}, []
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            count += 1
            rad = math.sqrt((centre[0] - mouse_pos[0]) ** 2 + (centre[1] - mouse_pos[1]) ** 2)
            ang = math.atan2(centre[1] - mouse_pos[1], mouse_pos[0] - centre[0])
            planets[str(count)] = {"a": rad, "angle": ang, "omega": math.sqrt(1 / rad ** 3) * 90, "x": mouse_pos[0], "y": mouse_pos[1]}

    render()
    pygame.display.update()
    fps.tick(tick)

import pygame
import random
import requests
import os

# Inicializa o Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Labirinto Florestal")

movement_area = pygame.Rect(100, 100, 1100, 400)

# Carregar  imagem do Player
player_img = pygame.image.load('frontend/assets/images/player.png').convert_alpha()
player_img = pygame.transform.scale(player_img, (75,75))

# Configurações gerais
player_speed = 5
player_width, player_height = 75,75  # Tamanho fixo do jogador
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Carrega os assets para cada fase
assets = {
    1: {
        "background": pygame.image.load('frontend/assets/images/Background-Floresta.png'),
        "obstacle": pygame.image.load('frontend/assets/images/Urso.png'),
        "random_obstacle": pygame.image.load('frontend/assets/images/Urso-Mal.png'),
        "goal": pygame.image.load('frontend/assets/images/Burrito.png'),
    },
    2: {
        "background": pygame.image.load('frontend/assets/images/Background-Praia.png'),
        "obstacle": pygame.image.load('frontend/assets/images/Carangueijo.png'),
        "random_obstacle": pygame.image.load('frontend/assets/images/Carangueijo-Mal.png'),
        "goal": pygame.image.load('frontend/assets/images/Burrito.png'),
    },
    3: {
        "background": pygame.image.load('frontend/assets/images/Background-Rodovia.png'),
        "obstacle": pygame.image.load('frontend/assets/images/Carro.png'),
        "random_obstacle": pygame.image.load('frontend/assets/images/Carro-Mal.png'),
        "goal": pygame.image.load('frontend/assets/images/Burrito.png'),
    }
}

# Configurações das fases
phases = [
    {  # Fase 1
        "player_start": (50, 260),
        "goal": (1050, 280),
        "obstacles": [pygame.Rect(200, 200, 85, 100), pygame.Rect(350, 400, 85, 100), pygame.Rect(500, 150, 85, 100), pygame.Rect(650, 300, 85, 100), pygame.Rect(900, 220, 85, 100)],
        "bonus_points": [pygame.Rect(150, 150, 20, 20), pygame.Rect(400, 400, 20, 20)],
    },
    {  # Fase 2
        "player_start": (50, 260),
        "goal": (1050, 280),
        "obstacles": [pygame.Rect(100, 100, 85, 100), pygame.Rect(500, 100, 85, 100), pygame.Rect(600, 400, 85, 100), pygame.Rect(600, 400, 85, 100), pygame.Rect(600, 400, 85, 100), pygame.Rect(600, 400, 85, 100), pygame.Rect(600, 400, 85, 100)],
        "bonus_points": [pygame.Rect(200, 200, 20, 20), pygame.Rect(350, 450, 20, 20), pygame.Rect(650, 300, 20, 20)],
    },
    {  # Fase 3
        "player_start": (50, 260),
        "goal": (1050, 280),
        "obstacles": [pygame.Rect(300, 200, 85, 100), pygame.Rect(400, 300, 85, 100), pygame.Rect(600, 150, 85, 100), pygame.Rect(200, 500, 85, 100)],
        "bonus_points": [pygame.Rect(150, 350, 20, 20), pygame.Rect(450, 250, 20, 20), pygame.Rect(500, 500, 20, 20)],
    }
]

# Variáveis de jogo
current_phase = 1
player_x, player_y = 0, 0
score = 0
time_start = pygame.time.get_ticks()
random_obstacle = None

# Função para carregar a fase atual
def load_phase(phase):
    global player_x, player_y, goal, obstacles, bonus_points, random_obstacle, background_img, obstacle_img, random_obstacle_img, goal_img

    phase_data = phases[phase - 1]
    player_x, player_y = phase_data["player_start"]
    goal = pygame.Rect(*phase_data["goal"], 50, 50)
    obstacles = phase_data["obstacles"]
    bonus_points = phase_data["bonus_points"]

    # Carregar assets específicos da fase
    background_img = pygame.transform.scale(assets[phase]["background"], (SCREEN_WIDTH, SCREEN_HEIGHT))
    obstacle_img = pygame.transform.scale(assets[phase]["obstacle"], (85, 100))
    random_obstacle_img = pygame.transform.scale(assets[phase]["random_obstacle"], (70, 70))
    goal_img = pygame.transform.scale(assets[phase]["goal"], (70, 70))

    # Posicionar o obstáculo aleatório
    random_obstacle = pygame.Rect(
        random.randint(SCREEN_WIDTH - 1100, SCREEN_WIDTH - 200),
        random.randint(SCREEN_HEIGHT - 400, SCREEN_HEIGHT - 200),
        40,
        40
    )

# Carrega a primeira fase
load_phase(current_phase)

# Função principal do jogo
running = True
while running:
    # Carregar o fundo
    screen.blit(background_img, (0, 0))

    # Calcular tempo decorrido
    elapsed_time = (pygame.time.get_ticks() - time_start) / 1000

    # Exibir tempo e pontuação
    time_text = font.render(f"Tempo: {int(elapsed_time)}s", True, (255, 255, 255))
    score_text = font.render(f"Pontuação: {score}", True, (255, 255, 255))
    phase_text = font.render(f"Fase: {current_phase}", True, (255, 255, 255))
    screen.blit(time_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(phase_text, (10, 90))

    # Desenhar o jogador e objetivo
    screen.blit(player_img, (player_x, player_y))
    screen.blit(goal_img, (goal.x, goal.y))

    # Eventos de saída
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimentação do jogador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > movement_area.left:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < movement_area.right - player_width:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y > movement_area.top:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < movement_area.bottom - player_height:
        player_y += player_speed

    # Verificação de colisão com obstáculos fixos
    for obstacle in obstacles:
        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(obstacle):
            score -= 10
            player_x, player_y = phases[current_phase - 1]["player_start"]
        screen.blit(obstacle_img, (obstacle.x, obstacle.y))

    # Verificação de colisão com o obstáculo aleatório
    if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(random_obstacle):
        print("Você colidiu com o obstáculo aleatório! Jogo reiniciado.")
        score = 0
        current_phase = 1
        load_phase(current_phase)

    # Desenhar obstáculo aleatório
    screen.blit(random_obstacle_img, (random_obstacle.x, random_obstacle.y))

    # Verificação de colisão com pontos bônus
    for bonus in bonus_points:
        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(bonus):
            score += 20
            bonus_points.remove(bonus)

    # Verifica se o jogador chegou ao objetivo
    if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(goal):
        score += 100
        print(f"Parabéns! Fase {current_phase} concluída.")

        if current_phase < len(phases):
            current_phase += 1
            load_phase(current_phase)
        else:
            print("Parabéns! Você completou o jogo!")
            running = False

    # Atualização da tela
    pygame.display.flip()
    clock.tick(30)

pygame.quit()

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
player_width, player_height = 40,75  # Tamanho fixo do jogador
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock() 

# Carrega os assets para cada fase
assets = {
    1: {
        "background": pygame.image.load('frontend/assets/images/Background-Floresta.png'),
        "obstacle": pygame.image.load('frontend/assets/images/Urso.png'),
        "random_obstacle": pygame.image.load('frontend/assets/images/Urso-Mal.png'),
        "goal": pygame.image.load('frontend/assets/images/Burrito.png'),
        "bonus_point": pygame.image.load('frontend/assets/images/bonus_point.png'),
    },
    2: {
        "background": pygame.image.load('frontend/assets/images/Background-Praia.png'),
        "obstacle": pygame.image.load('frontend/assets/images/Carangueijo.png'),
        "random_obstacle": pygame.image.load('frontend/assets/images/Carangueijo-Mal.png'),
        "goal": pygame.image.load('frontend/assets/images/Burrito.png'),
        "bonus_point": pygame.image.load('frontend/assets/images/bonus_point.png'),
    },
    3: {
        "background": pygame.image.load('frontend/assets/images/Background-Rodovia.png'),
        "obstacle": pygame.image.load('frontend/assets/images/Carro.png'),
        "random_obstacle": pygame.image.load('frontend/assets/images/Carro-Mal.png'),
        "goal": pygame.image.load('frontend/assets/images/Burrito.png'),
        "bonus_point": pygame.image.load('frontend/assets/images/bonus_point.png'),
    }
}

# Configurações das fases
phases = [
    {  # Fase 1
        "player_start": (50, 260),
        "goal": (1050, 280),
        "obstacles": [
            pygame.Rect(200, 200, 85, 100), 
            pygame.Rect(350, 400, 85, 100), 
            pygame.Rect(500, 150, 85, 100), 
            pygame.Rect(650, 300, 85, 100), 
            pygame.Rect(900, 220, 85, 100)
            ],
        "bonus_points": [
            pygame.Rect(150, 150, 20, 20), 
            pygame.Rect(670, 200, 20, 20)
            ],
    },
    {  # Fase 2
        "player_start": (50, 260),
        "goal": (1050, 280),
        "obstacles": [
            pygame.Rect(100, 100, 85, 100),
            pygame.Rect(230, 250, 85, 100),
            pygame.Rect(380, 310, 85, 100),
            pygame.Rect(555, 360, 85, 100),
            pygame.Rect(670, 150, 85, 100),
            pygame.Rect(850, 240, 85, 100),
            pygame.Rect(950, 340, 85, 100),
        ],
        "bonus_points": [
            pygame.Rect(150, 300, 20, 20),
            pygame.Rect(450, 350, 20, 20),
            pygame.Rect(750, 250, 20, 20),
        ],
    },
    {  # Fase 3
        "player_start": (50, 260),
        "goal": (1050, 280),
        "obstacles": [
            pygame.Rect(380, 130, 85, 100),
            pygame.Rect(170, 220, 85, 100),
            pygame.Rect(300, 380, 85, 100),
            pygame.Rect(450, 290, 85, 100),
            pygame.Rect(600, 180, 85, 100),
            pygame.Rect(750, 320, 85, 100),
            pygame.Rect(850, 240, 85, 100),
            pygame.Rect(950, 100, 85, 100),
            pygame.Rect(990, 340, 85, 100),
        ],
        "bonus_points": [
            pygame.Rect(200, 200, 20, 20),
            pygame.Rect(500, 150, 20, 20),
            pygame.Rect(800, 250, 20, 20),
        ],
    }
]

# Variáveis de jogo
current_phase = 1
player_x, player_y = 0, 0
score = 0
time_start = pygame.time.get_ticks()
random_obstacle = None
random_obstacle_hidden_until = 0

# Função para carregar a fase atual
def load_phase(phase):
    global player_x, player_y, goal, obstacles, bonus_points, random_obstacle, background_img, obstacle_img, random_obstacle_img, goal_img, bonus_point_img

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
    bonus_point_img = pygame.transform.scale(assets[phase]["bonus_point"], (40, 40))

    # Posicionar o obstáculo aleatório
    random_obstacle = pygame.Rect(
        random.randint(SCREEN_WIDTH - 1100, SCREEN_WIDTH - 200),
        random.randint(SCREEN_HEIGHT - 400, SCREEN_HEIGHT - 200),
        70,
        70
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
    current_time = pygame.time.get_ticks() / 1000  # Tempo atual em segundos

    # Exibir tempo e pontuação
    time_text = font.render(f"Tempo: {int(elapsed_time)}s", True, (255, 255, 255))
    score_text = font.render(f"Pontuação: {score}", True, (255, 255, 255))
    phase_text = font.render(f"Fase: {current_phase}", True, (255, 255, 255))
    screen.blit(time_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(phase_text, (10, 90))
    
    # Desenha os bonus points
    for bonus in bonus_points:
        screen.blit(bonus_point_img, (bonus.x, bonus.y))  # Desenha cada bonus_point na posição especificada

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
    # Dicionário para ajustes de hitbox por fase
    hitbox_adjustments = {
        1: (10, 10, 19, 20),  # Ajustes para fase 1 (x_offset, y_offset, width_reduction, height_reduction)
        2: (0, 10, 0, 33),  # Ajustes para fase 2
        3: (3, 35, 0, 73),   # Ajustes para fase 3
    }

    # Ajuste da hitbox do jogador (deslocamentos para centralizar na imagem)
    player_hitbox_x_offset = 17  # Ajuste horizontal (depende do design da imagem)
    player_hitbox_y_offset = 0   # Ajuste vertical (depende do design da imagem)
    player_hitbox_width = 40     # Largura da hitbox
    player_hitbox_height = 75    # Altura da hitbox

    player_hitbox = pygame.Rect(
        player_x + player_hitbox_x_offset,
        player_y + player_hitbox_y_offset,
        player_hitbox_width,
        player_hitbox_height
    )

    for obstacle in obstacles:
        # Obter ajustes específicos para a fase atual
        x_offset, y_offset, width_reduction, height_reduction = hitbox_adjustments[current_phase]

        # Aplicar ajustes de hitbox
        reduced_hitbox = pygame.Rect(
            obstacle.x + x_offset,
            obstacle.y + y_offset,
            obstacle.width - width_reduction,
            obstacle.height - height_reduction
        )

        # Verificar colisão com a hitbox reduzida
        if player_hitbox.colliderect(reduced_hitbox):
            score -= 10
            player_x, player_y = phases[current_phase - 1]["player_start"]

        # Desenhar o obstáculo
        screen.blit(obstacle_img, (obstacle.x, obstacle.y))

    # Verificação de colisão com o obstáculo aleatório
    reduced_random_hitbox = pygame.Rect(
        random_obstacle.x + 5, 
        random_obstacle.y + 5,  
        random_obstacle.width - 10,  
        random_obstacle.height - 10  
    )

    if current_time > random_obstacle_hidden_until:
        if player_hitbox.colliderect(reduced_random_hitbox):
            print("Você colidiu com o obstáculo aleatório! Jogo reiniciado.")
            score = 0
            current_phase = 1
            load_phase(current_phase)

        # Desenhar obstáculo aleatório
        screen.blit(random_obstacle_img, (random_obstacle.x, random_obstacle.y))

    # Verificação de colisão com pontos bônus
    for bonus in bonus_points[:]:  # Usar uma cópia da lista para evitar problemas ao remover elementos
        if player_hitbox.colliderect(bonus):
            score += 20
            bonus_points.remove(bonus)
            random_obstacle_hidden_until = current_time + 5

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

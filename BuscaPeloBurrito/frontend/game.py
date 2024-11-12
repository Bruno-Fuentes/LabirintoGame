import pygame
import random
import requests

# Inicializa o Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Labirinto Florestal")

# Carrega e redimensiona as imagens
background_img = pygame.image.load('frontend/assets/images/forest_background.png')
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Ajusta para o tamanho da tela

player_img = pygame.image.load('frontend/assets/images/player.png')
player_img = pygame.transform.scale(player_img, (50, 50))  # Tamanho ajustado para o jogador

goal_img = pygame.image.load('frontend/assets/images/goal.png')
goal_img = pygame.transform.scale(goal_img, (50, 50))  # Tamanho ajustado para o objetivo

obstacle_img = pygame.image.load('frontend/assets/images/obstaculo.png')
obstacle_img = pygame.transform.scale(obstacle_img, (40, 40))  # Tamanho ajustado para os obstáculos

# Definindo propriedades do jogador
player_speed = 5
player_width, player_height = player_img.get_width(), player_img.get_height()

# Variáveis de jogo
score = 0
time_start = pygame.time.get_ticks()
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
current_phase = 1

# Configurações das fases
phases = [
    {  # Fase 1
        "player_start": (50, 50),
        "goal": (700, 500),
        "obstacles": [pygame.Rect(200, 200, 40, 40), pygame.Rect(300, 300, 40, 40)],
        "bonus_points": [pygame.Rect(150, 150, 20, 20), pygame.Rect(400, 400, 20, 20)]
    },
    {  # Fase 2
        "player_start": (50, 550),
        "goal": (750, 50),
        "obstacles": [pygame.Rect(100, 100, 40, 40), pygame.Rect(500, 100, 40, 40), pygame.Rect(600, 400, 40, 40)],
        "bonus_points": [pygame.Rect(200, 200, 20, 20), pygame.Rect(350, 450, 20, 20), pygame.Rect(650, 300, 20, 20)]
    },
    {  # Fase 3
        "player_start": (750, 50),
        "goal": (50, 550),
        "obstacles": [pygame.Rect(300, 200, 40, 40), pygame.Rect(400, 300, 40, 40), pygame.Rect(600, 150, 40, 40), pygame.Rect(200, 500, 40, 40)],
        "bonus_points": [pygame.Rect(150, 350, 20, 20), pygame.Rect(450, 250, 20, 20), pygame.Rect(500, 500, 20, 20)]
    }
]

# Função para enviar pontuação ao servidor Django
def send_score(name, score, time_spent):
    url = 'http://localhost:8000/scores/'
    data = {'player_name': name, 'points': score, 'time_spent': time_spent}
    response = requests.post(url, json=data)
    return response.json()

# Função para carregar a fase atual
def load_phase(phase):
    global player_x, player_y, goal, obstacles, bonus_points
    player_x, player_y = phases[phase - 1]["player_start"]
    goal = pygame.Rect(*phases[phase - 1]["goal"], 50, 50)
    obstacles = phases[phase - 1]["obstacles"]
    bonus_points = phases[phase - 1]["bonus_points"]

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
    if keys[pygame.K_LEFT] and player_x > 0: player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width: player_x += player_speed
    if keys[pygame.K_UP] and player_y > 0: player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < SCREEN_HEIGHT - player_height: player_y += player_speed

    # Verificação de colisão com obstáculos
    for obstacle in obstacles:
        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(obstacle):
            score -= 10  # Perde pontos ao colidir
            player_x, player_y = phases[current_phase - 1]["player_start"]  # Reinicia a posição
        screen.blit(obstacle_img, (obstacle.x, obstacle.y))

    # Verificação de colisão com pontos bônus
    for bonus in bonus_points:
        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(bonus):
            score += 20  # Ganha pontos ao pegar o bônus
            bonus_points.remove(bonus)  # Remove o ponto de bônus coletado

    # Verifica se o jogador chegou ao objetivo
    if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(goal):
        score += 100  # Ganha pontos ao completar a fase
        print(f"Parabéns! Fase {current_phase} concluída.")
        
        # Avança para a próxima fase, ou termina o jogo se for a última fase
        if current_phase < len(phases):
            current_phase += 1
            load_phase(current_phase)  # Carrega a nova fase
        else:
            print("Parabéns! Você completou o jogo!")
            running = False  # Termina o jogo após a última fase

    # Atualização da tela
    pygame.display.flip()
    clock.tick(30)

pygame.quit()

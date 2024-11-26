import pygame
import random
import sqlite3

# Inicializa o Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Em Busca do Burrito")

movement_area = pygame.Rect(100, 100, 1100, 400)

# Carregar  imagem do Player
player_img = pygame.image.load('frontend/assets/images/player.png').convert_alpha()
player_img = pygame.transform.scale(player_img, (75,75))

# Configurações gerais
player_speed = 5
player_width, player_height = 40,75  # Tamanho fixo do jogador
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock() 

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

db = sqlite3.connect("ranking.db")
cursor = db.cursor()

# Cria a tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS ranking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT,
    time INTEGER
)
""")
db.commit()

#cursor.execute("DELETE FROM ranking")
#db.commit()

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
            pygame.Rect(630, 150, 85, 100),
            pygame.Rect(850, 240, 85, 100),
            pygame.Rect(950, 340, 85, 100),
        ],
        "bonus_points": [
            pygame.Rect(150, 300, 20, 20),
            pygame.Rect(450, 150, 20, 20),
            pygame.Rect(750, 290, 20, 20),
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
show_hitboxes = False
game_over = False
player_name = None

# Funções auxiliares
def get_player_name():
    """Exibe uma tela para o jogador inserir seu nome."""
    global player_name
    if player_name:  # Se o nome já estiver definido, retorne-o diretamente
        return player_name

    input_active = True
    player_name = ""
    while input_active:
        screen.fill(BLACK)
        draw_text("Digite seu nome:", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, WHITE, 36)
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50), 2)
        draw_text(player_name, SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 10, WHITE, 36)
        draw_text("Pressione ENTER para confirmar", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 100, GRAY, 24)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 20:  # Limitar o nome a 20 caracteres
                    player_name += event.unicode

    player_name = player_name.strip()
    return player_name  # Retornar o nome sem espaços adicionais

def save_score(player_name, time):
    """Salva a pontuação no banco de dados."""
    cursor.execute("INSERT INTO ranking (player_name, time) VALUES (?, ?)", (player_name, time))
    db.commit()

def get_ranking():
    """Busca o ranking do banco de dados, ordenado por tempo."""
    cursor.execute("SELECT player_name, time FROM ranking ORDER BY time ASC LIMIT 10")
    return cursor.fetchall()

def draw_text(text, x, y, color=WHITE, font_size=36):
    font = pygame.font.Font(None, font_size)
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(midtop=(x + rendered_text.get_width() // 2, y))
    screen.blit(rendered_text, (x, y))

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

def reset_game():
    """Reinicia as variáveis do jogo para começar do zero."""
    global current_phase, score, time_start, game_over, player_x, player_y, bonus_points, player_name, game_data, copia_bonus_points
    
    # Redefinir dados do jogador
    player_name = None  # Redefine o nome do jogador para None ou estado inicial
    
    # Reiniciar progresso do jogo
    current_phase = 1  # Reinicia na primeira fase
    score = 0  # Zera a pontuação
    bonus_points = 0  # Remove todos os pontos de bônus
    
    # Redefinir estado do jogo
    game_over = False  # Define o jogo como ativo
    time_start = pygame.time.get_ticks()  # Reinicia o contador de tempo

    # Reiniciar pontos bônus
    resetar_bonus()
    
    # Reposicionar o jogador (ajustar para posição inicial do jogo)
    player_x = 0  # Posição inicial X do jogador
    player_y = 0  # Posição inicial Y do jogador
    
    # Limpar dados temporários ou globais adicionais se necessário
    game_data = {}  # Se houver dados armazenados temporariamente, redefina
    
    # Recarregar a fase inicial
    load_phase(current_phase)  # Função para carregar a fase 1

# Função para exibir a tela inicial
def show_start_screen():
    start_running = True
    global player_name
    while start_running:
        screen.fill(BLACK)
        draw_text("Em Busca do Burrito", SCREEN_WIDTH // 2 - 200, 100, WHITE, 50)
        draw_text("1 - Jogar", SCREEN_WIDTH // 2 - 100, 200, WHITE)
        draw_text("2 - Ranking", SCREEN_WIDTH // 2 - 100, 300, WHITE)
        draw_text("3 - Sair", SCREEN_WIDTH // 2 - 100, 400, WHITE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    reset_game()
                    start_running = False
                elif event.key == pygame.K_2:
                    show_ranking_screen()
                elif event.key == pygame.K_3:
                    pygame.quit()
                    quit()

def show_ranking_screen():
    screen.fill(BLACK)
    draw_text("Ranking", SCREEN_WIDTH // 2 - 100, 100, WHITE, 50)
    rankings = get_ranking()

    y_offset = 200
    for idx, (name, time) in enumerate(rankings):
        draw_text(f"{idx + 1}. {name} - {time}s", SCREEN_WIDTH // 2 - 100, y_offset, WHITE, 36)
        y_offset += 40

    pygame.display.flip()

    # Espera até que o jogador pressione ESC ou veja o ranking por 5 segundos
    ranking_screen_running = True
    while ranking_screen_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Se pressionar ESC, retorna para a tela inicial
                    ranking_screen_running = False
                    show_start_screen()  # Exibe a tela inicial novamente

def show_game_over_screen():
    global game_over, running, score, current_phase
    while game_over:
        screen.fill(RED)
        draw_text("GAME OVER", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, BLACK, 80)
        draw_text("Pressione ESC para sair ou R para reiniciar", SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 + 50, BLACK, 30)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_r:
                    reset_game()
                    game_over = False

def Mostrarbonus():
    global random_obstacle_hidden_until, score
    # Verificação de colisão com pontos bônus
    for bonus in bonus_points[:]:  # Usar uma cópia da lista para evitar problemas ao remover elementos
        if player_hitbox.colliderect(bonus):
            score += 20
            bonus_points.remove(bonus)
            random_obstacle_hidden_until = current_time + 3

def resetar_bonus():
    for i, fase in enumerate(phases):
        if i == 0:
            fase["bonus_points"] = [
                pygame.Rect(150, 150, 20, 20), 
                pygame.Rect(670, 200, 20, 20)
            ]
        elif i == 1:
            fase["bonus_points"] = [
                pygame.Rect(150, 300, 20, 20),
                pygame.Rect(450, 150, 20, 20),
                pygame.Rect(750, 290, 20, 20),
            ]
        elif i == 2:
            fase["bonus_points"] = [
                pygame.Rect(200, 200, 20, 20),
                pygame.Rect(500, 150, 20, 20),
                pygame.Rect(800, 250, 20, 20),
            ]

# Inicializa a tela inicial
show_start_screen()
reset_game()
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
        1: (15, 15, 30, 30),  # Ajustes para fase 1 (x_offset, y_offset, width_reduction, height_reduction)
        2: (5, 15, 10, 40),  # Ajustes para fase 2
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
            score -= 50
            current_phase = 1
            load_phase(current_phase)

        # Desenhar obstáculo aleatório
        screen.blit(random_obstacle_img, (random_obstacle.x, random_obstacle.y))

    Mostrarbonus()

    # Verifica se o jogador chegou ao objetivo
    if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(goal):
        score += 100

        if current_phase < len(phases):
            current_phase += 1
            load_phase(current_phase)
        else:
            elapsed_time = (pygame.time.get_ticks() - time_start) // 1000
    
            # Exibir tela para inserir o nome do jogador
            player_name = get_player_name()
            
            # Salvar o nome e tempo no banco de dados
            save_score(player_name, elapsed_time)
            
            # Exibir mensagem de conclusão e redirecionar para o ranking
            ranking_screen_active = True
            while ranking_screen_active:
                screen.fill(BLACK)
                draw_text("Parabéns, você completou o jogo!", SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 100, WHITE, 40)
                draw_text(f"Tempo final: {elapsed_time}s", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2, WHITE, 36)
                draw_text("Pressione Enter para ver o ranking", SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 100, GRAY, 24)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        ranking_screen_active = False
                        show_ranking_screen()  # Exibe a tela de ranking

    if show_hitboxes:
        # Desenhar hitbox do jogador
        player_hitbox = pygame.Rect(player_x + player_hitbox_x_offset, player_y + player_hitbox_y_offset, player_hitbox_width, player_hitbox_height)
        pygame.draw.rect(screen, (0, 0, 255), player_hitbox, 2)

        # Desenhar hitboxes dos obstáculos fixos
        for obstacle in obstacles:
            # Reaplicar os ajustes usados para colisão
            x_offset, y_offset, width_reduction, height_reduction = hitbox_adjustments[current_phase]
            adjusted_hitbox = pygame.Rect(
                obstacle.x + x_offset,
                obstacle.y + y_offset,
                obstacle.width - width_reduction,
                obstacle.height - height_reduction
            )
            pygame.draw.rect(screen, (255, 0, 0), adjusted_hitbox, 2)  # Vermelho para hitboxes ajustadas

        # Desenhar hitbox do obstáculo aleatório
        reduced_random_hitbox = pygame.Rect(
            random_obstacle.x + 5,
            random_obstacle.y + 5,
            random_obstacle.width - 10,
            random_obstacle.height - 10
        )
        pygame.draw.rect(screen, (0, 255, 0), reduced_random_hitbox, 2)

    if score <= -100:
        game_over = True
        show_game_over_screen()

    # Atualização da tela
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
import pygame
import os
import sys
import json
from game_state import GameState

pygame.init()
screen = pygame.display.set_mode((GameState.SCREEN_WIDTH, GameState.SCREEN_HEIGHT))
screen_rect=screen.get_rect()
tile_size = 38  # Tamanho de cada bloco no mapa
#compare https://www.atari2600.com.br/Sites/Atari/AtariFull.aspx
speed_default = 1.3
scroll_offset = -160
GAME_HEIGHT = GameState.game_height()
game_over_ticks_max = 20
game_over_ticks = 0
scale=2
from game_objects import *

def check_collisions(current_object, game_objects):
    for game_object in game_objects:
        if current_object.rect.colliderect(game_object.rect) and current_object != game_object and not isinstance(game_object, Bullet):
            #print(f"Collision detected between {type(current_object).__name__} and {type(game_object).__name__}.")
            #print(type(game_object))  
            return current_object,game_object
    return None,None

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def reset_game():
    global player, game_objects, game_over, game_over_ticks
    
    pygame.time.delay(2000)  # Aguarda 2 segundos (2000 milissegundos)
    player = Player(initial_player_x, initial_player_y, sheet_image)
    
    game_objects.clear()  # Adicione esta linha para remover todos os objetos antigos
    game_objects = load_game_state()  # Atualize a lista de objetos de jogo com a lista retornada por load_game_state()
    game_objects.append(player)  # Adicione o player à lista
    GameState.reset()
    gauge_meter.update(player.gasolina)     
    game_over = False
    game_over_ticks = 0
    player.is_dead = False
    

def check_collision_with_color(player, color):
    player_mask = pygame.mask.from_surface(player.player_image)  # Cria uma mask do jogador

    x, y = player.rect.x, player.rect.y  # A posição do jogador

    # Verifica cada ponto no retângulo do jogador
    for point in player_mask.outline():
        x_offset, y_offset = point  # A offset da mask em relação ao jogador
        x_pixel, y_pixel = x + x_offset, y + y_offset  # A posição do pixel na tela

        # Verifica se a posição do pixel é dentro da tela
        if 0 <= x_pixel < screen.get_width() and 0 <= y_pixel < GAME_HEIGHT:
            # Pega a cor do pixel na posição (x_pixel, y_pixel)
            pixel_color = screen.get_at((x_pixel, y_pixel))

            # Verifica se o pixel não é transparente e não é a cor da água
            if pixel_color != GameState.WATER_COLOR and pixel_color[3] != 0:  # O componente alfa é o quarto componente da cor
                return True  # Há uma colisão com um objeto não transparente

    # Se nenhum dos pixels do jogador está sobre um objeto não transparente e não é a cor da água, não há colisão
    return False





def load_game_state():
    object_dict = {
        "g": Grama,
        "a": Asfalto,
        "H": Helicopter,
        "N": Boat,
        "f": Fuel,
        "p": Ponte,
        "\\": Gramaupright,
        "/": Gramaupleft,
        "]": Gramadownleft,
        "[": Gramadownright,
        "^": Casa
    }
    try:
        with open('game_state.json', 'r') as f:
            game_objects_dicts = json.load(f)
    except FileNotFoundError:
        return []  # Retorna uma lista vazia se o arquivo não existir

    game_objects = []
    for obj_dict in game_objects_dicts:
        cls = char_to_class[obj_dict['type']]
        x = obj_dict['x']
        y = obj_dict['y'] - scroll_offset if obj_dict['y'] - scroll_offset < GAME_HEIGHT else GAME_HEIGHT  # Use scroll_offset em vez de um valor fixo
        z = obj_dict['z']  # Get the z value from the dictionary
        game_object = cls(x, y, sheet_image, z)  # Pass the z value to the constructor
        game_objects.append(game_object)

    return game_objects


sheet_image = pygame.image.load('Atari - River Raid Atari 2600 - River Raid.png') .convert_alpha()
initial_player_x = 400  # posição inicial X
initial_player_y = GAME_HEIGHT - 100
player = Player(initial_player_x, initial_player_y,sheet_image)
#enemies = [Airplane(200, 100,sheet_image), Airplane(400, 100,sheet_image), Airplane(600, 100,sheet_image)]



clock = pygame.time.Clock()
# Inicializa um contador de tempo
time_counter = 0
# Define um intervalo de tempo para diminuir o combustível (em milissegundos)
gas_decrement_interval = 1000  # Diminui o combustível a cada segundo

game_over = False
game_objects = load_game_state()
game_objects.append(player)  # Adiciona o player de volta à lista
GameState.reset()
# Cria o objeto Gauge primeiro na posição x=0
gauge = Gauge(0, GAME_HEIGHT + 45, sheet_image)

# Agora podemos calcular a posição x corretamente
gauge_x = (GameState.SCREEN_WIDTH - gauge.image.get_width()) // 2

# Ajusta a posição x do objeto Gauge
gauge.x = gauge_x
gauge.rect.x = gauge_x

# E também o GaugeMeter
gauge_meter_x = gauge_x  # supondo que o GaugeMeter comece na mesma posição x que o Gauge
gauge_meter = GaugeMeter(gauge_meter_x, GAME_HEIGHT + 45, gauge, sheet_image)

# Cria o objeto Score temporário
temp_score = Score(0, GAME_HEIGHT + 10, GameState.player_score, sheet_image, gauge_x+gauge.image.get_width(), scale)

# Define a posição x do Score de forma que esteja alinhado à direita do Gauge
score_x = gauge_x + gauge.image.get_width()

# Cria o objeto Score
score = Score(score_x, GAME_HEIGHT + 10, GameState.player_score, sheet_image, gauge_x+gauge.image.get_width(), scale)

# Atualiza o GaugeMeter
gauge_meter.update(player.gasolina) 


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.move_left()
    elif keys[pygame.K_RIGHT]:
        player.move_right()
    if keys[pygame.K_UP]:
        player.move_up()
    elif keys[pygame.K_DOWN]:
        player.move_down()
    elif not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:

        GameState.speed = speed_default  # Aqui, assumimos que speed_default é a velocidade padrão.
         
    if keys[pygame.K_r]:
        restart_program()
    elif keys[pygame.K_SPACE]:
        # Conta a quantidade de objetos Bullet em game_objects
        bullet_count = sum(isinstance(obj, Bullet) for obj in game_objects)

        # Se há menos de três Bullets, dispara um novo tiro
        if bullet_count < 2:

            bullet = Bullet(player.x + (player.rect.width / 2), player.y - player.rect.height, sheet_image)
            game_objects.append(bullet)
            
    # Limpa a tela antes de desenhar
    screen.fill(GameState.WATER_COLOR)
    for game_object in game_objects:

        if isinstance(game_object, Bullet):
            if game_object.y < 0:  # Se a bala saiu da tela
                game_objects.remove(game_object)  # Remova a bala da lista de objetos do jogo
            else:  # Se a bala ainda está na tela                

                current_object,collided_object  = check_collisions(game_object, game_objects)
                if collided_object is not None:   # Se a bala colidir com um objeto
                    if isinstance(collided_object, MovingObject) or isinstance(collided_object, Ponte) or isinstance(collided_object, Fuel):  # Se esse objeto for um inimigo ou uma ponte
                        collided_object.explode()  # Exploda o objeto
                        GameState.add_score(100)
                    
                        game_objects.remove(game_object)  # Remova a bala da lista de objetos do jogo
                    else:  # Se a bala atingir um objeto que não seja um inimigo ou uma ponte
                        game_objects.remove(game_object)  # Remova a bala da lista de objetos do jogo   

        if isinstance(game_object, StaticObject):       
            game_object.scroll()
            game_object.update(dt)
            if game_object.is_dead:
                game_objects.remove(game_object)
      
  
        elif isinstance(game_object, MovingObject):
            game_object.scroll()
            game_object.update(dt)

            current_object,collided_object = check_collisions(game_object, game_objects)
            if collided_object is not None: 
                game_object.trata_colisao(collided_object.rect)    


            game_object.move()    
            if game_object.is_dead:
                GameState.add_score(100)
                game_objects.remove(game_object)


        elif isinstance(game_object, Player):
            current_object,collided_object = check_collisions(game_object, game_objects)
            if collided_object is not None:
                if isinstance(collided_object, Fuel):
                    game_object.refuel()  # Refuel the player
                 
                    gauge_meter.update(player.gasolina)
                    #game_objects.remove(collided_object)  # Remove the Fuel from the game objects
                else:  # If the collision is not with Fuel, then proceed with the normal collision handling
                    game_object.blinking = True
                    if isinstance(collided_object, MovingObject) or \
                    (isinstance(collided_object, StaticObject) and \
                        check_collision_with_color(game_object, GameState.WATER_COLOR)):  # Checa colisão com a cor da água
                        game_object.explode()
                        player.draw(screen) 
                        if isinstance(collided_object, MovingObject):
                            collided_object.explode()
                            collided_object.draw(screen)
                        pygame.display.flip()  # Atualiza a tela para mostrar a explosão
                        game_over = True 
                game_object.blinking = False
                   
            game_object.update(dt)

        game_object.draw(screen)
    # Desenha o objeto Player por último para que ele fique na frente dos outros objetos
    #player.draw(screen)
    # Atualize e desenhe o placar
    pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(0, GAME_HEIGHT, GameState.SCREEN_WIDTH, GameState.PANEL_HEIGHT))

    score.update(GameState.player_score)
    score.draw(screen)
    gauge.draw(screen)
     # Atualiza o contador de tempo
    time_counter += clock.get_time()
    # Diminui o combustível em intervalos regulares
    if time_counter >= gas_decrement_interval:
        out_of_gas = player.decrease_gasolina(5, GameState.speed)
        if out_of_gas:
            player.explode();
            game_over = True
            player.draw(screen) 

        time_counter = 0  # Reseta o contador de tempo

    if game_over:
        game_over_ticks += 1
        if game_over_ticks >= game_over_ticks_max:
            game_objects.remove(player)
            reset_game()
    else:
        game_over_ticks = 0 

    gauge_meter.update(player.gasolina)  # Atualiza o medidor de combustível

    gauge_meter.draw(screen)
    pygame.display.update()    
    pygame.display.flip()
 
    # Limita a taxa de quadros
    clock.tick(60)
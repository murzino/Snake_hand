from random import randint
import cv2
import mediapipe as mp
import time
import math
import pygame
import sys
import random
import threading

pygame.init()

###Вводные игры

#Задаем параметры окна игры
width, height = 1400, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Змеюка-Гадюка")

# Определение цветов и шрифтов
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
font = pygame.font.Font(None, 36)
color = {}

# Начальные координаты Змеи
x, y = width // 2, height // 2
snake_positions = [(x, y)]

# Размер Змеи
snake_size = 25
snake_length = 1
shift_x = 0
shift_y = 0

# Начальные координаты еды
food_position = width // 3, height // 3

###Трекинг рук

#Работа с пальцами
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
flag = True

# Переменные для расчета FPS
previous_time = time.time()
frame_count = 0
fps = 0

#Функция возвращающая кол-во поднятых пальцев
def count_fingers(landmarks):
    
    #Именуем основные точки ладони
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = landmarks[mp_hands.HandLandmark.THUMB_MCP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = landmarks[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = landmarks[mp_hands.HandLandmark.PINKY_MCP]
    wrist = landmarks[mp_hands.HandLandmark.WRIST]
    
    # #Записывает в переменную расстояние между кончиками указательного и большого пальца (Можно установить на него действие)
    # rasstoianie = abs(index_tip.x - thumb_tip.x) + abs(index_tip.y - thumb_tip.y)
    # #Выводит переменную rasstoianie
    # cv2.putText(frame, f'Raznica bol, ykas:{rasstoianie}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # #Условие на переменной rasstoianie
    # if rasstoianie < 0.04 and fingers_count == 1:
    #     pass

    #Основная функция определения поднят ли палец
    def True_or_False(palec):
        if abs(wrist.x - palec.x)+abs(wrist.y - palec.y)  > 0.2 :
            return True

    #Каждый кадр определяет сколько пальцев поднято
    count = 0
    if True_or_False(index_tip):  # Указательный палец
        count += 1
    if True_or_False(middle_tip):  # Средний палец
        count += 1
    if True_or_False(ring_tip):  # Безымянный палец
        count += 1
    if True_or_False(pinky_tip):  # Малый палец
        count += 1
    return count



# Захват видео
cap = cv2.VideoCapture(0)


if not cap.isOpened():
    print("Ошибка: Не удалось открыть камеру.")
    exit()
    
# Запуск основного цикла
clock = pygame.time.Clock()
running = True
# asfd
def camera_thread():
    global running
    while running:
        global frame_count, previous_time, x, y, food_position, snake_length, snake_positions, snake_size, fps, shift_x, shift_y

        ret, frame = cap.read()

        # Обновляем FPS раз в секунду
        current_time = time.time()
        frame_count += 1

        if current_time - previous_time >= 1.0:
            fps = frame_count  # Обновляем значение FPS
            frame_count = 0  # Сбрасываем счетчик кадров
            previous_time = current_time  # Обновляем время
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

        # Преобразование цветового пространства
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Рисуем ключевые точки и соединяем их
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                INDEX_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                INDEX_finger_cmc = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Вычисление вектора
                dx = INDEX_finger_cmc.x - INDEX_finger_mcp.x
                dy = INDEX_finger_cmc.y - INDEX_finger_mcp.y  

                # Вычисление растояния между началом указ.п и кончика указ.п
                cm = (abs(dx) + abs(dy)) * 40


                # Вычисление угла в радианах
                angle_rad = math.atan2(dy, dx)
        
                # Преобразование радианов в градусы
                angle_deg = math.degrees(angle_rad)


                # Убедитесь, что угол находится в диапазоне от 0 до 360
                if angle_deg < 0:
                    angle_deg += 360


                rad_angle = math.radians(angle_deg)  # Преобразовываем угол в радианы
                shift_x = cm * math.cos(rad_angle)  # Изменяем координату x
                shift_y = cm * math.sin(rad_angle)  # Изменяем координату y


            
                # Вывод инфы на экран
                cv2.putText(frame, f'Angle: {angle_deg:.2f}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                cv2.putText(frame, f'Speed: {cm:.2f}', (10, 260), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                

                # Считаем количество поднятых пальцев   
                fingers_count = count_fingers(hand_landmarks.landmark)

                # Отображаем количество пальцев на экране
                cv2.putText(frame, f'Count: {fingers_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Показываем изображение
        cv2.imshow('Finger Count', frame)

        # Выход из программы при нажатии на клавишу 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

thread = threading.Thread(target=camera_thread, daemon=True)
thread.start()

def game_loop():
    global running
    while running:
        global x, y, food_position, snake_length, snake_positions, snake_size

        #Берет все события из активной сессии игры каждую итерацию
        for event in pygame.event.get():
            #Проверяет событие на значение QUIT
            if event.type == pygame.QUIT:
                #Если пользователь попытался закрыть окно, тогда останавливаем игру
                running = False

 
        
        # Ограничение движения квадратика в пределах окна (Если у змени нет смерти от стены)
        x = max(0, min(width - snake_size, x))
        y = max(0, min(height - snake_size, y))

        # Динамические координаты головы змени
        Head = (round(x), round(y))

        #Если еда оказалась в пределах координат головы
        if Head[0] -50 < food_position[0] < Head[0] + 50 and Head[1] -50 < food_position[1] < Head[1] + 50:
            #Назначаем еде новое рандомное положение
            food_position = random.randint(0, (width)), random.randint(0,(height))
            #Добавляем змее длинну
            snake_length += 1

        # Каждую итерацию в список в 0 индекс добавляем координаты головы
        snake_positions.insert(0, Head)
        # Обрезаем этот список до длинны змеи (На этом этапе и происходит логика по будущей отрисовке змеи)
        snake_positions = snake_positions[:snake_length]


        # # Проверка на столкновение с границами
        # if (Head[0] <= 0 or Head[0] >= width - snake_size or Head[1] <= 0 or Head[1] >= height - snake_size):
        #     running = False  # Конец игры
        
        # Заполнение фона черным цветом
        screen.fill(black)

        # Координаты
        text_surface = font.render(f"Координаты головы: {Head[0]}, {Head[1]}", True, white)
        screen.blit(text_surface, (10, 10))  # Отрисовываем текст в верхнем левом углу    

        text_surface = font.render(f"Координаты ЕДЫ: {food_position[0]}, {food_position[1]}", True, white)
        screen.blit(text_surface, (10, 30))  # Отрисовываем текст в верхнем левом углу

        text_surface = font.render(f"Змеинных КГ: {snake_length}", True, white)
        screen.blit(text_surface, (10, 70))  # Отрисовываем текст в верхнем левом углу

        # Получаем FPS и рендерим текст
        clock.tick(144)
        fps_in_game = clock.get_fps()
        fps_text = font.render(f"FPS: {fps_in_game:.2f}", True, white)
        screen.blit(fps_text, (10, 100))  # Отображаем текст в верхнем левом углу


        # Рисуем змею
        # for pos in enumerate(snake_positions):
        #     pygame.draw.circle(screen, (255 - pos[0] * 2, 255 -  pos[0] * 3, 255 - pos[0] * 4), (pos[1][0], pos[1][1]), snake_size )

        for pos in enumerate(snake_positions):
            if pos[0] not in color:
                color[pos[0]] = (randint(0,255), randint(0,255), randint(0,255))
            pygame.draw.circle(screen, (color[pos[0]]), (pos[1][0], pos[1][1]), snake_size  - pos[0] *2 )
        
        x -= shift_x
        y += shift_y

        # Рисуем еду
        pygame.draw.rect(screen, red, (food_position[0], food_position[1], snake_size, snake_size))
        
        # Обновляем экран
        pygame.display.flip()

        # Выход из программы при нажатии на клавишу 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

    ########################Конец игрового цикла############################################
        
game_loop()


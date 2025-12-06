import random, pygame, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
REVEALSPEED = 12 # Faster animations
BOXSIZE = 50
GAPSIZE = 15
BOARDWIDTH = 6
BOARDHEIGHT = 4

assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2) + 100

# Colors
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
LIGHTBLUE = (100, 150, 200)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

# Fun text themes (exciting words instead of emojis!)
THEMES = {
    'animals': ['Dog', 'Cat', 'Mouse', 'Hamster', 'Rabbit', 'Fox', 'Bear', 'Panda', 'Koala', 'Tiger', 'Lion', 'Frog'],
    'food': ['Apple', 'Banana', 'Grape', 'Strawberry', 'Orange', 'Kiwi', 'Peach', 'Cherry', 'Pineapple', 'Coconut', 'Watermelon', 'Lemon'],
    'space': ['Rocket', 'UFO', 'Star', 'Moon', 'Sun', 'Planet', 'Galaxy', 'Comet', 'Alien', 'Robot', 'Sparkle', 'Meteor'],
    'objects': ['Balloon', 'Gift', 'Game', 'Phone', 'Gem', 'Key', 'Shield', 'Sword', 'Wand', 'Hat', 'Toy', 'Dice']
}
ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
assert len(THEMES['animals']) * len(ALLCOLORS) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of words/colors defined."

SCORE_MATCH = 10
SCORE_MISMATCH = -5
SCORE_HINT = -20
START_TIME = 90
FONT_SIZE = 28
UI_BOX_COLOR = (0, 0, 0, 128)

def main():
    global FPSCLOCK, DISPLAYSURF, FONT, theme_name
    pygame.init()
    pygame.mixer.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    FONT = pygame.font.Font(None, FONT_SIZE) # Default font for UI and icons

    pygame.display.set_caption('Memory Game - Fun Edition!')

    # Start screen
    showStartScreen()

    score = 0
    level = 1
    time_left = START_TIME
    last_time = pygame.time.get_ticks()
    streak = 0
    theme_name = 'animals' # Start with animals

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None

    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False
        mousex = 0 # Initialize here to avoid UnboundLocalError
        mousey = 0
        current_time = pygame.time.get_ticks()
        time_left -= (current_time - last_time) / 1000.0
        last_time = current_time

        if time_left <= 0:
            gameOverAnimation("Time's Up! Press R to Restart", score, streak)
            score = 0
            level = 1
            time_left = START_TIME
            streak = 0
            mainBoard = getRandomizedBoard()
            revealedBoxes = generateRevealedBoxesData(False)
            startGameAnimation(mainBoard)
            continue

        drawGradientBackground()
        drawBoard(mainBoard, revealedBoxes)
        drawUI(score, time_left, level, streak)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_r:
                score = 0
                level = 1
                time_left = START_TIME
                streak = 0
                mainBoard = getRandomizedBoard()
                revealedBoxes = generateRevealedBoxesData(False)
                startGameAnimation(mainBoard)
            elif event.type == KEYUP and event.key == K_t:
                theme_list = list(THEMES.keys())
                current_index = theme_list.index(theme_name)
                theme_name = theme_list[(current_index + 1) % len(theme_list)]
                mainBoard = getRandomizedBoard()
                revealedBoxes = generateRevealedBoxesData(False)
                startGameAnimation(mainBoard)
            elif event.type == KEYUP and event.key == K_h:
                if score >= abs(SCORE_HINT):
                    score += SCORE_HINT
                    hintBoxes = getRandomPair(mainBoard, revealedBoxes)
                    if hintBoxes:
                        revealBoxesAnimation(mainBoard, hintBoxes)
                        pygame.time.wait(1500)
                        coverBoxesAnimation(mainBoard, hintBoxes)
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True
                if firstSelection == None:
                    firstSelection = (boxx, boxy)
                else:
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00\x00\x00\x00\x00\x00\x00\x00')).play()
                        score += SCORE_MISMATCH
                        streak = 0
                        pygame.time.wait(1000)
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    else:
                        pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x01\x00\x00\x00\x00\x00\x00\x00')).play()
                        score += SCORE_MATCH
                        streak += 1
                        # Confetti on match!
                        for _ in range(20):
                            x = random.randint(0, WINDOWWIDTH)
                            y = random.randint(0, WINDOWHEIGHT)
                            color = random.choice(ALLCOLORS)
                            pygame.draw.circle(DISPLAYSURF, color, (x, y), 2)
                        pygame.display.update()
                        pygame.time.wait(500) # Brief celebration
                        if hasWon(revealedBoxes):
                            gameWonAnimation(mainBoard, score, level, streak)
                            level += 1
                            time_left = START_TIME
                            mainBoard = getRandomizedBoard()
                            revealedBoxes = generateRevealedBoxesData(False)
                            drawBoard(mainBoard, revealedBoxes)
                            pygame.display.update()
                            pygame.time.wait(1000)
                            startGameAnimation(mainBoard)
                    firstSelection = None

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showStartScreen():
    DISPLAYSURF.fill(BGCOLOR)
    title_text = FONT.render('Memory Game - Fun Edition!', True, WHITE)
    rules = [
        'Rules:',
        '- Click boxes to reveal and match pairs.',
        '- Match all to win and level up.',
        '- Watch the timer!',
        '- Press T to change theme.',
        '- Press H for a hint (-20 points).',
        '- Press R to restart anytime.',
        '',
        'Press S to Start!'
    ]
    DISPLAYSURF.blit(title_text, (WINDOWWIDTH // 2 - title_text.get_width() // 2, 50))
    y_offset = 100
    for line in rules:
        rule_text = FONT.render(line, True, WHITE)
        DISPLAYSURF.blit(rule_text, (WINDOWWIDTH // 2 - rule_text.get_width() // 2, y_offset))
        y_offset += 30
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_s:
                print("S pressed, starting game!") # Debug print
                return

def drawGradientBackground():
    for y in range(WINDOWHEIGHT):
        color = (
            int(NAVYBLUE[0] + (LIGHTBLUE[0] - NAVYBLUE[0]) * (y / WINDOWHEIGHT)),
            int(NAVYBLUE[1] + (LIGHTBLUE[1] - NAVYBLUE[1]) * (y / WINDOWHEIGHT)),
            int(NAVYBLUE[2] + (LIGHTBLUE[2] - NAVYBLUE[2]) * (y / WINDOWHEIGHT))
        )
        pygame.draw.line(DISPLAYSURF, color, (0, y), (WINDOWWIDTH, y))

def drawUI(score, time_left, level, streak):
    ui_surf = pygame.Surface((220, 140), pygame.SRCALPHA)
    ui_surf.fill(UI_BOX_COLOR)
    DISPLAYSURF.blit(ui_surf, (10, 10))
    score_text = FONT.render(f'Score: {score}', True, WHITE)
    time_text = FONT.render(f'Time: {int(time_left)}s', True, WHITE)
    level_text = FONT.render(f'Level: {level}', True, WHITE)
    streak_text = FONT.render(f'Streak: {streak}', True, YELLOW)
    theme_text = FONT.render(f'Theme: {theme_name}', True, CYAN)
    DISPLAYSURF.blit(score_text, (20, 20))
    DISPLAYSURF.blit(time_text, (20, 45))
    DISPLAYSURF.blit(level_text, (20, 70))
    DISPLAYSURF.blit(streak_text, (20, 95))
    DISPLAYSURF.blit(theme_text, (20, 120))

def gameOverAnimation(message, score, streak):
    DISPLAYSURF.fill(BGCOLOR)
    msg_text = FONT.render(message, True, WHITE)
    score_text = FONT.render(f'Final Score: {score} Streak: {streak}', True, WHITE)
    DISPLAYSURF.blit(msg_text, (WINDOWWIDTH // 2 - msg_text.get_width() // 2, WINDOWHEIGHT // 2 - 50))
    DISPLAYSURF.blit(score_text, (WINDOWWIDTH // 2 - score_text.get_width() // 2, WINDOWHEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(3000)

def gameWonAnimation(board, score, level, streak):
    for _ in range(100): # Bigger confetti for win
        x = random.randint(0, WINDOWWIDTH)
        y = random.randint(0, WINDOWHEIGHT)
        color = random.choice(ALLCOLORS)
        pygame.draw.circle(DISPLAYSURF, color, (x, y), 3)
    win_text = FONT.render(f'You Win! Score: {score} Streak: {streak}', True, WHITE)
    DISPLAYSURF.blit(win_text, (WINDOWWIDTH // 2 - win_text.get_width() // 2, WINDOWHEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(2000)

def getRandomPair(board, revealed):
    pairs = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if not revealed[x][y]:
                shape, color = getShapeAndColor(board, x, y)
                pairs.append((x, y, shape, color))
    random.shuffle(pairs)
    for i in range(len(pairs) - 1):
        if pairs[i][2] == pairs[i+1][2] and pairs[i][3] == pairs[i+1][3]:
            return [(pairs[i][0], pairs[i][1]), (pairs[i+1][0], pairs[i+1][1])]
    return None

def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT)
    return revealedBoxes

def getRandomizedBoard():
    words = THEMES[theme_name]
    icons = [(words[i % len(words)], random.choice(ALLCOLORS)) for i in range(BOARDWIDTH * BOARDHEIGHT // 2)]
    random.shuffle(icons)
    numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2)
    icons = icons[:numIconsUsed] * 2
    random.shuffle(icons)

    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0]
        board.append(column)
    return board

def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)

def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def drawIcon(word, color, boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    text = FONT.render(word, True, color)
    DISPLAYSURF.blit(text, (left + BOXSIZE // 2 - text.get_width() // 2, top + BOXSIZE // 2 - text.get_height() // 2))

def getShapeAndColor(board, boxx, boxy):
    return board[boxx][boxy][0], board[boxx][boxy][1]

def drawBoxCovers(board, boxes, coverage):
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE), border_radius=10)
        word, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(word, color, box[0], box[1])
        if coverage > 0:
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE), border_radius=10)
    pygame.display.update()
    FPSCLOCK.tick(FPS)

def revealBoxesAnimation(board, boxesToReveal):
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)

def coverBoxesAnimation(board, boxesToCover):
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE), border_radius=10)
            else:
                word, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(word, color, boxx, boxy)

def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4, border_radius=12)

def startGameAnimation(board):
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x, y))
    random.shuffle(boxes)
    boxGroups = [boxes[i:i + 8] for i in range(0, len(boxes), 8)]

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i:
            return False
    return True

if __name__ == '__main__':
    main()
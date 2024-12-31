import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.fonts import GLUT_BITMAP_HELVETICA_18
import random


WINDOW_WIDTH = 800 
WINDOW_HEIGHT = 600 
BASKET_WIDTH = 40
BASKET_HEIGHT = 30
MAX_MISSED_FRUITS = 20


BUTTON_SIZE = 40 
BUTTON_SPACING = 10
BUTTON_Y = WINDOW_HEIGHT - 50 # Bottom of the screen


game_paused = False
game_over = False
score = 0
hearts = 5
missed_fruits = 0
basket_position = WINDOW_WIDTH // 2
# heart_animation_offset = 0



# List of GameObjects
fruits = [] 
bombs = [] 
eggs = []

class GameObject:    
    def __init__(self, x, y, radius, speed, object_type):
        self.x = x 
        self.y = y
        self.radius = radius # Radius of the object
        self.speed = speed # Speed at which the object falls
        self.type = object_type # Type of object (e.g. apple, bomb, etc.)
        self.missed = False #tracks if the object has been missed

# Button
buttons = {
    'restart': {
        'x': WINDOW_WIDTH - 3*BUTTON_SIZE - 2*BUTTON_SPACING, # X position of the button 
        '''Each button occupies a width of BUTTON_SIZE.
            To place the restart button, we need to account for the widths of:
            The exit button (1 * BUTTON_SIZE)
            The pause button (1 * BUTTON_SIZE)
            The restart button itself (1 * BUTTON_SIZE)
            Therefore, we subtract 3*BUTTON_SIZE from the window width to position the restart button relative to the far-right edge of the window.


            Reason for 2*BUTTON_SPACING
            Buttons are spaced apart horizontally by BUTTON_SPACING.
            Between the restart button and the pause button, there is 1 spacing.
            Between the pause button and the exit button, there is another spacing.
            Therefore, we subtract 2*BUTTON_SPACING to account for these two spaces.'''

        'hover': False, # True if the mouse is hovering over the button
        'color': (0.2, 0.7, 0.2)  
    },
    'pause': {
        'x': WINDOW_WIDTH - 2*BUTTON_SIZE - BUTTON_SPACING,
        'hover': False,
        'color': (0.2, 0.2, 0.7)  
    },
    'exit': {
        'x': WINDOW_WIDTH - BUTTON_SIZE,
        'hover': False,
        'color': (0.7, 0.2, 0.2) 
    }
}

def midpoint_line(x1, y1, x2, y2):    
    '''x1, y1: Coordinates of the starting point of the line.
    x2, y2: Coordinates of the ending point of the line. '''
    
    dx = abs(x2 - x1) 
    dy = abs(y2 - y1)
    ''' dx: The horizontal distance (change in x) between the two points.
    dy: The vertical distance (change in y) between the two points.
    The abs function ensures both are positive, simplifying calculations. '''
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    ''' sx: Determines whether the x-coordinate should increment (1) or decrement (-1) based on the direction of the line.
    sy: Determines whether the y-coordinate should increment (1) or decrement (-1) based on the direction of the line.
    These ensure the algorithm can handle all quadrants and line directions. '''

    err = dx - dy 
    '''If dx > dy, the line is more horizontal.
    If dx < dy, the line is more vertical.'''

    glBegin(GL_POINTS)
    while True:
        glVertex2f(x1, y1)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err # Calculate the error term for the next step
        if e2 > -dy:
            err -= dy
            x1 += sx # If e2 > -dy, the error allows a horizontal or diagonal step: Subtracts dy from err to reflect horizontal movement. Adjusts x1 by sx (move left or right).
        if e2 < dx: # If e2 < dx, the error allows a vertical or diagonal step: Adds dx to err to reflect vertical movement. Adjusts y1 by sy (move up or down).
            err += dx 
            y1 += sy
    glEnd()

def fill_circle(x, y, radius):    #x.y are the center of the circle
    glBegin(GL_POINTS)
    for dy in range(-radius, radius + 1): # Iterate over the vertical range of the circle
        for dx in range(-radius, radius + 1): # Iterate over the horizontal range of the circle
            if dx*dx + dy*dy <= radius*radius: # Check if the point is within the circle
                glVertex2f(x + dx, y + dy) # Draw the point
    glEnd()

def draw_apple(x, y, radius):    
    glBegin(GL_POINTS)
    glColor3f(0.8, 0.1, 0.1)
    for dy in range(-radius, radius + 1): # Iterate over the vertical range of the apple
        height_scale = 1.1  # apple taller than wide
        width = int(math.sqrt(radius*radius - (dy/height_scale)**2)) # Calculate the width of the apple at the current height
        ''' x^2 + y^2 = r^2 then x = sqrt(r^2 - y^2). Adjust for Elliptical Shape: To make the apple taller than it is wide,
          the vertical offset (here represented by dy) is scaled by height_scale. '''
        for dx in range(-width, width + 1): # Iterate over the horizontal range of the apple
            glVertex2f(x + dx, y + dy) # Draw the point

    glColor3f(0.4, 0.2, 0.0)#stem
    for i in range(10): # Draws the apple's stem above the body.
        stem_x = x + math.sin(i/3.0) * 2 #
        ''' create a slight sinusoidal curve for the stem, mimicking a natural look. '''
        stem_y = y + radius + i
        for dx in range(-1, 2): # Draws the stem as a 3-pixel wide horizontal line for each i.
            glVertex2f(stem_x + dx, stem_y) 


    glColor3f(0.2, 0.8, 0.2)#leaf
    for i in range(8): #create a slight sinusoidal curve for the stem, mimicking a natural look.
        leaf_x = x + 3 + i #Creates a curved leaf by offsetting leaf_x horizontally (x + 3 + i) and modulating the vertical position leaf_y with a sine function for curvature.
        leaf_y = y + radius + math.sin(i/2.0) * 3 #Creates a curved leaf by offsetting leaf_x horizontally (x + 3 + i) and modulating the vertical position leaf_y with a sine function for curvature.
        for dy in range(-2, 3): # Draws the leaf as a 5-pixel wide vertical line for each i.
            glVertex2f(leaf_x, leaf_y + dy)    
    glEnd()

def draw_banana(x, y, radius):
    glBegin(GL_POINTS)
    glColor3f(1.0, 0.8, 0.0) 
    for t in range(60):
        angle = t * math.pi / 60  # Convert the angle to radians. This divides half a circle (π) into 60 equal segments, forming the curve.
        curve_x = x + radius * math.cos(angle) # Calculate the x-coordinate of the curve point by multiplying the radius by the cosine of the angle.
        curve_y = y + radius * math.sin(angle) * 0.7  # Calculate the y-coordinate of the curve point by multiplying the radius by the sine of the angle and scaling it by 0.7.
        ''' The vertical component is scaled by 0.7 to squash the curve, making it more "banana-like" (elongated horizontally).'''
        thickness = int(5 + 3 * abs(math.sin(angle)))  # Calculate the thickness of the curve at the current angle. This creates a visually appealing, slightly uneven width.
        for r in range(-thickness, thickness + 1): # Iterate over the thickness of the curve.
            px = curve_x + r * math.cos(angle + math.pi/2) # Calculate the x-coordinate of the point on the curve. The x-coordinate is offset by r * cos(angle + π/2) to create the curve.
            py = curve_y + r * math.sin(angle + math.pi/2) # Calculate the y-coordinate of the point on the curve. The y-coordinate is offset by r * sin(angle + π/2) to create the curve.
            glVertex2f(px, py)
    

    glColor3f(0.4, 0.2, 0.0)  
    for dx in range(-3, 4): # Draws the stem as a 7-pixel wide horizontal line.
        for dy in range(-3, 4): # Draws the stem as a 7-pixel wide vertical line.
            if dx*dx + dy*dy <= 9: # Check if the point is within the stem. and This ensures the ends are circular.
                glVertex2f(x - radius + dx, y + dy)   #the left end of the banana
                glVertex2f(x + radius + dx, y + dy)  #the right end of the banana
    glEnd()

    ''' Curved Body:
    Created using a sine and cosine-based curve.
    Adjusted for banana-like shape with vertical squashing and sinusoidal thickness.
    Ends:
    Drawn as small circular regions at both tips of the banana.
    Colors:
    Body: Yellow.
    Ends: Brown (to mimic the natural stem and tip).
    This combination creates a visually distinct and recognizable banana shape!'''


def draw_grape(x, y, radius):
    glBegin(GL_POINTS)

    glColor3f(0.6, 0.2, 0.8)  
    offsets = [
        (0, 0), (radius, 0), (-radius, 0),  # First row. The center grape and two side grapes in the top row.
        (-radius//2, -radius), (radius//2, -radius),  # Second row. Two grapes slightly below and centered under the first row.
        (0, -2*radius)  # Third row. A single grape at the bottom center.
    ]
    for ox, oy in offsets: # Iterate over the offsets to draw the grapes.
        for dy in range(-radius, radius + 1): # Iterate over the vertical range of the grape.
            circle_width = int(math.sqrt(radius*radius - dy**2)) # Calculate the width of the grape at the current height. circle width = sqrt(radius^2 - dy^2)
            for dx in range(-circle_width, circle_width + 1): # Iterate over the horizontal range of the grape.
                glVertex2f(x + ox + dx, y + oy + dy) # Draw the point by offsetting the x and y coordinates by the current offset values.
    
    glEnd()
    
    #stem
    glBegin(GL_POINTS)
    glColor3f(0.4, 0.2, 0.0)  
    for i in range(radius * 2): # Draws the stem as a 2*radius wide horizontal line.
        stem_x = x # The stem is centered at the x-coordinate of the grape.
        stem_y = y + radius + i # The stem starts at the bottom of the grape and extends upwards.
        for dx in range(-1, 2):  # Draws the stem as a 3-pixel wide horizontal line for each i.
            '''Grapes:
                Rendered as a cluster of overlapping circles.
                Arranged in three rows using offsets.
                Stem:
                A thin vertical rectangle drawn above the cluster.'''
            glVertex2f(stem_x + dx, stem_y)
    glEnd()



def draw_egg(x, y, radius):
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 0.9)
    for dy in range(-radius, radius + 1): # Iterate over the vertical range of the egg.
        width_scale = 1.0 + 0.3 * (dy / radius) # Scale the width of the egg based on the current height.
        width = int(math.sqrt(radius*radius - dy*dy) * width_scale) # Calculate the width of the egg at the current height. ellipse equation
        for dx in range(-width, width + 1): # Iterate over the horizontal range of the egg.
            glVertex2f(x + dx, y + dy)

    glColor3f(1.0, 1.0, 1.0)
    highlight_radius = radius // 3 #  we want to draw the highlight on the top of the egg
    for dy in range(-highlight_radius, highlight_radius + 1): # Iterate over the vertical range of the highlight.
        for dx in range(-highlight_radius, highlight_radius + 1): # Iterate over the horizontal range of the highlight.
            if dx*dx + dy*dy <= highlight_radius*highlight_radius: # Check if the point is within the highlight.
                glVertex2f(x - radius//3 + dx, y + radius//3 + dy)  
    glEnd()

def draw_bomb(x, y, radius):
    glColor3f(0.1, 0.1, 0.1)
    fill_circle(x, y, radius) # Draw the bomb as a filled circle.
    
    glBegin(GL_POINTS)
    glColor3f(0.6, 0.3, 0.0) # Draw the fuse as a series of points.
    for i in range(12): # Iterate over the fuse points.
        fuse_x = x + math.sin(i/2.0) * 2 #Curvy fuse. Calculate the x-coordinate of the fuse point.
        fuse_y = y + radius + i # Calculate the y-coordinate of the fuse point.
        for dx in range(-1, 2): # Draw the fuse as a 3-pixel wide horizontal line for each i.
            glVertex2f(fuse_x + dx, fuse_y) 

    glColor3f(0.3, 0.3, 0.3)
    highlight_radius = radius // 3 #to stimulate light reflection
    for dy in range(-highlight_radius, highlight_radius + 1): # Iterate over the vertical range of the highlight.
        for dx in range(-highlight_radius, highlight_radius + 1): # Iterate over the horizontal range of the highlight.
            if dx*dx + dy*dy <= highlight_radius*highlight_radius: # Check if the point is within the highlight.
                glVertex2f(x - radius//3 + dx, y + radius//3 + dy)
    glEnd()

def draw_button(x, y, button_type, hover):
    button = buttons[button_type]
    color = button['color']

    if hover:
        glColor3f(color[0] + 0.2, color[1] + 0.2, color[2] + 0.2) # Lighten the color when the button is hovered over.
    else:
        glColor3f(*color) # Set the color of the button.

    fill_circle(x + BUTTON_SIZE//2, y + BUTTON_SIZE//2, BUTTON_SIZE//2) # Draw the button as a filled circle.
    
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 1.0)
    

    if button_type == 'restart':
        for i in range(30): # Draw the restart button as a circular arrow.
            angle = i * math.pi / 15 # we want to draw 12 arrows
            r = BUTTON_SIZE//3 # Calculate the radius of the arrow.
            px = x + BUTTON_SIZE//2 + r * math.cos(angle) # Calculate the x-coordinate of the arrow point. as we are drawing the arrow in the center of the button
            py = y + BUTTON_SIZE//2 + r * math.sin(angle) # Calculate the y-coordinate of the arrow point. as we are drawing the arrow in the center of the button
            for dx in range(-1, 2): # Draw the arrow as a 3-pixel wide horizontal line 
                for dy in range(-1, 2): # Draw the arrow as a 3-pixel wide vertical line
                    glVertex2f(px + dx, py + dy)
    elif button_type == 'pause':
        for i in range(BUTTON_SIZE//2): # Draw the pause button as two horizontal lines.
            glVertex2f(x + BUTTON_SIZE//3, y + BUTTON_SIZE//3 + i)
            glVertex2f(x + 2*BUTTON_SIZE//3, y + BUTTON_SIZE//3 + i)
    elif button_type == 'exit':
        for i in range(-BUTTON_SIZE//4, BUTTON_SIZE//4): # Draw the exit button as a diagonal line.
            glVertex2f(x + BUTTON_SIZE//2 + i, y + BUTTON_SIZE//2 + i)
            glVertex2f(x + BUTTON_SIZE//2 + i, y + BUTTON_SIZE//2 - i)
    
    glEnd()

def check_button_hover(mouse_x, mouse_y):
    for button_name, button in buttons.items():
        center_x = button['x'] + BUTTON_SIZE//2
        center_y = BUTTON_Y + BUTTON_SIZE//2
        distance = math.sqrt((mouse_x - center_x)**2 + (mouse_y - center_y)**2) #Computes the Euclidean distance between the mouse pointer
        button['hover'] = distance <= BUTTON_SIZE//2

def mouse_motion(x, y):
    '''inverts the y-coordinate to match the OpenGL coordinate system, as mouse coordinates are typically provided with the origin at the top-left corner, while OpenGL has the origin at the bottom-left. '''

    y = WINDOW_HEIGHT - y  
    check_button_hover(x, y)
    glutPostRedisplay()

def mouse_click(button, state, x, y):
    """Handles mouse clicks."""
    global game_paused, game_over
    
    if state == GLUT_DOWN and button == GLUT_LEFT_BUTTON:
        y = WINDOW_HEIGHT - y
        for button_name, button_data in buttons.items():
            center_x = button_data['x'] + BUTTON_SIZE//2
            center_y = BUTTON_Y + BUTTON_SIZE//2
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            if distance <= BUTTON_SIZE//2:
                if button_name == 'restart':
                    reset_game()
                elif button_name == 'pause':
                    game_paused = not game_paused
                elif button_name == 'exit':
                    glutLeaveMainLoop()

def create_fruit():
    fruit_types = [
        ('apple', 1, (1.0, 0.0, 0.0)),
        ('banana', 2, (1.0, 0.8, 0.0)),
        ('grape',3, (0.6, 0.2, 0.8))
    ]
    fruit_type = random.choice(fruit_types)
    return GameObject(
        random.randint(30, WINDOW_WIDTH - 30),
        WINDOW_HEIGHT + 20,
        15,
        random.uniform(1, 2),
        {'name': fruit_type[0], 'points': fruit_type[1], 'color': fruit_type[2]}
    )

def create_bomb():
    return GameObject(
        random.randint(30, WINDOW_WIDTH - 30),
        WINDOW_HEIGHT + 20,
        12,
        random.uniform(2.5, 3.5),
        {'name': 'bomb', 'damage': 2, 'color': (0.2, 0.2, 0.2)}
    )

def create_egg():
    return GameObject(
        random.randint(30, WINDOW_WIDTH - 30),
        WINDOW_HEIGHT + 20,10, random.uniform(2.0, 3.0),
        {'name': 'egg', 'heal': 1, 'color': (1.0, 1.0, 0.9)}
    )

def draw_basket():
    glColor3f(0.8, 0.6, 0.4)
    for i in range(-BASKET_WIDTH, BASKET_WIDTH + 1, 2): # Draw the basket as a series of vertical lines.
        x = basket_position + i #by adding i to the basket position, we can draw the basket centered at the basket position.
        y = 60 - int((-i * i) / (BASKET_WIDTH * 4)) #by adding i to the basket position, we can draw the basket centered at the basket position.
        midpoint_line(x, y, x + 2, y) # Draw a vertical line segment of the basket.

    midpoint_line(basket_position - BASKET_WIDTH, 60,
                 basket_position - BASKET_WIDTH + 15, 30)
    midpoint_line(basket_position + BASKET_WIDTH, 60,
                 basket_position + BASKET_WIDTH - 15, 30)
    midpoint_line(basket_position - BASKET_WIDTH + 15, 30,
                 basket_position + BASKET_WIDTH - 15, 30)

def update_game_state():
    global score, hearts, missed_fruits, game_over    
    if game_paused or game_over:
        return
    
    for fruit in fruits[:]:
        fruit.y -= fruit.speed
        if fruit.y < 0:
            fruits.remove(fruit)
            missed_fruits += 1
            if missed_fruits % 3 == 0:  
                hearts -= 1
                if hearts <= 0:
                    game_over = True
        elif check_collision(fruit):
            score += fruit.type['points']
            fruits.remove(fruit)
            missed_fruits = 0  
    for bomb in bombs[:]:
        bomb.y -= bomb.speed
        if bomb.y < 0:
            bombs.remove(bomb)
        elif check_collision(bomb):
            hearts -= 2  # Decrease hearts by 2 for bomb collision
            bombs.remove(bomb)
            if hearts <= 0:
                game_over = True

    for egg in eggs[:]:
        egg.y -= egg.speed
        if egg.y < 0:
            eggs.remove(egg)
        elif check_collision(egg):
            hearts = min(hearts + 1, 5)  
            eggs.remove(egg)


def check_collision(obj):
    basket_left = basket_position - BASKET_WIDTH
    basket_right = basket_position + BASKET_WIDTH
    basket_top = 60
    basket_bottom = 30
    if obj.y - obj.radius <= basket_top and obj.y - obj.radius >= basket_bottom:
        if basket_left <= obj.x <= basket_right:
            return True
    return False

def spawn_objects():
    if game_paused or game_over:
        return

    fruit_chance = 0.02 + min(score / 1000, 0.03)  # Increases with score
    bomb_chance = 0.01 + min(score / 2000, 0.02)   # Increases with score
    egg_chance = 0.005                             # Remains constant
    
    if random.random() < fruit_chance:
        fruits.append(create_fruit())
    if random.random() < bomb_chance:
        bombs.append(create_bomb())
    if random.random() < egg_chance:
        eggs.append(create_egg())

def draw_hearts():
    for i in range(hearts):
        heart_x = WINDOW_WIDTH // 2 - (hearts * 15) + i * 30 # Center the hearts at the top of the window by subtracting half the total width of the hearts.
        heart_y = WINDOW_HEIGHT - 30   # Draw the heart at the top of the window. by subtracting 30 from the window height  
        glColor3f(1.0, 0.2, 0.2)
        glBegin(GL_POINTS)
        for t in range(360): # Draw the heart as a series of points as a heart shape.
            angle = math.radians(t) # Convert the angle to radians.
            x = 16 * math.sin(angle) ** 3 # Calculate the x-coordinate of the heart point.
            y = 13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) # Calculate the y-coordinate of the heart point by combining three cosine functions.
            scale = 0.7
            glVertex2f(heart_x + x * scale, heart_y + y * scale) # Draw the point at the scaled x and y coordinates by adding the heart_x and heart_y offsets.
        glEnd()

def draw_text(x, y, text): # Draw text on the screen.
    glColor3f(0.0, 0.0, 0.0)
    glRasterPos2f(x + 1, y - 1) # Draw the text shadow by offsetting the position by (1, -1).
    for ch in text: #
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch)) # Draw the text using the 18-point Helvetica font.
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def display():
    glClear(GL_COLOR_BUFFER_BIT)    
    if not game_over:
        draw_basket()        
        for fruit in fruits: # Draw the fruits, bombs, and eggs on the screen.
            if fruit.type['name'] == 'apple': # Draw the fruit based on its type.
                draw_apple(fruit.x, fruit.y, fruit.radius) # Draw the apple at the fruit's position.
            elif fruit.type['name'] == 'banana': 
                draw_banana(fruit.x, fruit.y, fruit.radius)
            elif fruit.type['name'] == 'grape':
                draw_grape(fruit.x, fruit.y, fruit.radius)
        
        for bomb in bombs:
            draw_bomb(bomb.x, bomb.y, bomb.radius) # Draw the bomb at the bomb's position.
        
        for egg in eggs:
            draw_egg(egg.x, egg.y, egg.radius)
        
        draw_hearts() # Draw the hearts at the top of the window.
        draw_text(10, WINDOW_HEIGHT - 30,f"Score: {score}  Missed: {missed_fruits}/{MAX_MISSED_FRUITS}") # Draw the score and missed fruits at the top-left corner of the window.

        if game_paused:
            draw_text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2, "PAUSED")
        

        for button_name, button in buttons.items():
            draw_button(button['x'], BUTTON_Y, button_name, button['hover'])
    else:
        draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 
                 f"Game Over! Final Score: {score}")
        draw_text(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 - 30,
                 "Click the Restart button to play again!")
        
        for button_name, button in buttons.items():
            if button_name in ['restart', 'exit']:
                draw_button(button['x'], BUTTON_Y, button_name, button['hover'])
    
    glutSwapBuffers()

def update(value):
    spawn_objects()
    update_game_state()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0) 

def keyboard(key, x, y):
    global basket_position, game_paused    
    movement_speed = 10    
    if key == b'a' and basket_position > BASKET_WIDTH:
        basket_position = max(BASKET_WIDTH, basket_position - movement_speed)
    elif key == b'd' and basket_position < WINDOW_WIDTH - BASKET_WIDTH:
        basket_position = min(WINDOW_WIDTH - BASKET_WIDTH, 
                            basket_position + movement_speed)
    elif key == b'p':
        game_paused = not game_paused
    elif key == b'q':
        glutLeaveMainLoop()

def reset_game():
    global game_paused, game_over, score, hearts, missed_fruits
    global fruits, bombs, eggs, basket_position
    
    game_paused = False
    game_over = False
    score = 0
    hearts = 5
    missed_fruits = 0
    basket_position = WINDOW_WIDTH // 2
    fruits.clear()
    bombs.clear()
    eggs.clear()


glutInit() # Initialize the OpenGL utility toolkit.
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB) # Set the display mode to use double buffering and RGB color.
glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT) # Set the initial window size.
glutInitWindowPosition(100, 100) # Set the initial window position.
glutCreateWindow(b"Fruit Frenzy") # Create the window with the specified title.
glClearColor(0.0, 0.0, 0.1, 1.0)  ##Dark Blue BG
glMatrixMode(GL_PROJECTION) # Set the matrix mode to GL_PROJECTION.
glLoadIdentity() # Load the identity matrix.
gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT) # Set the orthographic projection.
glutDisplayFunc(display) # Set the display callback function.
glutKeyboardFunc(keyboard) # Set the keyboard callback function.
glutTimerFunc(16, update, 0) # Set the timer callback function.
glutPassiveMotionFunc(mouse_motion) # Set the mouse motion callback function.
glutMouseFunc(mouse_click) # Set the mouse click callback function.

print("\nFruit Frenzy Controls:")
print("A/D - Move basket left/right")
print("P - Pause/Unpause game")
print("Q - Quit game")
print("\nMouse Controls:")
print("- Click the circular buttons to:")
print("  * Restart game (Green)")
print("  * Pause/Play (Blue)")
print("  * Exit game (Red)")

glutMainLoop()

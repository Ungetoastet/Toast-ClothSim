import sys, pygame, math, time

# Function definitions
def normalise(vec):
    biggest = abs(max(abs(vec[0]), abs(vec[1])))
    if biggest != 0:
        normed = [vec[0]/biggest, vec[1]/biggest]
    else:
        normed = [0, 0]
    return normed

def calc_distance(p1, p2):
    dis = math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))
    return dis

# Class definitions
class point:
    def __init__(self, pos, loc):
        super().__init__()
        self.position = pos
        self.speed = [0, 0]
        self.force = [0, 0]
        self.locked = loc


class connector:
    def __init__(self, pa, pb, le):
        super().__init__()
        self.point_a = pa
        self.point_b = pb
        self.length = le
        self.middle = [0, 0]
        self.strechlen = 0


# Pygame render setup
pygame.init()
size = width, height = 1920, 1080
bg = 50, 50, 50
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Cloth Simulation")
pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


# Simulation setup
gravity = 0.25
sim = True
cloth_y = 12    
cloth_x = 50
dist = 20
points = []
conns = []
conn_force = 0.3
drag = 0.9
fix_height = 10
a = width/2 - ((cloth_x-1) * dist)/2
maximumforce = 100
conn_strength = 3

# Grid spawning
for x in range(cloth_x):
    if x%3 == 0:
        points.append(point([a + x * dist, fix_height], True))
    else:
        points.append(point([a + x * dist, fix_height], False))
    for y in range(cloth_y):
        points.append(point([a + x * dist, fix_height + y*dist + dist], False))
        
# Connection spawning
for i in range(len(points)-1): # Vertical
    if i%(cloth_y+1) != cloth_y:
        newc = connector(points[i], points[i+1], dist+10)
        conns.append(newc)
for i in range(len(points)-1-cloth_y): # Horizontal
    newc = connector(points[i], points[i+cloth_y + 1], dist)
    conns.append(newc)

print('Points: ' + str(len(points)))
print('Connectors: ' + str(len(conns)))

target_fps = 60
cpf = 5
grabbed_index = None

# Main Loop
while True:
    connlen = len(conns)
    startTime = time.time()
    # User Interaction
    if pygame.mouse.get_pressed()[0]: # Drag points
        mousepos = pygame.mouse.get_pos()
        if grabbed_index == None:
            smallest_index = 0
            smallest_distace = 1000
            for i in range(len(points)): # Find closest point to mouse
                d = calc_distance(mousepos, points[i].position)
                if d < smallest_distace:
                    smallest_distace = d
                    smallest_index = i

            grabbed_index = smallest_index
            points[grabbed_index].locked = True
        points[grabbed_index].position = mousepos
    
    else:
        if grabbed_index != None:
            points[grabbed_index].locked = False
            grabbed_index = None

    if pygame.mouse.get_pressed()[2]: # Drag and lock points
        mousepos = pygame.mouse.get_pos()
        smallest_index = 0
        smallest_distace = 1000
        for i in range(len(points)): # Find closest point to mouse
            d = calc_distance(mousepos, points[i].position)
            if d < smallest_distace:
                smallest_distace = d
                smallest_index = i

        if grabbed_index == None:
            grabbed_index = smallest_index
            points[grabbed_index].locked = True
            points[grabbed_index].position = mousepos
            grabbed_index = None

    if pygame.mouse.get_pressed()[1]: # Cut
        mousepos = pygame.mouse.get_pos()
        smallest_index = 0
        smallest_distace = 1000
        for i in range(len(conns)): # Find closest point to mouse
            d = calc_distance(mousepos, conns[i].middle)
            if d < smallest_distace:
                smallest_distace = d
                smallest_index = i

        if smallest_distace <= conns[smallest_index].strechlen/2:
            del conns[smallest_index]
            connlen -= 1

    if sim:
        for iterations in range(cpf):
            for p in points:
                p.force = [0, 0]

            # Simulate -----------------------------------------------------------
            for c in conns:
                direction = normalise([c.point_a.position[0] - c.point_b.position[0], c.point_a.position[1] - c.point_b.position[1]])
                distance = calc_distance(c.point_a.position, c.point_b.position)
                if not c.point_a.locked:
                    c.point_a.force = [c.point_a.force[0] - direction[0] * (distance - c.length), c.point_a.force[1] - direction[1] * (distance - c.length)]
                if not c.point_b.locked:
                    c.point_b.force = [c.point_b.force[0] + direction[0] * (distance - c.length), c.point_b.force[1] + direction[1] * (distance - c.length)]
            for p in points:
                if not p.locked: # apply force
                    if abs(p.force[0]) > maximumforce or abs(p.force[0]) > maximumforce: # Limit force
                        p.force = normalise(p.force)*maximumforce
                    p.speed = [drag * (p.speed[0] + p.force[0]*conn_force), drag * (p.speed[1] + p.force[1]*conn_force + gravity)]
                    p.position = [p.position[0] + p.speed[0], p.position[1] + p.speed[1]]

        brokenconns = []
        for i in range(connlen):
            conns[i].middle = [(conns[i].point_a.position[0] + conns[i].point_b.position[0]) / 2, (conns[i].point_a.position[1] + conns[i].point_b.position[1]) / 2]
            conns[i].strechlen = calc_distance(conns[i].point_a.position, conns[i].point_b.position)
            if conns[i].strechlen > dist*conn_strength:
                brokenconns.append(i)
        for x in brokenconns:
            del conns[x]

    # Quit -----------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # Draw -----------------------------------------------------------
    screen.fill(bg)
    p_col = (200, 200, 255)
    c_col = (150, 150, 200)
    p_col_l = (255, 200, 200)
    for c in conns:
        pygame.draw.line(screen, c_col, c.point_a.position, c.point_b.position, 3)
    for p in points:
        if p.locked:
            pygame.draw.circle(screen, p_col_l, p.position, 7)
        else:
            pygame.draw.circle(screen, p_col, p.position, 5)
    pygame.display.flip()

    deltaTime = time.time() - startTime
    target_delta = 1/target_fps
    if deltaTime < target_delta:
        time.sleep(target_delta - deltaTime)

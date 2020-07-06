import pygame
import neat
import os
import time
import random

# Initialize the fonts for pygame
pygame.font.init()

# Set window resolution
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800


# Load images
BIRD_IMG = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


# Bird class
class Bird:
    # Constants
    IMGS = BIRD_IMG
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    # Bird init
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    # Jump function
    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    # Move function called every tick
    def move(self):
        # Increment the tick counter
        self.tick_count += 1

        # Compute the displacement value
        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2
        # Apply the displacement
        self.y += displacement
        # Tilt the bird
        if displacement < 0 or self.y < self.height + 50:
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_VELOCITY

    # Draw the bird on a window
    def draw(self, window):
        # Update the image count
        self.img_count += 1

        # Use the right image for the bird animation
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.angle <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # Rotate the image with the the angle value
        rotated_image = pygame.transform.rotate(self.img, self.angle)
        new_rectangle = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)

        # Place the bird into the window
        window.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# Pipe class
class Pipe:
    # Constants
    GAP = 200
    VELOCITY = 5

    # Pipe init
    def __init__(self, x):
        self.x = x
        self.y = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    # Set the top and bottom pipes heights
    def set_height(self):
        self.y = random.randrange(50, 450)
        self.top = self.y - self.PIPE_TOP.get_height()
        self.bottom = self.y + self.GAP

    # Move the pipe
    def move(self):
        self.x -= self.VELOCITY

    # Draw the pipe the a window
    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # Check if the pipe is colliding with a bird
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        return t_point or b_point


# Base class
class Base:
    # Constants
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    # Base init
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # Move the base (Roll between two base images)
    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # Draw the base to a window
    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


# Draw the game window (Executed for every game tick)
def draw_window(window, birds, pipes, base, score):
    window.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(window)

    base.draw(window)

    for bird in birds:
        bird.draw(window)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()


# Game loop
def main(genomes, config):

    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append( net )
        birds.append( Bird(230, 350) )
        g.fitness = 0
        ge.append(g)


    base = Base(730)
    pipes = [Pipe(700)]
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    # Game loop
    while run:
        clock.tick(30)
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((
                bird.y,
                abs(bird.y - pipes[pipe_index].top),
                abs(bird.y - pipes[pipe_index].bottom)
            ))

            if output[0] > 0.5:
                bird.jump()

        # Pipe handler
        add_pipe = False
        remove = []
        for pipe in pipes:
            for x, bird in enumerate(birds):

                # Handle pipe/bird collision
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # Handle when the bird pass a pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # When a pipe is leaving the window add it to the remove list
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)

            # Move the pipe
            pipe.move()

        # Spawn a new pipe
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 10
            pipes.append(Pipe(600))

        # Remove the pipes out of the screen
        for pipe in remove:
            pipes.remove(pipe)

        for x, bird in enumerate(birds):
            # Check if a bird hits the ground or fly above the screen
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        if score > 250:
            break

        base.move()
        draw_window( window, birds, pipes, base, score )


def run( config_path ):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population( config )

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 50)

if __name__ == "__main__":
    local_directory = os.path.dirname( __file__ )
    config_path = os.path.join(local_directory, "neat_config.txt")
    run( config_path )

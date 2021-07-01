# The Nature of Code
# Daniel Shiffman
# http://natureofcode.com

# The "Vehicle" class
from copy import deepcopy


class Vehicle():

    def __init__(self, x, y):
        self.acceleration = PVector(0, 0)
        self.velocity = PVector(0, -2)
        self.position = PVector(x, y)
        self.r = 6
        self.maxspeed = 4
        self.maxforce = 0.2
        self.desired = PVector(0, 0)

    # Method to update location
    def update(self):
        # Update velocity
        self.velocity.add(self.acceleration)
        # Limit speed
        self.velocity.limit(self.maxspeed)
        # Reset accelerationelertion to 0 each cycle
        self.acceleration.mult(0)
        return self.velocity

    def applyForce(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration.add(force)

    # A method that calculates a steering force towards a target
    # STEER = DESIRED MINUS VELOCITY
    def arrive(self, target):
        # A vector pointing from the location to the target
        self.desired = target - self.position

    def display(self):
        # Draw a triangle rotated in the direction of velocity
        theta = self.desired.heading() + PI / 2
        fill(127)
        stroke(200)
        strokeWeight(1)
        ellipse(self.position.x, self.position.y, 25, 25)
        # with pushMatrix():
        #     translate(self.position.x, self.position.y)
        #     rotate(theta)
        #     beginShape()
        #     vertex(0, -self.r * 2)
        #     vertex(-self.r, self.r * 2)
        #     vertex(self.r, self.r * 2)
            # endShape(CLOSE)

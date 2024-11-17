import random
from tkinter import Tk, Button, Label, IntVar, BooleanVar, StringVar, Frame
import math

# Define constants for grid size and initial settings
GRID_SIZE = (8, 13)
INITIAL_CREDIT = 20
INITIAL_BUSTS = 2

class GhostBusterGame:
    def __init__(self, root):
        # Game state variables
        self.root = root
        self.credit = IntVar(master=root, value=INITIAL_CREDIT)
        self.bust_attempts = IntVar(master=root, value=INITIAL_BUSTS)
        self.view_probabilities = BooleanVar(master=root, value=False)
        self.view_directions = BooleanVar(master=root, value=False)
        self.result_label = StringVar(master=root)
        self.bust_mode = BooleanVar(master=root, value=False)

        # Game grid, ghost location, and probabilities
        self.grid = []
        self.ghost_x, self.ghost_y = self.place_ghost()
        self.posterior_probs = {}
        self.compute_initial_prior_probabilities()

        # Initialize UI elements
        self.init_ui()

    def place_ghost(self):
        """Place the ghost randomly on the grid."""
        return random.randint(0, GRID_SIZE[0] - 1), random.randint(0, GRID_SIZE[1] - 1)

    def compute_initial_prior_probabilities(self):
        """Initialize uniform prior probabilities for each cell."""
        prior_prob = 1 / (GRID_SIZE[0] * GRID_SIZE[1])
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                self.posterior_probs[(x, y)] = prior_prob

    def distance_sense(self, xclk, yclk):
        """Calculate the distance from the current position to the ghost and return a color."""
        # Calculate distances in respect to x and y axis
        dx = self.ghost_x - xclk
        dy = self.ghost_y - yclk
        distance = abs(dx) + abs(dy)

        # Now, calculate the direction based on the x and y distances (angle computation)
        angle = math.atan2(dy, dx)
        angle_deg = math.degrees(angle) % 360

        # Determine the cardinal direction based on angle
        if angle_deg >= 337.5 or angle_deg < 22.5:
            direction = '→'
        elif 22.5 <= angle_deg < 67.5:
            direction = '↗'
        elif 67.5 <= angle_deg < 112.5:
            direction = '↑'
        elif 112.5 <= angle_deg < 157.5:
            direction = '↖'
        elif 157.5 <= angle_deg < 202.5:
            direction = '←'
        elif 202.5 <= angle_deg < 247.5:
            direction = '↙'
        elif 247.5 <= angle_deg < 292.5:
            direction = '↓'
        else:
            direction = '↘'

        # Return a color based on the distance and the calculated direction
        if distance == 0:
            return 'Red', direction
        elif distance <= 2:
            return 'Orange', direction
        elif distance <= 4:
            return 'Yellow', direction
        else:
            return 'Green', direction

    def update_posterior_probabilities(self, color, direction, xclk, yclk):
        """Update the posterior probabilities based on sensor readings."""
        for loc, prob in self.posterior_probs.items():
            dist = abs(loc[0] - xclk) + abs(loc[1] - yclk)

            color_prob = self.conditional_color_probability(color, dist)
            direction_prob = self.conditional_direction_probability(direction, loc, xclk, yclk)
            self.posterior_probs[loc] = color_prob * direction_prob * prob

        total_prob = sum(self.posterior_probs.values())
        for loc in self.posterior_probs:
            self.posterior_probs[loc] /= total_prob

    def conditional_direction_probability(self, direction, loc, xclk, yclk):
        """Return the probability of a direction given the agent's position."""
        _, correct_direction = self.distance_sense(xclk, yclk)
        return 0.9 if direction == correct_direction else 0.1

    def conditional_color_probability(self, color, distance):
        """Return the probability of a color given the distance."""
        if distance == 0:
            return 0.99 if color == 'Red' else 0.01
        elif distance <= 2:
            return 0.8 if color == 'Orange' else 0.2
        elif distance <= 4:
            return 0.7 if color == 'Yellow' else 0.3
        else:
            return 0.99 if color == 'Green' else 0.01

    def on_click(self, x, y):
        """Handle click for sensing or busting the ghost location."""
        if self.credit.get() == 0 and self.bust_attempts.get() == 0:
            self.result_label.set("Game Over! No credit or bust attempts left.")
            self.disable_buttons()
            return

        if self.bust_mode.get() and self.bust_attempts.get() > 0:
            self.bust_attempt(x, y)
        elif self.credit.get() > 0:
            color, direction = self.distance_sense(x, y)
            self.update_posterior_probabilities(color, direction, x, y)
            self.credit.set(self.credit.get() - 1)
            self.view_probabilities.set(False)
            self.view_directions.set(False)
            self.grid[x][y].config(bg=color)
            self.update_grid_display()

    def bust_attempt(self, x, y):
        """Handle a bust attempt on a specific cell."""
        if self.bust_attempts.get() > 0:
            # Calculate the distance between the clicked cell and the ghost
            distance = abs(self.ghost_x - x) + abs(self.ghost_y - y)

            if distance == 0:
                # If distance is zero, the player found the ghost
                self.result_label.set("Congratulations! You found the ghost!")
                self.bust_attempts.set(0)  # End the game after a successful bust
            else:
                # If the distance is not zero, the player missed
                self.bust_attempts.set(self.bust_attempts.get() - 1)
                self.result_label.set(
                    "You missed! Try again." if self.bust_attempts.get() > 0
                    else "Game Over! No bust attempts left."
                )

            # Update the grid display after a bust attempt
            self.update_grid_display()

        # Set bust mode to false once a bust attempt is made
        self.bust_mode.set(False)

    def update_grid_display(self):
        """Update the grid display to show probabilities, directions, and sensor readings."""
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                if self.view_probabilities.get():
                    prob_text = f" {self.posterior_probs[(x, y)]:.2f}"
                    self.grid[x][y].config(text=prob_text)
                elif self.view_directions.get():
                    # Use distance_sense to get both the color and direction
                    _, direction = self.distance_sense(x, y)
                    self.grid[x][y].config(text=direction)
                else:
                    self.grid[x][y].config(text="")

        self.credit_label.config(text=f"Score: {self.credit.get()}")
        self.bust_label.config(text=f"Bust Attempts Left: {self.bust_attempts.get()}")

    def toggle_probabilities(self):
        """Toggle viewing probabilities on the grid."""
        self.view_probabilities.set(True)
        self.view_directions.set(False)
        self.update_grid_display()

    def toggle_directions(self):
        """Toggle viewing directions on the grid."""
        self.view_directions.set(True)
        self.view_probabilities.set(False)
        self.update_grid_display()

    def toggle_bust_mode(self):
        """Enable bust mode."""
        self.bust_mode.set(True)
        self.result_label.set("Bust Mode: Select a cell to attempt a bust.")

    def disable_buttons(self):
        """Disable all grid buttons."""
        for row in self.grid:
            for button in row:
                button.config(state="disabled")

    def init_ui(self):
        """Initialize the game board and UI elements."""
        grid_frame = Frame(self.root, bg="black")
        grid_frame.grid(row=0, column=0, padx=20, pady=20)

        for x in range(GRID_SIZE[0]):
            row = []
            for y in range(GRID_SIZE[1]):
                btn = Button(grid_frame, text=" ", width=4, height=2, command=lambda x=x, y=y: self.on_click(x, y),
                             bg="blue", fg="white")
                btn.grid(row=x, column=y, padx=1, pady=1)
                row.append(btn)
            self.grid.append(row)

        control_panel = Frame(self.root, bg="black")
        control_panel.grid(row=0, column=1, padx=20, pady=20, sticky="n")

        self.credit_label = Label(control_panel, text=f"Score: {self.credit.get()}", bg="black", fg="white",
                                  font=("Arial", 14))
        self.credit_label.pack(anchor="w", pady=5)

        self.bust_label = Label(control_panel, text=f"Bust Attempts Left: {self.bust_attempts.get()}", bg="black",
                                fg="white", font=("Arial", 14))
        self.bust_label.pack(anchor="w", pady=5)

        result_display = Label(control_panel, textvariable=self.result_label, bg="black", fg="white",
                               font=("Arial", 12))
        result_display.pack(anchor="w", pady=5)

        view_prob_btn = Button(control_panel, text="View Probabilities", command=self.toggle_probabilities,
                               bg="grey", fg="black", font=("Arial", 12))
        view_prob_btn.pack(anchor="w", pady=10)

        view_dir_btn = Button(control_panel, text="View Direction", command=self.toggle_directions,
                              bg="grey", fg="black", font=("Arial", 12))
        view_dir_btn.pack(anchor="w", pady=10)

        bust_mode_btn = Button(control_panel, text=" Bust Mode", command=self.toggle_bust_mode,
                               bg="red", fg="white", font=("Arial", 12))
        bust_mode_btn.pack(anchor="w", pady=10)

if __name__ == "__main__":
    root = Tk()
    game = GhostBusterGame(root)
    root.mainloop()

import random
from tkinter import Tk, Button, Label, IntVar, BooleanVar, StringVar, Frame

# Define grid size and game settings
GRID_SIZE = (8, 13)
INITIAL_CREDIT = 20
INITIAL_BUSTS = 2


class GhostBusterGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghost Buster Game")

        # Initialize game variables
        self.credit = IntVar(master=self.root, value=INITIAL_CREDIT)
        self.bust_attempts = IntVar(master=self.root, value=INITIAL_BUSTS)
        self.view_probabilities = BooleanVar(master=self.root, value=False)
        self.result_label = StringVar(master=self.root)
        self.posterior_probs = {}
        self.bust_mode = BooleanVar(master=self.root, value=False)

        # Initialize game state
        self.ghost_position = self.place_ghost()
        self.compute_initial_prior_probabilities()

        # Initialize UI elements
        self.grid = []
        self.credit_label = None
        self.bust_label = None
        self.init_ui()

    def place_ghost(self):
        """Place the ghost randomly on the grid."""
        return random.randint(0, GRID_SIZE[0] - 1), random.randint(0, GRID_SIZE[1] - 1)

    def compute_initial_prior_probabilities(self):
        """Compute uniform prior probabilities for each cell."""
        prior_prob = 1 / (GRID_SIZE[0] * GRID_SIZE[1])
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                self.posterior_probs[(x, y)] = prior_prob

    def distance_sense(self, xclk, yclk):
        """Return a color based on the distance from the ghost."""
        ghost_x, ghost_y = self.ghost_position
        distance = abs(xclk - ghost_x) + abs(yclk - ghost_y)

        if distance == 0:
            return 'Red'
        elif distance <= 2:
            return 'Orange'
        elif distance <= 4:
            return 'Yellow'
        else:
            return 'Green'

    def update_posterior_ghost_location_probabilities(self, color, xclk, yclk):
        """Update probabilities for each location based on sensor reading."""
        # Calculate likelihood based on color observed at clicked position
        likelihoods = {}
        for loc in self.posterior_probs:
            distance = abs(loc[0] - xclk) + abs(loc[1] - yclk)
            color_prob = self.conditional_color_probability(color, distance)
            likelihoods[loc] = color_prob

        # Update the posterior probabilities using Bayes' rule:
        # Pt(G = Li) = P(S = Color at Li | G = Li) * Pt-1(G = Li)
        total_prob = 0.0
        for loc in self.posterior_probs:
            prior_prob = self.posterior_probs[loc]
            posterior_prob = likelihoods[loc] * prior_prob
            self.posterior_probs[loc] = posterior_prob
            total_prob += posterior_prob

        # Normalize the probabilities
        if total_prob > 0:
            for loc in self.posterior_probs:
                self.posterior_probs[loc] /= total_prob

    def conditional_color_probability(self, color, distance):
        """Return the probability of a color given the distance."""
        if distance == 0:
            return 1.0 if color == 'Red' else 0.0
        elif distance <= 2:
            return 0.8 if color == 'Orange' else 0.2
        elif distance <= 4:
            return 0.7 if color == 'Yellow' else 0.3
        else:
            return 1.0 if color == 'Green' else 0.0

    def on_click(self, x, y):
        """Handle a player's click on a cell to sense or bust the ghost location."""
        if self.credit.get() == 0 and self.bust_attempts.get() == 0:
            self.result_label.set("Game Over! No credit or bust attempts left.")
            self.disable_buttons()
            return

        if self.bust_mode.get() and self.bust_attempts.get() > 0:
            self.bust_attempt(x, y)
        elif self.credit.get() > 0:
            color = self.distance_sense(x, y)
            self.update_posterior_ghost_location_probabilities(color, x, y)
            self.credit.set(self.credit.get() - 1)
            self.view_probabilities.set(False)
            self.grid[x][y].config(bg=color)
            self.update_grid_display()

            if self.credit.get() == 0 and self.bust_attempts.get() == 0:
                self.result_label.set("Game Over! No credit or bust attempts left.")
                self.disable_buttons()

    def bust_attempt(self, x, y):
        """Handle a bust attempt on a specific cell."""
        if self.bust_attempts.get() > 0:
            if (x, y) == self.ghost_position:
                self.result_label.set("Congratulations! You found the ghost!")
                self.bust_attempts.set(0)
            else:
                self.bust_attempts.set(self.bust_attempts.get() - 1)
                self.result_label.set(
                    "You missed! Try again." if self.bust_attempts.get() > 0 else "Game Over! No bust attempts left.")
            self.update_grid_display()
        self.bust_mode.set(False)

    def update_grid_display(self):
        """Update the grid display to show probabilities and scores."""
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                if self.view_probabilities.get():
                    prob_text = f"{self.posterior_probs[(x, y)]:.2f}"
                    self.grid[x][y].config(text=prob_text)
                else:
                    self.grid[x][y].config(text="")
        self.credit_label.config(text=f"Score: {self.credit.get()}")
        self.bust_label.config(text=f"Bust Attempts Left: {self.bust_attempts.get()}")

    def toggle_probabilities(self):
        """Toggle the view of probabilities on the grid."""
        self.view_probabilities.set(not self.view_probabilities.get())
        self.update_grid_display()

    def toggle_bust_mode(self):
        """Enable bust mode to allow the player to select a cell for busting."""
        self.bust_mode.set(True)
        self.result_label.set("Bust Mode: Select a cell to attempt a bust.")

    def disable_buttons(self):
        """Disable the command of all grid buttons once the game is over."""
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
        result_display.pack(anchor="w", pady=10)

        bust_button = Button(control_panel, text="Bust", command=self.toggle_bust_mode, bg="red", fg="white",
                             font=("Arial", 12, "bold"), width=10, height=2)
        bust_button.pack(pady=10)

        toggle_button = Button(control_panel, text="View Probabilities", command=self.toggle_probabilities, bg="gray",
                               fg="white", font=("Arial", 12, "bold"), width=15, height=2)
        toggle_button.pack(pady=10)

        self.update_grid_display()


# Run the game
if __name__ == "__main__":
    root = Tk()
    game = GhostBusterGame(root)
    root.mainloop()

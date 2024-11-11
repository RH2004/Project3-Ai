import random
from tkinter import Tk, Button, Label, IntVar, BooleanVar, StringVar, Frame

# Define grid size and game settings
GRID_SIZE = (8, 13)
INITIAL_CREDIT = 50
INITIAL_BUSTS = 2

# Initialize root window first
root = Tk()
root.title("Ghost Buster Game")

# Initialize variables with the root window as their master
credit = IntVar(master=root, value=INITIAL_CREDIT)
bust_attempts = IntVar(master=root, value=INITIAL_BUSTS)
view_probabilities = BooleanVar(master=root, value=False)
result_label = StringVar(master=root)
posterior_probs = {}
bust_mode = BooleanVar(master=root, value=False)

# Step 1: Define Functions for Game Initialization and Probability Calculation
def PlaceGhost():
    """Place the ghost randomly on the grid."""
    return random.randint(0, GRID_SIZE[0] - 1), random.randint(0, GRID_SIZE[1] - 1)

def ComputeInitialPriorProbabilities():
    """Compute uniform prior probabilities for each cell."""
    prior_prob = 1 / (GRID_SIZE[0] * GRID_SIZE[1])
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            posterior_probs[(x, y)] = prior_prob

def DistanceSense(xclk, yclk, ghost_x, ghost_y):
    """Return a color based on the distance from the ghost."""
    distance = abs(xclk - ghost_x) + abs(yclk - ghost_y)

    # Define color based on distance
    if distance == 0:
        return 'Red'
    elif distance <= 2:
        return 'Orange'
    elif distance <= 4:
        return 'Yellow'
    else:
        return 'Green'

def UpdatePosteriorGhostLocationProbabilities(color, xclk, yclk):
    """Update probabilities for each location based on sensor reading."""
    for loc, prob in posterior_probs.items():
        distance = abs(loc[0] - xclk) + abs(loc[1] - yclk)
        color_prob = conditional_color_probability(color, distance)
        posterior_probs[loc] = color_prob * prob

    # Normalize probabilities
    total_prob = sum(posterior_probs.values())
    for loc in posterior_probs:
        posterior_probs[loc] /= total_prob

def conditional_color_probability(color, distance):
    """Return the probability of a color given the distance."""
    if distance == 0:
        return 1.0 if color == 'Red' else 0.0
    elif distance <= 2:
        return 0.8 if color == 'Orange' else 0.2
    elif distance <= 4:
        return 0.7 if color == 'Yellow' else 0.3
    else:
        return 1.0 if color == 'Green' else 0.0

# Step 2: Define Button Click Handlers for Sensor Readings and Bust Attempts
def on_click(x, y):
    """Handle a player's click on a cell to sense or bust the ghost location."""
    if credit.get() == 0 and bust_attempts.get() == 0:
        result_label.set("Game Over! No credit or bust attempts left.")
        disable_buttons()  # Disable all buttons if game over
        return  # Do nothing further if game is over

    if bust_mode.get() and bust_attempts.get() > 0:
        # Bust mode
        bust_attempt(x, y)
    elif credit.get() > 0:
        # Sense mode
        color = DistanceSense(x, y, ghost_x, ghost_y)
        UpdatePosteriorGhostLocationProbabilities(color, x, y)
        credit.set(credit.get() - 1)
        view_probabilities.set(False)  # Hide probabilities after clicking on a cell
        grid[x][y].config(bg=color)
        update_grid_display()

        if credit.get() == 0 and bust_attempts.get() == 0:
            result_label.set("Game Over! No credit or bust attempts left.")
            disable_buttons()  # Disable buttons after game over

def bust_attempt(x, y):
    """Handle a bust attempt on a specific cell."""
    if bust_attempts.get() > 0:
        if (x, y) == (ghost_x, ghost_y):
            result_label.set("Congratulations! You found the ghost!")
            bust_attempts.set(0)  # End the game after a successful bust
        else:
            bust_attempts.set(bust_attempts.get() - 1)
            if bust_attempts.get() > 0:
                result_label.set("You missed! Try again.")
            else:
                result_label.set("Game Over! No bust attempts left.")
        update_grid_display()
    else:
        result_label.set("Game Over! No bust attempts left.")
    bust_mode.set(False)  # Exit bust mode after an attempt

# Step 3: Define GUI Initialization and Update Display Logic
def update_grid_display():
    """Update the grid display to show probabilities and scores."""
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            if view_probabilities.get():
                prob_text = f"{posterior_probs[(x, y)]:.2f}"
                grid[x][y].config(text=prob_text)
            else:
                grid[x][y].config(text="")

    credit_label.config(text=f"Credit: {credit.get()}")
    bust_label.config(text=f"Bust Attempts Left: {bust_attempts.get()}")
    if credit.get() == 0 and bust_attempts.get() == 0:
        result_label.set("Game Over! No credit or bust attempts left.")
        disable_buttons()  # Disable buttons if the game is over

def toggle_probabilities():
    """Toggle the view of probabilities on the grid."""
    view_probabilities.set(not view_probabilities.get())
    update_grid_display()

def toggle_bust_mode():
    """Enable bust mode to allow the player to select a cell for busting."""
    bust_mode.set(True)
    result_label.set("Bust Mode: Select a cell to attempt a bust.")

def disable_buttons():
    """Disable the command of all grid buttons once the game is over."""
    for row in grid:
        for button in row:
            button.config(state="disabled")  # Disable the button click

def init_game():
    """Initialize the game board and UI elements."""
    global grid, ghost_x, ghost_y, credit_label, bust_label
    ghost_x, ghost_y = PlaceGhost()
    ComputeInitialPriorProbabilities()

    # Create the game grid within a frame
    grid_frame = Frame(root, bg="black")
    grid_frame.grid(row=0, column=0, padx=20, pady=20)

    # Create grid buttons
    grid = []
    for x in range(GRID_SIZE[0]):
        row = []
        for y in range(GRID_SIZE[1]):
            btn = Button(grid_frame, text=" ", width=4, height=2,
                         command=lambda x=x, y=y: on_click(x, y), bg="blue", fg="white")
            btn.grid(row=x, column=y, padx=1, pady=1)
            row.append(btn)
        grid.append(row)

    # Control panel
    control_panel = Frame(root, bg="black")
    control_panel.grid(row=0, column=1, padx=20, pady=20, sticky="n")

    credit_label = Label(control_panel, text=f"Credit: {credit.get()}", bg="black", fg="white", font=("Arial", 14))
    credit_label.pack(anchor="w", pady=5)

    bust_label = Label(control_panel, text=f"Bust Attempts Left: {bust_attempts.get()}", bg="black", fg="white",
                       font=("Arial", 14))
    bust_label.pack(anchor="w", pady=5)

    result_display = Label(control_panel, textvariable=result_label, bg="black", fg="white", font=("Arial", 12))
    result_display.pack(anchor="w", pady=10)

    bust_button = Button(control_panel, text="Bust", command=toggle_bust_mode,
                         bg="red", fg="white", font=("Arial", 12, "bold"), width=10, height=2)
    bust_button.pack(pady=10)

    toggle_button = Button(control_panel, text="View Probabilities",
                           command=toggle_probabilities,
                           bg="gray", fg="white", font=("Arial", 12, "bold"), width=15, height=2)
    toggle_button.pack(pady=10)

    update_grid_display()

def main():
    """Main function to start the game."""
    init_game()
    root.mainloop()

# Run the game
if __name__ == "__main__":
    main()

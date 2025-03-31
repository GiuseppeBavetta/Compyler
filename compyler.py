import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import subprocess
import threading
import sys
import time
import re
import random
from tkinter.filedialog import askopenfilename, askdirectory
import queue
import webbrowser

class SnakeGame:
    def __init__(self, parent_frame, theme):
        """Initialize the Snake game in the given parent frame"""
        self.parent = parent_frame
        self.theme = theme
        
        # Game state
        self.game_running = False
        self.game_over = False
        self.score = 0
        self.high_score = 0
        
        # Settings
        self.width = 300
        self.height = 300
        self.cell_size = 15
        self.speed = 150  # milliseconds between moves
        
        # Create the game frame
        self.game_frame = tk.Frame(self.parent, bg=self.theme['bg_color'])
        self.game_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a header with game name and score
        self.header_frame = tk.Frame(self.game_frame, bg=self.theme['bg_color'])
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            self.header_frame,
            text="🐍 Snake Game",
            font=("Segoe UI", 14, "bold"),
            fg=self.theme['accent_color'],
            bg=self.theme['bg_color']
        ).pack(side=tk.LEFT)
        
        self.score_label = tk.Label(
            self.header_frame,
            text="Score: 0 | High Score: 0",
            font=("Segoe UI", 10),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color']
        )
        self.score_label.pack(side=tk.RIGHT)
        
        # Create the canvas for the game
        self.canvas_frame = tk.Frame(
            self.game_frame, 
            bg=self.theme['accent_color'],
            padx=2, 
            pady=2
        )
        self.canvas_frame.pack(pady=5)
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.width, 
            height=self.height,
            bg=self.theme['terminal_bg'],
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Start button
        self.button_frame = tk.Frame(self.game_frame, bg=self.theme['bg_color'])
        self.button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            self.button_frame,
            text="Start Game",
            command=self.start_game,
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(
            self.button_frame,
            text="Pause",
            command=self.toggle_pause,
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # Info text
        self.info_label = tk.Label(
            self.game_frame,
            text="Play Snake while Nuitka compiles your Python script!\nUse arrow keys to control the snake.",
            font=("Segoe UI", 9),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color'],
            justify=tk.CENTER
        )
        self.info_label.pack(pady=5)
        
        # Game variables
        self.snake = []
        self.food = None
        self.direction = "Right"
        self.next_direction = "Right"
        self.paused = False
        self.after_id = None
        
        # Initial drawing
        self.draw_border()
        self.draw_message("Press 'Start Game' to play")
        
        # Bind keys
        self.parent.bind("<Left>", lambda e: self.change_direction("Left"))
        self.parent.bind("<Right>", lambda e: self.change_direction("Right"))
        self.parent.bind("<Up>", lambda e: self.change_direction("Up"))
        self.parent.bind("<Down>", lambda e: self.change_direction("Down"))
        self.parent.bind("<space>", lambda e: self.toggle_pause())

    def draw_border(self):
        """Draw a border around the game area"""
        self.canvas.create_rectangle(
            2, 2, self.width-2, self.height-2, 
            outline=self.theme['accent_color'],
            width=2,
            tag="border"
        )
    
    def draw_message(self, message):
        """Draw a message on the canvas"""
        self.canvas.delete("message")
        self.canvas.create_text(
            self.width//2, self.height//2,
            text=message,
            fill=self.theme['text_color'],
            font=("Segoe UI", 12, "bold"),
            tag="message"
        )
    
    def start_game(self):
        """Start a new game"""
        # Reset game state
        self.canvas.delete("all")
        self.draw_border()
        self.game_running = True
        self.game_over = False
        self.score = 0
        self.update_score()
        
        # Reset snake
        self.snake = []
        for i in range(3):
            self.snake.append((self.width//2 - i*self.cell_size, self.height//2))
        
        # Reset direction
        self.direction = "Right"
        self.next_direction = "Right"
        
        # Create first food
        self.create_food()
        
        # Enable pause button
        self.pause_button.config(state=tk.NORMAL, text="Pause")
        
        # Start game loop
        self.paused = False
        self.update()
    
    def toggle_pause(self):
        """Pause or resume the game"""
        if not self.game_running or self.game_over:
            return
            
        self.paused = not self.paused
        
        if self.paused:
            self.pause_button.config(text="Resume")
            self.draw_message("Game Paused")
            if self.after_id:
                self.parent.after_cancel(self.after_id)
                self.after_id = None
        else:
            self.pause_button.config(text="Pause")
            self.canvas.delete("message")
            self.update()
    
    def create_food(self):
        """Create a new food item at a random position"""
        cell_width = self.width // self.cell_size
        cell_height = self.height // self.cell_size
        
        while True:
            # Generate random coordinates
            x = random.randint(1, cell_width - 2) * self.cell_size
            y = random.randint(1, cell_height - 2) * self.cell_size
            
            # Check if it overlaps with snake
            if (x, y) not in self.snake:
                self.food = (x, y)
                self.canvas.create_oval(
                    x, y, x + self.cell_size, y + self.cell_size,
                    fill=self.theme['success_color'],
                    tag="food"
                )
                break
    
    def change_direction(self, new_direction):
        """Change the snake direction ensuring it can't reverse"""
        if not self.game_running or self.game_over or self.paused:
            return
            
        # Prevent reversing
        if new_direction == "Left" and self.direction != "Right":
            self.next_direction = new_direction
        elif new_direction == "Right" and self.direction != "Left":
            self.next_direction = new_direction
        elif new_direction == "Up" and self.direction != "Down":
            self.next_direction = new_direction
        elif new_direction == "Down" and self.direction != "Up":
            self.next_direction = new_direction
    
    def update(self):
        """Update the game state and redraw"""
        if not self.game_running or self.paused:
            return
            
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        
        if self.direction == "Left":
            head_x -= self.cell_size
        elif self.direction == "Right":
            head_x += self.cell_size
        elif self.direction == "Up":
            head_y -= self.cell_size
        elif self.direction == "Down":
            head_y += self.cell_size
        
        new_head = (head_x, head_y)
        
        # Check for collisions
        if (
            new_head in self.snake or
            head_x < 0 or head_x >= self.width or
            head_y < 0 or head_y >= self.height
        ):
            self.game_over = True
            self.game_running = False
            self.draw_message("Game Over! Press 'Start Game' to play again")
            self.pause_button.config(state=tk.DISABLED)
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check if food eaten
        if new_head == self.food:
            # Remove old food
            self.canvas.delete("food")
            
            # Increment score
            self.score += 10
            self.update_score()
            
            # Create new food
            self.create_food()
        else:
            # Remove tail
            self.snake.pop()
        
        # Redraw snake
        self.canvas.delete("snake")
        for i, (x, y) in enumerate(self.snake):
            color = self.theme['accent_color'] if i == 0 else self.theme['text_color']
            self.canvas.create_rectangle(
                x, y, x + self.cell_size, y + self.cell_size,
                fill=color,
                tag="snake"
            )
        
        # Continue the game loop
        self.after_id = self.parent.after(self.speed, self.update)
    
    def update_score(self):
        """Update the score display"""
        if self.score > self.high_score:
            self.high_score = self.score
        self.score_label.config(text=f"Score: {self.score} | High Score: {self.high_score}")
    
    def destroy(self):
        """Clean up resources when the game is closed"""
        if self.after_id:
            self.parent.after_cancel(self.after_id)
        
        # Unbind keys
        self.parent.unbind("<Left>")
        self.parent.unbind("<Right>")
        self.parent.unbind("<Up>")
        self.parent.unbind("<Down>")
        self.parent.unbind("<space>")
        
        # Destroy widgets
        self.game_frame.destroy()
    
    def show_game_over_animation(self, callback=None):
        """Show a game over animation and then call the callback"""
        self.game_running = False
        self.paused = True
        
        if self.after_id:
            self.parent.after_cancel(self.after_id)
        
        # Animate snake disappearing
        def animate_disappear(iteration=0):
            if iteration >= len(self.snake):
                # Animation complete, call callback
                if callback:
                    self.parent.after(500, callback)
                return
                
            # Remove one segment at a time
            if self.snake:
                x, y = self.snake[0]
                self.canvas.create_rectangle(
                    x, y, x + self.cell_size, y + self.cell_size,
                    fill=self.theme['success_color'],
                    outline=self.theme['success_color'],
                    tag="animation"
                )
                self.snake.pop(0)
                self.canvas.delete("snake")
                
                for x, y in self.snake:
                    self.canvas.create_rectangle(
                        x, y, x + self.cell_size, y + self.cell_size,
                        fill=self.theme['text_color'],
                        tag="snake"
                    )
                
                self.parent.after(50, lambda: animate_disappear(iteration + 1))
        
        # Start animation
        self.draw_message("Compilation Complete!")
        self.parent.after(1000, animate_disappear)


class NuitkaCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nuitka Compiler GUI v3")
        self.root.geometry("1200x800")
        
        # Set theme colors
        self.theme = {
            'bg_color': "#2c3e50",          # Dark blue-gray
            'accent_color': "#3498db",       # Blue
            'success_color': "#2ecc71",      # Green
            'error_color': "#e74c3c",        # Red
            'text_color': "#ecf0f1",         # Light gray
            'text_tabcolor': "#000000",      # Black
            'secondary_bg': "#34495e",       # Slightly lighter blue-gray
            'terminal_bg': "#1a1a1a",        # Very dark gray for terminal
            'terminal_text': "#00ff00",      # Green for terminal text
            'input_prompt_color': "#FFA500", # Orange for input prompts
            'command_color': "#FFFF00"       # Yellow for commands
        }
        
        # Apply theme to root
        self.root.configure(bg=self.theme['bg_color'])
        
        # Create a custom style for ttk widgets
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.theme['bg_color'])
        self.style.configure("TButton", 
                             background=self.theme['accent_color'], 
                             foreground=self.theme['text_color'],
                             font=("Segoe UI", 10, "bold"))
        self.style.configure("TProgressbar", 
                             troughcolor=self.theme['secondary_bg'],
                             background=self.theme['accent_color'])
        
        # File paths
        self.file_path = ""
        self.output_dir = os.path.expanduser("~")
        self.icon_path = ""
        
        # Output queue and state tracking
        self.output_queue = queue.Queue()
        self.compilation_start_time = None
        self.compilation_progress = 0
        self.eta_text = "Calculating..."
        self.process = None
        self.smooth_progress_timer = None
        self.target_progress = 0
        
        # Progress tracking
        self.progress_model = {
            "dependency_scan": {"weight": 10, "complete": False},
            "c_generation": {"weight": 15, "complete": False},
            "c_compilation": {"weight": 50, "complete": False},
            "linking": {"weight": 15, "complete": False},
            "packaging": {"weight": 10, "complete": False}
        }
        self.current_phase = "waiting"
        self.output_log = []
        
        # Regex patterns for progress tracking
        self.percentage_patterns = [
            re.compile(r"(\d+)% completed"),
            re.compile(r"Progress: (\d+)%"),
            re.compile(r"Overall completion: (\d+)%"),
            re.compile(r"Nuitka:INFO: (\d+)% done")
        ]
        
        # Command history for terminal
        self.command_history = []
        self.history_index = 0
        
        # Success notification panel (initially hidden)
        self.success_panel_visible = False
        
        # Create the main layout
        self.create_layout()
        
        # Schedule the output checker
        self.check_output()
        
        # Progress update timer
        self.last_progress_update = 0
        self.progress_update_interval = 1  # seconds
        self.update_progress_periodically()
        
        # Focus input field after startup
        self.root.after(100, lambda: self.terminal_input.focus_set() 
                        if hasattr(self, 'terminal_input') else None)

    def create_layout(self):
        """Create the main application layout"""
        # Create main panels
        self.main_panel = tk.Frame(self.root, bg=self.theme['bg_color'])
        self.main_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.terminal_panel = tk.Frame(self.root, bg=self.theme['bg_color'])
        self.terminal_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)
        
        # Configure main panel rows
        self.main_panel.grid_rowconfigure(0, weight=0)  # Header
        self.main_panel.grid_rowconfigure(1, weight=0)  # File info
        self.main_panel.grid_rowconfigure(2, weight=0)  # Options 
        self.main_panel.grid_rowconfigure(3, weight=0)  # Success notification (initially hidden)
        self.main_panel.grid_rowconfigure(4, weight=1)  # Empty space/Snake game
        self.main_panel.grid_columnconfigure(0, weight=1)
        
        # Create widgets
        self.create_header()
        self.create_file_section()
        self.create_options_panel()
        self.create_success_panel()  # Create but don't show yet
        self.create_terminal()
        
        # Add button effects
        self.add_button_effects()

    def create_header(self):
        """Create the header section"""
        header_frame = tk.Frame(self.main_panel, bg=self.theme['bg_color'])
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        title_label = tk.Label(
            header_frame,
            text="Nuitka Compiler",
            font=("Segoe UI", 20, "bold"),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color']
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Python to Executable Converter",
            font=("Segoe UI", 10),
            fg=self.theme['accent_color'],
            bg=self.theme['bg_color']
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

    def create_file_section(self):
        """Create the file selection section"""
        file_section = tk.Frame(self.main_panel, bg=self.theme['bg_color'], padx=10, pady=10)
        file_section.grid(row=1, column=0, sticky="ew")
        
        # File selection area
        file_frame = tk.Frame(file_section, bg=self.theme['bg_color'])
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            file_frame, 
            text="Python Script:",
            font=("Segoe UI", 11, "bold"),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_info_text = tk.Label(
            file_frame, 
            text="No file selected",
            anchor="w",
            bg=self.theme['secondary_bg'],
            fg=self.theme['text_color'],
            relief=tk.GROOVE,
            padx=10,
            pady=5
        )
        self.file_info_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.browse_btn = tk.Button(
            file_frame,
            text="Browse...",
            command=self.browse_file,
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 10),
            relief=tk.GROOVE,
            padx=15,
            pady=5,
            borderwidth=0,
            cursor="hand2"
        )
        self.browse_btn.pack(side=tk.RIGHT)
        
        # Output directory selection area
        output_frame = tk.Frame(file_section, bg=self.theme['bg_color'])
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            output_frame, 
            text="Output Directory:",
            font=("Segoe UI", 11, "bold"),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_dir_text = tk.Label(
            output_frame, 
            text=self.output_dir,
            anchor="w",
            bg=self.theme['secondary_bg'],
            fg=self.theme['text_color'],
            relief=tk.GROOVE,
            padx=10,
            pady=5
        )
        self.output_dir_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.output_browse_btn = tk.Button(
            output_frame,
            text="Select...",
            command=self.browse_output_dir,
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 10),
            relief=tk.GROOVE,
            padx=15,
            pady=5,
            borderwidth=0,
            cursor="hand2"
        )
        self.output_browse_btn.pack(side=tk.RIGHT)
        
        # Spacer a sinistra per spingere il pulsante a destra
        compile_frame = tk.Frame(file_section, bg=self.theme['bg_color'])
        compile_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Spacer a sinistra per spingere il pulsante a destra
        spacer = tk.Frame(compile_frame, bg=self.theme['bg_color'])
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status label
        self.status_label = tk.Label(
            compile_frame,
            text="Ready",
            font=("Segoe UI", 9),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color'],
            anchor="w"
        )
        self.status_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Compile button
        self.compile_btn = tk.Button(
            compile_frame, 
            text="Compile with Nuitka", 
            command=self.compile_script,
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 11, "bold"),
            relief=tk.GROOVE,
            padx=20,
            pady=8,
            borderwidth=0,
            cursor="hand2"
        )
        self.compile_btn.pack(side=tk.RIGHT)

    def create_options_panel(self):
        """Create compilation options panel"""
        # Create main options frame
        self.options_frame = tk.LabelFrame(
            self.main_panel, 
            text="Compilation Options", 
            bg=self.theme['bg_color'], 
            fg=self.theme['accent_color'],
            font=("Segoe UI", 12, "bold"), 
            padx=12, 
            pady=12,
            relief=tk.GROOVE,
            bd=2,
        )
        self.options_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Dictionary to store checkbox variables
        self.options_vars = {}
        
        # Create a notebook for categories
        self.options_notebook = ttk.Notebook(self.options_frame)
        self.options_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure notebook style
        self.style.configure("TNotebook", background=self.theme['bg_color'], borderwidth=0)
        self.style.configure("TNotebook.Tab", 
                            background=self.theme['secondary_bg'], 
                            foreground=self.theme['text_tabcolor'], 
                            padding=[15, 5],
                            font=("Segoe UI", 9, "bold"))
        
        self.style.map("TNotebook.Tab", 
                    background=[("selected", self.theme['accent_color'])],
                    foreground=[("selected", self.theme['text_tabcolor'])])
        
        # Create tabs
        self.create_mode_tab()
        self.create_optimization_tab()
        self.create_gui_tab()
        self.create_advanced_tab()

    def create_success_panel(self):
        """Create the success notification panel (initially hidden)"""
        # Crea un pannello di successo che sarà visualizzato all'interno dell'applicazione
        self.success_frame = tk.Frame(
            self.main_panel,
            bg=self.theme['bg_color'],
            relief=tk.RIDGE,
            bd=2,
            highlightbackground=self.theme['success_color'],
            highlightthickness=2
        )
        
        # Success icon and message
        success_header = tk.Frame(self.success_frame, bg=self.theme['bg_color'])
        success_header.pack(fill=tk.X, padx=10, pady=5)
        
        # Checkmark symbol
        tk.Label(
            success_header,
            text="✓",
            font=("Segoe UI", 20),
            fg=self.theme['success_color'],
            bg=self.theme['bg_color']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Success message
        tk.Label(
            success_header,
            text="Compilation Successful!",
            font=("Segoe UI", 12, "bold"),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color']
        ).pack(side=tk.LEFT)
        
        # Close button (X)
        close_btn = tk.Button(
            success_header,
            text="×",
            font=("Segoe UI", 14, "bold"),
            bg=self.theme['bg_color'],
            fg=self.theme['text_color'],
            relief=tk.FLAT,
            borderwidth=0,
            padx=5,
            pady=0,
            command=self.hide_success_panel
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Details frame
        details_frame = tk.Frame(self.success_frame, bg=self.theme['bg_color'])
        details_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # This will be updated when showing the success panel
        self.executable_label = tk.Label(
            details_frame,
            text="",
            font=("Segoe UI", 10),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color'],
            anchor="w"
        )
        self.executable_label.pack(fill=tk.X, pady=2)
        
        self.location_label = tk.Label(
            details_frame,
            text="",
            font=("Segoe UI", 9),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color'],
            anchor="w"
        )
        self.location_label.pack(fill=tk.X, pady=2)
        
        # Button frame
        btn_frame = tk.Frame(self.success_frame, bg=self.theme['bg_color'])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Open folder button
        open_btn = tk.Button(
            btn_frame,
            text="Open Folder",
            command=self.open_output_folder,
            bg=self.theme['secondary_bg'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        open_btn.pack(side=tk.RIGHT)
        
        # OK button
        ok_btn = tk.Button(
            btn_frame,
            text="OK",
            command=self.hide_success_panel,
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add hover effects
        self.add_hover_effect(ok_btn, self.theme['accent_color'], self.theme['success_color'])
        self.add_hover_effect(open_btn, self.theme['secondary_bg'], self.theme['accent_color'])

    def show_success_panel(self, executable_name):
        """Show the success notification panel with executable details"""
        # Update text
        self.executable_label.config(text=f"Executable created: {executable_name}")
        self.location_label.config(text=f"Location: {self.output_dir}")
        
        # Show the panel if not already visible
        if not self.success_panel_visible:
            self.success_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
            self.success_panel_visible = True

    def hide_success_panel(self):
        """Hide the success notification panel"""
        if self.success_panel_visible:
            self.success_frame.grid_forget()
            self.success_panel_visible = False

    def create_mode_tab(self):
        """Create mode options tab"""
        mode_frame = tk.Frame(self.options_notebook, bg=self.theme['bg_color'], padx=10, pady=10)
        self.options_notebook.add(mode_frame, text="Mode")
        
        mode_options = [
            {"name": "standalone", "text": "Standalone", "tooltip": "Create standalone package with all dependencies", "default": True},
            {"name": "onefile", "text": "Onefile", "tooltip": "Combine everything into a single executable file"},
            {"name": "module", "text": "Module", "tooltip": "Compile as Python extension module"},
            {"name": "follow_imports", "text": "Follow Imports", "tooltip": "Automatically follow all imports", "default": True},
            {"name": "no_follow_imports", "text": "No Follow Imports", "tooltip": "Don't automatically follow imports"}
        ]
        
        self.add_checkboxes(mode_frame, "mode", mode_options)

    def create_optimization_tab(self):
        """Create optimization options tab"""
        opt_frame = tk.Frame(self.options_notebook, bg=self.theme['bg_color'], padx=10, pady=10)
        self.options_notebook.add(opt_frame, text="Optimization")
        
        opt_options = [
            {"name": "lto", "text": "Link Time Optimization (LTO)", "tooltip": "Enable link-time optimization"},
            {"name": "jobs", "text": "Parallel Jobs", "tooltip": "Use multiple processors for compilation", "default": True}
        ]
        
        self.add_checkboxes(opt_frame, "opt", opt_options)
        
        # Add jobs count spinner
        jobs_frame = tk.Frame(opt_frame, bg=self.theme['bg_color'])
        jobs_frame.pack(fill=tk.X, pady=5, padx=25)
        
        jobs_label = tk.Label(
            jobs_frame, 
            text="Number of parallel jobs:", 
            bg=self.theme['bg_color'], 
            fg=self.theme['text_color'],
            font=("Segoe UI", 9)
        )
        jobs_label.pack(side=tk.LEFT, padx=(5, 5))
        
        self.jobs_var = tk.StringVar(value=str(max(1, os.cpu_count() or 4)))
        
        jobs_spinbox = tk.Spinbox(
            jobs_frame, 
            from_=1, 
            to=32, 
            width=3,
            textvariable=self.jobs_var,
            bg=self.theme['secondary_bg'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 9)
        )
        jobs_spinbox.pack(side=tk.LEFT, padx=(5, 0))

    def create_gui_tab(self):
        """Create GUI options tab"""
        gui_frame = tk.Frame(self.options_notebook, bg=self.theme['bg_color'], padx=10, pady=10)
        self.options_notebook.add(gui_frame, text="GUI")
        
        gui_options = [
            {"name": "disable_console", "text": "Disable Console", "tooltip": "Disable console (ideal for GUI apps)"},
            {"name": "enable_tk", "text": "Tkinter Support", "tooltip": "Enable support for tkinter", "default": True},
            {"name": "windows_icon", "text": "Custom Icon", "tooltip": "Use a custom icon"}
        ]
        
        self.add_checkboxes(gui_frame, "gui", gui_options)
        
        # Add icon selection
        icon_frame = tk.Frame(gui_frame, bg=self.theme['bg_color'])
        icon_frame.pack(fill=tk.X, pady=5, padx=25)
        
        self.icon_label = tk.Label(
            icon_frame,
            text="No icon selected", 
            bg=self.theme['bg_color'], 
            fg=self.theme['text_color'],
            font=("Segoe UI", 9),
            anchor="w"
        )
        self.icon_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.select_icon_btn = tk.Button(
            icon_frame,
            text="Select Icon...",
            command=self.browse_icon,
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=2,
            cursor="hand2"
        )
        self.select_icon_btn.pack(side=tk.RIGHT)

    def create_advanced_tab(self):
        """Create advanced options tab"""
        adv_frame = tk.Frame(self.options_notebook, bg=self.theme['bg_color'], padx=10, pady=10)
        self.options_notebook.add(adv_frame, text="Advanced")
        
        # Create a text entry for custom options
        custom_label = tk.Label(
            adv_frame, 
            text="Custom Nuitka options:", 
            bg=self.theme['bg_color'], 
            fg=self.theme['text_color'],
            font=("Segoe UI", 10)
        )
        custom_label.pack(anchor="w", pady=(5, 2))
        
        self.custom_options = tk.Text(
            adv_frame, 
            height=4, 
            width=40, 
            bg=self.theme['secondary_bg'], 
            fg=self.theme['text_color'],
            insertbackground=self.theme['text_color'],
            font=("Consolas", 10),
            padx=5,
            pady=5
        )
        self.custom_options.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Help button
        help_button = tk.Button(
            adv_frame, 
            text="Nuitka Documentation", 
            command=lambda: webbrowser.open("https://nuitka.net/doc/user-manual.html"),
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        help_button.pack(side=tk.RIGHT, pady=5)

    def create_terminal(self):
        """Create the terminal display panel"""
        # Terminal header
        terminal_header = tk.Frame(self.terminal_panel, bg=self.theme['bg_color'])
        terminal_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            terminal_header,
            text="Terminal Output",
            font=("Segoe UI", 12, "bold"),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color']
        ).pack(side=tk.LEFT)
        
        # ETA display
        self.eta_label = tk.Label(
            terminal_header,
            text="ETA: --:--",
            font=("Segoe UI", 10),
            fg=self.theme['accent_color'],
            bg=self.theme['bg_color']
        )
        self.eta_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Progress display
        self.progress_label = tk.Label(
            terminal_header,
            text="Progress: 0%",
            font=("Segoe UI", 10),
            fg=self.theme['accent_color'],
            bg=self.theme['bg_color']
        )
        self.progress_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Clear button
        self.clear_btn = tk.Button(
            terminal_header,
            text="Clear",
            command=self.clear_terminal,
            bg=self.theme['secondary_bg'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 8),
            relief=tk.GROOVE,
            padx=10,
            pady=2,
            borderwidth=0,
            cursor="hand2"
        )
        self.clear_btn.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.terminal_panel,
            orient="horizontal",
            length=600,
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Current stage label
        self.stage_label = tk.Label(
            self.terminal_panel,
            text="Stage: Waiting",
            font=("Segoe UI", 9),
            fg=self.theme['accent_color'],
            bg=self.theme['bg_color'],
            anchor="w"
        )
        self.stage_label.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Terminal text area
        terminal_frame = tk.Frame(
            self.terminal_panel,
            bg=self.theme['terminal_bg'],
            highlightbackground=self.theme['accent_color'],
            highlightthickness=1
        )
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        self.terminal = scrolledtext.ScrolledText(
            terminal_frame,
            bg=self.theme['terminal_bg'],
            fg=self.theme['terminal_text'],
            insertbackground=self.theme['terminal_text'],
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=5,
            pady=5
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.terminal.tag_configure("command", foreground=self.theme['command_color'])
        self.terminal.tag_configure("error", foreground=self.theme['error_color'])
        self.terminal.tag_configure("success", foreground=self.theme['success_color'])
        
        self.terminal.insert(tk.END, "=== Nuitka Compiler Terminal ===\n")
        self.terminal.insert(tk.END, "Ready to compile Python scripts.\n\n")
        self.terminal.config(state=tk.DISABLED)
        
        # Add a command prompt at the bottom
        self.terminal_input_frame = tk.Frame(self.terminal_panel, bg=self.theme['bg_color'])
        self.terminal_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Prompt label
        prompt_label = tk.Label(
            self.terminal_input_frame,
            text="Command:",
            font=("Consolas", 9, "bold"),
            fg=self.theme['text_color'],
            bg=self.theme['bg_color']
        )
        prompt_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Input field
        self.terminal_input = tk.Entry(
            self.terminal_input_frame,
            bg=self.theme['terminal_bg'],
            fg=self.theme['terminal_text'],
            insertbackground=self.theme['terminal_text'],
            font=("Consolas", 9),
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.terminal_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Aggiungi il supporto alla cronologia dei comandi
        self.terminal_input.bind("<Return>", self.process_command)
        self.terminal_input.bind("<Up>", self.history_up)
        self.terminal_input.bind("<Down>", self.history_down)
        
        # Send button
        self.send_btn = tk.Button(
            self.terminal_input_frame,
            text="Send",
            command=lambda: self.process_command(None),
            bg=self.theme['accent_color'],
            fg=self.theme['text_color'],
            font=("Segoe UI", 8),
            relief=tk.GROOVE,
            padx=10,
            pady=1,
            borderwidth=0,
            cursor="hand2"
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Terminal mode indicator
        self.terminal_mode_indicator = tk.Label(
            self.terminal_input_frame,
            text="[CMD]",
            font=("Consolas", 8),
            fg=self.theme['command_color'],
            bg=self.theme['bg_color']
        )
        self.terminal_mode_indicator.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Interactive mode flag
        self.interactive_mode = False

    # Funzioni per gestire la cronologia dei comandi
    def history_up(self, event=None):
        """Navigate up through command history"""
        if not self.command_history:
            return "break"
            
        if self.history_index > 0:
            self.history_index -= 1
            self.terminal_input.delete(0, tk.END)
            self.terminal_input.insert(0, self.command_history[self.history_index])
        
        return "break"  # Prevent default behavior
        
    def history_down(self, event=None):
        """Navigate down through command history"""
        if not self.command_history:
            return "break"
            
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.terminal_input.delete(0, tk.END)
            self.terminal_input.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            # At the end of history, show empty prompt
            self.history_index = len(self.command_history)
            self.terminal_input.delete(0, tk.END)
            
        return "break"  # Prevent default behavior

    def add_button_effects(self):
        """Add hover effects to buttons"""
        buttons = [
            (self.browse_btn, self.theme['accent_color'], self.theme['success_color']),
            (self.output_browse_btn, self.theme['accent_color'], self.theme['success_color']),
            (self.compile_btn, self.theme['accent_color'], self.theme['success_color']),
            (self.clear_btn, self.theme['secondary_bg'], self.theme['accent_color']),
            (self.send_btn, self.theme['accent_color'], self.theme['success_color'])
        ]
        
        if hasattr(self, 'select_icon_btn'):
            buttons.append((self.select_icon_btn, self.theme['accent_color'], self.theme['success_color']))
        
        for btn, default_bg, hover_bg in buttons:
            self.add_hover_effect(btn, default_bg, hover_bg)

    def add_hover_effect(self, button, default_bg, hover_bg):
        """Add hover effect to a button"""
        def on_enter(e):
            button['background'] = hover_bg
        
        def on_leave(e):
            button['background'] = default_bg
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def add_checkboxes(self, parent_frame, prefix, options_list):
        """Add checkboxes to a frame"""
        for option in options_list:
            var = tk.BooleanVar(value=option.get("default", False))
            self.options_vars[f"{prefix}_{option['name']}"] = var
            
            cb_frame = tk.Frame(parent_frame, bg=self.theme['bg_color'])
            cb_frame.pack(fill=tk.X, pady=2)
            
            checkbox = tk.Checkbutton(
                cb_frame, 
                text=option["text"],
                variable=var,
                bg=self.theme['bg_color'],
                fg=self.theme['text_color'],
                selectcolor=self.theme['secondary_bg'],
                activebackground=self.theme['bg_color'],
                activeforeground=self.theme['text_color'],
                highlightthickness=0
            )
            checkbox.pack(side=tk.LEFT)
            
            if "tooltip" in option:
                info_label = tk.Label(cb_frame, text="ℹ️", bg=self.theme['bg_color'], fg=self.theme['accent_color'])
                info_label.pack(side=tk.LEFT, padx=2)
                self.create_tooltip(info_label, option["tooltip"])

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create a toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(self.tooltip, text=text, justify=tk.LEFT,
                            background=self.theme['secondary_bg'], fg=self.theme['text_color'],
                            relief=tk.SOLID, borderwidth=1, padx=5, pady=2)
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def browse_file(self):
        """Open file browser to select a Python script"""
        try:
            file_path = askopenfilename(
                title="Select Python File",
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
                parent=self.root
            )
            
            if not file_path:
                self.append_to_terminal("File selection cancelled.\n")
                return
            
            if not file_path.lower().endswith('.py'):
                error_msg = f"Selected file '{os.path.basename(file_path)}' is not a Python file (.py extension required)"
                messagebox.showerror("Invalid File Type", error_msg)
                self.append_to_terminal(f"Error: {error_msg}\n")
                return
                
            if not os.path.exists(file_path):
                error_msg = f"The file '{file_path}' does not exist"
                messagebox.showerror("File Not Found", error_msg)
                self.append_to_terminal(f"Error: {error_msg}\n")
                return
            
            self.file_path = file_path
            self.file_info_text.config(text=file_path)
            self.status_label.config(text=f"Python script selected: {os.path.basename(file_path)}")
            self.append_to_terminal(f"File selected: {file_path}\n")
            
        except Exception as e:
            self.append_to_terminal(f"Error during file selection: {str(e)}\n")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def browse_output_dir(self):
        """Open directory browser to select output directory"""
        try:
            directory = askdirectory(
                title="Select Output Directory",
                initialdir=self.output_dir,
                parent=self.root
            )
            
            if not directory:
                self.append_to_terminal("Output directory selection cancelled.\n")
                return
                
            self.output_dir = directory
            self.output_dir_text.config(text=directory)
            self.append_to_terminal(f"Output directory selected: {directory}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting output directory: {str(e)}")
            self.append_to_terminal(f"Error selecting output directory: {str(e)}\n")

    def browse_icon(self):
        """Browse for an icon file for the executable"""
        icon_path = askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon Files", "*.ico"), ("All Files", "*.*")],
            parent=self.root
        )
        
        if icon_path:
            self.icon_path = icon_path
            self.icon_label.config(text=os.path.basename(icon_path))
            self.append_to_terminal(f"Icon selected: {icon_path}\n")

    def get_compilation_options(self):
        """Get selected Nuitka options as command line arguments"""
        options = []
        
        # Mode options
        if self.options_vars.get("mode_standalone", tk.BooleanVar(value=False)).get():
            options.append("--standalone")
        
        if self.options_vars.get("mode_onefile", tk.BooleanVar(value=False)).get():
            options.append("--onefile")
        
        if self.options_vars.get("mode_module", tk.BooleanVar(value=False)).get():
            options.append("--module")
        
        if self.options_vars.get("mode_follow_imports", tk.BooleanVar(value=False)).get():
            options.append("--follow-imports")
        
        if self.options_vars.get("mode_no_follow_imports", tk.BooleanVar(value=False)).get():
            options.append("--no-follow-imports")
        
        # Optimization options
        if self.options_vars.get("opt_lto", tk.BooleanVar(value=False)).get():
            options.append("--lto")
        
        if self.options_vars.get("opt_jobs", tk.BooleanVar(value=False)).get():
            try:
                jobs = int(self.jobs_var.get())
                options.append(f"--jobs={jobs}")
            except ValueError:
                pass
        
        # GUI options
        if self.options_vars.get("gui_disable_console", tk.BooleanVar(value=False)).get():
            options.append("--windows-disable-console")
        
        if self.options_vars.get("gui_enable_tk", tk.BooleanVar(value=False)).get():
            options.append("--enable-plugin=tk-inter")
        
        if self.options_vars.get("gui_windows_icon", tk.BooleanVar(value=False)).get() and self.icon_path:
            options.append(f"--windows-icon={self.icon_path}")
        
        # Custom options
        if hasattr(self, 'custom_options'):
            custom_text = self.custom_options.get(1.0, tk.END).strip()
            if custom_text:
                options.extend(custom_text.split())
        
        # Always add output directory
        options.append(f"--output-dir={self.output_dir}")
        
        return options

    def clear_terminal(self):
        """Clear the terminal output"""
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete(1.0, tk.END)
        self.terminal.insert(tk.END, "=== Nuitka Compiler Terminal ===\n")
        self.terminal.insert(tk.END, "Terminal cleared.\n\n")
        self.terminal.config(state=tk.DISABLED)
        
        if hasattr(self, 'terminal_input'):
            self.terminal_input.focus_set()

    def append_to_terminal(self, text):
        """Append text to the terminal"""
        self.terminal.config(state=tk.NORMAL)
        
        # Apply color formatting based on text type
        if text.startswith("$"):
            self.terminal.insert(tk.END, text, "command")
        elif "Error" in text or "ERROR" in text or "error:" in text:
            self.terminal.insert(tk.END, text, "error")
        elif "Success" in text or "Completed" in text or "✓" in text:
            self.terminal.insert(tk.END, text, "success")
        else:
            self.terminal.insert(tk.END, text)
            
        self.terminal.see(tk.END)  # Scroll to the end
        self.terminal.config(state=tk.DISABLED)
        
        # Store output for analysis
        self.output_log.append(text)

    def check_output(self):
        """Check for output in the queue and update the terminal"""
        try:
            while True:
                line = self.output_queue.get_nowait()
                self.append_to_terminal(line)
                
                # Parse the line for progress information
                self.parse_progress_info(line)
                
                self.output_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Schedule to check again
            self.root.after(100, self.check_output)

    def update_progress_periodically(self):
        """Update progress even when no new output is available"""
        if self.compilation_start_time is not None:
            current_time = time.time()
            
            # Only update at specified interval
            if current_time - self.last_progress_update >= self.progress_update_interval:
                self.last_progress_update = current_time
                self.ensure_minimum_progress()
                
        # Schedule next update
        self.root.after(1000, self.update_progress_periodically)

    def parse_progress_info(self, line):
        """Parse the output line for progress information"""
        line = line.strip()
        
        # Direct percentage detection
        for pattern in self.percentage_patterns:
            match = pattern.search(line)
            if match:
                try:
                    reported_percentage = int(match.group(1))
                    if 0 <= reported_percentage <= 100:
                        self.update_progress_display(reported_percentage)
                        return
                except (ValueError, IndexError):
                    pass
        
        # Phase detection
        if "Recursing" in line or "Finding modules" in line:
            self.current_phase = "dependency_scan"
            self.stage_label.config(text="Stage: Analyzing Dependencies")
        elif "Creating module" in line or "Creating code" in line:
            self.current_phase = "c_generation"
            self.stage_label.config(text="Stage: Generating C Code")
        elif "C Compile" in line or "Compiling" in line:
            self.current_phase = "c_compilation"
            self.stage_label.config(text="Stage: Compiling C Code")
        elif "Linking" in line or "Creating executable" in line:
            self.current_phase = "linking"
            self.stage_label.config(text="Stage: Linking")
        elif "Packaging" in line or "copying" in line:
            self.current_phase = "packaging"
            self.stage_label.config(text="Stage: Packaging")

    def update_progress_display(self, progress_percentage):
        """Update all progress indicators with the current percentage"""
        # Ensure progress is an integer within bounds
        progress_int = max(0, min(99, int(progress_percentage)))
        
        # Only update if progress has increased
        if progress_int > self.compilation_progress:
            old_progress = self.compilation_progress
            self.compilation_progress = progress_int
            
            # Update visual indicators
            self.progress_label.config(text=f"Progress: {progress_int}%")
            self.progress_bar['value'] = progress_int
            
            # Calculate and update ETA
            if progress_int > 0 and (progress_int % 5 == 0 or progress_int - old_progress >= 5):
                elapsed_time = time.time() - self.compilation_start_time
                
                if progress_int > 0:
                    estimated_total_time = elapsed_time * (100 / progress_int)
                    remaining_time = estimated_total_time - elapsed_time
                    self.update_eta(remaining_time)

    def update_eta(self, remaining_time):
        """Update the ETA display based on remaining time in seconds"""
        if remaining_time < 60:
            self.eta_text = f"{int(remaining_time)}s"
        elif remaining_time < 3600:
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            self.eta_text = f"{minutes}m {seconds}s"
        else:
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            self.eta_text = f"{hours}h {minutes}m"
        
        self.eta_label.config(text=f"ETA: {self.eta_text}")

    def ensure_minimum_progress(self):
        """Ensure progress advances at least a minimum amount based on time and phase"""
        if self.compilation_start_time is None:
            return
            
        elapsed_time = time.time() - self.compilation_start_time
        
        # Set minimum progress based on elapsed time
        time_factor = min(1.0, elapsed_time / 300.0)  # 5 minutes as reference
        min_progress_by_time = min(60, int(time_factor * 60))
        
        # Apply phase-specific minimum progress
        if self.current_phase == "dependency_scan":
            phase_min = 5
        elif self.current_phase == "c_generation":
            phase_min = 15
        elif self.current_phase == "c_compilation":
            phase_min = 30
        elif self.current_phase == "linking":
            phase_min = 70
        elif self.current_phase == "packaging":
            phase_min = 85
        else:
            phase_min = 0
        
        # Use time-based or phase-based minimum, whichever is higher
        self.update_target_progress(max(min_progress_by_time, phase_min))

    def update_target_progress(self, progress):
        """Set a target progress percentage to smoothly animate towards"""
        if progress > self.target_progress:
            self.target_progress = progress
            
            # Ensure the smooth timer is running
            if not self.smooth_progress_timer:
                self.start_smooth_progress()

    def start_smooth_progress(self):
        """Start a timer to smoothly update the progress bar"""
        if self.smooth_progress_timer:
            self.root.after_cancel(self.smooth_progress_timer)
            
        def update_smooth():
            if self.compilation_start_time is None:
                return
                
            # Don't go backwards or exceed target
            new_progress = min(
                self.target_progress, 
                max(self.compilation_progress + 0.2, self.compilation_progress)
            )
                               
            if new_progress > self.compilation_progress:
                self.compilation_progress = new_progress
                progress_int = int(self.compilation_progress)
                self.progress_label.config(text=f"Progress: {progress_int}%")
                self.progress_bar['value'] = progress_int
                
                # Update ETA if progress has changed meaningfully
                if progress_int > 0 and progress_int % 5 == 0:
                    elapsed_time = time.time() - self.compilation_start_time
                    remaining_time = (elapsed_time / self.compilation_progress) * (100 - self.compilation_progress)
                    self.update_eta(remaining_time)
            
            # Continue the timer if compilation is still running
            if self.compilation_start_time is not None:
                self.smooth_progress_timer = self.root.after(50, update_smooth)
        
        # Start the first update
        self.smooth_progress_timer = self.root.after(50, update_smooth)

    def process_command(self, event=None):
        """Process a command entered in the terminal input"""
        if not hasattr(self, 'terminal_input'):
            return
            
        command = self.terminal_input.get().strip()
        self.terminal_input.delete(0, tk.END)
        
        if not command:
            return
            
        # Aggiungi il comando alla cronologia
        if command not in self.command_history:
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            
        if self.interactive_mode and self.process and self.process.poll() is None:
            # Interactive mode
            try:
                self.append_to_terminal(f"> {command}\n")
                self.process.stdin.write(f"{command}\n")
                self.process.stdin.flush()
            except Exception as e:
                self.append_to_terminal(f"Error sending command: {str(e)}\n")
                self.interactive_mode = False
                self.terminal_mode_indicator.config(text="[CMD]", fg=self.theme['command_color'])
        else:
            # Command mode
            self.append_to_terminal(f"$ {command}\n")
            
            if command.lower() == "clear":
                self.clear_terminal()
            elif command.lower() == "help":
                self.show_help()
            elif command.lower() == "status":
                self.show_status()
            elif command.lower() == "version":
                self.check_nuitka_version()
            else:
                # Run as a system command
                self.run_command(command)
                
        # Always re-focus the input field
        self.terminal_input.focus_set()

    def show_help(self):
        """Show help information"""
        help_text = """
=== Available Commands ===
- clear           : Clear the terminal
- help            : Show this help message
- status          : Show compilation status
- version         : Check Nuitka version

Any other command will be executed as a system command.
Use Up/Down arrow keys to navigate command history.
"""
        self.append_to_terminal(help_text)

    def show_status(self):
        """Show current compilation status"""
        if self.compilation_start_time is None:
            status_text = "No compilation in progress.\n"
        else:
            elapsed_time = time.time() - self.compilation_start_time
            elapsed_str = self.format_time(elapsed_time)
            
            status_text = f"""
=== Compilation Status ===
Current stage: {self.current_phase}
Progress: {self.compilation_progress}%
Elapsed time: {elapsed_str}
ETA: {self.eta_text}
"""
        self.append_to_terminal(status_text)

    def format_time(self, seconds):
        """Format time in seconds to a readable string"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def check_nuitka_version(self):
        """Check and display Nuitka version"""
        try:
            result = subprocess.run(
                ["python", "-m", "nuitka", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.append_to_terminal(f"Nuitka version: {version}\n")
            else:
                self.append_to_terminal(f"Failed to get Nuitka version. Error: {result.stderr}\n")
        except Exception as e:
            self.append_to_terminal(f"Error checking Nuitka version: {str(e)}\n")

    def run_command(self, command):
        """Run a custom command"""
        try:
            self.interactive_mode = True
            self.terminal_mode_indicator.config(text="[INPUT]", fg=self.theme['input_prompt_color'])
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.process = process
            
            # Thread for reading stdout
            def read_output():
                for line in process.stdout:
                    self.output_queue.put(line)
                
                # Process ended
                self.interactive_mode = False
                self.root.after(0, lambda: self.terminal_mode_indicator.config(
                    text="[CMD]", fg=self.theme['command_color']))
            
            # Start reading thread
            threading.Thread(target=read_output, daemon=True).start()
            
        except Exception as e:
            self.append_to_terminal(f"Error executing command: {str(e)}\n")
            self.interactive_mode = False
            self.terminal_mode_indicator.config(text="[CMD]", fg=self.theme['command_color'])

    def check_nuitka_installed(self):
        """Check if Nuitka is installed"""
        try:
            result = subprocess.run(
                ["python", "-m", "nuitka", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def compile_script(self):
        """Compile the selected Python script with Nuitka"""
        # Hide success panel if visible
        self.hide_success_panel()
        
        # Validate file
        if not self.file_path:
            messagebox.showerror("Error", "No Python script selected")
            return
            
        if not os.path.isfile(self.file_path):
            messagebox.showerror("Error", "Selected file does not exist")
            return
            
        if not self.file_path.lower().endswith('.py'):
            messagebox.showerror("Error", "Selected file is not a Python file")
            return
            
        # Check Nuitka installation
        if not self.check_nuitka_installed():
            messagebox.showerror("Error", "Nuitka is not installed. Please install it with 'pip install nuitka'")
            return
            
        # Disable buttons during compilation
        self.compile_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.DISABLED)
        self.output_browse_btn.config(state=tk.DISABLED)
        
        # Reset progress tracking
        self.compilation_start_time = time.time()
        self.compilation_progress = 0
        self.target_progress = 0
        self.eta_text = "Calculating..."
        self.eta_label.config(text=f"ETA: {self.eta_text}")
        self.progress_label.config(text="Progress: 0%")
        self.progress_bar['value'] = 0
        
        # Reset output log
        self.output_log = []
        self.current_phase = "initialize"
        self.stage_label.config(text="Stage: Initialization")
        
        # Reset progress model
        for phase in self.progress_model:
            self.progress_model[phase]["complete"] = False
        
        # Start smooth progress updates
        self.update_target_progress(3)  # Start with 3% immediately
        self.start_smooth_progress()
        
        # Update status
        self.status_label.config(text="Compiling... This may take a while")
        
        # Get compilation options
        compilation_options = self.get_compilation_options()
        
        # Add to terminal
        self.append_to_terminal("\n=== Starting Compilation ===\n")
        self.append_to_terminal(f"Script: {self.file_path}\n")
        self.append_to_terminal(f"Output Directory: {self.output_dir}\n")
        self.append_to_terminal(f"Time: {time.strftime('%H:%M:%S')}\n")
        
        # Format the command for display
        command_display = f"python -m nuitka {' '.join(compilation_options)} {self.file_path}"
        self.append_to_terminal(f"Command: {command_display}\n")
        self.append_to_terminal("Compiling... Play Snake while you wait!\n\n")
        
        # Add the Snake game
        self.add_snake_game()
        
        # Run the compilation in a separate thread
        threading.Thread(target=self._run_compilation, 
                        args=(self.file_path, compilation_options), 
                        daemon=True).start()

    def _run_compilation(self, script_path, compilation_options):
        """Execute the Nuitka compilation command"""
        try:
            # Check if file exists
            if not os.path.isfile(script_path):
                raise FileNotFoundError(f"The file {script_path} does not exist")
                
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Prepare the Nuitka command
            nuitka_cmd = [
                "python", "-m", "nuitka"
            ]
            
            # Add all compilation options
            nuitka_cmd.extend(compilation_options)
            
            # Add the script path at the end
            nuitka_cmd.append(script_path)
            
            self.append_to_terminal(f"Executing: {' '.join(nuitka_cmd)}\n")
            
            # Execute the command
            self.process = subprocess.Popen(
                nuitka_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Enable interactive mode
            self.interactive_mode = True
            
            # Thread for reading stdout
            def read_output():
                for line in self.process.stdout:
                    self.output_queue.put(line)
                
                # Process ended
                self.interactive_mode = False
            
            # Start reading thread
            output_thread = threading.Thread(target=read_output, daemon=True)
            output_thread.start()
            
            # Wait for process to complete
            returncode = self.process.wait()
            
            # Wait for thread to finish reading
            output_thread.join()
            
            # Process finished, update UI in main thread
            self.root.after(0, lambda: self._compilation_finished(returncode))
            
        except Exception as e:
            self.output_queue.put(f"\nERROR: {str(e)}\n")
            self.root.after(0, lambda: self._compilation_error(str(e)))

    def _compilation_finished(self, returncode):
        """Handle compilation completion"""
        # Cancel the smooth progress timer
        if self.smooth_progress_timer:
            self.root.after_cancel(self.smooth_progress_timer)
            self.smooth_progress_timer = None
        
        # Set progress to 100%
        self.compilation_progress = 100
        self.progress_label.config(text="Progress: 100%")
        self.progress_bar['value'] = 100
        self.eta_label.config(text="ETA: Completed")
        self.stage_label.config(text="Stage: Completed")
        
        # Close Snake game with animation
        self.remove_snake_game()
        
        # Re-enable buttons
        self.compile_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.NORMAL)
        self.output_browse_btn.config(state=tk.NORMAL)
        
        # Add completion message to terminal
        if returncode == 0:
            self.append_to_terminal("\n=== Compilation Completed Successfully ===\n")
            self.status_label.config(text="Compilation completed successfully!")
            
            # Get the output executable name
            script_name = os.path.basename(self.file_path)
            executable_name = os.path.splitext(script_name)[0] + ".exe"
            
            # Mostra il pannello di successo invece di una finestra di dialogo
            self.show_success_panel(executable_name)
        else:
            self.append_to_terminal("\n=== Compilation Failed ===\n")
            self.append_to_terminal(f"Return code: {returncode}\n")
            self.status_label.config(text="Compilation failed. See terminal for details.")
            self.stage_label.config(text="Stage: Failed")

    def _compilation_error(self, error_message):
        """Handle exceptions during compilation"""
        # Cancel the smooth progress timer
        if self.smooth_progress_timer:
            self.root.after_cancel(self.smooth_progress_timer)
            self.smooth_progress_timer = None
                
        # Update progress indicators
        self.progress_label.config(text="Progress: Error")
        self.progress_bar['value'] = 0
        self.eta_label.config(text="ETA: Failed")
        self.stage_label.config(text="Stage: Error")
        
        # Close Snake game
        self.remove_snake_game()
        
        # Re-enable buttons
        self.compile_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.NORMAL)
        self.output_browse_btn.config(state=tk.NORMAL)
        
        self.status_label.config(text="Error occurred during compilation")
        self.append_to_terminal(f"\n=== ERROR ===\n{error_message}\n")
        
        messagebox.showerror(
            "Error",
            f"An error occurred during compilation:\n{error_message}"
        )
        
        # Reset compilation state
        self.compilation_start_time = None

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        try:
            if os.path.exists(self.output_dir):
                # Open folder in file explorer
                if sys.platform == 'win32':
                    os.startfile(self.output_dir)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', self.output_dir])
                else:  # Linux
                    subprocess.call(['xdg-open', self.output_dir])
                    
                self.append_to_terminal(f"Opened output folder: {self.output_dir}\n")
            else:
                self.append_to_terminal(f"Error: Output directory does not exist: {self.output_dir}\n")
        except Exception as e:
            self.append_to_terminal(f"Error opening output folder: {str(e)}\n")

    def add_snake_game(self):
        """Add the Snake game to the application"""
        # Hide options panel during compilation
        if hasattr(self, 'options_frame'):
            self.options_frame.grid_forget()
        
        # Hide success panel if visible
        self.hide_success_panel()
        
        # Create a new frame for the game
        self.game_container = tk.Frame(self.main_panel, bg=self.theme['bg_color'])
        self.game_container.grid(row=4, column=0, sticky="nsew", padx=10, pady=(10, 5))
        
        # Create the snake game
        self.snake_game = SnakeGame(self.game_container, self.theme)
    
        # Focus on game container for keyboard controls
        self.game_container.focus_set()

    def remove_snake_game(self):
        """Remove the Snake game and restore options panel"""
        if hasattr(self, 'snake_game'):
            # Show exit animation
            def cleanup():
                self.snake_game.destroy()
                self.game_container.destroy()
                delattr(self, 'snake_game')
                
                # Show options panel again
                if hasattr(self, 'options_frame'):
                    self.options_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 5))
            
            # Show game over animation and then clean up
            self.snake_game.show_game_over_animation(callback=cleanup)
        else:
            # Just show options panel if game doesn't exist
            if hasattr(self, 'options_frame'):
                self.options_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 5))

    def cleanup(self):
        """Clean up resources before application exit"""
        # Cancel any pending timers
        if self.smooth_progress_timer:
            self.root.after_cancel(self.smooth_progress_timer)
        
        # Terminate any running processes
        if hasattr(self, 'process') and self.process:
            try:
                if self.process.poll() is None:  # Process still running
                    self.process.terminate()
                    time.sleep(0.2)
                    if self.process.poll() is None:  # Still running
                        self.process.kill()  # Force kill
            except:
                pass
        
        # Clean up Snake game
        if hasattr(self, 'snake_game'):
            self.snake_game.destroy()

# Main function to run the application
def main():
    try:
        root = tk.Tk()
        app = NuitkaCompilerApp(root)
        
        # Set icon (if available)
        try:
            root.iconbitmap("python.ico")
        except:
            pass  # No icon available, continue without it
        
        # Handle window closing
        def on_closing():
            app.cleanup()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Application Error", f"An unexpected error occurred:\n{str(e)}")

if __name__ == "__main__":
    main()
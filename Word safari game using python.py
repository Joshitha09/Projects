import tkinter as tk
from tkinter import messagebox
import random
import string
import time
import pygame
import imageio

from PIL import Image, ImageTk

background_image_path = r"C:\Users\HOME\Downloads\page1.jpg"
background_image_path2 = r"C:\Users\HOME\Downloads\page11.mp4"
background_image_path3 = r"C:\Users\HOME\Downloads\page2.jpg"
class WordSearchGame:
    def __init__(self, root, player_name, levels, level_index):
        self.root = root
        self.player_name = player_name
        self.levels = levels
        self.current_level = level_index
        self.grid_size = 15
        self.grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.labels = []
        self.word_positions = {}
        self.selected_cells = []
        self.start_time = None
        self.paused_time = None
        self.elapsed_time = 0
        self.revealed_word_count = 0
        self.score = 0

        self.used_words = set()

        pygame.mixer.init()
        self.setup_level()

    def setup_level(self):
        full_dic = self.levels[self.current_level]
        selected_items = random.sample(list(full_dic.items()), 10)
        self.dic = dict(selected_items)
        self.keys = list(self.dic.keys())
        self.values = list(self.dic.values())
        self.grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.word_positions = {}
        self.selected_cells = []
        self.revealed_word_count = 0

        self.create_widgets()
        self.place_words()
        self.fill_empty_spaces()
        self.update_grid()
        self.start_timer()
        
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#fff1e0')
        main_frame.pack(expand=True, fill='both')

        # Player name display
        player_name_label = tk.Label(main_frame, text=f"Player: {self.player_name}", font=("Helvetica", 16, "bold"), fg='Black', bg='#fff1e0')
        player_name_label.pack(side=tk.TOP, pady=10)

        # Level display
        level_label = tk.Label(main_frame, text=f"Level: {self.current_level + 1}", font=("Helvetica", 16, "bold"), fg='Black', bg='#fff1e0')
        level_label.pack(side=tk.TOP, pady=5)

        # Create the word list
        word_frame = tk.Frame(main_frame, bg='#fff1e0')
        word_frame.pack(side=tk.LEFT, padx=10, pady=20)

        self.word_labels = {}
        for index, key in enumerate(self.keys):
            word_label = tk.Label(word_frame, text=key, font=("Algerian", 16), fg='Black', bg='#fff1e0')  # Adjust font here
            word_label.pack(anchor='w')
            self.word_labels[key] = word_label

        # Create the word search grid (Values)
        grid_frame = tk.Frame(main_frame, bg='#fff1e0')
        grid_frame.place(relx=0.5, rely=0.5, anchor='center')

        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                label = tk.Label(grid_frame, text='', font=("Helvetica", 14, "bold"), width=2, height=1, bg='#fff1e0', fg='Black', borderwidth=2, relief="groove")
                label.grid(row=i, column=j, padx=2, pady=2)
                label.bind("<Button-1>", lambda e, x=i, y=j: self.on_label_click(x, y))
                row.append(label)
            self.labels.append(row)

        # Create the control panel
        control_frame = tk.Frame(main_frame, bg='#fff1e0')
        control_frame.pack(side=tk.RIGHT, padx=10, pady=20)

        self.time_label = tk.Label(control_frame, text="TIME\n00:00", font=("Forte", 15), fg='Black', bg='#fff1e0')
        self.time_label.pack(pady=10)
        
        reveal_word_button = tk.Button(control_frame, text="REVEAL WORD", font=("Forte", 15), width=20, bg='#DA9DFF', fg='white', command=self.reveal_word)
        reveal_word_button.pack(pady=5)

        self.pause_button = tk.Button(control_frame, text="PAUSE", font=("Forte", 15), width=20, bg='#FD9FE6', fg='white', command=self.toggle_pause)
        self.pause_button.pack(pady=5)

        audio_button = tk.Button(control_frame, text="AUDIO", font=("Forte", 15), width=20, bg='#32CD32', fg='white', command=self.toggle_music)
        audio_button.pack(pady=5)

        menu_button = tk.Button(control_frame, text="HOME", font=("Forte", 15), width=20, bg='#1E90FF', fg='white', command=self.show_menu)
        menu_button.pack(pady=5)
        
        self.score_label = tk.Label(control_frame, text="SCORE\n0", font=("Forte", 15), fg='Black', bg='#fff1e0')
        self.score_label.pack(pady=10)


    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        if self.paused_time is None:
            self.elapsed_time = int(time.time() - self.start_time)
            self.time_label.config(text=f"TIME\n{self.format_time(self.elapsed_time)}")
            self.root.after(1000, self.update_timer)
                        
    def place_word_in_grid(self, word):
        placed = False
        while not placed:
            direction = random.choice(['horizontal', 'vertical', 'diagonal'])
            word_length = len(word)
            if direction == 'horizontal':
                row = random.randint(0, self.grid_size - 1)
                col = random.randint(0, self.grid_size - word_length)
                if all(self.grid[row][col + i] == ' ' for i in range(word_length)):
                    for i in range(word_length):
                        self.grid[row][col + i] = word[i]
                        self.word_positions.setdefault(word, []).append((row, col + i))
                    placed = True
            elif direction == 'vertical':
                row = random.randint(0, self.grid_size - word_length)
                col = random.randint(0, self.grid_size - 1)
                if all(self.grid[row + i][col] == ' ' for i in range(word_length)):
                    for i in range(word_length):
                        self.grid[row + i][col] = word[i]
                        self.word_positions.setdefault(word, []).append((row + i, col))
                    placed = True
            elif direction == 'diagonal':
                row = random.randint(0, self.grid_size - word_length)
                col = random.randint(0, self.grid_size - word_length)
                if all(self.grid[row + i][col + i] == ' ' for i in range(word_length)):
                    for i in range(word_length):
                        self.grid[row + i][col + i] = word[i]
                        self.word_positions.setdefault(word, []).append((row + i, col + i))
                    placed = True

    def place_words(self):
        for word in self.values:
            if word not in self.used_words:
                self.place_word_in_grid(word)
                self.used_words.add(word)
                
    def fill_empty_spaces(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == ' ':
                    self.grid[i][j] = random.choice(string.ascii_uppercase)

    def update_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.labels[i][j].config(text=self.grid[i][j])

    def on_label_click(self, row, col):
        if self.paused_time is None:
            self.selected_cells.append((row, col))
            self.labels[row][col].config(bg='yellow')
            if len(self.selected_cells) >= 2:
                self.check_word()
        else:
            messagebox.showinfo("Paused", "The game is currently paused. Resume the game to continue playing.")

    def check_word(self):
        start, end = self.selected_cells[0], self.selected_cells[-1]
        word = self.get_word_from_cells(start, end)

        if word in self.values or word[::-1] in self.values:
            # Increment score
            self.score += 1
            self.score_label.config(text=f"SCORE\n{self.score}")

            word_to_remove = word if word in self.values else word[::-1]
            word_positions = self.word_positions[word_to_remove]
            highlight_color = '#{0:06x}'.format(random.randint(0, 0xffffff))

            for (row, col) in word_positions:
                self.labels[row][col].config(bg=highlight_color, font=("Helvetica", 14, "bold", "overstrike"))

            key = self.get_key_by_value(word_to_remove)
            self.word_labels[key].config(fg='gray', font=("Helvetica", 14, "overstrike"))

            self.values.remove(word_to_remove)
            self.check_victory()
        else:
            for (row, col) in self.selected_cells:
                self.labels[row][col].config(bg='#fff1e0')

        self.selected_cells.clear()

    def get_word_from_cells(self, start, end):
        word = ''
        if start[0] == end[0]:  # Horizontal
            row = start[0]
            cols = range(start[1], end[1] + 1) if start[1] < end[1] else range(end[1], start[1] + 1)
            word = ''.join(self.grid[row][col] for col in cols)
        elif start[1] == end[1]:  # Vertical
            col = start[1]
            rows = range(start[0], end[0] + 1) if start[0] < end[0] else range(end[0], start[0] + 1)
            word = ''.join(self.grid[row][col] for row in rows)
        elif abs(start[0] - end[0]) == abs(start[1] - end[1]):  # Diagonal
            if start[0] < end[0] and start[1] < end[1]:  # Diagonal down-right
                word = ''.join(self.grid[start[0] + i][start[1] + i] for i in range(abs(start[0] - end[0]) + 1))
            elif start[0] > end[0] and start[1] > end[1]:  # Diagonal up-left
                word = ''.join(self.grid[start[0] - i][start[1] - i] for i in range(abs(start[0] - end[0]) + 1))
            elif start[0] < end[0] and start[1] > end[1]:  # Diagonal down-left
                word = ''.join(self.grid[start[0] + i][start[1] - i] for i in range(abs(start[0] - end[0]) + 1))
            elif start[0] > end[0] and start[1] < end[1]:  # Diagonal up-right
                word = ''.join(self.grid[start[0] - i][start[1] + i] for i in range(abs(start[0] - end[0]) + 1))
        return word

    def get_key_by_value(self, value):
        for key, val in self.dic.items():
            if val == value:
                return key
        return None

    def reveal_word(self):
        if self.revealed_word_count < 15:
            remaining_words = [word for word in self.values if word in self.word_positions]
            if remaining_words:
                random_word = random.choice(remaining_words)
                for (row, col) in self.word_positions[random_word]:
                    self.labels[row][col].config(bg='yellow')
                key = self.get_key_by_value(random_word)
                self.values.remove(random_word)
                self.word_labels[key].config(fg='gray')
                self.word_labels[key].config(font=("Helvetica", 14, "overstrike"))
                self.check_victory()
                self.revealed_word_count += 1
            else:
                messagebox.showinfo("No Words Left", "All words have been found.")
        else:
            messagebox.showinfo("Limit Reached", "You can reveal a maximum of 5 words per game.")
                        
    def toggle_pause(self):
        if self.paused_time is None:
            self.paused_time = time.time()
            self.pause_button.config(text="RESUME")
        else:
            paused_duration = time.time() - self.paused_time
            self.start_time += paused_duration
            self.paused_time = None
            self.pause_button.config(text="PAUSE")
            self.update_timer()

    def toggle_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.load(r"C:\Users\HOME\Downloads\joyride-jamboree-206911.mp3")
            pygame.mixer.music.play(-1)

    def show_menu(self):
        self.root.destroy()
        main()

            
    def check_victory(self):
        if not self.values:
            self.show_end_screen()

    def show_end_screen(self):
        # Clear the current window
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("Congratulations!")
        self.root.geometry("1000x1500")

        # Load the MP4 file
        video_path = r"C:\Users\HOME\Downloads\page.mp4"
        video = imageio.get_reader(video_path)

        # Create a canvas to display the video
        canvas = tk.Canvas(self.root, width=800, height=600)
        canvas.pack(fill="both", expand=True)

        def update_video(frame_number):
            try:
                frame = video.get_next_data()
                frame = Image.fromarray(frame)
                frame = ImageTk.PhotoImage(frame)
                canvas.create_image(0, 0, anchor=tk.NW, image=frame)
                canvas.image = frame
                self.root.after(33, update_video, frame_number + 1)
            except:
                pass

        update_video(0)

        congrats_label = tk.Label(self.root, text=f"Congratulations {self.player_name}!", font=("Forte", 40), fg='Black', bg='#fff1e0')
        congrats_label.place(relx=0.5, rely=0.4, anchor='center')

        total_time_label = tk.Label(self.root, text=f"Total Time: {self.format_time(self.elapsed_time)}", font=("Forte", 35), fg='Black', bg='#fff1e0')
        total_time_label.place(relx=0.5, rely=0.6, anchor='center')

        score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Forte", 35), fg='Black', bg='#fff1e0')
        score_label.place(relx=0.5, rely=0.7, anchor='center')

        # Displaying the title again
        title = tk.Label(self.root, text="Word Safari", font=("Forte", 96, "bold"), fg='white', bg='#fff1e0')
        title.place(relx=0.5, rely=0.2, anchor='center')
        change_title_color(title)

        subtitle = tk.Label(self.root, text="Track Down Words in the Wild!", font=("Brush Script MT", 24), fg='Black', bg='#fff1e0')
        subtitle.place(relx=0.5, rely=0.3, anchor='center')

        play_again_button = tk.Button(self.root, text="Play Again", font=("Forte", 20), bg='#DA9DFF', fg='white', command=self.play_again)
        play_again_button.place(relx=0.3, rely=0.8, anchor='center')

        exit_button = tk.Button(self.root, text="Exit", font=("Forte", 20), bg='#DA9DFF', fg='white', command=self.root.quit)
        exit_button.place(relx=0.7, rely=0.8, anchor='center')

        print("End screen displayed")
                    
    title_colors = ['#FF5733', '#33FF57', '#3357FF', '#F333FF', '#33FFF3', '#F3FF33']

    def change_title_color(label, color_index=0):
        label.config(fg=title_colors[color_index])
        next_color_index = (color_index + 1) % len(title_colors)
        root.after(500, change_title_color, label, next_color_index)

    def play_again(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        initial_screen()
    
    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"
    

    
def initial_screen():
    root.title("Word Safari")
    root.configure(bg='#4b0082')

    background_image = Image.open(background_image_path)
    background_photo = ImageTk.PhotoImage(background_image)

    canvas = tk.Canvas(root)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor='nw')
    canvas.image = background_photo
    
    title = tk.Label(root, text="Word Safari", font=("Forte", 100, "bold"), fg='white', bg='#fff1e0')
    title.place(relx=0.5, rely=0.15, anchor='center')
    change_title_color(title)

    subtitle = tk.Label(root, text="Track Down Words in the Wild!", font=("Brush Script MT", 24), fg='Black', bg='#fff1e0')
    subtitle.place(relx=0.5, rely=0.25, anchor='center')

    global name_entry
    name_label = tk.Label(root, text="Enter your name:", font=("Forte", 20), fg='Black', bg='#fff1e0')
    name_label.place(relx=0.5, rely=0.35, anchor='center')

    name_entry = tk.Entry(root, font=("Calibri", 16))
    name_entry.place(relx=0.5, rely=0.4, anchor='center')

    level_label = tk.Label(root, text="Choose Level:", font=("Forte", 20), fg='Black', bg='#fff1e0')
    level_label.place(relx=0.5, rely=0.45, anchor='center')

    global level_var
    level_var = tk.StringVar(value="Level 1")
    levels = ["Level 1", "Level 2", "Level 3"]
    for i, level in enumerate(levels, start=1):
        level_radio = tk.Radiobutton(root, text=level, variable=level_var, value=level, font=("Forte", 25), fg='Black', bg='#fff1e0', selectcolor='#fff1e0')
        level_radio.place(relx=0.5, rely=0.45 + i*0.05, anchor='center')

    play_button = tk.Button(root, text="Play Now", command=start_game, font=("Forte"), bg='#DA9DFF', fg='white', relief='flat', width=20, height=2)
    play_button.place(relx=0.5, rely=0.7, anchor='center')

    audio_button = tk.Button(root, text="Toggle Music", command=toggle_music, font=("Forte"), bg='#FFA500', fg='white', relief='flat', width=20, height=2)
    audio_button.place(relx=0.5, rely=0.8, anchor='center')

    instructions_button = tk.Button(root, text="Instructions", command=instructions_screen, font=("Forte"), bg='#00FFFF', fg='white', relief='flat', width=20, height=2)
    instructions_button.place(relx=0.5, rely=0.9, anchor='center')
    
def instructions_screen():
    instructions_window = tk.Toplevel(root)
    instructions_window.title("Instructions")
    instructions_window.geometry("2000x1500")

    background_image2 = Image.open(background_image_path3)
    background_photo2 = ImageTk.PhotoImage(background_image2)

    canvas = tk.Canvas(instructions_window, width=500, height=500)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo2, anchor='nw')
    canvas.image = background_photo2

    instructions_text = (
        "Welcome to Word Safari!\n\n"
        "How to play:\n\n"
        "1. Enter your name and click 'Play Now' to start the game.\n"
        "2. After entering your name, you will be taken to a screen to select the difficulty level.\n"
        "3. Once a level is selected, the game grid will appear with letters and a list of clues on the side.\n"
        "4. Your goal is to find and highlight the words, that we found from the list of clues, in the grid.\n"
        "5. Click and drag to select a word. Words can be found horizontally, vertically, or diagonally.\n"
        "6. Once you find a word, it will be highlighted, and the word will be crossed out from the list of clues.\n"
        "7. Continue until you find all the words.\n"
        "8. Click 'REVEAL WORD' to highlight a random word on the grid.\n"
        "9. Click 'PAUSE' to pause the game.\n"
        "10. Click 'HOME' to return to the main menu at any time.\n\n"

        "Enjoy the game!"
    )

    instructions_label = tk.Label(instructions_window, text=instructions_text, font=("Forte", 20), fg='Black', bg='#fff1e0', justify='left')
    instructions_label.place(relx=0.5, rely=0.4, anchor='center')

    close_button = tk.Button(instructions_window, text="Close", command=instructions_window.destroy, font=("Forte"), bg='#FD9FE6', fg='white', relief='flat', width=20, height=2)
    close_button.place(relx=0.5, rely=0.8, anchor='center')

title_colors = ['#FF5733', '#33FF57', '#3357FF', '#F333FF', '#33FFF3', '#F3FF33']
def toggle_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    else:
        pygame.mixer.music.load(r"C:\Users\HOME\Downloads\joyride-jamboree-206911.mp3")
        pygame.mixer.music.play(-1)

def change_title_color(label, color_index=0):
    label.config(fg=title_colors[color_index])
    next_color_index = (color_index + 1) % len(title_colors)
    root.after(500, change_title_color, label, next_color_index)

def start_game():
    global root
    player_name = name_entry.get()
    selected_level = level_var.get()
    level_index = int(selected_level.split()[-1]) - 1

    for widget in root.winfo_children():
        widget.destroy()

    game = WordSearchGame(root, player_name, levels, level_index)

def main():
    global root, background_image_path, levels
    background_image_path = r"C:\Users\HOME\Downloads\page1.jpg"

    pygame.mixer.init()
    pygame.mixer.music.load(r"C:\Users\HOME\Downloads\joyride-jamboree-206911.mp3")
    pygame.mixer.music.play(-1)

    level1 = {
        "CHARMINAR": "HYDERABAD",
        "IT HUB": "BANGALORE",
        "PINK CITY": "JAIPUR",
        "LAND OF TEMPLES": "TAMILNADU",
        "FINANCIAL CAPITAL": "MUMBAI",
        "COCONUT TREES": "KERALA",
        "TAJ MAHAL": "AGRA",
        "TEA": "ASSAM",
        "ANDHRA OOTY": "ARAKU",
        "DIAMOND CITY": "SURAT",
        "CITY OF LAKES": "UDAIPUR",
        "BLUE CITY": "JODHPUR",
        "QUEEN OF HILL STATIONS": "OOTY",
        "CITY OF JOY": "KOLKATA",
        "CITY BEAUTIFUL": "CHANDIGARH",
        "SPIRITUAL CAPITAL OF INDIA": "VARANASI"
    }

    level2 = {
        "EIFFEL TOWER": "PARIS",
        "STATUE OF LIBERTY": "NEWYORK",
        "BIG BEN": "LONDON",
        "GREAT WALL": "CHINA",
        "COLOSSEUM": "ROME",
        "TAJ MAHAL": "AGRA",
        "SYDNEY OPERA HOUSE": "SYDNEY",
        "PYRAMIDS": "EGYPT",
        "MACHU PICCHU": "PERU",
        "LEANING TOWER": "PISA",
        "PETRA": "JORDAN",
        "HOLLYWOOD": "LOSANGELES",
        "RED SQUARE": "MOSCOW",
        "GOLDEN GATE": "SANFRANCISCO"
    }

    level3 = {
        "I AM THE VEHICLE OF LORD VISHNU": "GARUDA",
        "I AM THE DEMON KING IN RAMAYANA": "RAVANA",
        "I AM THE ADDITION OF SEVEN AND THREE": "TEN",
        "I AM THE KING OF HINDU MYTHOLOGY": "INDRA",
        "I AM GOD'S OWN COUNTRY": "KERALA",
        "WHAT GOES UP BUT NEVER COMES DOWN": "AGE",
        "WHAT HAS TO BE BROKEN BEFORE YOU CAN USE IT": "EGG",
        "FIRST PRESIDENT OF UNITED STATES": "WASHINGTON",
        "WHAT ANCIENT CIVILIZATION BUILT THE PYRAMIDS": "EGYPTIANS",
        "WHO WAS KNOWN AS IRON LADY": "MARGARET",
        "I AM THE FASTEST LAND ANIMAL": "CHEETAH",
        "I AM THE LARGEST PLANET": "JUPITER",
        "I AM THE SMALLEST COUNTRY": "VATICANCITY",
        "I AM THE LARGEST OCEAN": "PACIFIC",
        "I AM THE TALLEST MOUNTAIN": "EVEREST",
        "I AM THE LONGEST RIVER": "NILE",
        "I AM THE BIGGEST DESERT": "SAHARA",
        "I AM THE CAPITAL OF JAPAN": "TOKYO",
        "I AM THE SMALLEST CONTINENT": "AUSTRALIA",
        "I AM THE LARGEST ISLAND": "GREENLAND"
    }

    levels = [level1, level2, level3]
    root = tk.Tk()
    initial_screen()
    root.mainloop()

if __name__ == "__main__":
    main()
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
import pygame
import os

# Initialize root window and Pygame mixer
root = Tk()
root.title("Music Player")
root.geometry("600x400")
pygame.mixer.init()

# Variables
songs = []
current_song = ""
paused = False
loop = False  # Track loop status
drag_data = {"song_index": None}  # Track drag start index

# Load music folder
def load_music():
    global current_song
    root.directory = filedialog.askdirectory()
    for song in os.listdir(root.directory):
        name, ext = os.path.splitext(song)
        if ext == ".mp3":
            songs.append(song)
    
    # Load songs into the listbox
    songlist.delete(0, END)
    for song in songs:
        songlist.insert("end", song)

    # Set the first song as the current song
    if songs:
        songlist.selection_set(0)
        current_song = songs[songlist.curselection()[0]]

def load_song():
    # Prompt user to select a song file
    song_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if song_path:
        song_name = os.path.basename(song_path)
        
        # Ask for position (default is end of queue)
        position = simpledialog.askinteger(
            "Position",
            f"Enter position to insert '{song_name}' (1 to {len(songs) + 1}, default: end):",
            minvalue=1,
            maxvalue=len(songs) + 1
        )

        # Insert song at the specified position (or end if no position is given)
        if position is None:
            position = len(songs)  # End of queue
        else:
            position -= 1  # Adjust for 0-based indexing

        songs.insert(position, song_name)
        songlist.insert(position, song_name)

def search_song():
    song_name = simpledialog.askstring("Search Song", "Enter the song name to search:") +".mp3"
    if song_name:
        try:
            position = songs.index(song_name) + 1  # Convert to 1-based index
            messagebox.showinfo("Song Found", f"'{song_name}' is at position {position} in the queue.")
            songlist.selection_clear(0, END)
            songlist.selection_set(position - 1)
            songlist.see(position - 1)  # Scroll to the song in the Listbox
        except ValueError:
            messagebox.showwarning("Not Found", f"'{song_name}' is not in the queue.")

# Play selected song
def play_music():
    global current_song, paused, loop
    if not paused:
        pygame.mixer.music.load(os.path.join(root.directory, current_song))
        pygame.mixer.music.play(loops=-1 if loop else 0)  # Loop indefinitely if loop is enabled
    else:
        pygame.mixer.music.unpause()
        paused = False

def play_selected(event):
    global current_song, paused
    try:
        current_song = songs[songlist.curselection()[0]]
        paused = False
        play_music()
    except IndexError:
        pass
# Pause music
def pause_music():
    global paused
    pygame.mixer.music.pause()
    paused = True

# Play the next song in the list
def next_music():
    global current_song, paused
    try:
        songlist.selection_clear(0, END)
        songlist.selection_set(songs.index(current_song) + 1)
        current_song = songs[songlist.curselection()[0]]
        play_music()
    except:
        pass

# Play the previous song in the list
def prev_music():
    global current_song, paused
    try:
        songlist.selection_clear(0, END)
        songlist.selection_set(songs.index(current_song) - 1)
        current_song = songs[songlist.curselection()[0]]
        play_music()
    except:
        pass

def delete_song(event):
    try:
        selected_index = songlist.nearest(event.y)
        selected_song = songs[selected_index]

        # Ask for confirmation
        if messagebox.askyesno("Delete Song", f"Are you sure you want to delete '{selected_song}'?"):
            # Remove from the songs list and Listbox
            songs.pop(selected_index)
            songlist.delete(selected_index)

            # Adjust current_song if it was the deleted one
            global current_song
            if current_song == selected_song:
                current_song = songs[selected_index] if songs else ""
                
    except IndexError:
        pass

# Toggle looping
def toggle_loop():
    global loop
    loop = not loop
    loop_button.config(relief=SUNKEN if loop else RAISED)

# Handle drag start
def on_drag_start(event):
    drag_data["song_index"] = songlist.nearest(event.y)

# Handle drag motion
def on_drag_motion(event):
    pass  # Optional: Add visual feedback for dragging here

# Handle drag drop
def on_drag_drop(event):
    global songs

    # Get the index where the song is dropped
    from_index = drag_data["song_index"]
    to_index = songlist.nearest(event.y)

    # Rearrange items in both Listbox and songs list
    if from_index != to_index:
        song = songs.pop(from_index)
        songs.insert(to_index, song)

        # Update Listbox display to reflect new order
        songlist.delete(0, END)
        for song in songs:
            songlist.insert("end", song)

        # Reset selection to new position
        songlist.selection_set(to_index)

def show_guide():
    instructions = """
    Music Player Guide:
    - Select Folder: Go to Organise > Select Folder to load songs from a folder into the player.
    - Add Song to Queue: Go to Organise > Add Song to Queue to add a new song at a specific position in the queue.
    - Play/Pause: Use the Play button to start the music or Pause button to pause the playback.
    - Play Song from Queue: Double-click on any song in the list to play it immediately.
    - Next/Previous: Use the Next and Previous buttons to navigate through songs in the queue.
    - Loop: Toggle looping for the current song by clicking the Loop button.
    - Reorder Songs: Left-click and drag a song in the list to rearrange it within the queue.
    - Delete Song: Right-click on a song in the list to delete it from the queue. A confirmation prompt will appear.
    - Search Song: Go to Organise > Search Song to find a song in the queue. Its position will be displayed.
    """
    messagebox.showinfo("Guide", instructions)

# Menu bar for selecting folder
menubar = Menu(root)

organise_menu = Menu(menubar, tearoff=False)
organise_menu.add_command(label='Select Folder', command=load_music)
organise_menu.add_command(label='Select Song',command=load_song)
organise_menu.add_command(label='Search Song',command=search_song)
menubar.add_cascade(label='Organise', menu=organise_menu)

guide_menu = Menu(menubar, tearoff=False)
guide_menu.add_command(label='Guide', command=show_guide)
menubar.add_cascade(label='Help', menu=guide_menu)

root.config(menu=menubar)

# Listbox for song list with bindings for drag-and-drop
songlist = Listbox(root, bg='black', fg='white', width=100, height=20)
songlist.pack()
songlist.bind("<Button-1>", on_drag_start)      # Capture initial click position
songlist.bind("<B1-Motion>", on_drag_motion)    # (Optional) Handle drag motion
songlist.bind("<ButtonRelease-1>", on_drag_drop)  # Drop item when released
songlist.bind("<Double-1>", play_selected)      # Frame for control buttons
songlist.bind("<Button-3>", delete_song)
control_frame = Frame(root)
control_frame.pack()

# Load images for buttons
play_img = PhotoImage(file='play.png')
pause_img = PhotoImage(file='pause.png')
next_img = PhotoImage(file='next.png')
prev_img = PhotoImage(file='prev.png')
loop_img = PhotoImage(file='loop.png')

# Create control buttons with images
play_button = Button(control_frame, image=play_img, borderwidth=0, command=play_music)
pause_button = Button(control_frame, image=pause_img, borderwidth=0, command=pause_music)
next_button = Button(control_frame, image=next_img, borderwidth=0, command=next_music)
prev_button = Button(control_frame, image=prev_img, borderwidth=0, command=prev_music)
loop_button = Button(control_frame, image=loop_img, borderwidth=0, command=toggle_loop)

# Arrange buttons in grid
prev_button.grid(row=0, column=0, padx=7, pady=10)
play_button.grid(row=0, column=1, padx=7, pady=10)
pause_button.grid(row=0, column=2, padx=7, pady=10)
next_button.grid(row=0, column=3, padx=7, pady=10)
loop_button.grid(row=0, column=4, padx=7, pady=10)

# Run the application
root.mainloop()

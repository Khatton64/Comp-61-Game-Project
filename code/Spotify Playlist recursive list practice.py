#Spotify Playlist recursive list practie

catalog = {}

menu = ["1. Add a song","2.) Remove a song","3.) Print out Playlist", "4.) Quit"]

class Song:

    def __init__(self,name,artist,minutes,seconds):
        self.name = name
        self.artist = artist
        self.minutes = minutes 
        self.seconds = seconds

    def __str__(self):
        return f"{self.name} by {self.artist} - {self.minutes}:{self.seconds:02d}"
    
    def add_song():

        name = input("Please enter the song name: ")
        artist = input("Please enter the original artist of the song: ")
        minutes = int(input("Please enter the minute length: "))
        seconds = int(input("Please enter the second length: "))
           
        song = Song(name, artist, minutes, seconds)
        catalog.append(song)

    def print_playlist():

        for song in catalog:

            print(song)
        
        print()

        if not catalog:

            print("Bitch you playlist empty add some shi")

        else:

            for song in catalog:

                print(song)
            print()


while True:
    print("\n--- Spotify Playlist Builder ---")
    for item in menu:
        print(item)
    
    menu_input = input("Choose an option (1-4): ")

    if menu_input == "1":
        add_song()
    elif menu_input == "2":
        remove_song()
    elif menu_input == "3":
        print_playlist()
    elif menu_input == "4":
        print("Goodbye!")
        break  # ← This ends the loop
    else:
        print("Invalid input. Please choose a number from 1 to 4.")



        




   
    


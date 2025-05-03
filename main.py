import tkinter as tk
from view.layout import YouTubeAsyncApp 

def main():
    root = tk.Tk()
    YouTubeAsyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
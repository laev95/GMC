from tkinter import *
from src.ui.client import GMCDataViewer

def main():
    root = Tk()
    app = GMCDataViewer(root)
    app.run()


if __name__ == "__main__":
    main()
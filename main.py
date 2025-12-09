import tkinter as tk
from ConnectWiseApi import ConnectWiseAPIClient
from App import App

# Authors: Weiping, Shane, and Max

if __name__ == "__main__":
    username = "granitenet+4aEzXiEroletPUCe" # Don't ever give to AI
    password = "bXrww7ESRNdYiJBv" #don't ever give to AI
    client_id = "7e24f143-6e6e-4ae8-a26f-ebc90ca077c7" #don't ever give to AI

    # Build the API client
    api_client = ConnectWiseAPIClient(
        username=username,
        password=password,
        client_id=client_id
    )

    # Start the GUI
    root = tk.Tk()
    App(root, api_client)
    root.mainloop()
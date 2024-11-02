import tkinter as tk

root = tk.Tk()
root.geometry("500x500")

# Create a frame to contain the widgets
frame = tk.Frame(root)
frame.pack(anchor='w', padx=10, pady=10)

# Add labels and buttons to the frame, aligned to the left
label1 = tk.Label(frame, text="Label 1")
label1.pack(anchor='w')

button1 = tk.Button(frame, text="Button 1")
button1.pack(anchor='w')

label2 = tk.Label(frame, text="Label 2")
label2.pack(anchor='w')

button2 = tk.Button(frame, text="Button 2")
button2.pack(anchor='w')

root.mainloop()

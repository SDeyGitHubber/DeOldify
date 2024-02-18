import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from deoldify.visualize import get_image_colorizer

class DeOldifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DeOldify Image Colorization")

        # Initialize DeOldify colorizer
        self.colorizer = get_image_colorizer(artistic=True)
        self.render_factor = 35

        # Create and style widgets
        self.upload_button = ttk.Button(root, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=10)

        self.status_label = tk.Label(root, text="", font=("Helvetica", 10))
        self.status_label.pack()

        self.original_label = tk.Label(root, text="Original Image", font=("Helvetica", 12, "bold"))
        self.original_label.pack()

        self.colorized_label = tk.Label(root, text="Colorized Image", font=("Helvetica", 12, "bold"))
        self.colorized_label.pack()

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
        if file_path:
            self.status_label.config(text="Processing...")
            self.root.update()
            colorized_image = self.colorize_image(file_path)
            self.display_images(file_path, colorized_image)
            self.status_label.config(text="")

    def colorize_image(self, image_path):
        # Perform colorization using DeOldify
        result_path = self.colorizer.plot_transformed_image(path=image_path, render_factor=self.render_factor, compare=True)
        return Image.open(result_path)

    def display_images(self, original_path, colorized_image):
        # Resize images if they are too large for the application window
        max_size = (500, 500)
        original_img = Image.open(original_path)
        original_img.thumbnail(max_size, Image.LANCZOS)
        colorized_image.thumbnail(max_size, Image.LANCZOS)

        # Convert to PhotoImage after resizing
        original_img = ImageTk.PhotoImage(original_img)
        colorized_img = ImageTk.PhotoImage(colorized_image)

        # Display original and colorized images
        self.original_label.config(image=original_img)
        self.colorized_label.config(image=colorized_img)
        self.colorized_label.image = colorized_img

def main():
    root = tk.Tk()
    app = DeOldifyApp(root)
    root.geometry("600x600")  # Set initial window size
    root.mainloop()

if __name__ == "__main__":
    main()
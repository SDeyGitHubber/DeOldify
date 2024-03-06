import tkinter as tk
from tkinter import filedialog, ttk, simpledialog
from PIL import Image, ImageTk, ImageEnhance
from pathlib import Path  # Import Path for path handling
from deoldify.visualize import get_image_colorizer

class DeOldifyApp:
    max_size = (500, 500)

    def __init__(self, root):
        self.root = root
        self.variations = []
        self.variation_images = []

        self.colorized_image = None
        self.image_path = None

        self.colorized_frame = tk.Frame(self.root)
        self.colorized_frame.pack()

        self.generate_variations_button = tk.Button(self.root, text="Generate Variations", command=self.show_variation_options)
        self.generate_variations_button.pack()

        self.root.title("DeOldify Image Colorization")

        # Initialize DeOldify colorizer
        self.colorizer = get_image_colorizer(artistic=True)
        self.render_factor = 35

        # Load background image (you can replace with your path or remove the block if not needed)
        try:
            self.background_image = ImageTk.PhotoImage(Image.open("Images\Designer.png"))
        except FileNotFoundError:
            print("Background image not found. Proceeding without background.")
            self.background_image = None

        # Create canvas widget for background
        self.canvas = tk.Canvas(root, width="600", height="600")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        if self.background_image:
            self.canvas.create_image(0, 0, image=self.background_image, anchor=tk.NW)

        # Create image frame for side-by-side display
        self.image_frame = tk.Frame(self.canvas, width=600, height=300)  # Adjust height if needed
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        # Create sub-frames for original and colorized images
        self.original_frame = tk.Frame(self.image_frame, width=300, height=300)
        self.original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.colorized_frame = tk.Frame(self.image_frame, width=300, height=300)
        self.colorized_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create labels for original and colorized images
        self.original_label = tk.Label(self.original_frame, text="Original Image:", font=("Helvetica", 12, "bold"))
        self.original_label.pack(anchor=tk.NW)

        self.colorized_label = tk.Label(self.colorized_frame, text="Colorized Image:", font=("Helvetica", 12, "bold"))
        self.colorized_label.pack(anchor=tk.NW)

        # Create image labels (placeholders for now)
        self.original_image_label = tk.Label(self.original_frame, image=None)
        self.original_image_label.pack(fill=tk.BOTH, expand=True)

        self.colorized_image_label = tk.Label(self.colorized_frame, image=None)
        self.colorized_image_label.pack(fill=tk.BOTH, expand=True)

        # Create upload button
        self.upload_button = ttk.Button(self.canvas, text="Upload Image", command=self.upload_image)
        self.upload_button.place(relx=0.2, rely=0.9, anchor=tk.SW)

        # Create and style status label
        self.status_label = tk.Label(self.canvas, text="", font=("Helvetica", 10))
        self.status_label.place(relx=0.5, rely=0.1, anchor=tk.N)

        self.original_image = None  # Initialize as None initially
        self.resized_original_image = None  # Initialize as None initially

        self.colorized_image = None
        self.variations = None
        self.variation_images = None


    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
        if not file_path:
            raise RuntimeError("No image selected.")

        self.image_path = file_path

        self.status_label.config(text="Processing...")
        self.root.update()

        try:
            # Colorize image
            result_path = self.colorizer.plot_transformed_image(path=self.image_path, render_factor=self.render_factor, compare=True)
            self.colorized_image = Image.open(result_path)

            if self.colorized_image is not None:
                self.display_images(self.image_path, self.colorized_image)
                self.status_label.config(text="Image processed successfully.")

        except FileNotFoundError:
            self.status_label.config(text="Error opening image file.")

        """
        Handles image upload process, including error handling and display.

        Raises:
            RuntimeError: If no image file is selected.
        """

        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
        if not file_path:
            raise RuntimeError("No image selected.")

        # Store the uploaded file path
        self.image_path = file_path

        self.status_label.config(text="Processing...")
        self.root.update()

        try:
            # Colorize image
            result_path = self.colorizer.plot_transformed_image(path=self.image_path, render_factor=self.render_factor, compare=True)
            self.colorized_image = Image.open(result_path)  # Load the colorized image

            if self.colorized_image is not None:
                # Display the colorized image
                self.display_images(self.image_path, self.colorized_image)


        except FileNotFoundError:
            self.status_label.config(text="Error opening image file.")

        except Exception as e:
            self.status_label.config(text=f"An error occurred: {e}")
    
    

    def generate_variations(self, n):
        if self.colorized_image:
            original_img = self.colorized_image.copy()

            self.variations = []
            self.variation_images = []

            for i in range(n):
                hue_shift = (i - n // 2) * 10  # Adjust for desired range
                saturation_factor = 1.0 + (i / (n - 1)) * 0.5  # Adjust for desired range

                variation_img = original_img.copy()
                color_enhancer = ImageEnhance.Color(variation_img)
                variation_img = color_enhancer.enhance(saturation_factor)

                hue_filter = ImageEnhance.Color(variation_img)
                variation_img = hue_filter.enhance(hue_shift)

                # Resize variation if necessary
                if variation_img.size[0] > self.max_size[0] or variation_img.size[1] > self.max_size[1]:
                    variation_img.thumbnail(self.max_size, Image.LANCZOS)

                # Convert variation to PhotoImage format for Tkinter display
                variation_img = ImageTk.PhotoImage(variation_img)

                # Store variation and PhotoImage
                self.variations.append(variation_img)
                self.variation_images.append(variation_img)

            # Display variations
            self.display_variations()
        else:
            print("Colorized image not available. Please colorize an image first.")

    def show_variation_options(self):
        if self.colorized_image:
            num_variations = simpledialog.askinteger("Generate Variations", "Enter the number of variations:")
            if num_variations is not None and num_variations > 0:
                self.generate_variations(num_variations)
        else:
            print("Colorized image not available. Please colorize an image first.")

    def display_images(self, original_path, colorized_image):
        """
        Displays the original and colorized images in the application window.

        Args:
            original_path (str): Path to the original image file.
            colorized_image (PIL.Image object): The colorized image object.
        """

        try:
            # Define and initialize max_size as a constant variable
            max_size = self.max_size

            # Open both images
            original_img = Image.open(original_path)
            colorized_img_copy = colorized_image.copy()

            # Resize images if necessary
            if original_img.size[0] > max_size[0] or original_img.size[1] > max_size[1]:
                original_img.thumbnail(max_size, Image.LANCZOS)

            if colorized_img_copy.size[0] > max_size[0] or colorized_img_copy.size[1] > max_size[1]:
                colorized_img_copy.thumbnail(max_size, Image.LANCZOS)

            # Calculate image dimensions **before** updating labels
            original_width, original_height = original_img.size
            colorized_width, colorized_height = colorized_img_copy.size

            # Convert images to PhotoImage format for Tkinter display
            original_img = ImageTk.PhotoImage(original_img)
            colorized_img = ImageTk.PhotoImage(colorized_img_copy)

            # Create and position labels above images
            font = ("Helvetica", 12, "bold")  # Adjust font as desired

            original_label_text = tk.Label(
                self.original_frame, text="Original Image:", font=font, justify=tk.CENTER
            )
            original_label_text.pack(fill=tk.X)  # Pack horizontally across the frame

            colorized_label_text = tk.Label(
                self.colorized_frame, text="Colorized Image:", font=font, justify=tk.CENTER
            )
            colorized_label_text.pack(fill=tk.X)

            # Update image labels and store original dimensions
            self.original_image_label.config(image=original_img)
            self.original_image_label.image = original_img
            self.original_dimensions = (original_width, original_height)

            self.colorized_image_label.config(image=colorized_img)
            self.colorized_image_label.image = colorized_img
            self.colorized_dimensions = (colorized_width, colorized_height)

            # **Place image labels above images, adjusting for label height**
            x_offset_original = (self.original_frame.winfo_width() - self.original_dimensions[0]) // 2
            y_offset_original = original_label_text.winfo_height()  # Adjust for label height

            x_offset_colorized = (self.colorized_frame.winfo_width() - self.colorized_dimensions[0]) // 2
            y_offset_colorized = colorized_label_text.winfo_height()

            # Update label positions
            self.original_label.place(x=x_offset_original, y=y_offset_original)
            self.colorized_label.place(x=x_offset_colorized, y=y_offset_colorized)

            # **Place image labels on top of their respective frames**
            self.original_image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.colorized_image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
        except FileNotFoundError:
            self.status_label.config(text="Error opening original image!")

        except Exception as e:
            self.status_label.config(text=f"An error occurred: {e}")

    
    

    def colorize_image(self, image_path):
        # Perform colorization using DeOldify
        result_path = self.colorizer.plot_transformed_image(path=image_path, render_factor=self.render_factor, compare=True)
        return Image.open(result_path)
    


    def display_variations(self):
        """
        Displays the generated variations in additional labels.
        """
        if self.variations and self.variation_images:
            # Clear any existing variation labels
            for widget in self.colorized_frame.winfo_children():
                if widget.winfo_class() == "Label" and widget != self.colorized_label:
                    widget.destroy()

            # Create and display labels for each variation
            for i, variation_image in enumerate(self.variation_images):
                variation_label = tk.Label(self.colorized_frame, text=f"Variation {i+1}:")
                variation_label.pack(anchor=tk.NW)

                variation_image_label = tk.Label(self.colorized_frame, image=variation_image)
                variation_image_label.pack()


    def save_image(self):
        # Get user input for file name and format
        save_options = {
            "defaultextension": ".png",
            "filetypes": [("JPEG Images", "*.jpg"), ("PNG Images", "*.png")],
            "title": "Save Colorized Image",
        }
        save_path = filedialog.asksaveasfilename(**save_options)

        if save_path:
            # Extract format from extension
            format = save_path.split(".")[-1].lower()
            # Save the colorized image
            self.colorized_image.save(save_path, format.upper())
            self.status_label.config(text="Image saved successfully!")

def main():
    root = tk.Tk()
    app = DeOldifyApp(root)
    root.geometry("600x600")
    root.mainloop()

if __name__ == "__main__":
    main()
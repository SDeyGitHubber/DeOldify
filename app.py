import streamlit as st
import numpy as np
import cv2
import os

# Function to colorize image
def colorize_image(image):
    PROTOTXT = "C:/Users/Dhruv Sanghvi/Desktop/deoldify/DeOldify/models/colorization_deploy_v2.prototxt"
    POINTS = "C:/Users/Dhruv Sanghvi/Desktop/deoldify/DeOldify/models/pts_in_hull.npy"
    MODEL = "C:/Users/Dhruv Sanghvi/Desktop/deoldify/DeOldify/models/colorization_release_v2.caffemodel"

    # Load the model
    net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
    pts = np.load(POINTS)

    # Load centers for ab channel quantization used for rebalancing
    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

    # Prepare the image
    scaled = image.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(lab)[0]
    L -= 50

    # Colorize the image
    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))
    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")
    
    return colorized

# Streamlit app
def main():
    st.title("Image Colorization App")
    st.write("Upload a black and white image to colorize it.")
    
    # About section
    st.sidebar.title("About")
    st.sidebar.info(
        "This is a simple image colorization app built using Streamlit. "
        "It uses a deep learning model to automatically colorize black and white images."
    )

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

    if uploaded_file is not None:
        # Read the image
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        
        # Display uploaded image
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Loader
        with st.spinner('Colorizing Image...'):
            # Colorize the image
            colorized = colorize_image(image)

        # Display colorized image
        st.image(colorized, caption="Colorized Image", use_column_width=True)

        # Automatically play audio
       
     
if __name__ == "__main__":
    main()

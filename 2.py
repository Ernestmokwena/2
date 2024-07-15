import streamlit as st
from PIL import Image
from pyzbar.pyzbar import decode
import sqlite3
import cv2
import numpy as np

# SQLite setup
conn = sqlite3.connect('scanprods.db')
c = conn.cursor()

# Function to scan QR code from image
def scan_qr_code_from_image(img):
    img_gray = img.convert('L')
    decoded_objects = decode(img_gray)
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode('utf-8')
        return qr_data
    else:
        return None

# Function to fetch product details from database using product ID
def fetch_product_details(product_id):
    c.execute('SELECT product_name, barcode, expiry_date, status FROM products WHERE id = ?', (product_id,))
    product = c.fetchone()
    if product:
        return product
    else:
        return None

# Function to capture video from the camera and scan for QR codes
def scan_qr_code_from_camera():
    cap = cv2.VideoCapture(0)
    qr_data = None

    stframe = st.empty()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            pts = obj.polygon
            if len(pts) > 4:
                hull = cv2.convexHull(np.array([pts], dtype=np.float32))
                hull = list(map(tuple, np.squeeze(hull)))
            else:
                hull = pts
            n = len(hull)
            for j in range(0, n):
                cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 255, 0), 3)
        
        stframe.image(frame, channels="BGR")
        
        if qr_data:
            break
    
    cap.release()
    return qr_data

def main():
    st.title('Shoot & Scan QR Code')
    tab1, tab2 = st.tabs(["Upload Image", "Scan with Camera"])

    with tab1:
        uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            qr_data = scan_qr_code_from_image(img)
            if qr_data:
                if qr_data.startswith('PRODAPP:'):
                    try:
                        product_id = int(qr_data.split('\n')[0].split(': ')[1])
                        product_details = fetch_product_details(product_id)
                        if product_details:
                            product_name, barcode, expiry_date, status = product_details
                            st.success(f"Decoded QR Code Data:")
                            st.write(f"Product Name: {product_name}")
                            st.write(f"Barcode: {barcode}")
                            st.write(f"Expiry Date: {expiry_date}")
                            st.write(f"Status: {status}")

                            if status == 'AUTHORIZED':
                                st.success('Product is Authorized')
                                if st.button('the world can do with a smart shopper like you!'):
                                    st.write('Keep being a good citizen')
                            else:
                                st.warning('Product is Counterfeit')
                                if st.button('Report'):
                                    st.write('Report submitted!')
                        else:
                            st.warning("Product details not found.")
                    except Exception as e:
                        st.warning("Error decoding QR code data.")
                        st.warning(f"Details: {e}")
                else:
                    st.warning("This QR code was not generated by PRODTRACK app.")
            else:
                st.warning("No QR code found in the uploaded image.")

    with tab2:
        st.subheader('Or Scan with Camera')
        if st.button('Start Camera Scan'):
            qr_data = scan_qr_code_from_camera()
            if qr_data:
                st.write(f"QR Code Data: ")
                if qr_data.startswith('PRODAPP:'):
                    try:
                        product_id = int(qr_data.split('\n')[0].split(': ')[1])
                        product_details = fetch_product_details(product_id)
                        if product_details:
                            product_name, barcode, expiry_date, status = product_details
                            st.success(f"Decoded QR Code Data:")
                            st.write(f"Product Name: {product_name}")
                            st.write(f"Barcode: {barcode}")
                            st.write(f"Expiry Date: {expiry_date}")
                            st.write(f"Status: {status}")

                            if status == 'AUTHORIZED':
                                st.success('Product is Authorized')
                                if st.button('the world can do with a smart shopper like you!'):
                                    st.write('Keep being a good citizen')
                            else:
                                st.warning('Product is Counterfeit')
                                if st.button('Report'):
                                    st.write('Report submitted!')
                        else:
                            st.warning("Product details not found.")
                    except Exception as e:
                        st.warning("Error decoding QR code data.")
                        st.warning(f"Details: {e}")
                else:
                    st.warning("This QR code was not generated by PRODTRACK app.")
            else:
                st.warning("No QR code found in the camera feed.")

if __name__ == '__main__':
    main()

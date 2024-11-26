import cv2
import numpy as np
import tkinter as tk
import h
from tkinter import Button, Canvas
from PIL import Image, ImageTk
import requests

# Địa chỉ URL từ IP Webcam 
url = "http://192.168.137.231:8080/shot.jpg"

# Các thông số
widthCam = 640
heightCam = 480
questions = 30
choices = 4
ans = [1, 0, 1, 2, 3, 1, 2, 2, 1, 3, 0, 0, 1, 2, 0, 1, 0, 0, 2, 2, 2, 1, 3, 0, 1, 0, 1, 2, 3, 0]

# Biến toàn cục
running = False
score_display = ""
img_processed = None  # Biến lưu ảnh đã xử lý

# Hàm lấy ảnh từ IP Webcam
def fetch_image_from_ip():
    try:
        img_resp = requests.get(url)
        img_array = np.array(bytearray(img_resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        return img
    except Exception as e:
        print("Không thể lấy ảnh từ IP Webcam:", e)
        return None

# Hàm xử lý ảnh và chấm điểm
def process_image(img=None):
    global score_display, canvas_score, img_processed
    if img is None:  # Nếu không có ảnh đầu vào, đọc từ IP Webcam
        img = fetch_image_from_ip()
        if img is None:
            print("Không thể lấy ảnh từ IP Webcam")
            return

    # Tiền xử lý
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, 10, 50)

    # Tìm contour lớn nhất qua hàm trong h.py
    biggest = h.find_biggest_contour(imgCanny)

    # Xử lý khi tìm được khung
    if biggest is not None:
        biggest = biggest.reshape((4, 2))
        biggest = sorted(biggest, key=lambda x: x[0] + x[1])  # Sắp xếp thứ tự góc
        pts1 = np.float32(biggest)
        pts2 = np.float32([[500, 0], [0, 0], [500, 1500], [0, 1500]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarp = cv2.warpPerspective(img, matrix, (500, 1500))

        # Hiển thị ảnh đã làm phẳng
        imgWarpGray = cv2.cvtColor(imgWarp, cv2.COLOR_BGR2GRAY)
        imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]
        boxes = h.splitBoxes(imgThresh)
        myPixelVal = np.zeros((questions, choices))
        countR, countC = 0, 0

        for image in boxes:
            totalPixels = cv2.countNonZero(image)
            myPixelVal[countR][countC] = totalPixels
            countC += 1
            if countC == choices:
                countC = 0
                countR += 1
        
        myIndex = []
        for x in range(questions):
            arr = myPixelVal[x]
            max_val = np.max(arr)
            threshold = max_val * 0.8
            chosen_answers = np.where((arr >= threshold) & (arr > 1000))[0]
    
            if len(chosen_answers) == 1:
                myIndex.append(chosen_answers[0])
            else:
                myIndex.append(-1)

        grading = []
        for x in range(0, questions):
            if ans[x] == myIndex[x]:
                grading.append(1)
            else:
                grading.append(0)
        score = (sum(grading) / questions) * 10
        score_display = f"Điểm: {int(score)}" 

        # Cập nhật hiển thị điểm
        canvas_score.delete("all")
        canvas_score.create_text(80, 30, text=score_display, font=("Arial", 20), fill="green")
        
        # Áp dụng hàm showAnswers để đánh dấu các ô đáp án
        img_processed = h.showAnswers(imgWarp, myIndex, grading, ans, questions, choices)
        # Hiển thị ảnh đã chấm điểm trong cửa sổ mới
        show_processed_image()
    else:
        print("Không tìm thấy khung hình chữ nhật lớn nhất.")

# Hàm hiển thị ảnh đã xử lý trong cửa sổ mới
def show_processed_image():
    if img_processed is not None:
        processed_window = tk.Toplevel(root)
        processed_window.title("Ảnh đã chấm điểm")
        canvas_processed = Canvas(processed_window, width=500, height=1500, bg="white")
        canvas_processed.pack()
        resized_img = cv2.resize(img_processed, (300, 800))
        img_rgb = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)
        canvas_processed.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas_processed.image_tk = img_tk

# Hàm cập nhật ảnh từ IP Webcam
def update_camera():
    global running, canvas_cam
    if running:
        img = fetch_image_from_ip()
        if img is not None:
            img = cv2.resize(img, (widthCam, heightCam))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)
            canvas_cam.create_image(0, 0, anchor=tk.NW, image=img_tk)
            canvas_cam.image_tk = img_tk
        canvas_cam.after(10, update_camera)

# Bắt đầu luồng camera
def start_camera():
    global running
    running = True
    update_camera()

# Dừng camera
def stop_camera():
    global running
    running = False
    root.destroy()

# Giao diện Tkinter
root = tk.Tk()
root.title("Chấm điểm trắc nghiệm (IP Webcam)")
root.geometry(f"{widthCam}x{heightCam + 200}")

# Khung hiển thị camera
frame_left = tk.Frame(root, width=widthCam, height=heightCam, bg="black")
frame_left.grid(row=0, column=0, padx=10, pady=10)
canvas_cam = Canvas(frame_left, width=widthCam, height=heightCam, bg="black")
canvas_cam.pack()

# Khung hiển thị điểm
frame_right = tk.Frame(root, width=200, height=150, bg="white")
frame_right.grid(row=0, column=1, padx=10, pady=10)
canvas_score = Canvas(frame_right, width=200, height=150, bg="white")
canvas_score.pack()

# Các nút điều khiển
frame_buttons = tk.Frame(root, width=900, height=100, bg="")
frame_buttons.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

btn_start = Button(frame_buttons, text="Bắt đầu", command=start_camera, width=20, height=2, bg="green", fg="white")
btn_start.grid(row=0, column=0, padx=10)

btn_capture = Button(frame_buttons, text="Chụp ảnh", command=process_image, width=20, height=2, bg="blue", fg="white")
btn_capture.grid(row=0, column=1, padx=10)

btn_exit = Button(frame_buttons, text="Kết thúc", command=stop_camera, width=20, height=2, bg="red", fg="white")
btn_exit.grid(row=0, column=3, padx=10)

root.mainloop()

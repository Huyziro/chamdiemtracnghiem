import cv2
import numpy as np

def find_biggest_contour(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggest = None
    max_area = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(approx) == 4:  # Chỉ lấy contour có 4 cạnh (tứ giác)
                if area > max_area:
                    biggest = approx
                    max_area = area

    return biggest

def splitBoxes(img):
    rows = np.vsplit(img, 30)  # Chia ảnh thành 30 hàng (mỗi hàng là 1 câu hỏi)
    boxes = []
    for r in rows:
        cols = np.hsplit(r, 5)[1:]  # Bỏ cột đầu tiên (cột số thứ tự) và chỉ lấy 4 cột còn lại
        for box in cols:
            boxes.append(box)
    return boxes

def showAnswers(img, myIndex, grading, ans, questions, choices):
    cell_width = img.shape[1] // (choices + 1)  # Bỏ qua cột đầu tiên
    cell_height = img.shape[0] // questions

    for q in range(questions):
        correct_answer = ans[q]
        chosen_answer = myIndex[q]

        # Trường hợp không chọn hoặc chọn nhiều đáp án
        if chosen_answer == -1:
            for choice in range(choices):  # Duyệt qua tất cả các ô của câu hỏi
                x = int((choice + 1) * cell_width)  # +1 để bỏ qua cột đầu tiên
                y = int(q * cell_height)
                center_x = int(x + cell_width / 2)
                center_y = int(y + cell_height / 2)
                cv2.circle(img, (center_x, center_y), 20, (255, 165, 0), cv2.FILLED)
            continue

        for choice in range(choices):
            x = int((choice + 1) * cell_width)  # +1 để bỏ qua cột đầu tiên
            y = int(q * cell_height)
            center_x = int(x + cell_width / 2)
            center_y = int(y + cell_height / 2)

            # Vẽ chấm tròn theo kết quả
            if choice == correct_answer:
                cv2.circle(img, (center_x, center_y), 20, (0, 255, 0), cv2.FILLED)
            elif choice == chosen_answer and grading[q] == 0:
                cv2.circle(img, (center_x, center_y), 20, (0, 0, 255), cv2.FILLED)

    return img

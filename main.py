import pytesseract
from PIL import ImageGrab, ImageEnhance, ImageOps
from pynput.mouse import Controller as MouseController
import time
from openai import OpenAI




pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Adjustable offsets
TOP_OFFSET = 10       # pixels below first question header
BOTTOM_OFFSET = 5     # pixels above next question header
SCROLL_DELAY = 0.3    # seconds to wait between scrolls
WAIT_AFTER_CAPTURE = 1.0  # wait after capturing
SCROLL_AMOUNT = -2    # negative for scrolling down, small number for gradual scroll

# Question separator in the doc
QUESTION_SEPARATOR = "\n-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n"

# Number of questions to extract
amount = int(input("Enter number of questions to extract: "))

# Prepare output file
output_file = "Extracted_Text_Questions.txt"
with open(output_file, "w", encoding="utf-8") as f:
    pass  # clear file

# Initialize mouse controller
mouse_ctrl = MouseController()

# Tesseract config
custom_config = r'--psm 6'

current_question = 1
questions_captured = 0

while questions_captured < amount:
    # Take screenshot of current screen
    screenshot = ImageGrab.grab()

    # Preprocess image
    gray = ImageOps.grayscale(screenshot)
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(2.0)

    # OCR with bounding boxes
    data = pytesseract.image_to_data(enhanced, output_type=pytesseract.Output.DICT)

    # Find all question headers
    questions = []
    for j in range(len(data['text']) - 1):
        word1 = data['text'][j].strip()
        word2 = data['text'][j + 1].strip()
        if word1.lower() == "question" and word2.isdigit():
            questions.append({
                "number": int(word2),
                "x_min": data['left'][j],
                "y_min": data['top'][j],
                "x_max": data['left'][j] + data['width'][j],
                "y_max": data['top'][j] + data['height'][j]
            })

    # Detect current and next question headers
    q1 = next((q for q in questions if q["number"] == current_question), None)
    q2 = next((q for q in questions if q["number"] == current_question + 1), None)
    q3 = next((q for q in questions if q["number"] == current_question + 2), None)

    if q1 and q2:
        # Crop question text area between headers
        box_top = q1["y_max"] + TOP_OFFSET
        box_bottom = q2["y_min"] - BOTTOM_OFFSET
        box_left = q1["x_min"]
        box_right = 2000

        # Crop and extract text
        section_crop = enhanced.crop((box_left, box_top, box_right, box_bottom))
        section_text = pytesseract.image_to_string(section_crop, config=custom_config).strip()

        # Append to file
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(section_text + QUESTION_SEPARATOR)

        print(f"✅ Question {current_question} captured.")
        questions_captured += 1
        current_question += 1

        # Wait after capture
        time.sleep(WAIT_AFTER_CAPTURE)

        # If overshot and also see Question #+2, scroll up half
        if q3:
            mouse_ctrl.scroll(0, -SCROLL_AMOUNT // 2)  # scroll up half
        else:
            mouse_ctrl.scroll(0, SCROLL_AMOUNT)  # scroll down normally
        time.sleep(SCROLL_DELAY)

    else:
        # Gradually scroll down to find the question
        mouse_ctrl.scroll(0, SCROLL_AMOUNT)
        time.sleep(SCROLL_DELAY)


out = open("Extracted_Text_Questions.txt", "r", encoding="utf-8")

response = client.responses.create(
    model="gpt-4.1",
    input = ("awnser the questions, only repond with Question <number>: followed by capital A,B,C,D/ depending on whichever is relevant to the question. If you cannot find a question, say \"skip\"\n"+out.read())#(userin.read())
)
#out = response.output_text
#print('The current pointer position is {}'.format(mouse.position))
with open("awnsers.txt", "w") as a:
  a.write(response.output_text)
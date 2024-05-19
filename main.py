import face_recognition
import cv2
import numpy as np
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AttendanceSystem:
    def __init__(self):
        self.known_faces_encodings = []
        self.known_faces_names = []
        self.students = []
        self.pins = {}  # Dictionary to store PINs for each student
        self.admin_name = os.getenv("ADMIN_NAME")  # Admin name from environment variable
        self.create_log_file()
        self.load_known_faces()
        self.failed_attempts = {name.lower(): 0 for name in self.known_faces_names}  # Initialize failed attempts

    def create_log_file(self):
        # Create a single text file to store all login details
        self.log_filename = "attendance_log.txt"
        self.anomaly_log_filename = "anomaly_attendance_log.txt"
        with open(self.log_filename, 'a'):
            pass  # Create the file if it doesn't exist
        with open(self.anomaly_log_filename, 'a'):
            pass  # Create the file if it doesn't exist

    def load_known_faces(self):
        # Load known faces and their encodings
        try:
            jobs_image = face_recognition.load_image_file("photos/jobs.jpg")
            jobs_encoding = face_recognition.face_encodings(jobs_image)[0]

            ratan_mahinda_image = face_recognition.load_image_file("photos/mahinda.jpeg")
            ratan_mahinda_encoding = face_recognition.face_encodings(ratan_mahinda_image)[0]

            sadmona_image = face_recognition.load_image_file("photos/sadmona.jpg")
            sadmona_encoding = face_recognition.face_encodings(sadmona_image)[0]

            tesla_image = face_recognition.load_image_file("photos/tesla.jpeg")
            tesla_encoding = face_recognition.face_encodings(tesla_image)[0]

            self.known_faces_encodings = [
                jobs_encoding,
                ratan_mahinda_encoding,
                sadmona_encoding,
                tesla_encoding
            ]

            self.known_faces_names = [
                "jobs",
                "mahinda",
                "sadmona",
                "tesla"
            ]

            # Initialize PINs for each student using environment variables
            self.pins = {
                "jobs": os.getenv("JOBS_PIN"),
                "mahinda": os.getenv("mahinda_PIN"),
                "sadmona": os.getenv("SADMONA_PIN"),
                "tesla": os.getenv("TESLA_PIN")
            }

            self.students = self.known_faces_names.copy()

            # Load additional students from the file
            self.load_additional_students()

        except Exception as e:
            print(f"Error loading known faces: {e}")

    def load_additional_students(self):
    # Load additional students' data from the file
     if os.path.exists(".env"):
        with open(".env", "r") as file:
            for line in file:
                try:
                    name, pin, photo_path = line.strip().split(',')
                    new_face_image = face_recognition.load_image_file(photo_path)
                    new_face_encoding = face_recognition.face_encodings(new_face_image)[0]
                    self.known_faces_encodings.append(new_face_encoding)
                    self.known_faces_names.append(name)
                    self.pins[name] = pin
                    self.failed_attempts[name.lower()] = 0
                except Exception as e:
                    print(f"Error processing line '{line.strip()}': {e}")


    def run_attendance_system(self):
        video_capture = cv2.VideoCapture(0)

        while True:
            ret, frame = video_capture.read()  # Capture frame-by-frame
            if not ret:
                continue

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_faces_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_faces_names[first_match_index]

                    # Ensure the name is lowercase to match the dictionary keys
                    lower_name = name.lower()

                    if self.failed_attempts[lower_name] >= 3:
                        self.display_anomaly(frame, name)
                        self.log_anomaly(name)
                    else:
                        verified = self.verify_pin(name, frame)
                        if verified:
                            self.log_attendance(name)
                            if name == self.admin_name:
                                self.open_admin_window()
                        else:
                            self.failed_attempts[lower_name] += 1
                            self.display_incorrect_pin(frame)
                            self.log_incorrect_pin_attempt(name)

                cv2.rectangle(frame, (left * 4, top * 4), (right * 4, bottom * 4), (0, 0, 255), 2)
                cv2.putText(frame, name, (left * 4 + 6, bottom * 4 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 1)

            cv2.imshow("attendance system", frame)

            if cv2.waitKey(1) == 13:  # Check if Enter key is pressed
                break

        video_capture.release()
        cv2.destroyAllWindows()

    def verify_pin(self, name, frame):
        # Example method to verify PIN entry for a given student name
        if name in self.pins:
            entered_pin = self.get_pin_from_user_input(frame)  # Replace with actual method to get PIN from user input
            if entered_pin == self.pins[name]:
                self.failed_attempts[name.lower()] = 0  # Reset failed attempts on successful verification
                return True
        return False

    def get_pin_from_user_input(self, frame):
        # Example method to get PIN from user input using OpenCV
        pin = ""
        while True:
            cv2.putText(frame, "Enter PIN:", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.imshow("attendance system", frame)
            key = cv2.waitKey(1)
            if key == 13:  # Check if Enter key is pressed
                break
            elif key == 8:  # Backspace key
                pin = pin[:-1]
            elif key >= 48 and key <= 57:  # Numeric keys
                pin += chr(key)
            cv2.putText(frame, '*' * len(pin), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.imshow("attendance system", frame)
        return pin

    def log_attendance(self, name):
        # Log attendance by appending to the log file
        with open(self.log_filename, 'a') as file:
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"ATTENDANCE,{name},{current_time}\n")
            print(f"Attendance logged for {name} at {current_time}")

    def check_anomaly(self, login_time):
        # Hardcoded rules for anomaly detection (e.g., outside typical hours of 0600-1800)
        if login_time < 600 or login_time > 1800:
            return True
        return False

    def log_anomaly(self, name):
        with open(self.anomaly_log_filename, 'a') as file:
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"ANOMALY,{name},{current_time}\n")
            print(f"Anomaly logged for {name} at {current_time}")

    def log_incorrect_pin_attempt(self, name):
        with open(self.anomaly_log_filename, 'a') as file:
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"INCORRECT PIN ATTEMPT,{name},{current_time}\n")
            print(f"Incorrect PIN attempt logged for {name} at {current_time}")

    def display_anomaly(self, frame, name):
        cv2.putText(frame, "Anomaly Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.imshow("attendance system", frame)

    def display_incorrect_pin(self, frame):
        cv2.putText(frame, "Incorrect PIN!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.imshow("attendance system", frame)

    def open_admin_window(self):
        # Create a simple admin window with Tkinter
        admin_window = tk.Tk()
        admin_window.title("Admin Menu")

        tk.Label(admin_window, text="Admin Menu", font=("Helvetica", 16)).pack(pady=10)

        upload_btn = tk.Button(admin_window, text="Upload New Photo", command=self.upload_photo)
        upload_btn.pack(pady=5)

        tk.Label(admin_window, text="Enter Name:").pack(pady=5)
        self.name_entry = tk.Entry(admin_window)
        self.name_entry.pack(pady=5)

        tk.Label(admin_window, text="Enter PIN:").pack(pady=5)
        self.pin_entry = tk.Entry(admin_window)
        self.pin_entry.pack(pady=5)

        add_btn = tk.Button(admin_window, text="Add New Person", command=self.add_new_person)
        add_btn.pack(pady=20)

        admin_window.mainloop()

    def upload_photo(self):
        # Open file dialog to select a photo
        self.photo_path = filedialog.askopenfilename(
            title="Select Photo", filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )

    def add_new_person(self):
        # Get the entered name and PIN
        name = self.name_entry.get()
        pin = self.pin_entry.get()

        if not name or not pin or not self.photo_path:
            messagebox.showerror("Error", "All fields and photo must be provided")
            return

        # Load the new face photo and encode it
        new_face_image = face_recognition.load_image_file(self.photo_path)
        new_face_encoding = face_recognition.face_encodings(new_face_image)[0]

        # Add the new face encoding and name to the system
        self.known_faces_encodings.append(new_face_encoding)
        self.known_faces_names.append(name)
        self.pins[name] = pin
        self.failed_attempts[name.lower()] = 0

        # Save the new face photo to the photos directory
        cv2.imwrite(f"photos/{name}.jpg", cv2.imread(self.photo_path))

        # Save the new user data to the .env file
        with open(".env", "a") as file:
            file.write(f"{name},{pin},photos/{name}.jpg\n")

        messagebox.showinfo("Success", f"New person {name} added successfully!")

        # Reset the fields and photo path
        self.name_entry.delete(0, tk.END)
        self.pin_entry.delete(0, tk.END)
        self.photo_path = ""

if __name__ == "__main__":
    attendance_system = AttendanceSystem()
    attendance_system.run_attendance_system()

IT21160134 - Sandakelum M.D.B.
IT21161124 - Kumara D. D. K. C

Face recognition enable  attendance system

This Python project implements a simple attendance system using face recognition. The system captures video frames, detects faces, and verifies identities against a database of known faces using the `face_recognition` library. It logs attendance with timestamps and handles anomalies like incorrect PIN entries or suspicious login times.

 Features

- Face Detection and Recognition:** Utilizes `face_recognition` library to detect and recognize faces in real-time.
- PIN Verification: Secure verification process using PINs associated with each student.
- Anomaly Detection: Logs anomalies such as incorrect PIN attempts or suspicious login times outside defined hours.
- Admin Interface: Provides an admin interface using Tkinter for managing students and viewing system logs.

 Setup

1. Environment Setup: ( I already provie `.env` file)
   - Create a `.env` file with environment variables:
     ```
     ADMIN_NAME=your_admin_name
     JOBS_PIN=jobs_pin
     mahinda_PIN=mahinda_pin
     SADMONA_PIN=sadmona_pin
     TESLA_PIN=tesla_pin
     ```

2. Dependencies:
   - Install required Python libraries:
     ```
     pip install face_recognition opencv-python numpy python-dotenv
     ```

3. Run the Application:
   - Execute the `main.py` script:
     ```
     python main.py
     ```


Feel free to adjust the details as per your specific project setup and requirements. Let me know if you need any further modifications or if there's anything else you'd like to include!

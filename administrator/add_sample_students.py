from app import app, db, Student
import random

sample_students = [
    {"id": "ST001", "name": "Arjun Sharma", "class": "Grade 10", "contact": "Ramesh Sharma", "phone": "+91-9876543210"},
    {"id": "ST002", "name": "Priya Patel", "class": "Grade 11", "contact": "Meera Patel", "phone": "+91-9876543211"},
    {"id": "ST003", "name": "Rahul Singh", "class": "Grade 9", "contact": "Suresh Singh", "phone": "+91-9876543212"},
    {"id": "ST004", "name": "Sneha Gupta", "class": "Grade 12", "contact": "Rajesh Gupta", "phone": "+91-9876543213"},
    {"id": "ST005", "name": "Vikram Kumar", "class": "Grade 10", "contact": "Sunita Kumar", "phone": "+91-9876543214"},
    {"id": "ST006", "name": "Ananya Rao", "class": "Grade 11", "contact": "Venkat Rao", "phone": "+91-9876543215"},
    {"id": "ST007", "name": "Karan Joshi", "class": "Grade 9", "contact": "Pooja Joshi", "phone": "+91-9876543216"},
    {"id": "ST008", "name": "Riya Mehta", "class": "Grade 12", "contact": "Amit Mehta", "phone": "+91-9876543217"},
    {"id": "ST009", "name": "Aadhya Reddy", "class": "Grade 8", "contact": "Srinivas Reddy", "phone": "+91-9876543218"},
    {"id": "ST010", "name": "Rohan Verma", "class": "Grade 7", "contact": "Kavita Verma", "phone": "+91-9876543219"},
    {"id": "ST011", "name": "Ishita Agarwal", "class": "Grade 10", "contact": "Deepak Agarwal", "phone": "+91-9876543220"},
    {"id": "ST012", "name": "Harsh Malik", "class": "Grade 11", "contact": "Nisha Malik", "phone": "+91-9876543221"},
    {"id": "ST013", "name": "Diya Kapoor", "class": "Grade 6", "contact": "Rohit Kapoor", "phone": "+91-9876543222"},
    {"id": "ST014", "name": "Aryan Tiwari", "class": "Grade 8", "contact": "Sunita Tiwari", "phone": "+91-9876543223"},
    {"id": "ST015", "name": "Kavya Nair", "class": "Grade 9", "contact": "Manoj Nair", "phone": "+91-9876543224"},
]

def add_sample_students():
    with app.app_context():
        # Check if students already exist
        if Student.query.count() > 0:
            print("Sample students already exist!")
            return
            
        print("Adding sample students...")
        
        for student_data in sample_students:
            student = Student(
                student_id=student_data["id"],
                name=student_data["name"],
                class_name=student_data["class"],
                emergency_contact_name=student_data["contact"],
                emergency_contact_phone=student_data["phone"],
                drill_participation=random.randint(60, 100),  # Random participation percentage
                status='active'
            )
            db.session.add(student)
        
        db.session.commit()
        print(f"Added {len(sample_students)} sample students successfully!")

if __name__ == '__main__':
    add_sample_students()

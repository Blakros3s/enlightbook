# Enlightbook - School Management System

A comprehensive school management system for managing students, teachers, academic records, attendance, exams, and finances.

## Overview

Enlightbook provides an all-in-one solution for educational institutions to manage their daily operations efficiently. The system includes modules for student management, academic administration, attendance tracking, examination management, financial operations, and communication.

## System Access

**URL**: http://localhost:3000

### First Time Setup (IMPORTANT!)

Before you can use the system, you need to create the first admin user (superuser). This is done via the backend command line:

**Using Docker:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

**Without Docker:**
```bash
cd backend
python manage.py createsuperuser
```

You will be prompted to enter:
- Username (e.g., `admin`)
- Email address
- Password (enter twice for confirmation)

**Example:**
```
Username: admin
Email: admin@school.com
Password: your_secure_password
Password (again): your_secure_password
Superuser created successfully.
```

### Logging In

Once the superuser is created:

1. Go to **http://localhost:3000/login**
2. Enter your superuser **username** and **password**
3. Click **Login**

You now have full administrative access to create other users (teachers, students, accountants, etc.) and configure the system.

## Core Features

### 1. Dashboard
The main dashboard provides:
- Overview statistics (total students, teachers, classes)
- Quick action buttons for common tasks
- Recent activity feed
- Visual charts and analytics
- System notifications

### 2. User Management
- **Login System**: Secure authentication with JWT tokens
- **User Profiles**: Manage personal information and settings
- **Role-based Access**: Different permissions for administrators, teachers, and staff
- **User Directory**: View and manage system users

### 3. Student Management
- **Student Directory**: Complete list of all enrolled students
- **Student Profiles**: 
  - Personal information
  - Contact details
  - Academic history
  - Attendance records
  - Fee status
- **Enrollment**: Register new students
- **Search & Filter**: Find students by name, class, or ID

### 4. Teacher Management
- **Teacher Directory**: List of all teaching staff
- **Teacher Profiles**:
  - Qualifications and experience
  - Assigned classes
  - Subject assignments
  - Contact information
- **Class Assignments**: Assign teachers to specific classes

### 5. Academic Management

#### Academic Years
- Create and manage academic sessions
- Set start and end dates
- Activate/deactivate academic years
- View year-wise statistics

#### Classes
- Create and organize classes/grades
- Assign class teachers
- Set capacity limits
- View class rosters

#### Subjects
- Manage subject catalog
- Assign subjects to classes
- Set subject codes and credits
- Assign subject teachers

#### Enrollments
- Enroll students in classes
- View enrollment history
- Transfer students between classes
- Generate enrollment reports

### 6. Attendance System

#### Daily Attendance
- Mark daily attendance for classes
- Bulk attendance marking
- View attendance calendars
- Export attendance reports

#### Period Attendance
- Subject-wise attendance tracking
- Period-by-period marking
- Teacher-specific attendance views

#### Leave Management
- Apply for student leave
- Approve/reject leave requests
- View leave history
- Track leave balances

#### Attendance Reports
- Monthly attendance summaries
- Student-wise attendance percentage
- Class attendance analytics
- Absentee reports
- Late coming reports

### 7. Examination Management

#### Exam Schedule
- Create examination timetables
- Set exam dates and timings
- Assign exam venues
- Manage different exam types (unit tests, mid-terms, finals)

#### Grading System
- Configure grading scales (A-F, percentage, etc.)
- Set grade boundaries
- Manage grading criteria
- Custom grading schemes per class/subject

#### Results Entry
- Enter exam marks for students
- Bulk result upload
- Calculate totals and percentages
- Generate rank lists

#### Report Cards
- Generate student report cards
- View complete academic performance
- Print-friendly formats
- Parent/guardian copies

### 8. Financial Management

#### Fee Structure
- Create fee structures for different classes
- Set fee categories (tuition, exam, transport, etc.)
- Configure one-time and recurring fees
- Fee revision history

#### Billing
- Generate student bills
- Automatic bill generation based on fee structure
- View bill history
- Print bills and receipts

#### Payments
- Record fee payments
- Multiple payment modes (cash, card, online)
- Partial payment support
- Payment receipts
- Outstanding fee tracking

#### Scholarships
- Manage scholarship programs
- Award scholarships to students
- Track scholarship disbursements
- Scholarship reports

### 9. Communication

#### Messaging System
- Send messages to students, teachers, or parents
- Group messaging
- Message history
- Notification alerts

#### Notifications
- System announcements
- Event notifications
- Payment reminders
- Attendance alerts

### 10. Reports & Analytics

#### Academic Reports
- Class performance reports
- Subject-wise analysis
- Student progress reports
- Year-over-year comparisons

#### Financial Reports
- Fee collection reports
- Outstanding dues reports
- Revenue analysis
- Scholarship distribution reports

#### Attendance Reports
- Monthly/Yearly summaries
- Defaulter lists
- Trend analysis

## Navigation Guide

### Main Menu Sections

1. **Dashboard** - System overview and quick actions
2. **Students** - Student management
3. **Teachers** - Teacher management
4. **Academic** - Academic configuration
5. **Attendance** - Attendance tracking
6. **Exams** - Examination management
7. **Finance** - Fee and payment management
8. **Messages** - Communication center
9. **Users** - System user management
10. **Settings** - System configuration
11. **Profile** - Personal profile settings

### Common Actions

- **Search**: Use the search bar in tables to find records
- **Filter**: Apply filters to narrow down results
- **Export**: Export data to Excel/CSV where available
- **Print**: Print-friendly views for reports
- **Bulk Actions**: Perform actions on multiple records

## Quick Actions from Dashboard

1. **Add New Student** - Quick student registration
2. **Mark Attendance** - Go to daily attendance
3. **Create Exam** - Set up new examination
4. **Generate Bill** - Create student bill
5. **Send Message** - Compose new message

## Creating Users

Users in Enlightbook represent anyone who needs access to the system - administrators, teachers, students, accountants, and other staff members.

**Prerequisites:** You must be logged in as an administrator (Master Admin, Principal, or Coordinator role) to create users.

### How to Create a User

1. **Navigate to Users**
   - Go to **Users** in the main sidebar menu
   - Or click **"Add User"** from the Dashboard Quick Actions

2. **Click "Add User"**
   - Click the **"Add User"** button in the top-right corner

3. **Fill in Account Information**
   - **Username**: Unique login username (required)
   - **Email**: Valid email address (required)
   - **Password**: Create a secure password (required)
   - **Confirm Password**: Re-enter the password (required)

4. **Fill in Personal Information**
   - **First Name**: User's first name
   - **Last Name**: User's last name
   - **Phone Number**: Contact number

5. **Assign Roles**
   Select one or more roles for the user:
   - **Master Admin**: Full system access and control
   - **Principal**: School administration and oversight
   - **Coordinator**: Academic coordination and scheduling
   - **Teacher**: Teaching staff access (classes, attendance, results)
   - **Student**: Student access (view profile, results, attendance)
   - **Accountant**: Finance management (fees, payments, scholarships)
   - **Driver**: Transportation management

6. **Create User**
   - Click **"Create User"** to save
   - The user can now log in with their username and password

### User Roles Explained

| Role | Access Level | Typical Users |
|------|--------------|---------------|
| **Master Admin** | Full access to all features | System administrators, IT staff |
| **Principal** | Administrative oversight | School principal, vice principal |
| **Coordinator** | Academic management | Academic coordinators, department heads |
| **Teacher** | Class management, attendance, results | Teaching staff |
| **Student** | View-only personal data | Enrolled students |
| **Accountant** | Financial management | Finance department |
| **Driver** | Transport management | Bus drivers, transport staff |

### Managing Users

Once users are created, you can:
- **Edit User**: Click the menu icon → Edit to update information
- **Activate/Deactivate**: Toggle user status to enable/disable login
- **Delete User**: Permanently remove a user account
- **View Statistics**: See total users, active users, teachers, and students on the Users page

### Best Practices

- Create accounts for teachers so they can manage attendance and enter exam results
- Use descriptive usernames (e.g., `john.smith`, `teacher_001`)
- Assign multiple roles if needed (e.g., a teacher who also coordinates)
- Deactivate accounts instead of deleting for users who may return
- Ensure strong passwords for admin accounts

## Tips for Users

### For Administrators
- Start by configuring Academic Years before adding classes
- Set up Fee Structures before generating bills
- Create user accounts for teachers to access the system
- Regular backup of data is recommended

### For Teachers
- Use period attendance for subject-wise tracking
- Enter exam results promptly after exams
- Check messages regularly for announcements
- Keep student contact information updated

### For Staff
- Verify fee payments before marking them complete
- Double-check attendance data before finalizing
- Use bulk operations to save time
- Generate reports at month-end for records

## Keyboard Shortcuts

- `Ctrl + K` - Open command palette (if available)
- `Ctrl + S` - Save form (in edit mode)
- `Esc` - Close modals/dialogs
- `Tab` - Navigate between form fields

## Mobile Access

The system is responsive and can be accessed on mobile devices. Key features available on mobile:
- View dashboard and statistics
- Mark attendance
- View student/teacher profiles
- Send and receive messages
- View reports (read-only)

## Support & Help

For technical support or feature requests, contact the system administrator.

## System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Recommended screen resolution: 1920x1080 or higher
- JavaScript enabled

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-15

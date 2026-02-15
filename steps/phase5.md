# Phase 5: Attendance Management System

## Summary

Phase 5 implements a comprehensive attendance management system for EnlightBook, including daily attendance tracking, period-wise attendance, leave management, attendance policies, and detailed analytics with parent notifications.

**Status**: ✅ **COMPLETE**

---

## What Was Built

### 1. Backend (Django)

#### Models Created

**`apps/attendance/models.py`** (8 models, ~700 lines)

1. **AttendancePeriod** - School periods/sessions
   - Name, start/end times
   - Ordering for period sequence
   - Active/inactive status

2. **DailyAttendance** - Daily attendance tracking
   - Status: present, absent, late, excused, half_day, early_departure
   - Check-in/out times
   - Leave application integration
   - Recorded by teacher

3. **PeriodAttendance** - Period-wise attendance
   - Links to specific periods and subjects
   - Class and section tracking
   - Status: present, absent, late

4. **LeaveApplication** - Leave management
   - Types: sick, personal, family, medical, sports, academic, other
   - Date range with auto-calculation of days
   - Approval workflow (pending, approved, rejected, cancelled)
   - Auto-mark attendance on approval
   - Supporting documents

5. **AttendanceSummary** - Cached statistics
   - Monthly summaries per student
   - Working days and attendance counts
   - Attendance percentage
   - Performance optimization

6. **AttendancePolicy** - Attendance policies
   - Class-specific minimum percentage
   - Grace days allowance
   - Consecutive absence alerts
   - Compliance checking

7. **AttendanceNotification** - Parent/teacher notifications
   - Types: absence, low attendance, consecutive absence, late arrival
   - Multi-recipient support
   - Read tracking

8. **HolidayCalendar** - School holidays
   - Types: national, school, exam, event, vacation
   - Single and multi-day holidays
   - Monthly views

#### Serializers Created

**`apps/attendance/serializers.py`** (18+ serializers, ~400 lines)

- **AttendancePeriodSerializer**
- **DailyAttendanceListSerializer** / **DailyAttendanceDetailSerializer** / **DailyAttendanceCreateSerializer**
- **BulkAttendanceSerializer**
- **PeriodAttendanceSerializer** / **PeriodAttendanceCreateSerializer**
- **LeaveApplicationListSerializer** / **LeaveApplicationDetailSerializer** / **LeaveApplicationCreateSerializer**
- **AttendanceSummarySerializer**
- **AttendancePolicySerializer**
- **AttendanceNotificationSerializer**
- **HolidayCalendarSerializer**
- **AttendanceStatisticsSerializer**
- **StudentAttendanceDetailSerializer**
- **DefaulterListSerializer**

#### Views Created

**`apps/attendance/views.py`** (9 ViewSets, ~600 lines)

- **AttendancePeriodViewSet** - Period management

- **DailyAttendanceViewSet**
  - Full CRUD operations
  - `bulk_mark` action - Mark attendance for entire class
  - `by_class` action - Get class attendance for date
  - `by_student` action - Get student attendance history

- **PeriodAttendanceViewSet**
  - Full CRUD operations
  - `bulk_mark` action - Period-wise bulk entry

- **LeaveApplicationViewSet**
  - Full CRUD operations
  - `approve` action - Approve with auto-mark attendance
  - `reject` action - Reject application
  - `my_leaves` action - Get user's leaves

- **AttendanceSummaryViewSet**
  - Read-only summaries
  - `by_student` action - Get student summaries
  - `calculate` action - Recalculate statistics

- **AttendancePolicyViewSet** - Policy management

- **AttendanceNotificationViewSet**
  - Full CRUD
  - `mark_read` action
  - `unread` action

- **HolidayCalendarViewSet**
  - Full CRUD
  - `upcoming` action
  - `by_month` action

- **AttendanceReportViewSet**
  - `statistics` action - Generate stats
  - `defaulters` action - Low attendance list
  - `student_detail` action - Detailed report

#### Admin Configuration

**`apps/attendance/admin.py`** (~100 lines)

- **AttendancePeriodAdmin**
- **DailyAttendanceAdmin**
- **PeriodAttendanceAdmin**
- **LeaveApplicationAdmin**
- **AttendanceSummaryAdmin**
- **AttendancePolicyAdmin**
- **AttendanceNotificationAdmin**
- **HolidayCalendarAdmin**

#### URLs

**`apps/attendance/urls.py`** - 9 viewsets, 50+ endpoints:

```
# Attendance Periods
GET    /api/attendance/periods/
POST   /api/attendance/periods/
GET    /api/attendance/periods/{id}/
PATCH  /api/attendance/periods/{id}/
DELETE /api/attendance/periods/{id}/

# Daily Attendance
GET    /api/attendance/daily/?student=2&date=2024-12-01
POST   /api/attendance/daily/
GET    /api/attendance/daily/{id}/
PATCH  /api/attendance/daily/{id}/
DELETE /api/attendance/daily/{id}/
POST   /api/attendance/daily/bulk_mark/
GET    /api/attendance/daily/by_class/?school_class_id=1&date=2024-12-01
GET    /api/attendance/daily/by_student/?student_id=2

# Period Attendance
GET    /api/attendance/period-wise/
POST   /api/attendance/period-wise/
GET    /api/attendance/period-wise/{id}/
PATCH  /api/attendance/period-wise/{id}/
DELETE /api/attendance/period-wise/{id}/
POST   /api/attendance/period-wise/bulk_mark/

# Leave Applications
GET    /api/attendance/leaves/
POST   /api/attendance/leaves/
GET    /api/attendance/leaves/{id}/
PATCH  /api/attendance/leaves/{id}/
DELETE /api/attendance/leaves/{id}/
POST   /api/attendance/leaves/{id}/approve/
POST   /api/attendance/leaves/{id}/reject/
GET    /api/attendance/leaves/my_leaves/

# Attendance Summaries
GET    /api/attendance/summaries/
GET    /api/attendance/summaries/{id}/
GET    /api/attendance/summaries/by_student/?student_id=2
POST   /api/attendance/summaries/calculate/

# Attendance Policies
GET    /api/attendance/policies/
POST   /api/attendance/policies/
GET    /api/attendance/policies/{id}/
PATCH  /api/attendance/policies/{id}/
DELETE /api/attendance/policies/{id}/

# Attendance Notifications
GET    /api/attendance/notifications/
POST   /api/attendance/notifications/
GET    /api/attendance/notifications/{id}/
PATCH  /api/attendance/notifications/{id}/
DELETE /api/attendance/notifications/{id}/
POST   /api/attendance/notifications/{id}/mark_read/
GET    /api/attendance/notifications/unread/

# Holiday Calendar
GET    /api/attendance/holidays/
POST   /api/attendance/holidays/
GET    /api/attendance/holidays/{id}/
PATCH  /api/attendance/holidays/{id}/
DELETE /api/attendance/holidays/{id}/
GET    /api/attendance/holidays/upcoming/
GET    /api/attendance/holidays/by_month/?year=2024&month=12

# Attendance Reports
POST   /api/attendance/reports/statistics/
GET    /api/attendance/reports/defaulters/?threshold=75
GET    /api/attendance/reports/student_detail/?student_id=2
```

### 2. Frontend (Next.js)

#### API Client

**`lib/api-attendance.ts`** (8 API modules, ~350 lines)

- **attendancePeriodApi** - 5 methods
- **dailyAttendanceApi** - 8 methods
- **periodAttendanceApi** - 6 methods
- **leaveApplicationApi** - 8 methods
- **attendanceSummaryApi** - 4 methods
- **attendancePolicyApi** - 5 methods
- **attendanceNotificationApi** - 6 methods
- **holidayCalendarApi** - 7 methods
- **attendanceReportApi** - 3 methods

---

## What You Need To Do

### Prerequisites

- ✅ Phases 0, 1, 2, 3, 4 completed
- ✅ Docker running
- ✅ Database migrated through Phase 4

---

### Step 1: Run Database Migrations

```bash
docker-compose exec backend python manage.py makemigrations attendance
docker-compose exec backend python manage.py migrate
```

**Expected output:**
```
Migrations for 'attendance':
  apps/attendance/migrations/0001_initial.py
    - Create model AttendancePeriod
    - Create model DailyAttendance
    - Create model PeriodAttendance
    - Create model LeaveApplication
    - Create model AttendanceSummary
    - Create model AttendancePolicy
    - Create model AttendanceNotification
    - Create model HolidayCalendar

Running migrations:
  Applying attendance.0001_initial... OK
```

---

### Step 2: Create Initial Attendance Periods

```bash
docker-compose exec backend python manage.py shell
```

```python
from apps.attendance.models import AttendancePeriod

# Create periods for a typical school day
periods = [
    ('Period 1', '08:00:00', '08:45:00', 1),
    ('Period 2', '08:45:00', '09:30:00', 2),
    ('Period 3', '09:30:00', '10:15:00', 3),
    ('Break', '10:15:00', '10:30:00', 4),
    ('Period 4', '10:30:00', '11:15:00', 5),
    ('Period 5', '11:15:00', '12:00:00', 6),
    ('Lunch', '12:00:00', '12:45:00', 7),
    ('Period 6', '12:45:00', '13:30:00', 8),
    ('Period 7', '13:30:00', '14:15:00', 9),
    ('Period 8', '14:15:00', '15:00:00', 10),
]

for name, start, end, order in periods:
    AttendancePeriod.objects.create(
        name=name,
        start_time=start,
        end_time=end,
        order=order
    )

print("Attendance periods created!")
exit()
```

---

### Step 3: Create Attendance Policy

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"AdminPass123!"}' | jq -r '.access')

# Create policy for Class 10
curl -X POST http://localhost:8000/api/attendance/policies/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "school_class": 1,
    "minimum_percentage": "75.00",
    "grace_days": 5,
    "consecutive_absence_alert": 3
  }'
```

---

### Step 4: Mark Daily Attendance

#### Bulk Mark for Class

```bash
curl -X POST http://localhost:8000/api/attendance/daily/bulk_mark/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "school_class_id": 1,
    "section_id": 1,
    "date": "2024-12-01",
    "attendance_data": [
      {
        "student_id": 2,
        "status": "present",
        "check_in_time": "08:00:00"
      },
      {
        "student_id": 3,
        "status": "late",
        "check_in_time": "08:15:00"
      },
      {
        "student_id": 4,
        "status": "absent"
      }
    ]
  }'
```

---

### Step 5: Create and Approve Leave

```bash
# Apply for leave
curl -X POST http://localhost:8000/api/attendance/leaves/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type": "sick",
    "start_date": "2024-12-05",
    "end_date": "2024-12-06",
    "reason": "Fever and cold"
  }'

# Approve leave (as principal)
curl -X POST http://localhost:8000/api/attendance/leaves/1/approve/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "remarks": "Approved. Take rest."
  }'
```

---

### Step 6: Calculate Attendance Summary

```bash
curl -X POST http://localhost:8000/api/attendance/summaries/calculate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 2,
    "year": 2024,
    "month": 12
  }'
```

---

### Step 7: Generate Reports

#### Get Attendance Statistics

```bash
curl -X POST http://localhost:8000/api/attendance/reports/statistics/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "school_class_id": 1,
    "start_date": "2024-12-01",
    "end_date": "2024-12-31"
  }'
```

#### Get Defaulters List

```bash
curl "http://localhost:8000/api/attendance/reports/defaulters/?threshold=75" \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Student Detail

```bash
curl "http://localhost:8000/api/attendance/reports/student_detail/?student_id=2" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Step 8: Add Holidays

```bash
curl -X POST http://localhost:8000/api/attendance/holidays/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Christmas Holiday",
    "date": "2024-12-25",
    "holiday_type": "national",
    "description": "Christmas Day"
  }'
```

---

## Features Implemented

✅ **Daily Attendance:**
- 6 status types: present, absent, late, excused, half_day, early_departure
- Check-in/out time tracking
- Bulk marking for entire class
- Individual student history

✅ **Period-wise Attendance:**
- Subject-specific attendance
- Multiple periods per day
- Teacher-specific recording
- Bulk entry support

✅ **Leave Management:**
- 7 leave types
- Date range applications
- Approval workflow
- Auto-mark attendance on approval
- Supporting documents

✅ **Attendance Policies:**
- Class-specific minimum percentage
- Grace days
- Consecutive absence alerts
- Compliance tracking

✅ **Summaries & Reports:**
- Monthly cached summaries
- Attendance percentage calculation
- Defaulter identification
- Detailed student reports
- Statistics and trends

✅ **Notifications:**
- Absence alerts
- Low attendance warnings
- Consecutive absence alerts
- Late arrival notifications
- Multi-recipient support

✅ **Holiday Calendar:**
- 5 holiday types
- Multi-day holidays
- Upcoming holidays view
- Monthly calendar

---

## Verification Checklist

Before moving to Phase 6, verify:

- [ ] Migrations applied successfully
- [ ] Attendance periods created
- [ ] Can mark daily attendance individually
- [ ] Can bulk mark attendance for class
- [ ] Can mark period-wise attendance
- [ ] Can apply for leave
- [ ] Can approve/reject leave
- [ ] Leave approval auto-marks attendance
- [ ] Attendance summaries calculate correctly
- [ ] Attendance policies work
- [ ] Can generate statistics report
- [ ] Defaulters list shows low attendance
- [ ] Student detail report works
- [ ] Can add holidays
- [ ] All API endpoints in Swagger docs

---

## What's Next (Phase 6)

Once Phase 5 is verified, proceed to **Phase 6: Communication System**:

### Phase 6 Will Build:
1. Internal messaging system
2. Announcements and broadcasts
3. Discussion forums
4. File sharing
5. Notification system
6. Parent-teacher communication

### Skills Needed:
- Real-time messaging
- File upload handling
- Broadcast notifications
- Threaded discussions

---

## Troubleshooting

### Issue: "Attendance already recorded"

**Solution:** Use update (PATCH) instead of create (POST) to modify existing attendance.

### Issue: "Leave approval not marking attendance"

**Solution:** Ensure `auto_mark_attendance` is True on the leave application.

### Issue: "Attendance percentage incorrect"

**Solution:** Run summary recalculation:
```python
summary = AttendanceSummary.objects.get(student_id=2, month='2024-12-01')
summary.recalculate()
```

### Issue: "Bulk attendance fails"

**Solution:** Check that:
- All student IDs are valid
- Status values are valid choices
- Date format is YYYY-MM-DD

### Issue: "Notifications not created"

**Solution:** Notifications need to be created manually or triggered by specific actions. Check the notification type and recipient settings.

---

**Ready to proceed?** Once you've verified all attendance features work correctly, we can begin **Phase 6: Communication System**! 📨

# Autoshkolla-Pro API Reference

## Overview

This document provides complete reference for all API endpoints in the autoshkolla-pro system. All endpoints follow REST principles and return JSON responses unless otherwise specified.

**Base URL**: `/api/v1`

**Authentication**: All endpoints (except login) require JWT token in `Authorization: Bearer <token>` header

**Multi-Tenancy**: All endpoints automatically filter by `tenant_id` from authenticated user context

**Response Envelope**: All responses wrapped in `{"success": true, "data": ...}` format

---

## 1. Auth Module

Authentication and user session management endpoints.

### Login
- **Method**: POST
- **Path**: `/auth/login`
- **Authentication**: None
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "token_string_uuid",
    "expires_in": 900,
    "user_id": "uuid",
    "tenant_id": "uuid",
    "name": "User Name",
    "role": "administrator",
    "email": "user@example.com"
  }
  ```

### Refresh Token
- **Method**: POST
- **Path**: `/auth/refresh`
- **Authentication**: Required (but not validated, refresh token used instead)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "refresh_token": "token_string_uuid"
  }
  ```
- **Response** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "new_token_string_uuid",
    "expires_in": 900
  }
  ```

### Logout
- **Method**: POST
- **Path**: `/auth/logout`
- **Authentication**: Required
- **Status**: Not Implemented
- **Request Body**: None
- **Response** (200):
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

### Get Current User
- **Method**: GET
- **Path**: `/auth/me`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**: None
- **Response** (200):
  ```json
  {
    "user_id": "uuid",
    "email": "user@example.com",
    "tenant_id": "uuid",
    "name": "User Name",
    "role": "administrator",
    "active": true,
    "created_at": "2026-03-09T10:00:00Z"
  }
  ```

### Impersonate Tenant (Super-Admin Only)
- **Method**: POST
- **Path**: `/auth/impersonate`
- **Authentication**: Required (super_admin only)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "target_tenant_id": "uuid"
  }
  ```
- **Response** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 900,
    "is_impersonating": true,
    "target_tenant_id": "uuid"
  }
  ```

### Exit Impersonation (Super-Admin Only)
- **Method**: POST
- **Path**: `/auth/exit-impersonate`
- **Authentication**: Required (super_admin only)
- **Status**: Not Implemented
- **Request Body**: None
- **Response** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 900,
    "is_impersonating": false
  }
  ```

---

## 2. Locations Module

Geographic location hierarchy endpoints (countries, municipalities, places).

### Get All Countries
- **Method**: GET
- **Path**: `/locations/countries`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**: None
- **Response** (200):
  ```json
  {
    "data": [
      {
        "country_id": "uuid",
        "name": "Kosova",
        "code": "XK"
      }
    ],
    "total": 1
  }
  ```

### Get Municipalities by Country
- **Method**: GET
- **Path**: `/locations/municipalities`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `country_id` (string, required): UUID of country
- **Response** (200):
  ```json
  {
    "data": [
      {
        "municipality_id": "uuid",
        "name": "Prishtina",
        "country_id": "uuid"
      }
    ],
    "total": 30
  }
  ```

### Get Places by Municipality
- **Method**: GET
- **Path**: `/locations/places`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `municipality_id` (string, required): UUID of municipality
- **Response** (200):
  ```json
  {
    "data": [
      {
        "place_id": "uuid",
        "name": "Pristina City Center",
        "municipality_id": "uuid"
      }
    ],
    "total": 12
  }
  ```

---

## 3. School Module

School profile and configuration management.

### Get School Profile
- **Method**: GET
- **Path**: `/school/profile`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**: None
- **Response** (200):
  ```json
  {
    "school_id": "uuid",
    "tenant_id": "uuid",
    "name": "Driving School Name",
    "address": "Street Address",
    "phone": "+383123456789",
    "email": "info@school.com",
    "registration_number": "REG12345",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-03-09T10:00:00Z"
  }
  ```

### Create School Profile
- **Method**: POST
- **Path**: `/school/profile`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "name": "Driving School Name",
    "address": "Street Address",
    "phone": "+383123456789",
    "email": "info@school.com",
    "registration_number": "REG12345"
  }
  ```
- **Response** (201): Same as Get School Profile

### Update School Profile
- **Method**: PUT
- **Path**: `/school/profile`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create School Profile
- **Response** (200): Same as Get School Profile

### Get All Licenses
- **Method**: GET
- **Path**: `/school/licenses`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**: None
- **Response** (200):
  ```json
  {
    "data": [
      {
        "license_id": "uuid",
        "category_id": "uuid",
        "license_number": "LIC-001",
        "issued_date": "2025-01-01",
        "expiry_date": "2027-01-01",
        "active": true,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 5
  }
  ```

### Create License
- **Method**: POST
- **Path**: `/school/licenses`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "category_id": "uuid",
    "license_number": "LIC-001",
    "issued_date": "2025-01-01",
    "expiry_date": "2027-01-01"
  }
  ```
- **Response** (201): Same as Get License item

### Update License
- **Method**: PUT
- **Path**: `/school/licenses/{license_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create License
- **Response** (200): Same as Get License item

### Delete License
- **Method**: DELETE
- **Path**: `/school/licenses/{license_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

---

## 4. Categories Module

Vehicle categories (B, BE, C, C1, etc.) management.

### Get All Categories
- **Method**: GET
- **Path**: `/categories`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
- **Response** (200):
  ```json
  {
    "data": [
      {
        "category_id": "uuid",
        "tenant_id": "uuid",
        "code": "B",
        "name": "Personal Vehicle",
        "min_age": 18,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 8
  }
  ```

### Create Category
- **Method**: POST
- **Path**: `/categories`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "code": "B",
    "name": "Personal Vehicle",
    "min_age": 18
  }
  ```
- **Response** (201): Same as Get Category item

### Update Category
- **Method**: PUT
- **Path**: `/categories/{category_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create Category
- **Response** (200): Same as Get Category item

### Delete Category
- **Method**: DELETE
- **Path**: `/categories/{category_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

---

## 5. Instructors Module

Driving instructors management.

### Get All Instructors
- **Method**: GET
- **Path**: `/instructors`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `active` (boolean, optional): Filter by active status
- **Response** (200):
  ```json
  {
    "data": [
      {
        "instructor_id": "uuid",
        "tenant_id": "uuid",
        "first_name": "Arben",
        "last_name": "Rama",
        "email": "arben@school.com",
        "phone": "+383123456789",
        "license_number": "DL123456",
        "categories": ["B", "C"],
        "active": true,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 8
  }
  ```

### Create Instructor
- **Method**: POST
- **Path**: `/instructors`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "first_name": "Arben",
    "last_name": "Rama",
    "email": "arben@school.com",
    "password": "initialPassword123",
    "phone": "+383123456789",
    "personal_number": "1234567890",
    "position": "instructor",
    "license_info": "DL123456",
    "cost_per_candidate": 65.00
  }
  ```
- **Notes**: When `email` and `password` are provided, a `users` record is auto-created with `role='instructor'` and linked via `instructor.user_id`. The instructor can then log in to the Instructor Portal.
- **Response** (201): Same as Get Instructor item

### Update Instructor
- **Method**: PUT
- **Path**: `/instructors/{instructor_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create Instructor
- **Response** (200): Same as Get Instructor item

### Delete Instructor
- **Method**: DELETE
- **Path**: `/instructors/{instructor_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

### Get Instructor Candidates
- **Method**: GET
- **Path**: `/instructors/{instructor_id}/candidates`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
- **Response** (200):
  ```json
  {
    "data": [
      {
        "candidate_id": "uuid",
        "first_name": "Fatmir",
        "last_name": "Gashi",
        "category": "B",
        "status": "active"
      }
    ],
    "total": 12
  }
  ```

### Get Instructor Debt Summary
- **Method**: GET
- **Path**: `/instructors/{instructor_id}/debt-summary`
- **Authentication**: Required (administrator, or self if instructor)
- **Status**: Not Implemented
- **Response** (200):
  ```json
  {
    "instructor_id": "uuid",
    "instructor_name": "Arben Rama",
    "total_candidates": 12,
    "total_amount_owed": 780.00,
    "total_amount_paid": 520.00,
    "outstanding_balance": 260.00,
    "cost_per_candidate": 65.00
  }
  ```

### Get Instructor Payments
- **Method**: GET
- **Path**: `/instructors/{instructor_id}/payments`
- **Authentication**: Required (administrator, or self if instructor)
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `status` (string, optional): Filter by 'unpaid', 'partial', 'paid'
- **Response** (200):
  ```json
  {
    "data": [
      {
        "payment_id": "uuid",
        "instructor_id": "uuid",
        "candidate_id": "uuid",
        "candidate_name": "Fatmir Gashi",
        "amount": 65.00,
        "amount_paid": 65.00,
        "status": "paid",
        "payment_date": "2026-03-01",
        "payment_method": "cash",
        "created_at": "2026-02-15T10:00:00Z"
      }
    ],
    "total": 12
  }
  ```

### Record Instructor Payment
- **Method**: POST
- **Path**: `/instructors/{instructor_id}/payments`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "candidate_id": "uuid",
    "amount": 65.00,
    "payment_method": "cash",
    "remarks": "Monthly payment"
  }
  ```
- **Response** (201): Same as Get Instructor Payments item

---

## 5b. Instructor Self-Service Portal

Endpoints for instructors accessing their own data after login. All use `g.current_user` to identify the instructor.

### Get My Instructor Profile
- **Method**: GET
- **Path**: `/instructor/me`
- **Authentication**: Required (instructor role)
- **Status**: Not Implemented
- **Response** (200):
  ```json
  {
    "instructor_id": "uuid",
    "first_name": "Arben",
    "last_name": "Rama",
    "email": "arben@school.com",
    "phone": "+383123456789",
    "position": "instructor",
    "hours_realized": 150,
    "active_candidates_count": 8,
    "outstanding_debt": 260.00
  }
  ```

### Get My Candidates (Read-Only)
- **Method**: GET
- **Path**: `/instructor/candidates`
- **Authentication**: Required (instructor role)
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
- **Response** (200):
  ```json
  {
    "data": [
      {
        "candidate_id": "uuid",
        "first_name": "Fatmir",
        "last_name": "Gashi",
        "category": "B",
        "phone": "+383123456789",
        "registration_date": "2026-02-01",
        "practical_hours_completed": 12,
        "practical_hours_total": 20,
        "theory_hours_completed": 16,
        "theory_hours_total": 20,
        "amount_paid": 250.00,
        "total_price": 350.00
      }
    ],
    "total": 8
  }
  ```
- **Note**: Instructors can ONLY see candidates assigned to them. No create/edit/delete access.

### Get My Calendar
- **Method**: GET
- **Path**: `/instructor/calendar`
- **Authentication**: Required (instructor role)
- **Status**: Not Implemented
- **Query Parameters**:
  - `date_from` (string, required): ISO date
  - `date_to` (string, required): ISO date
- **Response** (200):
  ```json
  {
    "data": [
      {
        "lesson_id": "uuid",
        "candidate_id": "uuid",
        "candidate_name": "Fatmir Gashi",
        "vehicle_plate": "AA-123-BC",
        "scheduled_date": "2026-03-10",
        "start_time": "09:00",
        "end_time": "10:00",
        "status": "scheduled",
        "notes": "Highway driving practice"
      }
    ],
    "total": 15
  }
  ```

### Get My Debt Summary
- **Method**: GET
- **Path**: `/instructor/debt`
- **Authentication**: Required (instructor role)
- **Status**: Not Implemented
- **Response** (200): Same as Get Instructor Debt Summary

### Get My Dashboard Stats
- **Method**: GET
- **Path**: `/instructor/dashboard`
- **Authentication**: Required (instructor role)
- **Status**: Not Implemented
- **Response** (200):
  ```json
  {
    "active_candidates": 8,
    "lessons_today": 3,
    "lessons_this_week": 12,
    "outstanding_debt": 260.00,
    "unread_messages": 2,
    "hours_this_month": 45,
    "upcoming_lessons": [
      {
        "lesson_id": "uuid",
        "candidate_name": "Fatmir Gashi",
        "start_time": "09:00",
        "end_time": "10:00"
      }
    ]
  }
  ```

---

## 5c. Calendar / Lesson Scheduling

Practical lesson scheduling for instructors and candidates.

### Get Scheduled Lessons
- **Method**: GET
- **Path**: `/scheduled-lessons`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `instructor_id` (string, optional): Filter by instructor
  - `candidate_id` (string, optional): Filter by candidate
  - `date_from` (string, optional): ISO date
  - `date_to` (string, optional): ISO date
  - `status` (string, optional): 'scheduled', 'completed', 'cancelled', 'no_show'
- **Response** (200):
  ```json
  {
    "data": [
      {
        "lesson_id": "uuid",
        "instructor_id": "uuid",
        "instructor_name": "Arben Rama",
        "candidate_id": "uuid",
        "candidate_name": "Fatmir Gashi",
        "vehicle_id": "uuid",
        "vehicle_plate": "AA-123-BC",
        "scheduled_date": "2026-03-10",
        "start_time": "09:00",
        "end_time": "10:00",
        "status": "scheduled",
        "notes": "Highway driving"
      }
    ],
    "total": 30
  }
  ```

### Create Scheduled Lesson
- **Method**: POST
- **Path**: `/scheduled-lessons`
- **Authentication**: Required (administrator, instructor)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "instructor_id": "uuid",
    "candidate_id": "uuid",
    "vehicle_id": "uuid",
    "scheduled_date": "2026-03-10",
    "start_time": "09:00",
    "end_time": "10:00",
    "notes": "Highway driving practice"
  }
  ```
- **Response** (201): Same as lesson item

### Update Scheduled Lesson
- **Method**: PUT
- **Path**: `/scheduled-lessons/{lesson_id}`
- **Authentication**: Required (administrator, instructor)
- **Status**: Not Implemented
- **Request Body**: Same as Create
- **Response** (200): Same as lesson item

### Cancel Scheduled Lesson
- **Method**: DELETE
- **Path**: `/scheduled-lessons/{lesson_id}`
- **Authentication**: Required (administrator, instructor)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "cancelled_reason": "Student unavailable"
  }
  ```
- **Response** (200):
  ```json
  {
    "lesson_id": "uuid",
    "status": "cancelled",
    "cancelled_reason": "Student unavailable"
  }
  ```

### Complete Scheduled Lesson
- **Method**: POST
- **Path**: `/scheduled-lessons/{lesson_id}/complete`
- **Authentication**: Required (administrator, instructor)
- **Status**: Not Implemented
- **Notes**: Auto-creates a `practical_hour_sessions` record and links it
- **Response** (200):
  ```json
  {
    "lesson_id": "uuid",
    "status": "completed",
    "practical_session_id": "uuid"
  }
  ```

---

## 5d. Messaging (Instructor ↔ Admin Communication)

Threaded messaging between instructors and school administrators.

### Get Conversations
- **Method**: GET
- **Path**: `/conversations`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
- **Response** (200):
  ```json
  {
    "data": [
      {
        "conversation_id": "uuid",
        "subject": "Schedule change request",
        "participants": [
          {"user_id": "uuid", "name": "Arben Rama", "role": "instructor"},
          {"user_id": "uuid", "name": "Admin User", "role": "administrator"}
        ],
        "last_message": "Can we reschedule Monday's lessons?",
        "last_message_at": "2026-03-09T14:30:00Z",
        "unread_count": 2
      }
    ],
    "total": 5
  }
  ```

### Create Conversation
- **Method**: POST
- **Path**: `/conversations`
- **Authentication**: Required
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "subject": "Schedule change request",
    "recipient_id": "uuid",
    "initial_message": "Can we reschedule Monday's lessons?"
  }
  ```
- **Response** (201): Same as conversation item

### Get Conversation Messages
- **Method**: GET
- **Path**: `/conversations/{conversation_id}/messages`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
- **Response** (200):
  ```json
  {
    "data": [
      {
        "message_id": "uuid",
        "sender_id": "uuid",
        "sender_name": "Arben Rama",
        "content": "Can we reschedule Monday's lessons?",
        "is_read": true,
        "created_at": "2026-03-09T14:30:00Z"
      }
    ],
    "total": 8
  }
  ```

### Send Message
- **Method**: POST
- **Path**: `/conversations/{conversation_id}/messages`
- **Authentication**: Required
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "content": "Yes, we can move it to Wednesday."
  }
  ```
- **Response** (201): Same as message item

### Mark Conversation as Read
- **Method**: PUT
- **Path**: `/conversations/{conversation_id}/read`
- **Authentication**: Required (must be participant)
- **Status**: Implemented
- **Description**: Marks all unread messages in a conversation as read for the current user (messages not sent by the current user)
- **Response** (200):
  ```json
  {
    "count": 3
  }
  ```

### Mark Message as Read
- **Method**: PUT
- **Path**: `/messages/{message_id}/read`
- **Authentication**: Required
- **Status**: Implemented
- **Response** (200):
  ```json
  {
    "id": "uuid",
    "conversationId": "uuid",
    "senderId": "uuid",
    "senderName": "Emri Mbiemri",
    "sender": { "id": "uuid", "fullName": "Emri Mbiemri", "role": "administrator" },
    "content": "...",
    "isRead": true,
    "readAt": "2026-03-09T15:00:00",
    "createdAt": "2026-03-09T14:30:00"
  }
  ```

### Get Unread Message Count
- **Method**: GET
- **Path**: `/messages/unread-count`
- **Authentication**: Required
- **Status**: Implemented
- **Response** (200):
  ```json
  {
    "unreadCount": 3
  }
  ```

---

## 5e. Admin Dashboard

Dashboard statistics and data for the admin dashboard.

### Get Dashboard Stats
- **Method**: GET
- **Path**: `/dashboard/stats`
- **Authentication**: Required (administrator)
- **Status**: Implemented
- **Response** (200):
  ```json
  {
    "totalCandidates": 55,
    "activeCandidates": 45,
    "archivedCandidates": 10,
    "activeCandidatesTrend": 5,
    "totalRevenue": 45000.00,
    "monthlyRevenue": 12500.00,
    "monthlyRevenueTrend": 8.5,
    "pendingPayments": 8750.00,
    "practicalHoursToday": 12,
    "instructorTotalDebt": 1560.00,
    "recentCandidates": [
      {
        "id": "uuid",
        "fullName": "Arta Berisha",
        "registrationDate": "2026-03-10",
        "categoryCode": "B",
        "isArchived": false
      }
    ]
  }
  ```

### Get Revenue Chart Data
- **Method**: GET
- **Path**: `/dashboard/revenue-chart`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Query Parameters**:
  - `months` (integer, optional): Default 6
- **Response** (200):
  ```json
  {
    "data": [
      {"month": "2025-10", "revenue": 9800.00, "target": 10000.00},
      {"month": "2025-11", "revenue": 11200.00, "target": 10000.00}
    ]
  }
  ```

### Get Category Breakdown
- **Method**: GET
- **Path**: `/dashboard/category-breakdown`
- **Authentication**: Required (administrator)
- **Status**: Implemented
- **Response** (200):
  ```json
  {
    "data": [
      {"category": "B", "count": 35, "percentage": 77.8},
      {"category": "C", "count": 5, "percentage": 11.1},
      {"category": "CE", "count": 3, "percentage": 6.7},
      {"category": "D", "count": 2, "percentage": 4.4}
    ]
  }
  ```

### Get Today's Schedule
- **Method**: GET
- **Path**: `/dashboard/today-schedule`
- **Authentication**: Required (administrator)
- **Status**: Implemented
- **Response** (200):
  ```json
  {
    "data": [
      {
        "lesson_id": "uuid",
        "start_time": "09:00",
        "end_time": "10:00",
        "instructor_name": "Arben Rama",
        "candidate_name": "Fatmir Gashi",
        "vehicle_plate": "AA-123-BC",
        "status": "scheduled"
      }
    ],
    "total": 12
  }
  ```

### Get Recent Activity
- **Method**: GET
- **Path**: `/dashboard/recent-activity`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 10
- **Response** (200):
  ```json
  {
    "data": [
      {
        "activity_id": "uuid",
        "action": "candidate_registered",
        "description": "Fatmir Gashi u regjistrua në kategorinë B",
        "user_name": "Admin",
        "created_at": "2026-03-09T10:30:00Z"
      }
    ]
  }
  ```

### Get Dashboard Alerts
- **Method**: GET
- **Path**: `/dashboard/alerts`
- **Authentication**: Required (administrator)
- **Status**: Implemented
- **Response** (200):
  ```json
  {
    "expiring_registrations": [
      {"vehicle_plate": "AA-123-BC", "expiry_date": "2026-04-01", "days_remaining": 23}
    ],
    "expiring_licenses": [
      {"license_code": "R-561-05-B/25", "expiry_date": "2026-05-01", "days_remaining": 53}
    ],
    "overdue_payments": [
      {"candidate_name": "Fatmir Gashi", "amount_due": 100.00, "days_overdue": 35}
    ],
    "instructor_high_debt": [
      {"instructor_name": "Arben Rama", "outstanding": 390.00}
    ]
  }
  ```

---

## 6. Vehicles Module

Vehicle management for practical training.

### Get All Vehicles
- **Method**: GET
- **Path**: `/vehicles`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `active` (boolean, optional): Filter by active status
  - `instructor_id` (string, optional): Filter by instructor
- **Response** (200):
  ```json
  {
    "data": [
      {
        "vehicle_id": "uuid",
        "tenant_id": "uuid",
        "plate_number": "AA-123-BC",
        "model": "Opel Astra",
        "category": "B",
        "instructor_id": "uuid",
        "registration_date": "2025-01-01",
        "active": true,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 5
  }
  ```

### Create Vehicle
- **Method**: POST
- **Path**: `/vehicles`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "plate_number": "AA-123-BC",
    "model": "Opel Astra",
    "category": "B",
    "instructor_id": "uuid",
    "registration_date": "2025-01-01"
  }
  ```
- **Response** (201): Same as Get Vehicle item

### Update Vehicle
- **Method**: PUT
- **Path**: `/vehicles/{vehicle_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create Vehicle
- **Response** (200): Same as Get Vehicle item

### Delete Vehicle
- **Method**: DELETE
- **Path**: `/vehicles/{vehicle_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

---

## 7. Candidates Module

Candidate management (students enrolled in driving courses).

### Get All Candidates
- **Method**: GET
- **Path**: `/candidates`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `category` (string, optional): Filter by category code
  - `status` (string, optional): Filter by status (active, archived, completed)
  - `search` (string, optional): Search by name or email
  - `instructor_id` (string, optional): Filter by assigned instructor
- **Response** (200):
  ```json
  {
    "data": [
      {
        "candidate_id": "uuid",
        "first_name": "Fatmir",
        "last_name": "Gashi",
        "email": "fatmir@example.com",
        "phone": "+383123456789",
        "category": "B",
        "status": "active",
        "instructors": ["uuid"],
        "vehicles": ["uuid"],
        "theory_hours_completed": 30,
        "practical_hours_completed": 40,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 45
  }
  ```

### Create Candidate
- **Method**: POST
- **Path**: `/candidates`
- **Authentication**: Required (administrator, instructor)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "first_name": "Fatmir",
    "last_name": "Gashi",
    "email": "fatmir@example.com",
    "phone": "+383123456789",
    "id_number": "ID12345678",
    "date_of_birth": "1990-05-15",
    "gender": "M",
    "country_id": "uuid",
    "municipality_id": "uuid",
    "place_id": "uuid",
    "address": "Street Address",
    "category_id": "uuid",
    "instructor_ids": ["uuid"],
    "vehicle_ids": ["uuid"]
  }
  ```
- **Response** (201): Same as Get Candidate item

### Get Candidate
- **Method**: GET
- **Path**: `/candidates/{candidate_id}`
- **Authentication**: Required
- **Status**: Not Implemented
- **Response** (200): Same as Get Candidate item in list

### Update Candidate
- **Method**: PUT
- **Path**: `/candidates/{candidate_id}`
- **Authentication**: Required (administrator, instructor)
- **Status**: Not Implemented
- **Request Body**: Same as Create Candidate
- **Response** (200): Same as Get Candidate item

### Delete Candidate
- **Method**: DELETE
- **Path**: `/candidates/{candidate_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

### Archive Candidate
- **Method**: POST
- **Path**: `/candidates/{candidate_id}/archive`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "reason": "Student requested pause"
  }
  ```
- **Response** (200):
  ```json
  {
    "candidate_id": "uuid",
    "status": "archived",
    "archived_at": "2026-03-09T10:00:00Z",
    "archive_reason": "Student requested pause"
  }
  ```

### Create Supplementary Registration
- **Method**: POST
- **Path**: `/candidates/{candidate_id}/supplementary`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "category_id": "uuid",
    "reason": "Additional category training"
  }
  ```
- **Response** (201):
  ```json
  {
    "supplementary_id": "uuid",
    "candidate_id": "uuid",
    "category_id": "uuid",
    "reason": "Additional category training",
    "registration_date": "2026-03-09T10:00:00Z"
  }
  ```

### Export Candidates (PDF)
- **Method**: GET
- **Path**: `/candidates/export/pdf`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Query Parameters**:
  - `category` (string, optional): Filter by category
  - `status` (string, optional): Filter by status
  - `date_from` (string, optional): ISO date format
  - `date_to` (string, optional): ISO date format
- **Response** (200): Binary PDF file with candidates list

### Export Candidates (Excel)
- **Method**: GET
- **Path**: `/candidates/export/excel`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Query Parameters**: Same as PDF export
- **Response** (200): Binary XLSX file with candidates list

### Export Candidates (Word)
- **Method**: GET
- **Path**: `/candidates/export/word`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Query Parameters**: Same as PDF export
- **Response** (200): Binary DOCX file with candidates list

---

## 8. Theory Hours Module

Theory training hours tracking and management.

### Get Theory Hour Sessions
- **Method**: GET
- **Path**: `/theory-hours`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `candidate_id` (string, optional): Filter by candidate
  - `date_from` (string, optional): ISO date format
  - `date_to` (string, optional): ISO date format
- **Response** (200):
  ```json
  {
    "data": [
      {
        "session_id": "uuid",
        "candidate_id": "uuid",
        "date": "2026-03-09",
        "hours": 4,
        "topic": "Traffic Rules",
        "lecturer_name": "Prof. Name",
        "evidence_path": "/path/to/evidence.pdf",
        "created_at": "2026-03-09T10:00:00Z"
      }
    ],
    "total": 30
  }
  ```

### Save Theory Hour Session
- **Method**: POST
- **Path**: `/theory-hours`
- **Authentication**: Required (lecturer)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "candidate_id": "uuid",
    "date": "2026-03-09",
    "hours": 4,
    "topic": "Traffic Rules",
    "evidence_file": "<base64-encoded-file>"
  }
  ```
- **Response** (201): Same as Get Theory Hour Sessions item

### Update Theory Hour Session
- **Method**: PUT
- **Path**: `/theory-hours/{session_id}`
- **Authentication**: Required (lecturer)
- **Status**: Not Implemented
- **Request Body**: Same as Save Theory Hour Session
- **Response** (200): Same as Get Theory Hour Sessions item

### Delete Theory Hour Session
- **Method**: DELETE
- **Path**: `/theory-hours/{session_id}`
- **Authentication**: Required (lecturer, administrator)
- **Status**: Not Implemented
- **Response** (204): No content

### Bulk Upload Theory Hours Evidence
- **Method**: POST
- **Path**: `/theory-hours/bulk-upload`
- **Authentication**: Required (lecturer)
- **Status**: Not Implemented
- **Request Body**: multipart/form-data with evidence files
- **Response** (201):
  ```json
  {
    "uploaded": 5,
    "failed": 0,
    "message": "Successfully uploaded 5 evidence files"
  }
  ```

---

## 9. Practical Hours Module

Practical driving hours tracking and management.

### Get Practical Hour Sessions
- **Method**: GET
- **Path**: `/practical-hours`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `candidate_id` (string, optional): Filter by candidate
  - `instructor_id` (string, optional): Filter by instructor
  - `vehicle_id` (string, optional): Filter by vehicle
  - `date_from` (string, optional): ISO date format
  - `date_to` (string, optional): ISO date format
  - `status` (string, optional): Filter by status (scheduled, completed, cancelled)
- **Response** (200):
  ```json
  {
    "data": [
      {
        "session_id": "uuid",
        "candidate_id": "uuid",
        "instructor_id": "uuid",
        "vehicle_id": "uuid",
        "date": "2026-03-09",
        "start_time": "10:00",
        "end_time": "12:00",
        "hours": 2,
        "status": "completed",
        "route": "City Center Circuit",
        "notes": "Practiced parking",
        "created_at": "2026-03-09T10:00:00Z"
      }
    ],
    "total": 40
  }
  ```

### Create Practical Hour Session
- **Method**: POST
- **Path**: `/practical-hours`
- **Authentication**: Required (instructor)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "candidate_id": "uuid",
    "instructor_id": "uuid",
    "vehicle_id": "uuid",
    "date": "2026-03-09",
    "start_time": "10:00",
    "end_time": "12:00",
    "route": "City Center Circuit",
    "notes": "Practiced parking"
  }
  ```
- **Response** (201): Same as Get Practical Hour Sessions item

### Update Practical Hour Session
- **Method**: PUT
- **Path**: `/practical-hours/{session_id}`
- **Authentication**: Required (instructor)
- **Status**: Not Implemented
- **Request Body**: Same as Create Practical Hour Session
- **Response** (200): Same as Get Practical Hour Sessions item

### Delete Practical Hour Session
- **Method**: DELETE
- **Path**: `/practical-hours/{session_id}`
- **Authentication**: Required (instructor, administrator)
- **Status**: Not Implemented
- **Response** (204): No content

---

## 10. Payments Module

Payment tracking and management.

### Get All Payments
- **Method**: GET
- **Path**: `/payments`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `candidate_id` (string, optional): Filter by candidate
  - `status` (string, optional): Filter by status (pending, paid, partial)
  - `date_from` (string, optional): ISO date format
  - `date_to` (string, optional): ISO date format
- **Response** (200):
  ```json
  {
    "data": [
      {
        "payment_id": "uuid",
        "candidate_id": "uuid",
        "amount": 1000,
        "currency": "EUR",
        "date": "2026-03-09",
        "method": "bank_transfer",
        "status": "paid",
        "reference_number": "PAY-2026-00123",
        "notes": "Payment for category B",
        "created_by": "uuid",
        "created_at": "2026-03-09T10:00:00Z"
      }
    ],
    "total": 156
  }
  ```

### Create Payment
- **Method**: POST
- **Path**: `/payments`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "candidate_id": "uuid",
    "amount": 1000,
    "currency": "EUR",
    "date": "2026-03-09",
    "method": "bank_transfer",
    "reference_number": "PAY-2026-00123",
    "notes": "Payment for category B"
  }
  ```
- **Response** (201): Same as Get Payments item

### Update Payment
- **Method**: PUT
- **Path**: `/payments/{payment_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create Payment
- **Response** (200): Same as Get Payments item

### Delete Payment
- **Method**: DELETE
- **Path**: `/payments/{payment_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

### Get Candidate Payments
- **Method**: GET
- **Path**: `/candidates/{candidate_id}/payments`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
- **Response** (200): Same as Get All Payments response structure

---

## 11. Verifications Module

Student verification status (exam results, qualifications).

### Get All Verifications
- **Method**: GET
- **Path**: `/verifications`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `candidate_id` (string, optional): Filter by candidate
  - `status` (string, optional): Filter by status (pending, verified, failed)
- **Response** (200):
  ```json
  {
    "data": [
      {
        "verification_id": "uuid",
        "candidate_id": "uuid",
        "category_id": "uuid",
        "status": "verified",
        "theory_passed": true,
        "practical_passed": true,
        "theory_score": 85,
        "practical_score": 82,
        "verification_date": "2026-03-09",
        "certificate_number": "CERT-2026-00123",
        "verified_by": "uuid",
        "created_at": "2026-03-09T10:00:00Z"
      }
    ],
    "total": 42
  }
  ```

### Create Verification
- **Method**: POST
- **Path**: `/verifications`
- **Authentication**: Required (administrator, instructor)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "candidate_id": "uuid",
    "category_id": "uuid",
    "theory_passed": true,
    "practical_passed": true,
    "theory_score": 85,
    "practical_score": 82,
    "verification_date": "2026-03-09",
    "certificate_number": "CERT-2026-00123"
  }
  ```
- **Response** (201): Same as Get Verifications item

### Update Verification
- **Method**: PUT
- **Path**: `/verifications/{verification_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create Verification
- **Response** (200): Same as Get Verifications item

### Delete Verification
- **Method**: DELETE
- **Path**: `/verifications/{verification_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

---

## 12. Expenses Module

School expenses tracking.

### Get All Expenses
- **Method**: GET
- **Path**: `/expenses`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `type_id` (string, optional): Filter by expense type
  - `date_from` (string, optional): ISO date format
  - `date_to` (string, optional): ISO date format
  - `vehicle_id` (string, optional): Filter by vehicle
- **Response** (200):
  ```json
  {
    "data": [
      {
        "expense_id": "uuid",
        "type_id": "uuid",
        "vehicle_id": "uuid",
        "amount": 150,
        "currency": "EUR",
        "date": "2026-03-09",
        "description": "Oil change and filter replacement",
        "receipt_path": "/path/to/receipt.pdf",
        "created_at": "2026-03-09T10:00:00Z"
      }
    ],
    "total": 87
  }
  ```

### Create Expense
- **Method**: POST
- **Path**: `/expenses`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "type_id": "uuid",
    "vehicle_id": "uuid",
    "amount": 150,
    "currency": "EUR",
    "date": "2026-03-09",
    "description": "Oil change and filter replacement",
    "receipt_file": "<base64-encoded-file>"
  }
  ```
- **Response** (201): Same as Get Expenses item

### Update Expense
- **Method**: PUT
- **Path**: `/expenses/{expense_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create Expense
- **Response** (200): Same as Get Expenses item

### Delete Expense
- **Method**: DELETE
- **Path**: `/expenses/{expense_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

### Get All Expense Types
- **Method**: GET
- **Path**: `/expense-types`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**: None
- **Response** (200):
  ```json
  {
    "data": [
      {
        "type_id": "uuid",
        "name": "Vehicle Maintenance",
        "code": "MAINT",
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 12
  }
  ```

### Create Expense Type
- **Method**: POST
- **Path**: `/expense-types`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "name": "Vehicle Maintenance",
    "code": "MAINT"
  }
  ```
- **Response** (201): Same as Get Expense Types item

### Update Expense Type
- **Method**: PUT
- **Path**: `/expense-types/{type_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: Same as Create Expense Type
- **Response** (200): Same as Get Expense Types item

### Delete Expense Type
- **Method**: DELETE
- **Path**: `/expense-types/{type_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

---

## 13. Users Module

System user account management.

### Get All Users
- **Method**: GET
- **Path**: `/users`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `role` (string, optional): Filter by role
  - `active` (boolean, optional): Filter by active status
- **Response** (200):
  ```json
  {
    "data": [
      {
        "user_id": "uuid",
        "email": "user@school.com",
        "name": "User Name",
        "role": "administrator",
        "active": true,
        "last_login": "2026-03-09T10:00:00Z",
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 15
  }
  ```

### Create User
- **Method**: POST
- **Path**: `/users`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "email": "user@school.com",
    "name": "User Name",
    "role": "instructor",
    "temporary_password": true
  }
  ```
- **Response** (201):
  ```json
  {
    "user_id": "uuid",
    "email": "user@school.com",
    "name": "User Name",
    "role": "instructor",
    "temporary_password": "TempPass123!",
    "active": true,
    "created_at": "2026-03-09T10:00:00Z"
  }
  ```

### Update User
- **Method**: PUT
- **Path**: `/users/{user_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "name": "Updated Name",
    "role": "instructor"
  }
  ```
- **Response** (200): Same as Get Users item

### Delete User
- **Method**: DELETE
- **Path**: `/users/{user_id}`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Response** (204): No content

### Toggle User Active Status
- **Method**: POST
- **Path**: `/users/{user_id}/toggle-active`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**: None
- **Response** (200):
  ```json
  {
    "user_id": "uuid",
    "active": false
  }
  ```

### Reset User Password
- **Method**: POST
- **Path**: `/users/{user_id}/reset-password`
- **Authentication**: Required (administrator)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "send_email": true
  }
  ```
- **Response** (200):
  ```json
  {
    "user_id": "uuid",
    "temporary_password": "NewPass456!",
    "email_sent": true
  }
  ```

---

## 14. Print/PDF Module

Document generation and printing.

### Generate Fatura (Invoice)
- **Method**: GET
- **Path**: `/print/fatura/{payment_id}`
- **Authentication**: Required
- **Status**: Not Implemented
- **Response** (200): Binary PDF file (invoice)

### Generate Fleteparaqitja (Registration Form)
- **Method**: GET
- **Path**: `/print/fleteparaqitja/{candidate_id}`
- **Authentication**: Required
- **Status**: Not Implemented
- **Response** (200): Binary PDF file (registration form)

### Generate Libreza (Logbook)
- **Method**: GET
- **Path**: `/print/libreza/{candidate_id}`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `include_theory` (boolean, optional): Default true
  - `include_practical` (boolean, optional): Default true
- **Response** (200): Binary PDF file (logbook with hours)

### Generate Kontrata (Contract)
- **Method**: GET
- **Path**: `/print/kontrata/{candidate_id}`
- **Authentication**: Required
- **Status**: Not Implemented
- **Response** (200): Binary PDF file (student contract)

### Generate Vertetimi (Certificate)
- **Method**: GET
- **Path**: `/print/vertetimi/{verification_id}`
- **Authentication**: Required
- **Status**: Not Implemented
- **Response** (200): Binary PDF file (completion certificate)

### Generate Testi (Test Result)
- **Method**: GET
- **Path**: `/print/testi/{candidate_test_id}`
- **Authentication**: Required
- **Status**: Not Implemented
- **Response** (200): Binary PDF file (test results)

### Generate Candidate List (PDF)
- **Method**: GET
- **Path**: `/print/candidate-list`
- **Authentication**: Required
- **Status**: Not Implemented
- **Query Parameters**:
  - `category` (string, optional): Filter by category
  - `status` (string, optional): Filter by status
  - `format` (string, optional): pdf, excel, word
- **Response** (200): Binary file (PDF, XLSX, or DOCX with candidate list)

---

## 15. Super Admin Module

Platform-level administrative operations (tenant management, statistics, audit logs).

### Get All Tenants
- **Method**: GET
- **Path**: `/super-admin/tenants`
- **Authentication**: Required (super_admin)
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 50
  - `offset` (integer, optional): Default 0
  - `active` (boolean, optional): Filter by active status
- **Response** (200):
  ```json
  {
    "data": [
      {
        "tenant_id": "uuid",
        "name": "Driving School Name",
        "contact_email": "admin@school.com",
        "contact_phone": "+383123456789",
        "active": true,
        "created_at": "2026-01-01T00:00:00Z",
        "user_count": 8,
        "candidate_count": 45
      }
    ],
    "total": 23
  }
  ```

### Create Tenant
- **Method**: POST
- **Path**: `/super-admin/tenants`
- **Authentication**: Required (super_admin)
- **Status**: Not Implemented
- **Request Body**:
  ```json
  {
    "name": "Driving School Name",
    "contact_email": "admin@school.com",
    "contact_phone": "+383123456789"
  }
  ```
- **Response** (201): Same as Get Tenants item

### Update Tenant
- **Method**: PUT
- **Path**: `/super-admin/tenants/{tenant_id}`
- **Authentication**: Required (super_admin)
- **Status**: Not Implemented
- **Request Body**: Same as Create Tenant
- **Response** (200): Same as Get Tenants item

### Delete Tenant
- **Method**: DELETE
- **Path**: `/super-admin/tenants/{tenant_id}`
- **Authentication**: Required (super_admin)
- **Status**: Not Implemented
- **Response** (204): No content

### Get Platform Statistics
- **Method**: GET
- **Path**: `/super-admin/stats`
- **Authentication**: Required (super_admin)
- **Status**: Not Implemented
- **Response** (200):
  ```json
  {
    "total_tenants": 23,
    "active_tenants": 21,
    "total_users": 156,
    "total_candidates": 1245,
    "total_payments": 125000,
    "currency": "EUR",
    "candidates_by_status": {
      "active": 1100,
      "completed": 125,
      "archived": 20
    }
  }
  ```

### Get Audit Log
- **Method**: GET
- **Path**: `/super-admin/audit-log`
- **Authentication**: Required (super_admin)
- **Status**: Not Implemented
- **Query Parameters**:
  - `limit` (integer, optional): Default 100
  - `offset` (integer, optional): Default 0
  - `action` (string, optional): Filter by action type
  - `tenant_id` (string, optional): Filter by tenant
  - `user_id` (string, optional): Filter by user
  - `date_from` (string, optional): ISO date format
  - `date_to` (string, optional): ISO date format
- **Response** (200):
  ```json
  {
    "data": [
      {
        "log_id": "uuid",
        "action": "candidate_created",
        "user_id": "uuid",
        "tenant_id": "uuid",
        "resource_type": "candidate",
        "resource_id": "uuid",
        "changes": {
          "first_name": {"old": null, "new": "Fatmir"},
          "last_name": {"old": null, "new": "Gashi"}
        },
        "is_impersonating": false,
        "ip_address": "192.168.1.1",
        "created_at": "2026-03-09T10:00:00Z"
      }
    ],
    "total": 5432
  }
  ```

---

## Common Response Patterns

### Error Responses

**400 Bad Request** - Invalid input
```json
{
  "error": "invalid_input",
  "message": "Email is required",
  "details": {
    "email": "This field is required"
  }
}
```

**401 Unauthorized** - Missing or invalid token
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

**403 Forbidden** - Insufficient permissions or cross-tenant access attempt
```json
{
  "error": "forbidden",
  "message": "You do not have permission to access this resource"
}
```

**404 Not Found** - Resource does not exist
```json
{
  "error": "not_found",
  "message": "Candidate not found"
}
```

**409 Conflict** - Resource already exists or state conflict
```json
{
  "error": "conflict",
  "message": "A candidate with this email already exists"
}
```

**500 Internal Server Error** - Server error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred. Please try again later."
}
```

### Pagination

All list endpoints support pagination via `limit` and `offset` query parameters:
- `limit`: Number of items to return (max 100, default 50)
- `offset`: Number of items to skip (default 0)

Response includes total count for UI pagination controls.

---

## Rate Limiting

- Standard endpoints: 100 requests per minute per user
- PDF generation endpoints: 10 requests per minute per user
- File upload endpoints: 5 requests per minute per user

Rate limit headers included in all responses:
- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Date/Time Formats

- Dates: ISO 8601 format (YYYY-MM-DD)
- Date-times: ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)
- Times: HH:mm format (24-hour)

---

## File Uploads

File uploads use multipart/form-data encoding:
- Maximum file size: 10MB per file
- Supported formats: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX
- All files scanned for viruses before storage


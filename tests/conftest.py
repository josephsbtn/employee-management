"""
Shared fixtures dan mock objects untuk semua test files.
File ini berisi setup yang digunakan bersama di semua test.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pendulum
from bson import ObjectId

@pytest.fixture
def mock_employee_repo():
    """Mock EmployeeRepo untuk testing"""
    repo = Mock()
    return repo

@pytest.fixture
def mock_store_repo():
    """Mock StoreRepo untuk testing"""
    repo = Mock()
    return repo

@pytest.fixture
def mock_history_repo():
    """Mock HistoryRepo untuk testing"""
    repo = Mock()
    return repo

@pytest.fixture
def mock_leave_request_repo():
    """Mock LeaveRequestRepo untuk testing"""
    repo = Mock()
    return repo

@pytest.fixture
def mock_attendance_repo():
    """Mock AttendanceRepo untuk testing"""
    repo = Mock()
    return repo

@pytest.fixture
def sample_list_employees(sample_employee, sample_manager, sample_owner):
    return [sample_employee, sample_manager, sample_owner]


@pytest.fixture
def sample_employee():
    """Sample employee data untuk testing"""
    return {
        "_id": "EMP_12345",
        "name": "John Doe",
        "email": "john@example.com",
        "password": b"$2b$12$hashedpassword",
        "role": "employee",
        "status": "active",
        "branchId": "STR_001",
        "salary": 5000000,
        "annualLeaveBalance": 12,
        "createdAt": pendulum.now("Asia/Jakarta"),
        "workDays": 0,
        "lateDays": 0
    }

@pytest.fixture
def sample_manager():
    """Sample manager data untuk testing"""
    return {
        "_id": "EMP_99999",
        "name": "Manager User",
        "email": "manager@example.com",
        "password": b"$2b$12$hashedpassword",
        "role": "manager",
        "status": "active",
        "branchId": "STR_001",
        "salary": 8000000,
        "annualLeaveBalance": 15,
        "createdAt": pendulum.now("Asia/Jakarta")
    }

@pytest.fixture
def sample_owner():
    """Sample owner data untuk testing"""
    return {
        "_id": "EMP_00001",
        "name": "Owner User",
        "email": "owner@example.com",
        "password": b"$2b$12$hashedpassword",
        "role": "owner",
        "status": "active",
        "salary": 15000000
    }

@pytest.fixture
def sample_store():
    """Sample store/branch data untuk testing"""
    return {
        "_id": "STR_001",
        "name": "Aventra Salatiga",
        "address": "Jl. Test No. 123",
        "status": "active",
        "coordinates": {
            "type": "Point",
            "coordinates": [110.4917, -7.3305]
        }
    }
    

@pytest.fixture
def sample_leave_request():
    """Sample leave request data untuk testing"""
    return {
    "_id": "ANR_001",
    "employeeId": "EMP_12345",
    "type": "annual",
    "startDate": pendulum.datetime(2025, 1, 1),
    "endDate": pendulum.datetime(2025, 1, 3),
    "status": "waiting",
    "days": 3,
    "reason": "",
    "reviewer" : None,
    "fileName" : "",
    "attachmentUrl" : "",
    "createdAt": pendulum.now(),
    "updatedAt": pendulum.now()
}

@pytest.fixture
def sample_review_request_approved_comment():
    """Sample review request data untuk testing"""
    return {
        "employeeId": "EMP_99999",
        "note": "Aightt!, I'll approve this request."
    }

@pytest.fixture
def sample_review_request_approved_no_comment():
    """Sample review request data untuk testing"""
    return {
        "employeeId": "EMP_99999",
    }

@pytest.fixture
def sample_review_request_rejected_comment():
    """Sample review request data untuk testing"""
    return {
        "employeeId": "EMP_99999",
        "note": "Sorry, I can't approve this request."
    }

@pytest.fixture
def sample_review_request_rejected_no_comment():
    """Sample review request data untuk testing"""
    return {
        "employeeId": "EMP_99999",
    }


@pytest.fixture
def mock_acknowledged_result():
    """Mock MongoDB acknowledged result"""
    result = Mock()
    result.acknowledged = True
    result.inserted_id = "MOCK_ID_123"
    return result

@pytest.fixture
def mock_not_acknowledged_result():
    """Mock MongoDB not acknowledged result"""
    result = Mock()
    result.acknowledged = False
    return result
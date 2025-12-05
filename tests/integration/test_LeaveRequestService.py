
import pytest
from unittest.mock import Mock, patch
import pendulum
from service.leaveRequestService import LeaveRequestService


class TestLeaveRequestServiceCheckDateRange:
    """Test checkDateRange - validasi tanggal kompleks"""
    
    @patch('service.leaveRequestService.LeaveRequestRepo')
    def test_check_date_range_valid(self, mock_repo_class):
        """Test path: date range valid"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = []
        mock_repo_class.return_value = mock_repo
        
        service = LeaveRequestService()
        
        future_date = pendulum.now("Asia/Jakarta").add(days=5)
        start = future_date.to_date_string()
        end = future_date.add(days=3).to_date_string()
        
        # Execute
        result = service.checkDateRange(start, end, "EMP_001")
        
        # Assert
        assert result["status"] == True
        assert result["days"] == 4  # 5-8 = 4 days inclusive
    
    @patch('service.leaveRequestService.LeaveRequestRepo')
    def test_check_date_range_start_in_past(self, mock_repo_class):
        """Test path: start date di masa lalu"""
        # Setup
        service = LeaveRequestService()
        
        past_date = pendulum.now("Asia/Jakarta").subtract(days=1)
        start = past_date.to_date_string()
        end = pendulum.now("Asia/Jakarta").add(days=5).to_date_string()
        
        # Execute
        result = service.checkDateRange(start, end, "EMP_001")
        
        # Assert
        assert result["status"] == False
        assert "past" in result["message"].lower()
    
    @patch('service.leaveRequestService.LeaveRequestRepo')
    def test_check_date_range_end_before_start(self, mock_repo_class):
        """Test path: end date sebelum start date"""
        # Setup
        service = LeaveRequestService()
        
        future_date = pendulum.now("Asia/Jakarta").add(days=10)
        start = future_date.to_date_string()
        end = future_date.subtract(days=5).to_date_string()
        
        # Execute
        result = service.checkDateRange(start, end, "EMP_001")
        
        # Assert
        assert result["status"] == False
        assert "after end date" in result["message"].lower()
    
    @patch('service.leaveRequestService.LeaveRequestRepo')
    def test_check_date_range_overlap_existing_request(self, mock_repo_class):
        """Test path: overlap dengan request yang sudah ada"""
        # Setup
        mock_repo = Mock()
        existing_request = {
            "_id": "ANR_001",
            "employeeId": "EMP_001",
            "startDate": "2025-12-20",
            "endDate": "2025-12-25",
            "status": "approved"
        }
        mock_repo.getAllData.return_value = [existing_request]
        mock_repo_class.return_value = mock_repo
        
        service = LeaveRequestService()
        
        # Overlap: 2025-12-23 to 2025-12-27
        start = "2025-12-23"
        end = "2025-12-27"
        
        # Execute
        result = service.checkDateRange(start, end, "EMP_001")
        
        # Assert
        assert result["status"] == False
        assert "overlaps" in result["message"].lower()


class TestLeaveRequestServiceCreateRequest:
    """Test createAnnualRequest - full workflow"""
    
    @patch('service.leaveRequestService.EmployeeRepo')
    @patch('service.leaveRequestService.LeaveRequestRepo')
    @patch('service.leaveRequestService.HistoryRepo')
    def test_create_annual_request_success(self, mock_history_repo, mock_leave_repo, 
                                          mock_emp_repo, sample_employee, mock_acknowledged_result):
        """Test path: berhasil create annual request"""
        
        mock_emp = Mock()
        mock_emp.getData.return_value = sample_employee
        mock_emp_repo.return_value = mock_emp
        
        mock_leave = Mock()
        mock_leave.getAllData.return_value = []  
        mock_leave.insertData.return_value = mock_acknowledged_result
        mock_leave_repo.return_value = mock_leave
        
        mock_history = Mock()
        mock_history.insertData.return_value = mock_acknowledged_result
        mock_history_repo.return_value = mock_history
        
        service = LeaveRequestService()
        
        future_date = pendulum.now("Asia/Jakarta").add(days=10)
        data = {
            "employeeId": "EMP_12345",
            "startDate": future_date.to_date_string(),
            "endDate": future_date.add(days=4).to_date_string(),
            "type": "annual",
            "reason": "Vacation"
        }
        
        result = service.createAnnualRequest(data, {"_id": "EMP_12345", "name": "John"})
        
        assert result["status"] == True
        assert "created successfully" in result["message"].lower()
        mock_leave.insertData.assert_called_once()
        mock_emp.updateData.assert_called_once()  
    
    @patch('service.leaveRequestService.EmployeeRepo')
    def test_create_request_insufficient_balance(self, mock_emp_repo, sample_employee):
        """Test path: saldo cuti tidak cukup"""
        # Setup mock employee
        sample_employee["annualLeaveBalance"] = 3  # Only 3 days
        mock_emp = Mock()
        mock_emp.getData.return_value = sample_employee
        mock_emp_repo.return_value = mock_emp
        
        service = LeaveRequestService()
        
        future_date = pendulum.now("Asia/Jakarta").add(days=10)
        data = {
            "employeeId": "EMP_12345",
            "startDate": future_date.to_date_string(),
            "endDate": future_date.add(days=5).to_date_string(),  # 6 days
            "type": "annual",
            "reason": "Vacation"
        }
        
        result = service.createAnnualRequest(data, {"_id": "EMP_12345", "name": "John"})
        
        assert result["status"] == False
        assert "Insufficient annual leave balance" in result["message"]

class TestLeaveRequestServiceAnnualRequest:
    """Test approveRequest - full workflow"""
    @patch('service.leaveRequestService.LeaveRequestRepo')
    @patch('service.leaveRequestService.HistoryRepo')
    @patch('service.leaveRequestService.EmployeeRepo')
    def test_approve_annualRequest_success_commented(self, mock_emp_repo,mock_history_repo, mock_leave_repo,
                                               mock_acknowledged_result, 
                                               sample_review_request_approved_comment, sample_leave_request,
                                               sample_employee):
        """Test path: berhasil approve annual request"""
        #setup buat mock data employee
        mock_emp = Mock()
        mock_emp.getData.return_value = sample_employee
        mock_emp_repo.return_value = mock_emp
        mock_emp.updateData.return_value = mock_acknowledged_result
        
        #setup buat mock data leave request
        mock_leave = Mock()
        mock_leave.getData.return_value = sample_leave_request
        mock_leave.updateData.return_value = mock_acknowledged_result
        mock_leave_repo.return_value = mock_leave
        
        #setup buat mock data history
        mock_history = Mock()
        mock_history.insertData.return_value = mock_acknowledged_result
        mock_history_repo.return_value = mock_history
        
        service = LeaveRequestService()
        
        result = service.approveRequest(id="ANR_001", data=sample_review_request_approved_comment ,currentUser={"_id": "EMP_12345", "name": "John"})
        
        assert result["status"] == True
        assert result["message"] == "Data updated successfully"
    
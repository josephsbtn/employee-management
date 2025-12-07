import pytest
from unittest.mock import Mock, patch
from marshmallow import ValidationError
from service.employeeService import EmployeeService
from bcrypt import hashpw, gensalt


class TestEmployeeServiceGetAllEmployee:
    """Test getAllEmployee method - berbagai path dan kondisi"""
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.StoreRepo')
    def test_get_all_employee_empty_list(self, mock_store_repo_class, mock_repo_class):
        """Test path: database kosong, return empty list"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = []
        mock_repo_class.return_value = mock_repo
        
        service = EmployeeService()
        
        # Execute
        result = service.getAllEmployee()
        print("[TESTING LOG] result: ", result)
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data fetched successfully"
        assert result["data"] == []
        mock_repo.getAllData.assert_called_once()
    
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.StoreRepo')
    def test_get_all_employee_filtered_by_branch(self, mock_store_repo_class, mock_repo_class, sample_employee):
        """Test path: filter by branchId"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = [sample_employee]
        mock_repo_class.return_value = mock_repo
        
        service = EmployeeService()
        
        # Execute
        result = service.getAllEmployee(branchId="STR_001")
        
        # Assert
        assert result["status"] == True
        mock_repo.getAllData.assert_called_once_with(
            query={"$and": [{"branchId": "STR_001"}, {"role": "employee"}]}
        )
    
    @patch('service.employeeService.EmployeeRepo')
    def test_get_all_employee_exception_handling(self, mock_repo_class):
        """Test path: exception during fetch"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.side_effect = Exception("Database error")
        mock_repo_class.return_value = mock_repo
        
        service = EmployeeService()
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to get data"):
            service.getAllEmployee()
            
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.StoreRepo')
    def test_get_all_employees_with_data(self, mock_store_repo, mock_employee_repo, sample_list_employees, sample_store):
        """Test path: exception during fetch"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = sample_list_employees
        mock_employee_repo.return_value = mock_repo
        
        mock_store = Mock()
        mock_store.getDataById.return_value = sample_store
        mock_store_repo.return_value = mock_store
        
        service = EmployeeService()
        result = service.getAllEmployee()
        print("[TESTING LOG] result: ", result)
        
        assert result["status"] == True
        assert result["message"] == "Data fetched successfully" 
        assert result["data"][0]["branch"] == sample_store

class TestEmployeeServiceNewEmployee:
    """Test newEmployee method - validation, business rules, edge cases"""
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.HistoryService')
    def test_create_employee_success(self, mock_history_class, mock_repo_class, mock_acknowledged_result):
        """Test path: successful employee creation"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = []  # No existing manager
        mock_repo.getData.return_value = None  # Email not used
        mock_repo.insertData.return_value = mock_acknowledged_result
        mock_repo_class.return_value = mock_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = EmployeeService()
        
        data = {
            "name": "Jane Smith",
            "email": "jane@aventra.com",
            "password": "secret123",
            "role": "employee",
            "branchId": "STR_001",
            "salary": 5000000
        }
        current_user = {"_id": "EMP_001", "name": "Admin"}
        
        # Execute
        result = service.newEmployee(data, current_user)
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data inserted successfully"
        mock_repo.insertData.assert_called_once()
        mock_history.createHistory.assert_called_once()
    
    @patch('service.employeeService.EmployeeRepo')
    def test_create_employee_email_already_used(self, mock_repo_class):
        """Test path: email sudah digunakan"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = []
        mock_repo.getData.return_value = {"email": "jane@aventra.com"}  # Email exists
        mock_repo_class.return_value = mock_repo
        
        service = EmployeeService()
        
        data = {
            "name": "Jane Smith",
            "email": "jane@aventra.com",
            "password": "secret123",
            "role": "employee",
            "branchId": "STR_001",
            "salary": 5000000
        }
        
        # Execute
        result = service.newEmployee(data, {"_id": "EMP_001", "name": "Admin"})
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Email already used"
    
    @patch('service.employeeService.EmployeeRepo')
    def test_create_manager_branch_already_has_manager(self, mock_repo_class):
        """Test path: branch sudah punya manager"""
        # Setup
        mock_repo = Mock()
        existing_manager = {"_id": "EMP_999", "role": "manager", "branchId": "STR_001", "status": "active"}
        mock_repo.getAllData.return_value = [existing_manager]
        mock_repo_class.return_value = mock_repo
        
        service = EmployeeService()
        
        data = {
            "name": "New Manager",
            "email": "newmanager@aventra.com",
            "password": "secret123",
            "role": "manager",
            "branchId": "STR_001",
            "salary": 8000000
        }
        
        # Execute
        result = service.newEmployee(data, {"_id": "EMP_001", "name": "Admin"})
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Branch already has 2 manager"
    
    @patch('service.employeeService.EmployeeRepo')
    def test_create_employee_branch_full(self, RepoMock):
        mock_repo = Mock()
        RepoMock.return_value = mock_repo

        mock_repo.getAllData.side_effect = [
            [{"_id": f"EMP_{i}"} for i in range(6)]
        ]

        
        mock_repo.getData.return_value = None

        service = EmployeeService()
        data = {
            "name": "New Employee",
            "email": "gtw@aventra.com",
            "password": "secret123",
            "role": "employee",
            "branchId": "STR_001",
            "salary": 5000000
        }
        
        # Execute
        result = service.newEmployee(data, {"_id": "EMP_001", "name": "Admin"})
        print("CALLS getAllData:", mock_repo.getAllData.call_args_list)
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Branch already has 6 employees"
    
    @patch('service.employeeService.EmployeeRepo')
    def test_create_employee_validation_error(self, mock_repo_class):
        """Test path: validation error dari schema"""
        
        service = EmployeeService()
        
        data = {
            "name": "",  # Invalid empty name
            "email": "invalid",
            "password": "123"
        }
        
        # Execute & Assert
        with pytest.raises(ValidationError):
            service.newEmployee(data, {"_id": "EMP_001", "name": "Admin"})


class TestEmployeeService:
    """Test login method - authentication paths"""
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.SessionService')
    @patch('service.employeeService.HistoryService')
    @patch('service.employeeService.checkpw')
    def test_login_success(self, mock_checkpw, mock_history_class, mock_session_class, 
                          mock_repo_class, sample_employee):
        """Test path: login berhasil"""
        # Setup
        mock_repo = Mock()
        mock_repo.getData.return_value = sample_employee
        mock_repo_class.return_value = mock_repo
        
        mock_checkpw.return_value = True
        
        mock_session = Mock()
        mock_session.createToken.return_value = "JWT_TOKEN_123"
        mock_session_class.return_value = mock_session
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = EmployeeService()
        
        data = {
            "email": "john@example.com",
            "password": "secret123"
        }
        
        # Execute
        result = service.login(data)
        
        # Assert
        assert result["status"] == True
        assert result["token"] == "JWT_TOKEN_123"
        mock_session.createToken.assert_called_once()
        mock_history.createHistory.assert_called_once()
    
    @patch('service.employeeService.EmployeeRepo')
    def test_login_email_not_found(self, mock_repo_class):
        """Test path: email tidak ditemukan"""
        # Setup
        mock_repo = Mock()
        mock_repo.getData.return_value = None
        mock_repo_class.return_value = mock_repo
        
        service = EmployeeService()
        
        data = {
            "email": "notfound@example.com",
            "password": "secret123"
        }
        
        # Execute
        result = service.login(data)
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Email or Password Invalid"
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.checkpw')
    def test_login_invalid_password(self, mock_checkpw, mock_repo_class, sample_employee):
        """Test path: password salah"""
        # Setup
        mock_repo = Mock()
        mock_repo.getData.return_value = sample_employee
        mock_repo_class.return_value = mock_repo
        
        mock_checkpw.return_value = False
        
        service = EmployeeService()
        
        data = {
            "email": "john@example.com",
            "password": "wrongpassword"
        }
        
        result = service.login(data)
        
        assert result["status"] == False
        assert result["message"] == "Email or Password Invalid"
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.checkpw')
    def test_login_inactive_account(self, mock_checkpw, mock_repo_class, sample_employee):
        """Test path: account inactive"""
        # Setup
        sample_employee["status"] = "inactive"
        mock_repo = Mock()
        mock_repo.getData.return_value = sample_employee
        mock_repo_class.return_value = mock_repo
        
        mock_checkpw.return_value = True
        
        service = EmployeeService()
        
        data = {
            "email": "john@example.com",
            "password": "secret123"
        }
        
        # Execute
        result = service.login(data)
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Your account has been disabled"
    
    def test_login_missing_credentials(self):
        """Test path: missing email or password"""
        service = EmployeeService()
        
        # Missing password
        data = {"email": "john@example.com"}
        
        # Execute & Assert
        with pytest.raises(ValidationError):
            service.login(data)
            
            
class TestEmployeeServiceFireAndActivate:
    """Test fireEmployee dan activateEmployee methods"""
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.HistoryService')
    def test_fire_employee_success(self, mock_history_class, mock_repo_class, mock_acknowledged_result):
        """Test path: berhasil fire employee"""
        # Setup
        mock_repo = Mock()
        mock_repo.updateData.return_value = mock_acknowledged_result
        mock_repo_class.return_value = mock_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = EmployeeService()
        
        # Execute
        result = service.fireEmployee(
            {"_id": "EMP_001", "name": "Admin"},
            "EMP_12345"
        )
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data Disabled successfully"
        mock_repo.updateData.assert_called_once_with(
            validateData={"status": "inactive", "branchId": ""},
            id="EMP_12345"
        )
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.HistoryService')
    def test_activate_employee_success(self, mock_history_class, mock_repo_class, mock_acknowledged_result):
        """Test path: berhasil activate employee"""
        # Setup
        mock_repo = Mock()
        mock_repo.updateData.return_value = mock_acknowledged_result
        mock_repo_class.return_value = mock_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = EmployeeService()
        
        # Execute
        result = service.activateEmployee(
            {"_id": "EMP_001", "name": "Admin"},
            "EMP_12345"
        )
        
        # Assert
        assert result["status"] == True
        mock_repo.updateData.assert_called_once()
        
class TestEmployeeServiceUpdate:
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.HistoryService')
    def test_update_employee_success(self,mock_history_repo, mock_repo_class, mock_acknowledged_result, sample_owner):
        """Test path: berhasil update employee"""
        # Setup
        mock_repo = Mock()
        mock_repo.updateData.return_value = mock_acknowledged_result
        mock_repo_class.return_value = mock_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_repo.return_value = mock_history
        
        service = EmployeeService()
        
        updateData = {
            "name": "Jane Smith",
            "email": "jane@aventra.com",
            "password": "secret123",
            "role": "employee",
            "branchId": "STR_001",
            "salary": 50000
        }
        
        # Execute
        result = service.updateEmploye(updateData, "EMP_12345", sample_owner)
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data updated successfully" 
        
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.HistoryService')
    def test_update_employee_manager_success(self,mock_history_repo, mock_repo_class, mock_acknowledged_result, sample_owner):
        """Test path: berhasil update employee to manager"""
        # Setup
        mock_repo = Mock()
        mock_repo.updateData.return_value = mock_acknowledged_result
        mock_repo.getAllData.return_value = []
        mock_repo_class.return_value = mock_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_repo.return_value = mock_history
        
        service = EmployeeService()
        
        updateData = {
            "name": "Jane Smith",
            "email": "jane@aventra.com",
            "password": "secret123",
            "role": "manager",
            "branchId": "STR_001",
            "salary": 50000
        }
        
        # Execute
        result = service.updateEmploye(updateData, "EMP_12345", sample_owner)
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data updated successfully"
    
    
    @patch('service.employeeService.EmployeeRepo')
    @patch('service.employeeService.HistoryService')
    def test_update_employee_validationError(self,mock_history_repo, mock_repo_class, mock_acknowledged_result, sample_owner):
        """Test path: berhasil update employee"""
        # Setup
        mock_repo = Mock()
        mock_repo.updateData.return_value = mock_acknowledged_result
        mock_repo_class.return_value = mock_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_repo.return_value = mock_history
        
        service = EmployeeService()
        
        updateData = {
            "name": "Jane Smith",
            "email": "jane@email.com",
            "password": "sec",
            "role": "employee",
            "branchId": "STR_001",
            "salary": 50000000
        }
        
        with pytest.raises(ValidationError):
            service.updateEmploye(updateData, "EMP_12345", sample_owner)
        
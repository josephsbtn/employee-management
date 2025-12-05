
import pytest
from unittest.mock import Mock, patch
from service.historyService import HistoryService
from  marshmallow import ValidationError


class TestHistoryServiceCreateHistory:
    """Test createHistory method"""
    
    @patch('service.historyService.HistoryRepo')
    def test_create_history_success(self, mock_repo_class, mock_acknowledged_result):
        """Test path: berhasil create history"""
        # Setup
        mock_repo = Mock()
        mock_repo.insertData.return_value = mock_acknowledged_result
        mock_repo_class.return_value = mock_repo
        
        service = HistoryService()
        
        data = {
            "employeeId": "EMP_001",
            "employeeName": "John Doe",
            "description": "Login successfully",
            "type": "auth"
        }
        
        # Execute
        result = service.createHistory(data)
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data inserted successfully"
        mock_repo.insertData.assert_called_once()
    
    @patch('service.historyService.HistoryRepo')
    def test_create_history_failed_insert(self, mock_repo_class, mock_not_acknowledged_result):
        """Test path: gagal insert ke database"""
        # Setup
        mock_repo = Mock()
        mock_repo.insertData.return_value = mock_not_acknowledged_result
        mock_repo_class.return_value = mock_repo
        
        service = HistoryService()
        
        data = {
            "employeeId": "EMP_001",
            "employeeName": "John Doe",
            "description": "Login successfully",
            "type": "auth"
        }
        
        # Execute
        result = service.createHistory(data)
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Failed to insert data"
        
    @patch('service.historyService.HistoryRepo')
    def test_create_user_history_validation_error(self, mock_repo_class):
        """Test path: user tidak punya history"""
        # Setup
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        service = HistoryService()
        
        data = {
            "employeeId": "EMP_001",
            "name": "John Doe",
            "description": "Login successfully",
            "type": "transaction"
        }
        
        with pytest.raises(ValidationError): 
            service.createHistory(data=data)
       


class TestHistoryServiceGetHistory:
    """Test getAllHistory dan getUserHistory"""
    
    @patch('service.historyService.HistoryRepo')
    def test_get_all_history_success(self, mock_repo_class):
        """Test path: berhasil get all history"""
        # Setup
        mock_repo = Mock()
        mock_data = [
            {"_id": "HIS_001", "employeeId": "EMP_001", "description": "Login"},
            {"_id": "HIS_002", "employeeId": "EMP_002", "description": "Create employee"}
        ]
        mock_repo.getAllData.return_value = mock_data
        mock_repo_class.return_value = mock_repo
        
        service = HistoryService()
        
        # Execute
        result = service.getAllHistory()
        
        # Assert
        assert result["status"] == True
        assert len(result["data"]) == 2
    
    @patch('service.historyService.HistoryRepo')
    def test_get_user_history_success(self, mock_repo_class):
        """Test path: berhasil get user history"""
        # Setup
        mock_repo = Mock()
        mock_data = [
            {"_id": "HIS_001", "employeeId": "EMP_001", "description": "Login"}
        ]
        mock_repo.getAllData.return_value = mock_data
        mock_repo_class.return_value = mock_repo
        
        service = HistoryService()
        
        # Execute
        result = service.getUserHistory("EMP_001")
        
        # Assert
        assert result["status"] == True
        assert len(result["data"]) == 1
        mock_repo.getAllData.assert_called_once_with(query={"employeeId": "EMP_001"})
    
    @patch('service.historyService.HistoryRepo')
    def test_get_user_history_not_found(self, mock_repo_class):
        """Test path: user tidak punya history"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = []
        mock_repo_class.return_value = mock_repo
        
        service = HistoryService()
        
        # Execute
        result = service.getUserHistory("EMP_999")
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Failed to get data"


    
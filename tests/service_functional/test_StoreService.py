import pytest
from unittest.mock import Mock, patch, MagicMock
from marshmallow import ValidationError
from service.storeService import StoreService
from datetime import datetime


class TestStoreServiceAddStore:
    """Test addStore - menambahkan store baru"""
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.StoreRepo')
    def test_add_store_success(self,  mock_repo_class, mock_history_class):
        """Test path: store berhasil ditambahkan"""
        # Setup
        mock_repo = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = "STR_12345"
        mock_insert_result.acknowledged = True
        mock_repo.insertData.return_value = mock_insert_result
        mock_repo_class.return_value = mock_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = StoreService()
        
        data = {
            
            "name": "Store Jakarta",
            "address": "Jakarta",
            "phone": "081234567890",
            "geometry": {"type": "Point", "coordinates": [0, 0]}
        }
        
        # Execute
        result = service.addStore(data, "EMP_001", "John Doe")
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Store added successfully"
        assert "Store" in result["data"]
        mock_repo.insertData.assert_called_once()
        mock_history.createHistory.assert_called_once()
    
    def test_add_store_validation_error(self):
        """Test path: validation error saat menambahkan store"""
        service = StoreService()
        
        data = {"name": ""}
        
        # Execute & Assert
        with pytest.raises(ValidationError):
            service.addStore(data, "EMP_001", "John Doe")
    
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.StoreRepo')
    @patch('service.storeService.createStoreSchema')
    def test_add_store_history_failed(self, mock_schema_class, mock_repo_class, mock_history_class):
        """Test path: gagal menambahkan history"""
        # Setup
        mock_repo = Mock()
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = "STR_12345"
        mock_insert_result.acknowledged = True
        mock_repo.insertData.return_value = mock_insert_result
        mock_repo_class.return_value = mock_repo
        
        mock_schema = Mock()
        mock_schema.load.return_value = {"name": "Store Jakarta"}
        mock_schema_class.return_value = mock_schema
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": False}
        mock_history_class.return_value = mock_history
        
        service = StoreService()
        service.createSchema = mock_schema
        
        data = {"name": "Store Jakarta"}
        
        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            service.addStore(data, "EMP_001", "John Doe")
        assert "Failed to add history" in str(exc_info.value)


class TestStoreServiceGetAllStore:
    """Test getAllStore - mendapatkan semua store"""
    
    @patch('service.storeService.StoreRepo')
    def test_get_all_store_success(self, mock_repo_class):
        """Test path: berhasil mendapatkan semua store"""
        # Setup
        mock_repo = Mock()
        mock_data = [
            {"_id": "STR_001", "name": "Store A"},
            {"_id": "STR_002", "name": "Store B"}
        ]
        mock_repo.getAllData.return_value = mock_data
        mock_repo_class.return_value = mock_repo
        
        service = StoreService()
        
        # Execute
        result = service.getAllStore()
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data fetched successfully"
        assert len(result["data"]) == 2
        mock_repo.getAllData.assert_called_once()
    
    @patch('service.storeService.StoreRepo')
    def test_get_all_store_empty(self, mock_repo_class):
        """Test path: tidak ada store"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = []
        mock_repo_class.return_value = mock_repo
        
        service = StoreService()
        
        # Execute
        result = service.getAllStore()
        
        # Assert
        assert result["status"] == True
        assert len(result["data"]) == 0
    
    @patch('service.storeService.StoreRepo')
    def test_get_all_store_exception(self, mock_repo_class):
        """Test path: exception saat get all store"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.side_effect = Exception("Database error")
        mock_repo_class.return_value = mock_repo
        
        service = StoreService()
        
        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            service.getAllStore()
        assert "Failed to get data" in str(exc_info.value)


class TestStoreServiceStoreDetails:
    """Test storeDetails - mendapatkan detail store dengan employees"""
    
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_store_details_success(self, mock_store_repo_class, mock_emp_repo_class):
        """Test path: berhasil mendapatkan detail store"""
        # Setup
        mock_store_repo = Mock()
        mock_store_repo.getData.return_value = {
            "_id": "STR_001",
            "name": "Store Jakarta"
        }
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_repo.getAllData.return_value = [
            {"_id": "EMP_001", "name": "John"},
            {"_id": "EMP_002", "name": "Jane"}
        ]
        mock_emp_repo_class.return_value = mock_emp_repo
        
        service = StoreService()
        
        # Execute
        result = service.storeDetails("STR_001")
        
        # Assert
        assert result["status"] == True
        assert result["data"]["_id"] == "STR_001"
        assert len(result["data"]["employees"]) == 2
        mock_store_repo.getData.assert_called_once_with(id="STR_001")
        mock_emp_repo.getAllData.assert_called_once_with(query={"storeID": "STR_001"})
    
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_store_details_no_employees(self, mock_store_repo_class, mock_emp_repo_class):
        """Test path: store tanpa employees"""
        # Setup
        mock_store_repo = Mock()
        mock_store_repo.getData.return_value = {
            "_id": "STR_001",
            "name": "Store Jakarta"
        }
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_repo.getAllData.return_value = []
        mock_emp_repo_class.return_value = mock_emp_repo
        
        service = StoreService()
        
        # Execute
        result = service.storeDetails("STR_001")
        
        # Assert
        assert result["status"] == True
        assert len(result["data"]["employees"]) == 0


class TestStoreServiceDeleteStore:
    """Test deleteStore - menghapus store"""
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_delete_store_with_employees_success(self, mock_store_repo_class, 
                                                   mock_emp_repo_class, mock_history_class):
        """Test path: berhasil menghapus store beserta employees"""
        # Setup
        mock_store_repo = Mock()
        mock_store_repo.deleteData.return_value = True
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_repo.getAllData.return_value = [{"_id": "EMP_001"}]
        mock_emp_repo.deleteData.return_value = True
        mock_emp_repo_class.return_value = mock_emp_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = StoreService()
        
        # Execute
        result = service.deleteStore("STR_001", "EMP_999", "Admin")
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data deleted successfully"
        mock_emp_repo.deleteData.assert_called_once()
        mock_store_repo.deleteData.assert_called_once_with(id="STR_001")
        mock_history.createHistory.assert_called_once()
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_delete_store_without_employees_success(self, mock_store_repo_class,
                                                      mock_emp_repo_class, mock_history_class):
        """Test path: berhasil menghapus store tanpa employees"""
        # Setup
        mock_store_repo = Mock()
        mock_store_repo.deleteData.return_value = True
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_repo.getAllData.return_value = []
        mock_emp_repo_class.return_value = mock_emp_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = StoreService()
        
        # Execute
        result = service.deleteStore("STR_001", "EMP_999", "Admin")
        
        # Assert
        assert result["status"] == True
        mock_emp_repo.deleteData.assert_not_called()
        mock_store_repo.deleteData.assert_called_once()
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_delete_store_history_failed(self, mock_store_repo_class,
                                          mock_emp_repo_class, mock_history_class):
        """Test path: gagal menambahkan history"""
        # Setup
        mock_store_repo = Mock()
        mock_store_repo.deleteData.return_value = True
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_repo.getAllData.return_value = []
        mock_emp_repo_class.return_value = mock_emp_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": False}
        mock_history_class.return_value = mock_history
        
        service = StoreService()
        
        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            service.deleteStore("STR_001", "EMP_999", "Admin")
        assert "Failed to add history" in str(exc_info.value)


class TestStoreServiceUpdateStore:
    """Test updateStore - update data store"""
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.StoreRepo')
    @patch('service.storeService.UpdateStoreSchema')
    def test_update_store_success(self, mock_schema_class, mock_repo_class, mock_history_class):
        """Test path: berhasil update store"""
        # Setup
        mock_repo = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = True
        mock_repo.updateData.return_value = mock_update_result
        mock_repo_class.return_value = mock_repo
        
        mock_schema = Mock()
        mock_schema.load.return_value = {
            "name": "Store Updated",
            "address": "New Address"
        }
        mock_schema_class.return_value = mock_schema
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = StoreService()
        service.updateSchema = mock_schema
        
        data = {
            "id": "STR_001",
            "name": "Store Updated",
            "address": "New Address"
        }
        
        # Execute
        result = service.updateStore("STR_001", data, "EMP_001", "John Doe")
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data updated successfully"
        mock_repo.updateData.assert_called_once()
        mock_history.createHistory.assert_called_once()
    
    @patch('service.storeService.StoreRepo')
    @patch('service.storeService.UpdateStoreSchema')
    def test_update_store_validation_error(self, mock_schema_class, mock_repo_class):
        """Test path: validation error saat update"""
        # Setup
        mock_schema = Mock()
        mock_schema.load.side_effect = ValidationError("Invalid data")
        mock_schema_class.return_value = mock_schema
        
        service = StoreService()
        service.updateSchema = mock_schema
        
        data = {"id": "STR_001", "name": ""}
        
        # Execute & Assert
        with pytest.raises(ValidationError):
            service.updateStore("STR_001", data, "EMP_001", "John Doe")
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.StoreRepo')
    @patch('service.storeService.UpdateStoreSchema')
    def test_update_store_not_acknowledged(self, mock_schema_class, 
                                            mock_repo_class, mock_history_class):
        """Test path: update tidak acknowledged"""
        # Setup
        mock_repo = Mock()
        mock_update_result = Mock()
        mock_update_result.acknowledged = False
        mock_repo.updateData.return_value = mock_update_result
        mock_repo_class.return_value = mock_repo
        
        mock_schema = Mock()
        mock_schema.load.return_value = {"name": "Store Updated"}
        mock_schema_class.return_value = mock_schema
        
        service = StoreService()
        service.updateSchema = mock_schema
        
        data = {"id": "STR_001", "name": "Store Updated"}
        
        # Execute
        result = service.updateStore("STR_001", data, "EMP_001", "John Doe")
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Failed to update data"


class TestStoreServiceNonActivateStore:
    """Test nonActivateStore - menonaktifkan store"""
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_non_activate_store_success(self, mock_store_repo_class,
                                         mock_emp_repo_class, mock_history_class):
        """Test path: berhasil menonaktifkan store"""
        # Setup
        mock_store_repo = Mock()
        mock_store_result = Mock()
        mock_store_result.acknowledged = True
        mock_store_repo.updateData.return_value = mock_store_result
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_result = Mock()
        mock_emp_result.acknowledged = True
        mock_emp_repo.updateData.return_value = mock_emp_result
        mock_emp_repo_class.return_value = mock_emp_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = StoreService()
        
        employee = {"_id": "EMP_001", "name": "John Doe"}
        
        # Execute
        result = service.nonActivateStore("STR_001", employee)
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data fetched successfully"
        mock_store_repo.updateData.assert_called_once_with(
            id="STR_001", 
            validateData={"status": "inactive"}
        )
        mock_emp_repo.updateData.assert_called_once()
        mock_history.createHistory.assert_called_once()
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_non_activate_store_employee_update_failed(self, mock_store_repo_class,
                                                         mock_emp_repo_class, mock_history_class):
        """Test path: gagal update employees"""
        # Setup
        mock_store_repo = Mock()
        mock_store_result = Mock()
        mock_store_result.acknowledged = True
        mock_store_repo.updateData.return_value = mock_store_result
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_result = Mock()
        mock_emp_result.acknowledged = False
        mock_emp_repo.updateData.return_value = mock_emp_result
        mock_emp_repo_class.return_value = mock_emp_repo
        
        service = StoreService()
        
        employee = {"_id": "EMP_001", "name": "John Doe"}
        
        # Execute
        result = service.nonActivateStore("STR_001", employee)
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Failed to update data"


class TestStoreServiceActivateStore:
    """Test ActivateStore - mengaktifkan store"""
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.StoreRepo')
    def test_activate_store_success(self, mock_repo_class, mock_history_class):
        """Test path: berhasil mengaktifkan store"""
        # Setup
        mock_repo = Mock()
        mock_result = Mock()
        mock_result.acknowledged = True
        mock_repo.updateData.return_value = mock_result
        mock_repo_class.return_value = mock_repo
        
        mock_history = Mock()
        mock_history.createHistory.return_value = {"status": True}
        mock_history_class.return_value = mock_history
        
        service = StoreService()
        
        employee = {"_id": "EMP_001", "name": "John Doe"}
        
        # Execute
        result = service.ActivateStore("STR_001", employee)
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data fetched successfully"
        mock_repo.updateData.assert_called_once_with(
            id="STR_001",
            validateData={"status": "active"}
        )
        mock_history.createHistory.assert_called_once()
    
    @patch('service.storeService.HistoryService')
    @patch('service.storeService.StoreRepo')
    def test_activate_store_update_failed(self, mock_repo_class, mock_history_class):
        """Test path: gagal update store"""
        # Setup
        mock_repo = Mock()
        mock_result = Mock()
        mock_result.acknowledged = False
        mock_repo.updateData.return_value = mock_result
        mock_repo_class.return_value = mock_repo
        
        service = StoreService()
        
        employee = {"_id": "EMP_001", "name": "John Doe"}
        
        # Execute
        result = service.ActivateStore("STR_001", employee)
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Failed to update data"


class TestStoreServiceGetStoreDetails:
    """Test getStoreDetails - mendapatkan detail lengkap store"""
    
    @patch('service.storeService.EmployeeSchema')
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_get_store_details_success(self, mock_store_repo_class,
                                        mock_emp_repo_class, mock_emp_schema_class):
        """Test path: berhasil mendapatkan detail store"""
        # Setup
        mock_store_repo = Mock()
        mock_store_repo.getData.return_value = {
            "_id": "STR_001",
            "name": "Store Jakarta"
        }
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_repo.getAllData.return_value = [
            {"_id": "EMP_001", "name": "John"}
        ]
        mock_emp_repo_class.return_value = mock_emp_repo
        
        mock_emp_schema = Mock()
        mock_emp_schema.dump.return_value = {"_id": "EMP_001", "name": "John"}
        mock_emp_schema_class.return_value = mock_emp_schema
        
        service = StoreService()
        service.employeeSchema = mock_emp_schema
        
        # Execute
        result = service.getStoreDetails("STR_001")
        
        # Assert
        assert result["status"] == True
        assert result["data"]["_id"] == "STR_001"
        assert len(result["data"]["employees"]) == 1
        mock_emp_schema.dump.assert_called_once()
    
    @patch('service.storeService.EmployeeRepo')
    @patch('service.storeService.StoreRepo')
    def test_get_store_details_not_found(self, mock_store_repo_class, mock_emp_repo_class):
        """Test path: store tidak ditemukan"""
        # Setup
        mock_store_repo = Mock()
        mock_store_repo.getData.return_value = None
        mock_store_repo_class.return_value = mock_store_repo
        
        mock_emp_repo = Mock()
        mock_emp_repo_class.return_value = mock_emp_repo
        
        service = StoreService()
        
        # Execute
        result = service.getStoreDetails("STR_999")
        
        # Assert
        assert result["status"] == False
        assert result["message"] == "Data not found"


class TestStoreServiceGetActiveStore:
    """Test getActiveStore - mendapatkan store aktif"""
    
    @patch('service.storeService.StoreSchema')
    @patch('service.storeService.StoreRepo')
    def test_get_active_store_success(self, mock_repo_class, mock_schema_class):
        """Test path: berhasil mendapatkan store aktif"""
        # Setup
        mock_repo = Mock()
        mock_data = [
            {"_id": "STR_001", "name": "Store A", "status": "active"},
            {"_id": "STR_002", "name": "Store B", "status": "active"}
        ]
        mock_repo.getAllData.return_value = mock_data
        mock_repo_class.return_value = mock_repo
        
        mock_schema = Mock()
        mock_schema.dump.return_value = mock_data
        mock_schema_class.return_value = mock_schema
        
        service = StoreService()
        service.schema = mock_schema
        
        # Execute
        result = service.getActiveStore()
        
        # Assert
        assert result["status"] == True
        assert result["message"] == "Data fetched successfully"
        assert len(result["data"]) == 2
        mock_repo.getAllData.assert_called_once_with(query={"status": "active"})
        mock_schema.dump.assert_called_once_with(mock_data, many=True)
    
    @patch('service.storeService.StoreSchema')
    @patch('service.storeService.StoreRepo')
    def test_get_active_store_empty(self, mock_repo_class, mock_schema_class):
        """Test path: tidak ada store aktif"""
        # Setup
        mock_repo = Mock()
        mock_repo.getAllData.return_value = []
        mock_repo_class.return_value = mock_repo
        
        mock_schema = Mock()
        mock_schema.dump.return_value = []
        mock_schema_class.return_value = mock_schema
        
        service = StoreService()
        service.schema = mock_schema
        
        # Execute
        result = service.getActiveStore()
        
        # Assert
        assert result["status"] == True
        assert len(result["data"]) == 0
    
    @patch('service.storeService.StoreRepo')
    def test_get_active_store_exception(self, mock_repo_class):
        """Test path: exception saat get active store"""
        mock_repo = Mock()
        mock_repo.getAllData.side_effect = Exception("Database error")
        mock_repo_class.return_value = mock_repo
        
        service = StoreService()
        
        with pytest.raises(Exception) as exc_info:
            service.getActiveStore()
        assert "Failed to get data" in str(exc_info.value)
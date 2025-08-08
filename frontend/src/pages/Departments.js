import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { mockDepartments, getUsersByDepartment } from '../data/mockData';
import { 
  Building2, 
  Plus, 
  Edit, 
  Trash2, 
  Users, 
  Search,
  Filter,
  Shield,
  AlertTriangle,
  CheckCircle,
  Briefcase
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Departments = () => {
  const { toast } = useToast();
  const { user, isAdmin } = useAuth();
  
  // All hooks must be called before any conditional returns
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [newDepartment, setNewDepartment] = useState({
    name: '',
    description: ''
  });
  const [editDepartment, setEditDepartment] = useState({
    id: '',
    name: '',
    description: ''
  });

  // Redirect non-admin users AFTER hooks are called
  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md mx-auto">
          <CardContent className="text-center py-12">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Shield className="w-10 h-10 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
            <p className="text-gray-600 mb-6">
              You don't have permission to access department management. This feature is restricted to administrators only.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                <p className="text-sm text-yellow-800">
                  <strong>Security Notice:</strong> Department management requires admin privileges
                </p>
              </div>
            </div>
            <Button onClick={() => window.history.back()} variant="outline">
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const filteredDepartments = mockDepartments.filter(dept =>
    dept.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dept.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreateDepartment = () => {
    if (!newDepartment.name || !newDepartment.description) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information.",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Department created successfully!",
      description: `${newDepartment.name} department has been created.`,
    });

    setNewDepartment({ name: '', description: '' });
    setIsCreateModalOpen(false);
  };

  const handleEditDepartment = (department) => {
    setSelectedDepartment(department);
    setEditDepartment({
      id: department.id,
      name: department.name,
      description: department.description
    });
    setIsEditModalOpen(true);
  };

  const handleUpdateDepartment = () => {
    if (!editDepartment.name || !editDepartment.description) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information.",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Department updated successfully!",
      description: `${editDepartment.name} department has been updated.`,
    });

    setEditDepartment({ id: '', name: '', description: '' });
    setSelectedDepartment(null);
    setIsEditModalOpen(false);
  };

  const handleCancelEdit = () => {
    setEditDepartment({ id: '', name: '', description: '' });
    setSelectedDepartment(null);
    setIsEditModalOpen(false);
  };

  const handleDeleteDepartment = (departmentId, departmentName) => {
    const usersInDepartment = getUsersByDepartment(departmentId);
    if (usersInDepartment.length > 0) {
      toast({
        title: "Cannot delete department",
        description: `${departmentName} has ${usersInDepartment.length} users assigned. Please reassign or remove users first.`,
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Department deleted",
      description: `${departmentName} department has been removed from the system.`,
    });
  };

  const getStatusBadge = (isActive) => {
    return isActive ? (
      <Badge className="bg-green-100 text-green-800">
        <CheckCircle className="w-3 h-3 mr-1" />
        Active
      </Badge>
    ) : (
      <Badge className="bg-gray-100 text-gray-800">
        Inactive
      </Badge>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Department Management</h1>
          <p className="text-gray-600">Manage departments and organize your organization structure</p>
        </div>
        
        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Add New Department
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Department</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Department Name</Label>
                <Input
                  id="name"
                  placeholder="Enter department name"
                  value={newDepartment.name}
                  onChange={(e) => setNewDepartment(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Enter department description"
                  rows={4}
                  value={newDepartment.description}
                  onChange={(e) => setNewDepartment(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>
              
              <div className="flex items-center justify-end space-x-3 pt-4">
                <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateDepartment}>
                  Create Department
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Edit Department Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Department</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                <Briefcase className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="font-medium text-gray-900">Editing: {selectedDepartment?.name}</p>
                <p className="text-sm text-gray-600">Department ID: {selectedDepartment?.id}</p>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="edit-name">Department Name</Label>
              <Input
                id="edit-name"
                placeholder="Enter department name"
                value={editDepartment.name}
                onChange={(e) => setEditDepartment(prev => ({ ...prev, name: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                placeholder="Enter department description"
                rows={4}
                value={editDepartment.description}
                onChange={(e) => setEditDepartment(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label>Additional Information</Label>
              <div className="text-sm text-gray-600 space-y-1">
                <p>Created: {selectedDepartment ? new Date(selectedDepartment.createdAt).toLocaleDateString() : ''}</p>
                <p>Users: <span className="font-medium">{selectedDepartment?.userCount || 0}</span></p>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 pt-4">
              <Button variant="outline" onClick={handleCancelEdit}>
                Cancel
              </Button>
              <Button onClick={handleUpdateDepartment} className="bg-blue-600 hover:bg-blue-700">
                Update Department
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Departments</p>
                <p className="text-2xl font-bold text-blue-700">{mockDepartments.length}</p>
              </div>
              <Building2 className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Active Departments</p>
                <p className="text-2xl font-bold text-green-700">
                  {mockDepartments.filter(d => d.isActive).length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Total Users</p>
                <p className="text-2xl font-bold text-orange-700">
                  {mockDepartments.reduce((sum, d) => sum + d.userCount, 0)}
                </p>
              </div>
              <Users className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Avg Users/Dept</p>
                <p className="text-2xl font-bold text-purple-700">
                  {Math.round(mockDepartments.reduce((sum, d) => sum + d.userCount, 0) / mockDepartments.length)}
                </p>
              </div>
              <Briefcase className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Departments Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl">All Departments</CardTitle>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search departments..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Department</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Users</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDepartments.map((department) => (
                <TableRow 
                  key={department.id} 
                  className="cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => handleEditDepartment(department)}
                >
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <Briefcase className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{department.name}</p>
                        <p className="text-sm text-gray-500">ID: {department.id}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <p className="text-sm text-gray-900 line-clamp-2 max-w-xs">
                      {department.description}
                    </p>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center text-sm text-gray-600">
                      <Users className="w-4 h-4 mr-1" />
                      {department.userCount}
                    </div>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(department.isActive)}
                  </TableCell>
                  <TableCell>
                    {new Date(department.createdAt).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation(); // Prevent row click
                          handleEditDepartment(department);
                        }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation(); // Prevent row click
                          handleDeleteDepartment(department.id, department.name);
                        }}
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          {filteredDepartments.length === 0 && (
            <div className="text-center py-12">
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No departments found</h3>
              <p className="text-gray-600">Try adjusting your search or create a new department.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Departments;
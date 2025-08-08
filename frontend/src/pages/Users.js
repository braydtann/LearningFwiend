import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { mockUsers, mockDepartments } from '../data/mockData';
import { Search, Filter, Plus, Edit, Trash2, UserPlus, Shield, AlertTriangle, Building2 } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Users = () => {
  const { toast } = useToast();
  const { user, isAdmin } = useAuth();
  
  // Redirect non-admin users
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
              You don't have permission to access user management. This feature is restricted to administrators only.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                <p className="text-sm text-yellow-800">
                  <strong>Security Notice:</strong> User management requires admin privileges
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
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userToDelete, setUserToDelete] = useState(null);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'learner',
    departmentId: '',
    startDate: new Date().toISOString().split('T')[0] // Today's date as default
  });
  const [editUser, setEditUser] = useState({
    id: '',
    name: '',
    email: '',
    role: 'learner',
    departmentId: '',
    startDate: ''
  });

  const filteredUsers = mockUsers.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const handleCreateUser = () => {
    if (!newUser.name || !newUser.email || !newUser.startDate) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information including start date.",
        variant: "destructive",
      });
      return;
    }

    // Check if role requires department
    if (newUser.role !== 'admin' && !newUser.departmentId) {
      toast({
        title: "Missing department",
        description: "Please select a department for instructors and learners.",
        variant: "destructive",
      });
      return;
    }

    const departmentName = newUser.departmentId ? 
      mockDepartments.find(d => d.id === newUser.departmentId)?.name : 'No Department';

    toast({
      title: "User created successfully!",
      description: `${newUser.name} has been added as a ${newUser.role} in ${departmentName}.`,
    });

    setNewUser({ name: '', email: '', role: 'learner', departmentId: '', startDate: new Date().toISOString().split('T')[0] });
    setIsCreateModalOpen(false);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setEditUser({
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
      departmentId: user.departmentId || '',
      startDate: user.startDate || ''
    });
    setIsEditModalOpen(true);
  };

  const handleUpdateUser = () => {
    if (!editUser.name || !editUser.email || !editUser.startDate) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information including start date.",
        variant: "destructive",
      });
      return;
    }

    // Check if role requires department
    if (editUser.role !== 'admin' && !editUser.departmentId) {
      toast({
        title: "Missing department",
        description: "Please select a department for instructors and learners.",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "User updated successfully!",
      description: `${editUser.name}'s information has been updated.`,
    });

    setEditUser({ id: '', name: '', email: '', role: 'learner', departmentId: '', startDate: '' });
    setSelectedUser(null);
    setIsEditModalOpen(false);
  };

  const handleCancelEdit = () => {
    setEditUser({ id: '', name: '', email: '', role: 'learner', departmentId: '', startDate: '' });
    setSelectedUser(null);
    setIsEditModalOpen(false);
  };

  const handleDeleteClick = (user) => {
    setUserToDelete(user);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteUser = () => {
    if (!userToDelete) return;

    toast({
      title: "User deleted",
      description: `${userToDelete.name} has been removed from the system.`,
    });

    setUserToDelete(null);
    setIsDeleteModalOpen(false);
  };

  const handleCancelDelete = () => {
    setUserToDelete(null);
    setIsDeleteModalOpen(false);
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800';
      case 'instructor':
        return 'bg-green-100 text-green-800';
      case 'learner':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">User Management</h1>
          <p className="text-gray-600">Manage all users in your LearningFwiend platform</p>
        </div>
        
        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <UserPlus className="w-4 h-4 mr-2" />
              Add New User
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New User</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  placeholder="Enter full name"
                  value={newUser.name}
                  onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter email address"
                  value={newUser.email}
                  onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="startDate">Start Date</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={newUser.startDate}
                  onChange={(e) => setNewUser(prev => ({ ...prev, startDate: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Select value={newUser.role} onValueChange={(value) => setNewUser(prev => ({ ...prev, role: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="learner">Student</SelectItem>
                    <SelectItem value="instructor">Instructor</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {newUser.role !== 'admin' && (
                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Select value={newUser.departmentId} onValueChange={(value) => setNewUser(prev => ({ ...prev, departmentId: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select department" />
                    </SelectTrigger>
                    <SelectContent>
                      {mockDepartments.map(dept => (
                        <SelectItem key={dept.id} value={dept.id}>
                          <div className="flex items-center">
                            <Building2 className="w-4 h-4 mr-2" />
                            {dept.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              <div className="flex items-center justify-end space-x-3 pt-4">
                <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateUser}>
                  Create User
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Edit User Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
              <img 
                src={selectedUser?.avatar} 
                alt={selectedUser?.name}
                className="w-12 h-12 rounded-full object-cover"
              />
              <div>
                <p className="font-medium text-gray-900">Editing: {selectedUser?.name}</p>
                <p className="text-sm text-gray-600">User ID: {selectedUser?.id}</p>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="edit-name">Full Name</Label>
              <Input
                id="edit-name"
                placeholder="Enter full name"
                value={editUser.name}
                onChange={(e) => setEditUser(prev => ({ ...prev, name: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="edit-email">Email Address</Label>
              <Input
                id="edit-email"
                type="email"
                placeholder="Enter email address"
                value={editUser.email}
                onChange={(e) => setEditUser(prev => ({ ...prev, email: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-startDate">Start Date</Label>
              <Input
                id="edit-startDate"
                type="date"
                value={editUser.startDate}
                onChange={(e) => setEditUser(prev => ({ ...prev, startDate: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="edit-role">Role</Label>
              <Select value={editUser.role} onValueChange={(value) => setEditUser(prev => ({ ...prev, role: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="learner">Student</SelectItem>
                  <SelectItem value="instructor">Instructor</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {editUser.role !== 'admin' && (
              <div className="space-y-2">
                <Label htmlFor="edit-department">Department</Label>
                <Select value={editUser.departmentId} onValueChange={(value) => setEditUser(prev => ({ ...prev, departmentId: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    {mockDepartments.map(dept => (
                      <SelectItem key={dept.id} value={dept.id}>
                        <div className="flex items-center">
                          <Building2 className="w-4 h-4 mr-2" />
                          {dept.name}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            
            <div className="space-y-2">
              <Label>Additional Information</Label>
              <div className="text-sm text-gray-600 space-y-1">
                <p>Join Date: {selectedUser ? new Date(selectedUser.joinDate).toLocaleDateString() : ''}</p>
                <p>Start Date: {selectedUser ? new Date(selectedUser.startDate).toLocaleDateString() : ''}</p>
                <p>Current Role: <span className="font-medium">{selectedUser?.role}</span></p>
                <p>Department: <span className="font-medium">{selectedUser?.department || 'No Department'}</span></p>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 pt-4">
              <Button variant="outline" onClick={handleCancelEdit}>
                Cancel
              </Button>
              <Button onClick={handleUpdateUser} className="bg-blue-600 hover:bg-blue-700">
                Update User
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
                <p className="text-blue-600 text-sm font-medium">Total Users</p>
                <p className="text-2xl font-bold text-blue-700">{mockUsers.length}</p>
              </div>
              <UserPlus className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Instructors</p>
                <p className="text-2xl font-bold text-green-700">
                  {mockUsers.filter(u => u.role === 'instructor').length}
                </p>
              </div>
              <UserPlus className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Students</p>
                <p className="text-2xl font-bold text-orange-700">
                  {mockUsers.filter(u => u.role === 'learner').length}
                </p>
              </div>
              <UserPlus className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Admins</p>
                <p className="text-2xl font-bold text-purple-700">
                  {mockUsers.filter(u => u.role === 'admin').length}
                </p>
              </div>
              <UserPlus className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl">All Users</CardTitle>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger className="w-48">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Filter by role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="instructor">Instructor</SelectItem>
                  <SelectItem value="learner">Student</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Join Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.map((user) => (
                <TableRow 
                  key={user.id} 
                  className="cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => handleEditUser(user)}
                >
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <img 
                        src={user.avatar} 
                        alt={user.name}
                        className="w-10 h-10 rounded-full object-cover"
                      />
                      <div>
                        <p className="font-medium text-gray-900">{user.name}</p>
                        <p className="text-sm text-gray-500">ID: {user.id}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Badge className={getRoleBadgeColor(user.role)}>
                      {user.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(user.joinDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation(); // Prevent row click
                          handleEditUser(user);
                        }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation(); // Prevent row click
                          handleDeleteUser(user.id, user.name);
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
          
          {filteredUsers.length === 0 && (
            <div className="text-center py-12">
              <UserPlus className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
              <p className="text-gray-600">Try adjusting your search or filters.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Users;
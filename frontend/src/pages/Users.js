import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { mockDepartments } from '../data/mockData';
import { Search, Filter, Plus, Edit, Trash2, UserPlus, Shield, AlertTriangle, Building2, Eye, EyeOff, Key, RefreshCw } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Users = () => {
  const { toast } = useToast();
  const { user, isAdmin, createUser, resetUserPassword, getAllUsers } = useAuth();
  
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

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isPasswordResetModalOpen, setIsPasswordResetModalOpen] = useState(false);
  const [selectedUserForReset, setSelectedUserForReset] = useState(null);
  const [showTempPassword, setShowTempPassword] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [newUser, setNewUser] = useState({
    full_name: '',
    username: '',
    email: '',
    role: 'learner',
    department: '',
    temporary_password: ''
  });
  const [resetPasswordData, setResetPasswordData] = useState({
    new_temporary_password: ''
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    const result = await getAllUsers();
    if (result.success) {
      setUsers(result.users);
    } else {
      toast({
        title: "Error loading users",
        description: result.error,
        variant: "destructive",
      });
    }
    setLoading(false);
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const validatePassword = (password) => {
    if (password.length < 6) {
      return 'Password must be at least 6 characters long';
    }
    if (!/\d/.test(password)) {
      return 'Password must contain at least one number';
    }
    if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
      return 'Password must contain at least one special character';
    }
    return null;
  };

  const handleCreateUser = async () => {
    if (!newUser.full_name || !newUser.username || !newUser.email || !newUser.temporary_password) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information including temporary password.",
        variant: "destructive",
      });
      return;
    }

    // Check if role requires department
    if (newUser.role !== 'admin' && !newUser.department) {
      toast({
        title: "Missing department",
        description: "Please select a department for instructors and learners.",
        variant: "destructive",
      });
      return;
    }

    // Validate password
    const passwordError = validatePassword(newUser.temporary_password);
    if (passwordError) {
      toast({
        title: "Invalid password",
        description: passwordError,
        variant: "destructive",
      });
      return;
    }

    const result = await createUser(newUser);

    if (result.success) {
      toast({
        title: "User created successfully!",
        description: `${newUser.full_name} has been added with temporary password.`,
      });
      
      // Show the temporary password to admin
      toast({
        title: "Temporary Password Created",
        description: `Password for ${newUser.username}: ${newUser.temporary_password}`,
        duration: 10000, // Show for 10 seconds
      });

      setNewUser({ 
        full_name: '', 
        username: '', 
        email: '', 
        role: 'learner', 
        department: '', 
        temporary_password: '' 
      });
      setIsCreateModalOpen(false);
      fetchUsers(); // Refresh user list
    } else {
      toast({
        title: "User creation failed",
        description: result.error,
        variant: "destructive",
      });
    }
  };

  const handlePasswordReset = async () => {
    if (!resetPasswordData.new_temporary_password) {
      toast({
        title: "Missing password",
        description: "Please enter a new temporary password.",
        variant: "destructive",
      });
      return;
    }

    // Validate password
    const passwordError = validatePassword(resetPasswordData.new_temporary_password);
    if (passwordError) {
      toast({
        title: "Invalid password",
        description: passwordError,
        variant: "destructive",
      });
      return;
    }

    const result = await resetUserPassword(selectedUserForReset.id, resetPasswordData.new_temporary_password);

    if (result.success) {
      toast({
        title: "Password reset successful!",
        description: `${selectedUserForReset.username}'s password has been reset.`,
      });
      
      // Show the new temporary password to admin
      toast({
        title: "New Temporary Password",
        description: `Password for ${selectedUserForReset.username}: ${resetPasswordData.new_temporary_password}`,
        duration: 10000, // Show for 10 seconds
      });

      setResetPasswordData({ new_temporary_password: '' });
      setIsPasswordResetModalOpen(false);
      setSelectedUserForReset(null);
    } else {
      toast({
        title: "Password reset failed",
        description: result.error,
        variant: "destructive",
      });
    }
  };

  const openPasswordResetModal = (user) => {
    setSelectedUserForReset(user);
    setIsPasswordResetModalOpen(true);
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

  const generateRandomPassword = () => {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let result = '';
    
    // Ensure at least one of each required type
    result += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[Math.floor(Math.random() * 26)]; // uppercase
    result += 'abcdefghijklmnopqrstuvwxyz'[Math.floor(Math.random() * 26)]; // lowercase
    result += '0123456789'[Math.floor(Math.random() * 10)]; // number
    result += '!@#$%^&*'[Math.floor(Math.random() * 8)]; // special char
    
    // Fill the rest randomly
    for (let i = 4; i < 8; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    // Shuffle the result
    return result.split('').sort(() => Math.random() - 0.5).join('');
  };

  const generatePasswordForCreate = () => {
    const password = generateRandomPassword();
    setNewUser(prev => ({ ...prev, temporary_password: password }));
  };

  const generatePasswordForReset = () => {
    const password = generateRandomPassword();
    setResetPasswordData({ new_temporary_password: password });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading users...</p>
        </div>
      </div>
    );
  }

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
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create New User</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input
                  id="full_name"
                  placeholder="Enter full name"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser(prev => ({ ...prev, full_name: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  placeholder="Enter username"
                  value={newUser.username}
                  onChange={(e) => setNewUser(prev => ({ ...prev, username: e.target.value }))}
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
                  <Select value={newUser.department} onValueChange={(value) => setNewUser(prev => ({ ...prev, department: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select department" />
                    </SelectTrigger>
                    <SelectContent>
                      {mockDepartments.map(dept => (
                        <SelectItem key={dept.id} value={dept.name}>
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
                <Label htmlFor="temporary_password">Temporary Password</Label>
                <div className="flex space-x-2">
                  <div className="relative flex-1">
                    <Input
                      id="temporary_password"
                      type={showTempPassword ? "text" : "password"}
                      placeholder="Enter temporary password"
                      value={newUser.temporary_password}
                      onChange={(e) => setNewUser(prev => ({ ...prev, temporary_password: e.target.value }))}
                      className="pr-10"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-2 top-2 h-6 w-6 p-0"
                      onClick={() => setShowTempPassword(!showTempPassword)}
                    >
                      {showTempPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={generatePasswordForCreate}
                    className="px-3"
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
                <div className="text-xs text-gray-600 space-y-1">
                  <p>Requirements: 6+ characters, 1 number, 1 special character</p>
                  <p className="text-orange-600">User will be required to change this password on first login</p>
                </div>
              </div>
              
              <div className="flex items-center justify-end space-x-3 pt-4">
                <Button variant="outline" onClick={() => {
                  setIsCreateModalOpen(false);
                  setNewUser({ full_name: '', username: '', email: '', role: 'learner', department: '', temporary_password: '' });
                }}>
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

      {/* Password Reset Modal */}
      <Dialog open={isPasswordResetModalOpen} onOpenChange={setIsPasswordResetModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reset User Password</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {selectedUserForReset && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <UserPlus className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{selectedUserForReset.full_name}</p>
                    <p className="text-sm text-gray-600">{selectedUserForReset.email}</p>
                    <p className="text-sm text-gray-600">Username: {selectedUserForReset.username}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="reset_password">New Temporary Password</Label>
              <div className="flex space-x-2">
                <div className="relative flex-1">
                  <Input
                    id="reset_password"
                    type={showResetPassword ? "text" : "password"}
                    placeholder="Enter new temporary password"
                    value={resetPasswordData.new_temporary_password}
                    onChange={(e) => setResetPasswordData({ new_temporary_password: e.target.value })}
                    className="pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-2 top-2 h-6 w-6 p-0"
                    onClick={() => setShowResetPassword(!showResetPassword)}
                  >
                    {showResetPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={generatePasswordForReset}
                  className="px-3"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
              <div className="text-xs text-gray-600 space-y-1">
                <p>Requirements: 6+ characters, 1 number, 1 special character</p>
                <p className="text-orange-600">User will be required to change this password on next login</p>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                <div>
                  <p className="text-sm text-yellow-800 font-medium">Security Notice</p>
                  <p className="text-sm text-yellow-700">
                    The user will be logged out and required to change this temporary password on their next login.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 pt-4">
              <Button variant="outline" onClick={() => {
                setIsPasswordResetModalOpen(false);
                setSelectedUserForReset(null);
                setResetPasswordData({ new_temporary_password: '' });
              }}>
                Cancel
              </Button>
              <Button onClick={handlePasswordReset} className="bg-orange-600 hover:bg-orange-700">
                <Key className="w-4 h-4 mr-2" />
                Reset Password
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
                <p className="text-2xl font-bold text-blue-700">{users.length}</p>
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
                  {users.filter(u => u.role === 'instructor').length}
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
                  {users.filter(u => u.role === 'learner').length}
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
                  {users.filter(u => u.role === 'admin').length}
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
                <TableHead>Department</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.map((user) => (
                <TableRow key={user.id} className="hover:bg-gray-50 transition-colors">
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <UserPlus className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{user.full_name}</p>
                        <p className="text-sm text-gray-500">@{user.username}</p>
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
                    {user.department ? (
                      <div className="flex items-center text-sm text-gray-600">
                        <Building2 className="w-4 h-4 mr-1" />
                        {user.department}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">No Department</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {user.first_login_required ? (
                      <Badge className="bg-orange-100 text-orange-800">
                        Temp Password
                      </Badge>
                    ) : (
                      <Badge className="bg-green-100 text-green-800">
                        Active
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => openPasswordResetModal(user)}
                        title="Reset Password"
                      >
                        <Key className="w-4 h-4 text-orange-500" />
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
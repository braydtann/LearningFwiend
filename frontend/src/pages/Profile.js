import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Avatar, AvatarImage, AvatarFallback } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import { useToast } from '../hooks/use-toast';

const Profile = () => {
  const { user, updateUser, checkAuthStatus } = useAuth();
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    bio: user?.bio || '',
    avatar: user?.avatar || ''
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    
    try {
      // Prepare update data - only send fields that changed
      const updateData = {};
      if (formData.full_name !== user?.full_name) {
        updateData.full_name = formData.full_name;
      }
      if (formData.email !== user?.email) {
        updateData.email = formData.email;
      }
      // Note: bio and avatar aren't supported by backend yet, but ready for future implementation
      
      if (Object.keys(updateData).length === 0) {
        toast({
          title: "No changes made",
          description: "Please make some changes before saving.",
          variant: "destructive",
        });
        setLoading(false);
        return;
      }

      const result = await updateUser(user.id, updateData);

      if (result.success) {
        toast({
          title: "Profile updated!",
          description: "Your profile has been successfully updated.",
        });
        setIsEditing(false);
        
        // Refresh user data to reflect changes
        await checkAuthStatus();
      } else {
        toast({
          title: "Update failed",
          description: result.error || "Failed to update profile.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An unexpected error occurred.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      full_name: user?.full_name || '',
      email: user?.email || '',
      bio: user?.bio || '',
      avatar: user?.avatar || ''
    });
    setIsEditing(false);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile Settings</h1>
        <p className="text-gray-600">Manage your account information and preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Information */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Personal Information</CardTitle>
                {!isEditing && (
                  <Button onClick={() => setIsEditing(true)}>
                    Edit Profile
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Avatar */}
              <div className="flex items-center space-x-6">
                <Avatar className="h-24 w-24">
                  <AvatarImage src={formData.avatar} alt={formData.name} />
                  <AvatarFallback className="text-2xl">
                    {formData.name?.charAt(0) || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{formData.name}</h3>
                  <p className="text-gray-600 capitalize">{user?.role}</p>
                  <p className="text-sm text-gray-500">
                    Member since {new Date(user?.joinDate).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    disabled={!isEditing}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    disabled={!isEditing}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="avatar">Avatar URL</Label>
                <Input
                  id="avatar"
                  placeholder="https://example.com/avatar.jpg"
                  value={formData.avatar}
                  onChange={(e) => handleInputChange('avatar', e.target.value)}
                  disabled={!isEditing}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  placeholder="Tell us about yourself..."
                  rows={4}
                  value={formData.bio}
                  onChange={(e) => handleInputChange('bio', e.target.value)}
                  disabled={!isEditing}
                />
              </div>

              {isEditing && (
                <div className="flex items-center space-x-4 pt-4">
                  <Button onClick={handleSave}>
                    Save Changes
                  </Button>
                  <Button variant="outline" onClick={handleCancel}>
                    Cancel
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Profile Stats */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Account Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Role</span>
                <Badge className="capitalize">
                  {user?.role}
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-600">User ID</span>
                <span className="font-mono text-sm">{user?.id}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Join Date</span>
                <span className="text-sm">
                  {new Date(user?.joinDate).toLocaleDateString()}
                </span>
              </div>
            </CardContent>
          </Card>

          {user?.role === 'learner' && (
            <Card>
              <CardHeader>
                <CardTitle>Learning Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Courses Enrolled</span>
                  <span className="font-semibold">2</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Completed</span>
                  <span className="font-semibold">1</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Certificates</span>
                  <span className="font-semibold">1</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Hours Learned</span>
                  <span className="font-semibold">24h</span>
                </div>
              </CardContent>
            </Card>
          )}

          {user?.role === 'instructor' && (
            <Card>
              <CardHeader>
                <CardTitle>Teaching Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Courses Created</span>
                  <span className="font-semibold">3</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Total Students</span>
                  <span className="font-semibold">105</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Avg Rating</span>
                  <span className="font-semibold">4.8/5</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Total Reviews</span>
                  <span className="font-semibold">42</span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
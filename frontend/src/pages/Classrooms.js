import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { mockClassrooms, getClassroomsForTrainer, getStudentClassrooms, mockUsers, mockCourses } from '../data/mockData';
import { 
  Users, 
  Calendar, 
  BookOpen, 
  Plus, 
  Eye, 
  Edit, 
  TrendingUp,
  Clock,
  Award,
  Target,
  UserPlus
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Classrooms = () => {
  const { user, isAdmin, isInstructor, isLearner } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newClassroom, setNewClassroom] = useState({
    name: '',
    description: '',
    trainerId: '',
    courseIds: [],
    studentIds: [],
    startDate: '',
    endDate: ''
  });

  // Get classrooms based on user role
  const getClassroomsForUser = () => {
    if (isAdmin) {
      return mockClassrooms;
    } else if (isInstructor) {
      return getClassroomsForTrainer(user.id);
    } else if (isLearner) {
      return getStudentClassrooms(user.id);
    }
    return [];
  };

  const classrooms = getClassroomsForUser();
  const instructors = mockUsers.filter(u => u.role === 'instructor');
  const students = mockUsers.filter(u => u.role === 'learner');

  const handleCreateClassroom = () => {
    if (!newClassroom.name || !newClassroom.trainerId || newClassroom.courseIds.length === 0) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information.",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Classroom created successfully!",
      description: `${newClassroom.name} has been created and is ready for students.`,
    });

    setNewClassroom({
      name: '',
      description: '',
      trainerId: '',
      courseIds: [],
      studentIds: [],
      startDate: '',
      endDate: ''
    });
    setIsCreateModalOpen(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'upcoming':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {isLearner ? 'My Classrooms' : 'Classroom Management'}
          </h1>
          <p className="text-gray-600">
            {isLearner 
              ? 'Track your progress across different training programs'
              : 'Manage cohort-based training programs and track student progress'
            }
          </p>
        </div>
        
        {(isAdmin || isInstructor) && (
          <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
            <DialogTrigger asChild>
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="w-4 h-4 mr-2" />
                Create Classroom
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Classroom</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Classroom Name</Label>
                    <Input
                      id="name"
                      placeholder="Enter classroom name"
                      value={newClassroom.name}
                      onChange={(e) => setNewClassroom(prev => ({ ...prev, name: e.target.value }))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="trainer">Assign Trainer</Label>
                    <Select 
                      value={newClassroom.trainerId} 
                      onValueChange={(value) => setNewClassroom(prev => ({ ...prev, trainerId: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select trainer" />
                      </SelectTrigger>
                      <SelectContent>
                        {instructors.map(instructor => (
                          <SelectItem key={instructor.id} value={instructor.id}>
                            {instructor.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe the training program"
                    rows={3}
                    value={newClassroom.description}
                    onChange={(e) => setNewClassroom(prev => ({ ...prev, description: e.target.value }))}
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="startDate">Start Date</Label>
                    <Input
                      id="startDate"
                      type="date"
                      value={newClassroom.startDate}
                      onChange={(e) => setNewClassroom(prev => ({ ...prev, startDate: e.target.value }))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="endDate">End Date</Label>
                    <Input
                      id="endDate"
                      type="date"
                      value={newClassroom.endDate}
                      onChange={(e) => setNewClassroom(prev => ({ ...prev, endDate: e.target.value }))}
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label>Select Courses</Label>
                  <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {mockCourses.map(course => (
                      <label key={course.id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={newClassroom.courseIds.includes(course.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setNewClassroom(prev => ({
                                ...prev,
                                courseIds: [...prev.courseIds, course.id]
                              }));
                            } else {
                              setNewClassroom(prev => ({
                                ...prev,
                                courseIds: prev.courseIds.filter(id => id !== course.id)
                              }));
                            }
                          }}
                        />
                        <span className="text-sm">{course.title}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label>Select Students</Label>
                  <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {students.map(student => (
                      <label key={student.id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={newClassroom.studentIds.includes(student.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setNewClassroom(prev => ({
                                ...prev,
                                studentIds: [...prev.studentIds, student.id]
                              }));
                            } else {
                              setNewClassroom(prev => ({
                                ...prev,
                                studentIds: prev.studentIds.filter(id => id !== student.id)
                              }));
                            }
                          }}
                        />
                        <span className="text-sm">{student.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div className="flex items-center justify-end space-x-3 pt-4">
                  <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateClassroom}>
                    Create Classroom
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">
                  {isLearner ? 'Enrolled Classrooms' : 'Total Classrooms'}
                </p>
                <p className="text-2xl font-bold text-blue-700">{classrooms.length}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Active Sessions</p>
                <p className="text-2xl font-bold text-green-700">
                  {classrooms.filter(c => c.status === 'active').length}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">
                  {isLearner ? 'My Progress' : 'Avg. Progress'}
                </p>
                <p className="text-2xl font-bold text-orange-700">
                  {Math.round(classrooms.reduce((sum, c) => sum + (c.metrics?.averageProgress || c.progress || 0), 0) / (classrooms.length || 1))}%
                </p>
              </div>
              <Target className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">
                  {isLearner ? 'Certificates' : 'Completions'}
                </p>
                <p className="text-2xl font-bold text-purple-700">
                  {classrooms.reduce((sum, c) => sum + (c.metrics?.completedStudents || 0), 0)}
                </p>
              </div>
              <Award className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Classrooms List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">
            {isLearner ? 'My Training Programs' : 'Classroom Overview'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {classrooms.length === 0 ? (
            <div className="text-center py-12">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {isLearner ? 'No classrooms enrolled' : 'No classrooms created yet'}
              </h3>
              <p className="text-gray-600">
                {isLearner 
                  ? 'You haven\'t been enrolled in any training programs yet.'
                  : 'Create your first classroom to start cohort-based training.'
                }
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {classrooms.map((classroom) => (
                <Card key={classroom.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {classroom.name}
                        </h3>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                          {classroom.description}
                        </p>
                      </div>
                      <Badge className={getStatusColor(classroom.status)}>
                        {classroom.status}
                      </Badge>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Progress</span>
                        <span className="font-medium">
                          {isLearner ? `${classroom.progress || 0}%` : `${classroom.metrics?.averageProgress || 0}%`}
                        </span>
                      </div>
                      <Progress 
                        value={isLearner ? (classroom.progress || 0) : (classroom.metrics?.averageProgress || 0)} 
                        className="h-2" 
                      />

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center text-gray-600">
                          <Users className="w-4 h-4 mr-1" />
                          <span>
                            {isLearner ? 'Classmates' : 'Students'}: {classroom.metrics?.totalStudents || classroom.studentIds?.length || 0}
                          </span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <BookOpen className="w-4 h-4 mr-1" />
                          <span>
                            Courses: {classroom.courseIds?.length || 0}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="w-4 h-4 mr-1" />
                        <span>
                          {new Date(classroom.startDate).toLocaleDateString()} - {new Date(classroom.endDate).toLocaleDateString()}
                        </span>
                      </div>

                      {!isLearner && (
                        <div className="text-sm text-gray-600">
                          <strong>Trainer:</strong> {classroom.trainerName}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 mt-4">
                      <Button 
                        size="sm" 
                        className="flex-1"
                        onClick={() => navigate(`/classroom/${classroom.id}`)}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View Details
                      </Button>
                      {(isAdmin || (isInstructor && classroom.trainerId === user.id)) && (
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => navigate(`/classroom/${classroom.id}/manage`)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Classrooms;
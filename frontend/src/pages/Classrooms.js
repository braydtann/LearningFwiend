import React, { useState, useEffect } from 'react';
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
import { mockUsers, mockCourses, mockPrograms, mockDepartments } from '../data/mockData';
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
  UserPlus,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Classrooms = () => {
  const { user, isAdmin, isInstructor, isLearner, getAllUsers, getAllCourses, getAllPrograms, getAllClassrooms, createClassroom, getAllDepartments } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [realUsers, setRealUsers] = useState([]);
  const [realCourses, setRealCourses] = useState([]);
  const [realPrograms, setRealPrograms] = useState([]);
  const [realDepartments, setRealDepartments] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [loadingPrograms, setLoadingPrograms] = useState(false);
  const [loadingDepartments, setLoadingDepartments] = useState(false);
  const [loadingClassrooms, setLoadingClassrooms] = useState(true);
  const [newClassroom, setNewClassroom] = useState({
    name: '',
    batchId: '',
    description: '',
    trainerId: '',
    courseIds: [],
    programIds: [], // New: Program selection
    studentIds: [],
    departmentId: '', // New: Department selection
    startDate: '',
    endDate: ''
  });

  // Load real users, courses, programs, and classrooms from backend on component mount
  useEffect(() => {
    loadUsers();
    loadCourses();
    loadPrograms();
    loadClassrooms();
  }, []);

  const loadClassrooms = async () => {
    setLoadingClassrooms(true);
    try {
      if (getAllClassrooms) {
        const result = await getAllClassrooms();
        if (result.success) {
          setClassrooms(result.classrooms);
        } else {
          console.error('Failed to load classrooms:', result.error);
          setClassrooms([]);
        }
      } else {
        setClassrooms([]);
      }
    } catch (error) {
      console.error('Error loading classrooms:', error);
      setClassrooms([]);
    } finally {
      setLoadingClassrooms(false);
    }
  };

  const loadUsers = async () => {
    setLoadingUsers(true);
    try {
      if (getAllUsers) {
        const result = await getAllUsers();
        if (result.success) {
          setRealUsers(result.users);
        } else {
          console.error('Failed to load users:', result.error);
          setRealUsers(mockUsers);
        }
      } else {
        setRealUsers(mockUsers);
      }
    } catch (error) {
      console.error('Error loading users:', error);
      setRealUsers(mockUsers);
    } finally {
      setLoadingUsers(false);
    }
  };

  const loadCourses = async () => {
    setLoadingCourses(true);
    try {
      if (getAllCourses) {
        const result = await getAllCourses();
        if (result.success) {
          setRealCourses(result.courses);
        } else {
          console.error('Failed to load courses:', result.error);
          setRealCourses(mockCourses);
        }
      } else {
        setRealCourses(mockCourses);
      }
    } catch (error) {
      console.error('Error loading courses:', error);
      setRealCourses(mockCourses);
    } finally {
      setLoadingCourses(false);
    }
  };

  const loadPrograms = async () => {
    setLoadingPrograms(true);
    try {
      if (getAllPrograms) {
        const result = await getAllPrograms();
        if (result.success) {
          setRealPrograms(result.programs);
        } else {
          console.error('Failed to load programs:', result.error);
          setRealPrograms(mockPrograms);
        }
      } else {
        setRealPrograms(mockPrograms);
      }
    } catch (error) {
      console.error('Error loading programs:', error);
      setRealPrograms(mockPrograms);
    } finally {
      setLoadingPrograms(false);
    }
  };

  // Reset form function
  const resetForm = () => {
    setNewClassroom({
      name: '',
      batchId: '',
      description: '',
      trainerId: '',
      courseIds: [],
      programIds: [],
      studentIds: [],
      departmentId: '',
      startDate: '',
      endDate: ''
    });
  };

  // Use real data from backend with fallbacks to mock data
  const allUsers = realUsers.length > 0 ? realUsers : mockUsers;
  const allCourses = realCourses.length > 0 ? realCourses : mockCourses;
  const allPrograms = realPrograms.length > 0 ? realPrograms : mockPrograms;
  
  const instructors = allUsers.filter(u => u.role === 'instructor');
  const students = allUsers.filter(u => u.role === 'learner');

  // Simple access status check
  const getAccessStatus = (classroom) => {
    if (!classroom.endDate) return { status: 'active', message: 'Active' };
    
    const endDate = new Date(classroom.endDate);
    const now = new Date();
    const daysUntilEnd = Math.ceil((endDate - now) / (1000 * 60 * 60 * 24));
    
    if (daysUntilEnd < 0) {
      return { status: 'expired', message: 'Expired' };
    } else if (daysUntilEnd <= 7) {
      return { status: 'ending-soon', message: `Ending in ${daysUntilEnd} days` };
    } else {
      return { status: 'active', message: 'Active' };
    }
  };

  const handleCreateClassroom = async () => {
    if (!newClassroom.name || !newClassroom.batchId || !newClassroom.trainerId || !newClassroom.departmentId) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information including name, batch ID, trainer, and department.",
        variant: "destructive",
      });
      return;
    }

    if (newClassroom.courseIds.length === 0 && newClassroom.programIds.length === 0) {
      toast({
        title: "No content selected",
        description: "Please select at least one course or program for the classroom.",
        variant: "destructive",
      });
      return;
    }

    try {
      // Create classroom using backend API
      const result = await createClassroom({
        name: newClassroom.name,
        batchId: newClassroom.batchId,
        description: newClassroom.description,
        trainerId: newClassroom.trainerId,  // Fixed: use trainerId not instructorId
        courseIds: newClassroom.courseIds,
        programIds: newClassroom.programIds,
        studentIds: newClassroom.studentIds,
        department: newClassroom.departmentId,  // Fixed: use department not departmentId
        startDate: newClassroom.startDate,
        endDate: newClassroom.endDate
      });

      if (result.success) {
        toast({
          title: "Classroom created successfully!",
          description: `${newClassroom.name} (${newClassroom.batchId}) has been created and is ready for students.`,
        });

        // Reload classrooms to show the new one
        await loadClassrooms();
        
        resetForm();
        setIsCreateModalOpen(false);
      } else {
        toast({
          title: "Failed to create classroom",
          description: result.error || "An error occurred while creating the classroom.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error creating classroom:', error);
      toast({
        title: "Error creating classroom",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    }
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
                    <Label htmlFor="batchId">Classroom Batch ID</Label>
                    <Input
                      id="batchId"
                      placeholder="Enter batch ID (e.g., BATCH-2024-Q2-001)"
                      value={newClassroom.batchId}
                      onChange={(e) => setNewClassroom(prev => ({ ...prev, batchId: e.target.value }))}
                    />
                  </div>
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
                      {loadingUsers ? (
                        <SelectItem value="loading" disabled>
                          Loading trainers...
                        </SelectItem>
                      ) : instructors.length === 0 ? (
                        <SelectItem value="none" disabled>
                          No instructors available
                        </SelectItem>
                      ) : (
                        instructors.map(instructor => (
                          <SelectItem key={instructor.id} value={instructor.id}>
                            {instructor.full_name || instructor.name} ({instructor.username || instructor.email})
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
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
                  <Label>Select Department</Label>
                  <Select 
                    value={newClassroom.departmentId} 
                    onValueChange={(value) => setNewClassroom(prev => ({ ...prev, departmentId: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select department" />
                    </SelectTrigger>
                    <SelectContent>
                      {mockDepartments.map(department => (
                        <SelectItem key={department.id} value={department.id}>
                          {department.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Select Programs</Label>
                  <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {loadingPrograms ? (
                      <div className="text-sm text-gray-500 p-2">Loading programs...</div>
                    ) : allPrograms.length === 0 ? (
                      <div className="text-sm text-gray-500 p-2">No programs available</div>
                    ) : (
                      allPrograms.map(program => (
                        <label key={program.id} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={newClassroom.programIds.includes(program.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setNewClassroom(prev => ({
                                  ...prev,
                                  programIds: [...prev.programIds, program.id]
                                }));
                              } else {
                                setNewClassroom(prev => ({
                                  ...prev,
                                  programIds: prev.programIds.filter(id => id !== program.id)
                                }));
                              }
                            }}
                          />
                          <div className="flex-1">
                            <span className="text-sm font-medium">{program.title || program.name}</span>
                            <p className="text-xs text-gray-500 mt-1">{program.description}</p>
                          </div>
                        </label>
                      ))
                    )}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label>Select Courses</Label>
                  <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {loadingCourses ? (
                      <div className="text-sm text-gray-500 p-2">Loading courses...</div>
                    ) : allCourses.length === 0 ? (
                      <div className="text-sm text-gray-500 p-2">No courses available</div>
                    ) : (
                      allCourses.map(course => (
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
                      ))
                    )}
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
                        <span className="text-sm">{student.full_name || student.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div className="flex items-center justify-end space-x-3 pt-4">
                  <Button variant="outline" onClick={() => {
                    setIsCreateModalOpen(false);
                    resetForm();
                  }}>
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
                        {classroom.batchId && (
                          <p className="text-xs text-blue-600 font-medium mb-1">
                            Batch ID: {classroom.batchId}
                          </p>
                        )}
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

                      <div className="flex items-center text-sm text-gray-600 mb-2">
                        <Calendar className="w-4 h-4 mr-1" />
                        <span>
                          {new Date(classroom.startDate).toLocaleDateString()} - {new Date(classroom.endDate).toLocaleDateString()}
                        </span>
                      </div>

                      {/* Access Status Indicator */}
                      {(() => {
                        const accessStatus = getAccessStatus(classroom);
                        return (
                          <div className={`flex items-center text-sm p-2 rounded-lg ${
                            accessStatus.status === 'expired' 
                              ? 'bg-red-50 border border-red-200 text-red-800' 
                              : accessStatus.status === 'ending-soon'
                              ? 'bg-orange-50 border border-orange-200 text-orange-800'
                              : 'bg-green-50 border border-green-200 text-green-800'
                          }`}>
                            {accessStatus.status === 'expired' ? (
                              <XCircle className="w-4 h-4 mr-1" />
                            ) : accessStatus.status === 'ending-soon' ? (
                              <AlertTriangle className="w-4 h-4 mr-1" />
                            ) : (
                              <CheckCircle className="w-4 h-4 mr-1" />
                            )}
                            <span className="font-medium">
                              {accessStatus.status === 'expired' ? 'Expired' : 
                               accessStatus.status === 'ending-soon' ? 'Ending Soon' : 'Active'}
                            </span>
                            <span className="ml-2 text-xs">
                              {accessStatus.message}
                            </span>
                          </div>
                        );
                      })()}

                      {!isLearner && (
                        <div className="text-sm text-gray-600">
                          <strong>Trainer:</strong> {classroom.trainerName}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 mt-4">
                      {(() => {
                        const accessStatus = getAccessStatus(classroom);
                        const isExpired = accessStatus.status === 'expired';
                        
                        return (
                          <>
                            <Button 
                              size="sm" 
                              className="flex-1"
                              onClick={() => navigate(`/classroom/${classroom.id}`)}
                              disabled={isLearner && isExpired}
                              variant={isLearner && isExpired ? "outline" : "default"}
                            >
                              <Eye className="w-4 h-4 mr-1" />
                              {isLearner && isExpired ? 'Access Expired' : 'View Details'}
                            </Button>
                            {(isAdmin || (isInstructor && classroom.trainerId === user.id)) && (
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => navigate(`/classroom/${classroom.id}?mode=edit`)}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                            )}
                          </>
                        );
                      })()}
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
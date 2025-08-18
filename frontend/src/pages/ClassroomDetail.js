import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { mockClassrooms, getClassroomStudents, mockCourses } from '../data/mockData';
import { 
  ArrowLeft,
  Users, 
  Calendar, 
  BookOpen, 
  Clock,
  Award,
  Target,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Edit,
  Save,
  X
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const ClassroomDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isEditMode = searchParams.get('mode') === 'edit';
  const { user, isLearner, getAllCourses, getClassroomById, updateClassroom, getAllUsers, getAllPrograms } = useAuth();
  const { toast } = useToast();
  
  const [classroom, setClassroom] = useState(null);
  const [courses, setCourses] = useState([]);
  const [loadingClassroom, setLoadingClassroom] = useState(true);
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [coursesError, setCoursesError] = useState(null);
  
  // Edit mode states
  const [editData, setEditData] = useState({
    name: '',
    batchId: '',
    description: '',
    trainerId: '',
    courseIds: [],
    programIds: [],
    department: '',
    startDate: '',
    endDate: '',
    maxStudents: 30
  });
  const [availableUsers, setAvailableUsers] = useState([]);
  const [availableCourses, setAvailableCourses] = useState([]);
  const [availablePrograms, setAvailablePrograms] = useState([]);
  const [saving, setSaving] = useState(false);
  
  // Load classroom data from backend
  useEffect(() => {
    loadClassroomData();
  }, [id]);

  // Load additional data for edit mode
  useEffect(() => {
    if (isEditMode) {
      loadEditData();
    }
  }, [isEditMode]);

  const loadClassroomData = async () => {
    setLoadingClassroom(true);
    try {
      const result = await getClassroomById(id);
      if (result.success) {
        setClassroom(result.classroom);
        setEditData(result.classroom);
      } else {
        // Fallback to mock data
        const mockClassroom = mockClassrooms.find(c => c.id === id);
        if (mockClassroom) {
          setClassroom(mockClassroom);
          setEditData(mockClassroom);
        } else {
          toast({
            title: "Classroom not found",
            description: "The requested classroom could not be found.",
            variant: "destructive",
          });
          navigate('/classrooms');
        }
      }
    } catch (error) {
      console.error('Error loading classroom:', error);
      // Fallback to mock data
      const mockClassroom = mockClassrooms.find(c => c.id === id);
      if (mockClassroom) {
        setClassroom(mockClassroom);
        setEditData(mockClassroom);
      }
    } finally {
      setLoadingClassroom(false);
    }
  };

  const loadEditData = async () => {
    try {
      // Load users, courses, programs for edit dropdowns
      const [usersResult, coursesResult, programsResult] = await Promise.all([
        getAllUsers(),
        getAllCourses(),
        getAllPrograms()
      ]);

      if (usersResult.success) {
        setAvailableUsers(usersResult.users);
      }
      
      if (coursesResult.success) {
        setAvailableCourses(coursesResult.courses);
      }
      
      if (programsResult.success) {
        setAvailablePrograms(programsResult.programs);
      }
    } catch (error) {
      console.error('Error loading edit data:', error);
    }
  };

  const students = classroom ? getClassroomStudents(classroom.id) : [];

  const loadCourses = async () => {
    setLoadingCourses(true);
    setCoursesError(null);
    try {
      const result = await getAllCourses();
      if (result.success) {
        // Filter courses that are assigned to this classroom
        const classroomCourses = result.courses.filter(course => 
          classroom?.courseIds?.includes(course.id)
        );
        setCourses(classroomCourses);
      } else {
        // Fallback to mock courses if backend fails
        const fallbackCourses = classroom?.courseIds?.map(courseId => 
          mockCourses.find(course => course.id === courseId)
        ).filter(Boolean) || [];
        setCourses(fallbackCourses);
        setCoursesError('Failed to load courses from backend, using cached data');
        console.warn('Failed to load courses from backend:', result.error);
      }
    } catch (error) {
      // Fallback to mock courses
      console.error('Error loading courses:', error);
      const fallbackCourses = classroom?.courseIds?.map(courseId => 
        mockCourses.find(course => course.id === courseId)
      ).filter(Boolean) || [];
      setCourses(fallbackCourses);
      setCoursesError('Network error loading courses');
    } finally {
      setLoadingCourses(false);
    }
  };

  // Load courses when classroom data is available
  useEffect(() => {
    if (classroom) {
      loadCourses();
    }
  }, [classroom]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const result = await updateClassroom(id, editData);
      if (result.success) {
        setClassroom(result.classroom);
        toast({
          title: "Classroom updated",
          description: "The classroom has been successfully updated.",
        });
        // Exit edit mode
        navigate(`/classroom/${id}`);
      } else {
        toast({
          title: "Update failed",
          description: result.error || "Failed to update classroom.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An unexpected error occurred while updating the classroom.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    // Reset edit data and exit edit mode
    setEditData(classroom);
    navigate(`/classroom/${id}`);
  };

  const handleInputChange = (field, value) => {
    setEditData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (loadingClassroom) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Loading classroom...</h3>
        <p className="text-gray-600">Please wait while we fetch the classroom details.</p>
      </div>
    );
  }

  if (!classroom) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Classroom not found</h1>
        <Button onClick={() => navigate('/classrooms')}>
          Back to Classrooms
        </Button>
      </div>
    );
  }

  const getPerformanceLevel = (score) => {
    if (score >= 90) return { level: 'Excellent', color: 'text-green-600' };
    if (score >= 80) return { level: 'Good', color: 'text-blue-600' };
    if (score >= 70) return { level: 'Average', color: 'text-orange-600' };
    return { level: 'Needs Improvement', color: 'text-red-600' };
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => navigate('/classrooms')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div className="h-6 border-l border-gray-300"></div>
          <nav className="text-sm text-gray-500">
            <span>Classrooms</span> / <span className="text-gray-900">{classroom.name}</span>
          </nav>
        </div>

        {/* Edit Mode Controls */}
        <div className="flex items-center space-x-2">
          {isEditMode ? (
            <>
              <Button 
                variant="outline" 
                onClick={handleCancel}
                disabled={saving}
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button 
                onClick={handleSave}
                disabled={saving}
              >
                <Save className="w-4 h-4 mr-2" />
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </>
          ) : (
            <Button 
              variant="outline"
              onClick={() => navigate(`/classroom/${id}?mode=edit`)}
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit Classroom
            </Button>
          )}
        </div>
      </div>

      {/* Edit Form - Only show in edit mode */}
      {isEditMode && (
        <Card>
          <CardHeader>
            <CardTitle>Edit Classroom</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">Classroom Name *</Label>
                <Input
                  id="name"
                  value={editData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter classroom name"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="batchId">Batch ID</Label>
                <Input
                  id="batchId"
                  value={editData.batchId}
                  onChange={(e) => handleInputChange('batchId', e.target.value)}
                  placeholder="e.g., BATCH-2024-Q1-001"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={editData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe the purpose and goals of this classroom"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="trainer">Trainer</Label>
                <Select 
                  value={editData.trainerId} 
                  onValueChange={(value) => handleInputChange('trainerId', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select trainer" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableUsers
                      .filter(user => user.role === 'instructor' || user.role === 'admin')
                      .map(user => (
                        <SelectItem key={user.id} value={user.id}>
                          {user.full_name} ({user.email})
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="department">Department</Label>
                <Select 
                  value={editData.department} 
                  onValueChange={(value) => handleInputChange('department', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Technology">Technology</SelectItem>
                    <SelectItem value="Marketing">Marketing</SelectItem>
                    <SelectItem value="Sales">Sales</SelectItem>
                    <SelectItem value="Human Resources">Human Resources</SelectItem>
                    <SelectItem value="Finance">Finance</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="startDate">Start Date</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={editData.startDate}
                  onChange={(e) => handleInputChange('startDate', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="endDate">End Date</Label>
                <Input
                  id="endDate"
                  type="date"
                  value={editData.endDate}
                  onChange={(e) => handleInputChange('endDate', e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="maxStudents">Maximum Students</Label>
              <Input
                id="maxStudents"
                type="number"
                value={editData.maxStudents}
                onChange={(e) => handleInputChange('maxStudents', parseInt(e.target.value) || 30)}
                min="1"
                max="100"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Classroom Overview */}
      <Card>
        <CardContent className="p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-4">
                <h1 className="text-3xl font-bold text-gray-900">{classroom.name}</h1>
                <Badge 
                  className={
                    classroom.status === 'active' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }
                >
                  {classroom.status}
                </Badge>
              </div>
              <p className="text-lg text-gray-600 mb-6">{classroom.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="flex items-center space-x-3">
                  <Calendar className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Duration</p>
                    <p className="font-medium">
                      {new Date(classroom.startDate).toLocaleDateString()} - {new Date(classroom.endDate).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Students</p>
                    <p className="font-medium">{classroom.metrics?.totalStudents || classroom.totalStudents || 0}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <BookOpen className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Courses</p>
                    <p className="font-medium">{courses.length}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {!isLearner && (
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-900 mb-4">Trainer KPIs</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-700">{classroom.metrics?.averageProgress || 0}%</div>
                  <div className="text-sm text-blue-600">Average Progress</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-700">{classroom.metrics?.completionRate || 0}%</div>
                  <div className="text-sm text-green-600">Completion Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-700">{classroom.metrics?.averageTestScore || 0}</div>
                  <div className="text-sm text-orange-600">Avg. Test Score</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-700">
                    {classroom.metrics?.averageTimeToCompletion ? `${classroom.metrics.averageTimeToCompletion}h` : 'N/A'}
                  </div>
                  <div className="text-sm text-purple-600">Avg. Time to Complete</div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabs Content */}
      <Tabs defaultValue={isLearner ? "courses" : "students"} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          {!isLearner && <TabsTrigger value="students">Students</TabsTrigger>}
          <TabsTrigger value="courses">Courses</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>
        
        {!isLearner && (
          <TabsContent value="students" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Student Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Student</TableHead>
                      <TableHead>Progress</TableHead>
                      <TableHead>Test Scores</TableHead>
                      <TableHead>Time Spent</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {students.map((student) => {
                      const avgScore = student.testScores?.length > 0 
                        ? student.testScores.reduce((sum, test) => sum + test.score, 0) / student.testScores.length
                        : 0;
                      const performance = getPerformanceLevel(avgScore);
                      
                      return (
                        <TableRow key={student.id}>
                          <TableCell>
                            <div className="flex items-center space-x-3">
                              <img 
                                src={student.avatar} 
                                alt={student.name}
                                className="w-8 h-8 rounded-full object-cover"
                              />
                              <div>
                                <p className="font-medium">{student.name}</p>
                                <p className="text-sm text-gray-500">{student.email}</p>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span>{student.progress}%</span>
                              </div>
                              <Progress value={student.progress} className="h-2" />
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className={`font-medium ${performance.color}`}>
                              {avgScore.toFixed(0)} - {performance.level}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center text-sm text-gray-600">
                              <Clock className="w-4 h-4 mr-1" />
                              {Math.round(student.totalTimeSpent / 60)}h {student.totalTimeSpent % 60}m
                            </div>
                          </TableCell>
                          <TableCell>
                            {student.progress === 100 ? (
                              <Badge className="bg-green-100 text-green-800">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Completed
                              </Badge>
                            ) : student.progress > 0 ? (
                              <Badge className="bg-orange-100 text-orange-800">
                                <TrendingUp className="w-3 h-3 mr-1" />
                                In Progress
                              </Badge>
                            ) : (
                              <Badge className="bg-gray-100 text-gray-800">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                Not Started
                              </Badge>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        )}
        
        <TabsContent value="courses" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Curriculum</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingCourses ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-gray-500">Loading courses...</div>
                </div>
              ) : coursesError ? (
                <div className="text-center py-8">
                  <div className="text-amber-600 mb-2">⚠️ {coursesError}</div>
                  <Button 
                    onClick={loadCourses} 
                    variant="outline" 
                    size="sm"
                  >
                    Retry Loading Courses
                  </Button>
                </div>
              ) : courses.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No courses assigned to this classroom
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {courses.map((course) => (
                    <Card key={course.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-start space-x-4">
                          <img 
                            src={course.thumbnailUrl || course.thumbnail || '/api/placeholder/64/64'} 
                            alt={course.title}
                            className="w-16 h-16 rounded-lg object-cover flex-shrink-0"
                            onError={(e) => {
                              e.target.src = '/api/placeholder/64/64';
                            }}
                          />
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 mb-2">{course.title}</h4>
                            <p className="text-sm text-gray-600 mb-3 line-clamp-2">{course.description}</p>
                            <div className="flex items-center justify-between text-sm text-gray-500">
                              <div className="flex items-center">
                                <Clock className="w-4 h-4 mr-1" />
                                {course.duration}
                              </div>
                              <div className="flex items-center">
                                <BookOpen className="w-4 h-4 mr-1" />
                                {course.totalLessons || course.modules?.length || 0} lessons
                              </div>
                            </div>
                            <Button 
                              size="sm" 
                              className="w-full mt-3"
                              onClick={() => navigate(`/course/${course.id}`)}
                            >
                              {isLearner ? 'Continue Learning' : 'View Course'}
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Progress Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Overall Progress</span>
                    <span className="font-semibold">{classroom.metrics?.averageProgress || 0}%</span>
                  </div>
                  <Progress value={classroom.metrics?.averageProgress || 0} className="h-3" />
                  
                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-lg font-bold text-green-700">{classroom.metrics?.completedStudents || 0}</div>
                      <div className="text-sm text-green-600">Completed</div>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <div className="text-lg font-bold text-orange-700">
                        {(classroom.metrics?.totalStudents || classroom.totalStudents || 0) - (classroom.metrics?.completedStudents || classroom.completedStudents || 0)}
                      </div>
                      <div className="text-sm text-orange-600">In Progress</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center">
                      <Target className="h-5 w-5 text-blue-600 mr-2" />
                      <span className="text-sm font-medium">Average Test Score</span>
                    </div>
                    <span className="font-bold text-blue-700">{classroom.metrics?.averageTestScore || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <div className="flex items-center">
                      <Award className="h-5 w-5 text-purple-600 mr-2" />
                      <span className="text-sm font-medium">Completion Rate</span>
                    </div>
                    <span className="font-bold text-purple-700">{classroom.metrics?.completionRate || 0}%</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div className="flex items-center">
                      <Clock className="h-5 w-5 text-orange-600 mr-2" />
                      <span className="text-sm font-medium">Avg. Time to Complete</span>
                    </div>
                    <span className="font-bold text-orange-700">
                      {classroom.metrics?.averageTimeToCompletion ? `${classroom.metrics.averageTimeToCompletion}h` : 'N/A'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ClassroomDetail;
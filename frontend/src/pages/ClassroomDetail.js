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
  const { user, isLearner, getAllCourses } = useAuth();
  
  const [courses, setCourses] = useState([]);
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [coursesError, setCoursesError] = useState(null);
  
  const classroom = mockClassrooms.find(c => c.id === id);
  const students = getClassroomStudents(id);
  
  // Load courses from backend
  useEffect(() => {
    loadCourses();
  }, []);

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
      <div className="flex items-center space-x-4 mb-6">
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
                    <p className="font-medium">{classroom.metrics.totalStudents}</p>
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
                  <div className="text-2xl font-bold text-blue-700">{classroom.metrics.averageProgress}%</div>
                  <div className="text-sm text-blue-600">Average Progress</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-700">{classroom.metrics.completionRate}%</div>
                  <div className="text-sm text-green-600">Completion Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-700">{classroom.metrics.averageTestScore}</div>
                  <div className="text-sm text-orange-600">Avg. Test Score</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-700">
                    {classroom.metrics.averageTimeToCompletion ? `${classroom.metrics.averageTimeToCompletion}h` : 'N/A'}
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
                    <span className="font-semibold">{classroom.metrics.averageProgress}%</span>
                  </div>
                  <Progress value={classroom.metrics.averageProgress} className="h-3" />
                  
                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-lg font-bold text-green-700">{classroom.metrics.completedStudents}</div>
                      <div className="text-sm text-green-600">Completed</div>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <div className="text-lg font-bold text-orange-700">
                        {classroom.metrics.totalStudents - classroom.metrics.completedStudents}
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
                    <span className="font-bold text-blue-700">{classroom.metrics.averageTestScore}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <div className="flex items-center">
                      <Award className="h-5 w-5 text-purple-600 mr-2" />
                      <span className="text-sm font-medium">Completion Rate</span>
                    </div>
                    <span className="font-bold text-purple-700">{classroom.metrics.completionRate}%</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div className="flex items-center">
                      <Clock className="h-5 w-5 text-orange-600 mr-2" />
                      <span className="text-sm font-medium">Avg. Time to Complete</span>
                    </div>
                    <span className="font-bold text-orange-700">
                      {classroom.metrics.averageTimeToCompletion ? `${classroom.metrics.averageTimeToCompletion}h` : 'N/A'}
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
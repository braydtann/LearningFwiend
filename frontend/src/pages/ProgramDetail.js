import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { 
  ArrowLeft,
  Award, 
  Users, 
  BookOpen, 
  Clock,
  Calendar,
  Target,
  CheckCircle,
  Play,
  Lock,
  UnlockIcon
} from 'lucide-react';

const ProgramDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, getProgramById, getAllCourses } = useAuth();
  
  const [program, setProgram] = useState(null);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadProgramDetails = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Load program details
        const programResult = await getProgramById(id);
        if (programResult.success) {
          setProgram(programResult.program);
          
          // Load courses if program has courseIds
          if (programResult.program.courseIds && programResult.program.courseIds.length > 0) {
            const coursesResult = await getAllCourses();
            if (coursesResult.success) {
              // Filter courses to only show those in this program
              const programCourses = coursesResult.courses.filter(course => 
                programResult.program.courseIds.includes(course.id)
              );
              setCourses(programCourses);
            }
          }
        } else {
          setError(programResult.error);
        }
      } catch (err) {
        console.error('Error loading program details:', err);
        setError('Failed to load program details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadProgramDetails();
    }
  }, [id, getProgramById, getAllCourses]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading program details...</p>
        </div>
      </div>
    );
  }

  if (error || !program) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          {error || 'Program not found'}
        </h1>
        <Button onClick={() => navigate('/programs')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Programs
        </Button>
      </div>
    );
  }

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner':
        return 'bg-green-100 text-green-800';
      case 'Intermediate':
        return 'bg-orange-100 text-orange-800';
      case 'Advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate('/programs')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div className="h-6 border-l border-gray-300"></div>
        <nav className="text-sm text-gray-500">
          <span>Programs</span> / <span className="text-gray-900">{program.name}</span>
        </nav>
      </div>

      {/* Program Overview */}
      <Card>
        <CardContent className="p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-4">
                <h1 className="text-3xl font-bold text-gray-900">{program.name}</h1>
                <Badge className={getDifficultyColor(program.difficulty)}>
                  {program.difficulty}
                </Badge>
                <Badge variant={program.status === 'active' ? 'default' : 'secondary'}>
                  {program.status}
                </Badge>
              </div>
              <p className="text-lg text-gray-600 mb-6">{program.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="flex items-center space-x-3">
                  <BookOpen className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Courses</p>
                    <p className="font-medium">{program.totalCourses}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Enrolled Students</p>
                    <p className="font-medium">{program.enrolledStudents}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Duration</p>
                    <p className="font-medium">{program.duration}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <Target className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Estimated Hours</p>
                    <p className="font-medium">{program.estimatedHours}h</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">Program Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-700">{program.enrolledStudents}</div>
                <div className="text-sm text-blue-600">Total Enrollments</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-700">85%</div>
                <div className="text-sm text-green-600">Completion Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-700">4.8</div>
                <div className="text-sm text-orange-600">Average Rating</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Course Sequence */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Learning Path</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {courses.map((course, index) => (
              <div key={course.id} className="relative">
                {/* Connector Line */}
                {index < courses.length - 1 && (
                  <div className="absolute left-6 top-20 w-0.5 h-16 bg-gray-200"></div>
                )}
                
                <Card className={`transition-shadow ${
                  course.status === 'locked' 
                    ? 'border-gray-300 bg-gray-50' 
                    : course.status === 'completed'
                    ? 'border-green-300 bg-green-50 hover:shadow-md'
                    : 'hover:shadow-md'
                }`}>
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      {/* Step Number with Status Icon */}
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg flex-shrink-0 ${
                        course.status === 'locked' 
                          ? 'bg-gray-400 text-white'
                          : course.status === 'completed'
                          ? 'bg-green-600 text-white'
                          : course.status === 'in-progress'
                          ? 'bg-orange-600 text-white'
                          : 'bg-blue-600 text-white'
                      }`}>
                        {course.status === 'locked' ? (
                          <Lock className="w-5 h-5" />
                        ) : course.status === 'completed' ? (
                          <CheckCircle className="w-5 h-5" />
                        ) : (
                          index + 1
                        )}
                      </div>
                      
                      {/* Course Thumbnail */}
                      <img 
                        src={course.thumbnail} 
                        alt={course.title}
                        className={`w-20 h-20 rounded-lg object-cover flex-shrink-0 ${
                          course.status === 'locked' ? 'grayscale opacity-50' : ''
                        }`}
                      />
                      
                      {/* Course Details */}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className={`text-lg font-semibold mb-0 ${
                            course.status === 'locked' ? 'text-gray-500' : 'text-gray-900'
                          }`}>
                            {course.title}
                          </h3>
                          <Badge variant="outline" className={
                            course.status === 'locked' ? 'border-gray-400 text-gray-500' :
                            course.status === 'completed' ? 'border-green-500 text-green-700 bg-green-50' :
                            course.status === 'in-progress' ? 'border-orange-500 text-orange-700 bg-orange-50' :
                            'border-blue-500 text-blue-700 bg-blue-50'
                          }>
                            {course.status === 'locked' ? 'Locked' :
                             course.status === 'completed' ? 'Completed' :
                             course.status === 'in-progress' ? 'In Progress' : 'Available'}
                          </Badge>
                        </div>

                        <p className={`text-sm mb-3 line-clamp-2 ${
                          course.status === 'locked' ? 'text-gray-400' : 'text-gray-600'
                        }`}>
                          {course.description}
                        </p>
                        
                        {/* Progress Bar for In-Progress Courses */}
                        {course.status === 'in-progress' && (
                          <div className="mb-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs text-gray-600">Progress</span>
                              <span className="text-xs text-gray-600">{course.progress}%</span>
                            </div>
                            <Progress value={course.progress} className="h-2" />
                          </div>
                        )}
                        
                        <div className={`flex items-center space-x-4 text-sm mb-3 ${
                          course.status === 'locked' ? 'text-gray-400' : 'text-gray-500'
                        }`}>
                          <div className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {course.duration}
                          </div>
                          <div className="flex items-center">
                            <BookOpen className="w-4 h-4 mr-1" />
                            {course.totalLessons} lessons
                          </div>
                          <div className="flex items-center">
                            <Users className="w-4 h-4 mr-1" />
                            {course.enrolledStudents} students
                          </div>
                        </div>

                        <Badge variant="secondary" className={
                          course.status === 'locked' ? 'bg-gray-200 text-gray-500' : ''
                        }>
                          {course.category}
                        </Badge>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex flex-col space-y-2 flex-shrink-0">
                        {course.status === 'locked' ? (
                          <div className="text-center">
                            <Lock className="w-6 h-6 text-gray-400 mx-auto mb-2" />
                            <p className="text-xs text-gray-500 mb-2">Complete previous course to unlock</p>
                            <Button size="sm" disabled>
                              Locked
                            </Button>
                          </div>
                        ) : (
                          <Button 
                            size="sm"
                            onClick={() => navigate(`/course/${course.id}`)}
                            className={
                              course.status === 'completed' ? 'bg-green-600 hover:bg-green-700' : ''
                            }
                          >
                            {course.status === 'completed' ? (
                              <>
                                <CheckCircle className="w-4 h-4 mr-1" />
                                Review Course
                              </>
                            ) : (
                              <>
                                <Play className="w-4 h-4 mr-1" />
                                {course.status === 'in-progress' ? 'Continue Course' : 'Start Course'}
                              </>
                            )}
                          </Button>
                        )}
                        <div className="text-xs text-gray-500 text-center">
                          Step {index + 1} of {courses.length}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Final Test Section */}
      {courses.every(course => course.status === 'completed') && (
        <Card className="bg-gradient-to-r from-purple-50 to-indigo-50 border-purple-200">
          <CardContent className="p-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center">
                  <Award className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-purple-900 mb-2">Final Assessment Available!</h3>
                  <p className="text-purple-700 mb-2">
                    Congratulations! You've completed all courses in this program.
                  </p>
                  <p className="text-sm text-purple-600">
                    Take the comprehensive final test to earn your program certificate and complete your learning journey.
                  </p>
                </div>
              </div>
              <Button 
                size="lg"
                onClick={() => navigate(`/final-test/program/${program.id}`)}
                className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3"
              >
                <Award className="w-5 h-5 mr-2" />
                Take Final Test
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Progress Summary */}
      {!courses.every(course => course.status === 'completed') && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Program Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Overall Completion</span>
                <span className="text-sm font-medium text-gray-900">
                  {courses.filter(c => c.status === 'completed').length} / {courses.length} courses completed
                </span>
              </div>
              <Progress 
                value={(courses.filter(c => c.status === 'completed').length / courses.length) * 100} 
                className="h-3"
              />
              {courses.some(course => course.status === 'locked') && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <Lock className="w-5 h-5 text-yellow-600 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-yellow-800">Course Progression</p>
                      <p className="text-sm text-yellow-700">
                        Complete each course in order to unlock the next one. The final test will be available after completing all courses.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Program Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Program Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 mb-2">
                Created on {new Date(program.createdAt).toLocaleDateString()}
              </p>
              <p className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline">
                Export Program
              </Button>
              <Button onClick={() => navigate(`/program/${program.id}/edit`)}>
                Edit Program
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProgramDetail;
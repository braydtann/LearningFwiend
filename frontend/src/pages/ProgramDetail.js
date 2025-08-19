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
  const { user, isLearner, getProgramById, getAllCourses, checkProgramAccess } = useAuth();
  
  const [program, setProgram] = useState(null);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accessStatus, setAccessStatus] = useState(null);

  useEffect(() => {
    const loadProgramDetails = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Load program details
        const programResult = await getProgramById(id);
        if (programResult.success) {
          setProgram(programResult.program);
          
          // For learners, check access status
          if (isLearner) {
            const accessResult = await checkProgramAccess(id);
            setAccessStatus(accessResult);
            
            // If access is denied, we can still show the program details but with restrictions
            if (!accessResult.hasAccess) {
              console.log('Program access denied:', accessResult.message);
            }
          }
          
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
  }, [id, getProgramById, getAllCourses, checkProgramAccess, isLearner]);

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
          <span>Programs</span> / <span className="text-gray-900">{program.title}</span>
        </nav>
      </div>

      {/* Access Status Banner for Learners */}
      {isLearner && accessStatus && !accessStatus.hasAccess && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="p-6">
            <div className="flex items-start space-x-3">
              <Lock className="w-6 h-6 text-yellow-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-lg font-semibold text-yellow-800 mb-2">Program Access Restricted</h3>
                <p className="text-yellow-700 mb-3">{accessStatus.message}</p>
                <div className="text-sm text-yellow-600">
                  {accessStatus.reason === 'classroom_expired' && (
                    <p>Your classroom access to this program has expired. Contact your instructor for more information.</p>
                  )}
                  {accessStatus.reason === 'not_enrolled' && (
                    <p>You need to be enrolled in a classroom that includes this program to access it.</p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Program Overview */}
      <Card>
        <CardContent className="p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-4">
                <h1 className="text-3xl font-bold text-gray-900">{program.title}</h1>
                <Badge variant={program.isActive ? 'default' : 'secondary'}>
                  {program.isActive ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <p className="text-lg text-gray-600 mb-6">{program.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="flex items-center space-x-3">
                  <BookOpen className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Courses</p>
                    <p className="font-medium">{program.courseCount || 0}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Enrolled Students</p>
                    <p className="font-medium">0</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Duration</p>
                    <p className="font-medium">{program.duration || 'N/A'}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <Calendar className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Created</p>
                    <p className="font-medium">{new Date(program.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <div className="flex items-center space-x-3">
                  <Award className="h-5 w-5 text-purple-500" />
                  <div>
                    <p className="text-sm text-gray-500">Created by</p>
                    <p className="font-medium">{program.instructor || 'Unknown'}</p>
                  </div>
                </div>
              </div>
            </div>
            
            {(user?.role === 'admin' || program.instructorId === user?.id) && (
              <div className="flex flex-col space-y-2">
                <Button 
                  onClick={() => navigate(`/program/${program.id}/edit`)}
                  className="flex items-center space-x-2"
                >
                  <span>Edit Program</span>
                </Button>
              </div>
            )}
          </div>

          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">Program Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-700">0</div>
                <div className="text-sm text-blue-600">Total Enrollments</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-700">{program.courseCount || 0}</div>
                <div className="text-sm text-green-600">Total Courses</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-700">{program.isActive ? 'Active' : 'Inactive'}</div>
                <div className="text-sm text-orange-600">Status</div>
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
          {courses.length === 0 ? (
            <div className="text-center py-8">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Courses Added</h3>
              <p className="text-gray-600">This program doesn't have any courses assigned yet.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {courses.map((course, index) => (
                <div key={course.id} className="relative">
                  {/* Connector Line */}
                  {index < courses.length - 1 && (
                    <div className="absolute left-6 top-20 w-0.5 h-16 bg-gray-200"></div>
                  )}
                  
                  <Card className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start space-x-4">
                        {/* Step Number */}
                        <div className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-lg flex-shrink-0">
                          {index + 1}
                        </div>
                        
                        {/* Course Thumbnail */}
                        <img 
                          src={course.thumbnail || 'https://via.placeholder.com/80'} 
                          alt={course.title}
                          className="w-20 h-20 rounded-lg object-cover flex-shrink-0"
                        />
                        
                        {/* Course Details */}
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {course.title}
                            </h3>
                            <Badge variant="outline" className="border-blue-500 text-blue-700 bg-blue-50">
                              Available
                            </Badge>
                          </div>
                          
                          <p className="text-gray-600 mb-3 line-clamp-2">
                            {course.description || 'No description available'}
                          </p>
                          
                          <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                            <div className="flex items-center space-x-1">
                              <BookOpen className="w-4 h-4" />
                              <span>{course.category || 'General'}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Clock className="w-4 h-4" />
                              <span>{course.duration || 'N/A'}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Target className="w-4 h-4" />
                              <span>{course.level || 'Beginner'}</span>
                            </div>
                          </div>
                          
                          <Button 
                            size="sm"
                            onClick={() => navigate(`/course/${course.id}`)}
                            className="flex items-center space-x-2"
                            disabled={isLearner && accessStatus && !accessStatus.hasAccess}
                          >
                            {isLearner && accessStatus && !accessStatus.hasAccess ? (
                              <>
                                <Lock className="w-4 h-4" />
                                <span>Access Restricted</span>
                              </>
                            ) : (
                              <>
                                <Play className="w-4 h-4" />
                                <span>Start Course</span>
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ProgramDetail;
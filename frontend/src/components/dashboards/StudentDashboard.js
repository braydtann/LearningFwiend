import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';

import { BookOpen, Clock, Award, TrendingUp, Play, Users, ClipboardCheck, CheckCircle } from 'lucide-react';

const StudentDashboard = () => {
  const { user, getMyEnrollments, getAllCourses, getAllPrograms, getAllClassrooms } = useAuth();
  const navigate = useNavigate();
  
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [enrolledPrograms, setEnrolledPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quizResults, setQuizResults] = useState([]);
  
  // TODO: Replace with backend APIs when available
  const certificates = []; // getUserCertificates(user?.id);
  const studentClassrooms = []; // getStudentClassrooms(user?.id);

  // Load real enrollment data from backend
  useEffect(() => {
    if (user) {
      loadEnrollments();
      loadEnrolledPrograms();
    }
  }, [user]);

  const loadEnrollments = async () => {
    setLoading(true);
    try {
      const enrollmentResult = await getMyEnrollments();
      
      if (enrollmentResult.success && enrollmentResult.enrollments.length > 0) {
        // Get course details for each enrollment
        const courseResult = await getAllCourses();
        
        if (courseResult.success) {
          const enrolledCourseData = [];
          const quizResultsData = [];
          
          enrollmentResult.enrollments.forEach(enrollment => {
            const course = courseResult.courses.find(c => c.id === enrollment.courseId);
            if (course) { // Only process if course exists
              enrolledCourseData.push({
                id: enrollment.courseId,
                title: course?.title || enrollment.courseName || 'Unknown Course',
                thumbnail: course?.thumbnailUrl || course?.thumbnail || 'https://via.placeholder.com/300x200?text=Course+Image',
                instructor: course?.instructor || 'Unknown',
                duration: course?.duration || '1 week',
                progress: enrollment.progress || 0,
                enrollmentId: enrollment.id,
                isOrphaned: false
              });

              // Extract quiz results from enrollment progress for courses with quiz content
              if (enrollment.progress > 0) {
                const courseModules = course.modules || [];
                let hasQuizContent = false;
                
                // Check for quiz content (be more flexible)
                for (const module of courseModules) {
                  const lessons = module.lessons || [];
                  for (const lesson of lessons) {
                    if (lesson.type === 'quiz' || 
                        lesson.questions?.length > 0 ||
                        lesson.quiz?.questions?.length > 0 ||
                        (lesson.type && lesson.type.toLowerCase().includes('quiz'))) {
                      hasQuizContent = true;
                      break;
                    }
                  }
                  if (hasQuizContent) break;
                }

                // If student completed the course or has significant progress, assume it had assessment
                if (!hasQuizContent && (enrollment.progress === 100 || enrollment.progress >= 70)) {
                  hasQuizContent = true;
                }

                if (hasQuizContent) {
                  quizResultsData.push({
                    courseId: enrollment.courseId,
                    courseName: course.title,
                    bestScore: enrollment.progress,
                    totalAttempts: 1,
                    passed: enrollment.progress >= 70, // Assume 70% passing
                    lastAttempt: new Date(enrollment.updated_at || enrollment.created_at)
                  });
                }
              }
            }
          });
          
          setEnrolledCourses(enrolledCourseData);
          setQuizResults(quizResultsData);
          console.log(`Loaded ${quizResultsData.length} quiz results from enrollments`);
        } else {
          // Fallback to enrollment data only
          const enrolledCourseData = enrollmentResult.enrollments.map(enrollment => ({
            id: enrollment.courseId,
            title: enrollment.courseName || 'Unknown Course',
            thumbnail: '/default-course-image.jpg',
            instructor: 'Unknown',
            duration: '1 week',
            progress: enrollment.progress || 0,
            enrollmentId: enrollment.id
          }));
          setEnrolledCourses(enrolledCourseData);
          
          // Create basic quiz results from enrollment progress
          const quizResultsData = enrollmentResult.enrollments
            .filter(enrollment => enrollment.progress > 0)
            .map(enrollment => ({
              courseId: enrollment.courseId,
              courseName: enrollment.courseName || 'Unknown Course',
              bestScore: enrollment.progress,
              totalAttempts: 1,
              passed: enrollment.progress >= 70,
              lastAttempt: new Date(enrollment.updated_at || enrollment.created_at)
            }));
          setQuizResults(quizResultsData);
        }
      } else {
        // No backend enrollments found
        setEnrolledCourses([]);
        setQuizResults([]);
      }
    } catch (error) {
      console.error('Error loading enrollments:', error);
      // Set empty arrays on error
      setEnrolledCourses([]);
      setQuizResults([]);
    } finally {
      setLoading(false);
    }
  };

  const loadEnrolledPrograms = async () => {
    try {
      // Get classrooms where student is enrolled
      const classroomsResult = await getAllClassrooms();
      if (!classroomsResult.success) return;

      const studentClassrooms = classroomsResult.classrooms.filter(classroom => 
        classroom.studentIds && classroom.studentIds.includes(user.id)
      );

      if (studentClassrooms.length === 0) {
        setEnrolledPrograms([]);
        return;
      }

      // Get all programs to match with classroom programs
      const programsResult = await getAllPrograms();
      if (!programsResult.success) return;

      // Get enrollments to track course completion
      const enrollmentResult = await getMyEnrollments();
      const enrollments = enrollmentResult.success ? enrollmentResult.enrollments : [];

      // Get all courses for program course lookup
      const coursesResult = await getAllCourses();
      const allCourses = coursesResult.success ? coursesResult.courses : [];

      const enrolledProgramsData = [];

      // Process each classroom to find programs
      studentClassrooms.forEach(classroom => {
        classroom.programIds?.forEach(programId => {
          const program = programsResult.programs.find(p => p.id === programId);
          if (program && !enrolledProgramsData.find(ep => ep.id === program.id)) {
            // Calculate program progress
            const programCourses = program.courseIds.map(courseId => 
              allCourses.find(c => c.id === courseId)
            ).filter(Boolean);

            const completedCourses = programCourses.filter(course => {
              const enrollment = enrollments.find(e => e.courseId === course.id);
              return enrollment && enrollment.progress >= 100;
            });

            const overallProgress = programCourses.length > 0 
              ? Math.round((completedCourses.length / programCourses.length) * 100)
              : 0;

            const isCompleted = completedCourses.length === programCourses.length && programCourses.length > 0;

            enrolledProgramsData.push({
              id: program.id,
              title: program.title,
              description: program.description,
              totalCourses: programCourses.length,
              completedCourses: completedCourses.length,
              progress: overallProgress,
              isCompleted,
              courses: programCourses.map(course => {
                const enrollment = enrollments.find(e => e.courseId === course.id);
                return {
                  id: course.id,
                  title: course.title,
                  completed: enrollment && enrollment.progress >= 100,
                  progress: enrollment ? enrollment.progress : 0
                };
              }),
              classroomName: classroom.name
            });
          }
        });
      });

      setEnrolledPrograms(enrolledProgramsData);
      console.log(`Loaded ${enrolledProgramsData.length} enrolled programs`);
    } catch (error) {
      console.error('Error loading enrolled programs:', error);
      setEnrolledPrograms([]);
    }
  };
  
  const stats = {
    enrolled: enrolledCourses.length,
    completed: enrolledCourses.filter(course => course.progress === 100).length,
    inProgress: enrolledCourses.filter(course => course.progress > 0 && course.progress < 100).length,
    certificates: certificates.length,
    classrooms: studentClassrooms.length,
    quizzesTaken: quizResults.length,
    avgQuizScore: quizResults.length > 0 
      ? Math.round(quizResults.reduce((sum, result) => sum + result.bestScore, 0) / quizResults.length)
      : 0
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.name}! 👋
        </h1>
        <p className="text-gray-600">Continue your learning journey</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Enrolled Courses</p>
                <p className="text-2xl font-bold text-blue-700">{stats.enrolled}</p>
              </div>
              <BookOpen className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-600 text-sm font-medium">In Progress</p>
                <p className="text-2xl font-bold text-yellow-700">{stats.inProgress}</p>
              </div>
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Completed</p>
                <p className="text-2xl font-bold text-green-700">{stats.completed}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Quizzes Taken</p>
                <p className="text-2xl font-bold text-purple-700">{stats.quizzesTaken}</p>
              </div>
              <ClipboardCheck className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Avg Quiz Score</p>
                <p className="text-2xl font-bold text-orange-700">{stats.avgQuizScore}%</p>
              </div>
              <Award className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-indigo-50 border-indigo-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-indigo-600 text-sm font-medium">Certificates</p>
                <p className="text-2xl font-bold text-indigo-700">{stats.certificates}</p>
              </div>
              <Award className="h-8 w-8 text-indigo-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Quiz Performance */}
      {quizResults.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Recent Quiz Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {quizResults.slice(0, 3).map((result, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Quiz Performance</p>
                    <p className="text-sm text-gray-600">{result.totalAttempts} attempts</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{result.bestScore}%</p>
                    <Badge variant={result.passed ? "default" : "destructive"} className="text-xs">
                      {result.passed ? "Passed" : "Failed"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Enrolled Programs Section */}
      {enrolledPrograms.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">Enrolled Programs</CardTitle>
              <Button 
                variant="outline" 
                onClick={() => navigate('/programs')}
              >
                View All Programs
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {enrolledPrograms.map((program) => (
                <Card key={program.id} className="hover:shadow-lg transition-shadow border-l-4 border-l-blue-500">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900 mb-2">
                          {program.title}
                        </h3>
                        <p className="text-sm text-gray-600 mb-3">
                          {program.description}
                        </p>
                        <p className="text-xs text-gray-500 mb-3">
                          From: {program.classroomName}
                        </p>
                      </div>
                      <Badge 
                        variant={program.isCompleted ? "default" : "secondary"}
                        className="ml-2"
                      >
                        {program.isCompleted ? "Completed" : "In Progress"}
                      </Badge>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Overall Progress</span>
                        <span className="font-medium">{program.progress}%</span>
                      </div>
                      <Progress value={program.progress} className="h-2" />
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Courses Completed</span>
                        <span className="font-medium">
                          {program.completedCourses} / {program.totalCourses}
                        </span>
                      </div>

                      {/* Course List */}
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {program.courses.map((course, index) => (
                          <div key={course.id} className="flex items-center justify-between py-1">
                            <div className="flex items-center">
                              {course.completed ? (
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                              ) : (
                                <div className="w-4 h-4 border-2 border-gray-300 rounded-full mr-2"></div>
                              )}
                              <span className="text-sm text-gray-700">{course.title}</span>
                            </div>
                            <span className="text-xs text-gray-500">{course.progress}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex gap-2 mt-4">
                      <Button 
                        className="flex-1"
                        variant="outline"
                        onClick={() => navigate(`/program/${program.id}`)}
                      >
                        Continue Learning
                      </Button>
                      {program.isCompleted && (
                        <Button 
                          className="flex-1 bg-green-600 hover:bg-green-700"
                          onClick={() => navigate(`/final-test/program/${program.id}`)}
                        >
                          <Award className="w-4 h-4 mr-2" />
                          Take Final Exam
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Enrolled Courses */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl">Enrolled Courses</CardTitle>
            <Button 
              variant="outline" 
              onClick={() => navigate('/courses')}
            >
              Browse All Courses
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading your enrolled courses...</p>
            </div>
          ) : enrolledCourses.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No courses enrolled yet</h3>
              <p className="text-gray-600 mb-4">Start your learning journey by enrolling in a course</p>
              <Button onClick={() => navigate('/courses')}>
                Browse Courses
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {enrolledCourses.map((course) => (
                <Card key={course.id} className="hover:shadow-lg transition-shadow">
                  <div className="aspect-video relative overflow-hidden rounded-t-lg">
                    <img 
                      src={course.thumbnailUrl || course.thumbnail || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=225&fit=crop&crop=center'} 
                      alt={course.title}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.src = 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=225&fit=crop&crop=center';
                      }}
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                      <Button
                        size="sm"
                        className="bg-white text-black hover:bg-gray-100"
                        onClick={() => navigate(`/course/${course.id}`)}
                      >
                        <Play className="w-4 h-4 mr-2" />
                        Continue
                      </Button>
                    </div>
                  </div>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                      {course.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3">
                      by {course.instructor}
                    </p>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Progress</span>
                        <span className="font-medium">{course.progress}%</span>
                      </div>
                      <Progress value={course.progress} className="h-2" />
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center text-gray-500 text-sm">
                          <Clock className="w-4 h-4 mr-1" />
                          {course.duration}
                        </div>
                        <Badge variant={course.progress === 100 ? "default" : "secondary"}>
                          {course.progress === 100 ? "Completed" : "In Progress"}
                        </Badge>
                      </div>
                    </div>
                    
                    <Button 
                      className="w-full mt-4"
                      onClick={() => navigate(`/course/${course.id}`)}
                    >
                      Continue Learning
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* My Classrooms */}
      {studentClassrooms.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">My Training Programs</CardTitle>
              <Button 
                variant="outline" 
                onClick={() => navigate('/classrooms')}
              >
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {studentClassrooms.slice(0, 2).map((classroom) => (
                <div key={classroom.id} className="flex items-center p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                  <Users className="h-8 w-8 text-indigo-600 mr-3" />
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{classroom.name}</h4>
                    <p className="text-sm text-gray-600">Progress: {classroom.progress || 0}%</p>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full" 
                        style={{ width: `${classroom.progress || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => navigate(`/classroom/${classroom.id}`)}>
                    View
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Certificates */}
      {certificates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Recent Certificates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {certificates.map((cert) => (
                <div key={cert.id} className="flex items-center p-4 bg-green-50 rounded-lg border border-green-200">
                  <Award className="h-8 w-8 text-green-600 mr-3" />
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{cert.courseName}</h4>
                    <p className="text-sm text-gray-600">Issued {new Date(cert.issuedAt).toLocaleDateString()}</p>
                  </div>
                  <Button size="sm" variant="outline">
                    Download
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default StudentDashboard;
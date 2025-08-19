import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../components/ui/accordion';
import { getImageUrl, handleImageError } from '../utils/imageUtils';
import { 
  BookOpen, 
  Clock, 
  Users, 
  Play, 
  FileText, 
  CheckCircle, 
  Star,
  ArrowLeft,
  Download,
  Presentation,
  AlertTriangle,
  Lock,
  ChevronRight,
  SkipForward
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { 
    user, 
    isLearner, 
    getCourseById, 
    getMyEnrollments, 
    updateEnrollmentProgress 
  } = useAuth();
  const { toast } = useToast();
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [loadingEnrollments, setLoadingEnrollments] = useState(true);
  const [currentEnrollment, setCurrentEnrollment] = useState(null);
  const [nextAction, setNextAction] = useState(null); // { type: 'module'|'lesson', target: {...} }

  // Load course data and enrollments from backend
  useEffect(() => {
    loadCourse();
    if (isLearner) {
      loadEnrollments();
    }
  }, [id, isLearner]);

  // Calculate next action when course, enrollment, or selected lesson changes
  useEffect(() => {
    if (course && currentEnrollment && selectedLesson) {
      calculateNextAction();
    }
  }, [course, currentEnrollment, selectedLesson]);

  const loadCourse = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getCourseById(id);
      if (result.success) {
        setCourse(result.course);
      } else {
        setError(result.error || 'Course not found');
      }
    } catch (error) {
      console.error('Error loading course:', error);
      setError('Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  const loadEnrollments = async () => {
    setLoadingEnrollments(true);
    try {
      const result = await getMyEnrollments();
      if (result.success) {
        setEnrollments(result.enrollments);
        
        // Find current enrollment for this course
        const enrollment = result.enrollments.find(e => e.courseId === id);
        setCurrentEnrollment(enrollment || null);
      } else {
        console.error('Failed to load enrollments:', result.error);
        setEnrollments([]);
        setCurrentEnrollment(null);
      }
    } catch (error) {
      console.error('Error loading enrollments:', error);
      setEnrollments([]);
      setCurrentEnrollment(null);
    } finally {
      setLoadingEnrollments(false);
    }
  };

  // Calculate real progress based on enrollment data
  const calculateProgress = () => {
    if (!currentEnrollment || !course) return 0;
    
    // Use backend progress if available
    if (currentEnrollment.progress !== undefined && currentEnrollment.progress !== null) {
      return Math.round(currentEnrollment.progress);
    }
    
    // Calculate based on module progress if available
    if (currentEnrollment.moduleProgress && course.modules) {
      const totalLessons = course.modules.reduce((total, module) => 
        total + (module.lessons?.length || 0), 0);
      
      if (totalLessons === 0) return 0;
      
      const completedLessons = currentEnrollment.moduleProgress.reduce((total, moduleProgress) => 
        total + (moduleProgress.lessons?.filter(l => l.completed).length || 0), 0);
      
      return Math.round((completedLessons / totalLessons) * 100);
    }
    
    return 0;
  };

  // Calculate next action (next lesson or next module)
  const calculateNextAction = () => {
    if (!course?.modules || !selectedLesson) {
      setNextAction(null);
      return;
    }
    
    // Find current module and lesson
    let currentModuleIndex = -1;
    let currentLessonIndex = -1;
    
    for (let mi = 0; mi < course.modules.length; mi++) {
      const module = course.modules[mi];
      if (module.lessons) {
        for (let li = 0; li < module.lessons.length; li++) {
          if (module.lessons[li].id === selectedLesson.id) {
            currentModuleIndex = mi;
            currentLessonIndex = li;
            break;
          }
        }
        if (currentModuleIndex !== -1) break;
      }
    }
    
    if (currentModuleIndex === -1) {
      setNextAction(null);
      return;
    }
    
    const currentModule = course.modules[currentModuleIndex];
    
    // Check if there's a next lesson in current module
    if (currentLessonIndex < currentModule.lessons.length - 1) {
      setNextAction({
        type: 'lesson',
        target: currentModule.lessons[currentLessonIndex + 1],
        moduleIndex: currentModuleIndex,
        lessonIndex: currentLessonIndex + 1
      });
      return;
    }
    
    // Check if there's a next module
    if (currentModuleIndex < course.modules.length - 1) {
      const nextModule = course.modules[currentModuleIndex + 1];
      if (nextModule.lessons && nextModule.lessons.length > 0) {
        setNextAction({
          type: 'module',
          target: nextModule.lessons[0],
          moduleIndex: currentModuleIndex + 1,
          lessonIndex: 0,
          nextModuleTitle: nextModule.title
        });
        return;
      }
    }
    
    // No next action available
    setNextAction(null);
  };

  // Check if user is enrolled using real backend data
  const isEnrolled = isLearner && currentEnrollment;
  
  // For now, set basic progress - this can be enhanced later with real progress tracking
  const progress = 0; // TODO: Implement real progress tracking

  // For now, allow access to enrolled courses - classroom restrictions can be added later  
  const canAccessCourse = !isLearner || isEnrolled;

  // Loading state - wait for both course and enrollment data
  if (loading || (isLearner && loadingEnrollments)) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Loading course...</h3>
        <p className="text-gray-600">Please wait while we fetch the course details.</p>
      </div>
    );
  }

  // Error or course not found
  if (error || !course) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-16 w-16 text-orange-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Course Not Available
        </h1>
        <p className="text-gray-600 mb-6">
          {error || 'This course is no longer available or may have been removed.'}
        </p>
        <div className="space-x-4">
          <Button onClick={() => navigate('/courses')}>
            Browse All Courses
          </Button>
          <Button variant="outline" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  // Check access for learners - they need to be enrolled
  if (isLearner && !canAccessCourse) {
    return (
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center space-x-4 mb-6">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => navigate('/courses')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div className="h-6 border-l border-gray-300"></div>
          <nav className="text-sm text-gray-500">
            <span>Courses</span> / <span className="text-gray-900">{course.title}</span>
          </nav>
        </div>

        {/* Access Denied */}
        <Card className="max-w-2xl mx-auto">
          <CardContent className="text-center py-12">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Lock className="w-10 h-10 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Course Access Restricted</h2>
            <p className="text-gray-600 mb-6">
              You need to be enrolled in this course to access its content.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">Enrollment Required</p>
                  <p className="text-sm text-yellow-700">
                    Please contact your instructor to get enrolled in this course.
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <Button onClick={() => navigate('/courses')} variant="outline">
                Browse Other Courses
              </Button>
              <p className="text-xs text-gray-500">
                Contact your instructor if you believe this is an error
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleEnroll = () => {
    toast({
      title: "Enrolled successfully!",
      description: "You can now access all course materials.",
    });
  };

  const handleLessonClick = (lesson) => {
    if (lesson.type === 'quiz') {
      // Navigate to quiz taking page
      navigate(`/quiz/${id}/${lesson.id}`);
    } else {
      setSelectedLesson(lesson);
    }
  };

  const markLessonComplete = (lessonId) => {
    toast({
      title: "Lesson completed!",
      description: "Great job! Continue with the next lesson.",
    });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate('/courses')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div className="h-6 border-l border-gray-300"></div>
        <nav className="text-sm text-gray-500">
          <span>Courses</span> / <span className="text-gray-900">{course.title}</span>
        </nav>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Course Header */}
          <div>
            <div className="aspect-video relative overflow-hidden rounded-lg mb-6">
              <img 
                src={getImageUrl(course.thumbnailUrl || course.thumbnail)} 
                alt={course.title}
                className="w-full h-full object-cover"
                onError={(e) => handleImageError(e)}
              />
              {(selectedLesson?.type === 'video' || selectedLesson?.type === 'presentation') && 
               (selectedLesson.videoUrl || selectedLesson.presentationUrl || selectedLesson.embedCode) && (
                <div className="absolute inset-0 bg-black">
                  {(() => {
                    // Handle Canva presentations with embed code (priority)
                    if (selectedLesson.type === 'presentation' && selectedLesson.embedCode) {
                      return (
                        <div 
                          className="w-full h-full"
                          dangerouslySetInnerHTML={{ __html: selectedLesson.embedCode }}
                        />
                      );
                    }
                    
                    const url = selectedLesson.videoUrl || selectedLesson.presentationUrl;
                    
                    // Handle Canva presentations with URL (fallback)
                    if (selectedLesson.type === 'presentation' || url.includes('canva.com')) {
                      // Convert Canva sharing link to embed format
                      if (url.includes('canva.com/design/')) {
                        const designId = url.match(/design\/([^\/\?]+)/)?.[1];
                        if (designId) {
                          return (
                            <iframe
                              src={`https://www.canva.com/design/${designId}/view?embed`}
                              className="w-full h-full"
                              allowFullScreen
                              title={selectedLesson.title}
                            />
                          );
                        }
                      }
                      
                      // Fallback for other Canva URLs
                      return (
                        <iframe
                          src={url.includes('?embed') ? url : `${url}?embed`}
                          className="w-full h-full"
                          allowFullScreen
                          title={selectedLesson.title}
                        />
                      );
                    }
                    
                    // Handle Google Drive links
                    if (url.includes('drive.google.com')) {
                      const fileId = url.match(/\/file\/d\/([a-zA-Z0-9-_]+)/)?.[1] || 
                                   url.match(/id=([a-zA-Z0-9-_]+)/)?.[1];
                      if (fileId) {
                        return (
                          <iframe
                            src={`https://drive.google.com/file/d/${fileId}/preview`}
                            className="w-full h-full"
                            allowFullScreen
                            title={selectedLesson.title}
                          />
                        );
                      }
                    }
                    
                    // Handle YouTube and Vimeo (existing logic)
                    return (
                      <iframe
                        src={url}
                        className="w-full h-full"
                        allowFullScreen
                        title={selectedLesson.title}
                      />
                    );
                  })()}
                </div>
              )}
            </div>

            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <Badge variant="secondary" className="mb-2">
                  {course.category}
                </Badge>
                <h1 className="text-3xl font-bold text-gray-900 mb-3">
                  {course.title}
                </h1>
                <p className="text-lg text-gray-600 mb-4">
                  {course.description}
                </p>
                <div className="flex items-center space-x-6 text-sm text-gray-500">
                  <div className="flex items-center">
                    <Users className="w-4 h-4 mr-1" />
                    {course.enrolledStudents} students
                  </div>
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {course.duration}
                  </div>
                  <div className="flex items-center">
                    <BookOpen className="w-4 h-4 mr-1" />
                    {course.totalLessons} lessons
                  </div>
                  <div className="flex items-center">
                    <Star className="w-4 h-4 mr-1 fill-yellow-400 text-yellow-400" />
                    4.8 (245 reviews)
                  </div>
                </div>
              </div>
            </div>

            {isEnrolled && (
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-blue-700">Your Progress</span>
                  <span className="text-sm font-bold text-blue-700">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>
            )}
          </div>

          {/* Course Content Tabs */}
          <Tabs defaultValue="curriculum" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="curriculum">Curriculum</TabsTrigger>
              <TabsTrigger value="description">Description</TabsTrigger>
              <TabsTrigger value="reviews">Reviews</TabsTrigger>
            </TabsList>
            
            <TabsContent value="curriculum" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Course Content</CardTitle>
                </CardHeader>
                <CardContent>
                  <Accordion type="single" collapsible className="w-full">
                    {course.modules?.map((module, moduleIndex) => (
                      <AccordionItem key={module.id} value={module.id}>
                        <AccordionTrigger className="text-left">
                          <div className="flex items-center justify-between w-full mr-4">
                            <span className="font-medium">
                              Module {moduleIndex + 1}: {module.title}
                            </span>
                            <span className="text-sm text-gray-500">
                              {module.lessons?.length || 0} lessons
                            </span>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent>
                          <div className="space-y-3 pt-2">
                            {module.lessons?.map((lesson, lessonIndex) => (
                              <div 
                                key={lesson.id}
                                className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors ${
                                  selectedLesson?.id === lesson.id 
                                    ? 'bg-blue-50 border-blue-200' 
                                    : 'hover:bg-gray-50'
                                } ${!isEnrolled && 'opacity-50 cursor-not-allowed'}`}
                                onClick={() => isEnrolled && handleLessonClick(lesson)}
                              >
                                <div className="flex items-center space-x-3">
                                  <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                                    {lesson.type === 'video' && <Play className="w-4 h-4" />}
                                    {lesson.type === 'presentation' && <Presentation className="w-4 h-4" />}
                                    {lesson.type === 'text' && <FileText className="w-4 h-4" />}
                                    {lesson.type === 'quiz' && <CheckCircle className="w-4 h-4 text-purple-600" />}
                                  </div>
                                  <div>
                                    <p className="font-medium text-gray-900">
                                      {lessonIndex + 1}. {lesson.title}
                                      {lesson.type === 'quiz' && (
                                        <Badge variant="outline" className="ml-2 text-purple-600">
                                          Quiz
                                        </Badge>
                                      )}
                                    </p>
                                    {lesson.duration && (
                                      <p className="text-sm text-gray-500">{lesson.duration}</p>
                                    )}
                                    {lesson.type === 'quiz' && lesson.quiz && (
                                      <p className="text-sm text-gray-500">
                                        {lesson.quiz.questions?.length || 0} questions • {lesson.quiz.timeLimit || 10} min
                                      </p>
                                    )}
                                  </div>
                                </div>
                                {isEnrolled && (
                                  <Button 
                                    size="sm" 
                                    variant="outline"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      markLessonComplete(lesson.id);
                                    }}
                                  >
                                    <CheckCircle className="w-4 h-4" />
                                  </Button>
                                )}
                              </div>
                            ))}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="description">
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold mb-3">About this course</h3>
                      <p className="text-gray-600 leading-relaxed">
                        {course.description}
                      </p>
                    </div>
                    
                    <div>
                      <h3 className="text-lg font-semibold mb-3">What you'll learn</h3>
                      <ul className="space-y-2">
                        <li className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">Master the fundamentals and advanced concepts</span>
                        </li>
                        <li className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">Build real-world projects from scratch</span>
                        </li>
                        <li className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">Best practices and industry standards</span>
                        </li>
                        <li className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">Prepare for professional opportunities</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="reviews">
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold">Student Reviews</h3>
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star key={star} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          ))}
                        </div>
                        <span className="text-sm text-gray-600">4.8 out of 5 (245 reviews)</span>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      {[1, 2, 3].map((review) => (
                        <div key={review} className="border-b border-gray-200 pb-4">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center space-x-3">
                              <img 
                                src={`https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face`} 
                                className="w-10 h-10 rounded-full object-cover"
                                alt="Reviewer"
                              />
                              <div>
                                <p className="font-medium">John Doe</p>
                                <div className="flex items-center">
                                  {[1, 2, 3, 4, 5].map((star) => (
                                    <Star key={star} className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                                  ))}
                                </div>
                              </div>
                            </div>
                            <span className="text-sm text-gray-500">2 days ago</span>
                          </div>
                          <p className="text-gray-600">
                            Excellent course! The instructor explains everything clearly and the projects are very practical.
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Enrollment Card */}
          <Card>
            <CardContent className="p-6">
              <div className="text-center space-y-4">
                <div className="text-3xl font-bold text-gray-900">Free</div>
                
                {isEnrolled ? (
                  <div className="space-y-3">
                    <Badge className="w-full py-2 bg-green-600">
                      ✓ Enrolled
                    </Badge>
                    <Button className="w-full" onClick={() => navigate('/dashboard')}>
                      Go to Dashboard
                    </Button>
                  </div>
                ) : (
                  <Button 
                    className="w-full bg-blue-600 hover:bg-blue-700"
                    onClick={handleEnroll}
                  >
                    Enroll Now
                  </Button>
                )}
                
                <div className="text-xs text-gray-500 space-y-1">
                  <p>✓ Lifetime access</p>
                  <p>✓ Certificate of completion</p>
                  <p>✓ 30-day money-back guarantee</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Instructor Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Instructor</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-3 mb-4">
                <img 
                  src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=60&h=60&fit=crop&crop=face" 
                  className="w-12 h-12 rounded-full object-cover"
                  alt={course.instructor}
                />
                <div>
                  <p className="font-medium text-gray-900">{course.instructor}</p>
                  <p className="text-sm text-gray-600">Senior Developer</p>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Expert instructor with 10+ years of experience in the field.
              </p>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center justify-between">
                  <span>Total Students</span>
                  <span className="font-medium">2,543</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Courses</span>
                  <span className="font-medium">12</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Rating</span>
                  <span className="font-medium">4.9/5</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Course Features */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">This course includes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-gray-500" />
                  <span>{course.duration} of content</span>
                </div>
                <div className="flex items-center">
                  <BookOpen className="w-4 h-4 mr-2 text-gray-500" />
                  <span>{course.totalLessons} lessons</span>
                </div>
                <div className="flex items-center">
                  <Download className="w-4 h-4 mr-2 text-gray-500" />
                  <span>Downloadable resources</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-gray-500" />
                  <span>Certificate of completion</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;
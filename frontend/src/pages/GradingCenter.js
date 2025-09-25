import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  GraduationCap, 
  CheckCircle, 
  AlertCircle, 
  BookOpen,
  Users,
  MessageSquare,
  Star,
  Clock,
  FileText,
  Eye,
  Search,
  Filter
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const GradingCenter = () => {
  const { user, getAllCourses } = useAuth();
  const { toast } = useToast();
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [gradingSubmission, setGradingSubmission] = useState(null);
  const [gradeScore, setGradeScore] = useState('');
  const [gradeFeedback, setGradeFeedback] = useState('');
  const [viewMode, setViewMode] = useState('course'); // 'course' or 'all'
  const [selectedAttempt, setSelectedAttempt] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'quiz', 'final'

  useEffect(() => {
    if (user && (user.role === 'instructor' || user.role === 'admin')) {
      loadInstructorCourses();
      loadAllAttempts(); // Load attempts for review functionality
    }
  }, [user]);

  const loadInstructorCourses = async () => {
    setLoading(true);
    try {
      const result = await getAllCourses();
      if (result.success) {
        // Filter courses - admins can see all courses, instructors only see their own
        const accessibleCourses = user.role === 'admin' 
          ? result.courses 
          : result.courses.filter(course => course.instructorId === user.id);
        setCourses(accessibleCourses);
        
        if (accessibleCourses.length > 0) {
          setSelectedCourse(accessibleCourses[0]);
          if (viewMode === 'course') {
            await loadCourseSubmissions(accessibleCourses[0].id);
          }
        }
        
        if (viewMode === 'all') {
          await loadAllSubmissions();
        }
      }
    } catch (error) {
      console.error('Error loading instructor courses:', error);
      toast({
        title: "Error",
        description: "Failed to load your courses.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Load all attempts for attempt review functionality
  const loadAllAttempts = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');
      
      // Load quiz attempts
      const quizResponse = await fetch(`${backendUrl}/api/admin/quiz-attempts`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      // Load final test attempts  
      const finalResponse = await fetch(`${backendUrl}/api/admin/final-test-attempts`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      let allAttempts = [];
      
      if (quizResponse.ok) {
        const quizData = await quizResponse.json();
        // Add type identifier and format quiz attempts
        const quizAttempts = (quizData.attempts || []).map(attempt => ({
          ...attempt,
          type: 'quiz',
          title: attempt.quizTitle || attempt.lessonTitle || 'Unknown Quiz',
          courseName: attempt.courseName || 'Unknown Course',
          date: attempt.submittedAt || attempt.created_at
        }));
        allAttempts = [...allAttempts, ...quizAttempts];
      }
      
      if (finalResponse.ok) {
        const finalData = await finalResponse.json();
        // Add type identifier and format final test attempts
        const finalAttempts = (finalData.attempts || []).map(attempt => ({
          ...attempt,
          type: 'final',
          title: attempt.testTitle || 'Final Exam',
          courseName: attempt.programName || 'Unknown Program', 
          date: attempt.submittedAt || attempt.created_at
        }));
        allAttempts = [...allAttempts, ...finalAttempts];
      }
      
      // Sort by date (newest first)
      allAttempts.sort((a, b) => new Date(b.date) - new Date(a.date));
      setAttempts(allAttempts);
    } catch (error) {
      console.error('Error loading attempts:', error);
      setAttempts([]);
    }
  };

  const loadCourseSubmissions = async (courseId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendUrl}/api/courses/${courseId}/submissions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSubmissions(data.submissions || []);
      } else {
        console.error('Failed to load submissions:', response.status);
        setSubmissions([]);
      }
    } catch (error) {
      console.error('Error loading course submissions:', error);
      setSubmissions([]);
    }
  };

  const loadAllSubmissions = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendUrl}/api/courses/all/submissions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSubmissions(data.submissions || []);
      } else {
        console.error('Failed to load all submissions');
        setSubmissions([]);
      }
    } catch (error) {
      console.error('Error loading all submissions:', error);
      setSubmissions([]);
    }
  };

  const handleCourseChange = async (course) => {
    setSelectedCourse(course);
    if (viewMode === 'course') {
      await loadCourseSubmissions(course.id);
    }
  };

  const handleViewModeChange = async (mode) => {
    setViewMode(mode);
    if (mode === 'all') {
      await loadAllSubmissions();
    } else if (mode === 'course' && selectedCourse) {
      await loadCourseSubmissions(selectedCourse.id);
    }
  };

  const startGrading = (submission) => {
    setGradingSubmission(submission);
    setGradeScore('');
    setGradeFeedback('');
  };

  const submitGrade = async () => {
    const maxPoints = gradingSubmission.questionPoints || 100;
    if (!gradeScore || gradeScore < 0 || gradeScore > maxPoints) {
      toast({
        title: "Invalid Score",
        description: `Please enter a score between 0 and ${maxPoints}.`,
        variant: "destructive",
      });
      return;
    }

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendUrl}/api/submissions/${gradingSubmission.id}/grade`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          score: parseFloat(gradeScore),
          feedback: gradeFeedback
        })
      });
      
      if (response.ok) {
        toast({
          title: "Grade Submitted",
          description: `Successfully graded ${gradingSubmission.studentName}'s answer.`,
        });
        
        // Update the submission in the list
        setSubmissions(prev => prev.map(sub => 
          sub.id === gradingSubmission.id 
            ? { ...sub, status: 'graded', score: parseFloat(gradeScore), feedback: gradeFeedback }
            : sub
        ));
        
        setGradingSubmission(null);
      } else {
        throw new Error('Failed to submit grade');
      }
    } catch (error) {
      console.error('Error submitting grade:', error);
      toast({
        title: "Error",
        description: "Failed to submit grade. Please try again.",
        variant: "destructive",
      });
    }
  };

  const getPendingCount = () => {
    return submissions.filter(sub => sub.status === 'pending').length;
  };

  const getGradedCount = () => {
    return submissions.filter(sub => sub.status === 'graded').length;
  };

  // Filter attempts based on search term and type
  const getFilteredAttempts = () => {
    return attempts.filter(attempt => {
      const matchesSearch = !searchTerm || 
        attempt.studentName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        attempt.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        attempt.courseName?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = filterType === 'all' || attempt.type === filterType;
      
      return matchesSearch && matchesType;
    });
  };

  // Load detailed attempt data
  const loadAttemptDetails = async (attempt) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');
      
      let endpoint = '';
      if (attempt.type === 'quiz') {
        endpoint = `/api/quiz-attempts/${attempt.id}/detailed`;
      } else if (attempt.type === 'final') {
        endpoint = `/api/final-test-attempts/${attempt.id}/detailed`;
      }
      
      if (!endpoint) return;
      
      const response = await fetch(`${backendUrl}${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const detailedData = await response.json();
        setSelectedAttempt({
          ...attempt,
          questions: detailedData.questions || [],
          answers: detailedData.answers || [],
          detailed: true
        });
      } else {
        console.error('Failed to load attempt details');
        toast({
          title: "Error",
          description: "Failed to load attempt details.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading attempt details:', error);
      toast({
        title: "Error", 
        description: "An error occurred while loading attempt details.",
        variant: "destructive",
      });
    }
  };

  if (user?.role !== 'instructor' && user?.role !== 'admin') {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="text-center py-12">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
            <p className="text-gray-600">Only instructors and admins can access the grading center.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading grading center...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Grading Center</h1>
          <p className="text-gray-600">Review and grade student submissions</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="secondary" className="text-lg px-3 py-1">
            <Users className="w-4 h-4 mr-1" />
            {courses.length} Courses
          </Badge>
        </div>
      </div>

      {/* View Mode Toggle */}
      <Card>
        <CardHeader>
          <CardTitle>View Submissions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="radio"
                id="course-view"
                name="viewMode"
                checked={viewMode === 'course'}
                onChange={() => handleViewModeChange('course')}
                className="text-blue-600"
              />
              <label htmlFor="course-view" className="text-sm font-medium text-gray-700">
                By Course
              </label>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="radio"
                id="all-view"
                name="viewMode"
                checked={viewMode === 'all'}
                onChange={() => handleViewModeChange('all')}
                className="text-blue-600"
              />
              <label htmlFor="all-view" className="text-sm font-medium text-gray-700">
                All Submissions (Including Final Exams)
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Course Selection - Only show in course view mode */}
      {viewMode === 'course' && (
        <Card>
          <CardHeader>
            <CardTitle>Select Course</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {courses.map((course) => (
                <div
                  key={course.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedCourse?.id === course.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleCourseChange(course)}
                >
                  <h3 className="font-medium text-gray-900">{course.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{course.enrolledStudents} students enrolled</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Show submissions when either course is selected (in course mode) or in all mode */}
      {((viewMode === 'course' && selectedCourse) || viewMode === 'all') && (
        <>
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-600 text-sm font-medium">Total Submissions</p>
                    <p className="text-2xl font-bold text-blue-700">{submissions.length}</p>
                  </div>
                  <FileText className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-yellow-50 border-yellow-200">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-yellow-600 text-sm font-medium">Pending Review</p>
                    <p className="text-2xl font-bold text-yellow-700">{getPendingCount()}</p>
                  </div>
                  <Clock className="h-8 w-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-green-50 border-green-200">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-600 text-sm font-medium">Graded</p>
                    <p className="text-2xl font-bold text-green-700">{getGradedCount()}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-purple-50 border-purple-200">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-600 text-sm font-medium">
                      {viewMode === 'course' ? 'Course' : 'View Mode'}
                    </p>
                    <p className="text-lg font-bold text-purple-700 truncate">
                      {viewMode === 'course' ? selectedCourse?.title : 'All Submissions'}
                    </p>
                  </div>
                  <BookOpen className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Submissions List */}
          <Tabs defaultValue="pending" className="w-full">
            <TabsList>
              <TabsTrigger value="pending">Pending ({getPendingCount()})</TabsTrigger>
              <TabsTrigger value="graded">Graded ({getGradedCount()})</TabsTrigger>
              <TabsTrigger value="all">All ({submissions.length})</TabsTrigger>
              <TabsTrigger value="attempts">Attempt Reviews ({getFilteredAttempts().length})</TabsTrigger>
            </TabsList>
                  
                  <TabsContent value="pending" className="space-y-4">
                    {submissions.filter(sub => sub.status === 'pending').map((submission) => (
                      <SubmissionCard 
                        key={submission.id} 
                        submission={submission} 
                        onGrade={() => startGrading(submission)}
                      />
                    ))}
                  </TabsContent>
                  
                  <TabsContent value="graded" className="space-y-4">
                    {submissions.filter(sub => sub.status === 'graded').map((submission) => (
                      <SubmissionCard 
                        key={submission.id} 
                        submission={submission} 
                        onGrade={() => startGrading(submission)}
                      />
                    ))}
                  </TabsContent>
                  
                  <TabsContent value="all" className="space-y-4">
                    {submissions.map((submission) => (
                      <SubmissionCard 
                        key={submission.id} 
                        submission={submission} 
                        onGrade={() => startGrading(submission)}
                      />
                    ))}
                  </TabsContent>
                </Tabs>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Grading Modal */}
      {gradingSubmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>Grade Submission</CardTitle>
              <p className="text-sm text-gray-600">
                Student: <strong>{gradingSubmission.studentName}</strong>
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Question:</h3>
                <p className="text-gray-700 bg-gray-50 p-3 rounded">{gradingSubmission.questionText}</p>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Student Answer:</h3>
                <p className="text-gray-700 bg-blue-50 p-3 rounded whitespace-pre-wrap">
                  {gradingSubmission.studentAnswer}
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Score (0-{gradingSubmission.questionPoints || 100})
                </label>
                <input
                  type="number"
                  min="0"
                  max={gradingSubmission.questionPoints || 100}
                  value={gradeScore}
                  onChange={(e) => setGradeScore(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={`Enter score (max: ${gradingSubmission.questionPoints || 100})`}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Feedback (Optional)
                </label>
                <Textarea
                  value={gradeFeedback}
                  onChange={(e) => setGradeFeedback(e.target.value)}
                  placeholder="Provide feedback to the student..."
                  rows={4}
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <Button 
                  variant="outline" 
                  onClick={() => setGradingSubmission(null)}
                >
                  Cancel
                </Button>
                <Button onClick={submitGrade}>
                  <Star className="w-4 h-4 mr-2" />
                  Submit Grade
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

const SubmissionCard = ({ submission, onGrade }) => {
  const isFinalTest = submission.testId || submission.testTitle;
  
  return (
    <Card className={`border-l-4 ${isFinalTest ? 'border-l-purple-500' : 'border-l-blue-500'}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-medium text-gray-900">{submission.studentName}</h3>
              <Badge variant={submission.status === 'pending' ? 'secondary' : 'default'}>
                {submission.status === 'pending' ? 'Pending Review' : 'Graded'}
              </Badge>
              {isFinalTest && (
                <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-300">
                  Final Exam
                </Badge>
              )}
              {submission.status === 'graded' && (
                <Badge variant="outline">
                  Score: {submission.score}/{submission.questionPoints || 100}
                </Badge>
              )}
            </div>
            
            {/* Show context information */}
            {isFinalTest ? (
              <div className="text-xs text-gray-600 mb-2">
                <p><strong>Program:</strong> {submission.programName || 'Unknown Program'}</p>
                <p><strong>Test:</strong> {submission.testTitle || 'Final Test'}</p>
              </div>
            ) : (
              <div className="text-xs text-gray-600 mb-2">
                <p><strong>Course Quiz</strong></p>
              </div>
            )}
            
            <p className="text-sm text-gray-600 mb-2">
              <strong>Question:</strong> {submission.questionText}
            </p>
            <div className="text-sm text-gray-700 bg-gray-50 p-2 rounded mb-2">
              <strong>Student Answer:</strong>
              <p className="mt-1">{submission.studentAnswer?.slice(0, 300)}</p>
              {submission.studentAnswer?.length > 300 && <span className="text-gray-500">... (truncated)</span>}
            </div>
            
            {submission.feedback && (
              <div className="text-sm text-green-700 bg-green-50 p-2 rounded mb-2">
                <strong>Feedback:</strong>
                <p className="mt-1">{submission.feedback}</p>
              </div>
            )}
            
            <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
              <span>Submitted: {new Date(submission.submittedAt).toLocaleDateString()}</span>
              {submission.status === 'graded' && submission.gradedAt && (
                <span>Graded: {new Date(submission.gradedAt).toLocaleDateString()}</span>
              )}
            </div>
          </div>
          <Button 
            variant={submission.status === 'pending' ? 'default' : 'outline'}
            size="sm"
            onClick={onGrade}
          >
            {submission.status === 'pending' ? 'Grade' : 'Review'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default GradingCenter;
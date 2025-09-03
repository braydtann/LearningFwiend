import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Textarea } from '../components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Checkbox } from '../components/ui/checkbox';
import { Label } from '../components/ui/label';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Timer,
  Award,
  BookOpen,
  Trophy,
  Play,
  FileText,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const FinalTest = () => {
  const { courseId, programId } = useParams();
  const navigate = useNavigate();
  const { 
    user, 
    getProgramById, 
    getCourseById, 
    getAllCourses, 
    updateEnrollmentProgress,
    getAllFinalTests,
    getFinalTestById,
    submitFinalTestAttempt,
    getFinalTestAttempts
  } = useAuth();
  const { toast } = useToast();

  // Determine if this is a program or course final test
  const isProgram = programId !== undefined;
  
  const [program, setProgram] = useState(null);
  const [course, setCourse] = useState(null);
  const [finalTest, setFinalTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [previousAttempts, setPreviousAttempts] = useState([]);
  const [attemptResult, setAttemptResult] = useState(null);

  useEffect(() => {
    loadTestData();
  }, [courseId, programId, isProgram]);

  useEffect(() => {
    if (testStarted && finalTest?.timeLimit) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            // Time's up - auto submit
            handleSubmitExam();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [testStarted, finalTest]);

  const loadTestData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      if (isProgram && programId) {
        // Load program data
        const programResult = await getProgramById(programId);
        if (programResult.success) {
          setProgram(programResult.program);
          
          // Load final tests for this program
          const testsResult = await getAllFinalTests({ 
            program_id: programId, 
            published_only: true 
          });
          
          if (testsResult.success && testsResult.tests.length > 0) {
            // Get the first published final test for this program
            const testId = testsResult.tests[0].id;
            const testDetailResult = await getFinalTestById(testId);
            
            if (testDetailResult.success) {
              setFinalTest(testDetailResult.test);
              
              // Initialize time limit (convert minutes to seconds)
              if (testDetailResult.test.timeLimit) {
                setTimeRemaining(testDetailResult.test.timeLimit * 60);
              }
              
              // Load previous attempts
              const attemptsResult = await getFinalTestAttempts({ 
                test_id: testId,
                student_id: user.id 
              });
              
              if (attemptsResult.success) {
                setPreviousAttempts(attemptsResult.attempts);
              }
            } else {
              setError('Final test not found for this program');
            }
          } else {
            setError('No final test available for this program');
          }
          
          // Also load the courses to verify completion
          if (programResult.program.courseIds?.length > 0) {
            const coursesResult = await getAllCourses();
            if (coursesResult.success) {
              const programCourses = coursesResult.courses.filter(course => 
                programResult.program.courseIds.includes(course.id)
              );
              setProgram(prev => ({ ...prev, courses: programCourses }));
            }
          }
        } else {
          setError('Program not found');
        }
      } else if (courseId) {
        // Load course data - for course-level final tests
        const courseResult = await getCourseById(courseId);
        if (courseResult.success) {
          setCourse(courseResult.course);
          
          // For now, course-level final tests use the simulated interface
          // This can be expanded later if needed
          setError('Course-level final tests are not yet implemented');
        } else {
          setError('Course not found');
        }
      }
    } catch (err) {
      console.error('Error loading test data:', err);
      setError('Failed to load test data');
    } finally {
      setLoading(false);
    }
  };

  const startFinalExam = () => {
    if (!finalTest || !finalTest.questions || finalTest.questions.length === 0) {
      toast({
        title: "Error",
        description: "No questions available for this final exam.",
        variant: "destructive",
      });
      return;
    }

    setTestStarted(true);
    setCurrentQuestionIndex(0);
    setAnswers({});
    
    // Initialize time if there's a time limit
    if (finalTest.timeLimit) {
      setTimeRemaining(finalTest.timeLimit * 60);
    }

    toast({
      title: "Final Exam Started",
      description: "You are now taking the final exam. Good luck!",
    });
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < finalTest.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmitExam = async () => {
    if (!finalTest) return;

    try {
      // Prepare answers in the format expected by the backend
      const formattedAnswers = finalTest.questions.map(question => ({
        questionId: question.id,
        answer: answers[question.id] || null
      }));

      const attemptData = {
        testId: finalTest.id,
        programId: programId,
        answers: formattedAnswers,
        timeSpent: finalTest.timeLimit ? (finalTest.timeLimit * 60 - (timeRemaining || 0)) : null
      };

      const result = await submitFinalTestAttempt(attemptData);
      
      if (result.success) {
        setAttemptResult(result.attempt);
        setTestCompleted(true);
        setTestStarted(false);
        
        const score = result.attempt.score || 0;
        const passed = score >= (finalTest.passingScore || 70);
        
        toast({
          title: passed ? "Exam Completed Successfully!" : "Exam Completed",
          description: `You scored ${score}% on your final exam for "${finalTest.title}". ${passed ? 'Congratulations! Your certificate is being generated.' : 'You need 70% or higher to pass.'}`,
          variant: passed ? "default" : "destructive",
        });
        
        if (passed) {
          // Navigate to certificates page after a delay for passed exams
          setTimeout(() => {
            navigate('/certificates');
          }, 3000);
        }
      } else {
        toast({
          title: "Error",
          description: result.error || "Failed to submit exam. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error submitting final exam:', error);
      toast({
        title: "Error",
        description: "There was an error processing your exam submission.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading final exam...</p>
        </div>
      </div>
    );
  }

  if (error || (!program && isProgram) || (!course && !isProgram)) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="text-center py-12">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {error || 'Exam not found'}
            </h1>
            <p className="text-gray-600 mb-6">
              {isProgram 
                ? "The program exam you're looking for could not be found."
                : "The course exam you're looking for could not be found."
              }
            </p>
            <Button onClick={() => navigate('/dashboard')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const examTitle = isProgram ? program?.title : course?.title;
  const examType = isProgram ? "Program Final Exam" : "Course Final Exam";

  if (testCompleted) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="text-center py-12">
            <Trophy className="h-20 w-20 text-yellow-500 mx-auto mb-6" />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Congratulations! 🎉
            </h1>
            <p className="text-xl text-gray-600 mb-6">
              You have successfully completed the final exam for "{examTitle}"
            </p>
            <div className="flex gap-4 justify-center">
              <Button onClick={() => navigate('/certificates')}>
                <Award className="w-4 h-4 mr-2" />
                View Certificate
              </Button>
              <Button variant="outline" onClick={() => navigate('/dashboard')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (testStarted) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">{examType}</CardTitle>
                <p className="text-gray-600 mt-1">{examTitle}</p>
              </div>
              <Badge variant="secondary">
                <Timer className="w-4 h-4 mr-1" />
                60:00 remaining
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Simulated Exam Interface */}
            <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
              <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Final Examination in Progress
              </h3>
              <p className="text-gray-600 mb-6">
                This is a simulated final exam interface. In a real implementation, 
                this would contain actual exam questions.
              </p>
              <p className="text-sm text-gray-500 mb-6">
                For demonstration purposes, clicking "Submit Exam" will mark the exam as completed 
                with a passing grade.
              </p>
              <Button onClick={completeFinalExam} size="lg">
                Submit Exam
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate(isProgram ? `/program/${programId}` : `/course/${courseId}`)}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to {isProgram ? 'Program' : 'Course'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="text-center">
            <Trophy className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
            <CardTitle className="text-3xl mb-2">{examType}</CardTitle>
            <p className="text-xl text-gray-600">{examTitle}</p>
          </div>
        </CardHeader>
        <CardContent className="space-y-8">
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-4">
                📋 Exam Instructions
              </h3>
              <ul className="space-y-2 text-blue-800">
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  This is your final examination for {isProgram ? 'the program' : 'this course'}
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  You must achieve a passing score of 70% or higher
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  Time limit: 60 minutes
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  Upon successful completion, you will receive a certificate
                </li>
              </ul>
            </CardContent>
          </Card>

          {isProgram && program && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Program Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">{program.description}</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Total Courses</p>
                    <p className="text-lg font-semibold">{program.courseIds?.length || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Program Type</p>
                    <p className="text-lg font-semibold">Comprehensive Training</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="text-center">
            <Button onClick={startFinalExam} size="lg" className="px-8">
              <Play className="w-5 h-5 mr-2" />
              Start Final Exam
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
export default FinalTest;
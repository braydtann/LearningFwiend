import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card.jsx';
import { Button } from '../components/ui/button.jsx';
import { Badge } from '../components/ui/badge.jsx';
import { Progress } from '../components/ui/progress.jsx';
import { Textarea } from '../components/ui/textarea.jsx';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Timer,
  BookOpen,
  ChevronRight,
  ChevronLeft
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const QuizTakingNewFixed = () => {
  // Get URL parameters safely
  const urlParams = useParams();
  const navigate = useNavigate();
  const authContext = useAuth();
  const toastContext = useToast();
  
  // Extract values with fallbacks to prevent temporal dead zone
  const courseId = urlParams?.courseId || null;
  const lessonId = urlParams?.lessonId || null;
  const user = authContext?.user || null;
  const getCourseById = authContext?.getCourseById || null;
  const updateEnrollmentProgress = authContext?.updateEnrollmentProgress || null;
  const toast = toastContext?.toast || (() => console.log('Toast not available'));

  // All state declarations
  const [course, setCourse] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Refs for stable references
  const isMountedRef = useRef(true);
  const timerRef = useRef(null);

  // Initialize quiz data
  const initializeQuiz = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (!courseId || !lessonId) {
        throw new Error('Missing course ID or lesson ID');
      }

      if (!getCourseById || typeof getCourseById !== 'function') {
        throw new Error('getCourseById function not available');
      }

      console.log('Loading course:', courseId);
      const courseResult = await getCourseById(courseId);
      
      if (!courseResult.success) {
        throw new Error('Failed to load course');
      }

      const courseData = courseResult.course;
      setCourse(courseData);

      // Find the lesson and quiz
      let foundLesson = null;
      let foundQuiz = null;

      // Safely iterate through modules - handle both old and new quiz structures
      if (courseData.modules && Array.isArray(courseData.modules)) {
        for (let i = 0; i < courseData.modules.length; i++) {
          const module = courseData.modules[i];
          if (module && module.lessons && Array.isArray(module.lessons)) {
            for (let j = 0; j < module.lessons.length; j++) {
              const moduleLesson = module.lessons[j];
              if (moduleLesson && moduleLesson.id === lessonId) {
                foundLesson = moduleLesson;
                if (moduleLesson.type === 'quiz') {
                  // Handle both old and new quiz structures
                  if (moduleLesson.questions && Array.isArray(moduleLesson.questions)) {
                    // New structure: questions directly on lesson
                    foundQuiz = {
                      questions: moduleLesson.questions,
                      timeLimit: moduleLesson.timeLimit,
                      passingScore: moduleLesson.passingScore,
                      maxAttempts: moduleLesson.maxAttempts,
                      targetQuestionCount: moduleLesson.targetQuestionCount,
                      // Copy any other quiz properties that might exist
                      ...moduleLesson.quiz
                    };
                  } else if (moduleLesson.quiz && moduleLesson.quiz.questions) {
                    // Old structure: questions nested in quiz object
                    foundQuiz = {
                      ...moduleLesson.quiz,
                      // Ensure all expected properties exist with defaults
                      questions: moduleLesson.quiz.questions || [],
                      timeLimit: moduleLesson.quiz.timeLimit,
                      passingScore: moduleLesson.quiz.passingScore,
                      maxAttempts: moduleLesson.quiz.maxAttempts,
                      targetQuestionCount: moduleLesson.quiz.targetQuestionCount
                    };
                  }
                }
                break;
              }
            }
          }
          if (foundLesson) break;
        }
      }

      if (!foundLesson) {
        throw new Error('Lesson not found');
      }

      if (!foundQuiz || !foundQuiz.questions || foundQuiz.questions.length === 0) {
        throw new Error('Quiz not found or has no questions');
      }
      
      // Validate each question has required structure to prevent React Error #31
      const validatedQuestions = foundQuiz.questions.filter((question, index) => {
        if (!question || typeof question !== 'object') {
          console.warn(`Question ${index + 1} is invalid (not an object):`, question);
          return false;
        }
        if (!question.type) {
          console.warn(`Question ${index + 1} missing type:`, question);
          return false;
        }
        
        // Validate question-type specific requirements
        if (question.type === 'true-false') {
          // True/false questions don't need additional validation
        } else if (question.type === 'multiple-choice') {
          // Multiple choice questions need options array
          if (!question.options || !Array.isArray(question.options) || question.options.length < 2) {
            console.warn(`Question ${index + 1} (multiple-choice) missing valid options array:`, question);
            return false;
          }
          if (typeof question.correctAnswer !== 'number' || question.correctAnswer < 0 || question.correctAnswer >= question.options.length) {
            console.warn(`Question ${index + 1} (multiple-choice) has invalid correctAnswer:`, question.correctAnswer);
            return false;
          }
        } else if (question.type === 'select-all-that-apply') {
          // Select all questions need options array and correctAnswers array
          if (!question.options || !Array.isArray(question.options) || question.options.length < 2) {
            console.warn(`Question ${index + 1} (select-all-that-apply) missing valid options array:`, question);
            return false;
          }
          if (!question.correctAnswers || !Array.isArray(question.correctAnswers) || question.correctAnswers.length === 0) {
            console.warn(`Question ${index + 1} (select-all-that-apply) missing valid correctAnswers array:`, question.correctAnswers);
            return false;
          }
          // Validate that all correctAnswers indices are within options range
          const invalidIndices = question.correctAnswers.filter(idx => 
            typeof idx !== 'number' || idx < 0 || idx >= question.options.length
          );
          if (invalidIndices.length > 0) {
            console.warn(`Question ${index + 1} (select-all-that-apply) has invalid correctAnswers indices:`, invalidIndices);
            return false;
          }
        } else if (question.type === 'short-answer' || question.type === 'long-form-answer') {
          // Text questions don't need additional validation
        } else {
          console.warn(`Question ${index + 1} has unsupported type: ${question.type}`);
          return false;
        }
        
        return true;
      });
      
      if (validatedQuestions.length === 0) {
        throw new Error('No valid questions found after validation');
      }
      
      if (validatedQuestions.length < foundQuiz.questions.length) {
        console.warn(`Filtered out ${foundQuiz.questions.length - validatedQuestions.length} invalid questions`);
        foundQuiz = {
          ...foundQuiz,
          questions: validatedQuestions
        };
      }

      setLesson(foundLesson);
      
      // Handle target question count if specified
      if (foundQuiz.targetQuestionCount && foundQuiz.targetQuestionCount > 0 && foundQuiz.questions.length > foundQuiz.targetQuestionCount) {
        // If we have more questions than target, take the first targetQuestionCount questions
        // This prevents array access issues if targetQuestionCount is set incorrectly
        foundQuiz = {
          ...foundQuiz,
          questions: foundQuiz.questions.slice(0, foundQuiz.targetQuestionCount)
        };
        console.log(`Quiz filtered to ${foundQuiz.targetQuestionCount} questions (was ${foundQuiz.questions.length})`);
      }
      
      setQuiz(foundQuiz);
      
      // Initialize timer if quiz has time limit
      if (foundQuiz.timeLimit && foundQuiz.timeLimit > 0) {
        setTimeLeft(foundQuiz.timeLimit * 60); // Convert minutes to seconds
      }

      console.log('Quiz initialized successfully:', {
        questions: foundQuiz.questions.length,
        timeLimit: foundQuiz.timeLimit
      });

    } catch (err) {
      console.error('Error initializing quiz:', err);
      if (isMountedRef.current) {
        setError(err.message);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [courseId, lessonId, getCourseById]);

  // Submit quiz - MOVED UP to prevent temporal dead zone
  const handleSubmitQuiz = useCallback(async () => {
    if (!isMountedRef.current || submitting || quizCompleted) return;

    try {
      setSubmitting(true);
      console.log('Submitting quiz with answers:', answers);

      // Calculate score
      let correctAnswers = 0;
      const totalQuestions = quiz?.questions?.length || 0;

      // Safely iterate through questions
      if (quiz?.questions && Array.isArray(quiz.questions)) {
        for (let i = 0; i < quiz.questions.length; i++) {
          const question = quiz.questions[i];
          if (question && question.id) {
            const userAnswer = answers[question.id];
            
            // Handle different question types  
            if (question.type === 'true-false' && userAnswer === question.correctAnswer) {
              correctAnswers++;
            } else if (question.type === 'multiple-choice' && userAnswer === question.correctAnswer) {
              correctAnswers++;
            } else if (question.type === 'select-all-that-apply') {
              // For select-all questions, user must select ALL correct answers and NO incorrect ones
              const userSelectedAnswers = Array.isArray(userAnswer) ? userAnswer : [];
              const correctAnswers_array = Array.isArray(question.correctAnswers) ? question.correctAnswers : [];
              
              // Sort both arrays to compare them properly
              const sortedUserAnswers = [...userSelectedAnswers].sort((a, b) => a - b);
              const sortedCorrectAnswers = [...correctAnswers_array].sort((a, b) => a - b);
              
              // Check if arrays are exactly equal (same length and same elements)
              const isCorrect = sortedUserAnswers.length === sortedCorrectAnswers.length &&
                               sortedUserAnswers.every((answer, index) => answer === sortedCorrectAnswers[index]);
              
              if (isCorrect) {
                correctAnswers++;
              }
            } else if (question.type === 'short-answer' || question.type === 'long-form-answer') {
              // For text answers, basic string comparison (case-insensitive)
              const correctAnswer = question.correctAnswer || '';
              const userAnswerText = (userAnswer || '').toString().trim().toLowerCase();
              const correctAnswerText = correctAnswer.toString().trim().toLowerCase();
              if (userAnswerText === correctAnswerText) {
                correctAnswers++;
              }
            }
          }
        }
      }

      const score = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;
      const passed = score >= (quiz?.passingScore || 70);

      // Update progress
      if (updateEnrollmentProgress && typeof updateEnrollmentProgress === 'function') {
        const progressResult = await updateEnrollmentProgress(courseId, {
          progress: passed ? 100 : 0, // Set progress to 100% if passed, 0% if failed
          currentLessonId: lessonId,
          timeSpent: quiz?.timeLimit ? (quiz.timeLimit * 60 - (timeLeft || 0)) : null
        });

        if (progressResult.success) {
          if (isMountedRef.current) {
            setQuizCompleted(true);
            
            toast({
              title: passed ? "🎉 Quiz Passed!" : "📝 Quiz Completed",
              description: `Your score: ${score}% ${passed ? '(Passed)' : '(Below passing score)'}`,
              duration: 3000,
            });

            // Navigate to course after delay
            setTimeout(() => {
              if (isMountedRef.current) {
                navigate(`/course/${courseId}`);
              }
            }, 2000);
          }
        } else {
          throw new Error('Failed to update progress');
        }
      } else {
        throw new Error('updateEnrollmentProgress function not available');
      }

    } catch (err) {
      console.error('Error submitting quiz:', err);
      if (isMountedRef.current) {
        toast({
          title: "Error submitting quiz",
          description: "Please try again or contact support if the problem persists.",
          variant: "destructive",
        });
      }
    } finally {
      if (isMountedRef.current) {
        setSubmitting(false);
      }
    }
  }, [answers, quiz, courseId, lessonId, timeLeft, submitting, quizCompleted, updateEnrollmentProgress, toast, navigate]);

  // Initialize quiz on mount
  useEffect(() => {
    initializeQuiz();
  }, [initializeQuiz]);

  // Timer management with proper cleanup
  useEffect(() => {
    // Clear any existing timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // Start timer if conditions are met
    if (quizStarted && timeLeft !== null && timeLeft > 0 && !quizCompleted && quiz?.questions) {
      timerRef.current = setInterval(() => {
        if (!isMountedRef.current) return;
        
        setTimeLeft(prev => {
          if (prev <= 1) {
            return 0; // Will trigger auto-submit via separate effect
          }
          return prev - 1;
        });
      }, 1000);
    }

    // Cleanup function
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [quizStarted, timeLeft, quizCompleted, quiz]);

  // Auto-submit when time runs out
  useEffect(() => {
    if (quizStarted && timeLeft === 0 && !quizCompleted && !submitting && isMountedRef.current) {
      console.log('Time up - auto-submitting quiz');
      handleSubmitQuiz();
    }
  }, [timeLeft, quizStarted, quizCompleted, submitting, handleSubmitQuiz]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Format time display
  const formatTime = (seconds) => {
    if (seconds === null) return '';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Start quiz
  const handleStartQuiz = useCallback(() => {
    if (!isMountedRef.current) return;
    setQuizStarted(true);
    console.log('Quiz started');
  }, []);

  // Handle answer change
  const handleAnswerChange = useCallback((questionId, answer) => {
    if (!isMountedRef.current) return;
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  }, []);

  // Navigate between questions
  const handlePreviousQuestion = useCallback(() => {
    if (!isMountedRef.current || !quiz?.questions) return;
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => Math.max(0, prev - 1));
    }
  }, [currentQuestionIndex, quiz]);

  const handleNextQuestion = useCallback(() => {
    if (!isMountedRef.current || !quiz?.questions) return;
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(prev => Math.min(quiz.questions.length - 1, prev + 1));
    }
  }, [currentQuestionIndex, quiz]);



  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading quiz...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Quiz Loading Error</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <div className="space-y-2">
              <Button 
                onClick={() => navigate(`/course/${courseId}`)}
                className="w-full"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Course
              </Button>
              <Button 
                onClick={() => window.location.reload()}
                variant="outline"
                className="w-full"
              >
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Quiz not started state
  if (!quizStarted) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="mb-6">
            <Button 
              onClick={() => navigate(`/course/${courseId}`)}
              variant="outline"
              className="mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Course
            </Button>
          </div>

          <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-blue-600" />
                <span>{lesson?.title || 'Quiz'}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span>Questions: {quiz?.questions?.length || 0}</span>
                  </div>
                  {quiz?.timeLimit && (
                    <div className="flex items-center space-x-2">
                      <Timer className="w-4 h-4 text-orange-600" />
                      <span>Time Limit: {quiz.timeLimit} minutes</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-blue-600" />
                    <span>Passing Score: {quiz?.passingScore || 70}%</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-purple-600" />
                    <span>Max Attempts: {quiz?.maxAttempts || 'Unlimited'}</span>
                  </div>
                </div>

                {quiz?.description && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800 text-sm">{quiz.description}</p>
                  </div>
                )}

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-800 mb-2">Instructions:</h4>
                  <ul className="text-yellow-700 text-sm space-y-1">
                    <li>• Read each question carefully before answering</li>
                    <li>• You can navigate between questions using the Next/Previous buttons</li>
                    <li>• Make sure to answer all questions before submitting</li>
                    {quiz?.timeLimit && <li>• The quiz will auto-submit when time runs out</li>}
                    <li>• Click "Submit Quiz" when you're ready to finish</li>
                  </ul>
                </div>
              </div>

              <Button 
                onClick={handleStartQuiz}
                className="w-full bg-blue-600 hover:bg-blue-700"
                size="lg"
              >
                Start Quiz
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Quiz completed state
  if (quizCompleted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Quiz Submitted!</h3>
            <p className="text-gray-600 mb-4">Returning to course...</p>
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Main quiz taking interface
  // Add comprehensive null checks to prevent React Error #31
  if (!quiz || !quiz.questions || !Array.isArray(quiz.questions) || quiz.questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Quiz Error</h3>
            <p className="text-gray-600 mb-4">Quiz data is invalid or missing questions</p>
            <Button onClick={() => navigate(`/course/${courseId}`)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Course
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Ensure currentQuestionIndex is within bounds
  const safeCurrentQuestionIndex = Math.max(0, Math.min(currentQuestionIndex, quiz.questions.length - 1));
  const rawCurrentQuestion = quiz.questions[safeCurrentQuestionIndex];
  
  // Create a safely validated current question object
  const currentQuestion = rawCurrentQuestion && typeof rawCurrentQuestion === 'object' ? {
    ...rawCurrentQuestion,
    id: rawCurrentQuestion.id || `question-${safeCurrentQuestionIndex}`,
    type: rawCurrentQuestion.type || 'unknown',
    text: rawCurrentQuestion.text || '',
    options: Array.isArray(rawCurrentQuestion.options) ? rawCurrentQuestion.options : [],
    items: Array.isArray(rawCurrentQuestion.items) ? rawCurrentQuestion.items : []
  } : null;
  
  // Additional safety check for currentQuestion
  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Question Error</h3>
            <p className="text-gray-600 mb-4">Current question could not be loaded</p>
            <Button onClick={() => navigate(`/course/${courseId}`)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Course
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const progress = ((safeCurrentQuestionIndex + 1) / quiz.questions.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <Button 
            onClick={() => navigate(`/course/${courseId}`)}
            variant="outline"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Course
          </Button>
          
          {timeLeft !== null && (
            <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded-lg border">
              <Timer className="w-4 h-4 text-orange-600" />
              <span className="font-mono text-lg font-semibold">
                {formatTime(timeLeft)}
              </span>
            </div>
          )}
        </div>

        {/* Progress */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">
              Question {safeCurrentQuestionIndex + 1} of {quiz.questions.length}
            </span>
            <span className="text-sm text-gray-600">
              {Math.round(progress)}% Complete
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Question Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">
              {currentQuestion?.question || 'Question not available'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* True/False Questions */}
            {currentQuestion?.type === 'true-false' && (
              <div className="space-y-3">
                {[true, false].map((value) => (
                  <label
                    key={`tf-${value.toString()}`}
                    className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                  >
                    <input
                      type="radio"
                      name={`question-${currentQuestion.id || 'unknown'}`}
                      value={value.toString()}
                      checked={answers[currentQuestion.id] === value}
                      onChange={(e) => {
                        if (currentQuestion?.id) {
                          handleAnswerChange(currentQuestion.id, e.target.value === 'true');
                        }
                      }}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="flex-1">{value ? 'True' : 'False'}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Multiple Choice Questions */}
            {currentQuestion?.type === 'multiple-choice' && (
              <div className="space-y-3">
                {(Array.isArray(currentQuestion.options) ? currentQuestion.options : []).map((option, index) => {
                  // Handle both string and object option formats with defensive programming
                  const optionText = typeof option === 'string' ? option : (option?.text || `Option ${index + 1}`);
                  const optionImage = typeof option === 'object' ? option?.image : null;
                  const optionAudio = typeof option === 'object' ? option?.audio : null;
                  
                  return (
                    <label
                      key={`mc-${index}`}
                      className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <input
                        type="radio"
                        name={`question-${currentQuestion.id || 'unknown'}`}
                        value={index.toString()}
                        checked={answers[currentQuestion.id] === index}
                        onChange={(e) => {
                          if (currentQuestion?.id) {
                            handleAnswerChange(currentQuestion.id, parseInt(e.target.value));
                          }
                        }}
                        className="w-4 h-4 text-blue-600 mt-1"
                      />
                      <div className="flex-1">
                        <span className="block text-gray-900">{optionText}</span>
                        
                        {/* Display option image if available */}
                        {optionImage && optionImage.trim() !== '' && (
                          <div className="mt-2">
                            <img 
                              src={optionImage} 
                              alt={`Option ${index + 1}`} 
                              className="max-w-xs h-32 object-cover rounded border"
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          </div>
                        )}
                        
                        {/* Display option audio if available */}
                        {optionAudio && optionAudio.trim() !== '' && (
                          <div className="mt-2">
                            <audio controls className="w-full max-w-xs">
                              <source src={optionAudio} type="audio/mpeg" />
                              Your browser does not support the audio element.
                            </audio>
                          </div>
                        )}
                      </div>
                    </label>
                  );
                })}
                
                {/* Fallback if no options available */}
                {(!currentQuestion.options || !Array.isArray(currentQuestion.options) || currentQuestion.options.length === 0) && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800">No answer options available for this question.</p>
                  </div>
                )}
              </div>
            )}

            {/* Select All That Apply Questions */}
            {currentQuestion?.type === 'select-all-that-apply' && (
              <div className="space-y-3">
                {(Array.isArray(currentQuestion.options) ? currentQuestion.options : []).map((option, index) => {
                  // Handle both string and object option formats with defensive programming
                  const optionText = typeof option === 'string' ? option : (option?.text || `Option ${index + 1}`);
                  const optionImage = typeof option === 'object' ? option?.image : null;
                  const optionAudio = typeof option === 'object' ? option?.audio : null;
                  
                  // Get current selected answers (array of indices)
                  const selectedAnswers = Array.isArray(answers[currentQuestion.id]) ? answers[currentQuestion.id] : [];
                  const isSelected = selectedAnswers.includes(index);
                  
                  return (
                    <label
                      key={`sata-${index}`}
                      className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <input
                        type="checkbox"
                        name={`question-${currentQuestion.id || 'unknown'}`}
                        value={index.toString()}
                        checked={isSelected}
                        onChange={(e) => {
                          if (currentQuestion?.id) {
                            const currentAnswers = Array.isArray(answers[currentQuestion.id]) ? answers[currentQuestion.id] : [];
                            let newAnswers;
                            
                            if (e.target.checked) {
                              // Add this index to selected answers
                              newAnswers = [...currentAnswers, index];
                            } else {
                              // Remove this index from selected answers
                              newAnswers = currentAnswers.filter(idx => idx !== index);
                            }
                            
                            handleAnswerChange(currentQuestion.id, newAnswers);
                          }
                        }}
                        className="w-4 h-4 text-blue-600 mt-1"
                      />
                      <div className="flex-1">
                        <span className="block text-gray-900">{optionText}</span>
                        
                        {/* Display option image if available */}
                        {optionImage && optionImage.trim() !== '' && (
                          <div className="mt-2">
                            <img 
                              src={optionImage} 
                              alt={`Option ${index + 1}`} 
                              className="max-w-xs h-32 object-cover rounded border"
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          </div>
                        )}
                        
                        {/* Display option audio if available */}
                        {optionAudio && optionAudio.trim() !== '' && (
                          <div className="mt-2">
                            <audio controls className="w-full max-w-xs">
                              <source src={optionAudio} type="audio/mpeg" />
                              Your browser does not support the audio element.
                            </audio>
                          </div>
                        )}
                      </div>
                    </label>
                  );
                })}
                
                {/* Fallback if no options available */}
                {(!currentQuestion.options || !Array.isArray(currentQuestion.options) || currentQuestion.options.length === 0) && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800">No answer options available for this question.</p>
                  </div>
                )}
                
                {/* Show selected count */}
                {Array.isArray(answers[currentQuestion.id]) && answers[currentQuestion.id].length > 0 && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-blue-800 text-sm">
                      ✓ Selected {answers[currentQuestion.id].length} option{answers[currentQuestion.id].length !== 1 ? 's' : ''}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Short Answer Questions */}
            {currentQuestion?.type === 'short-answer' && (
              <Textarea
                placeholder="Enter your answer here..."
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => {
                  if (currentQuestion?.id) {
                    handleAnswerChange(currentQuestion.id, e.target.value);
                  }
                }}
                className="min-h-[100px]"
              />
            )}

            {/* Long Form Answer Questions */}
            {currentQuestion?.type === 'long-form-answer' && (
              <Textarea
                placeholder="Enter your detailed answer here..."
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => {
                  if (currentQuestion?.id) {
                    handleAnswerChange(currentQuestion.id, e.target.value);
                  }
                }}
                className="min-h-[200px]"
              />
            )}



            {/* Fallback for unknown question types */}
            {currentQuestion && !['true-false', 'multiple-choice', 'select-all-that-apply', 'short-answer', 'long-form-answer'].includes(currentQuestion.type) && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800">
                  Unsupported question type: {currentQuestion.type}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation and Submit */}
        <div className="flex items-center justify-between">
          <Button
            onClick={handlePreviousQuestion}
            disabled={safeCurrentQuestionIndex === 0}
            variant="outline"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          <div className="flex space-x-3">
            {safeCurrentQuestionIndex < quiz.questions.length - 1 ? (
              <Button onClick={handleNextQuestion}>
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmitQuiz}
                disabled={submitting}
                className="bg-green-600 hover:bg-green-700"
              >
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizTakingNewFixed;
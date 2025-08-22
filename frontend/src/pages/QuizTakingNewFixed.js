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

      // Safely iterate through modules
      if (courseData.modules && Array.isArray(courseData.modules)) {
        for (let i = 0; i < courseData.modules.length; i++) {
          const module = courseData.modules[i];
          if (module && module.lessons && Array.isArray(module.lessons)) {
            for (let j = 0; j < module.lessons.length; j++) {
              const moduleLesson = module.lessons[j];
              if (moduleLesson && moduleLesson.id === lessonId) {
                foundLesson = moduleLesson;
                if (moduleLesson.type === 'quiz' && moduleLesson.quiz) {
                  foundQuiz = moduleLesson.quiz;
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

      setLesson(foundLesson);
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
            if (question.type === 'multiple-choice' && userAnswer === question.correctAnswer) {
              correctAnswers++;
            } else if (question.type === 'true-false' && userAnswer === question.correctAnswer) {
              correctAnswers++;
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
  const currentQuestion = quiz.questions[safeCurrentQuestionIndex];
  
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
            {/* Multiple Choice Questions */}
            {currentQuestion?.type === 'multiple-choice' && currentQuestion?.options && (
              <div className="space-y-3">
                {currentQuestion.options.map((option, index) => (
                  <label
                    key={`option-${index}`}
                    className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                  >
                    <input
                      type="radio"
                      name={`question-${currentQuestion.id || 'unknown'}`}
                      value={index}
                      checked={answers[currentQuestion.id] === index}
                      onChange={(e) => {
                        const value = parseInt(e.target.value);
                        if (currentQuestion.id) {
                          handleAnswerChange(currentQuestion.id, value);
                        }
                      }}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="flex-1">{option || `Option ${index + 1}`}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Select All That Apply Questions */}
            {currentQuestion?.type === 'select-all-that-apply' && currentQuestion?.options && (
              <div className="space-y-3">
                <p className="text-sm text-gray-600 mb-3">Select all correct answers:</p>
                {currentQuestion.options.map((option, index) => (
                  <label
                    key={`select-${index}`}
                    className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                  >
                    <input
                      type="checkbox"
                      value={index}
                      checked={(answers[currentQuestion.id] || []).includes(index)}
                      onChange={(e) => {
                        if (currentQuestion.id) {
                          const currentAnswers = answers[currentQuestion.id] || [];
                          const value = parseInt(e.target.value);
                          const newAnswers = e.target.checked
                            ? [...currentAnswers, value]
                            : currentAnswers.filter(v => v !== value);
                          handleAnswerChange(currentQuestion.id, newAnswers);
                        }
                      }}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="flex-1">{option || `Option ${index + 1}`}</span>
                  </label>
                ))}
              </div>
            )}

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
                        if (currentQuestion.id) {
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

            {/* Short Answer Questions */}
            {currentQuestion?.type === 'short-answer' && (
              <Textarea
                placeholder="Enter your answer here..."
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => {
                  if (currentQuestion.id) {
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
                  if (currentQuestion.id) {
                    handleAnswerChange(currentQuestion.id, e.target.value);
                  }
                }}
                className="min-h-[200px]"
              />
            )}

            {/* Chronological Order Questions */}
            {currentQuestion?.type === 'chronological-order' && currentQuestion?.items && (
              <div className="space-y-3">
                <p className="text-sm text-gray-600 mb-3">Drag and drop to arrange in chronological order:</p>
                <div className="space-y-2">
                  {currentQuestion.items.map((item, index) => (
                    <div
                      key={`chrono-${index}`}
                      className="flex items-center space-x-3 p-3 border rounded-lg bg-gray-50"
                    >
                      <span className="text-sm font-medium text-gray-500 min-w-[60px]">
                        Position:
                      </span>
                      <select
                        value={answers[currentQuestion.id]?.[index] || index + 1}
                        onChange={(e) => {
                          if (currentQuestion.id) {
                            const currentOrder = answers[currentQuestion.id] || currentQuestion.items.map((_, i) => i + 1);
                            const newOrder = [...currentOrder];
                            newOrder[index] = parseInt(e.target.value);
                            handleAnswerChange(currentQuestion.id, newOrder);
                          }
                        }}
                        className="border rounded px-2 py-1 text-sm"
                      >
                        {currentQuestion.items.map((_, i) => (
                          <option key={i} value={i + 1}>{i + 1}</option>
                        ))}
                      </select>
                      <span className="flex-1">{item || `Item ${index + 1}`}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Fallback for unknown question types */}
            {currentQuestion && !['multiple-choice', 'select-all-that-apply', 'true-false', 'short-answer', 'long-form-answer', 'chronological-order'].includes(currentQuestion.type) && (
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
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Textarea } from '../components/ui/textarea';
import ScreenRecorder from '../components/ScreenRecorder';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Timer,
  BookOpen
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const QuizTaking = () => {
  const { courseId, lessonId } = useParams();
  const navigate = useNavigate();
  const { user, getCourseById } = useAuth();
  const { toast } = useToast();

  // Course and lesson loading states
  const [course, setCourse] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [courseLoading, setCourseLoading] = useState(true);
  const [courseError, setCourseError] = useState(null);

  // Load course data from backend
  useEffect(() => {
    const loadCourseData = async () => {
      try {
        setCourseLoading(true);
        const result = await getCourseById(courseId);
        
        if (result.success) {
          const courseData = result.course;
          setCourse(courseData);
          
          // Find the lesson and quiz
          let foundLesson = null;
          for (const module of courseData.modules || []) {
            if (module.lessons) {
              foundLesson = module.lessons.find(l => l.id === lessonId);
              if (foundLesson) break;
            }
          }
          
          if (foundLesson) {
            setLesson(foundLesson);
            if (foundLesson.type === 'quiz' && foundLesson.quiz) {
              setQuiz(foundLesson.quiz);
            } else {
              setCourseError('This lesson is not a quiz or quiz data is missing');
            }
          } else {
            setCourseError('Lesson not found in course');
          }
        } else {
          setCourseError(result.error || 'Course not found');
        }
      } catch (err) {
        console.error('Error loading course data:', err);
        setCourseError('Failed to load course data');
      } finally {
        setCourseLoading(false);
      }
    };

    loadCourseData();
  }, [courseId, lessonId, getCourseById]);

  // Quiz state
  const [quizState, setQuizState] = useState('loading'); // loading, ready, taking, submitted, error
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [quizResults, setQuizResults] = useState(null);

  // Get existing attempts and results (placeholder for now - will need backend API)
  const attempts = []; // TODO: Replace with backend API call
  const existingResults = null; // TODO: Replace with backend API call
  const canTakeQuiz = !existingResults || (existingResults.totalAttempts || 0) < (quiz?.maxAttempts || 3);

  useEffect(() => {
    if (!courseLoading) {
      if (!course || !lesson || !quiz) {
        console.error('Quiz component error - missing data:', { 
          course: !!course, 
          lesson: !!lesson, 
          quiz: !!quiz,
          courseError
        });
        setQuizState('error');
        return;
      }

      // Check if user can take the quiz
      if (!canTakeQuiz) {
        console.log('Max attempts reached for quiz');
        setQuizState('max-attempts-reached');
        return;
      }

      console.log('Quiz ready - all data loaded successfully');
      setQuizState('ready');
    } else {
      console.log('Quiz still loading course data...');
      setQuizState('loading');
    }
  }, [courseLoading, course, lesson, quiz, canTakeQuiz, courseError]);

  // Show loading state
  if (courseLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Loading quiz...</h3>
        <p className="text-gray-600">Please wait while we fetch the quiz data.</p>
      </div>
    );
  }

  // Show error state
  if (courseError || quizState === 'error') {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Quiz Not Available
        </h1>
        <p className="text-gray-600 mb-6">
          {courseError || 'This quiz could not be found or is not available.'}
        </p>
        <div className="space-x-4">
          <Button onClick={() => navigate(`/course/${courseId}`)}>
            Back to Course
          </Button>
          <Button variant="outline" onClick={() => navigate('/courses')}>
            All Courses
          </Button>
        </div>
      </div>
    );
  }

  // Timer effect
  useEffect(() => {
    if (quizState === 'taking' && timeLeft > 0) {
      const timer = setTimeout(() => {
        setTimeLeft(timeLeft - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (quizState === 'taking' && timeLeft === 0) {
      handleSubmitQuiz();
    }
  }, [quizState, timeLeft]);

  const startQuiz = () => {
    setQuizState('taking');
    setStartTime(Date.now());
    setTimeLeft((quiz.timeLimit || 10) * 60); // Convert minutes to seconds
    setAnswers({});
    setCurrentQuestionIndex(0);
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitQuiz = () => {
    const endTime = Date.now();
    const timeSpent = Math.floor((endTime - startTime) / 1000);
    
    // Calculate score
    let totalPoints = 0;
    let earnedPoints = 0;
    
    const gradedAnswers = quiz.questions.map(question => {
      const userAnswer = answers[question.id];
      let correct = false;
      let points = 0;
      
      totalPoints += question.points;
      
      if (question.type === 'multiple-choice') {
        correct = userAnswer === question.correctAnswer;
      } else if (question.type === 'select-all-that-apply') {
        const correctAnswers = question.correctAnswers || [];
        const userAnswers = userAnswer || [];
        correct = correctAnswers.length === userAnswers.length && 
                 correctAnswers.every(answer => userAnswers.includes(answer));
      } else if (question.type === 'true-false') {
        correct = userAnswer === question.correctAnswer;
      } else if (question.type === 'short-answer') {
        // For demo purposes, mark as correct if answer contains key terms
        // In real app, this might need manual grading
        correct = userAnswer && 
          userAnswer.toLowerCase().includes(question.correctAnswer.toLowerCase().split(' ')[0]);
      } else if (question.type === 'long-form-answer') {
        // Long form answers require manual grading - mark as pending for now
        // In real app, instructor would grade these manually
        correct = userAnswer && userAnswer.trim().length > 50; // Basic completion check
      } else if (question.type === 'chronological-order') {
        const correctOrder = question.correctOrder || [];
        const userOrder = userAnswer || [];
        correct = correctOrder.length === userOrder.length && 
                 correctOrder.every((item, index) => item === userOrder[index]);
      } else if (question.type === 'record-screen' || question.type === 'record_screen') {
        // Screen recording questions require manual grading
        // For now, mark as completed if recording exists
        correct = userAnswer && userAnswer.hasRecording && userAnswer.duration > 0;
      }
      
      if (correct) {
        points = question.points;
        earnedPoints += points;
      }
      
      return {
        questionId: question.id,
        answer: userAnswer,
        correct,
        points
      };
    });

    const score = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
    const passed = score >= (quiz.passingScore || 70);

    const results = {
      score,
      totalPoints,
      earnedPoints,
      passed,
      timeSpent,
      answers: gradedAnswers,
      completedAt: new Date().toISOString()
    };

    setQuizResults(results);
    setQuizState('submitted');
    
    if (quiz.showResults) {
      setShowResults(true);
    }

    toast({
      title: passed ? "Quiz Completed!" : "Quiz Submitted",
      description: passed 
        ? `Congratulations! You scored ${score}% and passed the quiz.`
        : `You scored ${score}%. The passing score is ${quiz.passingScore || 70}%.`,
      variant: passed ? "default" : "destructive"
    });
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    return Math.round(((currentQuestionIndex + 1) / quiz.questions.length) * 100);
  };

  if (quizState === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (quizState === 'error' || !quiz) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Quiz not found</h1>
        <p className="text-gray-600 mb-6">The quiz you're looking for doesn't exist or has been removed.</p>
        <Button onClick={() => navigate(`/courses/${courseId}`)}>
          Back to Course
        </Button>
      </div>
    );
  }

  if (quizState === 'max-attempts-reached') {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <AlertCircle className="w-16 h-16 text-orange-600 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Maximum Attempts Reached</h1>
          <p className="text-gray-600 mb-6">
            You have used all {quiz.maxAttempts} attempts for this quiz.
          </p>
          {existingResults && (
            <div className="bg-gray-50 p-4 rounded-lg mb-6 max-w-sm mx-auto">
              <p className="text-sm text-gray-600">Your best score:</p>
              <p className="text-2xl font-bold text-gray-900">{existingResults.bestScore}%</p>
              <p className="text-sm text-gray-600">
                {existingResults.passed ? '✅ Passed' : '❌ Not Passed'}
              </p>
            </div>
          )}
          <Button onClick={() => navigate(`/courses/${courseId}`)}>
            Back to Course
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate(`/courses/${courseId}`)}
          disabled={quizState === 'taking'}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Course
        </Button>
        <div className="h-6 border-l border-gray-300"></div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{quiz.title || lesson.title}</h1>
          <p className="text-gray-600">{course.title}</p>
        </div>
      </div>

      {quizState === 'ready' && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <BookOpen className="w-5 h-5 mr-2" />
              Ready to Start?
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {quiz.description && (
                <p className="text-gray-600">{quiz.description}</p>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 py-4">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Timer className="w-5 h-5 text-blue-600 mr-1" />
                  </div>
                  <p className="text-sm text-gray-600">Time Limit</p>
                  <p className="font-bold">{quiz.timeLimit} minutes</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-1" />
                  </div>
                  <p className="text-sm text-gray-600">Questions</p>
                  <p className="font-bold">{quiz.questions.length}</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Badge className="bg-purple-100 text-purple-800">
                      {quiz.passingScore}%
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">Passing Score</p>
                  <p className="font-bold">Required</p>
                </div>
              </div>

              {existingResults && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-blue-700 mb-2">
                    Previous attempts: {existingResults.totalAttempts} of {quiz.maxAttempts}
                  </p>
                  <p className="text-sm text-blue-700">
                    Best score: {existingResults.bestScore}%
                  </p>
                </div>
              )}

              <div className="flex items-center justify-center pt-4">
                <Button onClick={startQuiz} size="lg" className="bg-blue-600 hover:bg-blue-700">
                  Start Quiz
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {quizState === 'taking' && (
        <>
          {/* Quiz Progress */}
          <Card className="mb-6">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <Badge variant="outline">
                    Question {currentQuestionIndex + 1} of {quiz.questions.length}
                  </Badge>
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="w-4 h-4 mr-1" />
                    Time Left: <span className="font-mono ml-1 font-bold text-orange-600">
                      {formatTime(timeLeft)}
                    </span>
                  </div>
                </div>
              </div>
              <Progress value={getProgressPercentage()} className="h-2" />
            </CardContent>
          </Card>

          {/* Current Question */}
          {quiz.questions[currentQuestionIndex] && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg">
                  Question {currentQuestionIndex + 1}
                  <Badge variant="outline" className="ml-2">
                    {quiz.questions[currentQuestionIndex].points} points
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="space-y-4">
                    <p className="text-lg text-gray-900">
                      {quiz.questions[currentQuestionIndex].question}
                    </p>
                    
                    {/* Question Media */}
                    {quiz.questions[currentQuestionIndex].questionImage && (
                      <div className="my-4">
                        <img 
                          src={quiz.questions[currentQuestionIndex].questionImage} 
                          alt="Question illustration" 
                          className="max-w-full h-64 object-cover rounded border shadow-sm"
                        />
                      </div>
                    )}
                    {quiz.questions[currentQuestionIndex].questionAudio && (
                      <div className="my-4">
                        <audio controls className="w-full max-w-md">
                          <source src={quiz.questions[currentQuestionIndex].questionAudio} type="audio/mpeg" />
                          Your browser does not support the audio element.
                        </audio>
                      </div>
                    )}
                  </div>

                  {quiz.questions[currentQuestionIndex].type === 'multiple-choice' && (
                    <div className="space-y-3">
                      {quiz.questions[currentQuestionIndex].options.map((option, index) => {
                        const optionText = typeof option === 'string' ? option : option.text || '';
                        const optionImage = typeof option === 'object' ? option.image : null;
                        const optionAudio = typeof option === 'object' ? option.audio : null;
                        
                        return (
                          <label 
                            key={index} 
                            className="flex items-start space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                          >
                            <input
                              type="radio"
                              name={`question-${quiz.questions[currentQuestionIndex].id}`}
                              value={index}
                              checked={answers[quiz.questions[currentQuestionIndex].id] === index}
                              onChange={(e) => handleAnswerChange(
                                quiz.questions[currentQuestionIndex].id, 
                                parseInt(e.target.value)
                              )}
                              className="text-blue-600 mt-1"
                            />
                            <div className="flex-1 space-y-2">
                              <span className="text-gray-900">{optionText}</span>
                              {optionImage && (
                                <div>
                                  <img 
                                    src={optionImage} 
                                    alt={`Option ${index + 1}`} 
                                    className="max-w-xs h-32 object-cover rounded border"
                                  />
                                </div>
                              )}
                              {optionAudio && (
                                <div>
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
                    </div>
                  )}

                  {quiz.questions[currentQuestionIndex].type === 'select-all-that-apply' && (
                    <div className="space-y-3">
                      <p className="text-sm text-blue-600 font-medium mb-3">Select all correct answers:</p>
                      {quiz.questions[currentQuestionIndex].options.map((option, index) => {
                        const optionText = typeof option === 'string' ? option : option.text || '';
                        const optionImage = typeof option === 'object' ? option.image : null;
                        const optionAudio = typeof option === 'object' ? option.audio : null;
                        
                        return (
                          <label 
                            key={index} 
                            className="flex items-start space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                          >
                            <input
                              type="checkbox"
                              checked={(answers[quiz.questions[currentQuestionIndex].id] || []).includes(index)}
                              onChange={(e) => {
                                const currentAnswers = answers[quiz.questions[currentQuestionIndex].id] || [];
                                const newAnswers = e.target.checked
                                  ? [...currentAnswers, index]
                                  : currentAnswers.filter(answerIndex => answerIndex !== index);
                                handleAnswerChange(quiz.questions[currentQuestionIndex].id, newAnswers);
                              }}
                              className="text-blue-600 mt-1"
                            />
                            <div className="flex-1 space-y-2">
                              <span className="text-gray-900">{optionText}</span>
                              {optionImage && (
                                <div>
                                  <img 
                                    src={optionImage} 
                                    alt={`Option ${index + 1}`} 
                                    className="max-w-xs h-32 object-cover rounded border"
                                  />
                                </div>
                              )}
                              {optionAudio && (
                                <div>
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
                    </div>
                  )}

                  {quiz.questions[currentQuestionIndex].type === 'true-false' && (
                    <div className="space-y-3">
                      <label className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input
                          type="radio"
                          name={`question-${quiz.questions[currentQuestionIndex].id}`}
                          value="true"
                          checked={answers[quiz.questions[currentQuestionIndex].id] === true}
                          onChange={() => handleAnswerChange(quiz.questions[currentQuestionIndex].id, true)}
                          className="text-blue-600"
                        />
                        <span>True</span>
                      </label>
                      <label className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input
                          type="radio"
                          name={`question-${quiz.questions[currentQuestionIndex].id}`}
                          value="false"
                          checked={answers[quiz.questions[currentQuestionIndex].id] === false}
                          onChange={() => handleAnswerChange(quiz.questions[currentQuestionIndex].id, false)}
                          className="text-blue-600"
                        />
                        <span>False</span>
                      </label>
                    </div>
                  )}

                  {quiz.questions[currentQuestionIndex].type === 'short-answer' && (
                    <div>
                      <Textarea
                        placeholder="Enter your answer here..."
                        rows={4}
                        value={answers[quiz.questions[currentQuestionIndex].id] || ''}
                        onChange={(e) => handleAnswerChange(
                          quiz.questions[currentQuestionIndex].id, 
                          e.target.value
                        )}
                        className="w-full"
                      />
                    </div>
                  )}

                  {quiz.questions[currentQuestionIndex].type === 'long-form-answer' && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-blue-600 font-medium">Provide a detailed answer:</p>
                        {quiz.questions[currentQuestionIndex].wordLimit && (
                          <span className="text-sm text-gray-500">
                            Word limit: {quiz.questions[currentQuestionIndex].wordLimit} words
                          </span>
                        )}
                      </div>
                      <Textarea
                        placeholder="Enter your detailed answer here..."
                        rows={8}
                        value={answers[quiz.questions[currentQuestionIndex].id] || ''}
                        onChange={(e) => handleAnswerChange(
                          quiz.questions[currentQuestionIndex].id, 
                          e.target.value
                        )}
                        className="w-full"
                      />
                      {quiz.questions[currentQuestionIndex].wordLimit && (
                        <p className="text-xs text-gray-500">
                          Current word count: {(answers[quiz.questions[currentQuestionIndex].id] || '').split(/\s+/).filter(word => word.length > 0).length}
                        </p>
                      )}
                    </div>
                  )}

                  {quiz.questions[currentQuestionIndex].type === 'chronological-order' && (
                    <div className="space-y-4">
                      <p className="text-sm text-blue-600 font-medium mb-3">
                        Drag and drop the items to arrange them in chronological order:
                      </p>
                      <div className="space-y-3">
                        {(quiz.questions[currentQuestionIndex].items || []).map((item, index) => {
                          const itemText = typeof item === 'string' ? item : item.text || '';
                          const itemImage = typeof item === 'object' ? item.image : null;
                          const itemAudio = typeof item === 'object' ? item.audio : null;
                          
                          return (
                            <div
                              key={index}
                              className="p-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 cursor-move hover:bg-gray-100 transition-colors"
                              draggable
                              onDragStart={(e) => {
                                e.dataTransfer.setData('text/plain', index.toString());
                              }}
                              onDragOver={(e) => {
                                e.preventDefault();
                              }}
                              onDrop={(e) => {
                                e.preventDefault();
                                const draggedIndex = parseInt(e.dataTransfer.getData('text/plain'));
                                const targetIndex = index;
                                
                                if (draggedIndex !== targetIndex) {
                                  const currentOrder = answers[quiz.questions[currentQuestionIndex].id] || quiz.questions[currentQuestionIndex].items.map((_, i) => i);
                                  const newOrder = [...currentOrder];
                                  const [draggedItem] = newOrder.splice(draggedIndex, 1);
                                  newOrder.splice(targetIndex, 0, draggedItem);
                                  handleAnswerChange(quiz.questions[currentQuestionIndex].id, newOrder);
                                }
                              }}
                            >
                              <div className="flex items-start space-x-3">
                                <span className="text-sm font-medium text-gray-600 mt-1">#{index + 1}</span>
                                <div className="flex-1 space-y-2">
                                  <span className="text-gray-900">{itemText}</span>
                                  {itemImage && (
                                    <div>
                                      <img 
                                        src={itemImage} 
                                        alt={`Item ${index + 1}`} 
                                        className="max-w-xs h-24 object-cover rounded border"
                                      />
                                    </div>
                                  )}
                                  {itemAudio && (
                                    <div>
                                      <audio controls className="w-full max-w-xs">
                                        <source src={itemAudio} type="audio/mpeg" />
                                        Your browser does not support the audio element.
                                      </audio>
                                    </div>
                                  )}
                                </div>
                                <div className="ml-auto text-gray-400 mt-1">
                                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M10 6L6 10l4 4 4-4-4-4z"/>
                                  </svg>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      <p className="text-xs text-gray-500">
                        Click and drag the items to reorder them. The correct chronological order is from earliest to latest.
                      </p>
                    </div>
                  )}

                  {(quiz.questions[currentQuestionIndex].type === 'record-screen' || 
                    quiz.questions[currentQuestionIndex].type === 'record_screen') && (
                    <div className="space-y-4">
                      <ScreenRecorder
                        questionId={`quiz_${courseId}_${lessonId}_q${currentQuestionIndex}`}
                        onRecordingComplete={(blob, duration) => {
                          handleAnswerChange(quiz.questions[currentQuestionIndex].id, {
                            hasRecording: !!blob,
                            duration: duration,
                            size: blob ? blob.size : 0,
                            timestamp: new Date().toISOString(),
                            blob: blob // Store the actual blob for grading
                          });
                        }}
                        maxDuration={quiz.questions[currentQuestionIndex].maxRecordingTime ? 
                          quiz.questions[currentQuestionIndex].maxRecordingTime * 60 : 1800}
                        disabled={quizState === 'submitted'}
                      />
                      
                      {quiz.questions[currentQuestionIndex].instructions && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <h5 className="font-medium text-blue-900 mb-2">📋 Instructions:</h5>
                          <p className="text-sm text-blue-800 whitespace-pre-wrap">
                            {quiz.questions[currentQuestionIndex].instructions}
                          </p>
                          
                          {quiz.questions[currentQuestionIndex].requiredTools && (
                            <div className="mt-3">
                              <h6 className="font-medium text-blue-900 text-sm">Required Tools:</h6>
                              <p className="text-sm text-blue-700">
                                {quiz.questions[currentQuestionIndex].requiredTools}
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={prevQuestion}
              disabled={currentQuestionIndex === 0}
            >
              Previous
            </Button>

            <div className="flex space-x-2">
              {currentQuestionIndex < quiz.questions.length - 1 ? (
                <Button onClick={nextQuestion}>
                  Next
                </Button>
              ) : (
                <Button 
                  onClick={handleSubmitQuiz}
                  className="bg-green-600 hover:bg-green-700"
                >
                  Submit Quiz
                </Button>
              )}
            </div>
          </div>
        </>
      )}

      {quizState === 'submitted' && showResults && quizResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
              Quiz Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Score Summary */}
              <div className="text-center py-6 bg-gray-50 rounded-lg">
                <div className="text-4xl font-bold mb-2 text-gray-900">
                  {quizResults.score}%
                </div>
                <div className="text-lg mb-2">
                  {quizResults.passed ? (
                    <span className="text-green-600 font-medium">✅ Passed</span>
                  ) : (
                    <span className="text-red-600 font-medium">❌ Not Passed</span>
                  )}
                </div>
                <div className="text-sm text-gray-600">
                  {quizResults.earnedPoints} out of {quizResults.totalPoints} points
                </div>
                <div className="text-sm text-gray-600">
                  Time taken: {formatTime(quizResults.timeSpent)}
                </div>
              </div>

              {/* Question Breakdown */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Question Breakdown</h3>
                {quiz.questions.map((question, index) => {
                  const answer = quizResults.answers.find(a => a.questionId === question.id);
                  return (
                    <Card key={question.id} className="border-l-4 border-l-gray-200">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <p className="font-medium">Question {index + 1}</p>
                          <Badge variant={answer?.correct ? "default" : "destructive"}>
                            {answer?.correct ? `+${answer.points}` : '0'} points
                          </Badge>
                        </div>
                        <p className="text-gray-700 mb-3">{question.question}</p>
                        
                        <div className="space-y-2 text-sm">
                          <div>
                            <span className="text-gray-600">Your answer: </span>
                            <span className={answer?.correct ? 'text-green-600' : 'text-red-600'}>
                              {question.type === 'multiple-choice' 
                                ? (typeof question.options[answer?.answer] === 'string' 
                                    ? question.options[answer?.answer] 
                                    : question.options[answer?.answer]?.text || 'No answer')
                                : question.type === 'select-all-that-apply'
                                ? (answer?.answer || []).map(index => 
                                    typeof question.options[index] === 'string' 
                                      ? question.options[index] 
                                      : question.options[index]?.text || ''
                                  ).join(', ') || 'No answer'
                                : question.type === 'true-false'
                                ? (answer?.answer?.toString() || 'No answer')
                                : question.type === 'chronological-order'
                                ? (answer?.answer || []).map(index => 
                                    typeof question.items[index] === 'string' 
                                      ? question.items[index] 
                                      : question.items[index]?.text || ''
                                  ).join(' → ') || 'No answer'
                                : (question.type === 'record-screen' || question.type === 'record_screen')
                                ? (answer?.answer?.hasRecording 
                                    ? `Screen recording completed (Duration: ${Math.floor(answer.answer.duration / 60)}:${(answer.answer.duration % 60).toString().padStart(2, '0')}, Size: ${(answer.answer.size / (1024 * 1024)).toFixed(2)}MB)`
                                    : 'No recording submitted')
                                : answer?.answer || 'No answer'}
                            </span>
                          </div>
                          
                          {!answer?.correct && question.type !== 'long-form-answer' && (
                            <div>
                              <span className="text-gray-600">Correct answer: </span>
                              <span className="text-green-600">
                                {question.type === 'multiple-choice'
                                  ? (typeof question.options[question.correctAnswer] === 'string' 
                                      ? question.options[question.correctAnswer] 
                                      : question.options[question.correctAnswer]?.text || '')
                                  : question.type === 'select-all-that-apply'
                                  ? (question.correctAnswers || []).map(index => 
                                      typeof question.options[index] === 'string' 
                                        ? question.options[index] 
                                        : question.options[index]?.text || ''
                                    ).join(', ')
                                  : question.type === 'true-false'
                                  ? question.correctAnswer.toString()
                                  : question.type === 'chronological-order'
                                  ? (question.correctOrder || []).map(index => 
                                      typeof question.items[index] === 'string' 
                                        ? question.items[index] 
                                        : question.items[index]?.text || ''
                                    ).join(' → ')
                                  : question.correctAnswer}
                              </span>
                            </div>
                          )}

                          {question.type === 'long-form-answer' && (
                            <div className="mt-2 p-2 bg-yellow-50 rounded text-yellow-800">
                              <span className="font-medium">Note: </span>
                              This answer requires manual grading by your instructor. Your score may be updated after review.
                            </div>
                          )}

                          {(question.type === 'record-screen' || question.type === 'record_screen') && (
                            <div className="mt-2 p-2 bg-blue-50 rounded text-blue-800">
                              <span className="font-medium">Screen Recording: </span>
                              This recording will be reviewed by your instructor for grading. Your score may be updated after manual review.
                            </div>
                          )}

                          {question.explanation && (
                            <div className="mt-2 p-2 bg-blue-50 rounded text-blue-800">
                              <span className="font-medium">Explanation: </span>
                              {question.explanation}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              <div className="flex items-center justify-center pt-6">
                <Button onClick={() => navigate(`/courses/${courseId}`)}>
                  Back to Course
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {quizState === 'submitted' && !showResults && (
        <Card>
          <CardContent className="text-center py-12">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Quiz Submitted!</h2>
            <p className="text-gray-600 mb-6">
              Your quiz has been submitted successfully. Results will be available once graded.
            </p>
            <Button onClick={() => navigate(`/courses/${courseId}`)}>
              Back to Course
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default QuizTaking;
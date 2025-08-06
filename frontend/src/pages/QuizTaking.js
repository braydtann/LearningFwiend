import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Textarea } from '../components/ui/textarea';
import { mockCourses, getQuizAttempts, getQuizResults } from '../data/mockData';
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
  const { user } = useAuth();
  const { toast } = useToast();

  // Find course and lesson
  const course = mockCourses.find(c => c.id === courseId);
  const lesson = course?.modules
    ?.find(m => m.lessons?.some(l => l.id === lessonId))
    ?.lessons?.find(l => l.id === lessonId);
  const quiz = lesson?.quiz;

  // Quiz state
  const [quizState, setQuizState] = useState('loading'); // loading, ready, taking, submitted, error
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [quizResults, setQuizResults] = useState(null);

  // Get existing attempts and results
  const attempts = getQuizAttempts(user?.id, courseId, lessonId, quiz?.id);
  const existingResults = getQuizResults(user?.id, courseId, lessonId, quiz?.id);
  const canTakeQuiz = !existingResults || existingResults.totalAttempts < (quiz?.maxAttempts || 3);

  useEffect(() => {
    if (!course || !lesson || !quiz) {
      setQuizState('error');
      return;
    }

    // Check if user can take the quiz
    if (!canTakeQuiz) {
      setQuizState('max-attempts-reached');
      return;
    }

    setQuizState('ready');
  }, [course, lesson, quiz, canTakeQuiz]);

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
      } else if (question.type === 'true-false') {
        correct = userAnswer === question.correctAnswer;
      } else if (question.type === 'short-answer') {
        // For demo purposes, mark as correct if answer contains key terms
        // In real app, this might need manual grading
        correct = userAnswer && 
          userAnswer.toLowerCase().includes(question.correctAnswer.toLowerCase().split(' ')[0]);
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
        <Button onClick={() => navigate(`/course/${courseId}`)}>
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
          <Button onClick={() => navigate(`/course/${courseId}`)}>
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
          onClick={() => navigate(`/course/${courseId}`)}
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
                  <p className="text-lg text-gray-900">
                    {quiz.questions[currentQuestionIndex].question}
                  </p>

                  {quiz.questions[currentQuestionIndex].type === 'multiple-choice' && (
                    <div className="space-y-3">
                      {quiz.questions[currentQuestionIndex].options.map((option, index) => (
                        <label 
                          key={index} 
                          className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
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
                            className="text-blue-600"
                          />
                          <span>{option}</span>
                        </label>
                      ))}
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
                                ? question.options[answer?.answer] || 'No answer'
                                : question.type === 'true-false'
                                ? (answer?.answer?.toString() || 'No answer')
                                : answer?.answer || 'No answer'}
                            </span>
                          </div>
                          
                          {!answer?.correct && (
                            <div>
                              <span className="text-gray-600">Correct answer: </span>
                              <span className="text-green-600">
                                {question.type === 'multiple-choice'
                                  ? question.options[question.correctAnswer]
                                  : question.type === 'true-false'
                                  ? question.correctAnswer.toString()
                                  : question.correctAnswer}
                              </span>
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
                <Button onClick={() => navigate(`/course/${courseId}`)}>
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
            <Button onClick={() => navigate(`/course/${courseId}`)}>
              Back to Course
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default QuizTaking;
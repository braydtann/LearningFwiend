import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Textarea } from '../components/ui/textarea';
import ScreenRecorder from '../components/ScreenRecorder';
import { mockCourses, mockPrograms } from '../data/mockData';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Timer,
  Award,
  BookOpen,
  Trophy
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const FinalTest = () => {
  const { courseId, programId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  // Determine if this is a program or course final test
  const isProgram = programId !== undefined;
  
  // Find course and final test
  const course = !isProgram ? mockCourses.find(c => c.id === courseId) : null;
  const program = isProgram ? mockPrograms.find(p => p.id === programId) : null;
  const finalTest = isProgram ? program?.finalTest : course?.finalTest;

  // Quiz state
  const [testState, setTestState] = useState('loading'); // loading, ready, taking, submitted, error
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [testResults, setTestResults] = useState(null);

  useEffect(() => {
    if ((!course && !isProgram) || (!program && isProgram) || !finalTest) {
      setTestState('error');
      return;
    }

    setTestState('ready');
  }, [course, program, finalTest, isProgram]);

  // Timer effect
  useEffect(() => {
    if (testState === 'taking' && timeLeft > 0) {
      const timer = setTimeout(() => {
        setTimeLeft(timeLeft - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (testState === 'taking' && timeLeft === 0) {
      handleSubmitTest();
    }
  }, [testState, timeLeft]);

  const startTest = () => {
    setTestState('taking');
    setStartTime(Date.now());
    setTimeLeft((finalTest.timeLimit || 60) * 60); // Convert minutes to seconds
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
    if (currentQuestionIndex < finalTest.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitTest = () => {
    const endTime = Date.now();
    const timeSpent = Math.floor((endTime - startTime) / 1000);
    
    // Calculate score
    let totalPoints = 0;
    let earnedPoints = 0;
    
    const gradedAnswers = finalTest.questions.map(question => {
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
      } else if (question.type === 'chronological-order') {
        const correctOrder = question.correctOrder || [];
        const userOrder = userAnswer || [];
        correct = correctOrder.length === userOrder.length && 
                 correctOrder.every((item, index) => item === userOrder[index]);
      } else if (question.type === 'short-answer') {
        correct = userAnswer && 
          userAnswer.toLowerCase().includes(question.correctAnswer?.toLowerCase().split(' ')[0] || '');
      } else if (question.type === 'long-form-answer') {
        // Long form answers require manual grading
        correct = userAnswer && userAnswer.trim().length > 100; // Basic completion check
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
    const passed = score >= (finalTest.passingScore || 70);

    const results = {
      score,
      totalPoints,
      earnedPoints,
      passed,
      timeSpent,
      answers: gradedAnswers,
      completedAt: new Date().toISOString(),
      isFinalTest: true
    };

    setTestResults(results);
    setTestState('submitted');
    
    if (finalTest.showResults) {
      setShowResults(true);
    }

    toast({
      title: passed ? "Final Test Completed!" : "Final Test Submitted",
      description: passed 
        ? `Congratulations! You scored ${score}% and passed the final assessment. Your certificate is now available!`
        : `You scored ${score}%. The passing score is ${finalTest.passingScore || 70}%. You can retake the test if attempts are available.`,
      variant: passed ? "default" : "destructive"
    });
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    return Math.round(((currentQuestionIndex + 1) / finalTest.questions.length) * 100);
  };

  if (testState === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading final test...</p>
        </div>
      </div>
    );
  }

  if (testState === 'error' || !finalTest) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Final test not available</h1>
        <p className="text-gray-600 mb-6">The final test for this course is not available or you don't have access to it.</p>
        <Button onClick={() => navigate(`/course/${courseId}`)}>
          Back to Course
        </Button>
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
          disabled={testState === 'taking'}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Course
        </Button>
        <div className="h-6 border-l border-gray-300"></div>
        <div>
          <h1 className="text-2xl font-bold text-purple-900 flex items-center">
            <Trophy className="w-6 h-6 mr-2" />
            {finalTest.title}
          </h1>
          <p className="text-gray-600">
            {isProgram ? program?.name : course?.title}
          </p>
        </div>
      </div>

      {testState === 'ready' && (
        <Card className="mb-6 border-purple-200">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50">
            <CardTitle className="flex items-center text-purple-800">
              <Award className="w-5 h-5 mr-2" />
              Ready for Your Final Assessment?
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              {finalTest.description && (
                <p className="text-gray-600">{finalTest.description}</p>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 py-4">
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="flex items-center justify-center mb-2">
                    <Timer className="w-5 h-5 text-purple-600 mr-1" />
                  </div>
                  <p className="text-sm text-purple-600">Time Limit</p>
                  <p className="font-bold text-purple-800">{finalTest.timeLimit} minutes</p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-center mb-2">
                    <BookOpen className="w-5 h-5 text-blue-600 mr-1" />
                  </div>
                  <p className="text-sm text-blue-600">Questions</p>
                  <p className="font-bold text-blue-800">{finalTest.questions.length}</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center justify-center mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-1" />
                  </div>
                  <p className="text-sm text-green-600">Passing Score</p>
                  <p className="font-bold text-green-800">{finalTest.passingScore}%</p>
                </div>
              </div>

              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-4 rounded-lg border border-yellow-200">
                <h3 className="font-medium text-yellow-800 mb-2">Important Information:</h3>
                <ul className="text-sm text-yellow-700 space-y-1">
                  <li>• This is a comprehensive test covering the entire {isProgram ? 'program' : 'course'}</li>
                  <li>• You have {finalTest.maxAttempts} attempt(s) to pass</li>
                  <li>• Your answers will be saved automatically</li>
                  <li>• Passing this test will unlock your {isProgram ? 'program' : 'course'} certificate</li>
                </ul>
              </div>

              <div className="flex items-center justify-center pt-4">
                <Button onClick={startTest} size="lg" className="bg-purple-600 hover:bg-purple-700">
                  <Trophy className="w-4 h-4 mr-2" />
                  Start Final Test
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {testState === 'taking' && (
        <>
          {/* Test Progress */}
          <Card className="mb-6 border-purple-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <Badge variant="outline" className="border-purple-300 text-purple-700">
                    Question {currentQuestionIndex + 1} of {finalTest.questions.length}
                  </Badge>
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="w-4 h-4 mr-1" />
                    Time Left: <span className="font-mono ml-1 font-bold text-purple-600">
                      {formatTime(timeLeft)}
                    </span>
                  </div>
                </div>
              </div>
              <Progress value={getProgressPercentage()} className="h-2" />
            </CardContent>
          </Card>

          {/* Current Question */}
          {finalTest.questions[currentQuestionIndex] && (
            <Card className="mb-6 border-purple-200">
              <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50">
                <CardTitle className="text-lg flex items-center justify-between">
                  <span className="text-purple-800">
                    Question {currentQuestionIndex + 1}
                  </span>
                  <Badge variant="outline" className="border-purple-300 text-purple-700">
                    {finalTest.questions[currentQuestionIndex].points} points
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-6">
                  <p className="text-lg text-gray-900 leading-relaxed">
                    {finalTest.questions[currentQuestionIndex].question}
                  </p>

                  {/* Question Types - Same as regular quiz but with purple theming */}
                  {finalTest.questions[currentQuestionIndex].type === 'multiple-choice' && (
                    <div className="space-y-3">
                      {finalTest.questions[currentQuestionIndex].options.map((option, index) => (
                        <label 
                          key={index} 
                          className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-purple-50 transition-colors"
                        >
                          <input
                            type="radio"
                            name={`question-${finalTest.questions[currentQuestionIndex].id}`}
                            value={index}
                            checked={answers[finalTest.questions[currentQuestionIndex].id] === index}
                            onChange={(e) => handleAnswerChange(
                              finalTest.questions[currentQuestionIndex].id, 
                              parseInt(e.target.value)
                            )}
                            className="text-purple-600"
                          />
                          <span>{option}</span>
                        </label>
                      ))}
                    </div>
                  )}

                  {finalTest.questions[currentQuestionIndex].type === 'select-all-that-apply' && (
                    <div className="space-y-3">
                      <p className="text-sm text-purple-600 font-medium mb-3">Select all correct answers:</p>
                      {finalTest.questions[currentQuestionIndex].options.map((option, index) => (
                        <label 
                          key={index} 
                          className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-purple-50 transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={(answers[finalTest.questions[currentQuestionIndex].id] || []).includes(index)}
                            onChange={(e) => {
                              const currentAnswers = answers[finalTest.questions[currentQuestionIndex].id] || [];
                              const newAnswers = e.target.checked
                                ? [...currentAnswers, index]
                                : currentAnswers.filter(answerIndex => answerIndex !== index);
                              handleAnswerChange(finalTest.questions[currentQuestionIndex].id, newAnswers);
                            }}
                            className="text-purple-600"
                          />
                          <span>{option}</span>
                        </label>
                      ))}
                    </div>
                  )}

                  {finalTest.questions[currentQuestionIndex].type === 'long-form-answer' && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-purple-600 font-medium">Provide a comprehensive answer:</p>
                        {finalTest.questions[currentQuestionIndex].wordLimit && (
                          <span className="text-sm text-gray-500">
                            Word limit: {finalTest.questions[currentQuestionIndex].wordLimit} words
                          </span>
                        )}
                      </div>
                      <Textarea
                        placeholder="Enter your detailed answer here..."
                        rows={10}
                        value={answers[finalTest.questions[currentQuestionIndex].id] || ''}
                        onChange={(e) => handleAnswerChange(
                          finalTest.questions[currentQuestionIndex].id, 
                          e.target.value
                        )}
                        className="w-full"
                      />
                      {finalTest.questions[currentQuestionIndex].wordLimit && (
                        <p className="text-xs text-gray-500">
                          Current word count: {(answers[finalTest.questions[currentQuestionIndex].id] || '').split(/\s+/).filter(word => word.length > 0).length}
                        </p>
                      )}
                    </div>
                  )}

                  {finalTest.questions[currentQuestionIndex].type === 'chronological-order' && (
                    <div className="space-y-4">
                      <p className="text-sm text-purple-600 font-medium mb-3">
                        Arrange these items in chronological order:
                      </p>
                      <div className="space-y-2">
                        {(finalTest.questions[currentQuestionIndex].items || []).map((item, index) => (
                          <div
                            key={index}
                            className="p-4 border-2 border-dashed border-purple-200 rounded-lg bg-purple-50 cursor-move hover:bg-purple-100 transition-colors"
                          >
                            <div className="flex items-center space-x-3">
                              <span className="text-sm font-medium text-purple-600">#{index + 1}</span>
                              <span>{item}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {(finalTest.questions[currentQuestionIndex].type === 'record-screen' || 
                    finalTest.questions[currentQuestionIndex].type === 'record_screen') && (
                    <div className="space-y-4">
                      <ScreenRecorder
                        questionId={`finaltest_${isProgram ? programId : courseId}_q${currentQuestionIndex}`}
                        onRecordingComplete={(blob, duration) => {
                          handleAnswerChange(finalTest.questions[currentQuestionIndex].id, {
                            hasRecording: !!blob,
                            duration: duration,
                            size: blob ? blob.size : 0,
                            timestamp: new Date().toISOString(),
                            blob: blob
                          });
                        }}
                        maxDuration={finalTest.questions[currentQuestionIndex].maxRecordingTime ? 
                          finalTest.questions[currentQuestionIndex].maxRecordingTime * 60 : 1800}
                        disabled={testState === 'submitted'}
                      />
                      
                      {finalTest.questions[currentQuestionIndex].instructions && (
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                          <h5 className="font-medium text-purple-900 mb-2">📋 Instructions:</h5>
                          <p className="text-sm text-purple-800 whitespace-pre-wrap">
                            {finalTest.questions[currentQuestionIndex].instructions}
                          </p>
                          
                          {finalTest.questions[currentQuestionIndex].requiredTools && (
                            <div className="mt-3">
                              <h6 className="font-medium text-purple-900 text-sm">Required Tools:</h6>
                              <p className="text-sm text-purple-700">
                                {finalTest.questions[currentQuestionIndex].requiredTools}
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
              className="border-purple-300 text-purple-700 hover:bg-purple-50"
            >
              Previous
            </Button>

            <div className="flex space-x-2">
              {currentQuestionIndex < finalTest.questions.length - 1 ? (
                <Button 
                  onClick={nextQuestion}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  Next
                </Button>
              ) : (
                <Button 
                  onClick={handleSubmitTest}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Trophy className="w-4 h-4 mr-2" />
                  Submit Final Test
                </Button>
              )}
            </div>
          </div>
        </>
      )}

      {testState === 'submitted' && testResults && (
        <Card className="border-purple-200">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50">
            <CardTitle className="flex items-center text-purple-800">
              <Trophy className="w-5 h-5 mr-2" />
              Final Test Results
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="text-center py-8">
              <div className="text-5xl font-bold mb-4 text-purple-900">
                {testResults.score}%
              </div>
              <div className="text-2xl mb-4">
                {testResults.passed ? (
                  <div className="text-green-600 font-bold flex items-center justify-center">
                    <Trophy className="w-8 h-8 mr-2" />
                    Congratulations! You Passed!
                  </div>
                ) : (
                  <span className="text-red-600 font-bold">Not Passed</span>
                )}
              </div>
              <div className="text-lg text-gray-600 mb-6">
                You scored {testResults.earnedPoints} out of {testResults.totalPoints} points
              </div>
              
              {testResults.passed && (
                <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg border border-green-200 mb-6">
                  <h3 className="font-bold text-green-800 mb-2">🎉 Course Completed!</h3>
                  <p className="text-green-700">
                    You have successfully completed {course.title}. Your certificate has been generated and is now available in your certificates section.
                  </p>
                  <Button 
                    className="mt-4 bg-green-600 hover:bg-green-700"
                    onClick={() => navigate('/certificates')}
                  >
                    View Your Certificate
                  </Button>
                </div>
              )}

              <div className="flex items-center justify-center space-x-4 pt-6">
                <Button 
                  variant="outline"
                  onClick={() => navigate(`/course/${courseId}`)}
                  className="border-purple-300 text-purple-700 hover:bg-purple-50"
                >
                  Back to Course
                </Button>
                <Button 
                  onClick={() => navigate('/dashboard')}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  Go to Dashboard
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FinalTest;
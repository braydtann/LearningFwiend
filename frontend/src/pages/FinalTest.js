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

// Utility function to convert Google Drive URLs to direct image URLs
const convertGoogleDriveUrl = (url) => {
  if (!url || typeof url !== 'string') return url;
  
  // Check if it's a Google Drive URL
  const driveRegex = /https:\/\/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)\/view/;
  const match = url.match(driveRegex);
  
  if (match) {
    const fileId = match[1];
    return `https://drive.googleusercontent.com/u/0/uc?id=${fileId}&export=view`;
  }
  
  // Also handle alternative Google Drive sharing URLs
  const altDriveRegex = /https:\/\/drive\.google\.com\/open\?id=([a-zA-Z0-9_-]+)/;
  const altMatch = url.match(altDriveRegex);
  
  if (altMatch) {
    const fileId = altMatch[1];
    return `https://drive.googleusercontent.com/u/0/uc?id=${fileId}&export=view`;
  }
  
  // Return original URL if not a Google Drive URL
  return url;
};

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
  const [availableTests, setAvailableTests] = useState([]);

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
          
          console.log('Final tests result:', testsResult);
          console.log('Program ID:', programId);
          
          if (testsResult.success && testsResult.tests.length > 0) {
            // Get the first published final test for this program
            const testId = testsResult.tests[0].id;
            console.log('Using final test ID:', testId);
            
            const testDetailResult = await getFinalTestById(testId);
            console.log('Final test details result:', testDetailResult);
            
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
              console.error('Failed to get final test details:', testDetailResult);
              setError(`Final test not found for this program. Error: ${testDetailResult.error}`);
            }
          } else {
            console.error('No final tests found for program:', testsResult);
            // Try to get all final tests to see if any are available
            const allTestsResult = await getAllFinalTests({ published_only: true });
            console.log('All available final tests:', allTestsResult);
            
            if (allTestsResult.success && allTestsResult.tests.length > 0) {
              // There are final tests available, but not for this specific program
              // Check if the program exists first
              const programCheck = await getProgramById(programId);
              
              if (!programCheck.success) {
                // Program doesn't exist - offer to show available tests
                setError(`The program ID in the URL doesn't exist. However, you have access to ${allTestsResult.tests.length} final test(s). Would you like to see available final exams?`);
                
                // Set available tests for user to choose from
                setAvailableTests(allTestsResult.tests);
              } else {
                // Program exists but has no final tests - offer available tests as alternative
                setError(`No final test has been created for "${programCheck.program?.title || 'this program'}" yet. However, you have access to ${allTestsResult.tests.length} other final test(s). Would you like to see available final exams?`);
                
                // Set available tests for user to choose from  
                setAvailableTests(allTestsResult.tests);
              }
            } else {
              setError(`No final tests are available to you at this time. Please contact your instructor.`);
            }
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

  const renderQuestion = (question) => {
    const currentAnswer = answers[question.id];

    // Normalize question type to handle both snake_case and kebab-case
    const normalizedType = question.type?.replace(/_/g, '-');

    switch (normalizedType) {
      case 'multiple-choice':
        return (
          <div className="space-y-4">
            <RadioGroup
              value={currentAnswer || ''}
              onValueChange={(value) => handleAnswerChange(question.id, value)}
            >
              {question.options?.map((option, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <RadioGroupItem value={option} id={`option-${index}`} />
                  <Label htmlFor={`option-${index}`} className="flex-grow cursor-pointer">
                    {option}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
        );

      case 'select-all-that-apply':
        return (
          <div className="space-y-4">
            {question.options?.map((option, index) => {
              const selectedOptions = currentAnswer || [];
              const isChecked = selectedOptions.includes(option);
              
              return (
                <div key={index} className="flex items-center space-x-2">
                  <Checkbox
                    id={`option-${index}`}
                    checked={isChecked}
                    onCheckedChange={(checked) => {
                      let newSelection = [...selectedOptions];
                      if (checked && !isChecked) {
                        newSelection.push(option);
                      } else if (!checked && isChecked) {
                        newSelection = newSelection.filter(item => item !== option);
                      }
                      handleAnswerChange(question.id, newSelection);
                    }}
                  />
                  <Label htmlFor={`option-${index}`} className="flex-grow cursor-pointer">
                    {option}
                  </Label>
                </div>
              );
            })}
          </div>
        );

      case 'true-false':
        return (
          <div className="space-y-4">
            <RadioGroup
              value={currentAnswer || ''}
              onValueChange={(value) => handleAnswerChange(question.id, value)}
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="true" id="true" />
                <Label htmlFor="true" className="cursor-pointer">True</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="false" id="false" />
                <Label htmlFor="false" className="cursor-pointer">False</Label>
              </div>
            </RadioGroup>
          </div>
        );

      case 'short-answer':
        return (
          <div className="space-y-4">
            <Textarea
              placeholder="Enter your answer here..."
              value={currentAnswer || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              rows={3}
            />
          </div>
        );

      case 'long-form':
      case 'essay':
        return (
          <div className="space-y-4">
            <Textarea
              placeholder="Enter your detailed answer here..."
              value={currentAnswer || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              rows={6}
            />
          </div>
        );

      case 'chronological-order':
        const items = question.items || [];
        const currentOrder = Array.isArray(currentAnswer) ? currentAnswer : [];
        
        return (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
              <p className="text-blue-800 text-sm">
                📋 <strong>Instructions:</strong> Click items in the correct chronological order to arrange them.
              </p>
            </div>
            
            {/* Display items for ordering */}
            <div className="space-y-2">
              {items.map((item, index) => {
                const itemText = typeof item === 'string' ? item : (item?.text || `Item ${index + 1}`);
                const itemPosition = currentOrder.indexOf(index);
                const isOrdered = itemPosition !== -1;
                
                return (
                  <div
                    key={index}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      isOrdered 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                    onClick={() => {
                      if (isOrdered) {
                        // Remove from order
                        const newOrder = currentOrder.filter(idx => idx !== index);
                        handleAnswerChange(question.id, newOrder);
                      } else {
                        // Add to end of order
                        const newOrder = [...currentOrder, index];
                        handleAnswerChange(question.id, newOrder);
                      }
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex-1">{itemText}</span>
                      {isOrdered && (
                        <Badge variant="default" className="ml-2">
                          {itemPosition + 1}
                        </Badge>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Show current order summary */}
            {currentOrder.length > 0 && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-blue-800 text-sm mb-2">
                  <strong>Current Order:</strong>
                </p>
                <div className="space-y-1">
                  {currentOrder.map((itemIndex, position) => (
                    <div key={position} className="flex items-center text-sm">
                      <span className="font-medium mr-2">{position + 1}.</span>
                      <span>{typeof items[itemIndex] === 'string' ? items[itemIndex] : items[itemIndex]?.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      default:
        return (
          <div className="p-4 border border-yellow-200 bg-yellow-50 rounded">
            <p className="text-yellow-800">Unsupported question type: {question.type} (normalized: {normalizedType})</p>
            <p className="text-yellow-600 text-sm mt-1">
              Available types: multiple-choice, select-all-that-apply, true-false, short-answer, long-form, chronological-order
            </p>
          </div>
        );
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
            
            {/* Show available tests if program doesn't exist but tests are available */}
            {availableTests.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-4">Available Final Exams:</h3>
                <div className="space-y-2">
                  {availableTests.map((test) => (
                    <Card key={test.id} className="p-4">
                      <div className="flex justify-between items-center">
                        <div className="text-left">
                          <h4 className="font-medium">{test.title}</h4>
                          <p className="text-sm text-gray-600">{test.description}</p>
                        </div>
                        <Button
                          onClick={() => {
                            // Navigate to the correct final test URL
                            navigate(`/final-test/program/${test.programId || 'unknown'}`);
                          }}
                        >
                          Take Exam
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
            
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
    const passed = attemptResult && attemptResult.score >= (finalTest?.passingScore || 70);
    
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="text-center py-12">
            <Trophy className={`h-20 w-20 ${passed ? 'text-yellow-500' : 'text-gray-400'} mx-auto mb-6`} />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              {passed ? 'Congratulations! 🎉' : 'Exam Completed'}
            </h1>
            <p className="text-xl text-gray-600 mb-6">
              You have completed the final exam for "{examTitle}"
            </p>
            {attemptResult && (
              <div className="mb-6">
                <p className="text-2xl font-bold mb-2">
                  Score: {attemptResult.score}%
                </p>
                <p className="text-gray-600">
                  {passed ? 'You have passed the final exam!' : `You need ${finalTest?.passingScore || 70}% or higher to pass.`}
                </p>
              </div>
            )}
            <div className="flex gap-4 justify-center">
              {passed && (
                <Button onClick={() => navigate('/certificates')}>
                  <Award className="w-4 h-4 mr-2" />
                  View Certificate
                </Button>
              )}
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

  if (testStarted && finalTest) {
    const currentQuestion = finalTest.questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / finalTest.questions.length) * 100;
    const answeredCount = Object.keys(answers).length;

    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">{examType}</CardTitle>
                <p className="text-gray-600 mt-1">{examTitle}</p>
              </div>
              {timeRemaining !== null && (
                <Badge variant={timeRemaining < 300 ? "destructive" : "secondary"}>
                  <Timer className="w-4 h-4 mr-1" />
                  {formatTime(timeRemaining)} remaining
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Question {currentQuestionIndex + 1} of {finalTest.questions.length}</span>
                <span>{answeredCount} answered</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>

            {/* Current Question */}
            <Card className="border-l-4 border-l-blue-500">
              <CardContent className="p-6">
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-4">
                    {currentQuestion.question}
                  </h3>
                  
                  {/* Question Image - Display if available */}
                  {currentQuestion?.questionImage && currentQuestion.questionImage.trim() !== '' && (
                    <div className="mb-4">
                      <img 
                        src={currentQuestion.questionImage} 
                        alt="Question illustration" 
                        className="max-w-full h-64 object-contain rounded border mx-auto block"
                        onError={(e) => {
                          console.warn('Failed to load question image:', currentQuestion.questionImage);
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}

                  {/* Question Audio - Display if available */}
                  {currentQuestion?.questionAudio && currentQuestion.questionAudio.trim() !== '' && (
                    <div className="mb-4">
                      <audio controls className="w-full max-w-md mx-auto">
                        <source src={currentQuestion.questionAudio} type="audio/mpeg" />
                        Your browser does not support the audio element.
                      </audio>
                    </div>
                  )}
                  
                  {renderQuestion(currentQuestion)}
                </div>
              </CardContent>
            </Card>

            {/* Navigation */}
            <div className="flex justify-between items-center">
              <Button
                variant="outline"
                onClick={previousQuestion}
                disabled={currentQuestionIndex === 0}
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>

              <div className="flex gap-2">
                {currentQuestionIndex === finalTest.questions.length - 1 ? (
                  <Button
                    onClick={handleSubmitExam}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Submit Exam
                  </Button>
                ) : (
                  <Button onClick={nextQuestion}>
                    Next
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                )}
              </div>
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
          {finalTest ? (
            <>
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
                      You must achieve a passing score of {finalTest.passingScore || 70}% or higher
                    </li>
                    {finalTest.timeLimit && (
                      <li className="flex items-start">
                        <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                        Time limit: {finalTest.timeLimit} minutes
                      </li>
                    )}
                    <li className="flex items-start">
                      <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                      Total questions: {finalTest.questions?.length || 0}
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                      Upon successful completion, you will receive a certificate
                    </li>
                  </ul>
                </CardContent>
              </Card>

              {/* Previous Attempts */}
              {previousAttempts.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Previous Attempts</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {previousAttempts.slice(0, 3).map((attempt, index) => (
                        <div key={attempt.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                          <div>
                            <span className="font-medium">Attempt {previousAttempts.length - index}</span>
                            <span className="text-sm text-gray-500 ml-2">
                              {new Date(attempt.createdAt).toLocaleDateString()}
                            </span>
                          </div>
                          <Badge variant={attempt.score >= (finalTest.passingScore || 70) ? "default" : "secondary"}>
                            {attempt.score}%
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card className="bg-yellow-50 border-yellow-200">
              <CardContent className="p-6 text-center">
                <AlertCircle className="h-12 w-12 text-yellow-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-yellow-900 mb-2">
                  Final Exam Not Available
                </h3>
                <p className="text-yellow-800">
                  No final exam has been created for this program yet. Please contact your instructor.
                </p>
              </CardContent>
            </Card>
          )}

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
            {finalTest && finalTest.questions?.length > 0 ? (
              <Button onClick={startFinalExam} size="lg" className="px-8">
                <Play className="w-5 h-5 mr-2" />
                Start Final Exam
              </Button>
            ) : (
              <Button disabled size="lg" className="px-8">
                <Play className="w-5 h-5 mr-2" />
                Final Exam Not Available
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
export default FinalTest;
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import FinalTestQuestionInterface from '../components/FinalTestQuestionInterface';
import QuizPreview from '../components/QuizPreview';
import { 
  Award, 
  Users, 
  BookOpen, 
  Plus, 
  Eye, 
  Edit, 
  Clock,
  BarChart,
  ArrowUp,
  ArrowDown,
  Trash2,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Trophy
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Programs = () => {
  const { user, isAdmin, isLearner, getAllPrograms, getAllCourses, createProgram, deleteProgram, checkProgramAccess, createFinalTest } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isQuizPreviewOpen, setIsQuizPreviewOpen] = useState(false);
  const [newProgram, setNewProgram] = useState({
    title: '',
    description: '',
    courseIds: [],
    courseOrder: [],
    nestedProgramIds: [], // For 1-level program nesting
    duration: '',
    finalTest: {
      title: '',
      description: '',
      timeLimit: 90,
      passingScore: 75,
      maxAttempts: 2,
      questions: []
    }
  });

  const [programs, setPrograms] = useState([]);
  const [programAccessStatus, setProgramAccessStatus] = useState({}); // Store access status for each program
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  // Initialize programs and courses on component mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Load programs
        const programsResult = await getAllPrograms();
        if (programsResult.success) {
          setPrograms(programsResult.programs);
          
          // For learners, check access status for each program
          if (isLearner && programsResult.programs.length > 0) {
            const accessStatusPromises = programsResult.programs.map(async (program) => {
              const accessResult = await checkProgramAccess(program.id);
              return {
                programId: program.id,
                ...accessResult
              };
            });
            
            const accessResults = await Promise.all(accessStatusPromises);
            const statusMap = {};
            accessResults.forEach(result => {
              statusMap[result.programId] = result;
            });
            setProgramAccessStatus(statusMap);
          }
        } else {
          toast({
            title: "Error loading programs",
            description: programsResult.error,
            variant: "destructive",
          });
        }

        // Load courses
        const coursesResult = await getAllCourses();
        if (coursesResult.success) {
          setCourses(coursesResult.courses);
        } else {
          toast({
            title: "Error loading courses",
            description: coursesResult.error,
            variant: "destructive",
          });
        }
      } catch (error) {
        console.error('Error loading data:', error);
        toast({
          title: "Error loading data",
          description: "Failed to load programs and courses",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [getAllPrograms, getAllCourses, checkProgramAccess, isLearner, toast]);

  const handleCreateProgram = async () => {
    if (!newProgram.title || !newProgram.description || newProgram.courseIds.length === 0) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information and select at least one course.",
        variant: "destructive",
      });
      return;
    }

    try {
      // Prepare program data for backend
      const programData = {
        title: newProgram.title,
        description: newProgram.description,
        courseIds: newProgram.courseIds,
        nestedProgramIds: newProgram.nestedProgramIds,
        duration: newProgram.duration || '8 weeks',
        // Note: Backend will add instructorId, instructor, and other metadata
      };

      const result = await createProgram(programData);
      
      if (result.success) {
        let finalTestCreated = true;
        let finalTestError = null;
        
        console.log('Program created successfully:', result);
        console.log('Final test data:', newProgram.finalTest);
        console.log('Final test questions:', newProgram.finalTest.questions);
        console.log('Questions length:', newProgram.finalTest.questions?.length);
        console.log('Final test title:', newProgram.finalTest.title);
        console.log('Final test description:', newProgram.finalTest.description);
        
        // Create final test if questions are provided OR if any final test fields are filled
        const hasFinalTestContent = (
          (newProgram.finalTest.questions && newProgram.finalTest.questions.length > 0) ||
          (newProgram.finalTest.title && newProgram.finalTest.title.trim() !== '') ||
          (newProgram.finalTest.description && newProgram.finalTest.description.trim() !== '')
        );
        
        if (hasFinalTestContent) {
          // Sanitize and validate all question data before sending to backend
          const sanitizedQuestions = newProgram.finalTest.questions.map(question => {
            console.log('🔍 DEBUG: Processing question for sanitization:', {
              id: question.id,
              type: question.type,
              correctAnswer: question.correctAnswer,
              correctAnswerType: typeof question.correctAnswer
            });
            
            const sanitized = {
              type: String(question.type || 'multiple_choice'),
              question: String(question.question || ''),
              points: Number(question.points) || 10,
              explanation: String(question.explanation || '')
            };

            // Handle options for multiple choice and select-all-that-apply questions
            if (['multiple_choice', 'select-all-that-apply'].includes(sanitized.type)) {
              sanitized.options = (question.options || []).map(option => String(option || ''));
              sanitized.correctAnswer = String(question.correctAnswer || '0');
              
              console.log('🔍 DEBUG: Multiple choice sanitized:', {
                questionId: question.id,
                originalCorrectAnswer: question.correctAnswer,
                sanitizedCorrectAnswer: sanitized.correctAnswer,
                options: sanitized.options
              });
            }

            // Handle true/false questions (use string values, not indices)
            if (sanitized.type === 'true_false') {
              sanitized.correctAnswer = String(question.correctAnswer || 'true');
              
              console.log('🔍 DEBUG: True/false sanitized:', {
                questionId: question.id,
                originalCorrectAnswer: question.correctAnswer,
                sanitizedCorrectAnswer: sanitized.correctAnswer
              });
            }

            // Handle correctAnswers for select-all-that-apply questions  
            if (sanitized.type === 'select-all-that-apply') {
              sanitized.correctAnswers = (question.correctAnswers || []).map(answer => String(answer));
            }

            // Handle items for chronological-order questions
            if (sanitized.type === 'chronological-order') {
              sanitized.items = (question.items || []).map(item => String(item || ''));
              sanitized.correctOrder = (question.correctOrder || []).map(order => Number(order));
            }

            // Handle short_answer and essay questions
            if (['short_answer', 'essay'].includes(sanitized.type)) {
              sanitized.correctAnswer = String(question.correctAnswer || '');
            }

            return sanitized;
          });

          const finalTestData = {
            title: newProgram.finalTest.title || `${newProgram.title} Final Assessment`,
            description: newProgram.finalTest.description || `Comprehensive final test for ${newProgram.title}`,
            programId: result.program?.id || result.id,
            questions: sanitizedQuestions,
            timeLimit: newProgram.finalTest.timeLimit || 90,
            maxAttempts: newProgram.finalTest.maxAttempts || 2,
            passingScore: newProgram.finalTest.passingScore || 75,
            shuffleQuestions: false,
            showResults: true,
            isPublished: true
          };

          const finalTestResult = await createFinalTest(finalTestData);
          
          if (!finalTestResult.success) {
            finalTestCreated = false;
            finalTestError = finalTestResult.error;
          }
        } else {
          console.log('No final test questions provided, skipping final test creation');
        }
        
        // Refresh programs list
        const programsResult = await getAllPrograms();
        if (programsResult.success) {
          setPrograms(programsResult.programs);
        }

        // Show appropriate success message
        if (finalTestCreated) {
          const questionCount = newProgram.finalTest.questions?.length || 0;
          const finalTestMessage = questionCount > 0 
            ? ` and final test with ${questionCount} questions`
            : ' and empty final test (you can add questions by editing the program)';
            
          toast({
            title: "Program created successfully!",
            description: `${newProgram.title} has been created with ${newProgram.courseIds.length} courses${hasFinalTestContent ? finalTestMessage : ''}.`,
          });
        } else {
          toast({
            title: "Program created with issues",
            description: `${newProgram.title} was created, but final test creation failed: ${finalTestError}. You can add the final test by editing the program.`,
            variant: "destructive",
          });
        }

        // Reset form
        setNewProgram({
          title: '',
          description: '',
          courseIds: [],
          courseOrder: [],
          nestedProgramIds: [],
          duration: '',
          finalTest: {
            title: '',
            description: '',
            timeLimit: 90,
            passingScore: 75,
            maxAttempts: 2,
            questions: []
          }
        });
        setIsCreateModalOpen(false);
      } else {
        toast({
          title: "Error creating program",
          description: result.error,
          variant: "destructive",
        });
      }
      
    } catch (error) {
      console.error('Error creating program:', error);
      toast({
        title: "Error creating program",
        description: "There was an error creating the program. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleDeleteProgram = async (programId, programName) => {
    if (!window.confirm(`Are you sure you want to delete the program "${programName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const result = await deleteProgram(programId);
      
      if (result.success) {
        toast({
          title: "Program deleted successfully",
          description: `"${programName}" has been permanently deleted.`,
        });
        
        // Reload programs to update the list
        const programsResult = await getAllPrograms();
        if (programsResult.success) {
          setPrograms(programsResult.programs);
        }
      } else {
        toast({
          title: "Failed to delete program",
          description: result.error || "An error occurred while deleting the program.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error deleting program:', error);
      toast({
        title: "Error deleting program",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleCourseSelection = (courseId, checked) => {
    if (checked) {
      setNewProgram(prev => ({
        ...prev,
        courseIds: [...prev.courseIds, courseId],
        courseOrder: [...prev.courseOrder, courseId]
      }));
    } else {
      setNewProgram(prev => ({
        ...prev,
        courseIds: prev.courseIds.filter(id => id !== courseId),
        courseOrder: prev.courseOrder.filter(id => id !== courseId)
      }));
    }
  };

  const moveCourseUp = (index) => {
    if (index === 0) return;
    const newOrder = [...newProgram.courseOrder];
    [newOrder[index], newOrder[index - 1]] = [newOrder[index - 1], newOrder[index]];
    setNewProgram(prev => ({ ...prev, courseOrder: newOrder }));
  };

  const moveCourseDown = (index) => {
    if (index === newProgram.courseOrder.length - 1) return;
    const newOrder = [...newProgram.courseOrder];
    [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
    setNewProgram(prev => ({ ...prev, courseOrder: newOrder }));
  };

  const removeCourseFromOrder = (courseId) => {
    setNewProgram(prev => ({
      ...prev,
      courseIds: prev.courseIds.filter(id => id !== courseId),
      courseOrder: prev.courseOrder.filter(id => id !== courseId)
    }));
  };

  // Final Test handlers for Create Program
  const handleFinalTestChange = (field, value) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        [field]: value
      }
    }));
  };

  const addFinalTestQuestion = () => {
    const newQuestion = {
      id: `ftq_${Date.now()}`,
      type: 'multiple_choice',
      question: '',
      options: ['', '', '', ''],
      correctAnswer: '0',
      correctAnswers: [],
      items: [],
      correctOrder: [],
      points: 10,
      explanation: ''
    };
    
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: [...prev.finalTest.questions, newQuestion]
      }
    }));
  };

  const removeFinalTestQuestion = (questionIndex) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.filter((_, index) => index !== questionIndex)
      }
    }));
  };

  const handleFinalTestQuestionChange = (questionIndex, field, value) => {
    console.log('🔍 DEBUG: handleFinalTestQuestionChange called:', {
      questionIndex,
      field,
      value,
      valueType: typeof value
    });
    
    setNewProgram(prev => {
      const currentQuestion = prev.finalTest.questions[questionIndex];
      console.log('🔍 DEBUG: Current question before update:', {
        id: currentQuestion?.id,
        type: currentQuestion?.type,
        correctAnswer: currentQuestion?.correctAnswer,
        correctAnswerType: typeof currentQuestion?.correctAnswer
      });
      
      const updated = {
        ...prev,
        finalTest: {
          ...prev.finalTest,
          questions: prev.finalTest.questions.map((question, index) => {
            if (index !== questionIndex) return question;
            
            const updatedQuestion = { ...question, [field]: value };
            
            console.log('🔍 DEBUG: Question after field update:', {
              id: updatedQuestion.id,
              field: field,
              value: value,
              updatedCorrectAnswer: updatedQuestion.correctAnswer,
              updatedCorrectAnswerType: typeof updatedQuestion.correctAnswer
            });
            
            // Initialize appropriate arrays when question type changes
            if (field === 'type') {
              switch (value) {
                case 'multiple_choice':
                case 'select-all-that-apply':
                  // Ensure options array exists with strings
                  if (!updatedQuestion.options || updatedQuestion.options.length === 0) {
                    updatedQuestion.options = ['', '', '', ''];
                  }
                  // Ensure all options are strings
                  updatedQuestion.options = updatedQuestion.options.map(opt => String(opt || ''));
                  updatedQuestion.correctAnswer = String(updatedQuestion.correctAnswer || '0');
                  break;
                case 'true_false':
                  // For true/false, use string values "true"/"false" not indices
                  updatedQuestion.correctAnswer = 'true'; // Default to true
                  break;
                case 'chronological-order':
                  // Ensure items array exists with strings
                  if (!updatedQuestion.items || updatedQuestion.items.length === 0) {
                    updatedQuestion.items = ['', '', ''];
                  }
                  // Ensure all items are strings
                  updatedQuestion.items = updatedQuestion.items.map(item => String(item || ''));
                  updatedQuestion.correctOrder = [0, 1, 2];
                  break;
                case 'short_answer':
                case 'essay':
                  // Ensure correctAnswer is string
                  updatedQuestion.correctAnswer = String(updatedQuestion.correctAnswer || '');
                  break;
              }
            }
            
            // Ensure specific fields are always strings when updated
            if (field === 'question') {
              updatedQuestion.question = String(value || '');
            }
            if (field === 'correctAnswer') {
              updatedQuestion.correctAnswer = String(value || '0');
              console.log('🔍 DEBUG: Explicitly set correctAnswer to:', updatedQuestion.correctAnswer);
            }
            if (field === 'explanation') {
              updatedQuestion.explanation = String(value || '');
            }
            
            console.log('🔍 DEBUG: Final question after all processing:', {
              id: updatedQuestion.id,
              correctAnswer: updatedQuestion.correctAnswer,
              correctAnswerType: typeof updatedQuestion.correctAnswer
            });
            
            return updatedQuestion;
          })
        }
      };
      
      console.log('🔍 DEBUG: Full updated state questions:', updated.finalTest.questions.map(q => ({
        id: q.id,
        type: q.type,
        correctAnswer: q.correctAnswer
      })));
      
      return updated;
    });
  };

  const handleFinalTestOptionChange = (questionIndex, optionIndex, value) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? {
                ...question,
                options: question.options.map((option, oIndex) =>
                  oIndex === optionIndex ? String(value) : String(option || '')
                )
              }
            : question
        )
      }
    }));
  };

  const handleFinalTestOptionMediaChange = (questionIndex, optionIndex, mediaType, value) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? {
                ...question,
                options: question.options.map((option, oIndex) =>
                  oIndex === optionIndex ? { ...option, [mediaType]: value } : option
                )
              }
            : question
        )
      }
    }));
  };

  const addFinalTestAnswerOption = (questionIndex) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? { 
                ...question, 
                options: [...(question.options || []).map(opt => String(opt || '')), '']
              } 
            : question
        )
      }
    }));
  };

  const removeFinalTestAnswerOption = (questionIndex, optionIndex) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? { 
                ...question, 
                options: question.options.filter((_, oIdx) => oIdx !== optionIndex),
                correctAnswer: parseInt(question.correctAnswer) > optionIndex ? String(parseInt(question.correctAnswer) - 1) : question.correctAnswer,
                correctAnswers: (question.correctAnswers || [])
                  .map(idx => idx > optionIndex ? idx - 1 : idx)
                  .filter(idx => idx !== optionIndex)
              } 
            : question
        )
      }
    }));
  };

  const handleFinalTestItemChange = (questionIndex, itemIndex, value) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? {
                ...question,
                items: question.items.map((item, iIndex) =>
                  iIndex === itemIndex ? String(value) : String(item || '')
                )
              }
            : question
        )
      }
    }));
  };

  const addFinalTestOrderItem = (questionIndex) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? { 
                ...question, 
                items: [...(question.items || []).map(item => String(item || '')), '']
              } 
            : question
        )
      }
    }));
  };

  const removeFinalTestOrderItem = (questionIndex, itemIndex) => {
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? { 
                ...question, 
                items: question.items.filter((_, iIdx) => iIdx !== itemIndex)
              } 
            : question
        )
      }
    }));
  };

  const moveFinalTestOrderItemUp = (questionIndex, itemIndex) => {
    if (itemIndex === 0) return;
    
    setNewProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? {
                ...question,
                items: question.items.map((item, iIdx) => {
                  if (iIdx === itemIndex) return question.items[itemIndex - 1];
                  if (iIdx === itemIndex - 1) return question.items[itemIndex];
                  return item;
                })
              } 
            : question
        )
      }
    }));
  };

  const moveFinalTestOrderItemDown = (questionIndex, itemIndex) => {
    setNewProgram(prev => {
      const currentQuestion = prev.finalTest.questions[questionIndex];
      if (!currentQuestion || itemIndex >= currentQuestion.items.length - 1) return prev;
      
      return {
        ...prev,
        finalTest: {
          ...prev.finalTest,
          questions: prev.finalTest.questions.map((question, index) =>
            index === questionIndex 
              ? {
                  ...question,
                  items: question.items.map((item, iIdx) => {
                    if (iIdx === itemIndex) return question.items[itemIndex + 1];
                    if (iIdx === itemIndex + 1) return question.items[itemIndex];
                    return item;
                  })
                } 
              : question
          )
        }
      };
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Learning Programs</h1>
          <p className="text-gray-600">Create and manage structured learning paths by combining courses</p>
        </div>
        
        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Create Program
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Learning Program</DialogTitle>
            </DialogHeader>
            <div className="space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Program Title *</Label>
                  <Input
                    id="name"
                    placeholder="Enter program title"
                    value={newProgram.title}
                    onChange={(e) => setNewProgram(prev => ({ ...prev, title: e.target.value }))}
                  />
                </div>
                
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  placeholder="Describe the learning outcomes and goals of this program"
                  rows={3}
                  value={newProgram.description}
                  onChange={(e) => setNewProgram(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="duration">Estimated Duration</Label>
                  <Input
                    id="duration"
                    placeholder="e.g., 12 weeks, 3 months"
                    value={newProgram.duration}
                    onChange={(e) => setNewProgram(prev => ({ ...prev, duration: e.target.value }))}
                  />
                </div>

              </div>

              {/* Course Selection */}
              <div className="space-y-4">
                <Label>Select Courses *</Label>
                <div className="grid grid-cols-1 gap-3 max-h-48 overflow-y-auto border rounded-md p-4">
                  {courses.map(course => (
                    <label key={course.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newProgram.courseIds.includes(course.id)}
                        onChange={(e) => handleCourseSelection(course.id, e.target.checked)}
                        className="rounded"
                      />
                      <img 
                        src={course.thumbnailUrl || course.thumbnail || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=48&h=48&fit=crop&crop=center'} 
                        alt={course.title}
                        className="w-12 h-12 rounded-lg object-cover"
                      />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{course.title}</h4>
                        <p className="text-sm text-gray-600">{course.category} • {course.duration || 'N/A'}</p>
                      </div>
                    </label>
                  ))}
                </div>
                {courses.length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">
                    {loading ? 'Loading courses...' : 'No courses available. Create some courses first.'}
                  </p>
                )}
              </div>

              {/* Course Ordering */}
              {newProgram.courseOrder.length > 0 && (
                <div className="space-y-4">
                  <Label>Course Order (Use arrows to reorder)</Label>
                  <div className="space-y-2 border rounded-md p-4 bg-gray-50">
                    {newProgram.courseOrder.map((courseId, index) => {
                      const course = courses.find(c => c.id === courseId);
                      return (
                        <div
                          key={courseId}
                          className="flex items-center space-x-3 p-3 bg-white rounded-lg border shadow-sm"
                        >
                          <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                            {index + 1}
                          </div>
                          <img 
                            src={course?.thumbnail || 'https://via.placeholder.com/40'} 
                            alt={course?.title}
                            className="w-10 h-10 rounded-lg object-cover"
                          />
                          <div className="flex-1">
                            <h5 className="font-medium text-gray-900">{course?.title}</h5>
                            <p className="text-sm text-gray-600">{course?.duration || 'N/A'}</p>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => moveCourseUp(index)}
                              disabled={index === 0}
                            >
                              <ArrowUp className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => moveCourseDown(index)}
                              disabled={index === newProgram.courseOrder.length - 1}
                            >
                              <ArrowDown className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => removeCourseFromOrder(courseId)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Final Test Configuration */}
              <div className="space-y-4 border-t pt-6">
                <div className="flex items-center space-x-2">
                  <Trophy className="w-5 h-5 text-purple-600" />
                  <Label className="text-lg font-medium text-purple-800">Final Test Configuration</Label>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="finalTestTitle">Test Title</Label>
                    <Input
                      id="finalTestTitle"
                      placeholder="e.g., Full Stack Development Final Assessment"
                      value={newProgram.finalTest.title}
                      onChange={(e) => handleFinalTestChange('title', e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="finalTestTimeLimit">Time Limit (minutes)</Label>
                    <Input
                      id="finalTestTimeLimit"
                      type="number"
                      placeholder="90"
                      min="1"
                      value={newProgram.finalTest.timeLimit}
                      onChange={(e) => handleFinalTestChange('timeLimit', parseInt(e.target.value) || 90)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="finalTestPassingScore">Passing Score (%)</Label>
                    <Input
                      id="finalTestPassingScore"
                      type="number"
                      placeholder="75"
                      min="0"
                      max="100"
                      value={newProgram.finalTest.passingScore}
                      onChange={(e) => handleFinalTestChange('passingScore', parseInt(e.target.value) || 75)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="finalTestMaxAttempts">Max Attempts</Label>
                    <Input
                      id="finalTestMaxAttempts"
                      type="number"
                      placeholder="2"
                      min="1"
                      value={newProgram.finalTest.maxAttempts}
                      onChange={(e) => handleFinalTestChange('maxAttempts', parseInt(e.target.value) || 2)}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="finalTestDescription">Test Description</Label>
                  <Textarea
                    id="finalTestDescription"
                    placeholder="Describe what this final assessment covers"
                    rows={2}
                    value={newProgram.finalTest.description}
                    onChange={(e) => handleFinalTestChange('description', e.target.value)}
                  />
                </div>

                {/* Final Test Questions */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label className="text-base font-medium">Final Test Questions</Label>
                    <div className="flex items-center space-x-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setIsQuizPreviewOpen(true)}
                        disabled={newProgram.finalTest.questions.length === 0}
                        className="border-blue-300 text-blue-700 hover:bg-blue-50"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        Preview Test
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={addFinalTestQuestion}
                        className="border-purple-300 text-purple-700 hover:bg-purple-50"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Question
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {newProgram.finalTest.questions.map((question, questionIndex) => (
                      <FinalTestQuestionInterface
                        key={question.id}
                        question={question}
                        questionIndex={questionIndex}
                        onQuestionChange={handleFinalTestQuestionChange}
                        onOptionChange={handleFinalTestOptionChange}
                        onOptionMediaChange={handleFinalTestOptionMediaChange}
                        onItemChange={handleFinalTestItemChange}
                        onRemoveQuestion={removeFinalTestQuestion}
                        onAddOption={addFinalTestAnswerOption}
                        onRemoveOption={removeFinalTestAnswerOption}
                        onAddItem={addFinalTestOrderItem}
                        onRemoveItem={removeFinalTestOrderItem}
                        onMoveItemUp={moveFinalTestOrderItemUp}
                        onMoveItemDown={moveFinalTestOrderItemDown}
                      />
                    ))}

                    {newProgram.finalTest.questions.length === 0 && (
                      <div className="text-center py-6 text-purple-600 bg-purple-50 rounded-lg border border-purple-200">
                        <Trophy className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No questions added yet. Click "Add Question" to create your final test.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t">
                <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateProgram}>
                  Create Program
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Quiz Preview Modal */}
        <QuizPreview
          isOpen={isQuizPreviewOpen}
          onClose={() => setIsQuizPreviewOpen(false)}
          quizData={{
            title: newProgram.finalTest.title || 'Final Test Preview',
            timeLimit: newProgram.finalTest.timeLimit,
            passingScore: newProgram.finalTest.passingScore,
            questions: newProgram.finalTest.questions
          }}
        />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Programs</p>
                <p className="text-2xl font-bold text-blue-700">{programs.length}</p>
              </div>
              <Award className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Active Programs</p>
                <p className="text-2xl font-bold text-green-700">
                  {programs.filter(p => p.isActive).length}
                </p>
              </div>
              <BarChart className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Total Courses</p>
                <p className="text-2xl font-bold text-orange-700">
                  {programs.reduce((sum, p) => sum + (p.courseCount || 0), 0)}
                </p>
              </div>
              <BookOpen className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">My Programs</p>
                <p className="text-2xl font-bold text-purple-700">
                  {programs.filter(p => p.instructorId === user?.id).length}
                </p>
              </div>
              <Users className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Programs List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Learning Programs</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading programs...</p>
            </div>
          ) : programs.length === 0 ? (
            <div className="text-center py-12">
              <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No programs created yet</h3>
              <p className="text-gray-600 mb-4">Create your first learning program to get started</p>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Program
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {programs.map((program) => {
                const accessStatus = programAccessStatus[program.id];
                const hasAccess = !isLearner || (accessStatus && accessStatus.hasAccess);
                const isExpired = isLearner && accessStatus && accessStatus.reason === 'classroom_expired';
                const notEnrolled = isLearner && accessStatus && accessStatus.reason === 'not_enrolled';
                
                return (
                  <Card key={program.id} className={`hover:shadow-lg transition-shadow ${isExpired ? 'opacity-60' : ''}`}>
                    <CardContent className="p-6">
                      <div className="space-y-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">{program.title}</h3>
                            <p className="text-sm text-gray-600 leading-relaxed">{program.description}</p>
                          </div>
                          <div className="ml-2 space-y-1">
                            <Badge className="block">
                              {program.isActive ? 'Active' : 'Inactive'}
                            </Badge>
                            {isLearner && accessStatus && (
                              <Badge 
                                variant={hasAccess ? "default" : isExpired ? "destructive" : "secondary"}
                                className="block"
                              >
                                {hasAccess ? (
                                  <><CheckCircle className="w-3 h-3 mr-1" />Available</>
                                ) : isExpired ? (
                                  <><AlertTriangle className="w-3 h-3 mr-1" />Expired</>
                                ) : notEnrolled ? (
                                  <><AlertTriangle className="w-3 h-3 mr-1" />Not Enrolled</>
                                ) : (
                                  <><AlertTriangle className="w-3 h-3 mr-1" />No Access</>
                                )}
                              </Badge>
                            )}
                          </div>
                        </div>

                        {/* Access Status Message for Learners */}
                        {isLearner && accessStatus && !hasAccess && (
                          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                            <div className="flex items-start space-x-2">
                              <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                              <div className="text-sm text-yellow-800">
                                <p className="font-medium">Access Restricted</p>
                                <p className="text-xs mt-1">{accessStatus.message}</p>
                              </div>
                            </div>
                          </div>
                        )}

                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center text-blue-600">
                            <BookOpen className="w-4 h-4 mr-1" />
                            <span>{program.courseCount || 0} courses</span>
                          </div>
                          <div className="flex items-center text-gray-600">
                            <Users className="w-4 h-4 mr-1" />
                            <span>0 students</span>
                          </div>
                        </div>

                        {program.duration && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Clock className="w-4 h-4 mr-1" />
                            <span>{program.duration}</span>
                          </div>
                        )}

                        <div className="text-sm text-gray-600">
                          <strong>Created by:</strong> {program.instructor || 'Unknown'}
                        </div>

                        <div className="text-sm text-gray-600">
                          <strong>Created:</strong> {new Date(program.created_at).toLocaleDateString()}
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 mt-4">
                        <Button 
                          size="sm" 
                          className="flex-1"
                          onClick={() => navigate(`/program/${program.id}`)}
                          disabled={isLearner && !hasAccess}
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          {isLearner && !hasAccess ? 'Access Restricted' : 'View Details'}
                        </Button>
                        {(user?.role === 'admin' || program.instructorId === user?.id) && (
                          <>
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => navigate(`/program/${program.id}/edit`)}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            {isAdmin && (
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => handleDeleteProgram(program.id, program.title)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            )}
                          </>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Programs;
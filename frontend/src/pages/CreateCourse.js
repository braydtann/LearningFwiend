import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
// Backend data only - no more mock dependencies
import { ArrowLeft, Plus, Trash2, Upload, FileText, Eye, GripVertical } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import CoursePreview from '../components/CoursePreview';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

const CreateCourse = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user, createCourse, updateCourse, getCourseById, getAllCategories, uploadFile } = useAuth();
  const { toast } = useToast();
  
  const isEditing = Boolean(id);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSavingDraft, setIsSavingDraft] = useState(false);
  const [backendCourse, setBackendCourse] = useState(null);
  const [loadingCourse, setLoadingCourse] = useState(isEditing);
  
  const [courseData, setCourseData] = useState({
    title: '',
    description: '',
    category: '',
    duration: '',
    thumbnail: '',
    isPublic: true,
    enrollmentType: 'open', // 'open' or 'assignment'
    learningOutcomes: [''], // What students will learn
    modules: [
      {
        id: 'm1',
        title: '',
        lessons: [
          { id: 'l1', title: '', type: 'video', duration: '', videoUrl: '', presentationUrl: '', content: '', quiz: null }
        ]
      }
    ]
  });

  const [categories, setCategories] = useState([]);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  
  // Load course data if editing
  useEffect(() => {
    if (isEditing && id) {
      loadCourseData();
    }
  }, [isEditing, id]);
  
  // Load categories when component mounts
  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    setLoadingCategories(true);
    try {
      const result = await getAllCategories();
      if (result.success && result.categories && result.categories.length > 0) {
        // Filter out any categories with empty names and ensure valid values
        const validCategories = result.categories
          .filter(cat => cat.name && cat.name.trim() !== '')
          .map(cat => cat.name.trim());
        
        if (validCategories.length > 0) {
          setCategories(validCategories);
        } else {
          // Fallback to default categories if all are invalid
          setCategories(['Technology', 'Business', 'Design', 'Marketing']);
        }
      } else {
        // Fallback to default categories if backend fails
        console.warn('Failed to load categories from backend, using default categories:', result.error);
        setCategories(['Technology', 'Business', 'Design', 'Marketing']);
      }
    } catch (error) {
      // Fallback to default categories
      console.error('Error loading categories:', error);
      setCategories(['Technology', 'Business', 'Design', 'Marketing']);
    } finally {
      setLoadingCategories(false);
    }
  };

  const loadCourseData = async () => {
    setLoadingCourse(true);
    try {
      const result = await getCourseById(id);
      if (result.success) {
        setBackendCourse(result.course);
        // Initialize form with backend course data
        setCourseData({
          title: result.course.title || '',
          description: result.course.description || '',
          category: result.course.category || '',
          duration: result.course.duration || '',
          thumbnail: result.course.thumbnailUrl || result.course.thumbnail || '',
          isPublic: true,
          enrollmentType: 'open',
          learningOutcomes: result.course.learningOutcomes || [''],
          modules: result.course.modules || [
            {
              id: 'm1',
              title: '',
              lessons: [
                { id: 'l1', title: '', type: 'video', duration: '', videoUrl: '', presentationUrl: '', content: '', quiz: null }
              ]
            }
          ]
        });
      } else {
        // Fallback if backend fails
        console.error('Failed to load course from backend:', result.error);
        navigate('/courses');
        return;
      }
    } catch (error) {
      console.error('Error loading course:', error);
      toast({
        title: "Error loading course",
        description: "Failed to load course data",
        variant: "destructive",
      });
    } finally {
      setLoadingCourse(false);
    }
  };

  const handleCourseChange = (field, value) => {
    setCourseData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Learning Outcomes Functions
  const handleLearningOutcomeChange = (index, value) => {
    setCourseData(prev => ({
      ...prev,
      learningOutcomes: prev.learningOutcomes.map((outcome, idx) => 
        idx === index ? value : outcome
      )
    }));
  };

  const addLearningOutcome = () => {
    setCourseData(prev => ({
      ...prev,
      learningOutcomes: [...prev.learningOutcomes, '']
    }));
  };

  const removeLearningOutcome = (index) => {
    setCourseData(prev => ({
      ...prev,
      learningOutcomes: prev.learningOutcomes.filter((_, idx) => idx !== index)
    }));
  };

  const handleModuleChange = (moduleIndex, field, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, index) => 
        index === moduleIndex ? { ...module, [field]: value } : module
      )
    }));
  };

  const handleLessonChange = (moduleIndex, lessonIndex, field, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex ? { 
                  ...lesson, 
                  [field]: value,
                  // Initialize quiz data when type changes to 'quiz'
                  ...(field === 'type' && value === 'quiz' && !lesson.quiz ? {
                    quiz: {
                      id: `quiz${Date.now()}`,
                      title: (lesson.title || 'Untitled Lesson') + ' Quiz',
                      description: '',
                      timeLimit: 10,
                      maxAttempts: 3,
                      passingScore: 70,
                      showResults: true,
                      shuffleQuestions: false,
                      questions: []
                    }
                  } : {})
                } : lesson
              )
            }
          : module
      )
    }));
  };

  const handleQuizChange = (moduleIndex, lessonIndex, field, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        id: lesson.quiz?.id || `quiz${Date.now()}`,
                        title: lesson.title + ' Quiz',
                        [field]: value
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const addQuizQuestion = (moduleIndex, lessonIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: [
                          ...(lesson.quiz?.questions || []),
                          {
                            id: `q${Date.now()}`,
                            type: 'true-false',
                            question: '',
                            questionImage: '',
                            questionAudio: '',
                            options: [
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' }
                            ],
                            items: [], // for chronological-order
                            correctAnswer: 0,
                            correctAnswers: [], // for select-all-that-apply
                            correctOrder: [], // for chronological-order
                            sampleAnswer: '', // for essay questions
                            wordLimit: null, // for essay questions
                            points: 5,
                            explanation: ''
                          }
                        ]
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const removeQuizQuestion = (moduleIndex, lessonIndex, questionIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).filter((_, qIdx) => qIdx !== questionIndex)
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const handleQuestionChange = (moduleIndex, lessonIndex, questionIndex, field, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex ? { ...question, [field]: value } : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const handleOptionChange = (moduleIndex, lessonIndex, questionIndex, optionIndex, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                options: question.options?.map((option, oIdx) =>
                                  oIdx === optionIndex ? value : option
                                ) || []
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const handleOrderItemChange = (moduleIndex, lessonIndex, questionIndex, itemIndex, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                items: question.items?.map((item, iIdx) =>
                                  iIdx === itemIndex ? value : item
                                ) || []
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const addOrderItem = (moduleIndex, lessonIndex, questionIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                items: [...(question.items || []), { text: '', image: '', audio: '' }]
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const removeOrderItem = (moduleIndex, lessonIndex, questionIndex, itemIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                items: (question.items || []).filter((_, iIdx) => iIdx !== itemIndex)
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const addAnswerOption = (moduleIndex, lessonIndex, questionIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                options: [...(question.options || []), { text: '', image: '', audio: '' }]
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const removeAnswerOption = (moduleIndex, lessonIndex, questionIndex, optionIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                options: (question.options || []).filter((_, oIdx) => oIdx !== optionIndex),
                                correctAnswer: question.correctAnswer === optionIndex ? 0 : 
                                             question.correctAnswer > optionIndex ? question.correctAnswer - 1 : question.correctAnswer,
                                correctAnswers: question.correctAnswers ? 
                                  question.correctAnswers.map(ans => ans > optionIndex ? ans - 1 : ans).filter(ans => ans !== optionIndex) :
                                  []
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const toggleCorrectAnswer = (moduleIndex, lessonIndex, questionIndex, optionIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                correctAnswers: (() => {
                                  const currentAnswers = question.correctAnswers || [];
                                  const isCurrentlyCorrect = currentAnswers.includes(optionIndex);
                                  
                                  if (isCurrentlyCorrect) {
                                    // Remove from correct answers
                                    return currentAnswers.filter(idx => idx !== optionIndex);
                                  } else {
                                    // Add to correct answers
                                    return [...currentAnswers, optionIndex];
                                  }
                                })()
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const handleOptionTextChange = (moduleIndex, lessonIndex, questionIndex, optionIndex, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                options: (question.options || []).map((option, oIdx) =>
                                  oIdx === optionIndex 
                                    ? (typeof option === 'string' ? { text: value, image: '', audio: '' } : { ...option, text: value })
                                    : option
                                )
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const handleOptionMediaChange = (moduleIndex, lessonIndex, questionIndex, optionIndex, mediaType, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                options: (question.options || []).map((option, oIdx) =>
                                  oIdx === optionIndex 
                                    ? (typeof option === 'string' ? { text: option, [mediaType]: value } : { ...option, [mediaType]: value })
                                    : option
                                )
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const handleOrderItemTextChange = (moduleIndex, lessonIndex, questionIndex, itemIndex, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                items: (question.items || []).map((item, iIdx) =>
                                  iIdx === itemIndex 
                                    ? (typeof item === 'string' ? { text: value, image: '', audio: '' } : { ...item, text: value })
                                    : item
                                )
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const handleOrderItemMediaChange = (moduleIndex, lessonIndex, questionIndex, itemIndex, mediaType, value) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                items: (question.items || []).map((item, iIdx) =>
                                  iIdx === itemIndex 
                                    ? (typeof item === 'string' ? { text: item, [mediaType]: value } : { ...item, [mediaType]: value })
                                    : item
                                )
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  // Handle drag-and-drop reordering for chronological order items
  const handleChronologicalDragEnd = (result, moduleIndex, lessonIndex, questionIndex) => {
    if (!result.destination) {
      return;
    }

    const sourceIndex = result.source.index;
    const destinationIndex = result.destination.index;

    if (sourceIndex === destinationIndex) {
      return;
    }

    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.map((lesson, lIdx) =>
                lIdx === lessonIndex 
                  ? { 
                      ...lesson, 
                      quiz: {
                        ...lesson.quiz,
                        questions: (lesson.quiz?.questions || []).map((question, qIdx) =>
                          qIdx === questionIndex 
                            ? { 
                                ...question, 
                                items: (() => {
                                  const newItems = Array.from(question.items || []);
                                  const [reorderedItem] = newItems.splice(sourceIndex, 1);
                                  newItems.splice(destinationIndex, 0, reorderedItem);
                                  return newItems;
                                })(),
                                // Update correctOrder to match new item order (0-based indices)
                                correctOrder: (() => {
                                  const newItems = Array.from(question.items || []);
                                  const [reorderedItem] = newItems.splice(sourceIndex, 1);
                                  newItems.splice(destinationIndex, 0, reorderedItem);
                                  // correctOrder should be the current order (0, 1, 2, 3, ...)
                                  return newItems.map((_, index) => index);
                                })()
                              } 
                            : question
                        )
                      }
                    } 
                  : lesson
              )
            }
          : module
      )
    }));
  };

  const addModule = () => {
    setCourseData(prev => ({
      ...prev,
      modules: [
        ...prev.modules,
        {
          id: `m${prev.modules.length + 1}`,
          title: '',
          lessons: [
            { id: `l${Date.now()}`, title: '', type: 'video', duration: '', videoUrl: '', presentationUrl: '', content: '', quiz: null }
          ]
        }
      ]
    }));
  };

  const removeModule = (moduleIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.filter((_, index) => index !== moduleIndex)
    }));
  };

  const addLesson = (moduleIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, index) => 
        index === moduleIndex 
          ? {
              ...module,
              lessons: [
                ...module.lessons,
                { id: `l${Date.now()}`, title: '', type: 'video', duration: '', videoUrl: '', presentationUrl: '', content: '', quiz: null }
              ]
            }
          : module
      )
    }));
  };

  const removeLesson = (moduleIndex, lessonIndex) => {
    setCourseData(prev => ({
      ...prev,
      modules: prev.modules.map((module, mIdx) => 
        mIdx === moduleIndex 
          ? {
              ...module,
              lessons: module.lessons.filter((_, lIdx) => lIdx !== lessonIndex)
            }
          : module
      )
    }));
  };

  const handleSaveDraft = async () => {
    if (!courseData.title.trim()) {
      toast({
        title: "Title required",
        description: "Please enter a course title to save as draft.",
        variant: "destructive",
      });
      return;
    }

    setIsSavingDraft(true);
    
    try {
      const coursePayload = {
        title: courseData.title,
        description: courseData.description || "Draft course - description to be added",
        category: courseData.category || "Uncategorized",
        duration: courseData.duration || "TBD",
        thumbnailUrl: courseData.thumbnail,
        accessType: courseData.accessType || 'open',
        learningOutcomes: courseData.learningOutcomes.filter(outcome => outcome.trim() !== ''), // Only include non-empty outcomes
        modules: courseData.modules || [],
        canvaEmbedCode: courseData.canvaEmbedCode,
        status: "draft"  // Save as draft
      };

      let result;
      if (isEditing) {
        // Update existing course as draft
        result = await updateCourse(id, coursePayload);
      } else {
        // Create new course as draft
        result = await createCourse(coursePayload);
      }

      if (result.success) {
        toast({
          title: "Draft saved!",
          description: `Your course "${courseData.title}" has been saved as a draft. You can continue editing it later.`,
        });
        
        // If it's a new course, navigate to edit mode to continue working on it
        if (!isEditing && result.course) {
          navigate(`/edit-course/${result.course.id}`);
        }
      } else {
        toast({
          title: "Draft save failed",
          description: result.error || "Failed to save course as draft.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error saving draft:', error);
      toast({
        title: "Error",
        description: "An unexpected error occurred while saving the draft.",
        variant: "destructive",
      });
    } finally {
      setIsSavingDraft(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!courseData.title || !courseData.description || !courseData.category) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required course information.",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsSubmitting(true);

      // Prepare course data for API
      const coursePayload = {
        title: courseData.title,
        description: courseData.description,
        category: courseData.category,
        duration: courseData.duration,
        thumbnailUrl: courseData.thumbnail,
        accessType: courseData.accessType || 'open',
        learningOutcomes: courseData.learningOutcomes.filter(outcome => outcome.trim() !== ''), // Only include non-empty outcomes
        modules: courseData.modules || [],
        canvaEmbedCode: courseData.canvaEmbedCode,
        status: "published"  // Publish the course
      };

      let result;
      if (isEditing) {
        // Update existing course
        result = await updateCourse(id, coursePayload);
      } else {
        // Create new course
        result = await createCourse(coursePayload);
      }

      if (result.success) {
        toast({
          title: isEditing ? "Course updated!" : "Course created!",
          description: `Your course "${courseData.title}" has been ${isEditing ? 'updated' : 'created'} successfully and is now available in the course catalog.`,
        });
        
        navigate('/courses');
      } else {
        toast({
          title: "Course creation failed",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An unexpected error occurred while creating the course.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {isEditing ? 'Edit Course' : 'Create New Course'}
          </h1>
          <p className="text-gray-600">
            {isEditing ? 'Update your course content and settings' : 'Build an engaging learning experience'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="title">Course Title *</Label>
                <Input
                  id="title"
                  placeholder="Enter course title"
                  value={courseData.title}
                  onChange={(e) => handleCourseChange('title', e.target.value)}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select 
                  value={courseData.category} 
                  onValueChange={(value) => handleCourseChange('category', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.filter(category => category && category.trim() !== '').map(category => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                    {categories.length === 0 && (
                      <SelectItem key="loading" value="Technology">
                        Technology (Loading categories...)
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                placeholder="Describe what students will learn in this course"
                rows={4}
                value={courseData.description}
                onChange={(e) => handleCourseChange('description', e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="duration">Course Duration</Label>
                <Input
                  id="duration"
                  placeholder="e.g., 8 weeks, 20 hours"
                  value={courseData.duration}
                  onChange={(e) => handleCourseChange('duration', e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="thumbnail">Thumbnail URL</Label>
                <Input
                  id="thumbnail"
                  placeholder="https://example.com/image.jpg"
                  value={courseData.thumbnail}
                  onChange={(e) => handleCourseChange('thumbnail', e.target.value)}
                />
              </div>
            </div>

            {/* Enrollment Type */}
            <div className="space-y-4 border-t pt-6">
              <div className="space-y-2">
                <Label htmlFor="enrollmentType">Course Access Type</Label>
                <Select 
                  value={courseData.enrollmentType} 
                  onValueChange={(value) => handleCourseChange('enrollmentType', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select access type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="open">
                      <div className="flex flex-col">
                        <span className="font-medium">Open Enrollment</span>
                        <span className="text-sm text-gray-500">Anyone can enroll in this course</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="assignment">
                      <div className="flex flex-col">
                        <span className="font-medium">Assignment Only</span>
                        <span className="text-sm text-gray-500">Students must be assigned by instructor/admin</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-gray-600">
                  {courseData.enrollmentType === 'open' 
                    ? '🟢 Students can browse and enroll in this course themselves'
                    : '🔒 Only assigned students will have access to this course'
                  }
                </p>
              </div>
            </div>

            {/* What You'll Learn Section */}
            <div className="space-y-4 border-t pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-lg font-medium">What You'll Learn</Label>
                  <p className="text-sm text-gray-600">Add learning outcomes that will be displayed to students</p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addLearningOutcome}
                  className="border-green-300 text-green-700 hover:bg-green-100"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Outcome
                </Button>
              </div>
              
              <div className="space-y-3">
                {courseData.learningOutcomes.map((outcome, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-green-50/50 rounded-lg border border-green-200">
                    <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0"></div>
                    <Input
                      placeholder="e.g., Master the fundamentals and advanced concepts"
                      value={outcome}
                      onChange={(e) => handleLearningOutcomeChange(index, e.target.value)}
                      className="border-green-200 focus:border-green-400"
                    />
                    {courseData.learningOutcomes.length > 1 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeLearningOutcome(index)}
                        className="border-red-300 text-red-600 hover:bg-red-50 flex-shrink-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                ))}
                
                {courseData.learningOutcomes.length === 0 && (
                  <div className="text-center py-8 text-gray-500 bg-gray-50/50 rounded-lg border-2 border-dashed border-gray-200">
                    <p>No learning outcomes added yet. Click "Add Outcome" to get started.</p>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Course Content */}
        <Card className="bg-blue-50/50 border-blue-200">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full bg-blue-400"></div>
                <CardTitle className="text-blue-800">Course Content</CardTitle>
              </div>
              <Button type="button" variant="outline" onClick={addModule} className="border-blue-300 text-blue-700 hover:bg-blue-100">
                <Plus className="w-4 h-4 mr-2" />
                Add Module
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {courseData.modules.map((module, moduleIndex) => (
              <Card key={module.id} className="border-2 border-dashed border-green-200 bg-green-50/60">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 rounded-full bg-green-500"></div>
                      <Badge variant="secondary" className="bg-green-200 text-green-800 border-green-300">Module {moduleIndex + 1}</Badge>
                      <Input
                        placeholder="Module title"
                        value={module.title}
                        onChange={(e) => handleModuleChange(moduleIndex, 'title', e.target.value)}
                        className="flex-1"
                      />
                    </div>
                    {courseData.modules.length > 1 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeModule(moduleIndex)}
                        className="border-red-300 text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>

                  <div className="space-y-4">
                    {module.lessons.map((lesson, lessonIndex) => (
                      <div key={lesson.id} className="border-2 border-purple-200 rounded-lg p-4 bg-purple-50/70">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                            <h4 className="font-medium text-purple-800">Lesson {lessonIndex + 1}</h4>
                          </div>
                          {module.lessons.length > 1 && (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => removeLesson(moduleIndex, lessonIndex)}
                              className="border-red-300 text-red-600 hover:bg-red-50"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label>Lesson Title</Label>
                            <Input
                              placeholder="Enter lesson title"
                              value={lesson.title}
                              onChange={(e) => handleLessonChange(moduleIndex, lessonIndex, 'title', e.target.value)}
                            />
                          </div>
                          
                          <div className="space-y-2">
                            <Label>Lesson Type</Label>
                            <Select 
                              value={lesson.type} 
                              onValueChange={(value) => handleLessonChange(moduleIndex, lessonIndex, 'type', value)}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="video">Video</SelectItem>
                                <SelectItem value="presentation">Canva Presentation</SelectItem>
                                <SelectItem value="text">Text/Article</SelectItem>
                                <SelectItem value="quiz">Quiz</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>

                        {(lesson.type === 'video' || lesson.type === 'presentation') && (
                          <div className="space-y-4 mt-4">
                            {lesson.type === 'video' ? (
                              // Video URL fields
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                  <Label>Video URL</Label>
                                  <Input
                                    placeholder="YouTube, Vimeo, or Google Drive URL"
                                    value={lesson.videoUrl || ''}
                                    onChange={(e) => handleLessonChange(moduleIndex, lessonIndex, 'videoUrl', e.target.value)}
                                  />
                                  <p className="text-xs text-gray-500">
                                    Supported: YouTube, Vimeo, or Google Drive sharing links
                                  </p>
                                </div>
                                <div className="space-y-2">
                                  <Label>Duration</Label>
                                  <Input
                                    placeholder="e.g., 15 min"
                                    value={lesson.duration || ''}
                                    onChange={(e) => handleLessonChange(moduleIndex, lessonIndex, 'duration', e.target.value)}
                                  />
                                </div>
                              </div>
                            ) : (
                              // Canva Presentation fields
                              <div className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div className="space-y-2">
                                    <Label>Canva Presentation URL (Optional)</Label>
                                    <Input
                                      placeholder="Canva presentation sharing link"
                                      value={lesson.presentationUrl || ''}
                                      onChange={(e) => handleLessonChange(moduleIndex, lessonIndex, 'presentationUrl', e.target.value)}
                                    />
                                    <p className="text-xs text-gray-500">
                                      Direct link to your Canva presentation
                                    </p>
                                  </div>
                                  <div className="space-y-2">
                                    <Label>Duration</Label>
                                    <Input
                                      placeholder="e.g., 20 min"
                                      value={lesson.duration || ''}
                                      onChange={(e) => handleLessonChange(moduleIndex, lessonIndex, 'duration', e.target.value)}
                                    />
                                  </div>
                                </div>
                                
                                {/* Canva Embed Code Section */}
                                <div className="space-y-2 border-t pt-4">
                                  <Label>Canva Embed Code (Recommended)</Label>
                                  <Textarea
                                    placeholder='Paste your Canva embed code here (e.g., <div style="position: relative; width: 100%; height: 0; padding-top: 56.2500%;">...)'
                                    rows={4}
                                    value={lesson.embedCode || ''}
                                    onChange={(e) => handleLessonChange(moduleIndex, lessonIndex, 'embedCode', e.target.value)}
                                    className="font-mono text-sm"
                                  />
                                  <div className="bg-blue-50 p-3 rounded-lg">
                                    <p className="text-sm text-blue-800 font-medium mb-2">📋 How to get Canva embed code:</p>
                                    <ul className="text-xs text-blue-700 space-y-1">
                                      <li>1. Open your Canva presentation</li>
                                      <li>2. Click "Share" → "More" → "Embed"</li>
                                      <li>3. Copy the embed code and paste it above</li>
                                      <li>4. This will display the presentation directly in the course</li>
                                    </ul>
                                  </div>
                                  {lesson.embedCode && (
                                    <div className="bg-green-50 p-3 rounded-lg">
                                      <p className="text-sm text-green-800">
                                        ✅ Embed code detected! Students will see the presentation directly in the course.
                                      </p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {lesson.type === 'text' && (
                          <div className="mt-4 space-y-4">
                            <div className="space-y-2">
                              <Label>Content</Label>
                              <Textarea
                                placeholder="Enter lesson content"
                                rows={6}
                                value={lesson.content || ''}
                                onChange={(e) => handleLessonChange(moduleIndex, lessonIndex, 'content', e.target.value)}
                              />
                            </div>
                            
                            {/* Document Attachment Section */}
                            <div className="space-y-2">
                              <Label>Attachable Document (Optional)</Label>
                              <div className="border border-dashed border-gray-300 rounded-lg p-4">
                                <div className="flex items-center justify-center space-x-2 text-gray-600">
                                  <Upload className="w-5 h-5" />
                                  <span className="text-sm">Upload PDF, Word, or other documents</span>
                                </div>
                                <Input
                                  type="file"
                                  accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.xls,.xlsx"
                                  className="mt-2"
                                  onChange={async (e) => {
                                    const file = e.target.files?.[0];
                                    if (file) {
                                      try {
                                        // Show upload progress
                                        handleLessonChange(moduleIndex, lessonIndex, 'documentName', `Uploading ${file.name}...`);
                                        handleLessonChange(moduleIndex, lessonIndex, 'documentUrl', '');
                                        
                                        // Upload file using the new uploadFile function
                                        const uploadResult = await uploadFile(file);
                                        
                                        if (uploadResult.success) {
                                          handleLessonChange(moduleIndex, lessonIndex, 'documentUrl', uploadResult.fileUrl);
                                          handleLessonChange(moduleIndex, lessonIndex, 'documentName', uploadResult.fileName);
                                          toast({
                                            title: "File uploaded successfully",
                                            description: `${file.name} has been uploaded and will be available to students.`,
                                          });
                                        } else {
                                          handleLessonChange(moduleIndex, lessonIndex, 'documentName', '');
                                          handleLessonChange(moduleIndex, lessonIndex, 'documentUrl', '');
                                          toast({
                                            title: "Upload failed",
                                            description: uploadResult.error || "Failed to upload file. Please try again.",
                                            variant: "destructive",
                                          });
                                        }
                                      } catch (error) {
                                        handleLessonChange(moduleIndex, lessonIndex, 'documentName', '');
                                        handleLessonChange(moduleIndex, lessonIndex, 'documentUrl', '');
                                        toast({
                                          title: "Upload error",
                                          description: "An error occurred while uploading the file.",
                                          variant: "destructive",
                                        });
                                      }
                                    }
                                  }}
                                />
                                {lesson.documentName && (
                                  <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                      <FileText className="w-4 h-4 text-green-600" />
                                      <span className="text-sm text-green-800">{lesson.documentName}</span>
                                    </div>
                                    <Button
                                      type="button"
                                      variant="outline"
                                      size="sm"
                                      onClick={() => {
                                        handleLessonChange(moduleIndex, lessonIndex, 'documentUrl', '');
                                        handleLessonChange(moduleIndex, lessonIndex, 'documentName', '');
                                      }}
                                    >
                                      Remove
                                    </Button>
                                  </div>
                                )}
                                <p className="text-xs text-gray-500 mt-1">
                                  Supported formats: PDF, Word, PowerPoint, Excel, Text files
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {lesson.type === 'quiz' && (
                          <div className="mt-4 space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                              <div className="space-y-2">
                                <Label>Time Limit (minutes)</Label>
                                <Input
                                  type="number"
                                  placeholder="10"
                                  value={lesson.quiz?.timeLimit || ''}
                                  onChange={(e) => handleQuizChange(moduleIndex, lessonIndex, 'timeLimit', parseInt(e.target.value) || 0)}
                                />
                              </div>
                              <div className="space-y-2">
                                <Label>Passing Score (%)</Label>
                                <Input
                                  type="number"
                                  placeholder="70"
                                  min="0"
                                  max="100"
                                  value={lesson.quiz?.passingScore || ''}
                                  onChange={(e) => handleQuizChange(moduleIndex, lessonIndex, 'passingScore', parseInt(e.target.value) || 70)}
                                />
                              </div>
                              <div className="space-y-2">
                                <Label>Max Attempts</Label>
                                <Input
                                  type="number"
                                  placeholder="3"
                                  min="1"
                                  value={lesson.quiz?.maxAttempts || ''}
                                  onChange={(e) => handleQuizChange(moduleIndex, lessonIndex, 'maxAttempts', parseInt(e.target.value) || 3)}
                                />
                              </div>
                              <div className="space-y-2">
                                <Label>Target Questions</Label>
                                <Input
                                  type="number"
                                  placeholder="5"
                                  min="1"
                                  max="50"
                                  value={lesson.quiz?.targetQuestionCount || ''}
                                  onChange={(e) => handleQuizChange(moduleIndex, lessonIndex, 'targetQuestionCount', parseInt(e.target.value) || 5)}
                                />
                                <p className="text-xs text-gray-500">Recommended number of questions</p>
                              </div>
                            </div>
                            
                            <div className="space-y-2">
                              <Label>Quiz Description</Label>
                              <Textarea
                                placeholder="Describe what this quiz covers"
                                rows={2}
                                value={lesson.quiz?.description || ''}
                                onChange={(e) => handleQuizChange(moduleIndex, lessonIndex, 'description', e.target.value)}
                              />
                            </div>

                            <div className="space-y-2">
                              <div className="flex items-center space-x-4">
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="checkbox"
                                    id={`shuffle-${lesson.id}`}
                                    checked={lesson.quiz?.shuffleQuestions || false}
                                    onChange={(e) => handleQuizChange(moduleIndex, lessonIndex, 'shuffleQuestions', e.target.checked)}
                                    className="rounded border-gray-300"
                                  />
                                  <Label htmlFor={`shuffle-${lesson.id}`}>Shuffle Questions</Label>
                                </div>
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="checkbox"
                                    id={`show-results-${lesson.id}`}
                                    checked={lesson.quiz?.showResults !== false}
                                    onChange={(e) => handleQuizChange(moduleIndex, lessonIndex, 'showResults', e.target.checked)}
                                    className="rounded border-gray-300"
                                  />
                                  <Label htmlFor={`show-results-${lesson.id}`}>Show Results After Submission</Label>
                                </div>
                              </div>
                            </div>

                            <div className="border-t pt-4">
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-4">
                                  <div className="w-2 h-2 rounded-full bg-pink-500"></div>
                                  <Label className="text-lg font-medium text-pink-800">Quiz Questions</Label>
                                  {lesson.quiz?.targetQuestionCount && (
                                    <Badge variant="outline" className={
                                      (lesson.quiz?.questions || []).length === lesson.quiz.targetQuestionCount
                                        ? "border-green-500 text-green-700 bg-green-50"
                                        : (lesson.quiz?.questions || []).length > lesson.quiz.targetQuestionCount
                                        ? "border-orange-500 text-orange-700 bg-orange-50"
                                        : "border-gray-400 text-gray-600"
                                    }>
                                      {(lesson.quiz?.questions || []).length} / {lesson.quiz.targetQuestionCount} questions
                                      {(lesson.quiz?.questions || []).length === lesson.quiz.targetQuestionCount && " ✓"}
                                    </Badge>
                                  )}
                                </div>
                              </div>

                              <div className="space-y-4">
                                {(lesson.quiz?.questions || []).map((question, questionIndex) => (
                                  <Card key={question.id} className="border-dashed border-pink-300 bg-pink-50/80">
                                    <CardContent className="p-4">
                                      <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center space-x-2">
                                          <div className="w-1.5 h-1.5 rounded-full bg-pink-600"></div>
                                          <Badge variant="outline" className="bg-pink-200 text-pink-800 border-pink-400">Question {questionIndex + 1}</Badge>
                                        </div>
                                        <Button
                                          type="button"
                                          variant="outline"
                                          size="sm"
                                          onClick={() => removeQuizQuestion(moduleIndex, lessonIndex, questionIndex)}
                                          className="border-red-300 text-red-600 hover:bg-red-50"
                                        >
                                          <Trash2 className="w-4 h-4" />
                                        </Button>
                                      </div>

                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                        <div className="space-y-2">
                                          <Label>Question Type</Label>
                                          <Select 
                                            value={question.type || 'true-false'} 
                                            onValueChange={(value) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'type', value)}
                                          >
                                            <SelectTrigger>
                                              <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                              <SelectItem value="true-false">True/False</SelectItem>
                                              <SelectItem value="multiple-choice">Multiple Choice</SelectItem>
                                              <SelectItem value="select-all-that-apply">Select All That Apply</SelectItem>
                                              <SelectItem value="chronological-order">Chronological Order</SelectItem>
                                              <SelectItem value="short-answer">Short Answer</SelectItem>
                                              <SelectItem value="long-form-answer">Long Form Answer</SelectItem>
                                            </SelectContent>
                                          </Select>
                                        </div>
                                        <div className="space-y-2">
                                          <Label>Points</Label>
                                          <Input
                                            type="number"
                                            placeholder="5"
                                            min="1"
                                            value={question.points || ''}
                                            onChange={(e) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'points', parseInt(e.target.value) || 1)}
                                          />
                                        </div>
                                      </div>

                                      <div className="space-y-2 mb-4">
                                        <Label>Question Text</Label>
                                        <Textarea
                                          placeholder="Enter your question here"
                                          rows={2}
                                          value={question.question || ''}
                                          onChange={(e) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'question', e.target.value)}
                                        />
                                      </div>

                                      {/* Question Media Upload */}
                                      <div className="space-y-2 mb-4">
                                        <Label>Question Media (Optional)</Label>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                          <div className="space-y-2">
                                            <Label className="text-sm">Image URL</Label>
                                            <Input
                                              placeholder="https://example.com/image.jpg"
                                              value={question.questionImage || ''}
                                              onChange={(e) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'questionImage', e.target.value)}
                                            />
                                          </div>
                                          <div className="space-y-2">
                                            <Label className="text-sm">Audio URL</Label>
                                            <Input
                                              placeholder="https://example.com/audio.mp3"
                                              value={question.questionAudio || ''}
                                              onChange={(e) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'questionAudio', e.target.value)}
                                            />
                                          </div>
                                        </div>
                                        {question.questionImage && (
                                          <div className="mt-2">
                                            <img src={question.questionImage} alt="Question" className="max-w-xs h-32 object-cover rounded border" />
                                          </div>
                                        )}
                                        {question.questionAudio && (
                                          <div className="mt-2">
                                            <audio controls className="w-full max-w-xs">
                                              <source src={question.questionAudio} type="audio/mpeg" />
                                              Your browser does not support the audio element.
                                            </audio>
                                          </div>
                                        )}
                                      </div>

                                      {question.type === 'true-false' && (
                                        <div className="space-y-2 mb-4">
                                          <Label>Correct Answer</Label>
                                          <Select 
                                            value={question.correctAnswer?.toString() || ''} 
                                            onValueChange={(value) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'correctAnswer', value === 'true')}
                                          >
                                            <SelectTrigger>
                                              <SelectValue placeholder="Select correct answer" />
                                            </SelectTrigger>
                                            <SelectContent>
                                              <SelectItem value="true">True</SelectItem>
                                              <SelectItem value="false">False</SelectItem>
                                            </SelectContent>
                                          </Select>
                                        </div>
                                      )}

                                      {question.type === 'multiple-choice' && (
                                        <div className="space-y-4 mb-4">
                                          <div className="flex items-center justify-between">
                                            <Label>Answer Options</Label>
                                            <Button
                                              type="button"
                                              variant="outline"
                                              size="sm"
                                              onClick={() => addAnswerOption(moduleIndex, lessonIndex, questionIndex)}
                                            >
                                              <Plus className="w-4 h-4 mr-1" />
                                              Add Option
                                            </Button>
                                          </div>
                                          
                                          <div className="space-y-3">
                                            {((question.options && Array.isArray(question.options)) ? question.options : []).map((option, optionIndex) => (
                                              <div key={`option-${optionIndex}`} className="border border-gray-200 rounded-lg p-3">
                                                <div className="flex items-center justify-between mb-2">
                                                  <div className="flex items-center space-x-2">
                                                    <Badge variant={question.correctAnswer === optionIndex ? "default" : "outline"}>
                                                      Option {optionIndex + 1}
                                                    </Badge>
                                                    <Button
                                                      type="button"
                                                      variant={question.correctAnswer === optionIndex ? "default" : "outline"}
                                                      size="sm"
                                                      onClick={() => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'correctAnswer', optionIndex)}
                                                    >
                                                      {question.correctAnswer === optionIndex ? '✓ Correct' : 'Mark as Correct'}
                                                    </Button>
                                                  </div>
                                                  {question.options && question.options.length > 2 && (
                                                    <Button
                                                      type="button"
                                                      variant="outline"
                                                      size="sm"
                                                      onClick={() => removeAnswerOption(moduleIndex, lessonIndex, questionIndex, optionIndex)}
                                                    >
                                                      <Trash2 className="w-4 h-4" />
                                                    </Button>
                                                  )}
                                                </div>
                                                
                                                <div className="space-y-2">
                                                  <Label className="text-sm">Option Text</Label>
                                                  <Input
                                                    placeholder={`Enter option ${optionIndex + 1} text`}
                                                    value={(typeof option === 'string' ? option : option?.text) || ''}
                                                    onChange={(e) => handleOptionTextChange(moduleIndex, lessonIndex, questionIndex, optionIndex, e.target.value)}
                                                  />
                                                </div>
                                                
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                                                  <div className="space-y-2">
                                                    <Label className="text-sm">Image URL (Optional)</Label>
                                                    <Input
                                                      placeholder="https://example.com/image.jpg"
                                                      value={(typeof option === 'object' ? option?.image : '') || ''}
                                                      onChange={(e) => handleOptionMediaChange(moduleIndex, lessonIndex, questionIndex, optionIndex, 'image', e.target.value)}
                                                    />
                                                  </div>
                                                  <div className="space-y-2">
                                                    <Label className="text-sm">Audio URL (Optional)</Label>
                                                    <Input
                                                      placeholder="https://example.com/audio.mp3"
                                                      value={(typeof option === 'object' ? option?.audio : '') || ''}
                                                      onChange={(e) => handleOptionMediaChange(moduleIndex, lessonIndex, questionIndex, optionIndex, 'audio', e.target.value)}
                                                    />
                                                  </div>
                                                </div>
                                                
                                                {/* Preview media if provided */}
                                                {(typeof option === 'object' && option?.image) && (
                                                  <div className="mt-2">
                                                    <img src={option.image} alt={`Option ${optionIndex + 1}`} className="max-w-xs h-20 object-cover rounded border" />
                                                  </div>
                                                )}
                                                {(typeof option === 'object' && option?.audio) && (
                                                  <div className="mt-2">
                                                    <audio controls className="w-full max-w-xs">
                                                      <source src={option.audio} type="audio/mpeg" />
                                                      Your browser does not support the audio element.
                                                    </audio>
                                                  </div>
                                                )}
                                              </div>
                                            ))}
                                          </div>
                                          
                                          {(!question.options || question.options.length === 0) && (
                                            <div className="text-center py-4 text-gray-500 border border-dashed border-gray-300 rounded-lg">
                                              <p>No answer options added yet. Click "Add Option" to get started.</p>
                                            </div>
                                          )}
                                          
                                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                                            <p className="text-blue-800 text-sm">
                                              💡 <strong>Tip:</strong> Add at least 2 options and mark one as correct. Students will select one option as their answer.
                                            </p>
                                          </div>
                                        </div>
                                      )}

                                      {question.type === 'select-all-that-apply' && (
                                        <div className="space-y-4 mb-4">
                                          <div className="flex items-center justify-between">
                                            <Label>Answer Options</Label>
                                            <Button
                                              type="button"
                                              variant="outline"
                                              size="sm"
                                              onClick={() => addAnswerOption(moduleIndex, lessonIndex, questionIndex)}
                                            >
                                              <Plus className="w-4 h-4 mr-1" />
                                              Add Option
                                            </Button>
                                          </div>
                                          
                                          <div className="space-y-3">
                                            {((question.options && Array.isArray(question.options)) ? question.options : []).map((option, optionIndex) => (
                                              <div key={`option-${optionIndex}`} className="border border-gray-200 rounded-lg p-3">
                                                <div className="flex items-center justify-between mb-2">
                                                  <div className="flex items-center space-x-2">
                                                    <Badge variant={(question.correctAnswers && Array.isArray(question.correctAnswers) && question.correctAnswers.includes(optionIndex)) ? "default" : "outline"}>
                                                      Option {optionIndex + 1}
                                                    </Badge>
                                                    <Button
                                                      type="button"
                                                      variant={(question.correctAnswers && Array.isArray(question.correctAnswers) && question.correctAnswers.includes(optionIndex)) ? "default" : "outline"}
                                                      size="sm"
                                                      onClick={() => toggleCorrectAnswer(moduleIndex, lessonIndex, questionIndex, optionIndex)}
                                                    >
                                                      {(question.correctAnswers && Array.isArray(question.correctAnswers) && question.correctAnswers.includes(optionIndex)) ? '✓ Correct' : 'Mark as Correct'}
                                                    </Button>
                                                  </div>
                                                  {question.options && question.options.length > 2 && (
                                                    <Button
                                                      type="button"
                                                      variant="outline"
                                                      size="sm"
                                                      onClick={() => removeAnswerOption(moduleIndex, lessonIndex, questionIndex, optionIndex)}
                                                    >
                                                      <Trash2 className="w-4 h-4" />
                                                    </Button>
                                                  )}
                                                </div>
                                                
                                                <div className="space-y-2">
                                                  <Label className="text-sm">Option Text</Label>
                                                  <Input
                                                    placeholder={`Enter option ${optionIndex + 1} text`}
                                                    value={(typeof option === 'string' ? option : option?.text) || ''}
                                                    onChange={(e) => handleOptionTextChange(moduleIndex, lessonIndex, questionIndex, optionIndex, e.target.value)}
                                                  />
                                                </div>
                                                
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                                                  <div className="space-y-2">
                                                    <Label className="text-sm">Image URL (Optional)</Label>
                                                    <Input
                                                      placeholder="https://example.com/image.jpg"
                                                      value={(typeof option === 'object' ? option?.image : '') || ''}
                                                      onChange={(e) => handleOptionMediaChange(moduleIndex, lessonIndex, questionIndex, optionIndex, 'image', e.target.value)}
                                                    />
                                                  </div>
                                                  <div className="space-y-2">
                                                    <Label className="text-sm">Audio URL (Optional)</Label>
                                                    <Input
                                                      placeholder="https://example.com/audio.mp3"
                                                      value={(typeof option === 'object' ? option?.audio : '') || ''}
                                                      onChange={(e) => handleOptionMediaChange(moduleIndex, lessonIndex, questionIndex, optionIndex, 'audio', e.target.value)}
                                                    />
                                                  </div>
                                                </div>
                                                
                                                {/* Preview media if provided */}
                                                {(typeof option === 'object' && option?.image) && (
                                                  <div className="mt-2">
                                                    <img src={option.image} alt={`Option ${optionIndex + 1}`} className="max-w-xs h-20 object-cover rounded border" />
                                                  </div>
                                                )}
                                                {(typeof option === 'object' && option?.audio) && (
                                                  <div className="mt-2">
                                                    <audio controls className="w-full max-w-xs">
                                                      <source src={option.audio} type="audio/mpeg" />
                                                      Your browser does not support the audio element.
                                                    </audio>
                                                  </div>
                                                )}
                                              </div>
                                            ))}
                                          </div>
                                          
                                          {(!question.options || question.options.length === 0) && (
                                            <div className="text-center py-4 text-gray-500 border border-dashed border-gray-300 rounded-lg">
                                              <p>No answer options added yet. Click "Add Option" to get started.</p>
                                            </div>
                                          )}
                                          
                                          {/* Display selected correct answers */}
                                          {question.correctAnswers && Array.isArray(question.correctAnswers) && question.correctAnswers.length > 0 && (
                                            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                              <p className="text-green-800 text-sm font-medium mb-1">
                                                ✅ Correct Answers Selected: {question.correctAnswers.length}
                                              </p>
                                              <p className="text-green-700 text-xs">
                                                Options: {question.correctAnswers.map(idx => `${idx + 1}`).join(', ')}
                                              </p>
                                            </div>
                                          )}
                                          
                                          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                                            <p className="text-purple-800 text-sm">
                                              💡 <strong>Tip:</strong> Mark multiple options as correct. Students must select ALL correct answers to get points.
                                            </p>
                                          </div>
                                        </div>
                                      )}

                                      {question.type === 'chronological-order' && (
                                        <div className="space-y-4 mb-4">
                                          <div className="flex items-center justify-between">
                                            <Label>Items to Order</Label>
                                            <Button
                                              type="button"
                                              variant="outline"
                                              size="sm"
                                              onClick={() => addOrderItem(moduleIndex, lessonIndex, questionIndex)}
                                            >
                                              <Plus className="w-4 h-4 mr-1" />
                                              Add Item
                                            </Button>
                                          </div>
                                          
                                          {/* Drag and Drop Interface */}
                                          <DragDropContext
                                            onDragEnd={(result) => handleChronologicalDragEnd(result, moduleIndex, lessonIndex, questionIndex)}
                                          >
                                            <Droppable droppableId={`chronological-${moduleIndex}-${lessonIndex}-${questionIndex}`}>
                                              {(provided, snapshot) => (
                                                <div
                                                  {...provided.droppableProps}
                                                  ref={provided.innerRef}
                                                  className={`space-y-3 ${snapshot.isDraggingOver ? 'bg-blue-50 rounded-lg p-2' : ''}`}
                                                >
                                                  {((question.items && Array.isArray(question.items)) ? question.items : []).map((item, itemIndex) => (
                                                    <Draggable
                                                      key={`item-${itemIndex}`}
                                                      draggableId={`item-${moduleIndex}-${lessonIndex}-${questionIndex}-${itemIndex}`}
                                                      index={itemIndex}
                                                    >
                                                      {(provided, snapshot) => (
                                                        <div
                                                          ref={provided.innerRef}
                                                          {...provided.draggableProps}
                                                          className={`border border-gray-200 rounded-lg p-3 bg-white ${
                                                            snapshot.isDragging ? 'shadow-lg rotate-1' : 'shadow-sm'
                                                          }`}
                                                        >
                                                          <div className="flex items-center justify-between mb-2">
                                                            <div className="flex items-center space-x-2">
                                                              <div
                                                                {...provided.dragHandleProps}
                                                                className="cursor-grab hover:cursor-grabbing p-1 rounded hover:bg-gray-100"
                                                              >
                                                                <GripVertical className="w-4 h-4 text-gray-400" />
                                                              </div>
                                                              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                                                Position {itemIndex + 1}
                                                              </Badge>
                                                            </div>
                                                            {question.items && question.items.length > 2 && (
                                                              <Button
                                                                type="button"
                                                                variant="outline"
                                                                size="sm"
                                                                onClick={() => removeOrderItem(moduleIndex, lessonIndex, questionIndex, itemIndex)}
                                                              >
                                                                <Trash2 className="w-4 h-4" />
                                                              </Button>
                                                            )}
                                                          </div>
                                                          
                                                          <div className="space-y-2">
                                                            <Label className="text-sm">Item Text</Label>
                                                            <Input
                                                              placeholder={`Enter item ${itemIndex + 1} text`}
                                                              value={(typeof item === 'string' ? item : item?.text) || ''}
                                                              onChange={(e) => handleOrderItemTextChange(moduleIndex, lessonIndex, questionIndex, itemIndex, e.target.value)}
                                                            />
                                                          </div>
                                                          
                                                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                                                            <div className="space-y-2">
                                                              <Label className="text-sm">Image URL (Optional)</Label>
                                                              <Input
                                                                placeholder="https://example.com/image.jpg"
                                                                value={(typeof item === 'object' ? item?.image : '') || ''}
                                                                onChange={(e) => handleOrderItemMediaChange(moduleIndex, lessonIndex, questionIndex, itemIndex, 'image', e.target.value)}
                                                              />
                                                            </div>
                                                            <div className="space-y-2">
                                                              <Label className="text-sm">Audio URL (Optional)</Label>
                                                              <Input
                                                                placeholder="https://example.com/audio.mp3"
                                                                value={(typeof item === 'object' ? item?.audio : '') || ''}
                                                                onChange={(e) => handleOrderItemMediaChange(moduleIndex, lessonIndex, questionIndex, itemIndex, 'audio', e.target.value)}
                                                              />
                                                            </div>
                                                          </div>
                                                          
                                                          {/* Preview media if provided */}
                                                          {(typeof item === 'object' && item?.image) && (
                                                            <div className="mt-2">
                                                              <img src={item.image} alt={`Item ${itemIndex + 1}`} className="max-w-xs h-20 object-cover rounded border" />
                                                            </div>
                                                          )}
                                                          {(typeof item === 'object' && item?.audio) && (
                                                            <div className="mt-2">
                                                              <audio controls className="w-full max-w-xs">
                                                                <source src={item.audio} type="audio/mpeg" />
                                                                Your browser does not support the audio element.
                                                              </audio>
                                                            </div>
                                                          )}
                                                        </div>
                                                      )}
                                                    </Draggable>
                                                  ))}
                                                  {provided.placeholder}
                                                </div>
                                              )}
                                            </Droppable>
                                          </DragDropContext>
                                          
                                          {(!question.items || question.items.length === 0) && (
                                            <div className="text-center py-4 text-gray-500 border border-dashed border-gray-300 rounded-lg">
                                              <p>No items added yet. Click "Add Item" to get started.</p>
                                            </div>
                                          )}
                                          
                                          {/* Display current correct order - no more text input needed! */}
                                          {question.items && question.items.length > 0 && (
                                            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                              <p className="text-green-800 text-sm font-medium mb-1">
                                                ✅ Correct Order: {question.items.map((item, idx) => {
                                                  const itemText = typeof item === 'string' ? item : (item?.text || `Item ${idx + 1}`);
                                                  return itemText.length > 20 ? itemText.substring(0, 20) + '...' : itemText;
                                                }).join(' → ')}
                                              </p>
                                              <p className="text-green-700 text-xs">
                                                Students will see these items shuffled and must drag them into this exact order. Drag items above to reorder them.
                                              </p>
                                            </div>
                                          )}
                                          
                                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                                            <p className="text-blue-800 text-sm">
                                              🎯 <strong>New Drag & Drop Interface:</strong> Simply drag the items above to set the correct chronological order. The order you arrange them here is the correct answer students must match!
                                            </p>
                                          </div>
                                        </div>
                                      )}

                                      {question.type === 'short-answer' && (
                                        <div className="space-y-2 mb-4">
                                          <Label>Sample Correct Answer</Label>
                                          <Input
                                            placeholder="Enter a sample correct answer for reference"
                                            value={question.correctAnswer || ''}
                                            onChange={(e) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'correctAnswer', e.target.value)}
                                          />
                                          <p className="text-xs text-gray-500">This will be used for grading reference. Short answer questions may require manual grading.</p>
                                        </div>
                                      )}

                                      {question.type === 'long-form-answer' && (
                                        <div className="space-y-2 mb-4">
                                          <Label>Sample Answer (for instructor reference)</Label>
                                          <Textarea
                                            placeholder="Provide a sample answer to guide manual grading"
                                            rows={4}
                                            value={question.sampleAnswer || ''}
                                            onChange={(e) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'sampleAnswer', e.target.value)}
                                          />
                                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="space-y-2">
                                              <Label>Word Limit (optional)</Label>
                                              <Input
                                                type="number"
                                                placeholder="500"
                                                value={question.wordLimit || ''}
                                                onChange={(e) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'wordLimit', parseInt(e.target.value) || null)}
                                              />
                                            </div>
                                          </div>
                                          <p className="text-xs text-gray-500">Long form answers require manual grading by the instructor.</p>
                                        </div>
                                      )}



                                      <div className="space-y-2">
                                        <Label>Explanation (Optional)</Label>
                                        <Textarea
                                          placeholder="Explain why this is the correct answer"
                                          rows={2}
                                          value={question.explanation || ''}
                                          onChange={(e) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'explanation', e.target.value)}
                                        />
                                      </div>
                                    </CardContent>
                                  </Card>
                                ))}

                                {(!lesson.quiz?.questions || lesson.quiz.questions.length === 0) && (
                                  <div className="text-center py-8 text-pink-600 bg-pink-50/40 rounded-lg border-2 border-dashed border-pink-200">
                                    <p>No questions added yet. Click "Add Question" below to get started.</p>
                                  </div>
                                )}
                                
                                {/* Add Question Button at Bottom */}
                                <div className="pt-4 border-t border-pink-200">
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => addQuizQuestion(moduleIndex, lessonIndex)}
                                    disabled={
                                      lesson.quiz?.targetQuestionCount && 
                                      (lesson.quiz?.questions || []).length >= lesson.quiz.targetQuestionCount
                                    }
                                    className="w-full border-pink-300 text-pink-700 hover:bg-pink-100"
                                  >
                                    <Plus className="w-4 h-4 mr-2" />
                                    Add Question
                                    {lesson.quiz?.targetQuestionCount && 
                                     (lesson.quiz?.questions || []).length >= lesson.quiz.targetQuestionCount && 
                                     " (Target Reached)"}
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                    
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => addLesson(moduleIndex)}
                      className="border-purple-300 text-purple-700 hover:bg-purple-100"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Lesson
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>

        {/* Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Course Settings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="isPublic"
                  checked={courseData.isPublic}
                  onChange={(e) => handleCourseChange('isPublic', e.target.checked)}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="isPublic">Make this course public</Label>
              </div>
              <p className="text-sm text-gray-600">
                Public courses can be discovered and enrolled by any student. Private courses require manual enrollment.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-4">
          <Button 
            type="button" 
            variant="outline"
            onClick={() => navigate('/courses')}
          >
            Cancel
          </Button>
          <div className="flex items-center space-x-4">
            <Button 
              type="button"
              variant="outline"
              onClick={handleSaveDraft}
              disabled={isSavingDraft || !courseData.title.trim()}
              className="flex items-center"
            >
              {isSavingDraft ? 'Saving...' : 'Save as Draft'}
            </Button>
            <Button
              variant="outline"
              onClick={() => setIsPreviewOpen(true)}
              className="flex items-center"
            >
              <Eye className="w-4 h-4 mr-2" />
              Preview Course
            </Button>
            <Button type="submit" className="bg-blue-600 hover:bg-blue-700" disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : (isEditing ? 'Update Course' : 'Create Course')}
            </Button>
          </div>
        </div>
      </form>

      {/* Course Preview Modal */}
      <CoursePreview
        isOpen={isPreviewOpen}
        onClose={() => setIsPreviewOpen(false)}
        courseData={courseData}
      />
    </div>
  );
};

export default CreateCourse;
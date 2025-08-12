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
import { mockCourses, getCategories } from '../data/mockData';
import { ArrowLeft, Plus, Trash2, Upload, FileText } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const CreateCourse = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const isEditing = Boolean(id);
  const existingCourse = id ? mockCourses.find(c => c.id === id) : null;
  
  const [courseData, setCourseData] = useState({
    title: existingCourse?.title || '',
    description: existingCourse?.description || '',
    category: existingCourse?.category || '',
    duration: existingCourse?.duration || '',
    thumbnail: existingCourse?.thumbnail || '',
    isPublic: existingCourse?.isPublic || true,
    enrollmentType: existingCourse?.enrollmentType || 'open', // 'open' or 'assignment'
    modules: existingCourse?.modules || [
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
  
  useEffect(() => {
    // Load categories when component mounts
    const loadedCategories = getCategories();
    setCategories(loadedCategories.map(cat => cat.name));
  }, []);

  const handleCourseChange = (field, value) => {
    setCourseData(prev => ({
      ...prev,
      [field]: value
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
                lIdx === lessonIndex ? { ...lesson, [field]: value } : lesson
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
                            type: 'multiple-choice',
                            question: '',
                            questionImage: '',
                            questionAudio: '',
                            options: [
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' }
                            ],
                            correctAnswer: 0,
                            correctAnswers: [], // for select-all-that-apply
                            items: [
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' },
                              { text: '', image: '', audio: '' }
                            ], // for chronological-order
                            correctOrder: [], // for chronological-order
                            sampleAnswer: '', // for long-form-answer
                            wordLimit: null, // for long-form-answer
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

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!courseData.title || !courseData.description || !courseData.category) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required course information.",
        variant: "destructive",
      });
      return;
    }

    // In real app, would make API call to save course
    toast({
      title: isEditing ? "Course updated!" : "Course created!",
      description: `Your course has been ${isEditing ? 'updated' : 'created'} successfully.`,
    });
    
    navigate('/courses');
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
                    {categories.map(category => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
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
          </CardContent>
        </Card>

        {/* Course Content */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Course Content</CardTitle>
              <Button type="button" variant="outline" onClick={addModule}>
                <Plus className="w-4 h-4 mr-2" />
                Add Module
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {courseData.modules.map((module, moduleIndex) => (
              <Card key={module.id} className="border-2 border-dashed border-gray-200">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <Badge variant="secondary">Module {moduleIndex + 1}</Badge>
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
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>

                  <div className="space-y-4">
                    {module.lessons.map((lesson, lessonIndex) => (
                      <div key={lesson.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium">Lesson {lessonIndex + 1}</h4>
                          {module.lessons.length > 1 && (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => removeLesson(moduleIndex, lessonIndex)}
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
                                  onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (file) {
                                      // In a real app, you would upload the file and get a URL
                                      const fakeUrl = `https://example.com/documents/${file.name}`;
                                      handleLessonChange(moduleIndex, lessonIndex, 'documentUrl', fakeUrl);
                                      handleLessonChange(moduleIndex, lessonIndex, 'documentName', file.name);
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
                                  <Label className="text-lg font-medium">Quiz Questions</Label>
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
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  onClick={() => addQuizQuestion(moduleIndex, lessonIndex)}
                                  disabled={
                                    lesson.quiz?.targetQuestionCount && 
                                    (lesson.quiz?.questions || []).length >= lesson.quiz.targetQuestionCount
                                  }
                                >
                                  <Plus className="w-4 h-4 mr-2" />
                                  Add Question
                                  {lesson.quiz?.targetQuestionCount && 
                                   (lesson.quiz?.questions || []).length >= lesson.quiz.targetQuestionCount && 
                                   " (Target Reached)"}
                                </Button>
                              </div>

                              <div className="space-y-4">
                                {(lesson.quiz?.questions || []).map((question, questionIndex) => (
                                  <Card key={question.id} className="border-dashed">
                                    <CardContent className="p-4">
                                      <div className="flex items-center justify-between mb-3">
                                        <Badge variant="outline">Question {questionIndex + 1}</Badge>
                                        <Button
                                          type="button"
                                          variant="outline"
                                          size="sm"
                                          onClick={() => removeQuizQuestion(moduleIndex, lessonIndex, questionIndex)}
                                        >
                                          <Trash2 className="w-4 h-4" />
                                        </Button>
                                      </div>

                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                        <div className="space-y-2">
                                          <Label>Question Type</Label>
                                          <Select 
                                            value={question.type || 'multiple-choice'} 
                                            onValueChange={(value) => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'type', value)}
                                          >
                                            <SelectTrigger>
                                              <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                              <SelectItem value="multiple-choice">Multiple Choice</SelectItem>
                                              <SelectItem value="select-all-that-apply">Select All That Apply</SelectItem>
                                              <SelectItem value="true-false">True/False</SelectItem>
                                              <SelectItem value="short-answer">Short Answer</SelectItem>
                                              <SelectItem value="long-form-answer">Long Form Answer</SelectItem>
                                              <SelectItem value="chronological-order">Chronological Order</SelectItem>
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

                                      {(question.type === 'multiple-choice' || !question.type) && (
                                        <div className="space-y-2 mb-4">
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
                                          {(question.options || ['', '', '', '']).map((option, optionIndex) => (
                                            <div key={optionIndex} className="border rounded-lg p-3 space-y-3">
                                              <div className="flex items-center space-x-2">
                                                <input
                                                  type="radio"
                                                  name={`correct-${question.id}`}
                                                  checked={question.correctAnswer === optionIndex}
                                                  onChange={() => handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'correctAnswer', optionIndex)}
                                                  className="text-green-600"
                                                />
                                                <Input
                                                  placeholder={`Option ${optionIndex + 1} text`}
                                                  value={typeof option === 'string' ? option : (option?.text || '')}
                                                  onChange={(e) => handleOptionTextChange(moduleIndex, lessonIndex, questionIndex, optionIndex, e.target.value)}
                                                />
                                                {(question.options || []).length > 2 && (
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
                                              
                                              {/* Option Media */}
                                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ml-6">
                                                <div className="space-y-1">
                                                  <Label className="text-xs">Option Image URL</Label>
                                                  <Input
                                                    placeholder="https://example.com/option-image.jpg"
                                                    value={typeof option === 'object' ? (option.image || '') : ''}
                                                    onChange={(e) => handleOptionMediaChange(moduleIndex, lessonIndex, questionIndex, optionIndex, 'image', e.target.value)}
                                                  />
                                                </div>
                                                <div className="space-y-1">
                                                  <Label className="text-xs">Option Audio URL</Label>
                                                  <Input
                                                    placeholder="https://example.com/option-audio.mp3"
                                                    value={typeof option === 'object' ? (option.audio || '') : ''}
                                                    onChange={(e) => handleOptionMediaChange(moduleIndex, lessonIndex, questionIndex, optionIndex, 'audio', e.target.value)}
                                                  />
                                                </div>
                                              </div>
                                              
                                              {/* Media Preview */}
                                              {typeof option === 'object' && option.image && (
                                                <div className="ml-6">
                                                  <img src={option.image} alt={`Option ${optionIndex + 1}`} className="max-w-xs h-20 object-cover rounded border" />
                                                </div>
                                              )}
                                              {typeof option === 'object' && option.audio && (
                                                <div className="ml-6">
                                                  <audio controls className="w-full max-w-xs">
                                                    <source src={option.audio} type="audio/mpeg" />
                                                  </audio>
                                                </div>
                                              )}
                                            </div>
                                          ))}
                                          <p className="text-xs text-gray-500">Select the radio button next to the correct answer. Add images or audio to enhance your options.</p>
                                        </div>
                                      )}

                                      {question.type === 'select-all-that-apply' && (
                                        <div className="space-y-2 mb-4">
                                          <div className="flex items-center justify-between">
                                            <Label>Answer Options (Select all correct answers)</Label>
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
                                          {(question.options || ['', '', '', '', '']).map((option, optionIndex) => (
                                            <div key={optionIndex} className="border rounded-lg p-3 space-y-3">
                                              <div className="flex items-center space-x-2">
                                                <input
                                                  type="checkbox"
                                                  checked={(question.correctAnswers || []).includes(optionIndex)}
                                                  onChange={(e) => {
                                                    const currentAnswers = question.correctAnswers || [];
                                                    const newAnswers = e.target.checked
                                                      ? [...currentAnswers, optionIndex]
                                                      : currentAnswers.filter(index => index !== optionIndex);
                                                    handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'correctAnswers', newAnswers);
                                                  }}
                                                  className="text-green-600"
                                                />
                                                <Input
                                                  placeholder={`Option ${optionIndex + 1} text`}
                                                  value={typeof option === 'string' ? option : (option?.text || '')}
                                                  onChange={(e) => handleOptionTextChange(moduleIndex, lessonIndex, questionIndex, optionIndex, e.target.value)}
                                                />
                                                {(question.options || []).length > 2 && (
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
                                              
                                              {/* Option Media */}
                                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ml-6">
                                                <div className="space-y-1">
                                                  <Label className="text-xs">Option Image URL</Label>
                                                  <Input
                                                    placeholder="https://example.com/option-image.jpg"
                                                    value={typeof option === 'object' ? (option.image || '') : ''}
                                                    onChange={(e) => handleOptionMediaChange(moduleIndex, lessonIndex, questionIndex, optionIndex, 'image', e.target.value)}
                                                  />
                                                </div>
                                                <div className="space-y-1">
                                                  <Label className="text-xs">Option Audio URL</Label>
                                                  <Input
                                                    placeholder="https://example.com/option-audio.mp3"
                                                    value={typeof option === 'object' ? (option.audio || '') : ''}
                                                    onChange={(e) => handleOptionMediaChange(moduleIndex, lessonIndex, questionIndex, optionIndex, 'audio', e.target.value)}
                                                  />
                                                </div>
                                              </div>
                                              
                                              {/* Media Preview */}
                                              {typeof option === 'object' && option.image && (
                                                <div className="ml-6">
                                                  <img src={option.image} alt={`Option ${optionIndex + 1}`} className="max-w-xs h-20 object-cover rounded border" />
                                                </div>
                                              )}
                                              {typeof option === 'object' && option.audio && (
                                                <div className="ml-6">
                                                  <audio controls className="w-full max-w-xs">
                                                    <source src={option.audio} type="audio/mpeg" />
                                                  </audio>
                                                </div>
                                              )}
                                            </div>
                                          ))}
                                          <p className="text-xs text-gray-500">Check the boxes next to all correct answers. Add images or audio to enhance your options.</p>
                                        </div>
                                      )}

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

                                      {question.type === 'chronological-order' && (
                                        <div className="space-y-2 mb-4">
                                          <Label>Items to Order</Label>
                                          {(question.items || ['', '', '', '']).map((item, itemIndex) => (
                                            <div key={itemIndex} className="border rounded-lg p-3 space-y-3">
                                              <div className="flex items-center space-x-2">
                                                <span className="text-sm text-gray-600 min-w-[80px]">Position {itemIndex + 1}:</span>
                                                <Input
                                                  placeholder={`Item ${itemIndex + 1} text`}
                                                  value={typeof item === 'string' ? item : (item?.text || '')}
                                                  onChange={(e) => handleOrderItemTextChange(moduleIndex, lessonIndex, questionIndex, itemIndex, e.target.value)}
                                                />
                                                <Button
                                                  type="button"
                                                  variant="outline"
                                                  size="sm"
                                                  onClick={() => removeOrderItem(moduleIndex, lessonIndex, questionIndex, itemIndex)}
                                                  disabled={(question.items || []).length <= 2}
                                                >
                                                  <Trash2 className="w-4 h-4" />
                                                </Button>
                                              </div>
                                              
                                              {/* Item Media */}
                                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ml-20">
                                                <div className="space-y-1">
                                                  <Label className="text-xs">Item Image URL</Label>
                                                  <Input
                                                    placeholder="https://example.com/item-image.jpg"
                                                    value={typeof item === 'object' ? (item.image || '') : ''}
                                                    onChange={(e) => handleOrderItemMediaChange(moduleIndex, lessonIndex, questionIndex, itemIndex, 'image', e.target.value)}
                                                  />
                                                </div>
                                                <div className="space-y-1">
                                                  <Label className="text-xs">Item Audio URL</Label>
                                                  <Input
                                                    placeholder="https://example.com/item-audio.mp3"
                                                    value={typeof item === 'object' ? (item.audio || '') : ''}
                                                    onChange={(e) => handleOrderItemMediaChange(moduleIndex, lessonIndex, questionIndex, itemIndex, 'audio', e.target.value)}
                                                  />
                                                </div>
                                              </div>
                                              
                                              {/* Media Preview */}
                                              {typeof item === 'object' && item.image && (
                                                <div className="ml-20">
                                                  <img src={item.image} alt={`Item ${itemIndex + 1}`} className="max-w-xs h-20 object-cover rounded border" />
                                                </div>
                                              )}
                                              {typeof item === 'object' && item.audio && (
                                                <div className="ml-20">
                                                  <audio controls className="w-full max-w-xs">
                                                    <source src={item.audio} type="audio/mpeg" />
                                                  </audio>
                                                </div>
                                              )}
                                            </div>
                                          ))}
                                          <Button
                                            type="button"
                                            variant="outline"
                                            size="sm"
                                            onClick={() => addOrderItem(moduleIndex, lessonIndex, questionIndex)}
                                          >
                                            <Plus className="w-4 h-4 mr-2" />
                                            Add Item
                                          </Button>
                                          <div className="space-y-2">
                                            <Label>Correct Order</Label>
                                            <p className="text-xs text-gray-500 mb-2">
                                              Specify the correct chronological order by entering the position numbers (1, 2, 3, etc.)
                                            </p>
                                            <Input
                                              placeholder="e.g., 2,1,4,3 (comma-separated position numbers)"
                                              value={question.correctOrder ? question.correctOrder.map(i => i + 1).join(',') : ''}
                                              onChange={(e) => {
                                                const order = e.target.value.split(',').map(num => parseInt(num.trim()) - 1).filter(num => !isNaN(num));
                                                handleQuestionChange(moduleIndex, lessonIndex, questionIndex, 'correctOrder', order);
                                              }}
                                            />
                                          </div>
                                          <p className="text-xs text-gray-500">Students will drag and drop these items into the correct chronological order. Add images or audio to enhance the items.</p>
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
                                  <div className="text-center py-8 text-gray-500">
                                    <p>No questions added yet. Click "Add Question" to get started.</p>
                                  </div>
                                )}
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
          <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
            {isEditing ? 'Update Course' : 'Create Course'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CreateCourse;
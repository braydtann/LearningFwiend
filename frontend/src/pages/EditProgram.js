import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import FinalTestQuestionInterface from '../components/FinalTestQuestionInterface';
import { 
  ArrowLeft, 
  Save, 
  Plus, 
  Trash2, 
  ArrowUp, 
  ArrowDown, 
  Trophy 
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const EditProgram = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, getProgramById, updateProgram, getAllCourses } = useAuth();
  const { toast } = useToast();
  
  const [program, setProgram] = useState(null);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadProgramAndCourses = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Load program details
        const programResult = await getProgramById(id);
        if (programResult.success) {
          setProgram({
            ...programResult.program,
            courseOrder: programResult.program.courseIds || [],
            finalTest: {
              title: '',
              description: '',
              timeLimit: 90,
              passingScore: 75,
              maxAttempts: 2,
              questions: []
            }
          });
        } else {
          setError(programResult.error);
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
      } catch (err) {
        console.error('Error loading program and courses:', err);
        setError('Failed to load program details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadProgramAndCourses();
    }
  }, [id, getProgramById, getAllCourses, toast]);

  const handleSaveProgram = async () => {
    if (!program.title || !program.description || program.courseIds.length === 0) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information and select at least one course.",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      const programData = {
        title: program.title,
        description: program.description,
        courseIds: program.courseIds,
        nestedProgramIds: program.nestedProgramIds || [],
        duration: program.duration
      };

      const result = await updateProgram(id, programData);
      
      if (result.success) {
        toast({
          title: "Program updated successfully!",
          description: `${program.title} has been updated.`,
        });
        navigate(`/program/${id}`);
      } else {
        toast({
          title: "Error updating program",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error updating program:', error);
      toast({
        title: "Error updating program",
        description: "There was an error updating the program. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCourseSelection = (courseId, checked) => {
    if (checked) {
      setProgram(prev => ({
        ...prev,
        courseIds: [...prev.courseIds, courseId],
        courseOrder: [...prev.courseOrder, courseId]
      }));
    } else {
      setProgram(prev => ({
        ...prev,
        courseIds: prev.courseIds.filter(id => id !== courseId),
        courseOrder: prev.courseOrder.filter(id => id !== courseId)
      }));
    }
  };

  const moveCourseUp = (index) => {
    if (index === 0) return;
    const newOrder = [...program.courseOrder];
    [newOrder[index], newOrder[index - 1]] = [newOrder[index - 1], newOrder[index]];
    setProgram(prev => ({ ...prev, courseOrder: newOrder }));
  };

  const moveCourseDown = (index) => {
    if (index === program.courseOrder.length - 1) return;
    const newOrder = [...program.courseOrder];
    [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
    setProgram(prev => ({ ...prev, courseOrder: newOrder }));
  };

  const removeCourseFromOrder = (courseId) => {
    setProgram(prev => ({
      ...prev,
      courseIds: prev.courseIds.filter(id => id !== courseId),
      courseOrder: prev.courseOrder.filter(id => id !== courseId)
    }));
  };

  // Final Test handlers for Edit Program
  const handleFinalTestChange = (field, value) => {
    setProgram(prev => ({
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
      correctAnswers: [],
      items: [
        { text: '', image: '', audio: '' },
        { text: '', image: '', audio: '' },
        { text: '', image: '', audio: '' }
      ],
      correctOrder: [0, 1, 2],
      sampleAnswer: '',
      wordLimit: null,
      points: 10,
      explanation: ''
    };
    
    setProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: [...prev.finalTest.questions, newQuestion]
      }
    }));
  };

  const removeFinalTestQuestion = (questionIndex) => {
    setProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.filter((_, index) => index !== questionIndex)
      }
    }));
  };

  const handleFinalTestQuestionChange = (questionIndex, field, value) => {
    setProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex ? { ...question, [field]: value } : question
        )
      }
    }));
  };

  const handleFinalTestOptionChange = (questionIndex, optionIndex, value) => {
    setProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? {
                ...question,
                options: question.options.map((option, oIndex) =>
                  oIndex === optionIndex ? { ...option, text: value } : option
                )
              }
            : question
        )
      }
    }));
  };

  const handleFinalTestOptionMediaChange = (questionIndex, optionIndex, mediaType, value) => {
    setProgram(prev => ({
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
    setProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? { 
                ...question, 
                options: [...question.options, { text: '', image: '', audio: '' }]
              } 
            : question
        )
      }
    }));
  };

  const removeFinalTestAnswerOption = (questionIndex, optionIndex) => {
    setProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? { 
                ...question, 
                options: question.options.filter((_, oIdx) => oIdx !== optionIndex),
                correctAnswer: question.correctAnswer > optionIndex ? question.correctAnswer - 1 : question.correctAnswer,
                correctAnswers: (question.correctAnswers || [])
                  .map(idx => idx > optionIndex ? idx - 1 : idx)
                  .filter(idx => idx !== optionIndex)
              } 
            : question
        )
      }
    }));
  };

  const handleFinalTestItemChange = (questionIndex, itemIndex, field, value) => {
    setProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? {
                ...question,
                items: question.items.map((item, iIndex) =>
                  iIndex === itemIndex ? { ...item, [field]: value } : item
                )
              }
            : question
        )
      }
    }));
  };

  const addFinalTestOrderItem = (questionIndex) => {
    setProgram(prev => ({
      ...prev,
      finalTest: {
        ...prev.finalTest,
        questions: prev.finalTest.questions.map((question, index) =>
          index === questionIndex 
            ? { 
                ...question, 
                items: [...question.items, { text: '', image: '', audio: '' }]
              } 
            : question
        )
      }
    }));
  };

  const removeFinalTestOrderItem = (questionIndex, itemIndex) => {
    setProgram(prev => ({
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading program...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button 
            variant="outline" 
            onClick={() => navigate('/programs')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Programs</span>
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Edit Learning Program</h1>
            <p className="text-gray-600">Modify the structured learning path</p>
          </div>
        </div>
        
        <Button 
          onClick={handleSaveProgram}
          disabled={saving}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Save className="w-4 h-4 mr-2" />
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      {/* Edit Form */}
      <Card>
        <CardHeader>
          <CardTitle>Program Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="title">Program Name *</Label>
              <Input
                id="title"
                placeholder="Enter program name"
                value={program?.title || ''}
                onChange={(e) => setProgram(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="difficulty">Difficulty Level</Label>
              <Select 
                value={program.difficulty} 
                onValueChange={(value) => setProgram(prev => ({ ...prev, difficulty: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Beginner">Beginner</SelectItem>
                  <SelectItem value="Intermediate">Intermediate</SelectItem>
                  <SelectItem value="Advanced">Advanced</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              placeholder="Describe the learning outcomes and goals of this program"
              rows={3}
              value={program?.description || ''}
              onChange={(e) => setProgram(prev => ({ ...prev, description: e.target.value }))}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="duration">Estimated Duration</Label>
              <Input
                id="duration"
                placeholder="e.g., 12 weeks, 3 months"
                value={program?.duration || ''}
                onChange={(e) => setProgram(prev => ({ ...prev, duration: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="deadline">Program Deadline *</Label>
              <Input
                id="deadline"
                type="date"
                value={program.deadline}
                onChange={(e) => setProgram(prev => ({ ...prev, deadline: e.target.value }))}
                min={new Date().toISOString().split('T')[0]} // Prevent past dates
              />
              <p className="text-xs text-gray-500">Students must complete the program by this date</p>
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
                    checked={program.courseIds.includes(course.id)}
                    onChange={(e) => handleCourseSelection(course.id, e.target.checked)}
                    className="rounded"
                  />
                  <img 
                    src={course.thumbnail} 
                    alt={course.title}
                    className="w-12 h-12 rounded-lg object-cover"
                  />
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{course.title}</h4>
                    <p className="text-sm text-gray-600">{course.category} • {course.duration}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Course Ordering */}
          {program.courseOrder.length > 0 && (
            <div className="space-y-4">
              <Label>Course Order (Use arrows to reorder)</Label>
              <div className="space-y-2 border rounded-md p-4 bg-gray-50">
                {program.courseOrder.map((courseId, index) => {
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
                        src={course?.thumbnail} 
                        alt={course?.title}
                        className="w-10 h-10 rounded-lg object-cover"
                      />
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900">{course?.title}</h5>
                        <p className="text-sm text-gray-600">{course?.duration}</p>
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
                          disabled={index === program.courseOrder.length - 1}
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

          {/* Final Test Management */}
          <div className="space-y-6 border-t pt-6">
            <div className="flex items-center space-x-2">
              <Trophy className="w-6 h-6 text-purple-600" />
              <Label className="text-xl font-semibold text-purple-800">Final Test Management</Label>
            </div>
            
            <div className="bg-purple-50/50 rounded-lg p-6 space-y-6">
              {/* Final Test Basic Configuration */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Test Title *</Label>
                  <Input
                    placeholder="e.g., Full Stack Development Final Assessment"
                    value={program.finalTest?.title || ''}
                    onChange={(e) => handleFinalTestChange('title', e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Time Limit (minutes)</Label>
                  <Input
                    type="number"
                    placeholder="90"
                    min="1"
                    value={program.finalTest?.timeLimit || 90}
                    onChange={(e) => handleFinalTestChange('timeLimit', parseInt(e.target.value) || 90)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Passing Score (%)</Label>
                  <Input
                    type="number"
                    placeholder="75"
                    min="0"
                    max="100"
                    value={program.finalTest?.passingScore || 75}
                    onChange={(e) => handleFinalTestChange('passingScore', parseInt(e.target.value) || 75)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Max Attempts</Label>
                  <Input
                    type="number"
                    placeholder="2"
                    min="1"
                    value={program.finalTest?.maxAttempts || 2}
                    onChange={(e) => handleFinalTestChange('maxAttempts', parseInt(e.target.value) || 2)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Test Description</Label>
                <Textarea
                  placeholder="Describe what this final assessment covers and what students can expect"
                  rows={3}
                  value={program.finalTest?.description || ''}
                  onChange={(e) => handleFinalTestChange('description', e.target.value)}
                />
              </div>

              {/* Final Test Questions Management */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-lg font-medium">Final Test Questions</Label>
                    <p className="text-sm text-gray-600">Create comprehensive questions to assess program completion</p>
                  </div>
                  <Button
                    type="button"
                    onClick={addFinalTestQuestion}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Question
                  </Button>
                </div>

                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {(program.finalTest?.questions || []).map((question, questionIndex) => (
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
                    />
                  ))}

                  {(!program.finalTest?.questions || program.finalTest.questions.length === 0) && (
                    <div className="text-center py-8 text-purple-600 bg-purple-50 rounded-lg border-2 border-dashed border-purple-200">
                      <Trophy className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <h3 className="font-medium mb-2">No Final Test Questions Yet</h3>
                      <p className="text-sm mb-4">Create comprehensive questions to assess student understanding of the entire program.</p>
                      <Button
                        type="button"
                        onClick={addFinalTestQuestion}
                        className="bg-purple-600 hover:bg-purple-700"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Create First Question
                      </Button>
                    </div>
                  )}
                </div>

                {program.finalTest?.questions && program.finalTest.questions.length > 0 && (
                  <div className="bg-purple-100 rounded-lg p-4">
                    <h4 className="font-medium text-purple-800 mb-2">Final Test Summary</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-purple-600">Questions:</span>
                        <span className="ml-2 font-medium">{program.finalTest.questions.length}</span>
                      </div>
                      <div>
                        <span className="text-purple-600">Total Points:</span>
                        <span className="ml-2 font-medium">
                          {program.finalTest.questions.reduce((sum, q) => sum + (q.points || 0), 0)}
                        </span>
                      </div>
                      <div>
                        <span className="text-purple-600">Time Limit:</span>
                        <span className="ml-2 font-medium">{program.finalTest.timeLimit || 90} mins</span>
                      </div>
                      <div>
                        <span className="text-purple-600">Passing Score:</span>
                        <span className="ml-2 font-medium">{program.finalTest.passingScore || 75}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EditProgram;
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { getProgramById, mockCourses, updateProgram } from '../data/mockData';
import { 
  Save, 
  ArrowLeft,
  ArrowUp,
  ArrowDown,
  Trash2,
  Calendar,
  Trophy,
  Plus
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const EditProgram = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { id } = useParams();
  const { toast } = useToast();
  
  const [program, setProgram] = useState({
    name: '',
    description: '',
    courseIds: [],
    courseOrder: [],
    duration: '',
    difficulty: 'Beginner',
    deadline: ''
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Load program data on component mount
  useEffect(() => {
    const loadProgram = async () => {
      try {
        const programData = getProgramById(id);
        if (!programData) {
          toast({
            title: "Program not found",
            description: "The requested program could not be found.",
            variant: "destructive",
          });
          navigate('/programs');
          return;
        }
        
        setProgram({
          id: programData.id,
          name: programData.name,
          description: programData.description,
          courseIds: programData.courseIds || [],
          courseOrder: programData.courseOrder || programData.courseIds || [],
          duration: programData.duration || '',
          difficulty: programData.difficulty || 'Beginner',
          deadline: programData.deadline || ''
        });
      } catch (error) {
        console.error('Error loading program:', error);
        toast({
          title: "Error loading program",
          description: "There was an error loading the program data.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadProgram();
    }
  }, [id, toast, navigate]);

  const handleSaveProgram = async () => {
    if (!program.name || !program.description || program.courseIds.length === 0 || !program.deadline) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information including deadline and select at least one course.",
        variant: "destructive",
      });
      return;
    }

    // Validate deadline is in the future
    const today = new Date();
    const selectedDeadline = new Date(program.deadline);
    if (selectedDeadline <= today) {
      toast({
        title: "Invalid deadline",
        description: "Program deadline must be in the future.",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      const updatedProgram = {
        ...program,
        courseOrder: program.courseOrder.length > 0 ? program.courseOrder : program.courseIds,
        totalCourses: program.courseIds.length,
        estimatedHours: program.courseIds.length * 20,
      };

      // Update the program (this would normally be an API call)
      const success = updateProgram(id, updatedProgram);
      
      if (success) {
        toast({
          title: "Program updated successfully!",
          description: `${program.name} has been updated with ${program.courseIds.length} courses.`,
        });
        navigate('/programs');
      } else {
        throw new Error('Failed to update program');
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
              <Label htmlFor="name">Program Name *</Label>
              <Input
                id="name"
                placeholder="Enter program name"
                value={program.name}
                onChange={(e) => setProgram(prev => ({ ...prev, name: e.target.value }))}
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
              value={program.description}
              onChange={(e) => setProgram(prev => ({ ...prev, description: e.target.value }))}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="duration">Estimated Duration</Label>
              <Input
                id="duration"
                placeholder="e.g., 12 weeks, 3 months"
                value={program.duration}
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
              {mockCourses.map(course => (
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
                  const course = mockCourses.find(c => c.id === courseId);
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
        </CardContent>
      </Card>
    </div>
  );
};

export default EditProgram;
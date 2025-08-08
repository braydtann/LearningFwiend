import React, { useState } from 'react';
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
import { getProgramsForAdmin, mockCourses, getProgramsWithDeadlineStatus } from '../data/mockData';
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
  CheckCircle
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Programs = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newProgram, setNewProgram] = useState({
    name: '',
    description: '',
    courseIds: [],
    courseOrder: [],
    duration: '',
    difficulty: 'Beginner',
    deadline: '' // Add deadline field
  });

  const programs = getProgramsWithDeadlineStatus();

  const handleCreateProgram = () => {
    if (!newProgram.name || !newProgram.description || newProgram.courseIds.length === 0 || !newProgram.deadline) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information including deadline and select at least one course.",
        variant: "destructive",
      });
      return;
    }

    // Validate deadline is in the future
    const today = new Date();
    const selectedDeadline = new Date(newProgram.deadline);
    if (selectedDeadline <= today) {
      toast({
        title: "Invalid deadline",
        description: "Program deadline must be in the future.",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Program created successfully!",
      description: `${newProgram.name} has been created with ${newProgram.courseIds.length} courses and deadline set for ${new Date(newProgram.deadline).toLocaleDateString()}.`,
    });

    setNewProgram({
      name: '',
      description: '',
      courseIds: [],
      courseOrder: [],
      duration: '',
      difficulty: 'Beginner',
      deadline: ''
    });
    setIsCreateModalOpen(false);
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

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner':
        return 'bg-green-100 text-green-800';
      case 'Intermediate':
        return 'bg-orange-100 text-orange-800';
      case 'Advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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
                  <Label htmlFor="name">Program Name *</Label>
                  <Input
                    id="name"
                    placeholder="Enter program name"
                    value={newProgram.name}
                    onChange={(e) => setNewProgram(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="difficulty">Difficulty Level</Label>
                  <Select 
                    value={newProgram.difficulty} 
                    onValueChange={(value) => setNewProgram(prev => ({ ...prev, difficulty: value }))}
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

                <div className="space-y-2">
                  <Label htmlFor="deadline">Program Deadline *</Label>
                  <Input
                    id="deadline"
                    type="date"
                    value={newProgram.deadline}
                    onChange={(e) => setNewProgram(prev => ({ ...prev, deadline: e.target.value }))}
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
                        checked={newProgram.courseIds.includes(course.id)}
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
              {newProgram.courseOrder.length > 0 && (
                <div className="space-y-4">
                  <Label>Course Order (Use arrows to reorder)</Label>
                  <div className="space-y-2 border rounded-md p-4 bg-gray-50">
                    {newProgram.courseOrder.map((courseId, index) => {
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
                  {programs.filter(p => p.status === 'active').length}
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
                <p className="text-orange-600 text-sm font-medium">Total Enrollments</p>
                <p className="text-2xl font-bold text-orange-700">
                  {programs.reduce((sum, p) => sum + p.enrolledStudents, 0)}
                </p>
              </div>
              <Users className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-red-50 border-red-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-600 text-sm font-medium">Urgent Deadlines</p>
                <p className="text-2xl font-bold text-red-700">
                  {programs.filter(p => p.deadlineStatus?.status === 'urgent' || p.deadlineStatus?.status === 'overdue').length}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
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
          {programs.length === 0 ? (
            <div className="text-center py-12">
              <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No programs created yet</h3>
              <p className="text-gray-600 mb-4">Create your first learning program to combine courses into structured paths</p>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Program
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {programs.map((program) => (
                <Card key={program.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {program.name}
                        </h3>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                          {program.description}
                        </p>
                      </div>
                      <Badge className={getDifficultyColor(program.difficulty)}>
                        {program.difficulty}
                      </Badge>
                    </div>

                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center text-gray-600">
                          <BookOpen className="w-4 h-4 mr-1" />
                          <span>{program.totalCourses} courses</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <Users className="w-4 h-4 mr-1" />
                          <span>{program.enrolledStudents} students</span>
                        </div>
                      </div>

                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="w-4 h-4 mr-1" />
                        <span>{program.duration} • {program.estimatedHours}h estimated</span>
                      </div>

                      {/* Deadline Information */}
                      {program.deadline && (
                        <div className={`flex items-center text-sm p-2 rounded-lg ${
                          program.deadlineStatus?.status === 'overdue' 
                            ? 'bg-red-50 border border-red-200 text-red-800' 
                            : program.deadlineStatus?.status === 'urgent'
                            ? 'bg-orange-50 border border-orange-200 text-orange-800'
                            : program.deadlineStatus?.status === 'warning'
                            ? 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                            : 'bg-green-50 border border-green-200 text-green-800'
                        }`}>
                          <Calendar className="w-4 h-4 mr-1" />
                          <span className="font-medium">
                            Deadline: {new Date(program.deadline).toLocaleDateString()}
                          </span>
                          {program.deadlineStatus?.status === 'overdue' && (
                            <AlertTriangle className="w-4 h-4 ml-2" />
                          )}
                        </div>
                      )}

                      <div className="text-sm text-gray-600">
                        <strong>Created:</strong> {new Date(program.createdAt).toLocaleDateString()}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 mt-4">
                      <Button 
                        size="sm" 
                        className="flex-1"
                        onClick={() => navigate(`/program/${program.id}`)}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View Details
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => navigate(`/program/${program.id}/edit`)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Programs;
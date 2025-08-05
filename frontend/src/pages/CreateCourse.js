import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { mockCourses } from '../data/mockData';
import { ArrowLeft, Plus, Trash2, Upload } from 'lucide-react';
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
    modules: existingCourse?.modules || [
      {
        id: 'm1',
        title: '',
        lessons: [
          { id: 'l1', title: '', type: 'video', duration: '', videoUrl: '', presentationUrl: '', content: '' }
        ]
      }
    ]
  });

  const categories = ['Web Development', 'Data Science', 'Marketing', 'Design', 'Business'];

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

  const addModule = () => {
    setCourseData(prev => ({
      ...prev,
      modules: [
        ...prev.modules,
        {
          id: `m${prev.modules.length + 1}`,
          title: '',
          lessons: [
            { id: `l${Date.now()}`, title: '', type: 'video', duration: '', videoUrl: '', presentationUrl: '', content: '' }
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
                { id: `l${Date.now()}`, title: '', type: 'video', duration: '', videoUrl: '', presentationUrl: '', content: '' }
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
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                            <div className="space-y-2">
                              <Label>
                                {lesson.type === 'video' ? 'Video URL' : 'Canva Presentation URL'}
                              </Label>
                              <Input
                                placeholder={
                                  lesson.type === 'video' 
                                    ? "YouTube, Vimeo, or Google Drive URL" 
                                    : "Canva presentation sharing link"
                                }
                                value={lesson.videoUrl || lesson.presentationUrl || ''}
                                onChange={(e) => handleLessonChange(
                                  moduleIndex, 
                                  lessonIndex, 
                                  lesson.type === 'video' ? 'videoUrl' : 'presentationUrl', 
                                  e.target.value
                                )}
                              />
                              <p className="text-xs text-gray-500">
                                {lesson.type === 'video' 
                                  ? 'Supported: YouTube, Vimeo, or Google Drive sharing links'
                                  : 'Copy the sharing link from your Canva presentation'
                                }
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
                        )}

                        {lesson.type === 'text' && (
                          <div className="mt-4">
                            <Label>Content</Label>
                            <Textarea
                              placeholder="Enter lesson content"
                              rows={6}
                              value={lesson.content || ''}
                              onChange={(e) => handleLessonChange(moduleIndex, lessonIndex, 'content', e.target.value)}
                            />
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
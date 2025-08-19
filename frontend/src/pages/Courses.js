import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import CoursePreview from '../components/CoursePreview';
import { getImageUrl, handleImageError } from '../utils/imageUtils';

import { BookOpen, Clock, Users, Search, Filter, Play, Star, Eye, Trash2, Plus } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Courses = () => {
  const { user, isAdmin, isInstructor, isLearner, getAllCourses, getMyCourses, enrollInCourse, unenrollFromCourse, deleteCourse, getMyEnrollments } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrollments, setEnrollments] = useState([]);
  const [loadingEnrollments, setLoadingEnrollments] = useState(true);
  
  // Preview functionality
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [previewCourse, setPreviewCourse] = useState(null);

  // Get enrolled courses for learners
  const enrolledCourses = isLearner ? enrollments.map(enrollment => enrollment.course).filter(Boolean) : [];
  const enrolledCourseIds = enrolledCourses.map(course => course.id);

  // Load courses and enrollments on component mount
  useEffect(() => {
    loadCourses();
    if (isLearner) {
      loadEnrollments();
    }
  }, [isLearner]);

  const loadCourses = async () => {
    setLoading(true);
    try {
      // All users should see all available courses for collaboration
      const result = await getAllCourses();
      if (result.success) {
        setCourses(result.courses);
      } else {
        toast({
          title: "Error loading courses",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load courses",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadEnrollments = async () => {
    setLoadingEnrollments(true);
    try {
      const result = await getMyEnrollments();
      if (result.success) {
        setEnrollments(result.enrollments);
      } else {
        console.error('Failed to load enrollments:', result.error);
        setEnrollments([]);
      }
    } catch (error) {
      console.error('Error loading enrollments:', error);
      setEnrollments([]);
    } finally {
      setLoadingEnrollments(false);
    }
  };

  const handleEnroll = async (courseId) => {
    const result = await enrollInCourse(courseId);
    if (result.success) {
      toast({
        title: "Enrolled successfully!",
        description: "You have been enrolled in the course.",
      });
      // Reload courses and enrollments to update enrollment status
      loadCourses();
      if (isLearner) {
        loadEnrollments();
      }
    } else {
      toast({
        title: "Enrollment failed",
        description: result.error,
        variant: "destructive",
      });
    }
  };

  const handleUnenroll = async (courseId) => {
    const result = await unenrollFromCourse(courseId);
    if (result.success) {
      toast({
        title: "Unenrolled successfully!",
        description: "You have been removed from the course.",
      });
      // Reload courses and enrollments to update enrollment status
      loadCourses();
      if (isLearner) {
        loadEnrollments();
      }
    } else {
      toast({
        title: "Unenroll failed",
        description: result.error,
        variant: "destructive",
      });
    }
  };

  // Filter and sort courses
  const filteredCourses = courses
    .filter(course => {
      const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           course.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || course.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'students':
          return b.enrolledStudents - a.enrolledStudents;
        case 'recent':
        default:
          return new Date(b.createdAt) - new Date(a.createdAt);
      }
    });

  const categories = ['all', ...new Set(courses.map(course => course.category))];



  const handleViewCourse = (courseId, action = 'view') => {
    const course = courses.find(c => c.id === courseId);
    
    if (!course) {
      toast({
        title: "Course not found",
        description: "The requested course could not be found.",
        variant: "destructive",
      });
      return;
    }
    
    const isEnrolled = enrolledCourseIds.includes(courseId);
    const isOwner = course && course.instructor === user?.username;
    
    // If it's a preview action or user is not enrolled and not owner, show preview
    if (action === 'preview' || (!isEnrolled && !isOwner && action === 'view')) {
      // Ensure course has required structure for preview
      if (!course.modules || course.modules.length === 0) {
        toast({
          title: "Preview not available",
          description: "This course doesn't have any modules to preview yet.",
          variant: "destructive",
        });
        return;
      }
      
      setPreviewCourse(course);
      setIsPreviewOpen(true);
    } else {
      // Otherwise navigate to course detail page
      navigate(`/course/${courseId}`);
    }
  };

  const handlePreviewCourse = (courseId) => {
    handleViewCourse(courseId, 'preview');
  };

  const handleDeleteCourse = async (courseId, courseName) => {
    if (!window.confirm(`Are you sure you want to delete the course "${courseName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const result = await deleteCourse(courseId);
      
      if (result.success) {
        toast({
          title: "Course deleted successfully",
          description: `"${courseName}" has been permanently deleted.`,
        });
        
        // Reload courses to update the list
        loadCourses();
      } else {
        toast({
          title: "Failed to delete course",
          description: result.error || "An error occurred while deleting the course.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error deleting course:', error);
      toast({
        title: "Error deleting course",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            All Courses
          </h1>
          <p className="text-gray-600">
            Discover and manage all available courses
          </p>
        </div>
        {user?.role === 'instructor' && (
          <Button 
            onClick={() => navigate('/create-course')}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Create New Course
          </Button>
        )}
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search courses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full md:w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map(category => (
                  <SelectItem key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="recent">Recently Added</SelectItem>
                <SelectItem value="title">Title A-Z</SelectItem>
                <SelectItem value="students">Most Popular</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Enrolled Courses (for learners) */}
      {isLearner && enrolledCourses.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Continue Learning</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {enrolledCourses.slice(0, 3).map((course) => (
                <Card key={course.id} className="hover:shadow-lg transition-shadow">
                  <div className="aspect-video relative overflow-hidden rounded-t-lg">
                    <img 
                      src={getImageUrl(course.thumbnailUrl || course.thumbnail)} 
                      alt={course.title}
                      className="w-full h-full object-cover"
                      onError={(e) => handleImageError(e)}
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                      <Button
                        size="sm"
                        className="bg-white text-black hover:bg-gray-100"
                        onClick={() => handleViewCourse(course.id)}
                      >
                        <Play className="w-4 h-4 mr-2" />
                        Continue
                      </Button>
                    </div>
                    <div className="absolute top-2 right-2">
                      <Badge variant="secondary" className="bg-blue-600 text-white">
                        {course.progress}% Complete
                      </Badge>
                    </div>
                  </div>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                      {course.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3">
                      by {course.instructor}
                    </p>
                    <Button 
                      className="w-full"
                      onClick={() => handleViewCourse(course.id)}
                    >
                      Continue Learning
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* All Courses */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">
            {user?.role === 'instructor' ? 'My Courses' : 'Available Courses'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Loading courses...</h3>
              <p className="text-gray-600">Please wait while we fetch your courses.</p>
            </div>
          ) : filteredCourses.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No courses found</h3>
              <p className="text-gray-600">
                {user?.role === 'instructor' 
                  ? "You haven't created any courses yet."
                  : "Try adjusting your search or filters."
                }
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCourses.map((course) => {
                const isEnrolled = enrolledCourseIds.includes(course.id);
                const isOwner = user?.id === course.instructorId;
                const canEdit = isOwner || isAdmin; // Admins can edit any course
                
                return (
                  <Card key={course.id} className="hover:shadow-lg transition-shadow">
                    <div className="aspect-video relative overflow-hidden rounded-t-lg">
                      <img 
                        src={getImageUrl(course.thumbnailUrl || course.thumbnail)} 
                        alt={course.title}
                        className="w-full h-full object-cover"
                        onError={(e) => handleImageError(e)}
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                        <Button
                          size="sm"
                          className="bg-white text-black hover:bg-gray-100"
                          onClick={() => {
                            const isEnrolled = enrolledCourseIds.includes(course.id);
                            if (canEdit || isEnrolled) {
                              handleViewCourse(course.id, 'view');
                            } else {
                              handlePreviewCourse(course.id);
                            }
                          }}
                        >
                          <Play className="w-4 h-4 mr-2" />
                          {canEdit ? 'Manage' : isEnrolled ? 'Continue' : 'Preview'}
                        </Button>
                      </div>
                    </div>
                    
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start mb-2">
                        <Badge variant="secondary" className="text-xs">
                          {course.category}
                        </Badge>
                        <div className="flex items-center text-sm text-gray-500">
                          <Star className="w-4 h-4 mr-1 fill-yellow-400 text-yellow-400" />
                          4.8
                        </div>
                      </div>
                      
                      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                        {course.title}
                      </h3>
                      
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                        {course.description}
                      </p>
                      
                      <p className="text-sm text-gray-600 mb-3">
                        by {course.instructor}
                      </p>
                      
                      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                        <div className="flex items-center">
                          <Users className="w-4 h-4 mr-1" />
                          {course.enrolledStudents} students
                        </div>
                        <div className="flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {course.duration}
                        </div>
                        <div className="flex items-center">
                          <BookOpen className="w-4 h-4 mr-1" />
                          {course.totalLessons} lessons
                        </div>
                      </div>
                      
                      {canEdit ? (
                        <div className="flex space-x-2">
                          <Button 
                            variant="outline" 
                            className="flex-1"
                            onClick={() => handleViewCourse(course.id)}
                          >
                            View
                          </Button>
                          <Button 
                            className="flex-1"
                            onClick={() => navigate(`/edit-course/${course.id}`)}
                          >
                            Edit
                          </Button>
                          {isAdmin && (
                            <Button 
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteCourse(course.id, course.title)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      ) : isEnrolled ? (
                        <div className="flex space-x-2">
                          <Button 
                            className="flex-1"
                            onClick={() => handleViewCourse(course.id)}
                          >
                            Continue Learning
                          </Button>
                          {isAdmin && (
                            <Button 
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteCourse(course.id, course.title)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      ) : (
                        <div className="flex space-x-2">
                          <Button 
                            variant="outline" 
                            className="flex-1"
                            onClick={() => handlePreviewCourse(course.id)}
                          >
                            <Eye className="w-4 h-4 mr-2" />
                            Preview
                          </Button>
                          <Button 
                            className="flex-1 bg-blue-600 hover:bg-blue-700"
                            onClick={() => handleEnroll(course.id)}
                          >
                            Enroll
                          </Button>
                          {isAdmin && (
                            <Button 
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteCourse(course.id, course.title)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Course Preview Modal */}
      {previewCourse && (
        <CoursePreview
          isOpen={isPreviewOpen}
          onClose={() => {
            setIsPreviewOpen(false);
            setPreviewCourse(null);
          }}
          courseData={previewCourse}
        />
      )}
    </div>
  );
};

export default Courses;
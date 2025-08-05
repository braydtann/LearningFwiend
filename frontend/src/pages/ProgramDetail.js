import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { mockPrograms, getProgramCourses } from '../data/mockData';
import { 
  ArrowLeft,
  Award, 
  Users, 
  BookOpen, 
  Clock,
  Calendar,
  Target,
  CheckCircle,
  Play
} from 'lucide-react';

const ProgramDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const program = mockPrograms.find(p => p.id === id);
  const courses = getProgramCourses(id);

  if (!program) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Program not found</h1>
        <Button onClick={() => navigate('/programs')}>
          Back to Programs
        </Button>
      </div>
    );
  }

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
      <div className="flex items-center space-x-4 mb-6">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate('/programs')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div className="h-6 border-l border-gray-300"></div>
        <nav className="text-sm text-gray-500">
          <span>Programs</span> / <span className="text-gray-900">{program.name}</span>
        </nav>
      </div>

      {/* Program Overview */}
      <Card>
        <CardContent className="p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-4">
                <h1 className="text-3xl font-bold text-gray-900">{program.name}</h1>
                <Badge className={getDifficultyColor(program.difficulty)}>
                  {program.difficulty}
                </Badge>
                <Badge variant={program.status === 'active' ? 'default' : 'secondary'}>
                  {program.status}
                </Badge>
              </div>
              <p className="text-lg text-gray-600 mb-6">{program.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="flex items-center space-x-3">
                  <BookOpen className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Courses</p>
                    <p className="font-medium">{program.totalCourses}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Enrolled Students</p>
                    <p className="font-medium">{program.enrolledStudents}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Duration</p>
                    <p className="font-medium">{program.duration}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <Target className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Estimated Hours</p>
                    <p className="font-medium">{program.estimatedHours}h</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">Program Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-700">{program.enrolledStudents}</div>
                <div className="text-sm text-blue-600">Total Enrollments</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-700">85%</div>
                <div className="text-sm text-green-600">Completion Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-700">4.8</div>
                <div className="text-sm text-orange-600">Average Rating</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Course Sequence */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Learning Path</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {courses.map((course, index) => (
              <div key={course.id} className="relative">
                {/* Connector Line */}
                {index < courses.length - 1 && (
                  <div className="absolute left-6 top-20 w-0.5 h-16 bg-gray-200"></div>
                )}
                
                <Card className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      {/* Step Number */}
                      <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg flex-shrink-0">
                        {index + 1}
                      </div>
                      
                      {/* Course Thumbnail */}
                      <img 
                        src={course.thumbnail} 
                        alt={course.title}
                        className="w-20 h-20 rounded-lg object-cover flex-shrink-0"
                      />
                      
                      {/* Course Details */}
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {course.title}
                        </h3>
                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                          {course.description}
                        </p>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                          <div className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {course.duration}
                          </div>
                          <div className="flex items-center">
                            <BookOpen className="w-4 h-4 mr-1" />
                            {course.totalLessons} lessons
                          </div>
                          <div className="flex items-center">
                            <Users className="w-4 h-4 mr-1" />
                            {course.enrolledStudents} students
                          </div>
                        </div>

                        <Badge variant="secondary" className="mb-3">
                          {course.category}
                        </Badge>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex flex-col space-y-2 flex-shrink-0">
                        <Button 
                          size="sm"
                          onClick={() => navigate(`/course/${course.id}`)}
                        >
                          <Play className="w-4 h-4 mr-1" />
                          View Course
                        </Button>
                        <div className="text-xs text-gray-500 text-center">
                          Step {index + 1} of {courses.length}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Program Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Program Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 mb-2">
                Created on {new Date(program.createdAt).toLocaleDateString()}
              </p>
              <p className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline">
                Export Program
              </Button>
              <Button onClick={() => navigate(`/program/${program.id}/edit`)}>
                Edit Program
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProgramDetail;